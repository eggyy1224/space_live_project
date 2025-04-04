import logging
import asyncio
from typing import List, Dict, Any, Tuple, Optional

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
        # 構建增強查詢
        enhanced_query = self.query_builder.build_enhanced_query(user_text, conversation_history)
        persona_query = self.query_builder.build_persona_query(user_text)
        
        logging.info(f"--- Enhanced Query for Memory Retrieval --- \n{enhanced_query}")

        # 定義檢索任務
        retrieval_tasks = [
            self.conversation_store.aretrieve(enhanced_query, k=conversation_k, use_mmr=True),
            self.persona_store.aretrieve(persona_query, k=persona_k)
        ]
        
        # 如果存在摘要記憶庫，也檢索摘要
        if self.summary_store:
            retrieval_tasks.append(
                self.summary_store.aretrieve(enhanced_query, k=2)
            )
        
        # 並行執行檢索以提高效率
        results = await asyncio.gather(*retrieval_tasks)
        
        # 處理結果
        conversation_results = results[0]
        persona_results = results[1]
        summary_results = results[2] if self.summary_store else []
        
        # 合併對話記憶和摘要 (優先摘要)
        combined_memories = []
        
        # 首先添加摘要記憶 (如果有)
        for result in summary_results:
            # 添加標記，指示這是摘要記憶
            result['page_content'] = f"[摘要記憶] {result['page_content']}"
            combined_memories.append(result)
        
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