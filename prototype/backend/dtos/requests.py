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

class OBSScreenshotRequest(BaseModel):
    """OBS 截圖請求模型"""
    source_name: Optional[str] = None
    scene_name: Optional[str] = None
    width: int = 1920
    height: int = 1080
    image_format: str = "png"  # png 或 jpg

class OBSConnectionRequest(BaseModel):
    """OBS 連接設定請求模型"""
    host: str = "localhost"
    port: int = 4455
    password: str = ""
    timeout: int = 10 