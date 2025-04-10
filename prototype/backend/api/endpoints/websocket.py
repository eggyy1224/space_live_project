import json
import asyncio
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import random
import os
import base64

from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from core.config import settings
from utils.logger import logger

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
    print("connection open")
    
    # 記錄當前表情狀態，用於實現平滑過渡
    current_emotion = "neutral"
    emotion_confidence = 0.0  # 情緒置信度
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message["type"] == "message":
                    user_text = message["content"]
                    
                    # 分析情緒並獲取置信度
                    emotion, confidence = emotion_analyzer.analyze(user_text)
                    print(f"分析情緒結果: {emotion}, 置信度: {confidence}")
                    
                    # 根據置信度決定是否切換情緒
                    if confidence > emotion_confidence:
                        # 只有新情緒的置信度更高時才切換
                        next_emotion = emotion
                        emotion_confidence = confidence
                    else:
                        # 否則保持當前情緒
                        next_emotion = current_emotion
                    
                    # 更新當前表情狀態
                    current_emotion = next_emotion
                    
                    # 生成回復
                    ai_response = await ai_service.generate_response(user_text, current_emotion)
                    
                    # 轉換回復為語音
                    tts_result = await tts_service.synthesize_speech(ai_response)
                    audio_base64 = tts_result["audio"] if tts_result else None
                    audio_duration = tts_result["duration"] if tts_result else len(ai_response) * 0.3
                    
                    # 發送回覆
                    await websocket.send_json({
                        "type": "response",
                        "content": ai_response,
                        "emotion": current_emotion,
                        "confidence": emotion_confidence,
                        "audio": audio_base64,
                        "hasSpeech": audio_base64 is not None,
                        "speechDuration": audio_duration,
                        "characterState": ai_service.character_state  # 添加角色狀態
                    })
                    
                elif message["type"] == "chat-message":
                    # 處理前端傳來的文字訊息
                    logger.info(f"收到聊天訊息: {message}")
                    user_text = message["message"]

                    # --- 調用 AI Service 生成回應和 Keyframes ---
                    try:
                        # 調用 generate_response，預期返回包含 final_response 和 emotional_keyframes 的字典
                        # 注意：這裡暫時不傳遞初步分析的情緒，讓 DialogueGraph 決定
                        ai_result = await ai_service.generate_response(user_text) # 移除 current_emotion

                        # 提取結果
                        ai_response = ai_result.get("final_response", "抱歉，我好像有點短路了...")
                        emotional_keyframes = ai_result.get("emotional_keyframes") # 可能為 None
                        # suggested_body_animation = ai_result.get("bodyAnimationName") # 可能為 None <-- 暫時註解掉
                        # ---> 新增：測試用，固定返回 'SwingToLand' (修正拼寫)
                        suggested_body_animation = "SwingToLand" #test data
                        # <--- 結束

                        logger.info(f"AI 回應: {ai_response}")
                        if emotional_keyframes:
                            logger.info(f"生成的情緒 Keyframes: {emotional_keyframes}")
                        else:
                             logger.warning("AI Service 未返回有效的 emotional_keyframes")
                        if suggested_body_animation:
                            logger.info(f"建議的身體動畫: {suggested_body_animation}")
                        else:
                            logger.warning("AI Service 未返回有效的 bodyAnimationName")


                        # --- 後續處理：TTS, Lipsync, 發送訊息 ---

                        # 轉換回復為語音
                        tts_result = await tts_service.synthesize_speech(ai_response)
                        audio_base64 = tts_result.get("audio") if tts_result else None
                        # 修正：如果 tts_result 為 None 或不含 duration，則估算時間
                        audio_duration = tts_result.get("duration") if tts_result and "duration" in tts_result else len(ai_response) * 0.15 # 調整估算時間並添加檢查

                        # 創建機器人回覆的文字消息
                        bot_message = {
                            "id": f"bot-{int(asyncio.get_event_loop().time() * 1000)}",
                            "role": "bot",
                            "content": ai_response,
                            "bodyAnimationName": suggested_body_animation,
                            "timestamp": None,
                            "audioUrl": None # 稍後填充
                        }

                        # 如果有音頻，保存到文件並設置URL
                        if audio_base64:
                            # 生成唯一的文件名
                            audio_filename = f"{int(asyncio.get_event_loop().time() * 1000)}.mp3"
                            # 修正路徑查找方式，使其更健壯
                            backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                            audio_dir = os.path.join(backend_root, "audio")
                            os.makedirs(audio_dir, exist_ok=True) # 確保目錄存在
                            audio_filepath = os.path.join(audio_dir, audio_filename)

                            # 解碼並保存音頻
                            try:
                                if isinstance(audio_base64, str):
                                    if "," in audio_base64:
                                        audio_base64_data = audio_base64.split(",", 1)[1]
                                    else:
                                        audio_base64_data = audio_base64 # Assume it's pure base64

                                    # Decode base64 data
                                    audio_data = base64.b64decode(audio_base64_data)

                                    with open(audio_filepath, 'wb') as f:
                                        f.write(audio_data)

                                    if os.path.exists(audio_filepath) and os.path.getsize(audio_filepath) > 0:
                                        bot_message["audioUrl"] = f"/audio-file/{audio_filename}"
                                        logger.info(f"保存音頻文件成功: {audio_filepath}, 大小: {os.path.getsize(audio_filepath)} 字節")
                                    else:
                                        logger.error(f"保存音頻文件失敗: 文件不存在或大小為0 {audio_filepath}")
                                else:
                                    logger.error(f"音頻數據不是有效的字符串: {type(audio_base64)}")
                            except base64.binascii.Error as b64_error:
                                 logger.error(f"Base64 解碼錯誤: {b64_error}")
                            except Exception as e:
                                logger.error(f"保存音頻文件時發生未知錯誤: {e}", exc_info=True)


                        # 發送聊天文字回覆
                        await websocket.send_json({
                            "type": "chat-message",
                            "message": bot_message
                        })
                        logger.info("已發送聊天文字回覆")

                        # --- 發送 Emotional Trajectory ---
                        if emotional_keyframes:
                             # 使用 audio_duration 作為軌跡持續時間
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
                            # 如果沒有 keyframes，可以考慮發送一個默認的靜態表情或不發送
                            logger.warning("未生成 keyframes，不發送 emotionalTrajectory")
                            # 或者發送一個中性表情作為 fallback?
                            # await websocket.send_json({
                            #     "type": "morph_update",
                            #     "morphTargets": animation_service.calculate_morph_targets("neutral"),
                            #     "emotion": "neutral"
                            # })


                        # --- 移除後端唇型同步邏輯 ---
                        # # --- 生成並發送唇型同步序列 (如果需要的話) ---
                        # # 注意：唇型同步現在可能需要與 emotionalTrajectory 協調
                        # # 這裡的 lipsync_frames 可能需要調整，或者前端主要依賴 emotionalTrajectory
                        # # 暫時保留原有的唇型同步邏輯，但可能需要後續調整
                        # 
                        # # 獲取 lipsync 的基礎情緒 (例如，軌跡的第一個情緒，或保持 neutral)
                        # lipsync_base_emotion = emotional_keyframes[0]['tag'] if emotional_keyframes else 'neutral'
                        # 
                        # lipsync_frames = animation_service.create_lipsync_morph(
                        #     ai_response,
                        #     emotion=lipsync_base_emotion, # 使用基礎情緒
                        #     duration=audio_duration
                        # )
                        # if lipsync_frames:
                        #     # 發送唇型同步序列 (需要 emotion 參數)
                        #     asyncio.create_task(
                        #         send_lipsync_frames(websocket, lipsync_frames, lipsync_base_emotion) # 傳遞基礎情緒
                        #     )
                        #     logger.info("已啟動唇型同步幀發送任務")
                        # else:
                        #     logger.warning("未能生成唇型同步幀")
                        # --- 移除結束 ---

                    except WebSocketDisconnect:
                        logger.warning("處理 chat-message 時 WebSocket 連接斷開")
                        manager.disconnect(websocket)
                        #不需要做其他事，外層循環會處理
                    except Exception as e:
                        logger.error(f"處理 chat-message 時發生錯誤: {e}", exc_info=True)
                        try:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"處理您的消息時發生內部錯誤: {e}"
                            })
                        except Exception: # 如果連發送錯誤消息都失敗，就放棄
                            logger.error("發送錯誤消息給客戶端時也發生錯誤")


                    # --- 原來的邏輯結束 ---
                
                elif message["type"] == "get_character_state":
                    # 返回角色當前狀態
                    await websocket.send_json({
                        "type": "character_state_update",
                        "characterState": ai_service.character_state
                    })
                
                elif message["type"] == "update_character_state":
                    # 更新角色狀態
                    if "updates" in message and isinstance(message["updates"], dict):
                        ai_service.update_character_state(message["updates"])
                        await websocket.send_json({
                            "type": "character_state_update",
                            "characterState": ai_service.character_state
                        })
                
                elif message["type"] == "set_task":
                    # 設置當前任務
                    if "task" in message and isinstance(message["task"], str):
                        ai_service.set_current_task(message["task"])
                        await websocket.send_json({
                            "type": "task_update",
                            "task": ai_service.current_task
                        })
                
                elif message["type"] == "complete_task":
                    # 完成當前任務
                    success = message.get("success", True)
                    ai_service.complete_current_task(success)
                    await websocket.send_json({
                        "type": "task_complete",
                        "success": success,
                        "characterState": ai_service.character_state
                    })
                
                elif message["type"] == "advance_day":
                    # 推進一天
                    ai_service.advance_day()
                    await websocket.send_json({
                        "type": "day_advanced",
                        "day": ai_service.character_state["days_in_space"],
                        "characterState": ai_service.character_state
                    })
                
            except Exception as e:
                print(f"處理WebSocket消息錯誤: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("connection closed")