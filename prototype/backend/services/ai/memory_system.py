import logging
import time
import os
from typing import List, Tuple, Dict, Any
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage

from core.config import settings  # 直接導入 settings
from core.exceptions import AIServiceException # 假設有需要

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemorySystem:
    """專注於記憶儲存、檢索和管理的模組"""

    def __init__(self, embeddings: GoogleGenerativeAIEmbeddings, persona_name: str):
        self.embeddings = embeddings
        self.persona_name = persona_name

        # 初始化向量記憶庫
        self.conversation_memory: Chroma = self._init_vector_store("conversation_memory", "conversations")
        self.persona_memory: Chroma = self._init_vector_store("persona_memory", "persona_info")

        # 初始化角色核心記憶 (如果需要)
        self._initialize_persona_memory()

        # 初始化檢索器
        self.conversation_retriever = self.conversation_memory.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.VECTOR_MEMORY_K,
                "fetch_k": settings.VECTOR_MEMORY_K * 5, # Fetch more initially for MMR
                "lambda_mult": 0.75 # Balance relevance and diversity
            }
        )
        self.persona_retriever = self.persona_memory.as_retriever(
            search_kwargs={"k": 3} # Get top 3 relevant persona facts
        )

        self.memory_last_consolidated = time.time()
        logging.info("記憶系統初始化完成。")

    def _init_vector_store(self, dir_name: str, collection_name: str) -> Chroma:
        """初始化或加載指定的向量存儲"""
        db_path = os.path.join(settings.VECTOR_DB_PATH, dir_name)
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            logging.info(f"創建向量數據庫目錄: {db_path}")
        return Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )

    def _initialize_persona_memory(self):
        """初始化角色核心記憶 - 只在首次運行或數據庫為空時執行"""
        try:
            # 檢查是否已有數據
            if self.persona_memory.get(limit=1)['ids']:
                logging.info("角色記憶已存在，跳過初始化")
                return
        except Exception as e:
             # Chroma 可能在 collection 為空時拋出異常，這裡捕獲並繼續初始化
             logging.warning(f"檢查角色記憶時發生異常 (可能為空): {e}")

        # 添加核心角色信息
        core_memories = [
            f"我的名字是{self.persona_name}，是一名業餘太空網紅，在太空站生活一年。",
            "我喜歡探索太空的奧秘，分享太空生活的點滴。",
            "我的個性活潑開朗，但有時也會因為太空的孤獨而感到寂寞。",
            "我有時會想念地球上的自然環境、美食和親友。",
            "我在太空站做各種日常任務，也會進行一些科學實驗和觀測。"
        ]

        self.persona_memory.add_texts(
            texts=core_memories,
            metadatas=[{"type": "core_identity", "timestamp": time.time()} for _ in core_memories]
        )
        logging.info("角色核心記憶初始化完成")


    async def retrieve_context(self, user_text: str, conversation_history: List[BaseMessage]) -> Tuple[str, str]:
        """
        檢索相關的對話記憶和角色信息。
        Args:
            user_text: 當前用戶輸入。
            conversation_history: 最近的對話歷史列表 (BaseMessage)。
        Returns:
            (格式化後的相關對話記憶, 格式化後的相關角色信息)
        """
        enhanced_query = self._build_enhanced_query(user_text, conversation_history)
        logging.info(f"--- Enhanced Query for Memory Retrieval --- \n{enhanced_query}")

        # 並行執行檢索以提高效率
        relevant_docs_task = self.conversation_retriever.ainvoke(enhanced_query)
        persona_docs_task = self.persona_retriever.ainvoke(user_text) # Persona info is often triggered by direct questions

        relevant_docs, persona_docs = await asyncio.gather(relevant_docs_task, persona_docs_task)

        relevant_memories = self._format_retrieved_memories(relevant_docs)
        persona_info = "\n".join([doc.page_content for doc in persona_docs])

        logging.info(f"--- Relevant Memories Retrieved --- \n{relevant_memories}")
        logging.info(f"--- Persona Info Retrieved --- \n{persona_info}")
        return relevant_memories, persona_info

    def store_conversation_turn(self, user_text: str, ai_response: str):
        """儲存一輪對話到記憶庫。"""
        conversation_entry = f"input: {user_text}\noutput: {ai_response}"
        try:
            self.conversation_memory.add_texts(
                texts=[conversation_entry],
                metadatas=[{
                    "type": "conversation",
                    "timestamp": time.time(),
                    "user_input": user_text, # Add for potential filtering later
                    "ai_response": ai_response
                }]
            )
            # (可選) 檢查並更新角色記憶庫
            self._check_and_update_persona_memory(user_text, ai_response)
            logging.debug("對話輪次已儲存。")
        except Exception as e:
            logging.error(f"儲存對話輪次失敗: {e}", exc_info=True)


    def _build_enhanced_query(self, user_text: str, conversation_history: List[BaseMessage]) -> str:
        """構建增強查詢 - 結合上下文和用戶意圖"""
        query_parts = []

        # 加入最近的對話作為上下文線索
        if conversation_history:
            # 取最後 N 條對話
            recent_turns = conversation_history[-min(3, len(conversation_history)):]
            for msg in recent_turns:
                 prefix = "用戶之前問:" if isinstance(msg, HumanMessage) else f"{self.persona_name}之前回答:"
                 query_parts.append(f"{prefix} {msg.content}")

        # 添加當前問題作為主要焦點
        query_parts.append(f"當前用戶提問: {user_text}")

        # (可選) 提取關鍵詞或主題 - 這裡可以加入更複雜的NLP分析
        # simplified_topics = " ".join(user_text.split()[:5]) # Very basic example
        # query_parts.append(f"可能相關的主題: {simplified_topics}")

        return "\n".join(query_parts) # Use newline for better structure in logs/debugging


    def _format_retrieved_memories(self, docs: List[Document]) -> str:
        """智能格式化記憶，去除冗餘，突出重點"""
        if not docs:
            return "無相關記憶"

        # 基於MMR檢索，理論上重複性已降低，但可以做基礎過濾
        unique_contents = set()
        formatted_memories = []
        for doc in docs:
            content = doc.page_content.strip()
            # 簡單檢查是否已包含類似內容 (忽略空白差異)
            normalized_content = "".join(content.split())
            if normalized_content not in unique_contents:
                 formatted_memories.append(content)
                 unique_contents.add(normalized_content)

        # 返回前 K 個獨特記憶
        return "\n---\n".join(formatted_memories[:settings.VECTOR_MEMORY_K]) # Use separator for clarity

    def _check_and_update_persona_memory(self, user_text: str, ai_response: str):
        """檢查並更新角色記憶（如有新的重要信息） - 簡化版"""
        # 判斷是否包含關於角色的新信息 (可以使用LLM或關鍵詞)
        keywords = ["我是", "我叫", "我的名字", "我的身份是", "我喜歡", "我討厭", "我的感覺是"]
        if any(keyword in ai_response for keyword in keywords) or \
           any(keyword in user_text.lower() for keyword in ["你是", "你叫", "你的名字"]):
            memory_entry = f"關於我 ({self.persona_name}): 當用戶問 '{user_text}', 我回答 '{ai_response}'"
            try:
                # 檢查是否已有非常相似的記憶
                existing = self.persona_memory.similarity_search(memory_entry, k=1)
                if not existing or self._text_similarity(memory_entry, existing[0].page_content) < 0.85:
                    self.persona_memory.add_texts(
                        texts=[memory_entry],
                        metadatas=[{"type": "learned_identity", "timestamp": time.time()}]
                    )
                    logging.info(f"添加新的角色相關記憶: {memory_entry}")
            except Exception as e:
                 logging.error(f"更新角色記憶失敗: {e}", exc_info=True)


    def _text_similarity(self, text1: str, text2: str) -> float:
        """簡單的文本相似度計算 (Jaccard) - 可替換為更精確方法"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

    def consolidate_memories(self):
        """(可選) 定期執行的記憶整合、摘要或清理任務。"""
        # 目前是簡化版本，只記錄調用
        if time.time() - self.memory_last_consolidated > 3600: # 每小時檢查一次
            logging.info("觸發記憶整合檢查...")
            # TODO: 實現更複雜的邏輯, 例如:
            # 1. 獲取最近一段時間的對話
            # 2. 使用 LLM 生成摘要
            # 3. 將摘要存儲到一個特定的 "summary" 記憶庫或添加到 persona_memory
            # 4. (可選) 歸檔或刪除過於陳舊/不重要的對話記憶
            self.memory_last_consolidated = time.time()

# 需要導入 asyncio 才能使用 gather
import asyncio 