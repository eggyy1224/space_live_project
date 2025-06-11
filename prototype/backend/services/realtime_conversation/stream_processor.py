"""
資料流處理模組
處理音頻流的生成、轉換和測試模式功能。
"""

import asyncio
import io
import wave
import struct
import logging
from typing import AsyncIterator, AsyncGenerator

from .utils import pcm_to_wav

logger = logging.getLogger(__name__)


class StreamProcessor:
    """處理音頻資料流的生成和轉換"""
    
    def __init__(self):
        self.test_mode = False
    
    async def test_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """測試模式：模擬音頻回應"""
        logger.info("Running in test mode - generating simulated responses")
        
        chunk_count = 0
        last_response_time = 0
        
        async for chunk in audio_chunks:
            chunk_count += 1
            logger.info(f"Received audio chunk {chunk_count}: {len(chunk)} bytes")
            
            # 每收到幾個音頻片段就生成一個測試回應
            if chunk_count % 8 == 0:  # 每8個chunk回應一次（約2秒）
                # 生成一個簡單的測試音頻回應
                test_response = self._generate_test_audio_response(chunk_count)
                if test_response:
                    logger.info(f"Sending test audio response #{chunk_count // 8}: {len(test_response)} bytes")
                    yield test_response
                    
                # 添加小延遲模擬真實回應時間
                await asyncio.sleep(0.1)

    def _generate_test_audio_response(self, chunk_count: int) -> bytes:
        """生成測試音頻回應 - 創建真實的可播放 WAV 音頻"""
        logger.info(f"Generating test audio response #{chunk_count // 8}")
        
        # 生成一個簡短的 WAV 音頻文件（1秒的正弦波）
        sample_rate = 44100  # 44.1 kHz
        duration = 1.0  # 1 second
        frequency = 440  # A4 note (440 Hz)
        
        # 生成正弦波數據
        samples = []
        for i in range(int(sample_rate * duration)):
            # 生成正弦波，音量逐漸減小避免突然中斷
            t = i / sample_rate
            amplitude = 0.3 * (1 - t / duration)  # 逐漸減小的音量
            sample = amplitude * 32767 * (1 if i % (sample_rate // frequency) < (sample_rate // frequency // 2) else -1)
            samples.append(int(sample))
        
        # 創建 WAV 文件
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 單聲道
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # 寫入音頻數據
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))
        
        wav_buffer.seek(0)
        audio_data = wav_buffer.getvalue()
        
        logger.info(f"Generated WAV audio: {len(audio_data)} bytes")
        return audio_data
    
    def set_test_mode(self, enabled: bool):
        """設定是否啟用測試模式"""
        self.test_mode = enabled
        logger.info(f"Test mode {'enabled' if enabled else 'disabled'}")
    
    def is_test_mode(self) -> bool:
        """檢查是否為測試模式"""
        return self.test_mode 