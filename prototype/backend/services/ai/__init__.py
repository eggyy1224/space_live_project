"""
AI對話服務模組 - 提供對話生成和記憶功能
"""

import logging
import google.generativeai as genai
from typing import Dict, Optional, List, Any
from core.config import settings
from core.exceptions import AIServiceException
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from .memory_system import MemorySystem
from .dialogue_manager import DialogueManager

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIService:
    """
    向後兼容的 AI 服務 - 內部使用新的 Memory + Dialogue 架構，
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
        self.dialogue_manager = DialogueManager(self.memory_system, self.llm)
        
        # 為了兼容性，保留這些屬性的引用
        self.messages = self.dialogue_manager.messages
        self.character_state = self.dialogue_manager.character_state
        self.current_task = None
        self.tasks_history = self.dialogue_manager.tasks_history
        
        logging.info("AIService (兼容模式) 初始化完成")
        
    async def generate_response(self, user_text: str, current_emotion: str = None) -> str:
        """
        基於使用者輸入和記憶生成AI回應 - 兼容舊版 API
        
        Args:
            user_text: 使用者輸入文本
            current_emotion: 當前檢測到的情緒 (已棄用，保留參數兼容)
            
        Returns:
            AI生成的回應
        """
        # 直接委託給 dialogue_manager 的方法
        response = await self.dialogue_manager.generate_response(user_text)
        
        # 同步相關狀態，以確保兼容性
        self.character_state = self.dialogue_manager.character_state
        self.current_task = self.dialogue_manager.current_task
        self.tasks_history = self.dialogue_manager.tasks_history
        
        return response
            
    def update_character_state(self, updates: Dict[str, Any]) -> None:
        """
        更新角色狀態
        
        Args:
            updates: 要更新的狀態字典
        """
        self.dialogue_manager.update_character_state(updates)
        self.character_state = self.dialogue_manager.character_state
                    
    def set_current_task(self, task: str) -> None:
        """
        設置當前任務
        
        Args:
            task: 任務描述
        """
        self.dialogue_manager.set_current_task(task)
        self.current_task = self.dialogue_manager.current_task
        
    def complete_current_task(self, success: bool = True) -> None:
        """
        完成當前任務
        
        Args:
            success: 任務是否成功
        """
        self.dialogue_manager.complete_current_task(success)
        self.current_task = self.dialogue_manager.current_task
        self.character_state = self.dialogue_manager.character_state
            
    def advance_day(self) -> None:
        """推進一天時間並更新相關狀態"""
        self.dialogue_manager.advance_day()
        self.character_state = self.dialogue_manager.character_state 