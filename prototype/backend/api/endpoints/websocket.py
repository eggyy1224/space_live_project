import json
import asyncio
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import random
import os
import base64

from services.emotion import EmotionAnalyzer
from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from services.animation import AnimationService
from core.config import settings
from utils.logger import logger

# 建立服務實例
emotion_analyzer = EmotionAnalyzer()
ai_service = AIService()
tts_service = TextToSpeechService()
animation_service = AnimationService()

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
    current_morph_targets = animation_service.calculate_morph_targets("neutral")
    emotion_confidence = 0.0  # 情緒置信度
    transition_speed = settings.TRANSITION_SPEED  # 表情過渡速度
    
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
                    
                    # 計算平滑過渡的 Morph Targets
                    target_morph = animation_service.calculate_morph_targets(next_emotion)
                    transition_morph = animation_service.create_transition_morph(
                        current_morph_targets, target_morph, transition_speed
                    )
                    
                    # 更新當前表情狀態
                    current_emotion = next_emotion
                    current_morph_targets = transition_morph
                    
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
                        "morphTargets": transition_morph,
                        "emotion": current_emotion,
                        "confidence": emotion_confidence,
                        "audio": audio_base64,
                        "hasSpeech": audio_base64 is not None,
                        "speechDuration": audio_duration,
                        "characterState": ai_service.character_state  # 添加角色狀態
                    })
                    
                    # 持續發送表情更新，實現平滑過渡
                    asyncio.create_task(
                        send_transition_updates(websocket, transition_morph, target_morph, current_emotion)
                    )
                
                elif message["type"] == "chat-message":
                    # 處理前端傳來的文字訊息
                    logger.info(f"收到聊天訊息: {message}")
                    user_text = message["message"]

                    # --- 恢復原來的邏輯 ---
                    # 分析情緒 (這部分可以考慮移除或調整，因為主要情緒來自 LLM keyframes)
                    # emotion, confidence = emotion_analyzer.analyze(user_text)
                    # logger.info(f"初步分析情緒結果: {emotion}, 置信度: {confidence}")
                    # next_emotion = emotion # 暫時使用初步分析結果，或設為 neutral
                    # current_emotion = next_emotion # 更新當前情緒狀態

                    # --- 調用 AI Service 生成回應和 Keyframes ---
                    try:
                        # 調用 generate_response，預期返回包含 final_response 和 emotional_keyframes 的字典
                        # 注意：這裡暫時不傳遞初步分析的情緒，讓 DialogueGraph 決定
                        ai_result = await ai_service.generate_response(user_text) # 移除 current_emotion

                        # 提取結果
                        ai_response = ai_result.get("final_response", "抱歉，我好像有點短路了...")
                        emotional_keyframes = ai_result.get("emotional_keyframes") # 可能為 None

                        logger.info(f"AI 回應: {ai_response}")
                        if emotional_keyframes:
                            logger.info(f"生成的情緒 Keyframes: {emotional_keyframes}")
                        else:
                             logger.warning("AI Service 未返回有效的 emotional_keyframes")


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

# 發送表情過渡更新
async def send_transition_updates(websocket: WebSocket, start_morph: Dict[str, float], 
                              target_morph: Dict[str, float], emotion: str):
    try:
        steps = settings.TRANSITION_STEPS  # 過渡步驟數
        delay = settings.TRANSITION_DELAY  # 步驟間延遲
        
        for step in range(1, steps + 1):
            # 計算當前步驟的表情值
            progress = step / steps
            current_morph = {}
            
            for key in start_morph:
                start_val = start_morph[key]
                target_val = target_morph.get(key, 0.0)
                # 線性插值
                current_morph[key] = start_val + (target_val - start_val) * progress
            
            # 發送更新
            await websocket.send_json({
                "type": "morph_update",
                "morphTargets": current_morph,
                "emotion": emotion,
                "progress": progress
            })
            
            # 延遲
            await asyncio.sleep(delay)
            
    except Exception as e:
        print(f"發送表情過渡更新錯誤: {e}")

# --- 移除 send_lipsync_frames 輔助函數 ---
# async def send_lipsync_frames(websocket: WebSocket, frames: List[Dict[str, float]], emotion: str):
#     try:
#         if not frames:
#             print("警告: 未提供唇型同步幀")
#             return
#             
#         # 開始唇型同步前先等待一小段時間，讓語音開始播放
#         await asyncio.sleep(0.05)  # 減少初始延遲，使口型盡快開始
#         
#         # 計算每幀的延遲時間，調整為更流暢的幀率
#         frame_delay = 1 / 30  # 約30fps，使動畫更流暢
#         
#         # 發送更少的幀，但保持同步
#         skip_interval = max(1, len(frames) // 60)  # 控制幀數，避免發送過多幀
#         
#         # 為眨眼動作添加隨機時刻
#         blink_frames = []
#         if len(frames) > 60:  # 只在較長的序列中添加額外的眨眼
#             blink_times = random.randint(1, max(1, len(frames) // 120))  # 控制眨眼次數
#             for _ in range(blink_times):
#                 # 避免在開始和結束時添加眨眼
#                 blink_idx = random.randint(15, len(frames) - 30) // skip_interval
#                 blink_frames.append(blink_idx)
#         
#         try:
#             for i in range(0, len(frames), skip_interval):
#                 frame_index = i // skip_interval
#                 frame = frames[i].copy()  # 複製一份，避免修改原始數據
#                 
#                 # 檢查是否需要在此幀添加額外的眨眼
#                 if frame_index in blink_frames:
#                     frame["eyeBlinkLeft"] = 0.9
#                     frame["eyeBlinkRight"] = 0.9
#                 elif frame_index - 1 in blink_frames:
#                     # 眨眼恢復階段
#                     frame["eyeBlinkLeft"] = 0.3
#                     frame["eyeBlinkRight"] = 0.3
#                 
#                 # 發送更新，包含更多信息，並傳遞情緒信息
#                 await websocket.send_json({
#                     "type": "lipsync_update",
#                     "morphTargets": frame,
#                     "frameIndex": frame_index,
#                     "totalFrames": (len(frames) + skip_interval - 1) // skip_interval,
#                     "hasSpeech": True,
#                     "emotion": emotion  # 添加情緒信息
#                 })
#                 
#                 # 等待到下一幀
#                 await asyncio.sleep(frame_delay)
#                 
#             # 最後發送完成幀，通知前端唇型同步結束
#             await websocket.send_json({
#                 "type": "lipsync_update",
#                 "morphTargets": animation_service.calculate_morph_targets(emotion),
#                 "frameIndex": len(frames) // skip_interval,
#                 "totalFrames": len(frames) // skip_interval,
#                 "hasSpeech": False,
#                 "emotion": emotion  # 添加情緒信息
#             })
#             
#         except Exception as e:
#             print(f"發送唇型同步幀錯誤 (內部循環): {e}")
#             
#     except Exception as e:
#         print(f"發送唇型同步幀錯誤: {e}") 
# --- 移除結束 --- 