import logging
import time
import asyncio
from typing import List, Dict, Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from ..stores import BaseMemoryStore

class ConversationSummarizer:
    """
    負責生成對話摘要並存儲
    """
    
    def __init__(
        self, 
        conversation_store: BaseMemoryStore,
        summary_store: BaseMemoryStore,
        llm: Optional[ChatGoogleGenerativeAI] = None,
        persona_name: str = "星際小可愛"
    ):
        """
        初始化對話摘要器
        
        Args:
            conversation_store: 對話記憶儲存
            summary_store: 摘要記憶儲存
            llm: LLM模型，用於生成摘要 (可選)
            persona_name: AI角色名稱
        """
        self.conversation_store = conversation_store
        self.summary_store = summary_store
        self.llm = llm
        self.persona_name = persona_name
        
        # 記憶整合鎖 - 防止多個整合任務同時運行
        self.consolidation_lock = asyncio.Lock()
        
        # 記憶整合時間戳
        self.memory_last_consolidated = time.time()
    
    def consolidate_memories(self):
        """
        觸發記憶整合任務 (同步版本)
        """
        # 檢查是否需要整合
        if time.time() - self.memory_last_consolidated < 3600:  # 每小時最多整合一次
            return
        
        logging.info("觸發記憶整合...")
        if asyncio.get_event_loop().is_running():
            # 如果事件循環在運行，創建異步任務
            asyncio.create_task(self.async_consolidate_memories())
        else:
            # 否則同步運行
            self._perform_memory_consolidation()
    
    async def async_consolidate_memories(self):
        """
        異步執行記憶整合
        """
        # 使用鎖避免並發整合
        if self.consolidation_lock.locked():
            logging.info("記憶整合已在進行中，跳過...")
            return
            
        async with self.consolidation_lock:
            # 檢查是否需要整合
            if time.time() - self.memory_last_consolidated < 3600:  # 每小時最多整合一次
                return
                
            logging.info("開始異步記憶整合...")
            await self._async_perform_memory_consolidation()
            self.memory_last_consolidated = time.time()
    
    def _perform_memory_consolidation(self):
        """
        執行實際的記憶整合 (同步版本)
        """
        if not self.llm:
            logging.warning("沒有提供LLM，無法執行記憶整合")
            return
            
        # 從向量數據庫獲取最近的對話
        try:
            recent_conversations = self.conversation_store.get_all(
                limit=20,
                where={"timestamp": {"$gt": time.time() - 86400}}  # 獲取過去24小時的對話
            )
            
            if not recent_conversations["ids"]:
                logging.info("沒有找到最近24小時的對話記錄，跳過整合")
                return
                
            # 生成摘要並存儲
            self._generate_and_store_summaries(recent_conversations)
            
            logging.info("記憶整合完成")
            
        except Exception as e:
            logging.error(f"記憶整合失敗: {e}", exc_info=True)
    
    async def _async_perform_memory_consolidation(self):
        """
        執行實際的記憶整合 (異步版本)
        """
        if not self.llm:
            logging.warning("沒有提供LLM，無法執行記憶整合")
            return
            
        # 從向量數據庫獲取最近的對話
        try:
            recent_conversations = self.conversation_store.get_all(
                limit=20,
                where={"timestamp": {"$gt": time.time() - 86400}}  # 獲取過去24小時的對話
            )
            
            if not recent_conversations["ids"]:
                logging.info("沒有找到最近24小時的對話記錄，跳過整合")
                return
                
            # 生成摘要並存儲 (異步版本)
            await self._async_generate_and_store_summaries(recent_conversations)
            
            logging.info("異步記憶整合完成")
            
        except Exception as e:
            logging.error(f"異步記憶整合失敗: {e}", exc_info=True)
    
    def _generate_and_store_summaries(self, recent_conversations: Dict[str, Any]):
        """
        生成對話摘要並存儲 (同步版本)
        
        Args:
            recent_conversations: 近期對話數據
        """
        # 提取對話內容
        conversation_texts = recent_conversations["documents"]
        
        # 準備給LLM的提示
        summary_prompt = f"""
        作為{self.persona_name}，請總結以下對話片段的主要內容和重點。
        這些總結將用作你的長期記憶，幫助你記住重要的對話和用戶提及的事情。
        總結應該簡潔但要包含主要事實和見解。
        
        對話片段:
        {conversation_texts[:10]}
        
        請生成一個簡潔的總結:
        """
        
        try:
            # 調用LLM生成摘要
            summary = self.llm.invoke(summary_prompt).content
            
            # 存儲摘要到摘要記憶庫
            self.summary_store.add(
                text=summary,
                metadata={
                    "type": "conversation_summary",
                    "timestamp": time.time(),
                    "source": "recent_conversations",
                    "conversation_count": len(conversation_texts[:10])
                }
            )
            
            logging.info(f"生成並存儲了新的對話摘要: {summary[:50]}...")
            
        except Exception as e:
            logging.error(f"生成摘要失敗: {e}", exc_info=True)
    
    async def _async_generate_and_store_summaries(self, recent_conversations: Dict[str, Any]):
        """
        生成對話摘要並存儲 (異步版本)
        
        Args:
            recent_conversations: 近期對話數據
        """
        # 提取對話內容
        conversation_texts = recent_conversations["documents"]
        
        # 準備給LLM的提示
        summary_prompt = f"""
        作為{self.persona_name}，請總結以下對話片段的主要內容和重點。
        這些總結將用作你的長期記憶，幫助你記住重要的對話和用戶提及的事情。
        總結應該簡潔但要包含主要事實和見解。
        
        對話片段:
        {conversation_texts[:10]}
        
        請生成一個簡潔的總結:
        """
        
        try:
            # 異步調用LLM生成摘要
            summary = await self.llm.ainvoke(summary_prompt)
            summary_text = summary.content
            
            # 存儲摘要到摘要記憶庫
            self.summary_store.add(
                text=summary_text,
                metadata={
                    "type": "conversation_summary",
                    "timestamp": time.time(),
                    "source": "recent_conversations",
                    "conversation_count": len(conversation_texts[:10])
                }
            )
            
            logging.info(f"生成並存儲了新的對話摘要: {summary_text[:50]}...")
            
        except Exception as e:
            logging.error(f"異步生成摘要失敗: {e}", exc_info=True)
    
    def clean_up_old_memories(self, days: int = 30):
        """
        清理舊的或低質量的記憶
        
        Args:
            days: 要清理多少天前的記憶
        """
        # 清理一個月前的普通對話記憶
        days_ago = time.time() - days * 86400  # N天前的時間戳
        
        try:
            # 獲取舊記憶的IDs
            old_conversations = self.conversation_store.get_all(
                where={"timestamp": {"$lt": days_ago}}
            )
            
            if old_conversations["ids"]:
                # 刪除舊對話記憶
                self.conversation_store.delete(ids=old_conversations["ids"])
                logging.info(f"清理了 {len(old_conversations['ids'])} 條舊對話記憶")
        except Exception as e:
            logging.error(f"清理舊記憶失敗: {e}", exc_info=True) 