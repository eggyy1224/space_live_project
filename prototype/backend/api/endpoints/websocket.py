import json
import asyncio
from typing import Dict, List, Set, Optional, Any, Deque
from collections import deque
from fastapi import WebSocket, WebSocketDisconnect
import random
import os
import base64
import time
from datetime import datetime, timedelta
import re
import uuid
import logging

from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from core.config import settings
from utils.logger import logger
from services.ai.prompts import PROMPT_TEMPLATES  # 新增：導入 PROMPT_TEMPLATES
from services.murmur_service.murmur_service import MurmurService
from services.murmur_service import config as murmur_config
from services.murmur_service.utils import clean_murmur_prefix, is_murmur_too_similar, has_continuity_marker
from config.songs_config import SONGS_METADATA, SONG_PLAY_PROBABILITY

# --- 閒置設定 ---
IDLE_TIMEOUT_SECONDS = 15  # 從30秒改為15秒，讓murmur更快出現
IDLE_CHECK_INTERVAL_SECONDS = 3 # 從8秒改為3秒，更頻繁地檢查空閒狀態
MURMUR_MIN_INTERVAL_SECONDS = 25  # 從45秒改為25秒，允許murmur更頻繁出現
# MURMUR_MAX_COUNT = 3  # <--- 移除：不再限制連續 murmur 次數
MAX_HISTORY_LENGTH = 10 # 減少歷史長度，降低記憶負擔
# --- 結束 ---

# --- 新增：思考流設定 ---
THINKING_THEMES = [
    "太空生活", "直播計劃", "美妝技巧", "個人形象", "外表煩惱", 
    "粉絲互動", "地球思念", "太空站設備", "宅居日常", "飲食相關",
    "科技新聞", "娛樂話題", "自我反思", "夢想與目標", "網路流行語"
]
MAX_THREAD_CONTINUITY = 6  # 連續幾次保持同一個思考主題，增加到6確保更長的連續性
SIMILARITY_THRESHOLD_CONTINUOUS = 0.35  # 連續模式下的相似度閾值，降低允許更多思考變化
CONTINUITY_MARKERS = [
    "不過", "話說回來", "順便一提", "另外", "而且", "搞不好", "說到這個", "然後", "其實",
    "再想想", "也許", "不對", "等等", "嗯...", "哦！", "有了！", "原來如此", "但是", "所以",
    "還有", "對了", "想一想", "再說啦", "想想喔", "回到剛剛", "說真的", "講到這個", "仔細想想",
    "我突然想到", "換個角度想", "接著剛剛"
]
# --- 結束 ---

# --- 修改消息優先級和狀態，增加更高的語音保護 ---
MESSAGE_PRIORITY = {
    "user": 100,     # 用戶消息最高優先級
    "murmur": 50,    # murmur 中等優先級
    "system": 10     # 系統消息低優先級
}

# 定義音頻播放狀態枚舉
class SpeakingState:
    IDLE = "idle"             # 無語音播放
    PLAYING_USER_RESPONSE = "playing_user_response"  # 播放用戶回應
    PLAYING_MURMUR = "playing_murmur"    # 播放 murmur
    PLAYING_SYSTEM = "playing_system"    # 播放系統消息
    FINISHING = "finishing"   # 語音播放結束過渡狀態，不允許新播放
# --- 結束修改 ---

# --- 修改配置參數，減少保護時間 ---
MURMUR_BUFFER_MAX = 0.4  # 減少最大緩衝時間（從0.6秒進一步減少到0.4秒）
VOICE_FINISHING_BUFFER = 0.2  # 語音結束後的保護時間減至0.2秒
# --- 結束修改 ---

# 建立服務實例
ai_service = AIService()
tts_service = TextToSpeechService()
# 創建 MurmurService 實例
murmur_service = MurmurService(ai_service=ai_service, tts_service=tts_service)

# WebSocket連接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # Use a loop to safely remove the websocket instance
        # This handles cases where the same client might connect multiple times
        # although ideally, the disconnect logic should prevent duplicates.
        connections_to_remove = [conn for conn in self.active_connections if conn == websocket]
        for conn in connections_to_remove:
            self.active_connections.remove(conn)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- 新增：消息排隊和處理類 ---
class MessageQueue:
    """處理消息優先級和排隊的類"""
    
    def __init__(self):
        self.queue: Deque[Dict[str, Any]] = deque()
        self.processing_lock = asyncio.Lock()
        self.is_processing = False
    
    def add_message(self, message: Dict[str, Any], priority: int):
        """添加消息到隊列，根據優先級排序"""
        self.queue.append({"message": message, "priority": priority})
        # 根據優先級排序
        sorted_queue = sorted(self.queue, key=lambda x: x["priority"], reverse=True)
        self.queue = deque(sorted_queue)
    
    async def process_next(self, callback):
        """處理隊列中的下一條消息"""
        if not self.queue or self.is_processing:
            return False
        
        async with self.processing_lock:
            if not self.queue:  # 雙重檢查，避免競態條件
                return False
            
            self.is_processing = True
            try:
                next_message = self.queue.popleft()
                await callback(next_message["message"])
                return True
            finally:
                self.is_processing = False
    
    def clear(self):
        """清空隊列"""
        self.queue.clear()
    
    def is_empty(self):
        """檢查隊列是否為空"""
        return len(self.queue) == 0
# --- 結束新增 ---

# WebSocket端點
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(f"WebSocket connection open for client: {websocket.client}")
    
    # --- 新增：為此連線創建一個異步鎖和消息隊列 ---   
    ai_processing_lock = asyncio.Lock()
    message_queue = MessageQueue()
    # --- 結束新增 ---

    # --- 新增：結構化對話歷史 ---   
    conversation_history: List[Dict[str, any]] = []
    # --- 結束新增 ---
    
    # --- 新增：思考流追蹤變數 ---
    current_thinking_topic = random.choice(THINKING_THEMES)
    thinking_thread_continuity = 0
    last_murmur_content = ""
    # --- 結束新增 ---

    # 初始化連接狀態
    logger.info(f"Client connected: {websocket.client}")
    conversation_history = []
    last_activity_timestamp = datetime.utcnow()
    last_murmur_timestamp = None
    last_speaking_reset_timestamp = None  # 新增：追蹤最後一次重置說話狀態的時間
    recent_murmurs = set()  # 使用集合以避免重複
    current_emotion = "neutral"
    
    # --- 修改：使用更精確的語音狀態管理 ---
    speaking_state = SpeakingState.IDLE  # 當前語音狀態
    current_audio_task = None  # 當前播放的音頻任務
    # --- 結束修改 ---
    
    user_responded = False

    # 記錄當前表情狀態，用於實現平滑過渡
    idle_check_task = None # <--- 新增：閒置檢查任務

    async def add_to_history(role: str, content: str, is_murmur: bool = False):
        """安全地添加記錄到對話歷史並進行修剪。"""
        nonlocal conversation_history
        history_entry = {"role": role, "content": content}
        if role == "bot":
            history_entry["is_murmur"] = is_murmur
        conversation_history.append(history_entry)
        # 修剪歷史，只保留最近 MAX_HISTORY_LENGTH * 2 條消息 (約 MAX_HISTORY_LENGTH 輪對話)
        if len(conversation_history) > MAX_HISTORY_LENGTH * 2:
            conversation_history = conversation_history[-(MAX_HISTORY_LENGTH * 2):]

    async def reset_speaking_after_duration(duration_seconds: float, reset_to_state: str = SpeakingState.IDLE):
        """在指定的秒數後重置語音播放狀態。增加過渡保護階段。"""
        nonlocal speaking_state, last_activity_timestamp, last_murmur_timestamp, last_speaking_reset_timestamp
        
        # 記錄相關資訊以便調試
        previous_speaking_state = speaking_state
        logger.info(f"Starting reset_speaking_after_duration timer for {duration_seconds:.2f} seconds. Current speaking_state: {previous_speaking_state}")
        
        # 等待指定時間（語音估計播放時間）
        await asyncio.sleep(duration_seconds)
        
        # 先進入過渡保護狀態 FINISHING，不允許開始新的語音播放
        speaking_state = SpeakingState.FINISHING
        logger.info(f"Changed speaking_state from {previous_speaking_state} to {speaking_state} (finishing phase)")
        
        # 額外的保護緩衝時間，確保語音確實播放完畢
        await asyncio.sleep(VOICE_FINISHING_BUFFER)
        
        # 最終轉入閒置狀態
        speaking_state = reset_to_state
        
        # 更新所有相關時間戳，確保後續操作基於正確的時間
        current_time = datetime.utcnow()
        last_activity_timestamp = current_time
        last_speaking_reset_timestamp = current_time
        
        # 無論是什麼類型的語音(murmur或正常回覆)都更新last_murmur_timestamp
        # 這樣可以避免murmur結束後立即觸發下一個murmur
        last_murmur_timestamp = current_time
        
        logger.info(f"Reset speaking_state from {SpeakingState.FINISHING} to {reset_to_state} after total {duration_seconds + VOICE_FINISHING_BUFFER:.2f} seconds (including buffer) and updated all timestamps to current time")
        
        # 重置後處理下一條消息
        if not message_queue.is_empty():
            asyncio.create_task(process_message_queue())

    async def process_message_queue():
        """處理消息隊列中的下一條消息"""
        # 只有在完全閒置狀態時才處理新消息，更嚴格的條件
        if speaking_state != SpeakingState.IDLE:
            logger.info(f"Cannot process next message, speaking_state is {speaking_state}")
            return
            
        async def message_processor(message):
            # 根據消息類型分發處理
            message_type = message.get("type")
            if message_type == "user_message":
                await handle_user_message(message.get("content"))
            elif message_type == "murmur":
                await handle_murmur()
                
        await message_queue.process_next(message_processor)

    async def handle_user_message(content: str):
        """處理用戶消息"""
        nonlocal speaking_state, last_activity_timestamp, user_responded
        
        if not content:
            logger.warning("Received empty user message content.")
            return
            
        # 更新狀態
        last_activity_timestamp = datetime.utcnow()
        user_responded = True
        speaking_state = SpeakingState.PLAYING_USER_RESPONSE
        
        logger.info(f"Processing user message, setting speaking_state to {speaking_state}")
        
        try:
            # 確保會話歷史不為空，如果是第一次消息，添加一個初始消息
            if not conversation_history:
                # 添加一個初始化的系統消息，與murmur生成時的初始化方式保持一致
                await add_to_history("bot", "你好！我是星宅妹。", is_murmur=False)
                logger.info("初始化對話歷史")
            
            # 先將用戶消息添加到歷史
            await add_to_history("user", content)
            
            # 生成回復
            ai_result = await ai_service.generate_response(
                user_text=content,
                history=conversation_history
            )
            if not ai_result:
                logger.error("AI service returned None for user message")
                speaking_state = SpeakingState.IDLE
                return
                
            bot_response = ai_result.get("final_response", "抱歉，我似乎有點恍神了...")
            bot_response = clean_murmur_prefix(bot_response)
            
            # 處理TTS
            tts_result = await tts_service.synthesize_speech(bot_response)
            audio_base64 = tts_result.get("audio") if tts_result else None
            audio_duration = tts_result.get("duration") if tts_result and "duration" in tts_result else len(bot_response) * 0.15
            
            # 創建回應消息
            bot_message = {
                "id": f"bot-{int(asyncio.get_event_loop().time() * 1000)}",
                "role": "bot",
                "content": bot_response,
                "bodyAnimationSequence": ai_result.get("body_animation_sequence"),
                "timestamp": None,
                "audioUrl": None
            }
            
            # 保存並設置音頻URL
            if audio_base64:
                await save_audio_and_set_url(audio_base64, bot_message)
                
            # 發送回應
            await websocket.send_json({
                "type": "chat-message",
                "message": bot_message
            })
            
            # 發送情緒軌跡（如果有）
            emotional_keyframes = ai_result.get("emotional_keyframes")
            if emotional_keyframes:
                await websocket.send_json({
                    "type": "emotionalTrajectory",
                    "payload": {
                        "duration": audio_duration,
                        "keyframes": emotional_keyframes
                    }
                })
            
            # 設置音頻播放完成後的任務
            buffer_time = min(MURMUR_BUFFER_MAX, 0.3 + audio_duration * 0.03)
            reset_task = asyncio.create_task(
                reset_speaking_after_duration(audio_duration + buffer_time)
            )
            
            # 添加機器人回應到歷史
            await add_to_history("bot", bot_response)
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}", exc_info=True)
            speaking_state = SpeakingState.IDLE
            
    async def handle_murmur():
        """處理murmur生成和播放"""
        nonlocal speaking_state, last_murmur_timestamp, recent_murmurs, current_emotion
        # --- 新增：思考流變量 ---
        nonlocal current_thinking_topic, thinking_thread_continuity, last_murmur_content
        # --- 結束新增 ---
        
        # --- 新增：檢查是否播放預設歌曲 ---
        if SONGS_METADATA and random.random() < SONG_PLAY_PROBABILITY:
            try:
                selected_song = random.choice(SONGS_METADATA)
                song_id = selected_song.get("id", "unknown_song")
                song_title = selected_song.get("title", "一首歌")
                song_filename = selected_song.get("filename")
                song_duration = selected_song.get("duration", 60.0) # 預設60秒
                song_emotion_keyframes = selected_song.get("emotionalKeyframes", [])
                song_body_animation_sequence = selected_song.get("bodyAnimationSequence", [])

                if not song_filename:
                    logger.error("Selected song has no filename defined in songs_config.py")
                    # 可以選擇 fallback 到一般 murmur 或直接 return
                    # 此處選擇 fallback
                    pass # 讓它執行到後面的普通 murmur 邏輯
                else:
                    logger.info(f"Triggering song: {song_title} ({song_filename})")
                    speaking_state = SpeakingState.PLAYING_MURMUR # 或 PLAYING_SONG 如果有此狀態

                    song_audio_url = f"/songs-file/{song_filename}" # 基於 api/__init__.py 的設定

                    bot_message = {
                        "id": f"bot-song-{int(asyncio.get_event_loop().time() * 1000)}",
                        "role": "bot",
                        "content": song_title, # 可以是歌曲標題或特定文字
                        "bodyAnimationSequence": song_body_animation_sequence,
                        "timestamp": None, #  datetime.utcnow().isoformat() 如果前端需要
                        "audioUrl": song_audio_url,
                        "isMurmur": True, # 標記為 murmur 類型，或新增 isSong: True
                        "isSong": True # 新增一個明確的標記
                    }

                    await websocket.send_json({
                        "type": "chat-message",
                        "message": bot_message
                    })

                    if song_emotion_keyframes:
                        await websocket.send_json({
                            "type": "emotionalTrajectory",
                            "payload": {
                                "duration": song_duration,
                                "keyframes": song_emotion_keyframes
                            }
                        })
                    
                    last_murmur_timestamp = datetime.utcnow()
                    # 添加歌曲播放資訊到歷史 (可選)
                    await add_to_history("bot", f"[正在播放歌曲]: {song_title}", is_murmur=True)

                    # 設置音頻播放完成後的任務
                    buffer_time = min(MURMUR_BUFFER_MAX, 0.3 + song_duration * 0.03)
                    asyncio.create_task(
                        reset_speaking_after_duration(song_duration + buffer_time)
                    )
                    return # 成功播放歌曲，結束 handle_murmur

            except Exception as e:
                logger.error(f"Error processing song playback: {e}", exc_info=True)
                # 出錯時，可以選擇 fallback 到一般 murmur
                pass # 讓它執行到後面的普通 murmur 邏輯
        # --- 結束新增歌曲播放邏輯 ---
        
        # --- 以下是原有的 murmur 生成邏輯 ---
        speaking_state = SpeakingState.PLAYING_MURMUR
        logger.info(f"Generating standard murmur, setting speaking_state to {speaking_state}")

        # (此處省略了原有 murmur 的生成、TTS、訊息發送等邏輯，應保留)
        # 確保 if not conversation_history: block 和 ai_service.generate_response, tts_service.synthesize_speech, 
        # save_audio_and_set_url, websocket.send_json 等都在這裡
        # 範例: 
        if thinking_thread_continuity >= MAX_THREAD_CONTINUITY:
            available_themes = [t for t in THINKING_THEMES if t != current_thinking_topic and THINKING_THEMES] if THINKING_THEMES else ["default_topic"]
            current_thinking_topic = random.choice(available_themes) if available_themes else "default_topic"
            thinking_thread_continuity = 0
            logger.info(f"重置思考主題為: {current_thinking_topic}")
        else:
            thinking_thread_continuity += 1
            logger.info(f"繼續思考主題 {current_thinking_topic}，連續第 {thinking_thread_continuity} 次")

        context_prompt = ""
        thinking_thread = ""
        if recent_murmurs:
            # ... (處理 recent_murmurs 的邏輯)
            pass

        prompt_template_name = "murmur_continuous" if thinking_thread_continuity > 0 else "murmur"
        template = PROMPT_TEMPLATES.get(prompt_template_name, PROMPT_TEMPLATES.get("murmur", "請隨意地自言自語。"))
        # ... (格式化 murmur_prompt)
        murmur_prompt = template # 簡化範例

        try:
            temp_history = conversation_history.copy() if conversation_history else []
            if not temp_history:
                temp_history = [{"role": "bot", "content": "你好！我是星宅妹。", "is_murmur": False}]
            
            ai_result = await ai_service.generate_response(
                system_prompt=murmur_prompt,
                history=temp_history
            )

            if not ai_result or "final_response" not in ai_result:
                logger.error("AIService failed to generate murmur or returned invalid format.")
                speaking_state = SpeakingState.IDLE
                return
            
            ai_murmur_text = ai_result.get("final_response")
            ai_murmur_text = clean_murmur_prefix(ai_murmur_text) # 確保 clean_murmur_prefix 可用

            similarity_threshold = SIMILARITY_THRESHOLD_CONTINUOUS if thinking_thread_continuity > 0 else murmur_config.MURMUR_SIMILARITY_THRESHOLD
            if recent_murmurs and is_murmur_too_similar(ai_murmur_text, recent_murmurs, similarity_threshold):
                logger.warning(f"Generated murmur is too similar, skipping: '{ai_murmur_text}'")
                speaking_state = SpeakingState.IDLE
                return
            
            last_murmur_content = ai_murmur_text
            recent_murmurs.add(ai_murmur_text)
            if len(recent_murmurs) > 10: # 可配置
                oldest = next(iter(recent_murmurs))
                recent_murmurs.remove(oldest)

            murmur_emotion = ai_result.get("emotion", current_emotion)
            current_emotion = murmur_emotion
            await add_to_history("bot", ai_murmur_text, is_murmur=True)

            tts_result = await tts_service.synthesize_speech(ai_murmur_text)
            audio_base64 = tts_result.get("audio") if tts_result else None
            audio_duration = tts_result.get("duration", len(ai_murmur_text) * 0.15)

            bot_message = {
                "id": f"bot-murmur-{int(asyncio.get_event_loop().time() * 1000)}",
                "role": "bot",
                "content": ai_murmur_text,
                "bodyAnimationSequence": ai_result.get("body_animation_sequence"),
                "timestamp": None,
                "audioUrl": None,
                "isMurmur": True,
                "isContinuous": thinking_thread_continuity > 0,
                "thinkingTopic": current_thinking_topic,
                "continuityLevel": thinking_thread_continuity
            }

            if audio_base64:
                await save_audio_and_set_url(audio_base64, bot_message, is_murmur=True) # 確保 save_audio_and_set_url 可用
            
            await websocket.send_json({"type": "chat-message", "message": bot_message})

            emotional_keyframes = ai_result.get("emotional_keyframes")
            if emotional_keyframes:
                await websocket.send_json({
                    "type": "emotionalTrajectory",
                    "payload": {"duration": audio_duration, "keyframes": emotional_keyframes}
                })
            
            last_murmur_timestamp = datetime.utcnow()
            buffer_time = min(MURMUR_BUFFER_MAX, 0.3 + audio_duration * 0.03)
            asyncio.create_task(reset_speaking_after_duration(audio_duration + buffer_time))

        except Exception as e:
            logger.error(f"Error generating standard murmur: {e}", exc_info=True)
            speaking_state = SpeakingState.IDLE
        
    async def save_audio_and_set_url(audio_base64: str, message_obj: Dict[str, Any], is_murmur: bool = False):
        """保存音頻到文件並設置URL - 優化版本"""
        prefix = "murmur-" if is_murmur else ""
        audio_filename = f"{prefix}{int(asyncio.get_event_loop().time() * 1000)}.mp3"
        
        # 構建保存路徑
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        audio_dir = os.path.join(backend_root, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        audio_filepath = os.path.join(audio_dir, audio_filename)

        try:
            # 解碼並保存音頻
            if isinstance(audio_base64, str):
                audio_base64_data = audio_base64.split(",", 1)[1] if "," in audio_base64 else audio_base64
                audio_data = base64.b64decode(audio_base64_data)
                with open(audio_filepath, 'wb') as f:
                    f.write(audio_data)
                # 如果成功保存，設置 audioUrl
                message_obj["audioUrl"] = f"/audio-file/{audio_filename}"
            else:
                logger.error(f"Audio data is not a valid string: {type(audio_base64)}")
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")

    async def idle_checker():
        """背景任務，定期檢查閒置狀態並觸發 murmur。優化版本，減少日誌輸出"""
        nonlocal last_activity_timestamp, current_emotion, last_murmur_timestamp, recent_murmurs, user_responded, speaking_state, last_speaking_reset_timestamp
        while True:
            await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS)
            try:
                current_time = datetime.utcnow()
                idle_duration = current_time - last_activity_timestamp

                # --- 簡化的murmur觸發條件檢查 ---
                should_wait_after_speaking = False
                if last_speaking_reset_timestamp:
                    time_since_last_reset_seconds = (current_time - last_speaking_reset_timestamp).total_seconds()
                    should_wait_after_speaking = time_since_last_reset_seconds < 1.0  # 減少等待時間
                
                murmur_condition_met = (
                    idle_duration > timedelta(seconds=IDLE_TIMEOUT_SECONDS) and
                    (last_murmur_timestamp is None or 
                     current_time - last_murmur_timestamp > timedelta(seconds=MURMUR_MIN_INTERVAL_SECONDS)) and
                    speaking_state == SpeakingState.IDLE and
                    not should_wait_after_speaking
                )
                
                # 只在條件滿足時記錄日誌，減少I/O開銷
                if murmur_condition_met:
                    logger.info("Murmur conditions met, triggering murmur")
                    
                    # 使用消息隊列添加murmur請求
                    message_queue.add_message({"type": "murmur"}, priority=MESSAGE_PRIORITY["murmur"])
                    
                    # 嘗試立即處理
                    await process_message_queue()

            except WebSocketDisconnect:
                logger.info(f"Idle checker detected disconnection. Stopping checker.")
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in idle_checker loop: {e}")
                await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS * 2)

    try:
        idle_check_task = asyncio.create_task(idle_checker())
        logger.info(f"Started idle checker task for client {websocket.client}")

        while True:
            data = await websocket.receive_text()
            
            # 將用戶消息加入隊列
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "message" or message_type == "chat-message":
                content = message.get("content", message.get("message", ""))
                if content:
                    # 更新活動時間戳
                    last_activity_timestamp = datetime.utcnow()
                    user_responded = True
                    
                    # 添加到消息隊列
                    message_queue.add_message(
                        {"type": "user_message", "content": content},
                        priority=MESSAGE_PRIORITY["user"]
                    )
                    
                    # 嘗試立即處理
                    await process_message_queue()
                else:
                    logger.warning(f"Received empty content in message type: {message_type}")
            else:
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {websocket.client}")
    except asyncio.CancelledError:
        logger.info(f"Main websocket task cancelled for {websocket.client}")
    except Exception as e:
        logger.error(f"Unexpected error in websocket_endpoint for {websocket.client}: {e}", exc_info=True)
    finally:
        logger.info(f"Cleaning up connection for {websocket.client}")
        if idle_check_task and not idle_check_task.done():
            idle_check_task.cancel()
            try:
                await asyncio.wait_for(idle_check_task, timeout=1.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            logger.info(f"Cancelled idle checker task for client {websocket.client}")
        
        # 安全地斷開連接
        try:
            if websocket in manager.active_connections:
                 manager.disconnect(websocket)
                 logger.info(f"WebSocket connection successfully removed from manager for client {websocket.client}")
            else:
                 logger.warning(f"WebSocket for client {websocket.client} was already disconnected or not in manager.")
        except Exception as cleanup_err:
             logger.error(f"Error during connection cleanup for {websocket.client}: {cleanup_err}", exc_info=True)
        logger.info(f"WebSocket connection closed for client {websocket.client}")