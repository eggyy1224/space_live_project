"""
測試背景音頻工具功能
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from services.realtime_conversation.api_integrations import APIIntegrations


class TestBackgroundAudioTool:
    """測試背景音頻工具"""
    
    @pytest.fixture
    def api_integrations(self):
        """創建 APIIntegrations 實例"""
        return APIIntegrations()
    
    @pytest.mark.asyncio
    async def test_background_audio_tool_function_call(self, api_integrations):
        """測試透過 execute_tool_function 調用 background_audio"""
        
        # 模擬成功的 HTTP 回應
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{"status": "success"}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 測試 BGM 播放
            arguments = {
                "bgmUrl": "/audio/BGM/spacelive_theme.mp3"
            }
            
            result = await api_integrations.execute_tool_function(
                "background_audio", 
                json.dumps(arguments)
            )
            
            # 驗證結果
            assert result["success"] is True
            assert "BGM已設置" in result["message"]
            
            # 驗證API調用
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "/api/control/background-audio" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_background_audio_bgm_only(self, api_integrations):
        """測試只設置BGM"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3"
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is True
            assert "BGM已設置" in result["message"]
    
    @pytest.mark.asyncio
    async def test_background_audio_sfx_only(self, api_integrations):
        """測試只播放音效"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is True
            assert "音效已播放" in result["message"]
    
    @pytest.mark.asyncio
    async def test_background_audio_bgm_control(self, api_integrations):
        """測試BGM播放控制"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 測試暫停
            arguments = {
                "bgmPlaying": False
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is True
            assert "已暫停" in result["message"]
            
            # 測試播放
            arguments = {
                "bgmPlaying": True
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is True
            assert "已播放" in result["message"]
    
    @pytest.mark.asyncio
    async def test_background_audio_stop_bgm(self, api_integrations):
        """測試停止BGM"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "bgmUrl": ""  # 空字串表示停止
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is True
            assert "BGM已停止" in result["message"]
    
    @pytest.mark.asyncio
    async def test_background_audio_combined_params(self, api_integrations):
        """測試組合參數"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "bgmUrl": "/audio/BGM/spacelive_theme.mp3",
                "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is True
            assert "BGM已設置" in result["message"]
            assert "音效已播放" in result["message"]
    
    @pytest.mark.asyncio
    async def test_background_audio_no_params_error(self, api_integrations):
        """測試沒有參數時的錯誤處理"""
        
        arguments = {}
        
        result = await api_integrations._handle_background_audio(arguments)
        
        assert result["success"] is False
        assert "At least one parameter" in result["error"]
    
    @pytest.mark.asyncio
    async def test_background_audio_http_error(self, api_integrations):
        """測試HTTP錯誤處理"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value='Internal Server Error')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "bgmUrl": "/audio/BGM/spacelive_theme.mp3"
            }
            
            result = await api_integrations._handle_background_audio(arguments)
            
            assert result["success"] is False
            assert "HTTP 500" in result["error"] 