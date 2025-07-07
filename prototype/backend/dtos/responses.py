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