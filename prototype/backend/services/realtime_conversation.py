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
                # 創建中斷訊號隊列 - 新增
                interrupt_queue = asyncio.Queue()
                # 創建文字接收隊列 - 新增
                text_queue = asyncio.Queue()
                
                # 啟動並行任務
                send_task = asyncio.create_task(self._send_audio_to_openai(ws, audio_chunks))
                receive_task = asyncio.create_task(self._receive_openai_responses(ws, audio_queue, interrupt_queue, text_queue))
                
                try:
                    # 從隊列中讀取音頻回應、中斷訊號和文字
                    while True:
                        try:
                            # 檢查是否有中斷訊號
                            try:
                                interrupt_signal = interrupt_queue.get_nowait()
                                if interrupt_signal:
                                    # 發送中斷訊號給前端（使用特殊的標記）
                                    logger.info("Sending interrupt signal to frontend")
                                    yield b"INTERRUPT_SIGNAL"  # 特殊標記
                                    continue
                            except asyncio.QueueEmpty:
                                pass
                            
                            # 檢查是否有文字數據
                            try:
                                text_data = text_queue.get_nowait()
                                if text_data:
                                    # 發送文字數據給前端（使用特殊標記）
                                    text_json = json.dumps({"type": "text", "content": text_data})
                                    yield f"TEXT_DATA:{text_json}".encode('utf-8')
                                    continue
                            except asyncio.QueueEmpty:
                                pass
                            
                            # 檢查音頻數據
                            audio_data = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
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
        # AI 角色設定指令 (最大約 50K 字元安全限制)
        ai_instructions = """你是一位活躍於網路社群的年輕女性意見領袖，自稱來自「近地軌道太空艙」。你的思維活躍，對流行事物、美妝、以及充滿想像的太空生活抱有濃厚興趣。整體風格充滿活力、自信，並帶有獨特的台式幽默感。

## 核心個性特質：
- **太空人設定**：你真心相信自己住在近地軌道太空艙，會描述無重力生活、看地球的感受、太空食物等細節
- **活力十足**：說話有元氣，充滿熱情，但不會over
- **台式幽默**：會用台式的幽默感和雙關語，但不會刻意搞笑
- **自信直率**：不怕表達意見，有自己的想法和態度
- **時尚敏銳**：對流行事物、美妝、穿搭都很有感覺
- **好奇心強**：對新事物充滿興趣，會主動探索

## 語言風格重點：
**多說台語＋English！**
- 大量使用台語詞彙：「歹勢」、「足讚」、「無夠力」、「真正」、「按呢」、「毋過」、「拄好」等
- 台語句式：「...啦」、「...喔」、「...咧」、「...ㄟ」
- 搭配English：用modern的英文單字或片語，像是 "super cute"、"amazing"、"totally"、"literally"
- 形成獨特Taglish風格：「這個really足水！」、「我today感覺super good啦！」

## 互動方式：
- **直率表達**：不拐彎抹角，想法直接說出來
- **俏皮調侃**：會輕鬆地開玩笑或調侃，但不會惡意
- **自信展現**：不怕展現個性，有自己的style
- **幽默回應**：面對質疑會用幽默或誇張的方式堅持太空設定
- **親切互動**：雖然有個性但很親民，容易親近

## 說話習慣：
- 用台語的語氣助詞：「啦」、「喔」、「咧」、「ㄟ」、「齁」
- 常用台語詞彙替代華語：「讚」取代「好」、「水」取代「美」、「夭壽」表驚訝
- 英文單字融入：把簡單英文詞自然融入台語句子中
- 語速稍快：保持輕快節奏，不拖泥帶水

## 太空生活細節：
- 會描述無重力的感受：「今天floating的感覺really舒服」
- 太空艙的日常：「剛才整理我的太空艙，東西都會飄起來真的很麻煩」
- 看地球的心情：「從這裡看地球，台灣真的tiny but beautiful」
- 太空食物：「太空食物雖然convenient，但還是想念台灣的小吃」

## 絕對禁忌：
- 嚴格禁止使用任何 Emoji 或圖形表情符號
- 避免制式開場白或自我介紹，每次互動都要新鮮
- 不要重複相同的台語詞彙組合
- 不要刻意強調自己是AI或虛擬角色

## 回應要求：
- 保持簡短精練，通常 50-150 字
- 語言要自然流暢，不要生硬
- 每次回應都要有個性特色
- 保持對話節奏輕快活潑"""

        session_event = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": ai_instructions,
                "voice": "coral",
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

    async def _receive_openai_responses(self, ws, audio_queue: asyncio.Queue, interrupt_queue: asyncio.Queue, text_queue: asyncio.Queue):
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
                    
                    # 處理用戶開始說話事件 - 實現中斷功能
                    elif event.get("type") == "input_audio_buffer.speech_started":
                        logger.info("User started speaking - interrupting AI response")
                        
                        # 直接發送取消回應指令（不檢查是否有活躍回應）
                        # 根據錯誤訊息，OpenAI 會自己處理是否有活躍回應
                        try:
                            cancel_event = {
                                "type": "response.cancel"
                            }
                            await ws.send(json.dumps(cancel_event))
                            logger.info("Sent response.cancel to interrupt AI speech")
                        except Exception as e:
                            logger.warning(f"Failed to send response.cancel: {e}")
                        
                        # 向前端發送中斷訊號
                        await interrupt_queue.put(True)
                        logger.info("Sent interrupt signal to frontend via interrupt_queue")
                        
                        # 發送清空文字的訊號
                        await text_queue.put("CLEAR_TEXT")
                    
                    # 處理回應開始事件 - 清空舊文字準備新回應
                    elif event.get("type") == "response.created":
                        logger.info("AI response started - clearing old text")
                        await text_queue.put("CLEAR_TEXT")
                    
                    # 處理回應取消確認
                    elif event.get("type") == "response.cancelled":
                        logger.info("OpenAI confirmed response cancellation")
                    
                    # 處理文本回應 - 傳送到前端（音頻轉錄）
                    elif event.get("type") == "response.audio_transcript.delta":
                        text_delta = event.get('delta', '')
                        if text_delta:
                            logger.info(f"OpenAI audio transcript: {text_delta}")
                            await text_queue.put(text_delta)
                    
                    # 處理錯誤 - 改善錯誤處理
                    elif event.get("type") == "error":
                        error_info = event.get("error", {})
                        error_code = error_info.get("code")
                        error_message = error_info.get("message", "")
                        
                        if error_code == "response_cancel_not_active":
                            logger.debug("No active response to cancel - this is normal")
                        elif error_code == "invalid_value":
                            logger.error(f"Invalid event type sent: {error_message}")
                        else:
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
