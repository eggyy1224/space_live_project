from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from ..endpoints.websocket import manager  # 導入 WebSocket 連接管理器
import uuid
import asyncio
from datetime import datetime
import json

# 設置日誌
logger = logging.getLogger(__name__)

# 創建路由
router = APIRouter()

# 定義請求模型
class SendMessageRequest(BaseModel):
    content: str
    message_type: Optional[str] = "chat-message"

class TriggerMurmurRequest(BaseModel):
    topic: Optional[str] = None
    force: Optional[bool] = False

class PlayAudioRequest(BaseModel):
    url: str
    interrupt: Optional[bool] = False

class EmotionalTrajectoryRequest(BaseModel):
    duration: float
    keyframes: List[Dict[str, Any]]

@router.post("/control/send-message")
async def send_message_to_frontend(request: SendMessageRequest):
    """
    透過 API 向前端發送消息 (模擬機器人回應)
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")
        
        # 構建消息
        bot_message = {
            "id": f"api-bot-{int(asyncio.get_event_loop().time() * 1000)}",
            "role": "bot",
            "content": request.content,
            "timestamp": datetime.utcnow().isoformat(),
            "audioUrl": None,
            "isFromAPI": True  # 標記這是來自 API 的消息
        }
        
        # 發送到所有連接的前端
        message_data = {
            "type": request.message_type,
            "message": bot_message
        }
        
        await manager.broadcast(json.dumps(message_data))
        
        logger.info(f"API 發送消息到前端: {request.content}")
        
        return {
            "success": True,
            "message": "消息已發送到前端",
            "connections": len(manager.active_connections)
        }
    
    except Exception as e:
        logger.error(f"API 發送消息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"發送消息失敗: {str(e)}")

@router.post("/control/trigger-murmur")
async def trigger_murmur(request: TriggerMurmurRequest):
    """
    透過 API 觸發前端的 murmur (自言自語)
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")
        
        # 構建觸發消息 - 這裡我們可以向 WebSocket 發送一個特殊的觸發信號
        trigger_data = {
            "type": "trigger-murmur",
            "payload": {
                "topic": request.topic,
                "force": request.force,
                "source": "api"
            }
        }
        
        await manager.broadcast(json.dumps(trigger_data))
        
        logger.info(f"API 觸發 murmur，主題: {request.topic}")
        
        return {
            "success": True,
            "message": "murmur 觸發信號已發送",
            "topic": request.topic
        }
    
    except Exception as e:
        logger.error(f"API 觸發 murmur 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"觸發 murmur 失敗: {str(e)}")

@router.post("/control/play-audio")
async def play_audio_on_frontend(request: PlayAudioRequest):
    """
    透過 API 在前端播放音頻
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")
        
        # 構建音頻播放消息
        audio_data = {
            "type": "play-audio",
            "id": f"api-audio-{uuid.uuid4().hex[:8]}",
            "url": request.url,
            "interrupt": request.interrupt
        }
        
        await manager.broadcast(json.dumps(audio_data))
        
        logger.info(f"API 觸發音頻播放: {request.url}")
        
        return {
            "success": True,
            "message": "音頻播放信號已發送",
            "url": request.url
        }
    
    except Exception as e:
        logger.error(f"API 播放音頻失敗: {e}")
        raise HTTPException(status_code=500, detail=f"播放音頻失敗: {str(e)}")

@router.post("/control/emotion-trajectory")
async def send_emotion_trajectory(request: EmotionalTrajectoryRequest):
    """
    透過 API 發送情緒軌跡到前端
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")
        
        # 構建情緒軌跡消息
        emotion_data = {
            "type": "emotionalTrajectory",
            "payload": {
                "duration": request.duration,
                "keyframes": request.keyframes
            }
        }
        
        await manager.broadcast(json.dumps(emotion_data))
        
        logger.info(f"API 發送情緒軌跡，時長: {request.duration}s")
        
        return {
            "success": True,
            "message": "情緒軌跡已發送",
            "duration": request.duration
        }
    
    except Exception as e:
        logger.error(f"API 發送情緒軌跡失敗: {e}")
        raise HTTPException(status_code=500, detail=f"發送情緒軌跡失敗: {str(e)}")

@router.get("/control/status")
async def get_frontend_status():
    """
    獲取前端連接狀態
    """
    return {
        "active_connections": len(manager.active_connections),
        "is_available": len(manager.active_connections) > 0,
        "connections_detail": [
            {"client": str(conn.client)} for conn in manager.active_connections
        ]
    }

@router.post("/control/broadcast")
async def broadcast_custom_message(message: Dict[str, Any]):
    """
    向前端廣播自定義消息
    """
    try:
        if not manager.active_connections:
            raise HTTPException(status_code=503, detail="沒有活動的前端連接")
        
        await manager.broadcast(json.dumps(message))
        
        logger.info(f"API 廣播自定義消息: {message.get('type', 'unknown')}")
        
        return {
            "success": True,
            "message": "自定義消息已廣播",
            "connections": len(manager.active_connections)
        }
    
    except Exception as e:
        logger.error(f"API 廣播消息失敗: {e}")
        raise HTTPException(status_code=500, detail=f"廣播消息失敗: {str(e)}") 