"""
AI對話服務模組 - 提供對話生成和記憶功能 (基於 LangGraph 實現)
"""

import logging
import google.generativeai as genai
from typing import Dict, Optional, List, Any
from core.config import settings
from core.exceptions import AIServiceException
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from .memory_system import MemorySystem
from .dialogue_graph import DialogueGraph, DEFAULT_NEUTRAL_KEYFRAMES, DEFAULT_ANIMATION_SEQUENCE

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIService:
    """
    向後兼容的 AI 服務 - 內部使用基於 LangGraph 的新架構，
    但對外提供與舊版相同的介面
    """
    
    def __init__(self):
        # 配置 Google API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # 角色名稱
        self.persona_name = "星際小可愛"
        
        # 創建嵌入模型
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # 創建 LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.AI_MODEL_NAME,
            temperature=settings.GENERATION_TEMPERATURE,
            top_p=settings.GENERATION_TOP_P, 
            top_k=settings.GENERATION_TOP_K,
            max_output_tokens=settings.GENERATION_MAX_TOKENS,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # 初始化新架構的組件
        self.memory_system = MemorySystem(self.embeddings, self.persona_name)
        self.dialogue_graph = DialogueGraph(self.memory_system, self.llm, self.persona_name)
        
        # 為了兼容性，保留這些屬性和引用
        # self.messages: List[BaseMessage] = []  # <--- 改為從 dialogue_graph 或 history 獲取
        self.character_state = self.dialogue_graph.initial_character_state.copy()  # 角色狀態
        self.current_task = None  # 當前任務
        self.tasks_history = []  # 任務歷史
        
        logging.info("AIService (基於 LangGraph 的兼容模式) 初始化完成")
        
    async def generate_response(
        self, 
        user_text: Optional[str] = None, 
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None # <--- 新增 history 參數
    ) -> Dict[str, Any]:
        """
        基於使用者輸入、系統提示或記憶生成AI回應 - 兼容舊版 API，但返回字典
        
        Args:
            user_text: 使用者輸入文本 (與 system_prompt 互斥)
            system_prompt: 系統觸發的提示 (例如用於生成 murmur，與 user_text 互斥)
            history: 包含對話歷史的列表，每個元素是 {'role': str, 'content': str, 'is_murmur': Optional[bool]} 的字典
            
        Returns:
            包含 'final_response', 'emotion', 'emotional_keyframes' 和 'body_animation_sequence' 的字典
        """
        if user_text is not None and system_prompt is not None:
            logging.error("generate_response 不能同時接收 user_text 和 system_prompt")
            raise ValueError("不能同時提供 user_text 和 system_prompt")
        if user_text is None and system_prompt is None:
             logging.warning("generate_response 需要提供 user_text 或 system_prompt")
             return {
                "final_response": "嗯...發生了什麼事？我好像沒有收到任何訊息。",
                "emotion": "confused",
                "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
                "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy(),
                "error": "缺少 user_text 或 system_prompt"
             }

        try:
            # --- 根據傳入的 history 構建 LangChain messages ---
            messages: List[BaseMessage] = []
            if history:
                for entry in history:
                    role = entry["role"]
                    content = entry["content"]
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "bot":
                        # 可以選擇是否在 content 中標記 murmur，或者讓 LLM 自己判斷
                        # prefix = "[Murmur] " if entry.get("is_murmur") else ""
                        # messages.append(AIMessage(content=f"{prefix}{content}"))
                        messages.append(AIMessage(content=content)) # 暫時不加前綴
            # --- 結束構建 messages ---

            # 根據是否有 system_prompt 調整傳遞給圖的參數
            graph_input = {
                "messages": messages, # <--- 使用從 history 構建的 messages
                "character_state": self.character_state,
                "current_task": self.current_task,
                "tasks_history": self.tasks_history
            }
            if system_prompt:
                 graph_input["system_prompt"] = system_prompt
            # 如果有 user_text，它將被圖中的節點處理（例如添加到 messages 中）
            if user_text:
                 graph_input["user_text"] = user_text # 顯式傳遞，即使歷史中已有

            # 調用 LangGraph 生成回應
            graph_result: Dict[str, Any] = await self.dialogue_graph.generate_response(**graph_input)
            
            # --- 不再需要從 self 更新 messages，因為 graph 應返回更新後的 ---
            # self.messages = graph_result.get("updated_messages", messages)
            # --- 結束 ---
            
            # 提取需要的返回內容
            final_response = graph_result.get("final_response", "嗯...我好像有點走神了。")
            response_emotion = graph_result.get("emotion", "neutral")
            emotional_keyframes = graph_result.get("emotional_keyframes")
            body_animation_sequence = graph_result.get("body_animation_sequence")
            
            return {
                "final_response": final_response,
                "emotion": response_emotion,
                "emotional_keyframes": emotional_keyframes,
                "body_animation_sequence": body_animation_sequence
            }
            
        except Exception as e:
            logging.error(f"生成 AI 回應失敗: {str(e)}", exc_info=True)
            return {
                "final_response": "哎呀，我的系統出了點小問題。太空干擾有時候真的很煩人，你能再說一次嗎？",
                "emotion": "frustrated",
                "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(),
                "body_animation_sequence": DEFAULT_ANIMATION_SEQUENCE.copy(),
                "error": str(e)
            }
            
    def update_character_state(self, updates: Dict[str, Any]) -> None:
        """
        更新角色狀態
        
        Args:
            updates: 要更新的狀態字典
        """
        # 使用 DialogueGraph 的方法更新狀態
        self.character_state = self.dialogue_graph.update_character_state(
            self.character_state, updates
        )
                    
    def set_current_task(self, task: str) -> None:
        """
        設置當前任務
        
        Args:
            task: 任務描述
        """
        # 記錄被中斷的任務
        if self.current_task:
            self.tasks_history.append({
                "task": self.current_task, 
                "status": "interrupted",
                "day": self.character_state["days_in_space"]
            })
            logging.info(f"任務 '{self.current_task}' 被新任務中斷")
            
        self.current_task = task
        logging.info(f"設置新任務: {task}")
        
    def complete_current_task(self, success: bool = True) -> None:
        """
        完成當前任務
        
        Args:
            success: 任務是否成功
        """
        if self.current_task:
            # 記錄任務結果
            status = "success" if success else "failed"
            task_result = {
                "task": self.current_task,
                "status": status,
                "day": self.character_state["days_in_space"]
            }
            self.tasks_history.append(task_result)
            logging.info(f"任務 '{self.current_task}' 完成，狀態: {status}")
            
            # 更新狀態
            mood_change = 5 if success else -5
            energy_change = -5  # 完成任務消耗能量
            
            state_updates = {
                "mood": f"{mood_change:+d}", 
                "energy": f"{energy_change:+d}"
            }
            
            if success:
                state_updates["task_success"] = "+1"
                
            self.update_character_state(state_updates)
            
            # 重置當前任務
            self.current_task = None
        else:
            logging.warning("嘗試完成任務，但當前沒有任務。")
            
    def advance_day(self) -> None:
        """推進一天時間並更新相關狀態"""
        # 基礎狀態變化
        state_updates = {
            "days_in_space": "+1",
            "energy": "+15"  # 每天自然恢復能量
        }
        
        # 如果沒有任務，心情可能稍微下降
        if not self.current_task:
            state_updates["mood"] = "-2"
            
        self.update_character_state(state_updates)
        logging.info(f"時間推進到第 {self.character_state['days_in_space']} 天") 