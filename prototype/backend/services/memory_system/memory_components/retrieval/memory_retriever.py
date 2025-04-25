import logging
import asyncio
from typing import List, Dict, Any, Tuple, Optional
import time

from langchain_core.messages import BaseMessage

from ..stores import BaseMemoryStore
from .query_builder import QueryBuilder
from .formatter import MemoryFormatter


class MemoryRetriever:
    """
    記憶檢索系統 - 協調記憶儲存、查詢構建和格式化
    """
    
    def __init__(
        self,
        conversation_store: BaseMemoryStore,
        persona_store: BaseMemoryStore,
        summary_store: Optional[BaseMemoryStore] = None,
        persona_name: str = "星際小可愛"
    ):
        """
        初始化記憶檢索器
        
        Args:
            conversation_store: 對話記憶儲存
            persona_store: 角色記憶儲存
            summary_store: 摘要記憶儲存 (可選)
            persona_name: AI角色名稱
        """
        self.conversation_store = conversation_store
        self.persona_store = persona_store
        self.summary_store = summary_store
        
        # 初始化查詢構建器和格式化器
        self.query_builder = QueryBuilder(persona_name=persona_name)
        self.formatter = MemoryFormatter()
        
        self.persona_name = persona_name
    
    async def retrieve_context(
        self,
        user_text: str,
        conversation_history: List[BaseMessage],
        conversation_k: Optional[int] = None,
        persona_k: int = 3
    ) -> Tuple[str, str]:
        """
        檢索相關的對話記憶和角色信息
        
        Args:
            user_text: 當前用戶輸入
            conversation_history: 最近的對話歷史
            conversation_k: 要檢索的對話記憶數量
            persona_k: 要檢索的角色信息數量
            
        Returns:
            (格式化的相關對話記憶, 格式化的相關角色信息)
        """
        # 優化：檢查輸入類型，對簡單問候跳過記憶檢索
        if self._is_simple_greeting(user_text):
            logging.info("檢測到簡單問候，跳過完整記憶檢索")
            # 只檢索角色信息，不檢索對話記憶
            persona_query = self.query_builder.build_persona_query(user_text)
            persona_results = await self.persona_store.aretrieve(persona_query, k=persona_k)
            formatted_persona = self.formatter.format_persona_info(persona_results)
            return "", formatted_persona
        
        # 構建增強查詢
        enhanced_query = self.query_builder.build_enhanced_query(user_text, conversation_history)
        persona_query = self.query_builder.build_persona_query(user_text)
        
        logging.info(f"--- Enhanced Query for Memory Retrieval --- \n{enhanced_query}")

        # 優化：限制檢索範圍，設置最大k值避免檢索過多記憶
        if conversation_k is None:
            conversation_k = 5  # 默認只檢索最近5條記憶
        
        # 定義檢索任務
        retrieval_tasks = [
            # 優化：添加filter參數，只檢索最近的記憶（按時間戳排序）
            self.conversation_store.aretrieve(
                enhanced_query, 
                k=conversation_k, 
                use_mmr=True,
                # 添加過濾器，只檢索最近30天的記憶，減少檢索範圍
                filter={"timestamp": {"$gt": time.time() - 30*24*60*60}}
            ),
            self.persona_store.aretrieve(persona_query, k=persona_k)
        ]
        
        # 優化：移除摘要記憶庫檢索，減少API調用
        # 如果存在摘要記憶庫，也檢索摘要
        # if self.summary_store:
        #     retrieval_tasks.append(
        #         self.summary_store.aretrieve(enhanced_query, k=2)
        #     )
        
        # 並行執行檢索以提高效率
        results = await asyncio.gather(*retrieval_tasks)
        
        # 處理結果
        conversation_results = results[0]
        persona_results = results[1]
        # 優化：移除摘要結果處理
        # summary_results = results[2] if self.summary_store else []
        
        # 合併對話記憶和摘要 (優先摘要)
        combined_memories = []
        
        # 優化：移除摘要記憶處理
        # 首先添加摘要記憶 (如果有)
        # for result in summary_results:
        #     # 添加標記，指示這是摘要記憶
        #     result['page_content'] = f"[摘要記憶] {result['page_content']}"
        #     combined_memories.append(result)
        
        # 然後添加對話記憶，但排除問題輸入
        for result in conversation_results:
            # 檢查是否包含問題內容
            if not self._contains_problematic_content(result['page_content']):
                combined_memories.append(result)
        
        # 格式化記憶和角色信息
        formatted_memories = self.formatter.format_retrieved_memories(combined_memories)
        formatted_persona = self.formatter.format_persona_info(persona_results)
        
        logging.info(f"--- Relevant Memories Retrieved --- \n{formatted_memories}")
        logging.info(f"--- Persona Info Retrieved --- \n{formatted_persona}")
        
        return formatted_memories, formatted_persona
    
    def _is_simple_greeting(self, text: str) -> bool:
        """
        檢查文本是否為簡單問候，可以跳過記憶檢索
        
        Args:
            text: 用戶輸入文本
            
        Returns:
            如果是簡單問候則返回True
        """
        # 轉換為小寫並去除空白
        normalized_text = text.lower().strip()
        
        # 定義簡單問候詞列表
        simple_greetings = [
            "你好", "hello", "hi", "嗨", "哈囉", "早安", "午安", "晚安", 
            "good morning", "good afternoon", "good evening", "嘿", "hey",
            "在嗎", "有人在嗎", "在不在", "還在嗎", "測試", "test"
        ]
        
        # 檢查是否為簡單問候
        for greeting in simple_greetings:
            if greeting in normalized_text:
                return True
                
        # 檢查長度，非常短的輸入也視為簡單問候
        if len(normalized_text) <= 5:
            return True
            
        return False
    
    def _contains_problematic_content(self, content: str) -> bool:
        """
        檢查內容是否包含異常/奇怪/無意義的輸入
        
        Args:
            content: 要檢查的文本內容
            
        Returns:
            如果包含問題內容則返回 True，否則返回 False
        """
        # 檢查是否包含連接無意義的短字串
        weird_patterns = [
            "DevOps DevOps", "j8 dl4", "dl4", "GPS GPS", 
            "AAA", "三小", "哈哈哈哈哈", "毛怪", "點點點"
        ]
        
        # 如果內容中含有這些無意義片段，且不在合理的語境中，就過濾掉
        for pattern in weird_patterns:
            if pattern in content:
                # 排除一些合理的上下文 (例如，講解DevOps是合理的，但連續重複不合理)
                if pattern == "DevOps DevOps" and "開發運維" in content:
                    continue
                return True
                
        return False 