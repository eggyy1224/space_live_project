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

class YouTubeChatStartRequest(BaseModel):
    """YouTube 聊天室監控開始請求模型"""
    video_url_or_id: str

class YouTubeChatChannelRequest(BaseModel):
    """YouTube 聊天室頻道監控請求模型"""
    channel_id: str

class YouTubeChatSearchRequest(BaseModel):
    """YouTube 聊天室訊息搜尋請求模型"""
    keyword: str
    limit: int = 50

class YouTubeChatUserRequest(BaseModel):
    """YouTube 聊天室特定使用者訊息請求模型"""
    username: str
    limit: int = 20 