"""
實時對話服務核心模組
重構後的主要服務類別，整合各個子模組功能。
"""

import asyncio
import logging
from typing import AsyncIterator, AsyncGenerator
import openai

from core.config import settings
from .websocket_handler import WebSocketHandler
from .api_integrations import APIIntegrations
from .stream_processor import StreamProcessor

logger = logging.getLogger(__name__)


class RealtimeConversationService:
    """
    實時對話服務的主要類別
    整合 OpenAI Realtime API 的完整功能，包含音效播放、表情動畫、自拍功能、圖片生成等。
    """

    def __init__(self) -> None:
        """初始化實時對話服務"""
        # 初始化 OpenAI 客戶端
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # 初始化子模組
        self.websocket_handler = WebSocketHandler(settings.OPENAI_API_KEY)
        self.api_integrations = APIIntegrations()
        self.stream_processor = StreamProcessor()
        
        # 設定工具執行器，讓 WebSocket 處理器能夠調用工具函數
        self.websocket_handler.set_tool_executor(self.api_integrations.execute_tool_function)
        
        logger.info("RealtimeConversationService initialized with all modules")

    async def stream_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """
        處理音頻流對話
        
        Args:
            audio_chunks: 音頻數據流迭代器
            
        Yields:
            bytes: TTS 音頻位元組數據
        """
        try:
            # 嘗試使用 OpenAI Realtime API WebSocket 連接
            async for audio_response in self.websocket_handler.stream_conversation(audio_chunks):
                yield audio_response
                
        except Exception as exc:  # pragma: no cover - network
            logger.error("Realtime conversation failed: %s", exc)
            logger.info("Falling back to test mode...")
            
            # 回退到測試模式
            self.stream_processor.set_test_mode(True)
            async for test_audio in self.stream_processor.test_conversation(audio_chunks):
                yield test_audio

    def set_test_mode(self, enabled: bool):
        """
        設定測試模式
        
        Args:
            enabled: 是否啟用測試模式
        """
        self.stream_processor.set_test_mode(enabled)
        
    def is_test_mode(self) -> bool:
        """
        檢查是否為測試模式
        
        Returns:
            bool: 是否為測試模式
        """
        return self.stream_processor.is_test_mode()
    
    async def execute_tool_function(self, function_name: str, arguments_json: str) -> dict:
        """
        執行工具函數（向外暴露的介面）
        
        Args:
            function_name: 工具函數名稱
            arguments_json: 參數 JSON 字串
            
        Returns:
            dict: 執行結果
        """
        return await self.api_integrations.execute_tool_function(function_name, arguments_json)
    
    def get_websocket_handler(self) -> WebSocketHandler:
        """獲取 WebSocket 處理器引用（用於測試或直接操作）"""
        return self.websocket_handler
    
    def get_api_integrations(self) -> APIIntegrations:
        """獲取 API 整合模組引用（用於測試或直接操作）"""
        return self.api_integrations
    
    def get_stream_processor(self) -> StreamProcessor:
        """獲取串流處理器引用（用於測試或直接操作）"""
        return self.stream_processor 