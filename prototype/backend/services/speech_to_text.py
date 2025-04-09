import os
# import base64 # 不再直接需要
import logging
from typing import Optional, Dict, Any
# from google.cloud import speech # 移除 Google
import openai # 匯入 OpenAI
from core.config import settings
from core.exceptions import SpeechServiceException

# 設置日誌
logger = logging.getLogger("speech_service")
logger.setLevel(logging.DEBUG)

class SpeechToTextService:
    """語音轉文字服務 (使用 OpenAI Whisper)"""

    def __init__(self):
        # self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS # 移除 Google 憑證
        self.api_key = settings.OPENAI_API_KEY # 讀取 OpenAI Key
        if self.api_key:
            # 使用非同步客戶端
            self.openai_client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info("已初始化 OpenAI Whisper 客戶端")
        else:
            self.openai_client = None
            logger.error("警告: 找不到 OpenAI API 金鑰，語音轉文字功能將不可用")
            print("警告: 找不到 OpenAI API 金鑰，語音轉文字功能將不可用")

    async def transcribe_audio(self, audio_data: bytes, mime_type: str = "audio/webm;codecs=opus") -> Dict[str, Any]:
        """
        將音訊轉換為文字 (使用 OpenAI Whisper)

        Args:
            audio_data: 音訊數據 (bytes)
            mime_type: 音頻的MIME類型 (主要用於推斷檔名後綴)

        Returns:
            包含文字和狀態的字典
        """
        if not self.openai_client:
            logger.error("語音轉文字服務未初始化 (OpenAI)")
            return {"text": "", "success": False, "error": "語音服務未初始化"}

        try:
            logger.info(f"開始處理音頻 (OpenAI)，大小: {len(audio_data)} 字節，MIME類型: {mime_type}")

            # 從 mime_type 推斷檔名後綴，預設為 webm
            extension = "webm"
            if "ogg" in mime_type:
                extension = "ogg"
            elif "wav" in mime_type:
                extension = "wav"
            elif "mp3" in mime_type or "mpeg" in mime_type:
                extension = "mp3"
            elif "m4a" in mime_type:
                extension = "m4a"
            # 可以根據需要添加更多格式

            file_tuple = (f"audio.{extension}", audio_data)
            logger.info(f"準備上傳檔案: {file_tuple[0]}")

            # 呼叫 OpenAI Whisper API
            response = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=file_tuple,
                language="zh", # 指定語言為中文
                response_format="json" # 或 verbose_json
            )

            # 提取文字 (確保 response 和 response.text 存在)
            transcript = response.text if response and hasattr(response, 'text') else ""

            if transcript:
                logger.info(f"最終識別文字 (OpenAI): '{transcript}'")
                return {
                    "text": transcript,
                    "success": True,
                    "confidence": None # Whisper 標準回應不提供置信度
                }
            else:
                # 檢查是否有 API 返回的錯誤信息 (雖然通常會拋出異常)
                error_msg = "未能識別語音內容"
                if response and hasattr(response, 'error') and response.error:
                   error_msg = response.error.get('message', error_msg)

                logger.warning(f"未能識別語音內容 (OpenAI): {error_msg}")
                return {"text": "", "success": False, "error": error_msg}

        except openai.APIError as e:
            # 處理 OpenAI 特定錯誤
            logger.error(f"OpenAI API 錯誤: {e.status_code} - {e.message}", exc_info=True)
            # 嘗試提取更詳細的錯誤信息
            error_detail = e.message
            if hasattr(e, 'body') and e.body and 'error' in e.body and 'message' in e.body['error']:
                error_detail = e.body['error']['message']
            return {"text": "", "success": False, "error": f"OpenAI API 錯誤: {error_detail}"}
        except Exception as e:
            logger.error(f"語音轉文字失敗 (OpenAI): {str(e)}", exc_info=True)
            return {"text": "", "success": False, "error": str(e)} 