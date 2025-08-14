"""
WebSocket 處理模組
負責 OpenAI Realtime API 的連接管理和事件處理。
"""

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, AsyncIterator

import websockets
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from services.memory_system import MemorySystem
from services.perception import YouTubeChatMonitorService
from services.video_rotation_service import video_rotation_service
from websockets.exceptions import ConnectionClosed

from .logging import WebSocketLogger
from .session_config import create_session_config
from .utils import pcm_to_wav

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """處理 OpenAI Realtime API 的 WebSocket 連接"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._current_ws = None
        self._session_logger = None
        # 新增：YouTube 聊天室監控服務
        self._youtube_chat_service = YouTubeChatMonitorService()
        # 太空人頻道 ID（可以設定為環境變數）
        self._channel_id = "UCV60MYR7dQJM8TqY5eXb7YA"
        # YouTube 聊天監控任務
        self._youtube_monitor_task = None
        self._last_processed_message_count = 0
        # 記憶系統（懶加載）
        self._memory_system = None
        # 追蹤燈光呼吸效果任務，方便在結束時取消
        self._light_breath_task = None
        # 影片輪播交給服務管理

    async def _generate_background_from_conversation(self):
        """在會話啟動時，根據最近的對話記憶產生並設置背景圖片。
        策略：
        1) 讀取最近 3 筆 conversation 記憶
        2) 彙整為簡潔的場景描述，交由生成 API 逆向推測合適背景
        3) 呼叫 /api/generate-background-image 生成並自動套用
        """
        import re

        import aiohttp

        try:
            recent_contents = []
            # 取得最近的對話記憶（3 筆）
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/memory/get",
                    json={
                        "memory_type": "conversation",
                        "limit": 3,
                        "include_metadata": False,
                    },
                    timeout=aiohttp.ClientTimeout(total=6),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        memories = data.get("data", {}).get("memories", [])
                        for item in memories:
                            if isinstance(item, dict):
                                text = item.get("content")
                                if text:
                                    recent_contents.append(str(text))
                            else:
                                recent_contents.append(str(item))

            # 構造描述（依最近對話內容逆向生成場景）
            if recent_contents:
                joined = " | ".join(recent_contents)
                description = (
                    f"Cinematic background that fits these recent conversation beats: {joined}. "
                    f"Avoid text or logos; suggest environment, mood, lighting, and composition."
                )
            else:
                description = "Cinematic neutral space interior with gentle lights — fallback background"

            payload = {"description": description, "aspect_ratio": "16:9"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/generate-background-image",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        logger.info(
                            f"✅ 背景已根據最近對話記憶生成並套用，描述: {description} | 回應: {text[:200]}..."
                        )
                    else:
                        logger.warning(f"❌ 背景生成失敗: HTTP {resp.status} - {text}")
        except Exception as e:
            logger.error(f"會話啟動背景生成異常: {e}")

    async def _breathing_light_effect(self, brighten=True, steps=14, delay=0.08):
        """
        呼吸燈效果：
        brighten=True 時，從暗到亮；False 時，從亮到暗。
        steps: 亮度分段數
        delay: 每步延遲秒數
        """
        import math

        import aiohttp

        base_url = "http://localhost:8000/api/physical-light/set-brightness"
        # 用正弦波分布產生平滑亮度
        for i in range(steps + 1):
            t = i / steps
            if brighten:
                brightness = int((math.sin(t * math.pi / 2)) ** 2 * 65535)
            else:
                brightness = int((math.cos(t * math.pi / 2)) ** 2 * 65535)
            async with aiohttp.ClientSession() as session:
                await session.post(base_url, json={"brightness": brightness})
            await asyncio.sleep(delay)

    async def _set_initial_environment_light(self):
        """
        設定初始環境光強度為 1.0，並執行燈光漸亮呼吸效果
        """
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"intensity": 1.0}
                async with session.post(
                    "http://localhost:8000/api/control/environment/config", json=payload
                ) as response:
                    if response.status == 200:
                        logger.info("初始環境光強度設置為 1.0")
                    else:
                        logger.warning(
                            f"設置初始環境光強度失敗: {await response.text()}"
                        )
            # 新增：燈光漸亮呼吸效果（背景執行，並追蹤任務）
            self._light_breath_task = asyncio.create_task(
                self._breathing_light_effect(brighten=True)
            )
        except Exception as e:
            logger.error(f"設置初始環境光強度異常: {e}")

    def _get_memory_system(self) -> MemorySystem:
        """獲取記憶系統實例（懶加載）"""
        if self._memory_system is None:
            try:
                # 初始化嵌入模型
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY
                )

                # 初始化LLM
                llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.7,
                )

                # 創建記憶系統
                self._memory_system = MemorySystem(
                    embeddings=embeddings, persona_name="太空直播AI", llm=llm
                )

                logger.info("📝 WebSocket 處理器中的記憶系統初始化成功")
            except Exception as e:
                logger.error(f"❌ 記憶系統初始化失敗: {e}")
                # 返回 None 而不是拋出異常，避免影響主要功能
                return None

        return self._memory_system

    async def stream_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks to OpenAI and yield TTS audio bytes."""
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
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
                # 啟動前重置實體燈連線，確保乾淨狀態
                try:
                    await self._reset_physical_light_connection()
                except Exception as _e:
                    logger.warning(f"會話啟動前重置實體燈連線失敗: {_e}")
                # 新增：設定初始環境光強度
                await self._set_initial_environment_light()
                # 新增：即時對話啟動時開啟招牌燈（channel 0 設為 1）
                await self._set_sign_light(True)
                # 新增：即時對話啟動時關閉所有螢幕並停止任何既有輪播（服務化）
                await video_rotation_service.stop_rotation()
                await video_rotation_service.enable_inhibit()
                # 新增：開始 YouTube 聊天室監控
                logger.info("🎬 [DEBUG] 準備啟動 YouTube 聊天室監控...")
                await self._start_youtube_chat_monitoring()
                # 新增：啟動 YouTube 聊天留言監控任務
                logger.info("🔄 [DEBUG] 創建 YouTube 聊天留言監控任務...")
                self._youtube_monitor_task = asyncio.create_task(
                    self._monitor_youtube_chat_messages()
                )
                logger.info(
                    f"✅ [DEBUG] YouTube 監控任務已創建: {self._youtube_monitor_task}"
                )

                # 等待會話配置確認
                await asyncio.sleep(0.5)

                # 已移除：啟動時注入最近對話記憶，避免影響預設性格

                # 根據最近對話記憶生成並套用背景圖片（不切換3D房間場景）
                await self._generate_background_from_conversation()

                await self._set_initial_camera()
                # 新增：設定初始角色位置（Y 軸下降 30 單位）
                await self._set_initial_character_position()

                # 設定初始動畫，避免T-pose
                await self._set_initial_animation()

                # 設定舞群初始動畫
                # 新增：初始化時隨機播放一首 BGM
                await self._play_initial_bgm()
                # 自動發送歡迎訊息
                await self._send_welcome_message()

                # 創建音頻接收隊列
                audio_queue = asyncio.Queue(
                    maxsize=50
                )  # 限制隊列大小避免記憶體過度使用
                # 創建中斷訊號隊列
                interrupt_queue = asyncio.Queue(maxsize=10)
                # 創建文字接收隊列
                text_queue = asyncio.Queue(maxsize=100)

                # 啟動並行任務
                send_task = asyncio.create_task(
                    self._send_audio_to_openai(ws, audio_chunks)
                )
                receive_task = asyncio.create_task(
                    self._receive_openai_responses(
                        ws, audio_queue, interrupt_queue, text_queue
                    )
                )

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
                                    text_json = json.dumps(
                                        {"type": "text", "content": text_data}
                                    )
                                    yield f"TEXT_DATA:{text_json}".encode("utf-8")
                                    continue
                            except asyncio.QueueEmpty:
                                pass

                            # 檢查音頻數據
                            audio_data = await asyncio.wait_for(
                                audio_queue.get(), timeout=0.1
                            )
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
                    # 自動關閉背景音樂
                    await self._stop_bgm()
                    # 自動關閉場景顯示
                    await self._hide_scene()
                    # 停用背景圖片，確保待機時無背景圖
                    try:
                        import aiohttp

                        async with aiohttp.ClientSession() as session:
                            await session.post(
                                "http://localhost:8000/api/disable-background-image"
                            )
                        logger.info("已停用背景圖片（待機狀態）")
                    except Exception as _e:
                        logger.warning(f"停用背景圖片時發生例外: {_e}")
                    # 嘗試取消燈光呼吸效果任務，避免殘留持續改變亮度
                    if (
                        self._light_breath_task is not None
                        and not self._light_breath_task.done()
                    ):
                        try:
                            self._light_breath_task.cancel()
                            await self._light_breath_task
                        except asyncio.CancelledError:
                            pass
                        except Exception as _e:
                            logger.warning(f"取消呼吸燈任務時發生例外: {_e}")
                    self._light_breath_task = None
                    # 新增：停止 YouTube 聊天室監控
                    await self._stop_youtube_chat_monitoring()
                    # 停止 YouTube 聊天監控任務
                    if self._youtube_monitor_task:
                        self._youtube_monitor_task.cancel()
                        self._youtube_monitor_task = None
                    # 清理WebSocket引用
                    self._current_ws = None
                    # 關閉日誌記錄器
                    if self._session_logger:
                        self._session_logger.log_connection_closed("Normal closure")
                        self._session_logger = None
                    # 新增：燈光直接關閉（設為 0），且等待完成，避免殘留
                    import aiohttp

                    try:
                        await self._set_light_off()
                    except Exception as _e:
                        logger.warning(f"關閉燈光時發生例外: {_e}")
                    # 新增：即時對話結束時關閉招牌燈（channel 0 設為 0），等待完成
                    try:
                        await self._set_sign_light(False)
                    except Exception as _e:
                        logger.warning(f"關閉招牌燈時發生例外: {_e}")
                    # 新增：重置實體燈連線，避免殘留序列埠被佔用
                    try:
                        await self._reset_physical_light_connection()
                    except Exception as _e:
                        logger.warning(f"重置實體燈連線時發生例外: {_e}")
                    # 變更：即時對話結束後不再恢復影片輪播，保持螢幕隱藏（inhibit 維持啟用）
                    logger.info("會話結束：不恢復影片輪播，保持螢幕關閉以符合待機需求")

        except ConnectionClosed:
            logger.error("WebSocket connection to OpenAI was closed")
            if self._session_logger:
                self._session_logger.log_connection_closed(
                    "WebSocket connection closed"
                )
            raise
        except Exception as e:
            logger.error(f"Error in OpenAI Realtime WebSocket: {e}")
            if self._session_logger:
                self._session_logger.log_error("WEBSOCKET_ERROR", str(e))
            raise

    async def _send_session_update(self, ws):
        """發送會話配置到 OpenAI"""
        session_event = await create_session_config()
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
                    base64_audio = base64.b64encode(chunk).decode("utf-8")
                    audio_event = {
                        "type": "input_audio_buffer.append",
                        "audio": base64_audio,
                    }
                    await ws.send(json.dumps(audio_event))
                    logger.info(
                        f"Sent audio chunk #{chunk_count}: {len(chunk)} bytes (PCM16 format)"
                    )

                    # 記錄音頻塊發送
                    if self._session_logger:
                        self._session_logger.log_audio_chunk_sent(
                            chunk_count, len(chunk)
                        )

                    # 依賴 OpenAI 的 server_vad 自動檢測語音結束並回應
                    # 不再手動觸發回應

        except Exception as e:
            logger.error(f"Error sending audio to OpenAI: {e}")
            if self._session_logger:
                self._session_logger.log_error("AUDIO_SEND_ERROR", str(e))

    async def _receive_openai_responses(
        self,
        ws,
        audio_queue: asyncio.Queue,
        interrupt_queue: asyncio.Queue,
        text_queue: asyncio.Queue,
    ):
        """接收來自 OpenAI 的回應"""
        try:
            async for message in ws:
                # 使用 asyncio.create_task 確保每個事件處理都是異步的，不會相互阻塞
                asyncio.create_task(
                    self._process_openai_event(
                        message, audio_queue, interrupt_queue, text_queue
                    )
                )

        except ConnectionClosed:
            logger.info("OpenAI WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving from OpenAI: {e}")
            if self._session_logger:
                self._session_logger.log_error("AUDIO_RECEIVE_ERROR", str(e))
        finally:
            # 發送結束信號
            await audio_queue.put(None)

    async def _process_openai_event(
        self,
        message,
        audio_queue: asyncio.Queue,
        interrupt_queue: asyncio.Queue,
        text_queue: asyncio.Queue,
    ):
        """處理單個OpenAI事件 - 確保非阻塞處理"""
        try:
            event = json.loads(message)
            logger.debug(f"Received event: {event.get('type')}")

            # 記錄接收到的事件
            if self._session_logger:
                self._session_logger.log_event_received(
                    event.get("type", "unknown"), event
                )

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
                        self._session_logger.log_audio_processed(
                            len(pcm_data), len(wav_data)
                        )

                    # 使用 put_nowait 避免阻塞，如果隊列滿則跳過
                    try:
                        audio_queue.put_nowait(wav_data)
                    except asyncio.QueueFull:
                        logger.warning("Audio queue is full, skipping audio chunk")

            # 處理Function Calling - 使用正確的事件
            elif event.get("type") == "response.output_item.done":
                item = event.get("item", {})

                # 詳細記錄item內容以便調試
                logger.info(
                    f"🔍 Output item done - type: {item.get('type')}, item details: {item}"
                )

                # 檢查是否為function call
                if item.get("type") == "function_call":
                    function_name = item.get("name")
                    call_id = item.get("call_id")
                    arguments_json = item.get("arguments", "{}")

                    logger.info(
                        f"🎯 Function call detected: {function_name} with call_id: {call_id}"
                    )
                    logger.info(f"📝 Function arguments: {arguments_json}")

                    # 這裡需要由外部提供的tool_executor來執行工具函數
                    if hasattr(self, "tool_executor") and self.tool_executor:
                        tool_result = await self.tool_executor(
                            function_name, arguments_json
                        )
                    else:
                        tool_result = {
                            "success": False,
                            "error": "No tool executor configured",
                        }

                    # 記錄 Function Call 執行結果
                    if self._session_logger:
                        self._session_logger.log_function_call_executed(
                            function_name, call_id, tool_result
                        )

                    # 發送工具結果回OpenAI - 使用正確的格式
                    tool_result_event = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": json.dumps(tool_result),
                        },
                    }
                    await self._ws_send_safe(tool_result_event)

                    # 請求OpenAI繼續回應
                    response_create_event = {"type": "response.create"}
                    await self._ws_send_safe(response_create_event)

                    logger.info(
                        f"✅ Sent tool result and requested new response for call_id: {call_id}"
                    )
                else:
                    # 記錄非function call的項目
                    logger.debug(f"📄 Non-function output item: {item.get('type')}")

            # 處理用戶開始說話事件 - 實現中斷功能
            elif event.get("type") == "input_audio_buffer.speech_started":
                logger.info("User started speaking - interrupting AI response")

                # 直接發送取消回應指令（不檢查是否有活躍回應）
                # 根據錯誤訊息，OpenAI 會自己處理是否有活躍回應
                try:
                    cancel_event = {"type": "response.cancel"}
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
                text_delta = event.get("delta", "")
                if text_delta:
                    logger.info(f"OpenAI audio transcript: {text_delta}")
                    try:
                        text_queue.put_nowait(text_delta)
                    except asyncio.QueueFull:
                        logger.warning("Text queue is full, skipping text delta")

            # 處理用戶輸入轉錄 - 新增！
            elif (
                event.get("type") == "conversation.item.input_audio_transcription.delta"
            ):
                user_transcript_delta = event.get("delta", "")
                if user_transcript_delta:
                    logger.info(f"👤 User transcript delta: {user_transcript_delta}")
                    # 記錄用戶輸入轉錄增量
                    if self._session_logger:
                        self._session_logger.log_user_transcript_delta(
                            user_transcript_delta
                        )

            # 處理用戶輸入轉錄完成 - 新增！
            elif (
                event.get("type")
                == "conversation.item.input_audio_transcription.completed"
            ):
                user_transcript = event.get("transcript", "")
                if user_transcript:
                    logger.info(f"👤 User transcript completed: {user_transcript}")
                    # 記錄完整的用戶輸入轉錄
                    if self._session_logger:
                        self._session_logger.log_user_transcript_completed(
                            user_transcript
                        )

            # 處理會話物品創建 - 檢查用戶輸入
            elif event.get("type") == "conversation.item.created":
                item = event.get("item", {})
                if item.get("role") == "user":
                    logger.info(f"👤 User conversation item created: {item.get('id')}")
                    # 檢查是否有直接的轉錄內容
                    content = item.get("content", [])
                    for content_item in content:
                        if content_item.get(
                            "type"
                        ) == "input_audio" and content_item.get("transcript"):
                            transcript = content_item.get("transcript")
                            logger.info(
                                f"👤 User input transcript from item: {transcript}"
                            )
                            if self._session_logger:
                                self._session_logger.log_user_transcript_completed(
                                    transcript
                                )

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
                        self._session_logger.log_error(
                            "INVALID_VALUE_ERROR",
                            error_message,
                            {"error_code": error_code, "full_event": event},
                        )
                else:
                    logger.error(f"OpenAI API error: {event}")
                    # 記錄詳細錯誤到會話日誌
                    if self._session_logger:
                        self._session_logger.log_error(
                            "OPENAI_API_ERROR",
                            error_message,
                            {
                                "error_code": error_code,
                                "error_info": error_info,
                                "full_event": event,
                            },
                        )

            # 處理會話創建
            elif event.get("type") == "session.created":
                logger.info("OpenAI session created successfully")

            # 處理會話更新
            elif event.get("type") == "session.updated":
                logger.info("OpenAI session updated successfully")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
            if self._session_logger:
                self._session_logger.log_error(
                    "JSON_PARSE_ERROR", str(e), {"message": message}
                )
        except Exception as e:
            logger.error(f"Error processing OpenAI response: {e}")
            if self._session_logger:
                self._session_logger.log_error("EVENT_PROCESSING_ERROR", str(e))

    async def _ws_send_safe(self, event_dict):
        """安全地發送WebSocket消息，避免阻塞"""
        try:
            if hasattr(self, "_current_ws") and self._current_ws:
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
                    json=preset_data,
                ) as response:
                    if response.status == 200:
                        logger.info("初始相機預設設置為 frontal_dynamic_low")
                    else:
                        logger.warning(f"設置初始相機預設失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"設置初始相機預設異常: {e}")

    async def _set_initial_character_position(self):
        """設定初始角色位置：將 Y 軸往下移動 30 單位 (絕對座標 [0, -30, 0])"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"position": [0, -10, 0]}
                async with session.post(
                    "http://localhost:8000/api/control/character/position", json=payload
                ) as response:
                    if response.status == 200:
                        logger.info("初始角色位置已設定為 [0, -30, 0]")
                    else:
                        text = await response.text()
                        logger.warning(
                            f"設定初始角色位置失敗: HTTP {response.status} - {text}"
                        )
        except Exception as e:
            logger.error(f"設定初始角色位置異常: {e}")

    async def _set_initial_animation(self):
        """設定初始動畫，避免T-pose"""
        import random

        import aiohttp

        try:
            # 可用的初始動畫清單（排除Tpose）
            available_animations = [
                "運動2",
                "漂浮",
                "運動1",
                "不穩",
                "划手機",
                "漂浮2",
                "臥躺",
                "舞步1",
                "舞步2",
                "舞步3",
                "飛1",
                "飛2",
            ]

            # 隨機選擇一個動畫
            selected_animation = random.choice(available_animations)

            async with aiohttp.ClientSession() as session:
                animation_data = {
                    "animation": selected_animation,
                    "loop": True,
                    "speed": 1.0,
                }
                async with session.post(
                    "http://localhost:8000/api/control/character/animation",
                    json=animation_data,
                ) as response:
                    if response.status == 200:
                        logger.info(
                            f"初始動畫隨機設置為: {selected_animation}，避免T-pose"
                        )
                    else:
                        logger.warning(f"設置初始動畫失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"設置初始動畫異常: {e}")

    async def _play_initial_bgm(self):
        """隨機選擇一首 BGM 並播放（初始化用）"""
        import random

        import aiohttp

        try:
            bgm_files = [
                "spacelive_theme.mp3",
                "spacelive_theme2.mp3",
                "space_live_country_theme1.mp3",
                "space_live_country_theme2.mp3",
                "heavy_metal_bgm_01.mp3",
                "heavy_metal_bgm_02.mp3",
                "heavy_metal_bgm_03.mp3",
                "星際狂舞.mp3",
                "太空媽祖.mp3",
                "hihi.mp3",
                "hihi (1).mp3",
                "hihi (2).mp3",
                "hihi (3).mp3",
            ]
            selected_bgm = random.choice(bgm_files)
            bgm_url = f"/audio/BGM/{selected_bgm}"
            async with aiohttp.ClientSession() as session:
                bgm_data = {"bgmUrl": bgm_url, "volume": 0.1}
                async with session.post(
                    "http://localhost:8000/api/control/background-audio", json=bgm_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"初始隨機 BGM 播放成功: {selected_bgm}")
                        self._current_bgm_url = bgm_url  # 儲存 BGM URL
                    else:
                        logger.warning(f"初始 BGM 播放失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"初始 BGM 播放異常: {e}")

    async def _send_welcome_message(self):
        """自動發送隨機歡迎訊息"""
        import random

        import aiohttp

        try:
            welcome_messages = [
                "哈摟我是你最辣的太空主播，今天好嗎？這裡是屬於你的宇宙舞台，直接對我說話就可以囉～有什麼想聊的、想看的都可以直接說出來！",
                "歡迎來到太空艙直播間，這裡有最炫的星際表演和最潮的互動體驗！你現在可以直接和我對話，快來聊聊宇宙的祕密吧！",
                "Yo～這裡是賽博太空艙，準備好一起high了嗎？直接對我說話就能啟動零重力派對模式，讓我們用聲音連結彼此的星球！",
                "哈囉！我是來自近地軌道的太空主播，今天要帶你體驗宇宙級的互動！現在你可以直接和我對話，這裡就是你的專屬星球！",
                "太空連線成功！主播在這裡等你很久囉！只要直接說話，我就能聽見你，準備好一起探索星際、發現新奇的宇宙故事了嗎？",
                "地球的朋友午安，這裡是最潮的太空直播間！直接和主播對話，今天一起嗨翻銀河系吧！",
                "準備好進入無重力的歡樂時光了嗎？在這裡你可以直接開口說話，還有機會看到主播的太空舞步喔！",
                "哈囉哈囉～主播已經在太空艙stand by囉！隨時等你直接和我互動，讓我們一起開啟宇宙冒險！",
                "今天要不要來點太空瑜伽還是跳個舞？只要你直接說出來，主播都能陪你一起動起來，讓我們一起在星空下律動！",
                "歡迎光臨！這裡是最有梗的太空直播主，陪你high翻宇宙！直接對我說話，讓我們一起創造屬於你的星際回憶！",
                "星際連線已啟動，主播已經準備好和你一起探索宇宙的奧秘，想問什麼、想玩什麼直接說出來吧！",
                "銀河系的朋友們集合啦！這裡是你的太空夥伴主播，現在可以直接和我對話，讓我們一起開啟星際冒險！",
                "宇宙信號穩定連線中，想聽故事還是想點歌？直接對我說話，我都能陪你一起玩！",
                "歡迎進入零重力聊天室，這裡沒有距離，只有即時互動！有什麼想法直接說給主播聽吧！",
                "太空艙門已經打開，主播在這裡等你一起high翻宇宙，直接對我說話就能開始互動囉！",
                "地球呼叫太空艙，收到請回應！你現在可以直接和主播對話，讓我們一起創造星際回憶！",
                "星際派對正式啟動，想玩什麼、想聊什麼直接說出來，主播都能陪你一起嗨！",
                "宇宙廣播開啟，這裡是你的太空主播，現在可以直接對我說話，讓我們一起探索無限可能！",
                "歡迎來到星際互動空間，這裡每一句話都能即時傳到主播耳朵裡，快來和我聊聊你的宇宙夢想！",
                "太空信號滿格，主播隨時待命！有任何想法、願望、問題都可以直接說出來，讓我們一起玩出新宇宙！",
            ]
            message = random.choice(welcome_messages)
            async with aiohttp.ClientSession() as session:
                message_data = {"content": message, "message_type": "chat-message"}
                async with session.post(
                    "http://localhost:8000/api/control/send-message", json=message_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"自動發送歡迎訊息成功: {message}")
                    else:
                        logger.warning(f"發送歡迎訊息失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"發送歡迎訊息失敗: {e}")

    async def _stop_bgm(self):
        """將背景音樂音量調整為 0.3（不直接關閉 BGM）"""
        import aiohttp

        try:
            # 取得目前 BGM URL（假設前端會維持原 bgmUrl，不清空）
            # 若有全域變數或屬性可取得目前 bgmUrl，請取用，否則只設 volume
            bgm_url = getattr(self, "_current_bgm_url", None)
            bgm_data = {"volume": 0.3}
            if bgm_url:
                bgm_data["bgmUrl"] = bgm_url
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/control/background-audio", json=bgm_data
                ) as response:
                    if response.status == 200:
                        logger.info("已將背景音樂音量調整為 0.3（session 結束）")
                    else:
                        logger.warning(f"調整 BGM 音量失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"調整 BGM 音量發生異常: {e}")

    async def _hide_scene(self):
        """關閉場景顯示（隱藏背景）"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                scene_data = {"displayScene": False}
                async with session.post(
                    "http://localhost:8000/api/control/scene-display", json=scene_data
                ) as response:
                    if response.status == 200:
                        logger.info("已自動關閉場景顯示（session 結束）")
                    else:
                        logger.warning(f"自動關閉場景失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"自動關閉場景發生異常: {e}")
        # 新增：會話結束後重置環境光強度
        await self._reset_environment_light()

    async def _reset_environment_light(self):
        """重置環境光強度為 0.1"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                payload = {"intensity": 0.1}
                async with session.post(
                    "http://localhost:8000/api/control/environment/config", json=payload
                ) as response:
                    if response.status == 200:
                        logger.info("環境光強度重置為 0.1")
                    else:
                        logger.warning(f"重置環境光強度失敗: {await response.text()}")
        except Exception as e:
            logger.error(f"重置環境光強度異常: {e}")

    def set_tool_executor(self, executor):
        """設定工具執行器"""
        self.tool_executor = executor

    async def _set_light_off(self):
        """直接將燈光設為 0（全暗）"""
        import aiohttp

        base_url = "http://localhost:8000/api/physical-light/set-brightness"
        async with aiohttp.ClientSession() as session:
            await session.post(base_url, json={"brightness": 0})

    async def _set_sign_light(self, on: bool):
        """控制招牌燈（通道 0，開關）。"""
        import aiohttp

        base_url = "http://localhost:8000/api/physical-light/set-channel-brightness"
        payload = {"channel": 0, "brightness": 1 if on else 0}
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(base_url, json=payload)
        except Exception:
            # 靜默失敗以避免影響主要流程
            pass

    async def _reset_physical_light_connection(self):
        """呼叫後端 API 重置實體燈序列埠連線，避免殘留連線干擾下次會話。"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "http://localhost:8000/api/physical-light/reset-connection"
                )
        except Exception as e:
            # 只記錄警告，不阻斷主要流程
            logger.warning(f"重置實體燈序列埠連線失敗: {e}")

    async def _start_youtube_chat_monitoring(self):
        """開始 YouTube 聊天室監控"""
        try:
            logger.info(
                f"🚀 [DEBUG] 即時對話會話開始，啟動 YouTube 聊天室監控：{self._channel_id}"
            )

            # 檢查服務狀態
            logger.debug(
                f"🔍 [DEBUG] YouTube 服務狀態檢查: service={self._youtube_chat_service}, is_monitoring={self._youtube_chat_service.is_monitoring}"
            )

            # 使用頻道 ID 開始監控（自動獲取當前直播）
            result = self._youtube_chat_service.start_monitoring_by_channel(
                self._channel_id
            )
            logger.debug(f"📊 [DEBUG] 監控啟動結果: {result}")

            if result["success"]:
                video_id = result.get("video_id")
                logger.info(
                    f"✅ [DEBUG] YouTube 聊天室監控啟動成功！video_id: {video_id}"
                )

                # 立即檢查一次狀態
                status = self._youtube_chat_service.get_monitoring_status()
                logger.debug(f"📈 [DEBUG] 監控狀態確認: {status}")

                # 取得初始留言計數
                initial_messages = self._youtube_chat_service.get_recent_messages(
                    limit=10
                )
                self._last_processed_message_count = len(initial_messages)
                logger.info(
                    f"📝 [DEBUG] 初始留言計數設為: {self._last_processed_message_count}"
                )

                if initial_messages:
                    preview = [
                        f"{msg.get('author', '?')}:{msg.get('message', '?')[:15]}..."
                        for msg in initial_messages[:3]
                    ]
                    logger.debug(f"📋 [DEBUG] 初始留言預覽: {preview}")
                else:
                    logger.debug("📭 [DEBUG] 目前沒有歷史留言")

            else:
                error_msg = result.get("error", "未知錯誤")
                logger.warning(f"❌ [DEBUG] YouTube 聊天室監控啟動失敗: {error_msg}")
                logger.debug(f"🔍 [DEBUG] 失敗詳情: {result}")

        except Exception as e:
            logger.error(f"💥 [DEBUG] 啟動 YouTube 聊天室監控時發生錯誤: {e}")
            import traceback

            logger.error(f"🔍 [DEBUG] 啟動錯誤詳情: {traceback.format_exc()}")

    async def _stop_youtube_chat_monitoring(self):
        """停止 YouTube 聊天室監控"""
        try:
            logger.info("即時對話會話結束，停止 YouTube 聊天室監控")
            result = self._youtube_chat_service.stop_monitoring()
            if result["success"]:
                logger.info("YouTube 聊天室監控已停止")
            else:
                logger.warning(f"停止 YouTube 聊天室監控失敗: {result.get('error')}")
        except Exception as e:
            logger.error(f"停止 YouTube 聊天室監控時發生錯誤: {e}")

    async def _monitor_youtube_chat_messages(self):
        """監控 YouTube 聊天留言並即時注入到 OpenAI Realtime WebSocket"""
        logger.info("🎯 [DEBUG] 開始監控 YouTube 聊天留言，準備即時注入到對話中")

        iteration_count = 0
        while (
            self._current_ws
            and self._current_ws.state != websockets.protocol.State.CLOSED
        ):
            try:
                iteration_count += 1
                logger.debug(f"🔄 [DEBUG] YouTube 監控迭代 #{iteration_count}")

                # 檢查 WebSocket 狀態
                logger.debug(
                    f"📡 [DEBUG] WebSocket 狀態: current_ws={self._current_ws is not None}, state={self._current_ws.state if self._current_ws else 'N/A'}"
                )

                # 檢查是否有新的聊天留言
                if not self._youtube_chat_service.is_monitoring:
                    logger.debug(
                        f"⏸️ [DEBUG] YouTube 聊天室監控未啟動，is_monitoring={self._youtube_chat_service.is_monitoring}"
                    )
                    await asyncio.sleep(2)
                    continue

                logger.debug(
                    f"✅ [DEBUG] YouTube 聊天室監控中，is_monitoring={self._youtube_chat_service.is_monitoring}"
                )

                # 取得最近的聊天留言
                recent_messages = self._youtube_chat_service.get_recent_messages(
                    limit=10
                )
                current_message_count = len(recent_messages)

                logger.debug(
                    f"📊 [DEBUG] 訊息統計: current_count={current_message_count}, last_processed={self._last_processed_message_count}"
                )

                # 如果有留言，顯示最新幾條的預覽
                if recent_messages:
                    preview = [
                        f"{msg.get('author', '?')}:{msg.get('message', '?')[:20]}..."
                        for msg in recent_messages[:3]
                    ]
                    logger.debug(f"📝 [DEBUG] 最新留言預覽: {preview}")
                else:
                    logger.debug("📭 [DEBUG] 目前沒有任何留言")

                # 如果有新留言
                if current_message_count > self._last_processed_message_count:
                    # 計算新留言的數量
                    new_message_count = (
                        current_message_count - self._last_processed_message_count
                    )
                    # 取得新留言（最新的幾條）
                    new_messages = recent_messages[:new_message_count]

                    logger.info(
                        f"🆕 [DEBUG] 發現 {new_message_count} 條新留言！準備注入到 OpenAI"
                    )

                    for i, message in enumerate(
                        reversed(new_messages)
                    ):  # 反轉以按時間順序處理
                        logger.debug(
                            f"💬 [DEBUG] 處理新留言 {i+1}/{new_message_count}: {message.get('author', '?')} - {message.get('message', '?')}"
                        )
                        await self._inject_youtube_message_to_openai(message)

                    self._last_processed_message_count = current_message_count
                    logger.info(
                        f"✅ [DEBUG] 已處理完 {new_message_count} 條新留言，更新計數器到 {current_message_count}"
                    )
                else:
                    logger.debug(
                        f"😴 [DEBUG] 沒有新留言 (current={current_message_count}, last={self._last_processed_message_count})"
                    )

                # 每 1.5 秒檢查一次
                logger.debug("⏰ [DEBUG] 等待 1.5 秒後進行下次檢查...")
                await asyncio.sleep(1.5)

            except asyncio.CancelledError:
                logger.info("🛑 [DEBUG] YouTube 聊天留言監控任務被取消")
                break
            except Exception as e:
                logger.error(f"❌ [DEBUG] 監控 YouTube 聊天留言時發生錯誤: {e}")
                import traceback

                logger.error(f"🔍 [DEBUG] 錯誤詳情: {traceback.format_exc()}")
                await asyncio.sleep(3)  # 發生錯誤時稍微等久一點

    async def _inject_youtube_message_to_openai(self, message_data: dict):
        """將 YouTube 聊天留言注入到 OpenAI Realtime WebSocket"""
        try:
            logger.debug(f"🚀 [DEBUG] 開始注入 YouTube 留言: {message_data}")

            if (
                not self._current_ws
                or self._current_ws.state == websockets.protocol.State.CLOSED
            ):
                logger.warning(
                    f"❌ [DEBUG] WebSocket 不可用，無法注入留言: current_ws={self._current_ws is not None}, state={self._current_ws.state if self._current_ws else 'N/A'}"
                )
                return

            author = message_data.get("author", "觀眾")
            message_text = message_data.get("message", "")

            logger.debug(
                f"👤 [DEBUG] 留言詳情: author='{author}', message='{message_text}', length={len(message_text.strip()) if message_text else 0}"
            )

            # 過濾掉空訊息或純表情符號
            if not message_text.strip() or len(message_text.strip()) < 2:
                logger.debug(f"🚫 [DEBUG] 留言被過濾（太短或空白）: '{message_text}'")
                return

            # 構造用戶訊息格式，加上來源標識
            formatted_message = f"[YouTube 觀眾 {author}]: {message_text}"

            logger.info(f"💬 [DEBUG] 準備注入格式化留言到 OpenAI: {formatted_message}")

            # 創建 conversation.item.create 事件
            conversation_item = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": formatted_message}],
                },
            }

            logger.debug(
                f"📤 [DEBUG] 準備發送 conversation.item.create 事件: {json.dumps(conversation_item, ensure_ascii=False)}"
            )

            # 發送到 OpenAI
            await self._current_ws.send(json.dumps(conversation_item))
            logger.info(
                f"✅ [DEBUG] 已發送 YouTube 留言到 OpenAI: {author} - {message_text}"
            )

            # 存儲到記憶系統
            try:
                memory_system = self._get_memory_system()
                if memory_system:
                    memory_system.store_chat_message(message_data)
                    logger.info(
                        f"💾 [DEBUG] 已將 YouTube 留言存儲到記憶系統: {author} - {message_text[:30]}..."
                    )
                else:
                    logger.warning("⚠️ [DEBUG] 記憶系統不可用，跳過留言存儲")
            except Exception as memory_error:
                logger.error(f"❌ [DEBUG] 存儲留言到記憶系統失敗: {memory_error}")
                # 不影響主要流程，繼續執行

            # 記錄到會話日誌
            if self._session_logger:
                self._session_logger.log_event_sent(
                    "conversation.item.create", conversation_item
                )
                logger.debug(f"📝 [DEBUG] 已記錄到會話日誌")

            # 等待一小段時間確保訊息被處理
            await asyncio.sleep(0.1)

            # 觸發 AI 回應
            response_create = {"type": "response.create"}

            logger.debug(
                f"🎯 [DEBUG] 準備發送 response.create 觸發 AI 回應: {json.dumps(response_create)}"
            )
            await self._current_ws.send(json.dumps(response_create))
            logger.info("🚀 [DEBUG] 已觸發 AI 回應 YouTube 聊天留言")

        except Exception as e:
            logger.error(f"❌ [DEBUG] 注入 YouTube 聊天留言時發生錯誤: {e}")
            import traceback

            logger.error(f"🔍 [DEBUG] 注入錯誤詳情: {traceback.format_exc()}")
