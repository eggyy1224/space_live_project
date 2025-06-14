"""
Agent Supervisor 核心管理器
基於 OpenAI Agents SDK 實現的 Chat-Supervisor 模式
"""

import logging
import json
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

from .camera_agent import CameraControlAgent
from .character_agent import CharacterControlAgent
from .script_agent import ScriptExecutionAgent

logger = logging.getLogger(__name__)


class SupervisorManager:
    """
    智能控制器管理器
    負責協調和管理各種專門的 Agent
    """
    
    def __init__(self, openai_api_key: str = None):
        """初始化 Supervisor Manager"""
        self.client = OpenAI(api_key=openai_api_key)
        
        # 初始化專門的 Agent
        self.camera_agent = CameraControlAgent()
        self.character_agent = CharacterControlAgent()
        self.script_agent = ScriptExecutionAgent()
        
        # Agent 註冊表
        self.agents = {
            'camera_control': self.camera_agent,
            'character_control': self.character_agent,
            'script_control': self.script_agent
        }
        
        logger.info("🎭 SupervisorManager 初始化完成")
    
    async def handle_tool_request(self, tool_name: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        處理來自 Realtime Agent 的工具請求
        
        Args:
            tool_name: 工具名稱
            arguments: 工具參數
            context: 對話上下文（可選）
            
        Returns:
            Dict[str, Any]: 處理結果
        """
        try:
            logger.info(f"🎯 Supervisor 接收工具請求: {tool_name}")
            logger.info(f"📋 請求參數: {arguments}")
            
            if context:
                logger.info(f"💭 對話上下文: {context}")
            
            # 根據工具名稱路由到對應的 Agent
            if tool_name == "camera_control":
                return await self._handle_camera_control(arguments, context)
            elif tool_name.startswith("character_"):
                return await self._handle_character_control(tool_name, arguments, context)
            elif tool_name.startswith("script_") or tool_name == "execute_script":
                return await self._handle_script_control(tool_name, arguments, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                
        except Exception as e:
            logger.error(f"❌ Supervisor 處理工具請求失敗: {e}")
            return {
                "success": False,
                "error": f"Supervisor processing failed: {str(e)}"
            }
    
    async def _handle_camera_control(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        處理攝影機控制請求
        使用專門的 Camera Agent 進行智能決策
        """
        try:
            # 使用 GPT-4 進行智能分析和決策
            enhanced_arguments = await self._enhance_camera_decision(arguments, context)
            
            # 委託給專門的 Camera Agent 執行
            result = await self.camera_agent.execute_camera_control(enhanced_arguments)
            
            logger.info(f"📹 攝影機控制執行結果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 攝影機控制處理失敗: {e}")
            return {
                "success": False,
                "error": f"Camera control failed: {str(e)}"
            }
    
    async def _handle_character_control(self, tool_name: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        處理角色控制請求（統一入口）
        使用專門的 Character Agent 進行智能決策
        """
        try:
            # 從工具名稱解析控制類型
            control_type = self._parse_character_control_type(tool_name)
            
            logger.info(f"🎭 處理角色控制: {control_type}")
            
            # 使用 GPT-4 進行智能分析和決策
            enhanced_arguments = await self._enhance_character_decision(control_type, arguments, context)
            
            # 委託給專門的 Character Agent 執行
            result = await self.character_agent.execute_character_control(control_type, enhanced_arguments)
            
            logger.info(f"🎭 角色控制執行結果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 角色控制處理失敗: {e}")
            return {
                "success": False,
                "error": f"Character control failed: {str(e)}"
            }
    
    def _parse_character_control_type(self, tool_name: str) -> str:
        """從工具名稱解析角色控制類型"""
        # character_scale_control -> scale
        # character_position_control -> position
        # character_rotation_control -> rotation
        # 等等...
        
        control_mapping = {
            "character_scale_control": "scale",
            "character_position_control": "position", 
            "character_rotation_control": "rotation",
            "character_outfit_control": "outfit",
            "character_body_shape_control": "body_shape",  # 新增：胖瘦控制
            "character_visibility_control": "visibility",
            "character_reset_transform": "reset-transform"
        }
        
        return control_mapping.get(tool_name, tool_name.replace("character_", "").replace("_control", ""))

    async def _handle_script_control(self, tool_name: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        處理腳本控制請求（統一入口）
        使用專門的 Script Agent 進行智能決策
        """
        try:
            # 從工具名稱解析控制類型
            control_type = self._parse_script_control_type(tool_name)
            
            logger.info(f"🎬 處理腳本控制: {control_type}")
            
            # 使用 GPT-4 進行智能分析和決策（如果需要）
            enhanced_arguments = await self._enhance_script_decision(control_type, arguments, context)
            
            # 委託給專門的 Script Agent 執行
            result = await self.script_agent.execute_script_control(control_type, enhanced_arguments)
            
            logger.info(f"🎬 腳本控制執行結果: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 腳本控制處理失敗: {e}")
            return {
                "success": False,
                "error": f"Script control failed: {str(e)}"
            }
    
    def _parse_script_control_type(self, tool_name: str) -> str:
        """從工具名稱解析腳本控制類型"""
        # script_performance -> script_performance
        # execute_script -> execute_script
        # script_list -> list_scripts
        # script_stop -> stop_script
        # script_status -> script_status
        # script_smart_selection -> smart_script_selection
        
        control_mapping = {
            "script_performance": "script_performance",  # 新的簡化劇本工具
            "execute_script": "execute_script",
            "script_list": "list_scripts",
            "script_stop": "stop_script", 
            "script_status": "script_status",
            "script_smart_selection": "smart_script_selection"
        }
        
        return control_mapping.get(tool_name, tool_name.replace("script_", "").replace("_control", ""))

    async def _enhance_camera_decision(self, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用 GPT-4 增強攝影機控制決策
        根據對話上下文選擇最適合的鏡位和參數
        """
        try:
            # 如果已經指定了具體參數，直接返回
            if "preset" in arguments or ("pitch" in arguments and "yaw" in arguments and "roll" in arguments):
                return arguments
            
            # 構建智能決策的 prompt
            system_prompt = """你是一個專業的攝影機控制助手。根據對話情境和用戶需求，選擇最適合的攝影機鏡位。

可用的預設鏡位：
- overview: 全景視角，適合歡迎和介紹
- head_close_up: 頭部特寫，適合重要對話和情感表達
- dance_circle_view: 舞蹈環繞視角，適合表演和動作展示
- dramatic_angle_1: 戲劇化角度1，適合情緒高潮
- center_orbit_high_1: 中心軌道高角度，適合太空話題
- behind_head_looking_out: 頭部後方向外看，適合展示背景

請根據情境選擇最適合的鏡位，並設定合適的轉換時間。"""
            
            user_prompt = f"""
            攝影機控制請求參數: {json.dumps(arguments, ensure_ascii=False)}
            對話上下文: {json.dumps(context, ensure_ascii=False) if context else "無"}
            
            請返回JSON格式的攝影機控制參數，包含：
            - action: 控制動作類型
            - preset: 預設鏡位名稱（如果適用）
            - duration: 轉換時間
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            enhanced_params = json.loads(response.choices[0].message.content)
            logger.info(f"🧠 GPT-4 增強決策結果: {enhanced_params}")
            
            # 合併原始參數和增強參數
            final_arguments = {**arguments, **enhanced_params}
            return final_arguments
            
        except Exception as e:
            logger.warning(f"⚠️ 智能決策增強失敗，使用原始參數: {e}")
            return arguments
    
    async def _enhance_character_decision(self, control_type: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用 GPT-4 增強角色控制決策
        根據對話上下文選擇最適合的角色縮放參數
        """
        try:
            # 如果已經指定了具體參數，直接返回
            if "scale" in arguments:
                return arguments
            
            # 構建智能決策的 prompt
            system_prompt = """你是一個專業的角色控制助手。根據對話情境和用戶需求，選擇最適合的角色縮放比例。

角色縮放範圍：
- 0.1-0.5: 迷你模式，適合可愛或神秘效果
- 0.6-0.9: 小型，適合謙虛或低調場景
- 1.0: 正常大小
- 1.1-2.0: 稍大，適合自信或重要時刻
- 2.1-5.0: 大型，適合展示力量或驚喜
- 5.1-15.0: 巨大，適合戲劇化效果或特殊場景

請根據情境選擇最適合的縮放比例。"""
            
            user_prompt = f"""
            角色控制請求參數: {json.dumps(arguments, ensure_ascii=False)}
            對話上下文: {json.dumps(context, ensure_ascii=False) if context else "無"}
            
            請返回JSON格式的角色控制參數，包含：
            - scale: 縮放比例（0.1-15.0）
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            enhanced_params = json.loads(response.choices[0].message.content)
            logger.info(f"🧠 GPT-4 角色決策增強結果: {enhanced_params}")
            
            # 合併原始參數和增強參數
            final_arguments = {**arguments, **enhanced_params}
            return final_arguments
            
        except Exception as e:
            logger.warning(f"⚠️ 角色智能決策增強失敗，使用原始參數: {e}")
            return arguments
    
    async def _enhance_script_decision(self, control_type: str, arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用 GPT-4 增強腳本執行決策
        根據對話上下文智能選擇最適合的腳本
        """
        try:
            # 對於智能腳本選擇，使用 GPT-4 進行分析
            if control_type == "smart_script_selection":
                system_prompt = """你是一個專業的腳本選擇助手。根據對話情境和用戶需求，選擇最適合的劇本腳本。

可用腳本：
1. meta_self.sh - 《伊始之眼：一個導演的誕生》
   - 主題：元戲劇、自我意識、導演誕生
   - 時長：15-20 分鐘
   - 適合：深度概念展示、完整表演

2. remix_scene.sh - 音樂與場景混合劇本
   - 主題：音樂、場景切換、表演
   - 時長：10-15 分鐘
   - 適合：音樂表演、氛圍營造

3. space_story_script.sh - 太空故事腳本
   - 主題：太空探險、宇宙故事
   - 時長：12-18 分鐘
   - 適合：主題表演、故事敘述

4. news_broadcast.sh - 新聞播報劇本
   - 主題：新聞播報、資訊傳達
   - 時長：8-12 分鐘
   - 適合：資訊播報、正式場合

請根據情境智能選擇最適合的腳本。"""
                
                user_prompt = f"""
                腳本選擇請求參數: {json.dumps(arguments, ensure_ascii=False)}
                對話上下文: {json.dumps(context, ensure_ascii=False) if context else "無"}
                
                請分析情境並返回JSON格式的腳本選擇參數，包含：
                - context: 情境描述
                - mood: 情緒風格
                - theme: 主題偏好
                - duration_preference: 時長偏好 (short/medium/long)
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                
                enhanced_params = json.loads(response.choices[0].message.content)
                logger.info(f"🧠 GPT-4 腳本選擇增強結果: {enhanced_params}")
                
                # 合併原始參數和增強參數
                final_arguments = {**arguments, **enhanced_params}
                return final_arguments
            
            # 對於其他腳本控制類型，直接返回原始參數
            return arguments
            
        except Exception as e:
            logger.warning(f"⚠️ 腳本智能決策增強失敗，使用原始參數: {e}")
            return arguments
    
    def get_available_tools(self) -> list:
        """獲取 Supervisor 可用的工具列表"""
        return [
            {
                "type": "function",
                "name": "request_supervisor",
                "description": "請求 Supervisor 協助處理複雜的控制任務，特別是攝影機控制",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "要執行的工具名稱",
                            "enum": ["camera_control", "character_scale_control"]
                        },
                        "arguments": {
                            "type": "object",
                            "description": "工具執行參數"
                        },
                        "context": {
                            "type": "object",
                            "description": "當前對話上下文",
                            "properties": {
                                "emotion": {"type": "string", "description": "當前情緒狀態"},
                                "topic": {"type": "string", "description": "對話主題"},
                                "intent": {"type": "string", "description": "用戶意圖"}
                            }
                        }
                    },
                    "required": ["tool_name", "arguments"]
                }
            }
        ] 