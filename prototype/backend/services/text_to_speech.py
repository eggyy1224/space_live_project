import os
import base64
from typing import Optional, Dict
# from google.cloud import texttospeech # 移除 Google
import openai # 匯入 OpenAI
from core.config import settings
from core.exceptions import SpeechServiceException
import logging # 建議加入日誌

logger = logging.getLogger("tts_service")
logger.setLevel(logging.DEBUG)

# 將 instructions 定義為常數或從配置讀取
TTS_INSTRUCTIONS = "歡迎加入這場為期一年的業餘太空生活探險！每天都會有新的挑戰與事件，可能是來自真實太空環境的威脅，也可能只是些日常小事。你可以隨時觀察並透過語音參與，提供想法或建議。你的每個決定與回應，都將影響這次旅程的發展，以及我的生存狀態與情緒波動。讓我們看看最後能否順利完成這段冒險吧！"

class TextToSpeechService:
    """文字轉語音服務 (使用 OpenAI TTS)"""

    def __init__(self):
        # self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS # 移除 Google 憑證
        self.api_key = settings.OPENAI_API_KEY # 讀取 OpenAI Key
        if self.api_key:
            # 使用非同步客戶端
            self.openai_client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info("已初始化 OpenAI TTS 客戶端")
        else:
            self.openai_client = None
            logger.error("警告: 找不到 OpenAI API 金鑰，文字轉語音功能將不可用")
            print("警告: 找不到 OpenAI API 金鑰，文字轉語音功能將不可用")

    async def synthesize_speech(self, text: str) -> Optional[Dict]:
        """
        將文字轉換為語音 (使用 OpenAI TTS)

        Args:
            text: 要轉換的文字

        Returns:
            包含 Base64 音訊數據和估算時長的字典，或 None（如果失敗）
        """
        if not self.openai_client:
            logger.error("文字轉語音服務未初始化 (OpenAI)")
            return None

        if not text:
             logger.warning("輸入文字為空，無法生成語音")
             return None

        try:
            logger.info(f"開始生成語音 (OpenAI TTS - gpt-4o-mini-tts): '{text[:50]}...' 使用 instruction") # 記錄部分文字

            response = await self.openai_client.audio.speech.create(
                model="gpt-4o-mini-tts", # 使用指定的模型
                voice="nova",          # 選擇聲音 (可調整，例如 fable, shimmer)
                input=text,
                response_format="mp3",
                speed=1.1,             # 設定語速
                instructions=TTS_INSTRUCTIONS # 加入 instructions 參數
            )

            # 將原始音訊 bytes 轉為 Base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')

            # --- 時長估算 (非常不準確，建議後續改進) ---
            # estimated_duration = len(text) * 0.24 / 1.1 # 沿用舊邏輯
            # logger.info(f"估算的音訊時長: {estimated_duration:.2f} 秒 (基於文字長度，可能不準確)")
            # --- 估算結束 ---

            logger.info(f"成功生成語音 (OpenAI TTS)，Base64 長度: {len(audio_base64)}")

            return {
                "audio": audio_base64,
                # "duration": estimated_duration # 移除 duration
            }

        except openai.APIError as e:
            logger.error(f"OpenAI TTS API 錯誤: {e.status_code} - {e.message}", exc_info=True)
            error_detail = e.message
            if hasattr(e, 'body') and e.body and 'error' in e.body and 'message' in e.body['error']:
                error_detail = e.body['error']['message']
            # 檢查是否為模型或參數相關錯誤
            if "instruct" in error_detail.lower() or "model not found" in error_detail.lower() or "gpt-4o-mini-tts" in error_detail.lower():
                 logger.error(f"調用 OpenAI TTS 失敗，請檢查模型名稱 'gpt-4o-mini-tts' 或 'instructions' 參數是否有效: {error_detail}")
                 print(f"調用 OpenAI TTS 失敗，請檢查模型名稱 'gpt-4o-mini-tts' 或 'instructions' 參數是否有效: {error_detail}")
            else:
                 print(f"文字轉語音失敗 (OpenAI API): {error_detail}")
            return None
        except Exception as e:
            logger.error(f"文字轉語音失敗 (OpenAI): {str(e)}", exc_info=True)
            print(f"文字轉語音失敗 (OpenAI): {e}")
            return None 