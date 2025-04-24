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

from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from core.config import settings
from utils.logger import logger
from services.ai.prompts import PROMPT_TEMPLATES  # 新增：導入 PROMPT_TEMPLATES

# --- 閒置設定 ---
IDLE_TIMEOUT_SECONDS = 15  # 增加到15秒，減少murmur頻率
IDLE_CHECK_INTERVAL_SECONDS = 5 # 增加到5秒，降低檢查頻率
MURMUR_MIN_INTERVAL_SECONDS = 30  # 增加到30秒，減少AI調用頻率
# MURMUR_MAX_COUNT = 3  # <--- 移除：不再限制連續 murmur 次數
MAX_HISTORY_LENGTH = 10 # 減少歷史長度，降低記憶負擔
# --- 結束 ---

# --- 新增：思考流設定 ---
THINKING_THEMES = [
    "太空生活", "直播計劃", "美妝技巧", "個人形象", "外表煩惱", 
    "粉絲互動", "地球思念", "太空站設備", "宅居日常", "飲食相關",
    "科技新聞", "娛樂話題", "自我反思", "夢想與目標", "網路流行語"
]
MAX_THREAD_CONTINUITY = 4  # 連續幾次保持同一個思考主題
SIMILARITY_THRESHOLD_CONTINUOUS = 0.4  # 連續模式下的相似度閾值（更低允許更多變化）
CONTINUITY_MARKERS = ["不過", "話說回來", "順便一提", "另外", "而且", "搞不好", "說到這個", "然後", "其實"]
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
MURMUR_BUFFER_MAX = 0.6  # 減少最大緩衝時間（從1.2秒減少到0.6秒）
VOICE_FINISHING_BUFFER = 0.5  # 語音結束後的保護時間減半
# --- 結束修改 ---

# 建立服務實例
ai_service = AIService()
tts_service = TextToSpeechService()

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

# --- 特殊值處理，讓自言自語更頻繁 ---
MURMUR_SIMILARITY_THRESHOLD = 0.6  # 降低相似度閾值，允許更多變化 (原為0.7)

# --- 新增：清理輕聲自語前綴的函數 ---
def clean_murmur_prefix(text: str) -> str:
    """清理文本中的輕聲自語前綴，但保留連續性標記"""
    patterns = [
        r"^\s*\(輕聲自語\)\s*",
        r"^\s*（輕聲自語）\s*",
        r"^\s*\(自言自語\)\s*",
        r"^\s*（自言自語）\s*",
        r"^\s*\(喃喃自語\)\s*", 
        r"^\s*（喃喃自語）\s*",
        r"^\s*\(murmur\)\s*",
        r"^\s*（murmur）\s*",
        r"^\s*\(murmuring\)\s*",
        r"^\s*（murmuring）\s*"
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # 保留連接詞，但移除多餘空格
    for marker in CONTINUITY_MARKERS:
        if text.startswith(marker):
            # 保留標記但格式化為「標記，」的格式
            text = re.sub(f"^\s*{marker}\s*", f"{marker}，", text)
            break
    
    return text
# --- 結束添加 ---

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
            # 生成回復
            ai_result = await ai_service.generate_response(user_text=content)
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
            
            # 添加到歷史
            await add_to_history("user", content)
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
        
        # 設置狀態
        speaking_state = SpeakingState.PLAYING_MURMUR
        logger.info(f"Generating murmur, setting speaking_state to {speaking_state}")
        
        # --- 簡化：降低連續思考的複雜度，移除記憶檢索 ---
        # 決定是否要更換思考主題
        if thinking_thread_continuity >= MAX_THREAD_CONTINUITY:
            # 隨機選擇新主題，但避免選到當前主題
            available_themes = [t for t in THINKING_THEMES if t != current_thinking_topic]
            current_thinking_topic = random.choice(available_themes)
            thinking_thread_continuity = 0
        else:
            thinking_thread_continuity += 1
        
        # 構建簡化的連續思考上下文提示
        context_prompt = ""
        thinking_thread = ""
        
        # 只使用最後一條murmur作為上下文，不再從記憶中檢索
        if recent_murmurs:
            recent_murmurs_list = list(recent_murmurs)
            if len(recent_murmurs_list) > 0:
                # 最近的 murmur 作為直接延續的基礎
                last_murmur_content = recent_murmurs_list[-1]
                thinking_thread = f"你上一次的想法是：「{last_murmur_content}」，請自然延續這個想法。"
        # --- 結束簡化 ---
        
        # --- 修改：根據連續程度選擇不同的提示模板 ---
        prompt_template = "murmur_continuous" if thinking_thread_continuity > 0 else "murmur"
        
        # 獲取對應的 murmur 提示模板並填充變量
        template = PROMPT_TEMPLATES.get(prompt_template, PROMPT_TEMPLATES["murmur"])
        
        # 格式化提示模板
        if prompt_template == "murmur_continuous":
            murmur_prompt = template.format(
                context_prompt=context_prompt,
                current_topic=current_thinking_topic,
                thinking_thread=thinking_thread
            )
        else:
            murmur_prompt = template.format(
                context_prompt=context_prompt
            )
        # --- 結束修改 ---
        
        try:
            # 生成murmur
            ai_result = await ai_service.generate_response(
                system_prompt=murmur_prompt,
                history=conversation_history
            )
            
            if not ai_result or "final_response" not in ai_result:
                logger.error("AIService failed to generate murmur or returned invalid format.")
                speaking_state = SpeakingState.IDLE
                return
                
            ai_murmur_text = ai_result.get("final_response")
            ai_murmur_text = clean_murmur_prefix(ai_murmur_text)
            
            # --- 修改：根據連續思考模式調整相似度判斷 ---
            similarity_threshold = SIMILARITY_THRESHOLD_CONTINUOUS if thinking_thread_continuity > 0 else MURMUR_SIMILARITY_THRESHOLD
            
            if prompt_template == "murmur_continuous":
                # 檢查是否包含連續性標記，如包含則更寬容對待相似度
                has_continuity_marker = any(marker in ai_murmur_text for marker in CONTINUITY_MARKERS)
                if has_continuity_marker:
                    similarity_threshold *= 0.8  # 進一步降低相似度要求
                    logger.info(f"Continuity marker detected, lowering similarity threshold to {similarity_threshold}")
            
            # 如果是首次 murmur 或相似度在允許範圍內，接受這個 murmur
            if not recent_murmurs or not await is_murmur_too_similar(ai_murmur_text, recent_murmurs, similarity_threshold):
                # 將內容添加到最近 murmurs
                last_murmur_content = ai_murmur_text
                recent_murmurs.add(ai_murmur_text)
                if len(recent_murmurs) > 10:
                    # 移除最舊的 murmur (集合沒有直接的 pop first 方法)
                    oldest = next(iter(recent_murmurs))
                    recent_murmurs.remove(oldest)
                    logger.info(f"Removed oldest murmur from set: '{oldest}'")
            else:
                logger.warning(f"Generated murmur is too similar to existing ones, skipping: '{ai_murmur_text}'")
                speaking_state = SpeakingState.IDLE
                return
            # --- 結束修改 ---
                
            # 更新情緒
            murmur_emotion = ai_result.get("emotion", current_emotion)
            current_emotion = murmur_emotion
            
            # 添加到歷史
            await add_to_history("bot", ai_murmur_text, is_murmur=True)
            
            # 轉換為音頻
            tts_result = await tts_service.synthesize_speech(ai_murmur_text)
            audio_base64 = tts_result.get("audio") if tts_result else None
            audio_duration = tts_result.get("duration", len(ai_murmur_text) * 0.15)
            
            # 創建murmur消息
            bot_message = {
                "id": f"bot-murmur-{int(asyncio.get_event_loop().time() * 1000)}",
                "role": "bot",
                "content": ai_murmur_text,
                "bodyAnimationSequence": ai_result.get("body_animation_sequence"),
                "timestamp": None,
                "audioUrl": None,
                "isMurmur": True
            }
            
            # 保存並設置音頻URL
            if audio_base64:
                await save_audio_and_set_url(audio_base64, bot_message, is_murmur=True)
                
            # 發送murmur
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
                
            # 更新last_murmur_timestamp
            last_murmur_timestamp = datetime.utcnow()
            
            # 設置音頻播放完成後的任務
            buffer_time = min(MURMUR_BUFFER_MAX, 0.3 + audio_duration * 0.03)
            reset_task = asyncio.create_task(
                reset_speaking_after_duration(audio_duration + buffer_time)
            )
            
        except Exception as e:
            logger.error(f"Error generating murmur: {e}", exc_info=True)
            speaking_state = SpeakingState.IDLE

    async def is_murmur_too_similar(new_murmur: str, existing_murmurs: Set[str], threshold: float = MURMUR_SIMILARITY_THRESHOLD) -> bool:
        """檢查新的murmur是否與現有murmur太相似，簡化相似度檢測以提高速度"""
        # 如果完全相同，直接拒絕
        if new_murmur in existing_murmurs:
            return True
        
        # 只檢查最近的3個murmur，而不是全部
        recent_list = list(existing_murmurs)[-3:] if len(existing_murmurs) > 3 else existing_murmurs
        
        # 檢查與最近的murmur的相似度
        for existing_murmur in recent_list:
            # 簡化的相似度檢測，只檢查包含關係
            if (new_murmur in existing_murmur or existing_murmur in new_murmur):
                return True
            
        return False

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