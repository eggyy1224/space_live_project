from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class SpeechToTextResponse(BaseModel):
    """語音轉文字回應模型"""
    text: str
    success: bool
    error: Optional[str] = None

class TextToSpeechResponse(BaseModel):
    """文字轉語音回應模型"""
    audio: Optional[str] = None
    duration: float
    success: bool
    error: Optional[str] = None

class EmotionAnalysisResponse(BaseModel):
    """情緒分析回應模型"""
    emotion: str
    confidence: float

class OBSScreenshotResponse(BaseModel):
    """OBS 截圖回應模型"""
    success: bool
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    timestamp: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    source_type: Optional[str] = None
    source_name: Optional[str] = None
    error: Optional[str] = None

class OBSStatusResponse(BaseModel):
    """OBS 狀態回應模型"""
    connected: bool
    obs_version: Optional[str] = None
    websocket_version: Optional[str] = None
    current_scene: Optional[str] = None
    streaming: Optional[bool] = None
    recording: Optional[bool] = None
    error: Optional[str] = None

class OBSSourcesResponse(BaseModel):
    """OBS 來源列表回應模型"""
    success: bool
    current_scene: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class OBSScenesResponse(BaseModel):
    """OBS 場景列表回應模型"""
    success: bool
    current_scene: Optional[str] = None
    scenes: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class YouTubeChatMessageResponse(BaseModel):
    """YouTube 聊天室訊息回應模型"""
    id: str
    author: str
    message: str
    timestamp: str
    datetime: str
    elapsed_time: Optional[str] = None
    amount_value: Optional[float] = None
    amount_string: Optional[str] = None
    currency: Optional[str] = None
    message_type: str = "textMessage"
    author_channel_id: Optional[str] = None
    is_verified: bool = False
    is_owner: bool = False
    is_sponsor: bool = False
    is_moderator: bool = False

class YouTubeChatStatusResponse(BaseModel):
    """YouTube 聊天室監控狀態回應模型"""
    monitoring: bool
    video_id: Optional[str] = None
    message_count: int = 0
    chat_alive: bool = False

class YouTubeChatOperationResponse(BaseModel):
    """YouTube 聊天室操作回應模型"""
    success: bool
    message: str
    monitoring: bool
    video_id: Optional[str] = None
    error: Optional[str] = None

class YouTubeChatMessagesResponse(BaseModel):
    """YouTube 聊天室訊息列表回應模型"""
    success: bool
    messages: List[YouTubeChatMessageResponse]
    count: int
    error: Optional[str] = None 