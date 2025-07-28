"""
WebSocket 處理模組
負責 OpenAI Realtime API 的連接管理和事件處理。
"""

import asyncio
import json
import base64
import logging
import websockets
from typing import AsyncIterator, AsyncGenerator
from websockets.exceptions import ConnectionClosed
from pathlib import Path

from .utils import pcm_to_wav
from .session_config import create_session_config
from .logging import WebSocketLogger

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """處理 OpenAI Realtime API 的 WebSocket 連接"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._current_ws = None
        self._session_logger = None
    
    async def _set_initial_room_scene(self):
        """設定初始房間場景為賽博太空艙"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                scene_data = {
                    "displayScene": True,
                    "sceneName": "賽博太空艙"
                }
                async with session.post(
                    "http://localhost:8000/api/control/scene-display",
                    json=scene_data
                ) as response:
                    if response.status == 200:
                        logger.info("初始房間場景設置為：賽博太空艙")
                    else:
                        logger.warning(f"設置初始房間場景失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"設置初始房間場景異常: {e}")

    async def stream_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks to OpenAI and yield TTS audio bytes."""
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        # 初始化會話日誌記錄器
        logs_dir = Path(__file__).parent / "logging" / "logs"
        self._session_logger = WebSocketLogger(str(logs_dir))
        
        logger.info("Connecting to OpenAI Realtime API via WebSocket...")
        self._session_logger.log_connection_start(url, headers)
        
        try:
            async with websockets.connect(url, additional_headers=headers) as ws:
                logger.info("Connected to OpenAI Realtime API")
                self._session_logger.log_connection_success()
                
                # 儲存WebSocket引用以供其他方法使用
                self._current_ws = ws
                
                # 等待連接穩定
                await asyncio.sleep(0.1)
                
                # 發送初始會話配置
                await self._send_session_update(ws)
                
                # 等待會話配置確認
                await asyncio.sleep(0.5)
                await self._set_initial_room_scene()  # 新增：切換到賽博太空艙
                await self._set_initial_camera()
                
                # 設定初始動畫，避免T-pose
                await self._set_initial_animation()
                
                # 設定舞群初始動畫
                await self._set_initial_dance_group_animation()
                
                # 自動發送歡迎訊息
                await self._send_welcome_message()
                
                # 創建音頻接收隊列
                audio_queue = asyncio.Queue(maxsize=50)  # 限制隊列大小避免記憶體過度使用
                # 創建中斷訊號隊列
                interrupt_queue = asyncio.Queue(maxsize=10)
                # 創建文字接收隊列
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
                    if self._session_logger:
                        self._session_logger.log_connection_closed("Cancelled by user")
                finally:
                    # 取消所有任務
                    receive_task.cancel()
                    send_task.cancel()
                    # 清理WebSocket引用
                    self._current_ws = None
                    # 關閉日誌記錄器
                    if self._session_logger:
                        self._session_logger.log_connection_closed("Normal closure")
                        self._session_logger = None
                    
        except ConnectionClosed:
            logger.error("WebSocket connection to OpenAI was closed")
            if self._session_logger:
                self._session_logger.log_connection_closed("WebSocket connection closed")
            raise
        except Exception as e:
            logger.error(f"Error in OpenAI Realtime WebSocket: {e}")
            if self._session_logger:
                self._session_logger.log_error("WEBSOCKET_ERROR", str(e))
            raise

    async def _send_session_update(self, ws):
        """發送會話配置到 OpenAI"""
        session_event = create_session_config()
        await ws.send(json.dumps(session_event))
        logger.info("Sent session configuration with tools to OpenAI")
        
        # 記錄會話配置
        if self._session_logger:
            self._session_logger.log_session_config_sent(session_event)

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
                    
                    # 記錄音頻塊發送
                    if self._session_logger:
                        self._session_logger.log_audio_chunk_sent(chunk_count, len(chunk))
                    
                    # 依賴 OpenAI 的 server_vad 自動檢測語音結束並回應
                    # 不再手動觸發回應
                        
        except Exception as e:
            logger.error(f"Error sending audio to OpenAI: {e}")
            if self._session_logger:
                self._session_logger.log_error("AUDIO_SEND_ERROR", str(e))

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
            if self._session_logger:
                self._session_logger.log_error("AUDIO_RECEIVE_ERROR", str(e))
        finally:
            # 發送結束信號
            await audio_queue.put(None)

    async def _process_openai_event(self, message, audio_queue: asyncio.Queue, interrupt_queue: asyncio.Queue, text_queue: asyncio.Queue):
        """處理單個OpenAI事件 - 確保非阻塞處理"""
        try:
            event = json.loads(message)
            logger.debug(f"Received event: {event.get('type')}")
            
            # 記錄接收到的事件
            if self._session_logger:
                self._session_logger.log_event_received(event.get('type', 'unknown'), event)
            
            # 處理音頻回應
            if event.get("type") == "response.audio.delta":
                if "delta" in event:
                    # 解碼 base64 音頻數據
                    pcm_data = base64.b64decode(event["delta"])
                    logger.info(f"Received PCM audio delta: {len(pcm_data)} bytes")
                    
                    # 將 PCM16 數據轉換為 WAV 格式
                    wav_data = pcm_to_wav(pcm_data)
                    logger.info(f"Converted to WAV: {len(wav_data)} bytes")
                    
                    # 記錄音頻處理
                    if self._session_logger:
                        self._session_logger.log_audio_processed(len(pcm_data), len(wav_data))
                    
                    # 使用 put_nowait 避免阻塞，如果隊列滿則跳過
                    try:
                        audio_queue.put_nowait(wav_data)
                    except asyncio.QueueFull:
                        logger.warning("Audio queue is full, skipping audio chunk")
            
            # 處理Function Calling - 使用正確的事件
            elif event.get("type") == "response.output_item.done":
                item = event.get("item", {})
                
                # 詳細記錄item內容以便調試
                logger.info(f"🔍 Output item done - type: {item.get('type')}, item details: {item}")
                
                # 檢查是否為function call
                if item.get("type") == "function_call":
                    function_name = item.get("name")
                    call_id = item.get("call_id")
                    arguments_json = item.get("arguments", "{}")
                    
                    logger.info(f"🎯 Function call detected: {function_name} with call_id: {call_id}")
                    logger.info(f"📝 Function arguments: {arguments_json}")
                    
                    # 這裡需要由外部提供的tool_executor來執行工具函數
                    if hasattr(self, 'tool_executor') and self.tool_executor:
                        tool_result = await self.tool_executor(function_name, arguments_json)
                    else:
                        tool_result = {
                            "success": False,
                            "error": "No tool executor configured"
                        }
                    
                    # 記錄 Function Call 執行結果
                    if self._session_logger:
                        self._session_logger.log_function_call_executed(function_name, call_id, tool_result)
                    
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
                    
                    logger.info(f"✅ Sent tool result and requested new response for call_id: {call_id}")
                else:
                    # 記錄非function call的項目
                    logger.debug(f"📄 Non-function output item: {item.get('type')}")
            
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
            
            # 處理用戶輸入轉錄 - 新增！
            elif event.get("type") == "conversation.item.input_audio_transcription.delta":
                user_transcript_delta = event.get('delta', '')
                if user_transcript_delta:
                    logger.info(f"👤 User transcript delta: {user_transcript_delta}")
                    # 記錄用戶輸入轉錄增量
                    if self._session_logger:
                        self._session_logger.log_user_transcript_delta(user_transcript_delta)
            
            # 處理用戶輸入轉錄完成 - 新增！
            elif event.get("type") == "conversation.item.input_audio_transcription.completed":
                user_transcript = event.get('transcript', '')
                if user_transcript:
                    logger.info(f"👤 User transcript completed: {user_transcript}")
                    # 記錄完整的用戶輸入轉錄
                    if self._session_logger:
                        self._session_logger.log_user_transcript_completed(user_transcript)
            
            # 處理會話物品創建 - 檢查用戶輸入
            elif event.get("type") == "conversation.item.created":
                item = event.get("item", {})
                if item.get("role") == "user":
                    logger.info(f"👤 User conversation item created: {item.get('id')}")
                    # 檢查是否有直接的轉錄內容
                    content = item.get("content", [])
                    for content_item in content:
                        if content_item.get("type") == "input_audio" and content_item.get("transcript"):
                            transcript = content_item.get("transcript")
                            logger.info(f"👤 User input transcript from item: {transcript}")
                            if self._session_logger:
                                self._session_logger.log_user_transcript_completed(transcript)
            
            # 處理錯誤 - 改善錯誤處理
            elif event.get("type") == "error":
                error_info = event.get("error", {})
                error_code = error_info.get("code")
                error_message = error_info.get("message", "")
                
                if error_code == "response_cancel_not_active":
                    logger.debug("No active response to cancel - this is normal")
                elif error_code == "invalid_value":
                    logger.error(f"Invalid event type sent: {error_message}")
                    # 記錄詳細錯誤到會話日誌
                    if self._session_logger:
                        self._session_logger.log_error("INVALID_VALUE_ERROR", error_message, {
                            "error_code": error_code,
                            "full_event": event
                        })
                else:
                    logger.error(f"OpenAI API error: {event}")
                    # 記錄詳細錯誤到會話日誌
                    if self._session_logger:
                        self._session_logger.log_error("OPENAI_API_ERROR", error_message, {
                            "error_code": error_code,
                            "error_info": error_info,
                            "full_event": event
                        })
                
            # 處理會話創建
            elif event.get("type") == "session.created":
                logger.info("OpenAI session created successfully")
                
            # 處理會話更新
            elif event.get("type") == "session.updated":
                logger.info("OpenAI session updated successfully")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
            if self._session_logger:
                self._session_logger.log_error("JSON_PARSE_ERROR", str(e), {"message": message})
        except Exception as e:
            logger.error(f"Error processing OpenAI response: {e}")
            if self._session_logger:
                self._session_logger.log_error("EVENT_PROCESSING_ERROR", str(e))

    async def _ws_send_safe(self, event_dict):
        """安全地發送WebSocket消息，避免阻塞"""
        try:
            if hasattr(self, '_current_ws') and self._current_ws:
                await self._current_ws.send(json.dumps(event_dict))
            else:
                logger.warning("No active WebSocket connection to send message")
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
    
    async def _set_initial_camera(self):
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                preset_data = {"name": "frontal_dynamic_low", "duration": 2.0}
                async with session.post(
                    "http://localhost:8000/api/control/camera/set-frontend-preset",
                    json=preset_data
                ) as response:
                    if response.status == 200:
                        logger.info("初始相機預設設置為 frontal_dynamic_low")
                    else:
                        logger.warning(f"設置初始相機預設失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"設置初始相機預設異常: {e}")
    
    async def _set_initial_animation(self):
        """設定初始動畫，避免T-pose"""
        import aiohttp
        import random
        try:
            # 可用的初始動畫清單（排除Tpose）
            available_animations = [
                "運動2", "漂浮", "運動1", "不穩", "划手機", 
                "漂浮2", "臥躺", "舞步1", "舞步2", "舞步3", 
                "飛1", "飛2"
            ]
            
            # 隨機選擇一個動畫
            selected_animation = random.choice(available_animations)
            
            async with aiohttp.ClientSession() as session:
                animation_data = {
                    "animation": selected_animation, 
                    "loop": True, 
                    "speed": 1.0
                }
                async with session.post(
                    "http://localhost:8000/api/control/character/animation",
                    json=animation_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"初始動畫隨機設置為: {selected_animation}，避免T-pose")
                    else:
                        logger.warning(f"設置初始動畫失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"設置初始動畫異常: {e}")
    
    async def _set_initial_dance_group_animation(self):
        """設定舞群初始動畫，讓背景舞群一開始就跳舞"""
        import aiohttp
        import random
        try:
            # 可用的舞群動畫清單（選擇適合的舞蹈動畫）
            dance_group_animations = [
                "DancingTwerk", "SalsaDancing", "JazzDancing", "HipHopDancin", 
                "breaking", "hiphopdance", "twistdance", "CanCan", 
                "ButterflyTwirl", "Breakdance1990", "BreakdanceFootwork2"
            ]
            
            # 隨機選擇一個舞群動畫
            selected_dance = random.choice(dance_group_animations)
            
            async with aiohttp.ClientSession() as session:
                # 使用body-animation API控制舞群
                dance_data = {
                    "state": "play",
                    "animation": selected_dance,
                    "loop": True,
                    "speed": 1.0
                }
                async with session.post(
                    "http://localhost:8000/api/control/body-animation",
                    json=dance_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"舞群初始動畫隨機設置為: {selected_dance}，開始熱場跳舞！")
                    else:
                        logger.warning(f"設置舞群初始動畫失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"設置舞群初始動畫異常: {e}")
    
    async def _send_welcome_message(self):
        """自動發送隨機歡迎訊息"""
        import aiohttp
        import random
        try:
            welcome_messages = [
                "哈摟我是你最辣的太空主播，今天好嗎",
                "歡迎來到太空艙直播間，今天想看什麼表演？",
                "Yo～這裡是賽博太空艙，準備好一起high了嗎？",
                "哈囉！我是來自近地軌道的太空主播，今天要帶你體驗宇宙級的互動！",
                "太空連線成功！主播在這裡等你很久囉！",
                "地球的朋友午安，這裡是最潮的太空直播間！",
                "準備好進入無重力的歡樂時光了嗎？",
                "哈囉哈囉～主播已經在太空艙stand by囉！",
                "今天要不要來點太空瑜伽還是跳個舞？",
                "歡迎光臨！這裡是最有梗的太空直播主，陪你high翻宇宙！"
            ]
            message = random.choice(welcome_messages)
            async with aiohttp.ClientSession() as session:
                message_data = {
                    "content": message,
                    "message_type": "chat-message"
                }
                async with session.post(
                    "http://localhost:8000/api/control/send-message",
                    json=message_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"自動發送歡迎訊息成功: {message}")
                    else:
                        logger.warning(f"發送歡迎訊息失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"發送歡迎訊息失敗: {e}")
    
    def set_tool_executor(self, executor):
        """設定工具執行器"""
        self.tool_executor = executor 