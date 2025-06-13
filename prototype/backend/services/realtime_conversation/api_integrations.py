"""
API 整合模組
負責與外部服務的整合，包括音效播放、表情動畫、自拍功能等。
"""

import json
import logging
import random
import aiohttp
from typing import Dict, Any

from .utils import get_random_selfie_reference, get_selfies_directory
from ..agent_supervisor import SupervisorManager

logger = logging.getLogger(__name__)


class APIIntegrations:
    """處理各種外部API的整合"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.selfies_dir = get_selfies_directory()
        # 初始化 Supervisor Manager
        self.supervisor = SupervisorManager()
    
    async def execute_tool_function(self, function_name: str, arguments_json: str) -> dict:
        """執行工具函數並返回結果"""
        try:
            # 解析參數
            arguments = json.loads(arguments_json)
            logger.info(f"🔧 執行工具函數: {function_name}")
            logger.info(f"📋 參數內容: {arguments}")
            
            if function_name == "emotion_trajectory":
                logger.info("▶️ 調用 emotion_trajectory 處理器")
                return await self._handle_emotion_trajectory(arguments)
            elif function_name == "play_audio":
                logger.info("🎵 調用 play_audio 處理器")
                result = await self._handle_play_audio(arguments)
                logger.info(f"🎵 play_audio 處理結果: {result}")
                return result
            elif function_name == "take_selfie":
                logger.info("📸 調用 take_selfie 處理器")
                result = await self._handle_take_selfie(arguments)
                logger.info(f"📸 take_selfie 處理結果: {result}")
                return result
            elif function_name == "generate_image":
                logger.info("🎨 調用 generate_image 處理器")
                result = await self._handle_generate_image(arguments)
                logger.info(f"🎨 generate_image 處理結果: {result}")
                return result
            elif function_name == "background_audio":
                logger.info("🎼 調用 background_audio 處理器")
                result = await self._handle_background_audio(arguments)
                logger.info(f"🎼 background_audio 處理結果: {result}")
                return result
            elif function_name == "camera_control":
                logger.info("📹 調用 camera_control 處理器 (透過 Supervisor)")
                result = await self._handle_camera_control_via_supervisor(arguments)
                logger.info(f"📹 camera_control 處理結果: {result}")
                return result
            elif function_name == "head_size_control":
                logger.info("📏 調用 head_size_control 處理器")
                result = await self._handle_head_size_control(arguments)
                logger.info(f"📏 head_size_control 處理結果: {result}")
                return result
            elif function_name == "body_animation":
                logger.info("💃 調用 body_animation 處理器")
                result = await self._handle_body_animation(arguments)
                logger.info(f"💃 body_animation 處理結果: {result}")
                return result
            elif function_name == "character_animation":
                logger.info("🎭 調用 character_animation 處理器")
                result = await self._handle_character_animation(arguments)
                logger.info(f"🎭 character_animation 處理結果: {result}")
                return result
            else:
                # 🎯 智能路由：如果 realtime 無法處理，轉發給 Supervisor
                logger.info(f"🤖 Realtime 無法處理 {function_name}，嘗試轉發給 Supervisor")
                result = await self._try_supervisor_fallback(function_name, arguments)
                if result["success"]:
                    logger.info(f"✅ Supervisor 成功處理: {function_name}")
                    return result
                else:
                    logger.warning(f"❓ 未知工具函數: {function_name}")
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

    async def _try_supervisor_fallback(self, function_name: str, arguments: dict) -> dict:
        """嘗試透過 Supervisor 處理未知或複雜的工具請求"""
        try:
            logger.info(f"🎭 嘗試將 {function_name} 轉發給 Supervisor")
            
            # 檢查 Supervisor 是否支援這個工具
            if function_name in self._get_supervisor_supported_tools():
                # 調用 Supervisor 處理
                result = await self.supervisor.handle_tool_request(
                    tool_name=function_name,
                    arguments=arguments,
                    context=None  # 之後可以加入對話上下文
                )
                return result
            else:
                return {
                    "success": False,
                    "error": f"Tool not supported by Supervisor: {function_name}"
                }
            
        except Exception as e:
            logger.error(f"❌ Supervisor fallback 失敗: {e}")
            return {
                "success": False,
                "error": f"Supervisor fallback failed: {str(e)}"
            }
    
    def _get_supervisor_supported_tools(self) -> list:
        """獲取 Supervisor 支援的工具列表"""
        return [
            "character_scale_control",
            "character_position_control", 
            "character_rotation_control",
            "character_outfit_control",
            "character_body_shape_control",  # 新增：胖瘦控制
            "character_visibility_control",
            "character_reset_transform",
            # 未來可以加入更多複雜工具
        ]

    async def _handle_camera_control_via_supervisor(self, arguments: dict) -> dict:
        """透過 Supervisor 處理攝影機控制"""
        try:
            logger.info("🎭 將攝影機控制請求轉發給 Supervisor")
            
            # 調用 Supervisor 處理攝影機控制
            result = await self.supervisor.handle_tool_request(
                tool_name="camera_control",
                arguments=arguments,
                context=None  # 之後可以加入對話上下文
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Supervisor 攝影機控制失敗: {e}")
            return {
                "success": False,
                "error": f"Supervisor camera control failed: {str(e)}"
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
    
    async def _handle_play_audio(self, arguments: dict) -> dict:
        """處理play_audio工具調用"""
        try:
            # 驗證必要參數
            filename = arguments.get("filename")
            interrupt = arguments.get("interrupt", False)
            
            if filename is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: filename"
                }
            
            # 驗證檔案名稱
            if not isinstance(filename, str):
                return {
                    "success": False,
                    "error": "filename must be a string"
                }
            
            # 構建正確的URL路徑（根據文檔，使用 /songs-file/ 前綴）
            audio_url = f"/songs-file/{filename}"
            
            # 準備請求數據（根據文檔的API格式）
            request_data = {
                "url": audio_url,
                "interrupt": interrupt
            }
            
            logger.info(f"🎵 準備播放音檔: {filename}, URL: {audio_url}, interrupt: {interrupt}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/play-audio")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/control/play-audio API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/control/play-audio",
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
                                logger.info(f"✅ 成功播放音檔: {filename}")
                                return {
                                    "success": True,
                                    "message": f"Playing audio: {filename}",
                                    "result": result
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功播放音檔: {filename} (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Playing audio: {filename}"
                                }
                        else:
                            logger.error(f"❌ 播放音檔失敗 {filename}: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ HTTP 請求超時: {filename}")
                return {
                    "success": False,
                    "error": "Request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 HTTP 請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"HTTP request failed: {str(http_error)}"
                }
            
        except Exception as e:
            logger.error(f"❌ play_audio 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to play audio: {str(e)}"
            }
    
    async def _handle_take_selfie(self, arguments: dict) -> dict:
        """處理take_selfie工具調用"""
        try:
            # 驗證必要參數
            description = arguments.get("description")
            
            if description is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: description"
                }
            
            # 驗證描述格式
            if not isinstance(description, str) or len(description.strip()) == 0:
                return {
                    "success": False,
                    "error": "description must be a non-empty string"
                }
            
            # 設定預設參數 - 如果沒有指定參考圖片，就隨機選擇一張
            reference_image = arguments.get("reference_image")
            if not reference_image:
                reference_image = get_random_selfie_reference(self.selfies_dir)
            
            modification = arguments.get("modification", "")
            # 預設使用非中央位置，隨機選擇左右
            default_positions = ["center-right", "center-left"]
            position = arguments.get("position", random.choice(default_positions))
            size = arguments.get("size", "large")
            duration = arguments.get("duration", 15.0)
            aspect_ratio = arguments.get("aspect_ratio", "portrait")
            
            # 構建API請求數據（根據文檔的/api/take-selfie格式）
            request_data = {
                "description": description,
                "reference_image": reference_image,
                "position": position,
                "size": size,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "add_timestamp": True  # 自動添加時間戳章
            }
            
            # 如果有修改指令，加入到請求中
            if modification:
                request_data["modification"] = modification
            
            logger.info(f"📸 準備拍攝自拍: {description}")
            logger.info(f"🖼️ 使用參考圖片: {reference_image}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/take-selfie")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/take-selfie API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/take-selfie",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=15)  # 圖片生成需要較長時間
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                        logger.info(f"📄 HTTP 回應內容: {response_text}")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text) if response_text else {}
                                selfie_url = result.get("url", "")
                                caption = result.get("caption", "")
                                logger.info(f"✅ 成功拍攝自拍: {selfie_url}")
                                return {
                                    "success": True,
                                    "message": f"Selfie taken successfully: {caption}",
                                    "result": result,
                                    "url": selfie_url,
                                    "caption": caption
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功拍攝自拍 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Selfie taken successfully"
                                }
                        else:
                            logger.error(f"❌ 拍攝自拍失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 自拍請求超時")
                return {
                    "success": False,
                    "error": "Selfie request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 自拍HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Selfie HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ take_selfie 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to take selfie: {str(e)}"
            }
    
    async def _handle_generate_image(self, arguments: dict) -> dict:
        """處理generate_image工具調用"""
        try:
            # 驗證必要參數
            description = arguments.get("description")
            
            if description is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: description"
                }
            
            # 驗證描述格式
            if not isinstance(description, str) or len(description.strip()) == 0:
                return {
                    "success": False,
                    "error": "description must be a non-empty string"
                }
            
            # 設定預設參數，避免中央位置
            default_positions = ["center-right", "center-left", "top-right", "top-left"]
            position = arguments.get("position", random.choice(default_positions))
            size = arguments.get("size", "large")
            duration = arguments.get("duration", 10.0)
            aspect_ratio = arguments.get("aspect_ratio", "square")
            
            # 構建API請求數據（根據文檔的/api/generate-image格式）
            request_data = {
                "description": description,
                "position": position,
                "size": size,
                "duration": duration,
                "aspect_ratio": aspect_ratio
            }
            
            logger.info(f"🎨 準備生成圖片: {description}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/generate-image")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/generate-image API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/generate-image",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=30)  # 圖片生成需要較長時間
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                        logger.info(f"📄 HTTP 回應內容: {response_text}")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text) if response_text else {}
                                image_url = result.get("url", "")
                                caption = result.get("caption", "")
                                logger.info(f"✅ 成功生成圖片: {image_url}")
                                return {
                                    "success": True,
                                    "message": f"Image generated successfully: {caption}",
                                    "result": result,
                                    "url": image_url,
                                    "caption": caption
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功生成圖片 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Image generated successfully"
                                }
                        else:
                            logger.error(f"❌ 圖片生成失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 圖片生成請求超時")
                return {
                    "success": False,
                    "error": "Image generation request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 圖片生成HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Image generation HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ generate_image 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to generate image: {str(e)}"
            }
    
    async def _handle_background_audio(self, arguments: dict) -> dict:
        """處理background_audio工具調用"""
        try:
            # 獲取參數
            bgm_url = arguments.get("bgmUrl")
            sfx_url = arguments.get("sfxUrl")
            bgm_playing = arguments.get("bgmPlaying")
            
            # 至少需要一個參數
            if bgm_url is None and sfx_url is None and bgm_playing is None:
                return {
                    "success": False,
                    "error": "At least one parameter (bgmUrl, sfxUrl, or bgmPlaying) is required"
                }
            
            # 構建API請求數據（根據文檔的/api/control/background-audio格式）
            request_data = {}
            
            if bgm_url is not None:
                request_data["bgmUrl"] = bgm_url
            
            if sfx_url is not None:
                request_data["sfxUrl"] = sfx_url
                
            if bgm_playing is not None:
                request_data["bgmPlaying"] = bgm_playing
            
            logger.info(f"🎼 準備控制背景音頻")
            if bgm_url is not None:
                logger.info(f"🎵 BGM: {bgm_url}")
            if sfx_url is not None:
                logger.info(f"🔊 SFX: {sfx_url}")
            if bgm_playing is not None:
                logger.info(f"⏯️ BGM狀態: {'播放' if bgm_playing else '暫停'}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/background-audio")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/control/background-audio API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/control/background-audio",
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
                                logger.info(f"✅ 成功控制背景音頻")
                                
                                # 構建成功消息
                                message_parts = []
                                if bgm_url is not None:
                                    if bgm_url == "":
                                        message_parts.append("BGM已停止")
                                    else:
                                        message_parts.append(f"BGM已設置: {bgm_url}")
                                if sfx_url is not None:
                                    message_parts.append(f"音效已播放: {sfx_url}")
                                if bgm_playing is not None:
                                    message_parts.append(f"BGM{'已播放' if bgm_playing else '已暫停'}")
                                
                                success_message = ", ".join(message_parts)
                                
                                return {
                                    "success": True,
                                    "message": success_message,
                                    "result": result
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功控制背景音頻 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": "Background audio controlled successfully"
                                }
                        else:
                            logger.error(f"❌ 背景音頻控制失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 背景音頻請求超時")
                return {
                    "success": False,
                    "error": "Background audio request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 背景音頻HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Background audio HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ background_audio 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control background audio: {str(e)}"
            }

    
    async def _handle_head_size_control(self, arguments: dict) -> dict:
        """處理head_size_control工具調用"""
        try:
            # 驗證必要參數
            scale_factor = arguments.get("scaleFactor")
            
            if scale_factor is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: scaleFactor"
                }
            
            # 驗證scaleFactor格式和範圍（1.0 到 20.0）
            if not isinstance(scale_factor, (int, float)) or scale_factor < 1.0 or scale_factor > 20.0:
                return {
                    "success": False,
                    "error": "scaleFactor must be a number between 1.0 and 20.0"
                }
            
            # 構建API請求數據（根據文檔的/api/control/head-size格式）
            request_data = {
                "scaleFactor": scale_factor
            }
            
            logger.info(f"📏 準備控制頭部大小: {scale_factor}")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/head-size")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/control/head-size API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/control/head-size",
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
                                logger.info(f"✅ 成功控制頭部大小: {scale_factor}")
                                
                                return {
                                    "success": True,
                                    "message": f"Head size controlled successfully: {scale_factor}x",
                                    "scaleFactor": scale_factor,
                                    "result": result
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功控制頭部大小 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Head size controlled successfully: {scale_factor}x",
                                    "scaleFactor": scale_factor
                                }
                        else:
                            logger.error(f"❌ 頭部大小控制失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 頭部大小請求超時")
                return {
                    "success": False,
                    "error": "Head size request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 頭部大小HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Head size HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ head_size_control 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control head size: {str(e)}"
            }
    
    async def _handle_body_animation(self, arguments: dict) -> dict:
        """處理body_animation工具調用"""
        try:
            # 獲取參數
            state = arguments.get("state", "play")
            animation = arguments.get("animation")
            sequence = arguments.get("sequence")
            loop = arguments.get("loop", True)
            loop_count = arguments.get("loopCount")
            speed = arguments.get("speed", 1.0)
            transition_duration = arguments.get("transitionDuration", 0.5)
            
            # 驗證參數
            if state not in ["play", "pause", "resume", "stop"]:
                return {
                    "success": False,
                    "error": "state must be one of: play, pause, resume, stop"
                }
            
            # 如果是play狀態，需要提供animation或sequence
            if state == "play":
                if not animation and not sequence:
                    return {
                        "success": False,
                        "error": "animation or sequence is required when state is 'play'"
                    }
                
                if animation and sequence:
                    return {
                        "success": False,
                        "error": "Cannot specify both animation and sequence, choose one"
                    }
            
            # 驗證speed範圍
            if not isinstance(speed, (int, float)) or speed < 0.5 or speed > 3.0:
                return {
                    "success": False,
                    "error": "speed must be a number between 0.5 and 3.0"
                }
            
            # 驗證transition_duration範圍
            if not isinstance(transition_duration, (int, float)) or transition_duration < 0.1 or transition_duration > 2.0:
                return {
                    "success": False,
                    "error": "transitionDuration must be a number between 0.1 and 2.0"
                }
            
            # 構建API請求數據（根據文檔的body-animation格式）
            request_data = {
                "state": state,
                "speed": speed,
                "transitionDuration": transition_duration
            }
            
            # 添加可選參數
            if animation:
                request_data["animation"] = animation
            if sequence:
                request_data["sequence"] = sequence
            if loop is not None:
                request_data["loop"] = loop
            if loop_count is not None:
                request_data["loopCount"] = loop_count
            
            logger.info(f"💃 準備控制身體動畫: {state}")
            if animation:
                logger.info(f"🎭 動畫名稱: {animation}")
            if sequence:
                logger.info(f"🎬 動畫序列: {len(sequence)} 個動畫")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/body-animation")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/control/body-animation API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/control/body-animation",
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
                                logger.info(f"✅ 成功控制身體動畫")
                                
                                # 構建成功消息
                                if state == "play":
                                    if animation:
                                        success_message = f"正在播放動畫: {animation}"
                                        if loop:
                                            if loop_count:
                                                success_message += f"，循環 {loop_count} 次"
                                            else:
                                                success_message += "，無限循環"
                                        if speed != 1.0:
                                            success_message += f"，速度: {speed}x"
                                    elif sequence:
                                        success_message = f"正在播放動畫序列，包含 {len(sequence)} 個動畫"
                                        if speed != 1.0:
                                            success_message += f"，速度: {speed}x"
                                elif state == "pause":
                                    success_message = "動畫已暫停"
                                elif state == "resume":
                                    success_message = "動畫已恢復播放"
                                elif state == "stop":
                                    success_message = "動畫已停止"
                                
                                return {
                                    "success": True,
                                    "message": success_message,
                                    "result": result,
                                    "state": state,
                                    "animation": animation if animation else None,
                                    "sequence_length": len(sequence) if sequence else None
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功控制身體動畫 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Body animation {state} executed successfully",
                                    "state": state
                                }
                        else:
                            logger.error(f"❌ 身體動畫控制失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 身體動畫控制請求超時")
                return {
                    "success": False,
                    "error": "Body animation control request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 身體動畫控制HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Body animation control HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ body_animation 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control body animation: {str(e)}"
            }
    
    async def _handle_character_animation(self, arguments: dict) -> dict:
        """處理character_animation工具調用"""
        try:
            # 獲取參數
            animation = arguments.get("animation")
            loop = arguments.get("loop", True)
            speed = arguments.get("speed", 1.0)
            
            # 驗證必要參數
            if not animation:
                return {
                    "success": False,
                    "error": "animation parameter is required"
                }
            
            # 驗證動畫名稱
            valid_animations = [
                "運動1", "運動2", "漂浮", "漂浮2", "Tpose", 
                "不穩", "划手機", "臥躺", 
                "舞步1", "舞步2", "舞步3", 
                "飛1", "飛2"
            ]
            
            if animation not in valid_animations:
                return {
                    "success": False,
                    "error": f"Invalid animation name: {animation}. Valid options: {', '.join(valid_animations)}"
                }
            
            # 驗證speed範圍
            if not isinstance(speed, (int, float)) or speed < 0.5 or speed > 3.0:
                return {
                    "success": False,
                    "error": "speed must be a number between 0.5 and 3.0"
                }
            
            # 構建API請求數據
            request_data = {
                "animation": animation,
                "loop": loop,
                "speed": speed
            }
            
            logger.info(f"🎭 準備播放角色動畫: {animation}")
            logger.info(f"🔄 循環播放: {loop}, 速度: {speed}x")
            logger.info(f"🌐 發送請求到: {self.base_url}/api/control/character/animation")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用角色動畫控制 API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/control/character/animation",
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
                                logger.info(f"✅ 成功播放角色動畫: {animation}")
                                
                                # 構建成功消息
                                success_message = f"正在播放角色動畫: {animation}"
                                if loop:
                                    success_message += "，循環播放"
                                if speed != 1.0:
                                    success_message += f"，速度: {speed}x"
                                
                                return {
                                    "success": True,
                                    "message": success_message,
                                    "result": result,
                                    "animation": animation,
                                    "loop": loop,
                                    "speed": speed
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功播放角色動畫 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Character animation '{animation}' started successfully",
                                    "animation": animation,
                                    "loop": loop,
                                    "speed": speed
                                }
                        else:
                            logger.error(f"❌ 角色動畫控制失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 角色動畫控制請求超時")
                return {
                    "success": False,
                    "error": "Character animation control request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 角色動畫控制HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Character animation control HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ character_animation 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to control character animation: {str(e)}"
            } 