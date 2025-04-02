import os
import base64
import logging
from typing import Optional, Dict, Any
from google.cloud import speech
from core.config import settings
from core.exceptions import SpeechServiceException

# 設置日誌
logger = logging.getLogger("speech_service")
logger.setLevel(logging.DEBUG)

class SpeechToTextService:
    """語音轉文字服務"""
    
    def __init__(self):
        # 確認憑證路徑
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        if self.credentials_path and os.path.exists(self.credentials_path):
            self.client = speech.SpeechClient()
            logger.info(f"已初始化Google Speech-to-Text客戶端")
        else:
            self.client = None
            logger.error(f"警告: 找不到語音憑證檔案，語音轉文字功能將不可用")
            print(f"警告: 找不到語音憑證檔案，語音轉文字功能將不可用")
    
    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/webm;codecs=opus") -> Dict[str, Any]:
        """
        將音訊轉換為文字
        
        Args:
            audio_data: 音訊數據
            mime_type: 音頻的MIME類型
            
        Returns:
            包含文字和狀態的字典
        """
        if not self.client:
            logger.error("語音轉文字服務未初始化")
            return {"text": "", "success": False, "error": "語音服務未初始化"}
            
        try:
            logger.info(f"開始處理音頻，大小: {len(audio_data)} 字節，MIME類型: {mime_type}")
            
            # 檢查音頻數據開頭以判斷格式
            header = audio_data[:10] if len(audio_data) >= 10 else audio_data
            header_hex = ' '.join([f'{b:02x}' for b in header])
            logger.info(f"音頻數據頭部: {header_hex}")
            
            # 設定音訊配置
            audio = speech.RecognitionAudio(content=audio_data)
            
            # 根據MIME類型決定編碼
            encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
            sample_rate = 48000  # 默認採樣率
            
            if "webm" in mime_type and "opus" in mime_type:
                encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
                logger.info("使用WebM-Opus編碼")
            elif "webm" in mime_type:
                encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
                logger.info("使用WebM編碼")
            elif "ogg" in mime_type and "opus" in mime_type:
                encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
                logger.info("使用OGG-Opus編碼")
            else:
                # 嘗試自動檢測格式
                if header.startswith(b'\x1aE\xdf\xa3'):
                    logger.info("檢測到WebM格式")
                    encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
                elif header.startswith(b'OggS'):
                    logger.info("檢測到OGG格式")
                    encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
                else:
                    logger.info("無法確定格式，使用默認的WebM-Opus")
                    encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
                
            # 設置更詳細的配置
            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=sample_rate,
                language_code="zh-TW",
                enable_automatic_punctuation=True,
                model="default",
                use_enhanced=True,  # 使用增強模型
                audio_channel_count=1,  # 單聲道
                enable_separate_recognition_per_channel=False,
                max_alternatives=1,
            )
            
            logger.info(f"開始轉錄音頻，使用編碼: {encoding.name}, 採樣率: {sample_rate}Hz")
            
            # 轉錄音訊
            response = self.client.recognize(config=config, audio=audio)
            
            # 檢查和記錄響應
            if response.results:
                logger.info(f"收到 {len(response.results)} 個識別結果")
            else:
                logger.warning("未收到任何識別結果")
            
            # 提取文字
            transcript = ""
            confidence = 0.0
            
            if response.results:
                for i, result in enumerate(response.results):
                    if result.alternatives:
                        alt_text = result.alternatives[0].transcript
                        alt_confidence = result.alternatives[0].confidence
                        logger.info(f"結果 {i+1}: '{alt_text}' (置信度: {alt_confidence:.2f})")
                        transcript += alt_text
                        confidence = max(confidence, alt_confidence)
            
            if transcript:
                logger.info(f"最終識別文字: '{transcript}' (置信度: {confidence:.2f})")
                return {
                    "text": transcript, 
                    "success": True, 
                    "confidence": confidence
                }
            else:
                logger.warning("未能識別語音內容")
                return {"text": "", "success": False, "error": "未能識別語音內容"}
            
        except Exception as e:
            logger.error(f"語音轉文字失敗: {str(e)}", exc_info=True)
            return {"text": "", "success": False, "error": str(e)} 