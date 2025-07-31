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
            elif function_name == "character_control":
                logger.info("🎭 調用 character_control 處理器 (透過 Supervisor)")
                result = await self._try_supervisor_fallback(function_name, arguments)
                logger.info(f"🎭 character_control 處理結果: {result}")
                return result
            elif function_name == "get_memory":
                logger.info("🧠 調用 get_memory 處理器")
                result = await self._handle_get_memory(arguments)
                logger.info(f"🧠 get_memory 處理結果: {result}")
                return result
            elif function_name == "save_memory":
                logger.info("💾 調用 save_memory 處理器")
                result = await self._handle_save_memory(arguments)
                logger.info(f"💾 save_memory 處理結果: {result}")
                return result
            elif function_name == "room_control":
                logger.info("🏠 調用 room_control 處理器")
                result = await self._handle_room_control(arguments)
                logger.info(f"🏠 room_control 處理結果: {result}")
                return result
            elif function_name == "web_search":
                logger.info("🌐 調用 web_search 處理器")
                result = await self._handle_web_search(arguments)
                logger.info(f"🌐 web_search 處理結果: {result}")
                return result
            elif function_name == "environment_config":
                logger.info("💡 調用 environment_config 處理器")
                result = await self._handle_environment_config(arguments)
                logger.info(f"💡 environment_config 處理結果: {result}")
                return result
            elif function_name == "show_images_by_preview":
                logger.info("🖼️ 調用 show_images_by_preview 處理器")
                result = await self._handle_show_images_by_preview(arguments)
                logger.info(f"🖼️ show_images_by_preview 處理結果: {result}")
                return result
            elif function_name == "character_animation_mix":
                logger.info("🎭 調用 character_animation_mix 處理器")
                result = await self._handle_character_animation_mix(arguments)
                logger.info(f"🎭 character_animation_mix 處理結果: {result}")
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
                logger.warning(f"❌ Supervisor 不支援此工具: {function_name}")
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
        return ["character_control"]

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
    
    async def _handle_get_memory(self, arguments: dict) -> dict:
        """處理get_memory工具調用"""
        try:
            # 驗證必要參數
            memory_type = arguments.get("memory_type")
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            include_metadata = arguments.get("include_metadata", True)
            
            if memory_type is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: memory_type"
                }
            
            # 驗證記憶類型
            valid_types = ['conversation', 'persona', 'summary']
            if memory_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid memory_type: {memory_type}. Valid types: {valid_types}"
                }
            
            # 準備請求數據
            request_data = {
                "memory_type": memory_type,
                "limit": limit,
                "include_metadata": include_metadata
            }
            
            # 如果有查詢條件，加入查詢
            if query:
                request_data["query"] = query
            
            logger.info(f"🧠 準備獲取記憶: type={memory_type}, query={query}, limit={limit}")
            
            # 調用記憶API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/memory/get",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 記憶API回應狀態: {response.status}")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text)
                                memories_data = result.get("data", {})
                                memories = memories_data.get("memories", [])
                                
                                logger.info(f"✅ 成功獲取 {len(memories)} 條 {memory_type} 記憶")
                                return {
                                    "success": True,
                                    "message": f"Retrieved {len(memories)} {memory_type} memories",
                                    "memory_type": memory_type,
                                    "memories": memories,
                                    "total_count": len(memories)
                                }
                            except json.JSONDecodeError as e:
                                logger.error(f"❌ 解析記憶API回應失敗: {e}")
                                return {
                                    "success": False,
                                    "error": f"Failed to parse memory response: {str(e)}"
                                }
                        else:
                            logger.error(f"❌ 獲取記憶失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"Memory API error: HTTP {response.status}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 記憶API請求超時")
                return {
                    "success": False,
                    "error": "Memory request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 記憶API請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Memory request failed: {str(http_error)}"
                }
            
        except Exception as e:
            logger.error(f"❌ get_memory 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to get memory: {str(e)}"
            }
    
    def _sanitize_metadata(self, metadata):
        if not isinstance(metadata, dict):
            return metadata
        sanitized = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                sanitized[k] = v
            elif isinstance(v, list):
                sanitized[k] = ",".join(map(str, v))
            else:
                sanitized[k] = str(v)
        return sanitized

    async def _handle_save_memory(self, arguments: Dict[str, Any]) -> dict:
        """處理 save_memory 工具，將重要資訊儲存到記憶系統"""
        try:
            # 自動處理 metadata 型別
            if "metadata" in arguments:
                arguments["metadata"] = self._sanitize_metadata(arguments["metadata"])
            # 驗證必要參數
            memory_type = arguments.get("memory_type")
            content = arguments.get("content")
            metadata = arguments.get("metadata")
            
            if memory_type is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: memory_type"
                }
            
            if content is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: content"
                }
            
            # 驗證記憶類型
            valid_types = ['conversation', 'persona', 'summary']
            if memory_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid memory_type: {memory_type}. Valid types: {valid_types}"
                }
            
            # 準備請求數據
            request_data = {
                "memory_type": memory_type,
                "content": content
            }
            
            # 如果有元數據，加入
            if metadata:
                request_data["metadata"] = metadata
            
            logger.info(f"💾 準備儲存記憶: type={memory_type}, content_length={len(content)}")
            
            # 調用記憶API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/memory/save",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 記憶儲存API回應狀態: {response.status}")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text)
                                logger.info(f"✅ 成功儲存 {memory_type} 記憶")
                                return {
                                    "success": True,
                                    "message": f"Successfully saved {memory_type} memory",
                                    "memory_type": memory_type,
                                    "content_length": len(content)
                                }
                            except json.JSONDecodeError as e:
                                logger.error(f"❌ 解析記憶儲存回應失敗: {e}")
                                return {
                                    "success": False,
                                    "error": f"Failed to parse save response: {str(e)}"
                                }
                        else:
                            logger.error(f"❌ 儲存記憶失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"Memory save error: HTTP {response.status}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 記憶儲存API請求超時")
                return {
                    "success": False,
                    "error": "Memory save timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 記憶儲存API請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Memory save request failed: {str(http_error)}"
                }
            
        except Exception as e:
            logger.error(f"❌ save_memory 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to save memory: {str(e)}"
            } 

    async def _handle_room_control(self, arguments: Dict[str, Any]) -> dict:
        """處理 room_control 工具，切換/隱藏場景"""
        try:
            display_scene = arguments.get("displayScene")
            scene_name = arguments.get("sceneName")
            payload = {"displayScene": display_scene}
            if scene_name:
                payload["sceneName"] = scene_name
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/control/scene-display", json=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"房間場景切換成功: {payload}")
                        return {"success": True, "message": "Room/scene switched successfully"}
                    else:
                        error_text = await resp.text()
                        logger.warning(f"房間場景切換失敗: {error_text}")
                        return {"success": False, "error": error_text}
        except Exception as e:
            logger.error(f"room_control 執行異常: {e}")
            return {"success": False, "error": str(e)} 

    async def _handle_web_search(self, arguments: dict) -> dict:
        """呼叫本地 /api/web-search 進行網頁搜尋"""
        try:
            url = f"{self.base_url}/api/web-search"
            payload = {
                "query": arguments.get("query"),
                "num_results": arguments.get("num_results", 5),
                "language": arguments.get("language", "zh-TW"),
                "safe_search": arguments.get("safe_search", "active")
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "results": data.get("results", []),
                            "total_results": data.get("total_results"),
                            "search_time": data.get("search_time"),
                            "query": data.get("query")
                        }
                    else:
                        err = await resp.text()
                        return {"success": False, "error": f"Web search API error: {err}"}
        except Exception as e:
            logger.error(f"web_search 執行失敗: {e}")
            return {"success": False, "error": str(e)} 

    async def _handle_environment_config(self, arguments: dict) -> dict:
        """批次設定環境光照（僅允許 preset 與 intensity，背景永遠為 false）"""
        try:
            # 僅允許 preset 與 intensity
            payload = {}
            if "preset" in arguments:
                payload["preset"] = arguments["preset"]
            if "intensity" in arguments:
                payload["intensity"] = arguments["intensity"]
            # 不允許 background 參數
            logger.info(f"💡 發送環境光照批次設定: {payload}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/environment/config",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"💡 HTTP 回應狀態: {response.status}")
                    logger.info(f"💡 HTTP 回應內容: {response_text}")
                    if response.status == 200:
                        try:
                            result = json.loads(response_text) if response_text else {}
                            logger.info(f"✅ 成功設定環境光照: {payload}")
                            return {
                                "success": True,
                                "message": "Environment config updated",
                                "result": result
                            }
                        except json.JSONDecodeError:
                            logger.info(f"✅ 成功設定環境光照: {payload} (無JSON回應)")
                            return {
                                "success": True,
                                "message": "Environment config updated"
                            }
                    else:
                        logger.error(f"❌ 設定環境光照失敗: HTTP {response.status} - {response_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
        except aiohttp.ClientTimeout:
            logger.error(f"⏰ HTTP 請求超時 (environment_config)")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"❌ environment_config 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to set environment config: {str(e)}"
            } 

    async def _handle_show_images_by_preview(self, arguments: Dict[str, Any]) -> dict:
        """處理 show_images_by_preview 工具，呼叫本地 API 端點展示圖片"""
        try:
            category = arguments.get("category")
            if not category:
                return {"success": False, "error": "Missing required parameter: category"}
            url = f"{self.base_url}/api/show_images_by_preview"
            params = {"category": category}
            logger.info(f"🔄 發送請求到: {url} 參數: {params}")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    text = await resp.text()
                    logger.info(f"🔄 show_images_by_preview HTTP 狀態: {resp.status}")
                    if resp.status == 200:
                        try:
                            data = json.loads(text) if text else {}
                            return {"success": True, "result": data}
                        except json.JSONDecodeError:
                            return {"success": True, "message": text}
                    else:
                        return {"success": False, "error": f"HTTP {resp.status}: {text}"}
        except Exception as e:
            logger.error(f"show_images_by_preview 處理錯誤: {e}")
            return {"success": False, "error": str(e)} 

    async def _handle_character_animation_mix(self, arguments: dict) -> dict:
        """處理角色動畫混合工具，轉發到 animation-mix 端點"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/character/animation-mix",
                    json=arguments,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as response:
                    response_text = await response.text()
                    if response.status == 200:
                        return {
                            "success": True,
                            "message": "角色動畫混合已設置",
                            "result": json.loads(response_text) if response_text else {},
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
        except Exception as e:
            logger.error(f"❌ character_animation_mix 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"character_animation_mix failed: {str(e)}"
            } 