"""
腳本執行控制 Agent
專門處理腳本執行的智能決策和控制邏輯
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import aiohttp
import subprocess
import os

logger = logging.getLogger(__name__)


class ScriptExecutionAgent:
    """
    腳本執行控制 Agent
    負責智能選擇和執行適合的腳本
    """
    
    def __init__(self):
        """初始化腳本執行 Agent"""
        self.base_url = "http://localhost:8000"
        self.scripts_dir = Path(__file__).parent.parent.parent / "experiment_scripts"
        
        # 腳本映射：情境 -> 推薦腳本
        self.script_mapping = {
            "meta": ["meta_self.sh"],
            "元戲劇": ["meta_self.sh"],
            "自我": ["meta_self.sh"],
            "導演": ["meta_self.sh"],
            "意識": ["meta_self.sh"],
            
            "音樂": ["remix_scene.sh"],
            "舞蹈": ["remix_scene.sh"],
            "表演": ["remix_scene.sh"],
            "remix": ["remix_scene.sh"],
            "混合": ["remix_scene.sh"],
            
            "太空": ["space_story_script.sh"],
            "宇宙": ["space_story_script.sh"],
            "星球": ["space_story_script.sh"],
            "探險": ["space_story_script.sh"],
            "story": ["space_story_script.sh"],
            
            "瑜伽": ["space_yoga2.sh"],
            "yoga": ["space_yoga2.sh"],
            "太空瑜伽": ["space_yoga2.sh"],
            "space yoga": ["space_yoga2.sh"],
            "瑜伽教室": ["space_yoga2.sh"],
            "辣妹瑜伽": ["space_yoga2.sh"],
            "運動": ["space_yoga2.sh"],
            "健身": ["space_yoga2.sh"],
            "教學": ["space_yoga2.sh"],
            "冥想": ["space_yoga2.sh"],
            
            "新聞": ["news_broadcast.sh"],
            "播報": ["news_broadcast.sh"],
            "廣播": ["news_broadcast.sh"],
            "資訊": ["news_broadcast.sh"],
            "news": ["news_broadcast.sh"]
        }
        
        # 所有可用腳本
        self.available_scripts = [
            "meta_self.sh",
            "remix_scene.sh", 
            "space_story_script.sh",
            "news_broadcast.sh",
            "space_yoga2.sh"
        ]
        
        logger.info("🎬 ScriptExecutionAgent 初始化完成")
    
    async def _handle_script_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """處理簡化的劇本表演請求（包含執行和停止）"""
        try:
            request = arguments.get("request", "")
            
            if not request:
                return {
                    "success": False,
                    "error": "Missing required parameter: request"
                }
            
            logger.info(f"🎭 處理劇本表演請求: {request}")
            
            # 檢查是否為停止請求
            if self._is_stop_request(request):
                return await self._handle_stop_all_scripts()
            
            # 檢查是否有腳本正在執行
            status_result = await self._handle_script_status({})
            if status_result.get("success") and status_result.get("total_running", 0) > 0:
                running_scripts = status_result.get("running_scripts", [])
                logger.warning(f"⚠️ 有腳本正在執行中: {running_scripts}")
                return {
                    "success": False,
                    "error": f"有腳本正在執行中: {', '.join(running_scripts)}。請等待執行完成或先停止現有腳本。",
                    "running_scripts": running_scripts,
                    "total_running": len(running_scripts)
                }
            
            # 否則為執行請求：選擇並執行劇本
            selected_script = self._smart_script_selection(request)
            execution_args = {
                "script_name": selected_script,
                "background": True
            }
            
            result = await self._handle_execute_script(execution_args)
            
            if result.get("success"):
                result["selected_script"] = selected_script
                result["request"] = request
                logger.info(f"✅ 劇本表演成功啟動: {selected_script}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 處理劇本表演時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"Script performance failed: {str(e)}"
            }
    
    def _is_stop_request(self, request: str) -> bool:
        """判斷是否為停止請求"""
        stop_keywords = ["停止", "結束", "停", "stop", "end", "關閉", "取消", "cancel", "暫停", "pause"]
        request_lower = request.lower()
        return any(keyword in request_lower for keyword in stop_keywords)
    
    async def _handle_stop_all_scripts(self) -> Dict[str, Any]:
        """停止所有正在運行的劇本"""
        try:
            # 透過 API 調用停止所有腳本
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/scripts/stop-all"
                
                async with session.post(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ 所有劇本停止成功")
                        return result
                    else:
                        # 如果沒有 stop-all API，嘗試逐個停止
                        return await self._stop_scripts_individually()
                        
        except Exception as e:
            logger.error(f"❌ 停止劇本時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"Stop scripts failed: {str(e)}"
            }
    
    async def _stop_scripts_individually(self) -> Dict[str, Any]:
        """逐個停止所有可能的劇本"""
        try:
            stopped_scripts = []
            for script in self.available_scripts:
                try:
                    result = await self._handle_stop_script({"script_name": script})
                    if result.get("success"):
                        stopped_scripts.append(script)
                except:
                    continue  # 忽略錯誤，繼續嘗試下一個
            
            return {
                "success": True,
                "message": f"成功停止 {len(stopped_scripts)} 個劇本",
                "stopped_scripts": stopped_scripts
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Individual stop failed: {str(e)}"
            }
    
    def _smart_script_selection(self, request: str) -> str:
        """根據請求內容智能選擇劇本"""
        request_lower = request.lower()
        
        # 關鍵詞匹配 - 按關鍵詞長度降序排列，確保較長的關鍵詞優先匹配
        matched_keywords = []
        for keyword, scripts in self.script_mapping.items():
            if keyword.lower() in request_lower:
                matched_keywords.append((keyword, scripts[0], len(keyword)))
        
        # 如果有匹配的關鍵詞，選擇最長的（最具體的）
        if matched_keywords:
            # 按關鍵詞長度降序排列，最長的排在前面
            matched_keywords.sort(key=lambda x: x[2], reverse=True)
            best_match = matched_keywords[0]
            logger.info(f"🎯 關鍵詞匹配: '{best_match[0]}' (長度: {best_match[2]}) -> {best_match[1]}")
            return best_match[1]
        
        # 如果沒有匹配，默認選擇 meta_self.sh（最具代表性的表演）
        default_script = "meta_self.sh"
        logger.info(f"🎲 沒有關鍵詞匹配，使用默認劇本: {default_script}")
        return default_script
    
    async def execute_script_control(self, control_type: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行腳本控制操作
        
        Args:
            control_type: 控制類型 (script_performance, execute_script, list_scripts, stop_script, script_status)
            arguments: 控制參數
            
        Returns:
            Dict[str, Any]: 執行結果
        """
        try:
            logger.info(f"🎬 執行腳本控制: {control_type}")
            logger.info(f"📋 控制參數: {arguments}")
            
            if control_type == "script_performance":
                return await self._handle_script_performance(arguments)
            elif control_type == "execute_script":
                return await self._handle_execute_script(arguments)
            elif control_type == "list_scripts":
                return await self._handle_list_scripts(arguments)
            elif control_type == "stop_script":
                return await self._handle_stop_script(arguments)
            elif control_type == "script_status":
                return await self._handle_script_status(arguments)
            elif control_type == "smart_script_selection":
                return await self._handle_smart_script_selection(arguments)
            else:
                return {
                    "success": False,
                    "error": f"Unknown script control type: {control_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ 腳本控制執行失敗: {e}")
            return {
                "success": False,
                "error": f"Script control execution failed: {str(e)}"
            }
    
    async def _handle_execute_script(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """處理腳本執行請求"""
        try:
            script_name = arguments.get("script_name")
            background = arguments.get("background", True)
            
            if not script_name:
                return {
                    "success": False,
                    "error": "Missing required parameter: script_name"
                }
            
            # 透過 API 調用執行腳本
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/scripts/execute"
                payload = {
                    "script_name": script_name,
                    "background": background
                }
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ 腳本執行成功: {result}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 腳本執行失敗: {error_text}")
                        return {
                            "success": False,
                            "error": f"API call failed: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 執行腳本時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"Execute script failed: {str(e)}"
            }
    
    async def _handle_list_scripts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """處理列出腳本請求"""
        try:
            # 透過 API 調用列出腳本
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/scripts/list"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ 腳本列表取得成功")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 腳本列表取得失敗: {error_text}")
                        return {
                            "success": False,
                            "error": f"API call failed: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 列出腳本時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"List scripts failed: {str(e)}"
            }
    
    async def _handle_stop_script(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """處理停止腳本請求"""
        try:
            script_name = arguments.get("script_name")
            
            if not script_name:
                return {
                    "success": False,
                    "error": "Missing required parameter: script_name"
                }
            
            # 透過 API 調用停止腳本
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/scripts/stop/{script_name}"
                
                async with session.post(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ 腳本停止成功: {result}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 腳本停止失敗: {error_text}")
                        return {
                            "success": False,
                            "error": f"API call failed: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 停止腳本時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"Stop script failed: {str(e)}"
            }
    
    async def _handle_script_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """處理腳本狀態查詢請求"""
        try:
            # 透過 API 調用查詢腳本狀態
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/scripts/status"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ 腳本狀態查詢成功")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ 腳本狀態查詢失敗: {error_text}")
                        return {
                            "success": False,
                            "error": f"API call failed: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ 查詢腳本狀態時發生錯誤: {e}")
            return {
                "success": False,
                "error": f"Get script status failed: {str(e)}"
            }
    
    async def _handle_smart_script_selection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """智能腳本選擇"""
        try:
            context = arguments.get("context", "")
            mood = arguments.get("mood", "")
            theme = arguments.get("theme", "")
            duration_preference = arguments.get("duration_preference", "medium")  # short, medium, long
            
            # 基於關鍵詞匹配推薦腳本
            recommended_scripts = []
            search_text = f"{context} {mood} {theme}".lower()
            
            for keyword, scripts in self.script_mapping.items():
                if keyword.lower() in search_text:
                    recommended_scripts.extend(scripts)
            
            # 去重並按優先級排序
            recommended_scripts = list(set(recommended_scripts))
            
            if not recommended_scripts:
                # 如果沒有匹配，根據時長偏好推薦
                if duration_preference == "short":
                    recommended_scripts = ["news_broadcast.sh"]
                elif duration_preference == "long":
                    recommended_scripts = ["meta_self.sh"]
                else:
                    recommended_scripts = ["remix_scene.sh", "space_story_script.sh"]
            
            # 選擇第一個推薦的腳本執行
            if recommended_scripts:
                selected_script = recommended_scripts[0]
                
                # 自動執行選中的腳本
                execution_result = await self._handle_execute_script({
                    "script_name": selected_script,
                    "background": True
                })
                
                return {
                    "success": True,
                    "selected_script": selected_script,
                    "recommended_scripts": recommended_scripts,
                    "execution_result": execution_result,
                    "message": f"智能選擇並執行腳本: {selected_script}"
                }
            else:
                return {
                    "success": False,
                    "error": "No suitable script found for the given context"
                }
                
        except Exception as e:
            logger.error(f"❌ 智能腳本選擇失敗: {e}")
            return {
                "success": False,
                "error": f"Smart script selection failed: {str(e)}"
            }
    
    def get_script_info(self, script_name: str) -> Dict[str, Any]:
        """取得腳本資訊"""
        script_info = {
            "meta_self.sh": {
                "name": "meta_self.sh",
                "title": "《伊始之眼：一個導演的誕生》",
                "description": "元戲劇腳本，講述 AI 導演自我形成的故事",
                "duration": "15-20 分鐘",
                "theme": "元戲劇、自我意識、導演誕生",
                "suitable_for": "完整表演、概念展示"
            },
            "remix_scene.sh": {
                "name": "remix_scene.sh", 
                "title": "音樂與場景混合劇本",
                "description": "音樂導向的場景組合表演",
                "duration": "10-15 分鐘",
                "theme": "音樂、場景切換、表演",
                "suitable_for": "音樂表演、氛圍營造"
            },
            "space_story_script.sh": {
                "name": "space_story_script.sh",
                "title": "太空故事腳本", 
                "description": "太空主題的敘事表演",
                "duration": "12-18 分鐘",
                "theme": "太空探險、宇宙故事",
                "suitable_for": "主題表演、故事敘述"
            },
            "news_broadcast.sh": {
                "name": "news_broadcast.sh",
                "title": "新聞播報劇本",
                "description": "新聞主播風格的表演", 
                "duration": "8-12 分鐘",
                "theme": "新聞播報、資訊傳達",
                "suitable_for": "資訊播報、正式場合"
            },
            "space_yoga2.sh": {
                "name": "space_yoga2.sh",
                "title": "《太空辣妹瑜伽教室 2.0》",
                "description": "太空主題的瑜伽動作教學與互動表演，融合動畫、音效與多媒體展示",
                "duration": "15-25 分鐘",
                "theme": "太空、瑜伽、互動教學、運動",
                "suitable_for": "主題互動、運動教學、趣味表演"
            }
        }
        
        return script_info.get(script_name, {
            "name": script_name,
            "title": "未知腳本",
            "description": "無描述",
            "duration": "未知",
            "theme": "未知",
            "suitable_for": "未知"
        }) 