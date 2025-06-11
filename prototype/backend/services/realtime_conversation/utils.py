"""
實時對話服務的工具函式模組
包含音頻處理、檔案操作等通用功能。
"""

import io
import os
import wave
import glob
import random
import logging

logger = logging.getLogger(__name__)


def pcm_to_wav(pcm_data: bytes) -> bytes:
    """將 PCM16 數據轉換為 WAV 格式"""
    if not pcm_data:
        return b''
        
    # WAV 文件參數
    sample_rate = 24000  # OpenAI Realtime API 使用 24kHz
    channels = 1  # 單聲道
    sample_width = 2  # 16-bit
    
    # 創建 WAV 文件
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    
    wav_buffer.seek(0)
    wav_data = wav_buffer.getvalue()
    
    return wav_data


def get_random_selfie_reference(selfies_dir: str) -> str:
    """從selfies資料夾中隨機選擇一張照片作為參考圖片"""
    try:
        # 搜尋所有支援的圖片格式
        selfie_patterns = [
            os.path.join(selfies_dir, "*.png"),
            os.path.join(selfies_dir, "*.jpg"),
            os.path.join(selfies_dir, "*.jpeg")
        ]
        
        all_selfies = []
        for pattern in selfie_patterns:
            all_selfies.extend(glob.glob(pattern))
        
        if not all_selfies:
            logger.warning(f"No selfie images found in {selfies_dir}, using default")
            return "202506091142.png"  # 回退到預設圖片
        
        # 隨機選擇一張照片
        selected_selfie = random.choice(all_selfies)
        # 只返回檔名，不包含路徑
        filename = os.path.basename(selected_selfie)
        
        logger.info(f"🎲 隨機選擇參考圖片: {filename} (從 {len(all_selfies)} 張照片中選擇)")
        return filename
        
    except Exception as e:
        logger.error(f"Error selecting random selfie: {e}")
        return "202506091142.png"  # 回退到預設圖片


def get_selfies_directory() -> str:
    """獲取自拍照片資料夾的絕對路徑"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "../selfies") 