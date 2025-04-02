import os
import base64
from typing import Optional, Dict
from google.cloud import texttospeech
from core.config import settings
from core.exceptions import SpeechServiceException

class TextToSpeechService:
    """文字轉語音服務"""
    
    def __init__(self):
        # 確認憑證路徑
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        if self.credentials_path and os.path.exists(self.credentials_path):
            self.client = texttospeech.TextToSpeechClient()
        else:
            self.client = None
            print(f"警告: 找不到語音憑證檔案，文字轉語音功能將不可用")
    
    async def synthesize_speech(self, text: str) -> Optional[Dict]:
        """
        將文字轉換為語音
        
        Args:
            text: 要轉換的文字
            
        Returns:
            包含音訊數據的字典，或None（如果失敗）
        """
        if not self.client:
            return None
            
        try:
            input_text = texttospeech.SynthesisInput(text=text)
            
            # 設定語音參數 - 僅指定語言和性別，讓Google選擇最佳語音
            voice = texttospeech.VoiceSelectionParams(
                language_code="zh-TW",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # 設定音訊參數 - 增加品質和語速調整
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.1,  # 稍微加快語速
                pitch=0.0,  # 標準音高
                volume_gain_db=0.0,  # 標準音量
                sample_rate_hertz=24000  # 提高採樣率提升音質
            )
            
            # 生成音訊
            response = self.client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )
            
            # 轉換為base64格式
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            # 計算音訊長度（考慮語速調整）
            audio_duration = len(text) * 0.24 / 1.1  # 每個中文字約0.24秒，考慮1.1倍速
            
            # 返回音訊資料
            return {
                "audio": audio_base64,
                "duration": audio_duration
            }
            
        except Exception as e:
            print(f"文字轉語音失敗: {e}")
            return None 