from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class SpeechToTextRequest(BaseModel):
    """語音轉文字請求模型"""
    audio_base64: str
    mime_type: Optional[str] = "audio/webm;codecs=opus"

class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None 