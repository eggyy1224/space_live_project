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
TTS_INSTRUCTIONS = "說台語＋English"

# 允許的聲音清單
ALLOWED_TTS_VOICES = {
    "alloy", "ash", "ballad", "coral", "echo", "fable",
    "onyx", "nova", "sage", "shimmer", "verse",
}

DEFAULT_TTS_VOICE = "coral"
DEFAULT_TTS_SPEED = 1.2  # 與舊版保持一致
MIN_TTS_SPEED = 0.5
MAX_TTS_SPEED = 3.0

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

    async def synthesize_speech(
        self,
        text: str,
        instructions: Optional[str] = None,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
    ) -> Optional[Dict]:
        """
        將文字轉換為語音 (使用 OpenAI TTS)

        Args:
            text: 要轉換的文字
            instructions: 可選，傳入給 TTS 模型的 instructions；未提供時使用預設常數

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
            logger.info(
                f"開始生成語音 (OpenAI TTS - gpt-4o-mini-tts): '{text[:50]}...' 使用 instruction/voice/speed"
            )  # 記錄部分文字

            # 若呼叫端未提供，回退到預設值；同時限制聲音/語速範圍
            effective_instructions = instructions or TTS_INSTRUCTIONS

            cand_voice = (voice or DEFAULT_TTS_VOICE).strip().lower()
            if cand_voice not in ALLOWED_TTS_VOICES:
                logger.warning(f"TTS voice '{voice}' 不在允許清單內，已回退為 '{DEFAULT_TTS_VOICE}'")
                effective_voice = DEFAULT_TTS_VOICE
            else:
                effective_voice = cand_voice

            if isinstance(speed, (int, float)):
                clamped = max(MIN_TTS_SPEED, min(MAX_TTS_SPEED, float(speed)))
                if clamped != speed:
                    logger.warning(
                        f"TTS speed {speed} 超出允許範圍 [{MIN_TTS_SPEED}, {MAX_TTS_SPEED}]，已調整為 {clamped}"
                    )
                effective_speed = clamped
            else:
                effective_speed = DEFAULT_TTS_SPEED

            response = await self.openai_client.audio.speech.create(
                model="gpt-4o-mini-tts",  # 使用指定的模型
                voice=effective_voice,     # 可被呼叫端覆蓋
                input=text,
                response_format="mp3",
                speed=effective_speed,     # 可被呼叫端覆蓋
                instructions=effective_instructions,  # 可被呼叫端覆蓋
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
