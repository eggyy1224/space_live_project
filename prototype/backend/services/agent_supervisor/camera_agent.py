"""
Camera Control Agent
專門負責攝影機控制的智能代理
從 realtime_conversation/api_integrations.py 遷移的邏輯
"""

import logging
import aiohttp
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CameraControlAgent:
    """
    攝影機控制專門代理
    負責執行各種攝影機控制操作
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        logger.info("📹 CameraControlAgent 初始化完成")
    
    async def execute_camera_control(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行攝影機控制操作
        從 realtime_conversation 遷移的邏輯
        """
        try:
            # 驗證必要參數
            action = arguments.get("action", "set_preset")
            
            if action not in ["set_preset", "set_angle", "transition"]:
                return {
                    "success": False,
                    "error": f"Invalid action: {action}. Must be one of: set_preset, set_angle, transition"
                }
            
            # 根據不同動作構建API請求
            if action == "set_preset":
                # 使用前端預設鏡位
                preset = arguments.get("preset")
                if not preset:
                    return {
                        "success": False,
                        "error": "preset parameter is required for set_preset action"
                    }
                
                duration = arguments.get("duration", 2.0)
                api_endpoint = "/api/control/camera/set-frontend-preset"
                request_data = {
                    "name": preset,
                    "duration": duration
                }
                
            elif action == "set_angle":
                # 立即設定攝影機角度
                pitch = arguments.get("pitch")
                yaw = arguments.get("yaw") 
                roll = arguments.get("roll")
                
                if pitch is None or yaw is None or roll is None:
                    return {
                        "success": False,
                        "error": "pitch, yaw, and roll parameters are required for set_angle action"
                    }
                
                api_endpoint = "/api/control/camera/set-angle"
                request_data = {
                    "pitch": pitch,
                    "yaw": yaw,
                    "roll": roll
                }
                
            elif action == "transition":
                # 平滑轉換攝影機角度
                pitch = arguments.get("pitch")
                yaw = arguments.get("yaw")
                roll = arguments.get("roll")
                duration = arguments.get("duration", 2.0)
                
                if pitch is None or yaw is None or roll is None:
                    return {
                        "success": False,
                        "error": "pitch, yaw, and roll parameters are required for transition action"
                    }
                
                api_endpoint = "/api/control/camera/transition"
                request_data = {
                    "pitch": pitch,
                    "yaw": yaw,
                    "roll": roll,
                    "duration": duration
                }
            
            logger.info(f"📹 準備執行攝影機控制: {action}")
            logger.info(f"🌐 發送請求到: {self.base_url}{api_endpoint}")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用對應的攝影機控制 API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}{api_endpoint}",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                        logger.info(f"📄 HTTP 回應內容: {response_text}")
                        
                        if response.status == 200:
                            try:
                                import json
                                result = json.loads(response_text) if response_text else {}
                                logger.info(f"✅ 成功控制攝影機")
                                
                                # 構建成功消息
                                if action == "set_preset":
                                    success_message = f"鏡位已切換至: {preset}"
                                    if duration > 0:
                                        success_message += f"，轉換時間: {duration}秒"
                                elif action == "set_angle":
                                    success_message = f"攝影機角度已設定: pitch={pitch}°, yaw={yaw}°, roll={roll}°"
                                elif action == "transition":
                                    success_message = f"攝影機平滑轉換至: pitch={pitch}°, yaw={yaw}°, roll={roll}°，耗時{duration}秒"
                                
                                return {
                                    "success": True,
                                    "message": success_message,
                                    "result": result,
                                    "action": action
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功控制攝影機 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Camera {action} executed successfully",
                                    "action": action
                                }
                        else:
                            logger.error(f"❌ 攝影機控制失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 攝影機控制請求超時")
                return {
                    "success": False,
                    "error": "Camera control request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 攝影機控制HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Camera control HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ camera_control 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control camera: {str(e)}"
            }
    
    def get_camera_presets(self) -> list:
        """獲取可用的攝影機預設鏡位列表"""
        return [
            "overview", "head_close_up", "dance_circle_view", "side_view", "low_angle_head",
            "center_orbit_high_1", "center_orbit_high_2", "center_orbit_low_1", "center_orbit_low_2",
            "top_down_center", "dramatic_angle_1", "dramatic_angle_2", "behind_head_looking_out",
            "fly_by_left", "fly_by_right", "frontal_dynamic_low", "frontal_dynamic_high",
            "orbit_head_1", "orbit_head_2", "full_shot_dancers"
        ] 