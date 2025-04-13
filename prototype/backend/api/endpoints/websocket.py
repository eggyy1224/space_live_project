import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import random
import os
import base64
import time
from datetime import datetime, timedelta

from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from core.config import settings
from utils.logger import logger

# --- 閒置設定 ---
IDLE_TIMEOUT_SECONDS = 30  # 閒置多少秒後觸發 murmur
IDLE_CHECK_INTERVAL_SECONDS = 5 # 每隔多少秒檢查一次閒置狀態
MURMUR_MIN_INTERVAL_SECONDS = 45  # <--- 修改：縮短兩次 murmur 之間的最小間隔（例如 45 秒）
# MURMUR_MAX_COUNT = 3  # <--- 移除：不再限制連續 murmur 次數
MAX_HISTORY_LENGTH = 20 # 保存的最大對話歷史輪數（用戶+機器人算一輪）
# --- 結束 ---

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

# WebSocket端點
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(f"WebSocket connection open for client: {websocket.client}")
    
    # --- 新增：為此連線創建一個異步鎖 ---   
    ai_processing_lock = asyncio.Lock()
    # --- 結束新增 ---

    # --- 新增：結構化對話歷史 ---   
    conversation_history: List[Dict[str, any]] = []
    # --- 結束新增 ---

    # 初始化連接狀態
    logger.info(f"Client connected: {websocket.client}")
    conversation_history = []
    last_activity_timestamp = datetime.utcnow()
    last_murmur_timestamp = None
    last_speaking_reset_timestamp = None  # 新增：追蹤最後一次重置說話狀態的時間
    recent_murmurs = set()  # 使用集合以避免重複
    current_emotion = "neutral"
    is_speaking = False  # 指示當前是否有語音在播放
    user_responded = False

    # 記錄當前表情狀態，用於實現平滑過渡
    # emotion_confidence = 0.0  # 情緒置信度 - 不再需要，由 AIService 決定
    idle_check_task = None # <--- 新增：閒置檢查任務

    # --- 添加 murmur 狀態追蹤 ---
    # murmur_count = 0 # <--- 移除：不再需要計數
    # --- 結束添加 ---

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

    async def reset_speaking_after_duration(duration_seconds: float):
        """在指定的秒數後重置語音播放狀態。"""
        nonlocal is_speaking, last_activity_timestamp, last_murmur_timestamp, last_speaking_reset_timestamp
        await asyncio.sleep(duration_seconds)
        # 記錄重置前的狀態以便調試
        speaking_before_reset = is_speaking
        is_speaking = False
        # 更新最後活動時間戳，以確保在語音結束後計時器從新開始計時
        last_activity_timestamp = datetime.utcnow() 
        last_speaking_reset_timestamp = datetime.utcnow()
        # 如果是murmur導致的語音，也更新murmur時間戳
        if last_murmur_timestamp is not None:
            last_murmur_timestamp = datetime.utcnow()
        logger.info(f"Reset is_speaking from {speaking_before_reset} to False after {duration_seconds:.2f} seconds and updated timestamps")

    async def idle_checker():
        """背景任務，定期檢查閒置狀態並觸發 murmur。"""
        nonlocal last_activity_timestamp, current_emotion, last_murmur_timestamp, recent_murmurs, user_responded, is_speaking
        while True:
            await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS)
            try:
                current_time = datetime.utcnow()
                idle_duration = current_time - last_activity_timestamp

                # --- 檢查是否應該觸發 murmur ---
                # 1. 必須達到閒置閾值
                # 2. 距離上次 murmur 必須超過最小間隔
                # 3. 當前不能有其他語音在播放
                # 4. 如果最後的語音重置時間很近，也應該等待
                current_speaking_state = is_speaking  # 記錄當前狀態用於日誌
                should_wait_after_speaking = False
                
                if last_speaking_reset_timestamp:
                    time_since_last_reset = current_time - last_speaking_reset_timestamp
                    should_wait_after_speaking = time_since_last_reset < timedelta(seconds=3)  # 至少等待3秒再觸發新的murmur
                
                if (idle_duration > timedelta(seconds=IDLE_TIMEOUT_SECONDS) and
                   (last_murmur_timestamp is None or 
                   current_time - last_murmur_timestamp > timedelta(seconds=MURMUR_MIN_INTERVAL_SECONDS)) and
                   not is_speaking and
                   not should_wait_after_speaking):
                    
                    time_since_reset = "N/A" if not last_speaking_reset_timestamp else f"{(current_time - last_speaking_reset_timestamp).total_seconds():.2f}s"
                    logger.info(f"Checking murmur conditions - idle: {idle_duration.total_seconds():.2f}s, " +
                                f"speaking: {current_speaking_state}, time since last reset: {time_since_reset}")

                    # --- 嘗試獲取鎖，如果鎖已被持有（表示正在處理用戶消息），則等待 ---                   
                    async with ai_processing_lock:
                        # 再次檢查閒置時間，避免在等待鎖的過程中用戶剛好發送了消息
                        if datetime.utcnow() - last_activity_timestamp <= timedelta(seconds=IDLE_TIMEOUT_SECONDS):
                            logger.info(f"User became active while waiting for lock in idle_checker. Skipping murmur.")
                            continue # 用户在等待锁期间变得活跃，跳过此次 murmur

                        # <--- 移除基於 murmur_count 重置計數器的邏輯 --->
                        # if murmur_count >= MURMUR_MAX_COUNT and user_responded:\n                        #    murmur_count = 0\n                        #    user_responded = False\n                        #    recent_murmurs.clear()\n                        \n                        # logger.info(f\"Client {websocket.client} idle timeout reached. Generating murmur... (Count: {murmur_count+1})\") # <-- 移除 Count 顯示\n                        logger.info(f"Client {websocket.client} idle timeout reached. Generating murmur...")\n

                        # 1. 觸發 Murmur 生成
                        context_prompt = ""
                        if recent_murmurs:
                            context_prompt = f"最近的幾句自言自語: {', '.join(list(recent_murmurs)[-3:])}\n避免重複，但可以適度延續之前的想法或開啟新話題。"
                        
                        # <-- 修改 Prompt，明確要求參考歷史 -->
                        murmur_prompt = f"""請生成一句角色的內心獨白或自言自語 (murmur)。符合以下條件：
1. 作為太空站的虛擬主播「星際小可愛」，反映當前情境和心境。
2. 參考提供的對話歷史(`history`)，特別是最近的互動或你自己的思考。
3. 內容應自然、簡短（約50字內），像是腦海中閃過的念頭。
4. **盡量有變化，可以延續之前的自言自語思路，或者開啟一個全新的、符合角色當前狀態的隨機想法。也可以是對最近用戶發言的無聲回味或思考。**
5. 目標是讓角色聽起來像是在持續思考，而不是機械重複。
{context_prompt}
"""

                        ai_result = None
                        ai_murmur_text = None
                        try:
                            # --- 傳遞歷史給 AI ---                           
                            ai_result = await ai_service.generate_response(\
                                system_prompt=murmur_prompt,\
                                history=conversation_history # <--- 傳遞歷史\
                            )
                            # --- 結束 ---                           
                            if not ai_result or "final_response" not in ai_result:
                                 logger.error("AIService failed to generate murmur or returned invalid format.")
                                 continue # 跳過此次 murmur

                            ai_murmur_text = ai_result.get("final_response")
                            
                            # 更嚴格的重複檢查 - 不僅檢查完全匹配，還檢查高度相似
                            skip_due_to_similarity = False
                            for existing_murmur in recent_murmurs:
                                # 簡單的相似度檢測 - 如果包含或被包含，認為太相似
                                if (ai_murmur_text in existing_murmur or 
                                    existing_murmur in ai_murmur_text or
                                    len(ai_murmur_text) > 0 and existing_murmur and 
                                    (len(set(ai_murmur_text.lower()) & set(existing_murmur.lower())) / len(set(ai_murmur_text.lower() + existing_murmur.lower())) > 0.7)):
                                    logger.warning(f"Generated murmur is too similar to existing: New: '{ai_murmur_text}', Existing: '{existing_murmur}', skipping...")
                                    skip_due_to_similarity = True
                                    break
                            
                            if skip_due_to_similarity:
                                continue
                                
                            if ai_murmur_text in recent_murmurs:
                                logger.warning(f"Generated murmur is a duplicate: '{ai_murmur_text}', skipping...")
                                continue
                            
                            recent_murmurs.add(ai_murmur_text)
                            if len(recent_murmurs) > 10:
                                recent_murmurs.pop()
                                
                            murmur_emotion = ai_result.get("emotion", current_emotion)
                            current_emotion = murmur_emotion
                            logger.info(f"Generated murmur: '{ai_murmur_text}', Emotion: {current_emotion}")

                            # --- 將生成的 murmur 添加到歷史 ---                           
                            await add_to_history("bot", ai_murmur_text, is_murmur=True)
                            # --- 結束 ---                           

                        except Exception as ai_err:
                            logger.error(f"Error generating murmur from AIService: {ai_err}", exc_info=True)
                            continue # 發生錯誤，跳過此次 murmur

                        # 2. 轉換為語音
                        tts_result = None
                        audio_base64 = None
                        audio_duration = len(ai_murmur_text) * 0.15 # 預設估算值
                        logger.info(f"Estimated initial audio duration for murmur: {audio_duration:.2f}s (based on text length)")
                        try:
                            if ai_murmur_text:
                                tts_start_time = time.monotonic()
                                tts_result = await tts_service.synthesize_speech(ai_murmur_text)
                                tts_end_time = time.monotonic()
                                logger.info(f"TTS processing time for murmur: {(tts_end_time - tts_start_time)*1000:.2f}ms")
                                
                                if tts_result:
                                    audio_base64 = tts_result.get("audio")
                                    audio_duration = tts_result.get("duration", audio_duration)
                                    logger.info(f"TTS succeeded for murmur, actual duration: {audio_duration:.2f}s")
                                else:
                                    logger.warning("TTS returned empty result for murmur")
                        except Exception as tts_err:
                            logger.error(f"Error synthesizing speech for murmur: {tts_err}", exc_info=True)
                            # 即使 TTS 失敗，還是可以發送文字 murmur

                        # 3. 使用 chat-message 格式推送 Murmur
                        # 創建機器人消息結構
                        bot_message = {
                            "id": f"bot-murmur-{int(asyncio.get_event_loop().time() * 1000)}",
                            "role": "bot",
                            "content": ai_murmur_text,
                            "bodyAnimationSequence": ai_result.get("body_animation_sequence"),
                            "timestamp": None,
                            "audioUrl": None, # 稍後填充
                            "isMurmur": True  # 標識這是一個自主生成的 murmur
                        }

                        # 如果有音頻，保存到文件並設置URL
                        if audio_base64:
                            # 生成唯一文件名
                            audio_filename = f"murmur-{int(asyncio.get_event_loop().time() * 1000)}.mp3"
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
                                    if os.path.exists(audio_filepath) and os.path.getsize(audio_filepath) > 0:
                                        bot_message["audioUrl"] = f"/audio-file/{audio_filename}"
                                        logger.info(f"Successfully saved murmur audio file: {audio_filepath}")
                                    else:
                                        logger.error(f"Failed to save murmur audio file or file is empty: {audio_filepath}")
                                else:
                                    logger.error(f"Audio data is not a valid string: {type(audio_base64)}")
                            except base64.binascii.Error as b64_error:
                                logger.error(f"Base64 decoding error: {b64_error}")
                            except Exception as e:
                                logger.error(f"Error saving murmur audio file: {e}", exc_info=True)

                        # 發送 chat-message 格式的 murmur
                        is_speaking = True
                        await websocket.send_json({
                            "type": "chat-message",
                            "message": bot_message
                        })
                        logger.info(f"Sent murmur as chat-message to client {websocket.client}")

                        # 如果有情緒關鍵幀，發送 emotionalTrajectory
                        emotional_keyframes = ai_result.get("emotional_keyframes")
                        if emotional_keyframes:
                            trajectory_payload = {
                                "duration": audio_duration,
                                "keyframes": emotional_keyframes
                            }
                            await websocket.send_json({
                                "type": "emotionalTrajectory",
                                "payload": trajectory_payload
                            })
                            logger.info(f"已發送 Emotional Trajectory，時長: {audio_duration:.2f}s")

                        # 告知客戶端語音播放完成，這將重置播放狀態
                        if audio_duration > 0 and audio_base64:
                            # 根據語音時長安排一個任務，在語音播放結束後重置 is_speaking
                            # 添加一些額外時間作為緩衝，隨著音頻時長增加，緩衝也適度增加
                            buffer_time = min(1.0, 0.5 + audio_duration * 0.05)  # 最小0.5秒，隨著音頻長度增加但不超過1秒
                            total_wait_time = audio_duration + buffer_time
                            reset_task = asyncio.create_task(reset_speaking_after_duration(total_wait_time))
                            logger.info(f"Scheduled reset_speaking_after_duration in {total_wait_time:.2f}s (audio: {audio_duration:.2f}s + buffer: {buffer_time:.2f}s)")
                            
                            # 額外安全措施：更新murmur時間戳
                            last_murmur_timestamp = datetime.utcnow()
                        else:
                            # 如果沒有音頻，立即重置說話狀態
                            is_speaking = False
                            logger.info("No audio for murmur, immediately reset is_speaking to False")

                        # 重置活動時間戳，因為我們剛剛處理了一個消息
                        last_activity_timestamp = datetime.utcnow()

            except WebSocketDisconnect:
                logger.info(f"Idle checker detected disconnection for {websocket.client}. Stopping checker.")
                break # 連線斷開，退出檢查循環
            except asyncio.CancelledError:
                 logger.info(f"Idle checker task cancelled for {websocket.client}.")
                 break # 捕獲取消錯誤並退出
            except Exception as e:
                logger.error(f"Error in idle_checker loop for {websocket.client}: {e}", exc_info=True)
                await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS * 2)

    try:
        idle_check_task = asyncio.create_task(idle_checker())
        logger.info(f"Started idle checker task for client {websocket.client}")

        while True:
            data = await websocket.receive_text()
            
            # --- 更新活動時間，並獲取鎖以處理用戶消息 ---           
            async with ai_processing_lock:
                last_activity_timestamp = datetime.utcnow() 
                user_responded = True
                # murmur_count = 0 # <-- 移除計數重置
                # --- 鎖定區間開始 ---

                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    logger.info(f"Received message type '{message_type}' from {websocket.client} while holding lock")

                    if message_type == "message":
                        user_text = message.get("content")
                        if not user_text:
                            logger.warning("Received empty 'message' content.")
                            continue

                        # 移除獨立的情緒分析器調用
                        # emotion, confidence = emotion_analyzer.analyze(user_text)
                        # print(f"分析情緒結果: {emotion}, 置信度: {confidence}")
                        # if confidence > emotion_confidence:
                        #     next_emotion = emotion
                        #     emotion_confidence = confidence
                        # else:
                        #     next_emotion = current_emotion
                        # current_emotion = next_emotion

                        # 生成回復 (包含文字和情緒)
                        ai_response = ""
                        response_emotion = current_emotion # 預設為當前情緒
                        ai_result = None
                        try:
                             # 假設 generate_response 返回包含 final_response 和 emotion 的字典
                            ai_result = await ai_service.generate_response(user_text=user_text)
                            if ai_result:
                                ai_response = ai_result.get("final_response", "嗯...我該說些什麼呢？")
                                response_emotion = ai_result.get("emotion", current_emotion) # 更新情緒
                                current_emotion = response_emotion # 更新 Websocket 狀態
                            else:
                                 logger.error("AIService returned None or empty result for user message.")
                                 ai_response = "抱歉，我好像沒聽清楚。"

                        except Exception as ai_err:
                            logger.error(f"Error generating response from AIService: {ai_err}", exc_info=True)
                            ai_response = "糟糕，我的思緒有點混亂。"

                        # 轉換回復為語音
                        tts_result = await tts_service.synthesize_speech(ai_response)
                        audio_base64 = tts_result.get("audio") if tts_result else None
                        audio_duration = tts_result.get("duration") if tts_result and "duration" in tts_result else len(ai_response) * 0.15

                        # 發送回覆
                        await websocket.send_json({
                            "type": "response",
                            "content": ai_response,
                            "emotion": current_emotion, # <--- 使用 AI 返回或更新後的情緒
                            # "confidence": emotion_confidence, # <-- 移除
                            "audio": audio_base64,
                            "hasSpeech": audio_base64 is not None,
                            "speechDuration": audio_duration,
                            "characterState": ai_service.character_state
                        })
                        logger.info(f"Sent response to client {websocket.client}")

                    elif message_type == "chat-message":
                        logger.info(f"收到聊天訊息: {message}")
                        user_text = message.get("message") # <-- 注意鍵名不同
                        if not user_text:
                            logger.warning("Received empty 'chat-message' message content.")
                            continue

                        T_recv = time.monotonic()
                        logger.info(f"[Perf] T_recv: {T_recv:.4f}", extra={"log_category": "PERFORMANCE"})

                        ai_response = ""
                        response_emotion = current_emotion
                        ai_result = None
                        emotional_keyframes = None
                        body_animation_sequence = None
                        audio_base64 = None
                        audio_duration = 0

                        # <--- 修改：收到用戶消息，表示用戶已回應 --->
                        # 設置播放狀態為 False，因為我們將開始一個新的回應
                        prev_speaking = is_speaking
                        is_speaking = False  # 重置語音播放狀態
                        logger.info(f"Received user message, reset is_speaking from {prev_speaking} to False")
                        user_responded = True
                        # <--- 修改結束 --->

                        try:
                            T_ai_start = time.monotonic()
                            logger.info(f"[Perf] T_ai_start: {T_ai_start:.4f}", extra={"log_category": "PERFORMANCE"})
                            ai_result = await ai_service.generate_response(user_text)
                            T_ai_end = time.monotonic()
                            logger.info(f"[Perf] T_ai_end: {T_ai_end:.4f} (Duration: {(T_ai_end - T_ai_start)*1000:.2f} ms)", extra={"log_category": "PERFORMANCE"})

                            if ai_result:
                                ai_response = ai_result.get("final_response", "抱歉，我好像有點短路了...")
                                response_emotion = ai_result.get("emotion", current_emotion)
                                current_emotion = response_emotion
                                emotional_keyframes = ai_result.get("emotional_keyframes")
                                body_animation_sequence = ai_result.get("body_animation_sequence")
                                logger.info(f"AI 回應: {ai_response}, Emotion: {current_emotion}") # <--- 添加情緒日誌
                            else:
                                logger.error("AIService returned None for chat-message")
                                ai_response = "看來我的迴路有點問題..."

                            # TTS處理 - 只調用一次
                            if ai_response:
                                T_tts_start = time.monotonic()
                                logger.info(f"[Perf] T_tts_start: {T_tts_start:.4f}", extra={"log_category": "PERFORMANCE"})
                                tts_result = await tts_service.synthesize_speech(ai_response)
                                T_tts_end = time.monotonic()
                                logger.info(f"[Perf] T_tts_end: {T_tts_end:.4f} (Duration: {(T_tts_end - T_tts_start)*1000:.2f} ms)", extra={"log_category": "PERFORMANCE"})
                                if tts_result:
                                    audio_base64 = tts_result.get("audio")
                                    audio_duration = tts_result.get("duration", len(ai_response) * 0.15)
                                    # 設置語音正在播放標誌
                                    is_speaking = True
                                    logger.info(f"TTS generated successfully, duration: {audio_duration:.2f}s, is_speaking set to True")
                                else:
                                    logger.warning("TTS returned no result, no audio will be played")

                        except Exception as e:
                            logger.error(f"Error during AI or TTS for chat-message: {e}", exc_info=True)
                            ai_response = "處理時發生了一點小插曲。"
                            # 重置音頻和動畫，避免發送不匹配的數據
                            audio_base64 = None
                            emotional_keyframes = None
                            body_animation_sequence = None

                        # 準備消息體
                        bot_message = {
                            "id": f"bot-{int(asyncio.get_event_loop().time() * 1000)}",
                            "role": "bot",
                            "content": ai_response,
                            "bodyAnimationSequence": body_animation_sequence,
                            "timestamp": None,
                            "audioUrl": None
                        }

                        if audio_base64:
                            audio_filename = f"{int(asyncio.get_event_loop().time() * 1000)}.mp3"
                            backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                            audio_dir = os.path.join(backend_root, "audio")
                            os.makedirs(audio_dir, exist_ok=True)
                            audio_filepath = os.path.join(audio_dir, audio_filename)
                            T_save_start = time.monotonic()
                            try:
                                if isinstance(audio_base64, str):
                                    audio_base64_data = audio_base64.split(",", 1)[1] if "," in audio_base64 else audio_base64
                                    audio_data = base64.b64decode(audio_base64_data)
                                    with open(audio_filepath, 'wb') as f:
                                        f.write(audio_data)
                                    if os.path.exists(audio_filepath) and os.path.getsize(audio_filepath) > 0:
                                        bot_message["audioUrl"] = f"/audio-file/{audio_filename}"
                                        T_save_end = time.monotonic()
                                        logger.info(f"[Perf] T_save_end: {T_save_end:.4f} (Duration: {(T_save_end - T_save_start)*1000:.2f} ms)", extra={"log_category": "PERFORMANCE"})
                                    else:
                                        logger.error(f"保存音頻文件失敗: 文件不存在或大小為0 {audio_filepath}")
                                else:
                                    logger.error(f"音頻數據不是有效的字符串: {type(audio_base64)}")
                            except base64.binascii.Error as b64_error:
                                logger.error(f"Base64 解碼錯誤: {b64_error}")
                            except Exception as e:
                                logger.error(f"保存音頻文件時發生未知錯誤: {e}", exc_info=True)

                        T_send_start = time.monotonic()
                        await websocket.send_json({
                            "type": "chat-message",
                            "message": bot_message
                        })
                        T_send_end = time.monotonic()
                        logger.info(f"[Perf] Total Backend Processing Time (chat-message): {(T_send_end - T_recv)*1000:.2f} ms", extra={"log_category": "PERFORMANCE"})

                        # 發送情緒軌跡（如果有的話）
                        if emotional_keyframes:
                            trajectory_payload = {
                                "duration": audio_duration,
                                "keyframes": emotional_keyframes
                            }
                            await websocket.send_json({
                                "type": "emotionalTrajectory",
                                "payload": trajectory_payload
                            })
                            logger.info(f"已發送 Emotional Trajectory，時長: {audio_duration:.2f}s")
                        else:
                            logger.info("No emotional keyframes available for this response")

                        # 告知客戶端語音播放完成，這將重置播放狀態
                        if audio_duration > 0 and audio_base64:
                            # 根據語音時長安排一個任務，在語音播放結束後重置 is_speaking
                            # 添加一些額外時間作為緩衝，隨著音頻時長增加，緩衝也適度增加
                            buffer_time = min(1.0, 0.5 + audio_duration * 0.05)  # 最小0.5秒，隨著音頻長度增加但不超過1秒
                            total_wait_time = audio_duration + buffer_time
                            reset_task = asyncio.create_task(reset_speaking_after_duration(total_wait_time))
                            logger.info(f"Scheduled reset_speaking_after_duration in {total_wait_time:.2f}s (audio: {audio_duration:.2f}s + buffer: {buffer_time:.2f}s)")
                        else:
                            # 如果沒有音頻，立即重置說話狀態
                            is_speaking = False
                            logger.info("No audio for response, immediately reset is_speaking to False")

                        # 重置活動時間戳，因為我們剛剛處理了一個消息
                        last_activity_timestamp = datetime.utcnow()

                    else:
                        logger.warning(f"Received unknown message type: {message_type}")

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from message: {data}")
                except WebSocketDisconnect: # 這個應該不太可能在鎖內部發生，但為了完整性加上
                    logger.info(f"WebSocket disconnected while processing message inside lock for {websocket.client}")
                    raise 
                except Exception as e:
                    logger.error(f"Error processing WebSocket message inside lock: {e}", exc_info=True)
                    try:
                        await websocket.send_json({"type": "error", "message": "處理訊息時發生內部錯誤。"})
                    except WebSocketDisconnect:
                        pass
                # --- 鎖在此處自動釋放 ---

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {websocket.client}")
    except asyncio.CancelledError:
        logger.info(f"Main websocket task cancelled for {websocket.client}")
        # 不需要再做什麼，finally 會處理清理工作
    except Exception as e:
        logger.error(f"Unexpected error in websocket_endpoint for {websocket.client}: {e}", exc_info=True)
    finally:
        logger.info(f"Cleaning up connection for {websocket.client}")
        if idle_check_task and not idle_check_task.done():
            idle_check_task.cancel()
            try:
                # 等待任務實際取消完成（可選，但更安全）
                await asyncio.wait_for(idle_check_task, timeout=1.0) 
            except asyncio.TimeoutError:
                logger.warning(f"Idle checker task for {websocket.client} did not cancel within timeout.")
            except asyncio.CancelledError:
                pass # 任務已被取消是正常的
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

# --- 舊的 emotion_analyzer (需要移除或替換) ---
# class SimpleEmotionAnalyzer:
#     def analyze(self, text):
#         # 這裡是一個非常基礎的實現，實際應用中會使用更複雜的模型
#         text_lower = text.lower()
#         if any(word in text_lower for word in ["開心", "高興", "太棒了", "好耶"]):
#             return "happy", 0.8
#         elif any(word in text_lower for word in ["傷心", "難過", "唉"]):
#             return "sad", 0.7
#         elif any(word in text_lower for word in ["生氣", "可惡", "討厭"]):
#             return "angry", 0.6
#         elif any(word in text_lower for word in ["驚訝", "哇", "真的嗎"]):
#             return "surprised", 0.5
#         return "neutral", 0.3

# emotion_analyzer = SimpleEmotionAnalyzer()
# --- 結束 ---