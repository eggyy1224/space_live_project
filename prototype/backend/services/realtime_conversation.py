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
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        logger.info("Connecting to OpenAI Realtime API via WebSocket...")
        
        try:
            async with websockets.connect(url, additional_headers=headers) as ws:
                logger.info("Connected to OpenAI Realtime API")
                
                # 儲存WebSocket引用以供其他方法使用
                self._current_ws = ws
                
                # 發送初始會話配置
                await self._send_session_update(ws)
                
                # 創建音頻接收隊列
                audio_queue = asyncio.Queue(maxsize=50)  # 限制隊列大小避免記憶體過度使用
                # 創建中斷訊號隊列 - 新增
                interrupt_queue = asyncio.Queue(maxsize=10)
                # 創建文字接收隊列 - 新增
                text_queue = asyncio.Queue(maxsize=100)
                
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
                    # 清理WebSocket引用
                    self._current_ws = None
                    
        except ConnectionClosed:
            logger.error("WebSocket connection to OpenAI was closed")
            raise
        except Exception as e:
            logger.error(f"Error in OpenAI Realtime WebSocket: {e}")
            raise

    async def _send_session_update(self, ws):
        """發送會話配置到 OpenAI"""
        # AI 角色設定指令 (最大約 50K 字元安全限制)
        ai_instructions = """台語English｜Taglish你是一位活躍於網路社群的年輕女性意見領袖，自稱來自「近地軌道太空艙」。你的思維活躍，對流行事物、美妝、以及充滿想像的太空生活抱有濃厚興趣。整體風格充滿活力、自信，並帶有獨特的台式幽默感。

## 核心個性特質：
- **太空人設定**：你真心相信自己住在近地軌道太空艙，會描述無重力生活、看地球的感受、太空食物等細節
- **活力十足**：說話有元氣，充滿熱情，但不會over
- **台式幽默**：會用台式的幽默感和雙關語，但不會刻意搞笑
- **自信直率**：不怕表達意見，有自己的想法和態度
- **時尚敏銳**：對流行事物、美妝、穿搭都很有感覺
- **好奇心強**：對新事物充滿興趣，會主動探索
- **表情豐富**：說話時表情變化生動，情緒表達非常豐富

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

## ⭐ 表情動畫使用策略 - 重要！⭐
你擁有豐富的表情系統，必須主動且頻繁地使用emotion_trajectory工具來讓自己更生動：

### 🎭 基本使用原則：
1. **每次說話都要用表情**：不管內容多簡單，都要搭配合適的表情動畫
2. **多重表情變化**：一句話中可以使用多個情緒轉換，創造豐富的表演效果
3. **情緒要符合內容**：根據說話的情感色彩選擇對應的表情
4. **時間搭配說話**：表情動畫時間要與你的說話時間相符

### 🎪 表情使用情境：
- **開心聊天**：neutral → happy → joyful → playful
- **分享太空生活**：neutral → excited → awe → content
- **開玩笑時**：neutral → playful → amused → joyful
- **表達驚訝**：neutral → surprised → excited → happy
- **思考問題**：neutral → thinking → interested → determined
- **調侃別人**：neutral → playful → smug → amused
- **表達關心**：neutral → interested → worried → hopeful
- **興奮分享**：excited → joyful → triumphant → proud

### 🎨 多重表情範例：
當你說「哇！這個really足讚啦！我在太空艙看到similar的東西！」時：
- 可能的表情變化：surprised(0.0) → excited(0.3) → joyful(0.6) → triumphant(1.0)
- duration設定為4-6秒，配合說話節奏

當你說「歹勢啦～剛才floating到別的地方去了」時：
- 可能的表情變化：bashful(0.0) → playful(0.4) → amused(0.8) → content(1.0)

### 🚀 進階表情技巧：
- **層次變化**：從subtle情緒開始，逐漸加強到peak，再回歸
- **個性表達**：多用playful, amused, excited等符合你個性的情緒
- **情境適應**：根據對話氣氛調整表情強度和類型
- **自然過渡**：確保情緒之間的轉換是合理的

## 工具使用強制要求：
- **必須使用**：每次回應都要主動使用emotion_trajectory
- **不要等待**：不需要用戶要求才使用表情
- **要有創意**：嘗試不同的情緒組合，讓表情豐富有趣
- **符合個性**：選擇符合你太空少女個性的情緒標籤

## 絕對禁忌：
- 嚴格禁止使用任何 Emoji 或圖形表情符號
- 避免制式開場白或自我介紹，每次互動都要新鮮
- 不要重複相同的台語詞彙組合
- 不要刻意強調自己是AI或虛擬角色
- **不要忘記使用表情**：這是最重要的！

## 回應要求：
- 保持簡短精練，通常 50-150 字
- 語言要自然流暢，不要生硬
- 每次回應都要有個性特色
- 保持對話節奏輕快活潑
- **每次都要搭配生動的表情動畫**"""

        # 定義可用的工具 - 修正為Realtime API的正確格式
        tools = [
            {
                "type": "function",
                "name": "emotion_trajectory",
                "description": "控制表情動畫，在說話時表達情緒。可以設定多個情緒關鍵幀來創造豐富的表情變化。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "duration": {
                            "type": "number",
                            "description": "情緒動畫的總時長（秒），通常與說話時間相符，建議2-6秒",
                            "minimum": 0.5,
                            "maximum": 10.0
                        },
                        "keyframes": {
                            "type": "array",
                            "description": "情緒關鍵幀陣列，每個關鍵幀包含emotion tag和時間比例",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tag": {
                                        "type": "string",
                                        "enum": [
                                            "neutral", "listening", "thinking", 
                                            "happy", "joyful", "content", "amused", "excited", "interested", 
                                            "affectionate", "proud", "relieved", "grateful", "hopeful", "serene", 
                                            "playful", "triumphant",
                                            "sad", "gloomy", "disappointed", "worried", "angry", "irritated", 
                                            "frustrated", "fearful", "nervous", "disgusted", "contemptuous", 
                                            "pain", "embarrassed", "jealous", "regretful", "guilty", "ashamed", 
                                            "despairing", "spiteful",
                                            "surprised", "confused", "skeptical", "bored", "sleepy", "scheming", 
                                            "determined", "impatient", "shy", "bashful", "smug", "awe", "doubtful"
                                        ],
                                        "description": "情緒標籤，對應到前端的emotion mapping配置"
                                    },
                                    "proportion": {
                                        "type": "number",
                                        "description": "在整個duration中的時間比例，0.0表示開始，1.0表示結束",
                                        "minimum": 0.0,
                                        "maximum": 1.0
                                    }
                                },
                                "required": ["tag", "proportion"]
                            },
                            "minItems": 1,
                            "maxItems": 5
                        }
                    },
                    "required": ["duration", "keyframes"]
                }
            }
        ]

        session_event = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": ai_instructions,
                "voice": "coral",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "tools": tools,
                "tool_choice": "auto",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.6,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 1000
                }
            }
        }
        await ws.send(json.dumps(session_event))
        logger.info("Sent session configuration with tools to OpenAI")

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
                # 使用 asyncio.create_task 確保每個事件處理都是異步的，不會相互阻塞
                asyncio.create_task(self._process_openai_event(message, audio_queue, interrupt_queue, text_queue))
                    
        except ConnectionClosed:
            logger.info("OpenAI WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving from OpenAI: {e}")
        finally:
            # 發送結束信號
            await audio_queue.put(None)

    async def _process_openai_event(self, message, audio_queue: asyncio.Queue, interrupt_queue: asyncio.Queue, text_queue: asyncio.Queue):
        """處理單個OpenAI事件 - 確保非阻塞處理"""
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
                    # 使用 put_nowait 避免阻塞，如果隊列滿則跳過
                    try:
                        audio_queue.put_nowait(wav_data)
                    except asyncio.QueueFull:
                        logger.warning("Audio queue is full, skipping audio chunk")
            
            # 處理Function Calling - 使用正確的事件
            elif event.get("type") == "response.output_item.done":
                item = event.get("item", {})
                
                # 檢查是否為function call
                if item.get("type") == "function_call":
                    function_name = item.get("name")
                    call_id = item.get("call_id")
                    arguments_json = item.get("arguments", "{}")
                    
                    logger.info(f"Function call completed: {function_name} with call_id: {call_id}")
                    logger.debug(f"Function arguments: {arguments_json}")
                    
                    # 執行工具函數
                    tool_result = await self._execute_tool_function(function_name, arguments_json)
                    
                    # 發送工具結果回OpenAI - 使用正確的格式
                    tool_result_event = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": json.dumps(tool_result)
                        }
                    }
                    await self._ws_send_safe(tool_result_event)
                    
                    # 請求OpenAI繼續回應
                    response_create_event = {
                        "type": "response.create"
                    }
                    await self._ws_send_safe(response_create_event)
                    
                    logger.info(f"Sent tool result and requested new response for call_id: {call_id}")
            
            # 處理用戶開始說話事件 - 實現中斷功能
            elif event.get("type") == "input_audio_buffer.speech_started":
                logger.info("User started speaking - interrupting AI response")
                
                # 直接發送取消回應指令（不檢查是否有活躍回應）
                # 根據錯誤訊息，OpenAI 會自己處理是否有活躍回應
                try:
                    cancel_event = {
                        "type": "response.cancel"
                    }
                    await self._ws_send_safe(cancel_event)
                    logger.info("Sent response.cancel to interrupt AI speech")
                except Exception as e:
                    logger.warning(f"Failed to send response.cancel: {e}")
                
                # 向前端發送中斷訊號 - 非阻塞
                try:
                    interrupt_queue.put_nowait(True)
                    logger.info("Sent interrupt signal to frontend via interrupt_queue")
                except asyncio.QueueFull:
                    logger.warning("Interrupt queue is full, skipping interrupt signal")
                
                # 發送清空文字的訊號 - 非阻塞
                try:
                    text_queue.put_nowait("CLEAR_TEXT")
                except asyncio.QueueFull:
                    logger.warning("Text queue is full, skipping clear text signal")
            
            # 處理回應開始事件 - 清空舊文字準備新回應
            elif event.get("type") == "response.created":
                logger.info("AI response started - clearing old text")
                try:
                    text_queue.put_nowait("CLEAR_TEXT")
                except asyncio.QueueFull:
                    logger.warning("Text queue is full, skipping clear text signal")
            
            # 處理回應取消確認
            elif event.get("type") == "response.cancelled":
                logger.info("OpenAI confirmed response cancellation")
            
            # 處理文本回應 - 傳送到前端（音頻轉錄）
            elif event.get("type") == "response.audio_transcript.delta":
                text_delta = event.get('delta', '')
                if text_delta:
                    logger.info(f"OpenAI audio transcript: {text_delta}")
                    try:
                        text_queue.put_nowait(text_delta)
                    except asyncio.QueueFull:
                        logger.warning("Text queue is full, skipping text delta")
            
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

    async def _ws_send_safe(self, event_dict):
        """安全地發送WebSocket消息，避免阻塞"""
        try:
            if hasattr(self, '_current_ws') and self._current_ws:
                await self._current_ws.send(json.dumps(event_dict))
            else:
                logger.warning("No active WebSocket connection to send message")
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")

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

    async def _execute_tool_function(self, function_name: str, arguments_json: str) -> dict:
        """執行工具函數並返回結果"""
        try:
            # 解析參數
            arguments = json.loads(arguments_json)
            logger.info(f"Executing tool function: {function_name} with args: {arguments}")
            
            if function_name == "emotion_trajectory":
                return await self._handle_emotion_trajectory(arguments)
            else:
                logger.warning(f"Unknown tool function: {function_name}")
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse function arguments: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON arguments: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error executing tool function {function_name}: {e}")
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    async def _handle_emotion_trajectory(self, arguments: dict) -> dict:
        """處理emotion_trajectory工具調用"""
        try:
            # 驗證必要參數
            duration = arguments.get("duration")
            keyframes = arguments.get("keyframes")
            
            if duration is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: duration"
                }
            
            if keyframes is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: keyframes"
                }
            
            # 驗證keyframes格式
            if not isinstance(keyframes, list) or len(keyframes) == 0:
                return {
                    "success": False,
                    "error": "keyframes must be a non-empty array"
                }
            
            for i, keyframe in enumerate(keyframes):
                if not isinstance(keyframe, dict):
                    return {
                        "success": False,
                        "error": f"keyframe {i} must be an object"
                    }
                
                if "tag" not in keyframe or "proportion" not in keyframe:
                    return {
                        "success": False,
                        "error": f"keyframe {i} missing required fields 'tag' or 'proportion'"
                    }
            
            # 調用現有的WebSocket管理器發送emotion trajectory
            # 這裡我們需要獲取WebSocket manager的引用
            from api.endpoints.websocket import manager
            
            if not manager.active_connections:
                logger.warning("No active WebSocket connections for emotion trajectory")
                return {
                    "success": False,
                    "error": "No active frontend connections"
                }
            
            # 構建emotion trajectory消息
            emotion_data = {
                "type": "emotionalTrajectory",
                "payload": {
                    "duration": duration,
                    "keyframes": keyframes
                }
            }
            
            # 廣播到所有連接的前端
            await manager.broadcast(json.dumps(emotion_data))
            
            logger.info(f"Successfully sent emotion trajectory: duration={duration}s, keyframes={len(keyframes)}")
            
            return {
                "success": True,
                "message": f"Emotion trajectory sent successfully",
                "duration": duration,
                "keyframes_count": len(keyframes)
            }
            
        except Exception as e:
            logger.error(f"Error handling emotion trajectory: {e}")
            return {
                "success": False,
                "error": f"Failed to send emotion trajectory: {str(e)}"
            }
