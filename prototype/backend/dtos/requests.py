from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class SpeechToTextRequest(BaseModel):
    """語音轉文字請求模型"""
    audio_base64: str

class TextToSpeechRequest(BaseModel):
    """文字轉語音請求模型"""
    text: str

class EmotionAnalysisRequest(BaseModel):
    """情緒分析請求模型"""
    text: str 