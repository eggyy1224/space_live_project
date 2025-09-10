"""
API 整合模組
負責與外部服務的整合，包括音效播放、表情動畫、自拍功能等。
"""

import json
import logging
import random
import asyncio
import aiohttp
from typing import Dict, Any

from .utils import get_random_selfie_reference, get_selfies_directory
from ..agent_supervisor import SupervisorManager
from services.perception import YouTubeChatMonitorService, VisionAnalysisService

logger = logging.getLogger(__name__)


class APIIntegrations:
    """處理各種外部API的整合"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.selfies_dir = get_selfies_directory()
        # 初始化 Supervisor Manager
        self.supervisor = SupervisorManager()
        # 初始化 YouTube 聊天室監控服務
        self.youtube_chat_service = YouTubeChatMonitorService()
        # 初始化視覺分析服務
        self.vision_service = VisionAnalysisService()
    
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
            elif function_name == "speak_message":
                logger.info("🗣️ 調用 speak_message 處理器")
                result = await self._handle_speak_message(arguments)
                logger.info(f"🗣️ speak_message 處理結果: {result}")
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
            elif function_name == "analyze_exhibition_field":
                logger.info("🔍 調用 analyze_exhibition_field 處理器")
                result = await self.analyze_exhibition_field(arguments.get("analysis_focus", "exhibition"))
                logger.info(f"🔍 analyze_exhibition_field 處理結果: {result}")
                return result
            elif function_name == "analyze_obs_scene":
                logger.info("📺 調用 analyze_obs_scene 處理器")
                result = await self.analyze_obs_scene(arguments)
                logger.info(f"📺 analyze_obs_scene 處理結果: {result}")
                return result
            elif function_name == "get_youtube_chat_messages":
                logger.info("💬 調用 get_youtube_chat_messages 處理器")
                result = await self._handle_get_youtube_chat_messages(arguments)
                logger.info(f"💬 get_youtube_chat_messages 處理結果: {result}")
                return result
            elif function_name == "generate_background_image":
                logger.info("🖼️ 調用 generate_background_image 處理器")
                result = await self._handle_generate_background_image(arguments)
                logger.info(f"🖼️ generate_background_image 處理結果: {result}")
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

    async def _handle_speak_message(self, arguments: dict) -> dict:
        """處理 speak_message 工具調用，讓虛擬角色說出指定台詞。

        會呼叫本地 /api/control/send-message，伺服器端自動進行 TTS 並廣播到前端。
        """
        try:
            content = arguments.get("content")
            message_type = arguments.get("message_type", "chat-message")
            tts_instruction = arguments.get("tts_instruction")
            tts_voice = arguments.get("tts_voice")
            tts_speed = arguments.get("tts_speed")

            if content is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: content"
                }

            payload = {
                "content": content,
                "message_type": message_type,
            }
            # 透傳可選的 TTS 參數（僅在提供時加入 payload）
            if tts_instruction:
                payload["tts_instruction"] = tts_instruction
            if tts_voice:
                payload["tts_voice"] = tts_voice
            if tts_speed is not None:
                payload["tts_speed"] = tts_speed

            logger.info(
                f"🗣️ 讓角色說話，type={message_type}, content_len={len(content)}, "
                f"tts_instruction={'set' if bool(tts_instruction) else 'none'}, "
                f"tts_voice={tts_voice if tts_voice else 'default'}, "
                f"tts_speed={tts_speed if tts_speed is not None else 'default'}"
            )
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/control/send-message",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as response:
                    response_text = await response.text()

                    if response.status == 200:
                        try:
                            result = json.loads(response_text) if response_text else {}
                        except json.JSONDecodeError:
                            result = {}
                        return {
                            "success": True,
                            "message": "Message sent to avatar",
                            "result": result
                        }
                    else:
                        logger.error(f"❌ 調用 send-message 失敗: HTTP {response.status} - {response_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
        except aiohttp.ClientTimeout:
            logger.error("⏰ speak_message 請求超時")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ speak_message 處理錯誤: {e}")
            return {"success": False, "error": f"Failed to send message: {str(e)}"}

    async def analyze_exhibition_field(self, analysis_focus: str = "exhibition") -> dict:
        """
        展場視覺分析工具
        截圖展場視訊源並進行智能分析，了解展場即時狀況。
        注意：不再將截圖顯示到前端或設為背景，僅回傳分析結果。
        
        Args:
            analysis_focus: 分析重點類型
            
        Returns:
            dict: 包含截圖和分析結果
        """
        try:
            logger.info(f"🔍 開始展場視覺分析 (focus: {analysis_focus})")
            
            # 1) 只截圖，不顯示到前端
            async with aiohttp.ClientSession() as session:
                screenshot_payload = {
                    "source_name": "展場視訊源",
                    "width": 1280,
                    "height": 720,
                    "image_format": "png"
                }
                async with session.post(
                    "http://localhost:8000/api/perception/obs/screenshot",
                    json=screenshot_payload,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        error_msg = f"展場截圖失敗: HTTP {response.status} - {response_text}"
                        logger.error(error_msg)
                        return {"success": False, "error": error_msg}

                    screenshot_result = await response.json()

            # 2) 進行 AI 圖像分析
            screenshot_path = screenshot_result.get("file_path")
            analysis_result = await self.vision_service.analyze_image(
                image_path=screenshot_path,
                analysis_type="exhibition"
            )

            if analysis_result.get("success", False):
                logger.info(f"✅ 展場分析完成: {screenshot_result.get('filename', 'unknown')}")
                return {
                    "success": True,
                    "screenshot_filename": screenshot_result.get("filename"),
                    "screenshot_path": screenshot_path,
                    "timestamp": screenshot_result.get("timestamp"),
                    "analysis_description": analysis_result.get("description", "分析失敗"),
                    "full_result": {
                        "screenshot": screenshot_result,
                        "analysis": analysis_result
                    }
                }
            else:
                error_msg = analysis_result.get("error", "分析失敗")
                logger.error(f"AI 分析失敗: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "screenshot_filename": screenshot_result.get("filename"),
                    "screenshot_path": screenshot_path
                }
                        
        except Exception as e:
            logger.error(f"❌ analyze_exhibition_field 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"展場分析失敗: {str(e)}"
            }
    
    async def analyze_obs_scene(self, arguments: Dict[str, Any]) -> dict:
        """
        OBS 場景智能分析工具
        可以截圖任意 OBS 來源並進行智能分析，支援多來源對比分析
        
        Args:
            arguments: 包含分析參數的字典
                - source_name: OBS 來源名稱（如「主螢幕」、「瀏覽器」等）
                - analysis_focus: 分析重點
                - compare_sources: 是否進行多來源對比分析
                
        Returns:
            dict: 包含截圖和分析結果
        """
        try:
            source_name = arguments.get("source_name", "主螢幕")
            analysis_focus = arguments.get("analysis_focus", "general")
            compare_sources = arguments.get("compare_sources", False)
            
            logger.info(f"📺 開始 OBS 場景分析 (來源: {source_name}, focus: {analysis_focus})")
            
            if compare_sources:
                # 多來源對比分析
                return await self._perform_multi_source_analysis(source_name, analysis_focus)
            else:
                # 單一來源分析
                return await self._perform_single_source_analysis(source_name, analysis_focus)
                
        except Exception as e:
            logger.error(f"❌ analyze_obs_scene 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"OBS 場景分析失敗: {str(e)}"
            }
    
    async def _perform_single_source_analysis(self, source_name: str, analysis_focus: str) -> dict:
        """執行單一 OBS 來源分析"""
        try:
            # 呼叫 OBS 截圖 API
            async with aiohttp.ClientSession() as session:
                screenshot_payload = {
                    "source_name": source_name,
                    "width": 1280,
                    "height": 720,
                    "image_format": "png"
                }
                
                # 先截圖
                async with session.post(
                    "http://localhost:8000/api/perception/obs/screenshot",
                    json=screenshot_payload,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OBS 截圖失敗: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"截圖失敗: HTTP {response.status}"
                        }
                    
                    screenshot_result = await response.json()
                    screenshot_path = screenshot_result.get("file_path")
                    
                    if not screenshot_path:
                        return {
                            "success": False,
                            "error": "截圖成功但無法獲得檔案路徑"
                        }
                
                # 進行 AI 視覺分析
                analysis_type = self._get_analysis_type_for_source(source_name)
                analysis_result = await self.vision_service.analyze_image(
                    image_path=screenshot_path,
                    analysis_type=analysis_type
                )
                
                if analysis_result.get("success", False):
                    logger.info(f"✅ {source_name} 分析完成")
                    
                    # 顯示截圖到前端（僅針對一般 OBS 場景分析；展場專用路徑已於 analyze_exhibition_field 中關閉顯示）
                    display_status = await self._display_screenshot_to_frontend(
                        screenshot_result.get("filename"),
                        source_name,
                        analysis_focus
                    )
                    
                    return {
                        "success": True,
                        "source_name": source_name,
                        "screenshot_path": screenshot_path,
                        "analysis_description": analysis_result.get("description", "分析失敗"),
                        "analysis_type": analysis_type,
                        "timestamp": screenshot_result.get("timestamp"),
                        "display_status": display_status,
                        "full_analysis": analysis_result
                    }
                else:
                    logger.error(f"AI 分析失敗: {analysis_result.get('error', '未知錯誤')}")
                    return {
                        "success": False,
                        "error": f"AI 分析失敗: {analysis_result.get('error', '未知錯誤')}",
                        "screenshot_path": screenshot_path  # 至少還有截圖
                    }
                        
        except Exception as e:
            logger.error(f"❌ 單一來源分析錯誤: {e}")
            return {
                "success": False,
                "error": f"分析過程發生錯誤: {str(e)}"
            }
    
    async def _perform_multi_source_analysis(self, primary_source: str, analysis_focus: str) -> dict:
        """執行多來源對比分析"""
        try:
            # 定義要對比的來源組合
            sources_to_compare = [primary_source]
            
            # 根據主要來源決定對比來源
            if primary_source == "主螢幕":
                sources_to_compare.append("展場視訊源")
            elif primary_source == "展場視訊源":
                sources_to_compare.append("主螢幕")
            else:
                # 其他來源與主螢幕對比
                sources_to_compare.append("主螢幕")
            
            logger.info(f"🔄 開始多來源對比分析: {sources_to_compare}")
            
            # 並行截圖和分析所有來源
            analysis_tasks = []
            for source in sources_to_compare:
                task = self._perform_single_source_analysis(source, analysis_focus)
                analysis_tasks.append(task)
            
            # 等待所有分析完成
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # 整理結果
            successful_results = []
            errors = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    errors.append(f"{sources_to_compare[i]}: {str(result)}")
                elif result.get("success", False):
                    successful_results.append(result)
                else:
                    errors.append(f"{sources_to_compare[i]}: {result.get('error', '未知錯誤')}")
            
            if not successful_results:
                return {
                    "success": False,
                    "error": "所有來源分析都失敗了",
                    "errors": errors
                }
            
            # 生成對比分析報告
            comparison_report = self._generate_comparison_report(successful_results)

            # 顯示所有截圖到前端（如果有 display_status 說明已經顯示過了）
            display_statuses = []
            for result in successful_results:
                if "display_status" not in result:
                    # 如果還沒顯示，現在顯示
                    filename = result.get("screenshot_path", "").split("/")[-1] if result.get("screenshot_path") else None
                    if filename:
                        display_status = await self._display_screenshot_to_frontend(
                            filename,
                            result.get("source_name", ""),
                            analysis_focus
                        )
                        display_statuses.append(f"{result.get('source_name')}: {display_status}")
                else:
                    display_statuses.append(f"{result.get('source_name')}: {result['display_status']}")
            
            return {
                "success": True,
                "analysis_type": "multi_source_comparison",
                "primary_source": primary_source,
                "sources_analyzed": [r["source_name"] for r in successful_results],
                "individual_results": successful_results,
                "comparison_report": comparison_report,
                "display_statuses": display_statuses,
                "errors": errors if errors else None
            }
            
        except Exception as e:
            logger.error(f"❌ 多來源分析錯誤: {e}")
            return {
                "success": False,
                "error": f"多來源分析失敗: {str(e)}"
            }
    
    def _get_analysis_type_for_source(self, source_name: str) -> str:
        """根據來源名稱決定分析類型"""
        source_analysis_map = {
            "主螢幕": "screen_output",
            "展場視訊源": "exhibition_field", 
            "瀏覽器": "web_content",
            "攝像頭": "camera_feed",
            "桌面": "desktop_capture"
        }
        return source_analysis_map.get(source_name, "general")
    
    def _generate_comparison_report(self, results: list) -> str:
        """生成多來源對比分析報告"""
        if len(results) < 2:
            return "無法進行對比分析，需要至少兩個成功的來源分析結果。"
        
        report_parts = []
        report_parts.append("🔍 **多來源對比分析報告**")
        report_parts.append("")
        
        # 列出各來源的分析摘要
        for result in results:
            source_name = result.get("source_name", "未知來源")
            analysis = result.get("analysis_description", "無分析結果")
            report_parts.append(f"**{source_name}**: {analysis[:200]}...")
            report_parts.append("")
        
        # 生成對比總結
        report_parts.append("🔄 **對比觀察**:")
        report_parts.append("- 可以根據不同來源的內容差異，了解展場內外的互動狀況")
        report_parts.append("- 主螢幕反映對外播出內容，展場視訊源反映現場實況")
        report_parts.append("- 建議結合兩個視角進行更全面的情況判斷")
        
        return "\n".join(report_parts)
    
    async def _display_screenshot_to_frontend(self, filename: str, source_name: str, analysis_focus: str) -> str:
        """顯示截圖到前端"""
        try:
            # 根據來源類型決定顯示配置
            caption = self._get_display_caption(source_name, analysis_focus)
            position = self._get_display_position(source_name)
            
            show_image_payload = {
                "filename": filename,
                "caption": caption,
                "position": position,
                "size": "large",
                "duration": 25.0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/show-existing-image",
                    json=show_image_payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ {source_name} 截圖已顯示到前端")
                        return f"✅ {source_name} 截圖已顯示到前端"
                    else:
                        error_text = await response.text()
                        logger.warning(f"❌ 顯示截圖失敗: {response.status} - {error_text}")
                        return f"❌ 顯示截圖失敗: HTTP {response.status}"
                        
        except Exception as e:
            logger.error(f"❌ 顯示截圖到前端失敗: {e}")
            return f"❌ 顯示截圖失敗: {str(e)}"
    
    def _get_display_caption(self, source_name: str, analysis_focus: str) -> str:
        """根據來源和分析重點生成顯示標題"""
        caption_map = {
            "主螢幕": "🖥️ OBS 主螢幕輸出截圖",
            "展場視訊源": "🎪 展場視訊源即時截圖", 
            "瀏覽器": "🌐 瀏覽器畫面截圖",
            "攝像頭": "📹 攝像頭畫面截圖",
            "桌面": "💻 桌面畫面截圖"
        }
        
        base_caption = caption_map.get(source_name, f"📺 {source_name} 截圖")
        
        focus_suffix = {
            "technical": " - 技術狀況檢查",
            "streaming": " - 直播效果分析", 
            "audience": " - 觀眾互動分析",
            "content": " - 內容品質檢查",
            "detailed": " - 詳細分析"
        }
        
        if analysis_focus in focus_suffix:
            base_caption += focus_suffix[analysis_focus]
            
        return base_caption
    
    def _get_display_position(self, source_name: str) -> str:
        """根據來源類型決定顯示位置"""
        position_map = {
            "主螢幕": "center-right",  # 主螢幕顯示在右側
            "展場視訊源": "center-left",  # 展場保持在左側（與現有一致）
            "瀏覽器": "top-center",
            "攝像頭": "bottom-left",
            "桌面": "bottom-right"
        }
        return position_map.get(source_name, "center")

    async def _handle_generate_background_image(self, arguments: Dict[str, Any]) -> dict:
        """呼叫本地 /api/generate-background-image 生成背景並自動套用。
        策略：後端會自動從最近 3 筆 conversation 記憶生成描述；可選 extra_hint 與 aspect_ratio。
        """
        try:
            extra_hint = arguments.get("extra_hint")
            aspect_ratio = arguments.get("aspect_ratio")

            # 取得最近 3 筆對話記憶
            recent_contents: list[str] = []
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/memory/get",
                    json={"memory_type": "conversation", "limit": 3, "include_metadata": False},
                    timeout=aiohttp.ClientTimeout(total=6)
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

            if recent_contents:
                joined = " | ".join(recent_contents)
                description = (
                    f"Cinematic background that fits these recent conversation beats: {joined}. "
                )
            else:
                description = "Cinematic neutral space interior, gentle lights"

            if extra_hint:
                description += f" Hint: {extra_hint}."

            payload = {"description": description}
            if aspect_ratio:
                payload["aspect_ratio"] = aspect_ratio

            url = f"{self.base_url}/api/generate-background-image"
            logger.info(f"🖼️ 發送背景生成請求: {url} payload_desc_len={len(description)} aspect_ratio={aspect_ratio}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    text = await response.text()
                    if response.status == 200:
                        try:
                            data = json.loads(text) if text else {}
                        except json.JSONDecodeError:
                            data = {}
                        return {"success": True, "message": "Background generated", "result": data}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}: {text}"}
        except Exception as e:
            logger.error(f"❌ generate_background_image 處理錯誤: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_get_youtube_chat_messages(self, arguments: Dict[str, Any]) -> dict:
        """處理 YouTube 聊天室訊息獲取請求"""
        try:
            action = arguments.get("action", "recent")
            limit = arguments.get("limit", 10)
            
            logger.info(f"💬 處理 YouTube 聊天室訊息請求: action={action}, limit={limit}")
            
            # 檢查監控狀態
            status = self.youtube_chat_service.get_monitoring_status()
            if not status["monitoring"]:
                return {
                    "success": False,
                    "error": "YouTube 聊天室監控未啟動，請先開始直播對話會話",
                    "message_count": 0,
                    "messages": []
                }
            
            if action == "recent":
                # 獲取最新訊息
                messages = self.youtube_chat_service.get_recent_messages(limit)
                
                if not messages:
                    return {
                        "success": True,
                        "message": "目前沒有新的聊天訊息",
                        "message_count": 0,
                        "messages": [],
                        "monitoring_status": status
                    }
                
                # 格式化訊息用於 AI 理解
                formatted_messages = []
                for msg in messages:
                    formatted_msg = f"[{msg['datetime']}] {msg['author']}: {msg['message']}"
                    if msg['is_owner']:
                        formatted_msg += " (頻道擁有者)"
                    elif msg['is_sponsor']:
                        formatted_msg += " (贊助者)"
                    elif msg['is_moderator']:
                        formatted_msg += " (管理員)"
                    formatted_messages.append(formatted_msg)
                
                return {
                    "success": True,
                    "message": f"成功獲取 {len(messages)} 條最新聊天訊息",
                    "message_count": len(messages),
                    "messages": messages,
                    "formatted_messages": formatted_messages,
                    "monitoring_status": status
                }
                
            elif action == "search":
                # 搜尋特定關鍵字
                keyword = arguments.get("keyword")
                if not keyword:
                    return {
                        "success": False,
                        "error": "搜尋模式需要提供 keyword 參數"
                    }
                
                messages = self.youtube_chat_service.search_messages(keyword, limit)
                
                if not messages:
                    return {
                        "success": True,
                        "message": f"沒有找到包含 '{keyword}' 的聊天訊息",
                        "message_count": 0,
                        "messages": [],
                        "keyword": keyword
                    }
                
                return {
                    "success": True,
                    "message": f"找到 {len(messages)} 條包含 '{keyword}' 的訊息",
                    "message_count": len(messages),
                    "messages": messages,
                    "keyword": keyword,
                    "monitoring_status": status
                }
                
            elif action == "user_messages":
                # 獲取特定使用者的訊息
                username = arguments.get("username")
                if not username:
                    return {
                        "success": False,
                        "error": "使用者模式需要提供 username 參數"
                    }
                
                messages = self.youtube_chat_service.get_user_messages(username, limit)
                
                if not messages:
                    return {
                        "success": True,
                        "message": f"沒有找到使用者 '{username}' 的聊天訊息",
                        "message_count": 0,
                        "messages": [],
                        "username": username
                    }
                
                return {
                    "success": True,
                    "message": f"找到 {len(messages)} 條來自 '{username}' 的訊息",
                    "message_count": len(messages),
                    "messages": messages,
                    "username": username,
                    "monitoring_status": status
                }
            
            else:
                return {
                    "success": False,
                    "error": f"不支援的查詢類型: {action}"
                }
                
        except Exception as e:
            logger.error(f"❌ YouTube 聊天室訊息處理錯誤: {e}")
            return {
                "success": False,
                "error": f"獲取 YouTube 聊天室訊息失敗: {str(e)}"
            } 
