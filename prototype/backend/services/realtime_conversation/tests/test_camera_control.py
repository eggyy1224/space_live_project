"""
測試鏡位控制工具功能
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from services.realtime_conversation.api_integrations import APIIntegrations


class TestCameraControlTool:
    """測試鏡位控制工具"""
    
    @pytest.fixture
    def api_integrations(self):
        """創建 APIIntegrations 實例"""
        return APIIntegrations()
    
    @pytest.mark.asyncio
    async def test_camera_control_tool_function_call(self, api_integrations):
        """測試透過 execute_tool_function 調用 camera_control"""
        
        # 模擬成功的 HTTP 回應
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{"status": "success"}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # 測試預設鏡位
            arguments = {
                "action": "set_preset",
                "preset": "overview",
                "duration": 3.0
            }
            
            result = await api_integrations.execute_tool_function(
                "camera_control", 
                json.dumps(arguments)
            )
            
            # 驗證結果
            assert result["success"] is True
            assert "鏡位已切換至: overview" in result["message"]
            assert result["action"] == "set_preset"
            
            # 驗證API調用
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "/api/control/camera/set-frontend-preset" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_camera_control_set_preset(self, api_integrations):
        """測試設定預設鏡位"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "action": "set_preset",
                "preset": "head_close_up",
                "duration": 2.5
            }
            
            result = await api_integrations._handle_camera_control(arguments)
            
            assert result["success"] is True
            assert "鏡位已切換至: head_close_up" in result["message"]
            assert "轉換時間: 2.5秒" in result["message"]
    
    @pytest.mark.asyncio
    async def test_camera_control_set_angle(self, api_integrations):
        """測試設定攝影機角度"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "action": "set_angle",
                "pitch": 30.0,
                "yaw": 45.0,
                "roll": 0.0
            }
            
            result = await api_integrations._handle_camera_control(arguments)
            
            assert result["success"] is True
            assert "pitch=30.0°, yaw=45.0°, roll=0.0°" in result["message"]
            assert result["action"] == "set_angle"
    
    @pytest.mark.asyncio
    async def test_camera_control_transition(self, api_integrations):
        """測試攝影機平滑轉換"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "action": "transition",
                "pitch": -20.0,
                "yaw": -30.0,
                "roll": 15.0,
                "duration": 6.0
            }
            
            result = await api_integrations._handle_camera_control(arguments)
            
            assert result["success"] is True
            assert "平滑轉換至: pitch=-20.0°, yaw=-30.0°, roll=15.0°" in result["message"]
            assert "耗時6.0秒" in result["message"]
            assert result["action"] == "transition"
    
    @pytest.mark.asyncio
    async def test_camera_control_invalid_action(self, api_integrations):
        """測試無效動作錯誤處理"""
        
        arguments = {
            "action": "invalid_action"
        }
        
        result = await api_integrations._handle_camera_control(arguments)
        
        assert result["success"] is False
        assert "Invalid action: invalid_action" in result["error"]
    
    @pytest.mark.asyncio
    async def test_camera_control_missing_preset(self, api_integrations):
        """測試缺少預設參數錯誤處理"""
        
        arguments = {
            "action": "set_preset"
            # 缺少 preset 參數
        }
        
        result = await api_integrations._handle_camera_control(arguments)
        
        assert result["success"] is False
        assert "preset parameter is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_camera_control_missing_angles(self, api_integrations):
        """測試缺少角度參數錯誤處理"""
        
        arguments = {
            "action": "set_angle",
            "pitch": 30.0
            # 缺少 yaw 和 roll 參數
        }
        
        result = await api_integrations._handle_camera_control(arguments)
        
        assert result["success"] is False
        assert "pitch, yaw, and roll parameters are required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_camera_control_http_error(self, api_integrations):
        """測試HTTP錯誤處理"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value='Internal Server Error')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                "action": "set_preset",
                "preset": "overview"
            }
            
            result = await api_integrations._handle_camera_control(arguments)
            
            assert result["success"] is False
            assert "HTTP 500" in result["error"]
    
    @pytest.mark.asyncio
    async def test_camera_control_default_action(self, api_integrations):
        """測試預設動作（set_preset）"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{}')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            arguments = {
                # 沒有指定 action，應該預設為 "set_preset"
                "preset": "dramatic_angle_1"
            }
            
            result = await api_integrations._handle_camera_control(arguments)
            
            assert result["success"] is True
            assert result["action"] == "set_preset"
            assert "dramatic_angle_1" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__]) 