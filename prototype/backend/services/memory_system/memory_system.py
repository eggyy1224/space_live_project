import logging
import time
import os
import asyncio
from typing import List, Tuple, Dict, Any, Optional

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from core.config import settings
from core.exceptions import AIServiceException

from .memory_components.stores import ChromaMemoryStore, ShortTermMemoryStore
from .memory_components.retrieval import MemoryRetriever
from .memory_components.processing import InputFilter, PersonaUpdater, ConversationSummarizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemorySystem:
    """
    記憶系統協調者 - 負責整合各個記憶組件
    管理記憶的儲存、檢索和處理
    """

    def __init__(self, embeddings: GoogleGenerativeAIEmbeddings, persona_name: str, llm: Optional[ChatGoogleGenerativeAI] = None):
        """
        初始化記憶系統
        
        Args:
            embeddings: 向量嵌入模型
            persona_name: AI角色名稱
            llm: 用於記憶整合和摘要的LLM模型 (可選)
        """
        self.embeddings = embeddings
        self.persona_name = persona_name
        self.llm = llm
        
        # 初始化記憶儲存組件
        self.conversation_store = self._init_memory_store("conversation_memory", "conversations")
        self.persona_store = self._init_memory_store("persona_memory", "persona_info")
        self.summary_store = self._init_memory_store("summary_memory", "conversation_summaries")
        self.short_term_store = ShortTermMemoryStore(max_size=20)
        
        # 初始化記憶處理組件
        self.input_filter = InputFilter(max_problematic_threshold=3)
        self.persona_updater = PersonaUpdater(self.persona_store, persona_name)
        self.summarizer = ConversationSummarizer(
            self.conversation_store,
            self.summary_store,
            llm,
            persona_name
        )
        
        # 初始化記憶檢索組件
        self.memory_retriever = MemoryRetriever(
            self.conversation_store,
            self.persona_store,
            self.summary_store,
            persona_name
        )
        
        # 初始化角色核心記憶
        self.persona_updater.initialize_core_persona_memory()
        
        logging.info("增強版記憶系統初始化完成")
    
    def _init_memory_store(self, dir_name: str, collection_name: str) -> ChromaMemoryStore:
        """
        初始化向量記憶儲存
        
        Args:
            dir_name: 儲存目錄名稱
            collection_name: 集合名稱
            
        Returns:
            初始化好的記憶儲存實例
        """
        db_path = os.path.join(settings.VECTOR_DB_PATH, dir_name)
        return ChromaMemoryStore(
            embedding_function=self.embeddings,
            persist_directory=db_path,
            collection_name=collection_name
        )
    
    async def retrieve_context(self, user_text: str, conversation_history: List[BaseMessage], k: Optional[int] = None) -> Tuple[str, str]:
        """
        檢索相關的對話記憶和角色信息
        
        Args:
            user_text: 當前用戶輸入
            conversation_history: 對話歷史
            k: 要檢索的記憶數量
            
        Returns:
            (格式化的相關對話記憶, 格式化的相關角色信息)
        """
        # 使用 MemoryRetriever 檢索上下文
        return await self.memory_retriever.retrieve_context(
            user_text=user_text,
            conversation_history=conversation_history,
            conversation_k=k
        )
    
    def store_conversation_turn(self, user_text: str, ai_response: str):
        """
        儲存一輪對話到記憶庫
        
        Args:
            user_text: 用戶輸入
            ai_response: AI回應
        """
        # 先加入短期記憶
        self.short_term_store.add(
            text=f"input: {user_text}\noutput: {ai_response}",
            metadata={
                "type": "conversation",
                "timestamp": time.time(),
                "user_input": user_text,
                "ai_response": ai_response
            }
        )
        
        # 檢查是否為問題輸入，如果是，不寫入長期記憶
        if not self.input_filter.should_store_input(user_text):
            logging.warning(f"檢測到問題輸入，不儲存到長期記憶。計數: {self.input_filter.problematic_input_count}")
            return
        
        # 寫入長期向量記憶
        try:
            self.conversation_store.add(
                text=f"input: {user_text}\noutput: {ai_response}",
                metadata={
                    "type": "conversation",
                    "timestamp": time.time(),
                    "user_input": user_text,
                    "ai_response": ai_response
                }
            )
            
            # 檢查並更新角色記憶
            self.persona_updater.check_and_update_persona_memory(user_text, ai_response)
            
            # 觸發記憶整合 (這是異步操作，不阻塞主流程)
            self.summarizer.consolidate_memories()
            
            logging.debug("對話輪次已儲存")
        except Exception as e:
            logging.error(f"儲存對話輪次失敗: {e}", exc_info=True)
    
    def _build_enhanced_query(self, user_text: str, conversation_history: List[BaseMessage]) -> str:
        """
        構建增強查詢 - 為了保持向後兼容而保留的方法
        
        Args:
            user_text: 用戶輸入
            conversation_history: 對話歷史
            
        Returns:
            增強查詢字串
        """
        # 直接委託給 memory_retriever 的 query_builder
        return self.memory_retriever.query_builder.build_enhanced_query(user_text, conversation_history)
    
    def _format_retrieved_memories(self, memory_contents: List[str]) -> str:
        """
        格式化檢索到的記憶 - 為了保持向後兼容而保留的方法
        
        Args:
            memory_contents: 記憶內容列表
            
        Returns:
            格式化後的記憶字串
        """
        # 將列表轉換為記憶檢索結果格式
        memory_results = [{"page_content": content} for content in memory_contents]
        # 委託給 memory_retriever 的 formatter
        return self.memory_retriever.formatter.format_retrieved_memories(memory_results)
    
    def _contains_problematic_content(self, content: str) -> bool:
        """
        檢查內容是否包含問題內容 - 為了保持向後兼容而保留的方法
        
        Args:
            content: 要檢查的內容
            
        Returns:
            如果包含問題內容則返回 True，否則返回 False
        """
        return self.memory_retriever._contains_problematic_content(content)
    
    def _is_problematic_input(self, text: str) -> bool:
        """
        判斷輸入是否為問題輸入 - 為了保持向後兼容而保留的方法
        
        Args:
            text: 要檢查的輸入
            
        Returns:
            如果是問題輸入則返回 True，否則返回 False
        """
        return self.input_filter.is_problematic_input(text)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        計算文本相似度 - 為了保持向後兼容而保留的方法
        
        Args:
            text1: 第一個文本
            text2: 第二個文本
            
        Returns:
            相似度分數 (0-1)
        """
        return self.persona_updater._text_similarity(text1, text2)
    
    def _check_and_update_persona_memory(self, user_text: str, ai_response: str):
        """
        檢查並更新角色記憶 - 為了保持向後兼容而保留的方法
        
        Args:
            user_text: 用戶輸入
            ai_response: AI回應
        """
        self.persona_updater.check_and_update_persona_memory(user_text, ai_response)
    
    def consolidate_memories(self):
        """
        觸發記憶整合 - 為了保持向後兼容而保留的方法
        """
        self.summarizer.consolidate_memories()
    
    async def async_consolidate_memories(self):
        """
        觸發異步記憶整合 - 為了保持向後兼容而保留的方法
        """
        await self.summarizer.async_consolidate_memories()
    
    def clean_up_old_memories(self, days: int = 30):
        """
        清理舊的記憶 - 為了保持向後兼容而保留的方法
        
        Args:
            days: 清理多少天前的記憶
        """
        self.summarizer.clean_up_old_memories(days) 