import json
import asyncio
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import random

from services.emotion import EmotionAnalyzer
from services.ai import AIService
from services.text_to_speech import TextToSpeechService
from services.animation import AnimationService
from core.config import settings

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
                    
                    # 生成唇型同步序列 - 使用語音的實際持續時間和當前情緒
                    lipsync_frames = animation_service.create_lipsync_morph(
                        ai_response, 
                        emotion=current_emotion,  # 傳遞當前情緒
                        duration=audio_duration
                    )
                    
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
                    })
                    
                    # 持續發送表情更新，實現平滑過渡
                    asyncio.create_task(
                        send_transition_updates(websocket, transition_morph, target_morph, current_emotion)
                    )
                    
                    # 發送唇型同步序列
                    asyncio.create_task(
                        send_lipsync_frames(websocket, lipsync_frames, current_emotion)
                    )
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

# 發送唇型同步幀
async def send_lipsync_frames(websocket: WebSocket, frames: List[Dict[str, float]], emotion: str):
    try:
        if not frames:
            print("警告: 未提供唇型同步幀")
            return
            
        # 開始唇型同步前先等待一小段時間，讓語音開始播放
        await asyncio.sleep(0.05)  # 減少初始延遲，使口型盡快開始
        
        # 計算每幀的延遲時間，調整為更流暢的幀率
        frame_delay = 1 / 30  # 約30fps，使動畫更流暢
        
        # 發送更少的幀，但保持同步
        skip_interval = max(1, len(frames) // 60)  # 控制幀數，避免發送過多幀
        
        # 為眨眼動作添加隨機時刻
        blink_frames = []
        if len(frames) > 60:  # 只在較長的序列中添加額外的眨眼
            blink_times = random.randint(1, max(1, len(frames) // 120))  # 控制眨眼次數
            for _ in range(blink_times):
                # 避免在開始和結束時添加眨眼
                blink_idx = random.randint(15, len(frames) - 30) // skip_interval
                blink_frames.append(blink_idx)
        
        try:
            for i in range(0, len(frames), skip_interval):
                frame_index = i // skip_interval
                frame = frames[i].copy()  # 複製一份，避免修改原始數據
                
                # 檢查是否需要在此幀添加額外的眨眼
                if frame_index in blink_frames:
                    frame["eyeBlinkLeft"] = 0.9
                    frame["eyeBlinkRight"] = 0.9
                elif frame_index - 1 in blink_frames:
                    # 眨眼恢復階段
                    frame["eyeBlinkLeft"] = 0.3
                    frame["eyeBlinkRight"] = 0.3
                
                # 發送更新，包含更多信息，並傳遞情緒信息
                await websocket.send_json({
                    "type": "lipsync_update",
                    "morphTargets": frame,
                    "frameIndex": frame_index,
                    "totalFrames": (len(frames) + skip_interval - 1) // skip_interval,
                    "hasSpeech": True,
                    "emotion": emotion  # 添加情緒信息
                })
                
                # 等待到下一幀
                await asyncio.sleep(frame_delay)
                
            # 最後發送完成幀，通知前端唇型同步結束
            await websocket.send_json({
                "type": "lipsync_update",
                "morphTargets": animation_service.calculate_morph_targets(emotion),
                "frameIndex": len(frames) // skip_interval,
                "totalFrames": len(frames) // skip_interval,
                "hasSpeech": False,
                "emotion": emotion  # 添加情緒信息
            })
            
        except Exception as e:
            print(f"發送唇型同步幀錯誤 (內部循環): {e}")
            
    except Exception as e:
        print(f"發送唇型同步幀錯誤: {e}") 