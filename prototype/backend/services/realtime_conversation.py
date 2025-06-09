import asyncio
import logging
from typing import AsyncIterator, AsyncGenerator
import io
import base64
import wave
import struct
import json
import websockets
from websockets.exceptions import ConnectionClosed

import openai

from core.config import settings

logger = logging.getLogger(__name__)


class RealtimeConversationService:
    """Wrapper around OpenAI real-time conversation API."""

    def __init__(self) -> None:
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.test_mode = False  # 測試模式標誌

    async def stream_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks to OpenAI and yield TTS audio bytes."""
        try:
            # 使用正確的 OpenAI Realtime API WebSocket 連接
            async for audio_response in self._openai_realtime_websocket(audio_chunks):
                yield audio_response
        except Exception as exc:  # pragma: no cover - network
            logger.error("Realtime conversation failed: %s", exc)
            logger.info("Falling back to test mode...")
            
            # 回退到測試模式
            self.test_mode = True
            async for test_audio in self._test_conversation(audio_chunks):
                yield test_audio

    async def _openai_realtime_websocket(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """使用 WebSocket 連接到 OpenAI Realtime API"""
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        logger.info("Connecting to OpenAI Realtime API via WebSocket...")
        
        try:
            async with websockets.connect(url, additional_headers=headers) as ws:
                logger.info("Connected to OpenAI Realtime API")
                
                # 發送初始會話配置
                await self._send_session_update(ws)
                
                # 創建音頻接收隊列
                audio_queue = asyncio.Queue()
                
                # 啟動並行任務
                send_task = asyncio.create_task(self._send_audio_to_openai(ws, audio_chunks))
                receive_task = asyncio.create_task(self._receive_openai_responses(ws, audio_queue))
                
                try:
                    # 從隊列中讀取音頻回應
                    while True:
                        try:
                            audio_data = await asyncio.wait_for(audio_queue.get(), timeout=1.0)
                            if audio_data is None:  # 結束信號
                                break
                            yield audio_data
                        except asyncio.TimeoutError:
                            # 檢查任務是否還在運行
                            if receive_task.done() or send_task.done():
                                break
                            continue
                            
                except asyncio.CancelledError:
                    logger.info("Realtime conversation cancelled")
                finally:
                    # 取消所有任務
                    receive_task.cancel()
                    send_task.cancel()
                    
        except ConnectionClosed:
            logger.error("WebSocket connection to OpenAI was closed")
            raise
        except Exception as e:
            logger.error(f"Error in OpenAI Realtime WebSocket: {e}")
            raise

    async def _send_session_update(self, ws):
        """發送會話配置到 OpenAI"""
        session_event = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": "你是一個有用的AI助手。請用中文簡短回應，避免過長的回答。",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.6,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 1000
                }
            }
        }
        await ws.send(json.dumps(session_event))
        logger.info("Sent session configuration to OpenAI")

    async def _send_audio_to_openai(self, ws, audio_chunks: AsyncIterator[bytes]):
        """發送音頻數據到 OpenAI"""
        try:
            chunk_count = 0
            async for chunk in audio_chunks:
                if chunk:
                    chunk_count += 1
                    # 前端現在直接發送 PCM16 格式的音頻位元組數據
                    # 直接進行 base64 編碼並發送到 OpenAI
                    base64_audio = base64.b64encode(chunk).decode('utf-8')
                    audio_event = {
                        "type": "input_audio_buffer.append",
                        "audio": base64_audio
                    }
                    await ws.send(json.dumps(audio_event))
                    logger.info(f"Sent audio chunk #{chunk_count}: {len(chunk)} bytes (PCM16 format)")
                    
                    # 依賴 OpenAI 的 server_vad 自動檢測語音結束並回應
                    # 不再手動觸發回應
                        
        except Exception as e:
            logger.error(f"Error sending audio to OpenAI: {e}")

    async def _receive_openai_responses(self, ws, audio_queue: asyncio.Queue):
        """接收來自 OpenAI 的回應"""
        try:
            async for message in ws:
                try:
                    event = json.loads(message)
                    logger.debug(f"Received event: {event.get('type')}")
                    
                    # 處理音頻回應
                    if event.get("type") == "response.audio.delta":
                        if "delta" in event:
                            # 解碼 base64 音頻數據
                            pcm_data = base64.b64decode(event["delta"])
                            logger.info(f"Received PCM audio delta: {len(pcm_data)} bytes")
                            
                            # 將 PCM16 數據轉換為 WAV 格式
                            wav_data = self._pcm_to_wav(pcm_data)
                            logger.info(f"Converted to WAV: {len(wav_data)} bytes")
                            await audio_queue.put(wav_data)
                    
                    # 處理文本回應（用於調試）
                    elif event.get("type") == "response.text.delta":
                        logger.info(f"OpenAI text response: {event.get('delta', '')}")
                    
                    # 處理錯誤
                    elif event.get("type") == "error":
                        logger.error(f"OpenAI API error: {event}")
                        
                    # 處理會話創建
                    elif event.get("type") == "session.created":
                        logger.info("OpenAI session created successfully")
                        
                    # 處理會話更新
                    elif event.get("type") == "session.updated":
                        logger.info("OpenAI session updated successfully")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON message: {e}")
                except Exception as e:
                    logger.error(f"Error processing OpenAI response: {e}")
                    
        except ConnectionClosed:
            logger.info("OpenAI WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving from OpenAI: {e}")
        finally:
            # 發送結束信號
            await audio_queue.put(None)

    def _pcm_to_wav(self, pcm_data: bytes) -> bytes:
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

    async def _test_conversation(
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
