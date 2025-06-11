"""
實時對話服務核心功能測試
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import AsyncIterator

from ..core import RealtimeConversationService


class TestRealtimeConversationService:
    """測試 RealtimeConversationService 主要功能"""
    
    @pytest.fixture
    def service(self):
        """創建測試用的服務實例"""
        with patch('core.config.settings.OPENAI_API_KEY', 'test-key'):
            return RealtimeConversationService()
    
    def test_initialization(self, service):
        """測試服務初始化"""
        assert service is not None
        assert service.websocket_handler is not None
        assert service.api_integrations is not None
        assert service.stream_processor is not None
        assert hasattr(service, 'client')
    
    def test_test_mode_operations(self, service):
        """測試模式操作測試"""
        # 初始狀態應該不是測試模式
        assert not service.is_test_mode()
        
        # 設定為測試模式
        service.set_test_mode(True)
        assert service.is_test_mode()
        
        # 關閉測試模式
        service.set_test_mode(False)
        assert not service.is_test_mode()
    
    def test_get_modules(self, service):
        """測試獲取子模組的方法"""
        assert service.get_websocket_handler() is service.websocket_handler
        assert service.get_api_integrations() is service.api_integrations
        assert service.get_stream_processor() is service.stream_processor
    
    @pytest.mark.asyncio
    async def test_execute_tool_function(self, service):
        """測試工具函數執行"""
        # Mock API integrations
        mock_result = {"success": True, "message": "test"}
        service.api_integrations.execute_tool_function = AsyncMock(return_value=mock_result)
        
        result = await service.execute_tool_function("test_function", '{"param": "value"}')
        
        assert result == mock_result
        service.api_integrations.execute_tool_function.assert_called_once_with(
            "test_function", '{"param": "value"}'
        )
    
    @pytest.mark.asyncio
    async def test_stream_conversation_fallback_to_test_mode(self, service):
        """測試當 WebSocket 失敗時回退到測試模式"""
        # Mock WebSocket handler to raise exception
        service.websocket_handler.stream_conversation = AsyncMock(side_effect=Exception("Connection failed"))
        
        # Mock test conversation
        async def mock_test_conversation(audio_chunks):
            yield b"test_audio_data"
        
        service.stream_processor.test_conversation = AsyncMock(return_value=mock_test_conversation(None))
        
        # 測試音頻數據
        async def audio_generator():
            yield b"input_audio"
        
        # 執行對話流
        results = []
        try:
            async for audio_data in service.stream_conversation(audio_generator()):
                results.append(audio_data)
        except Exception:
            pass  # 預期會有異常，因為是模擬失敗
        
        # 驗證測試模式被啟用
        assert service.stream_processor.is_test_mode()


if __name__ == "__main__":
    pytest.main([__file__]) 