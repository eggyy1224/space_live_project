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