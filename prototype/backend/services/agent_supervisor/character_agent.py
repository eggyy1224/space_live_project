"""
Character Control Agent

專門處理角色控制相關的邏輯，包括：
- 角色縮放 (character scale)
- 角色位置 (character position) 
- 角色旋轉 (character rotation)
- 角色動畫 (character animation)
- 角色服裝 (character outfit)
- 角色可見性 (character visibility)
"""

import json
import logging
import aiohttp
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CharacterControlAgent:
    """角色控制代理"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    async def execute_character_control(self, control_type: str, arguments: dict) -> dict:
        """執行角色控制操作"""
        try:
            logger.info(f"🎭 準備執行角色控制: {control_type}")
            
            if control_type == "scale":
                return await self._handle_character_scale(arguments)
            elif control_type == "position":
                return await self._handle_character_position(arguments)  
            elif control_type == "rotation":
                return await self._handle_character_rotation(arguments)
            elif control_type == "animation":
                return await self._handle_character_animation(arguments)
            elif control_type == "outfit":
                return await self._handle_character_outfit(arguments)
            elif control_type == "body_shape":
                return await self._handle_character_body_shape(arguments)
            elif control_type == "visibility":
                return await self._handle_character_visibility(arguments)
            elif control_type == "reset-transform":
                return await self._handle_character_reset_transform(arguments)
            else:
                return {
                    "success": False,
                    "error": f"未知的角色控制類型: {control_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ 角色控制執行失敗: {e}")
            return {
                "success": False,
                "error": f"Character control failed: {str(e)}"
            }
    
    async def _handle_character_scale(self, arguments: dict) -> dict:
        """處理角色縮放控制"""
        try:
            # 驗證必要參數
            scale = arguments.get("scale")
            if scale is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: scale"
                }
            
            # 驗證縮放範圍
            if not isinstance(scale, (int, float)) or not (0.1 <= scale <= 15.0):
                return {
                    "success": False,
                    "error": "scale must be a number between 0.1 and 15.0"
                }
            
            # 構建 API 請求數據
            request_data = {
                "scale": scale
            }
            
            logger.info(f"🎭 準備設置角色縮放: {scale}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/character/scale")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用角色縮放 API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/scale",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                    logger.info(f"📄 HTTP 回應內容: {response_text}")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text) if response_text else {}
                            logger.info(f"✅ 成功控制角色縮放")
                            
                            return {
                                "success": True,
                                "message": f"角色縮放已設置為: {scale}",
                                "result": result,
                                "action": "scale",
                                "scale": scale
                            }
                        except json.JSONDecodeError:
                            logger.info(f"✅ 成功控制角色縮放 (無JSON回應)")
                            return {
                                "success": True,
                                "message": f"角色縮放已設置為: {scale}",
                                "action": "scale",
                                "scale": scale
                            }
                    else:
                        logger.error(f"❌ 角色縮放控制失敗: HTTP {response.status} - {response_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色縮放處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character scale: {str(e)}"
            }
    
    async def _handle_character_position(self, arguments: dict) -> dict:
        """處理角色位置控制"""
        try:
            position = arguments.get("position")
            if position is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: position"
                }
            
            # 驗證位置格式
            if not isinstance(position, list) or len(position) != 3:
                return {
                    "success": False,
                    "error": "position must be a list of 3 numbers [x, y, z]"
                }
            
            request_data = {
                "position": position
            }
            
            logger.info(f"🎭 準備設置角色位置: {position}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/position",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text) if response_text else {}
                        return {
                            "success": True,
                            "message": f"角色位置已設置為: {position}",
                            "result": result,
                            "action": "position",
                            "position": position
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色位置處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character position: {str(e)}"
            }
    
    async def _handle_character_rotation(self, arguments: dict) -> dict:
        """處理角色旋轉控制"""
        try:
            rotation = arguments.get("rotation")
            if rotation is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: rotation"
                }
            
            # 驗證旋轉格式
            if not isinstance(rotation, list) or len(rotation) != 3:
                return {
                    "success": False,
                    "error": "rotation must be a list of 3 numbers [x, y, z] in radians"
                }
            
            request_data = {
                "rotation": rotation
            }
            
            logger.info(f"🎭 準備設置角色旋轉: {rotation}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/rotation",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text) if response_text else {}
                        return {
                            "success": True,
                            "message": f"角色旋轉已設置為: {rotation}",
                            "result": result,
                            "action": "rotation",
                            "rotation": rotation
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色旋轉處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character rotation: {str(e)}"
            }
    
    async def _handle_character_animation(self, arguments: dict) -> dict:
        """處理角色動畫控制"""
        try:
            animation = arguments.get("animation")
            if not animation:
                return {
                    "success": False,
                    "error": "Missing required parameter: animation"
                }
            
            loop = arguments.get("loop", True)
            speed = arguments.get("speed", 1.0)
            
            request_data = {
                "animation": animation,
                "loop": loop,
                "speed": speed
            }
            
            logger.info(f"🎭 準備設置角色動畫: {animation}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/animation",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text) if response_text else {}
                        return {
                            "success": True,
                            "message": f"角色動畫已設置為: {animation}",
                            "result": result,
                            "action": "animation",
                            "animation": animation
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色動畫處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character animation: {str(e)}"
            }
    
    async def _handle_character_outfit(self, arguments: dict) -> dict:
        """處理角色服裝控制"""
        try:
            outfit_morphs = arguments.get("outfit_morphs")
            if not outfit_morphs:
                return {
                    "success": False,
                    "error": "Missing required parameter: outfit_morphs"
                }
            
            request_data = {
                "outfit_morphs": outfit_morphs
            }
            
            logger.info(f"🎭 準備設置角色服裝: {outfit_morphs}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/outfit",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text) if response_text else {}
                        return {
                            "success": True,
                            "message": "角色服裝已更新",
                            "result": result,
                            "action": "outfit",
                            "outfit_morphs": outfit_morphs
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色服裝處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character outfit: {str(e)}"
            }
    
    async def _handle_character_visibility(self, arguments: dict) -> dict:
        """處理角色可見性控制"""
        try:
            visible = arguments.get("visible")
            if visible is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: visible"
                }
            
            request_data = {
                "visible": visible
            }
            
            logger.info(f"🎭 準備設置角色可見性: {visible}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/visibility",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text) if response_text else {}
                        return {
                            "success": True,
                            "message": f"角色可見性已設置為: {'可見' if visible else '隱藏'}",
                            "result": result,
                            "action": "visibility",
                            "visible": visible
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色可見性處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character visibility: {str(e)}"
            }
    
    async def _handle_character_reset_transform(self, arguments: dict) -> dict:
        """處理角色變換重置"""
        try:
            reset_position = arguments.get("reset_position", True)
            reset_rotation = arguments.get("reset_rotation", True)
            reset_scale = arguments.get("reset_scale", True)
            
            request_data = {
                "reset_position": reset_position,
                "reset_rotation": reset_rotation,
                "reset_scale": reset_scale
            }
            
            logger.info(f"🎭 準備重置角色變換")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/reset-transform", 
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        result = json.loads(response_text) if response_text else {}
                        return {
                            "success": True,
                            "message": "角色變換已重置",
                            "result": result,
                            "action": "reset-transform"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色重置處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to reset character transform: {str(e)}"
            }
    
    async def _handle_character_body_shape(self, arguments: dict) -> dict:
        """處理角色胖瘦控制（透過 outfit morph targets）"""
        try:
            # 獲取胖瘦參數
            key_1 = arguments.get("key_1", 0.0)  # 鍵 1
            misplace = arguments.get("misplace", 0.0)  # 錯置
            misplace_001 = arguments.get("misplace_001", 0.0)  # 錯置.001
            
            # 驗證參數範圍 (0.0-1.0)
            for name, value in [("key_1", key_1), ("misplace", misplace), ("misplace_001", misplace_001)]:
                if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                    return {
                        "success": False,
                        "error": f"{name} must be a number between 0.0 and 1.0"
                    }
            
            # 驗證至少一個參數大於等於 0.1
            if key_1 < 0.1 and misplace < 0.1 and misplace_001 < 0.1:
                return {
                    "success": False,
                    "error": "At least one body shape parameter must be >= 0.1 (cannot all be 0)"
                }
            
            # 構建 outfit morph targets
            outfit_morphs = {
                "鍵 1": key_1,
                "錯置": misplace,
                "錯置.001": misplace_001
            }
            
            # 過濾掉 0 值（可選優化）
            outfit_morphs = {k: v for k, v in outfit_morphs.items() if v > 0.0}
            
            request_data = {
                "outfit_morphs": outfit_morphs
            }
            
            logger.info(f"🎭 準備設置角色胖瘦: key_1={key_1}, misplace={misplace}, misplace_001={misplace_001}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/character/outfit")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用角色服裝 API（outfit API 處理 morph targets）
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/outfit",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    
                    logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                    logger.info(f"📄 HTTP 回應內容: {response_text}")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text) if response_text else {}
                            logger.info(f"✅ 成功控制角色胖瘦")
                            
                            # 構建描述性消息
                            shape_desc = []
                            if key_1 > 0:
                                shape_desc.append(f"鍵 1: {key_1:.2f}")
                            if misplace > 0:
                                shape_desc.append(f"錯置: {misplace:.2f}")
                            if misplace_001 > 0:
                                shape_desc.append(f"錯置.001: {misplace_001:.2f}")
                            
                            shape_message = "角色體型已調整: " + ", ".join(shape_desc)
                            
                            return {
                                "success": True,
                                "message": shape_message,
                                "result": result,
                                "action": "body_shape",
                                "body_shape": {
                                    "key_1": key_1,
                                    "misplace": misplace,
                                    "misplace_001": misplace_001
                                }
                            }
                        except json.JSONDecodeError:
                            logger.info(f"✅ 成功控制角色胖瘦 (無JSON回應)")
                            return {
                                "success": True,
                                "message": f"角色體型已調整",
                                "action": "body_shape"
                            }
                    else:
                        logger.error(f"❌ 角色胖瘦控制失敗: HTTP {response.status} - {response_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 角色胖瘦處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character body shape: {str(e)}"
            } 