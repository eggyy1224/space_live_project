import json
import asyncio
from typing import Dict, List
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

# --- 新增：閒置設定 ---
IDLE_TIMEOUT_SECONDS = 30  # 閒置多少秒後觸發 murmur
IDLE_CHECK_INTERVAL_SECONDS = 5 # 每隔多少秒檢查一次閒置狀態
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
        self.active_connections.remove(websocket)

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
    
    # 記錄當前表情狀態，用於實現平滑過渡
    current_emotion = "neutral"
    # emotion_confidence = 0.0  # 情緒置信度 - 不再需要，由 AIService 決定
    last_activity_timestamp = datetime.utcnow() # <--- 新增：記錄最後活動時間
    idle_check_task = None # <--- 新增：閒置檢查任務

    async def idle_checker():
        """背景任務，定期檢查閒置狀態並觸發 murmur。"""
        nonlocal last_activity_timestamp, current_emotion
        while True:
            await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS)
            try:
                idle_duration = datetime.utcnow() - last_activity_timestamp
                # logger.debug(f"Client {websocket.client} idle duration: {idle_duration}") # Debug log

                if idle_duration > timedelta(seconds=IDLE_TIMEOUT_SECONDS):
                    logger.info(f"Client {websocket.client} idle timeout reached. Generating murmur...")

                    # 1. 觸發 Murmur 生成
                    murmur_prompt = "請生成一句符合當前情境和角色心境的內心獨白或 murmur。"
                    ai_result = None
                    try:
                        # 假設 generate_response 能處理 user_input=None 並返回情緒
                        ai_result = await ai_service.generate_response(
                            system_prompt=murmur_prompt
                        )
                        if not ai_result or "final_response" not in ai_result:
                             logger.error("AIService failed to generate murmur or returned invalid format.")
                             continue # 跳過此次 murmur

                        ai_murmur_text = ai_result.get("final_response")
                        # ---> 從 AI 結果獲取情緒
                        murmur_emotion = ai_result.get("emotion", current_emotion) # 如果 AI 沒給，保持原來的情緒
                        current_emotion = murmur_emotion # 更新當前情緒
                        logger.info(f"Generated murmur: '{ai_murmur_text}', Emotion: {current_emotion}")

                    except Exception as ai_err:
                        logger.error(f"Error generating murmur from AIService: {ai_err}", exc_info=True)
                        continue # 發生錯誤，跳過此次 murmur

                    # 2. 轉換為語音
                    tts_result = None
                    audio_base64 = None
                    audio_duration = len(ai_murmur_text) * 0.15 # 預設估算值
                    try:
                        if ai_murmur_text:
                            tts_result = await tts_service.synthesize_speech(ai_murmur_text)
                            if tts_result:
                                audio_base64 = tts_result.get("audio")
                                audio_duration = tts_result.get("duration", audio_duration)
                    except Exception as tts_err:
                        logger.error(f"Error synthesizing speech for murmur: {tts_err}", exc_info=True)
                        # 即使 TTS 失敗，還是可以發送文字 murmur

                    # 3. ---> 修改：使用 chat-message 格式推送 Murmur <---
                    # 創建機器人消息結構（與處理 chat-message 一致）
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
                        logger.info(f"Sent Emotional Trajectory for murmur, duration: {audio_duration:.2f}s")
                    # <--- 結束修改 ---

                    # 4. 重置閒置計時器
                    last_activity_timestamp = datetime.utcnow()

            except WebSocketDisconnect:
                logger.info(f"Idle checker detected disconnection for {websocket.client}. Stopping checker.")
                break # 連線斷開，退出檢查循環
            except Exception as e:
                logger.error(f"Error in idle_checker loop for {websocket.client}: {e}", exc_info=True)
                # 可以在這裡決定是否中斷檢查或繼續
                await asyncio.sleep(IDLE_CHECK_INTERVAL_SECONDS * 2) # 發生錯誤時稍等久一點

    try:
        # 啟動閒置檢查任務
        idle_check_task = asyncio.create_task(idle_checker())
        logger.info(f"Started idle checker task for client {websocket.client}")

        while True:
            data = await websocket.receive_text()
            last_activity_timestamp = datetime.utcnow() # <--- 更新活動時間

            try:
                message = json.loads(data)
                message_type = message.get("type")
                logger.info(f"Received message type '{message_type}' from {websocket.client}")

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
                    # --- 保持原有 chat-message 處理邏輯，但也要更新 last_activity_timestamp ---
                    # --- 注意：這裡的 AI 調用也應該獲取情緒並更新 current_emotion ---
                    logger.info(f"收到聊天訊息: {message}")
                    user_text = message.get("message")
                    if not user_text:
                        logger.warning("Received empty 'chat-message' message content.")
                        continue

                    T_recv = time.monotonic()
                    logger.info(f"[Perf] T_recv: {T_recv:.4f}", extra={"log_category": "PERFORMANCE"})

                    try:
                        T_ai_start = time.monotonic()
                        logger.info(f"[Perf] T_ai_start: {T_ai_start:.4f}", extra={"log_category": "PERFORMANCE"})
                        # ---> 修改：調用 AI 並獲取情緒
                        ai_result = await ai_service.generate_response(user_text)
                        T_ai_end = time.monotonic()
                        logger.info(f"[Perf] T_ai_end: {T_ai_end:.4f} (Duration: {(T_ai_end - T_ai_start)*1000:.2f} ms)", extra={"log_category": "PERFORMANCE"})

                        ai_response = ai_result.get("final_response", "抱歉，我好像有點短路了...")
                        # ---> 新增：更新情緒
                        response_emotion = ai_result.get("emotion", current_emotion)
                        current_emotion = response_emotion
                        # <--- 結束
                        emotional_keyframes = ai_result.get("emotional_keyframes")
                        body_animation_sequence = ai_result.get("body_animation_sequence")

                        logger.info(f"AI 回應: {ai_response}, Emotion: {current_emotion}") # <--- 添加情緒日誌
                        # ... (省略日誌和後續處理，邏輯保持不變) ...

                        T_tts_start = time.monotonic()
                        logger.info(f"[Perf] T_tts_start: {T_tts_start:.4f}", extra={"log_category": "PERFORMANCE"})
                        tts_result = await tts_service.synthesize_speech(ai_response)
                        T_tts_end = time.monotonic()
                        logger.info(f"[Perf] T_tts_end: {T_tts_end:.4f} (Duration: {(T_tts_end - T_tts_start)*1000:.2f} ms)", extra={"log_category": "PERFORMANCE"})
                        audio_base64 = tts_result.get("audio") if tts_result else None
                        audio_duration = tts_result.get("duration") if tts_result and "duration" in tts_result else len(ai_response) * 0.15

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

                    except Exception as e:
                        logger.error(f"Error processing 'chat-message': {e}", exc_info=True)
                        # 可以考慮發送錯誤訊息給前端
                        await websocket.send_json({"type": "error", "message": "處理您的訊息時發生錯誤。"})
                else:
                    logger.warning(f"Received unknown message type: {message_type}")

            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from message: {data}")
            except WebSocketDisconnect:
                # 這個異常應該在外部處理，但以防萬一
                logger.info(f"WebSocket disconnected while processing message for {websocket.client}")
                raise # 重新拋出以便外部 finally 處理
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
                # 可以考慮發送通用錯誤訊息
                try:
                     await websocket.send_json({"type": "error", "message": "處理訊息時發生內部錯誤。"})
                except WebSocketDisconnect:
                     pass # 如果發送錯誤時也斷線了，就不用管了

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {websocket.client}")
    except Exception as e:
        # 捕捉主循環中的意外錯誤
        logger.error(f"Unexpected error in websocket_endpoint for {websocket.client}: {e}", exc_info=True)
    finally:
        logger.info(f"Cleaning up connection for {websocket.client}")
        if idle_check_task and not idle_check_task.done():
            idle_check_task.cancel() # <--- 確保任務被取消
            logger.info(f"Cancelled idle checker task for client {websocket.client}")
        manager.disconnect(websocket)
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