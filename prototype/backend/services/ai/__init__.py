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
from .dialogue_graph import DialogueGraph

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
        self.messages: List[BaseMessage] = []  # 對話歷史
        self.character_state = self.dialogue_graph.initial_character_state.copy()  # 角色狀態
        self.current_task = None  # 當前任務
        self.tasks_history = []  # 任務歷史
        
        logging.info("AIService (基於 LangGraph 的兼容模式) 初始化完成")
        
    async def generate_response(self, user_text: str, current_emotion: str = None) -> str:
        """
        基於使用者輸入和記憶生成AI回應 - 兼容舊版 API
        
        Args:
            user_text: 使用者輸入文本
            current_emotion: 當前檢測到的情緒 (已棄用，保留參數兼容)
            
        Returns:
            AI生成的回應
        """
        try:
            # 將原始對話歷史轉換為 BaseMessage 格式（如果需要）
            # 這確保即使外部傳入原始對話歷史，我們也能正確處理
            messages = self.messages.copy()
            
            # 調用 LangGraph 生成回應
            ai_response, updated_messages = await self.dialogue_graph.generate_response(
                user_text=user_text,
                messages=messages,
                character_state=self.character_state,
                current_task=self.current_task,
                tasks_history=self.tasks_history
            )
            
            # 更新對話歷史
            self.messages = updated_messages
            
            return ai_response
            
        except Exception as e:
            logging.error(f"生成 AI 回應失敗: {str(e)}", exc_info=True)
            # 返回一個友好的錯誤消息 
            return "哎呀，我的系統出了點小問題。太空干擾有時候真的很煩人，你能再說一次嗎？"
            
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