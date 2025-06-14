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
import re

logger = logging.getLogger(__name__)


class CharacterControlAgent:
    """角色控制代理"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    async def execute_character_control(self, control_type: str, arguments: dict) -> dict:
        """執行角色控制操作"""
        try:
            logger.info(f"🎭 準備執行角色控制: {control_type}")
            
            if control_type == "character_control":
                return await self._handle_character_control_unified(arguments)
            elif control_type == "scale":
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
    
    async def _handle_character_control_unified(self, arguments: dict) -> dict:
        """處理簡化的角色控制請求（統一入口）"""
        try:
            request = arguments.get("request", "")
            
            if not request:
                return {
                    "success": False,
                    "error": "Missing required parameter: request"
                }
            
            logger.info(f"🎭 處理角色控制請求: {request}")
            
            # 智能解析請求類型和參數
            control_info = self._parse_character_request(request)
            
            if not control_info:
                return {
                    "success": False,
                    "error": f"Unable to understand character control request: {request}"
                }
            
            control_type = control_info["type"]
            control_args = control_info["args"]
            
            logger.info(f"🎯 解析結果: {control_type}, 參數: {control_args}")
            
            # 調用對應的處理方法
            if control_type == "scale":
                return await self._handle_character_scale(control_args)
            elif control_type == "animation":
                return await self._handle_character_animation(control_args)
            elif control_type == "body_shape":
                return await self._handle_character_body_shape(control_args)
            elif control_type == "position":
                return await self._handle_character_position(control_args)
            elif control_type == "rotation":
                return await self._handle_character_rotation(control_args)
            elif control_type == "visibility":
                return await self._handle_character_visibility(control_args)
            elif control_type == "reset-transform":
                return await self._handle_character_reset_transform(control_args)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported character control type: {control_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ 處理統一角色控制時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"Unified character control failed: {str(e)}"
            }
    
    def _parse_character_request(self, request: str) -> dict:
        """解析角色控制請求"""
        request_lower = request.lower()
        
        # 優先處理包含數字的縮放請求（如"10倍"、"15倍"）
        if re.search(r'\d+(?:\.\d+)?倍', request_lower):
            return self._parse_scale_request(request_lower)
        
        # 檢查縮放相關關鍵詞
        scale_keywords = ["縮放", "大小", "變大", "變小", "放大", "縮小", "巨大", "微小", "身體放大", "身體調整", "身體壯"]
        for keyword in scale_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 縮放關鍵詞匹配: '{keyword}' -> scale")
                return self._parse_scale_request(request_lower)
        
        # 檢查動畫相關關鍵詞
        animation_keywords = ["動畫", "表演", "跳舞", "舞蹈", "漂浮", "飛", "運動", "划手機", "滑手機", "臥躺", "躺下", "躺", "不穩", "舞步"]
        for keyword in animation_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 動畫關鍵詞匹配: '{keyword}' -> animation")
                return self._parse_animation_request(request_lower)
        
        # 檢查體型相關關鍵詞
        body_shape_keywords = ["胖瘦", "胖", "瘦", "體型", "身材", "胖一點", "瘦一點", "變胖", "變瘦"]
        for keyword in body_shape_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 體型關鍵詞匹配: '{keyword}' -> body_shape")
                return self._parse_body_shape_request(request_lower)
        
        # 檢查位置相關關鍵詞
        position_keywords = ["位置", "移動", "移到"]
        for keyword in position_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 位置關鍵詞匹配: '{keyword}' -> position")
                return {"type": "position", "args": {"position": [0, 0, 0]}}
        
        # 檢查旋轉相關關鍵詞
        rotation_keywords = ["旋轉", "轉", "轉向"]
        for keyword in rotation_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 旋轉關鍵詞匹配: '{keyword}' -> rotation")
                return {"type": "rotation", "args": {"rotation": [0, 90, 0]}}
        
        # 檢查可見性相關關鍵詞
        visibility_keywords = ["顯示", "隱藏", "看見", "消失"]
        for keyword in visibility_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 可見性關鍵詞匹配: '{keyword}' -> visibility")
                return self._parse_visibility_request(request_lower)
        
        # 檢查重置相關關鍵詞
        reset_keywords = ["重置", "復原", "恢復"]
        for keyword in reset_keywords:
            if keyword in request_lower:
                logger.info(f"🎯 重置關鍵詞匹配: '{keyword}' -> reset-transform")
                return {"type": "reset-transform", "args": {}}
        
        logger.warning(f"⚠️ 無法解析角色控制請求: {request}")
        return None
    
    def _parse_scale_request(self, request: str) -> dict:
        """解析縮放請求"""
        # 首先嘗試提取具體數字
        scale_match = re.search(r'(\d+(?:\.\d+)?)倍', request)
        if scale_match:
            scale = float(scale_match.group(1))
            # 限制在合理範圍內
            scale = max(0.1, min(15.0, scale))
            return {
                "type": "scale",
                "args": {"scale": scale}
            }
        
        # 如果沒有找到具體數字，則根據關鍵詞判斷
        if "大" in request or "放大" in request or "巨大" in request:
            scale = 3.0  # 變大
        elif "小" in request or "縮小" in request or "微小" in request:
            scale = 0.5  # 變小
        else:
            scale = 1.5  # 默認稍微放大
            
        return {
            "type": "scale",
            "args": {"scale": scale}
        }
    
    def _parse_animation_request(self, request: str) -> dict:
        """解析動畫請求"""
        # 動畫名稱映射，增加更多關鍵詞匹配
        animation_mapping = {
            "跳舞": "舞步1", "舞蹈": "舞步1", "身體動作": "舞步1", "動作": "舞步1", 
            "舞步": "舞步1", "舞步1": "舞步1", "舞步2": "舞步2", "舞步3": "舞步3",
            "漂浮": "漂浮", "漂浮2": "漂浮2", "飛": "飛1", "飛1": "飛1", "飛2": "飛2",
            "運動": "運動1", "運動1": "運動1", "運動2": "運動2",
            "划手機": "划手機", "滑手機": "划手機", "臥躺": "臥躺", "躺下": "臥躺", "躺": "臥躺", "不穩": "不穩"
        }
        
        # 查找匹配的動畫
        for keyword, animation in animation_mapping.items():
            if keyword in request:
                logger.info(f"🎯 動畫匹配: '{keyword}' -> {animation}")
                return {
                    "type": "animation",
                    "args": {"animation": animation, "loop": True, "speed": 1.0}
                }
        
        # 默認動畫（當包含跳舞相關但沒有具體匹配時）
        logger.info(f"🎯 使用默認動畫: 舞步1")
        return {
            "type": "animation", 
            "args": {"animation": "舞步1", "loop": True, "speed": 1.0}
        }
    
    def _parse_body_shape_request(self, request: str) -> dict:
        """解析體型請求"""
        if "胖" in request:
            # 變胖
            return {
                "type": "body_shape",
                "args": {"key_1": 0.8, "misplace": 0.8, "misplace_001": 0.8}
            }
        elif "瘦" in request:
            # 變瘦
            return {
                "type": "body_shape", 
                "args": {"key_1": 0.2, "misplace": 0.2, "misplace_001": 0.2}
            }
        else:
            # 默認正常
            return {
                "type": "body_shape",
                "args": {"key_1": 0.5, "misplace": 0.5, "misplace_001": 0.5}
            }
    
    def _parse_visibility_request(self, request: str) -> dict:
        """解析可見性請求"""
        if "隱藏" in request or "消失" in request:
            visible = False
        else:
            visible = True
            
        return {
            "type": "visibility",
            "args": {"visible": visible}
        } 