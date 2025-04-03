import logging
import time
import os
import asyncio
from typing import List, Tuple, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import settings  # 直接導入 settings
from core.exceptions import AIServiceException # 假設有需要

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemorySystem:
    """
    專注於記憶儲存、檢索和管理的模組
    增強版: 分層記憶架構、更智慧的過濾和整合能力
    """

    def __init__(self, embeddings: GoogleGenerativeAIEmbeddings, persona_name: str, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.embeddings = embeddings
        self.persona_name = persona_name
        self.llm = llm  # 用於記憶整合和摘要，可選

        # 初始化向量記憶庫
        self.conversation_memory: Chroma = self._init_vector_store("conversation_memory", "conversations")
        self.persona_memory: Chroma = self._init_vector_store("persona_memory", "persona_info")
        # 新增: 摘要記憶庫
        self.summary_memory: Chroma = self._init_vector_store("summary_memory", "conversation_summaries")

        # 初始化角色核心記憶 (如果需要)
        self._initialize_persona_memory()

        # 初始化檢索器 - 使用更高級的檢索參數
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
        
        # 新增: 摘要檢索器
        self.summary_retriever = self.summary_memory.as_retriever(
            search_kwargs={"k": 2} # 獲取前2個相關摘要
        )

        # 記憶整合時間戳
        self.memory_last_consolidated = time.time()
        
        # 短期記憶緩存 - 用於存儲最近的對話，但不一定會持久化
        self.short_term_memory = []  # 最近的對話輪次
        self.max_short_term_memory = 20  # 最大短期記憶數量
        
        # 記憶整合鎖 - 防止多個整合任務同時運行
        self.consolidation_lock = asyncio.Lock()
        
        # 問題輸入計數器 - 連續偵測到多少次問題輸入
        self.problematic_input_count = 0
        self.max_problematic_threshold = 3  # 達到閾值後觸發特殊處理
        
        logging.info("增強版記憶系統初始化完成")

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
            metadatas=[{"type": "core_identity", "timestamp": time.time(), "persistent": True} for _ in core_memories]
        )
        logging.info("角色核心記憶初始化完成")


    async def retrieve_context(self, user_text: str, conversation_history: List[BaseMessage], k: int = None) -> Tuple[str, str]:
        """
        檢索相關的對話記憶和角色信息。
        Args:
            user_text: The current user input.
            conversation_history: Recent conversation history list (BaseMessage).
            k: Optional override for number of memories to retrieve. 
        Returns:
            (formatted relevant conversation memories, formatted relevant persona info)
        """
        enhanced_query = self._build_enhanced_query(user_text, conversation_history)
        logging.info(f"--- Enhanced Query for Memory Retrieval --- \n{enhanced_query}")

        # 並行執行檢索以提高效率
        retrieval_tasks = [
            self.conversation_retriever.ainvoke(enhanced_query),
            self.persona_retriever.ainvoke(user_text),  # Persona info is often triggered by direct questions
            self.summary_retriever.ainvoke(enhanced_query)  # 新增: 檢索相關摘要
        ]
        
        results = await asyncio.gather(*retrieval_tasks)
        relevant_docs, persona_docs, summary_docs = results

        # 如果提供了自定義的k值，限制結果數量
        if k is not None:
            relevant_docs = relevant_docs[:k]
        
        # 合併對話記憶和摘要 (摘要優先)
        combined_memories = []
        
        # 首先添加摘要 (如果有)
        if summary_docs:
            for doc in summary_docs:
                combined_memories.append(f"[摘要記憶] {doc.page_content}")
        
        # 然後添加具體對話記憶
        for doc in relevant_docs:
            # 檢查記憶是否包含奇怪/無意義的輸入
            if not self._contains_problematic_content(doc.page_content):
                combined_memories.append(doc.page_content)
        
        # 格式化記憶
        relevant_memories = self._format_retrieved_memories(combined_memories)
        persona_info = "\n".join([doc.page_content for doc in persona_docs])

        logging.info(f"--- Relevant Memories Retrieved --- \n{relevant_memories}")
        logging.info(f"--- Persona Info Retrieved --- \n{persona_info}")
        return relevant_memories, persona_info
    
    def _contains_problematic_content(self, content: str) -> bool:
        """檢查內容是否包含異常/奇怪/無意義的輸入"""
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

    def store_conversation_turn(self, user_text: str, ai_response: str):
        """儲存一輪對話到記憶庫。"""
        # 先加入短期記憶
        self.short_term_memory.append({
            "user_input": user_text,
            "ai_response": ai_response,
            "timestamp": time.time()
        })
        
        # 限制短期記憶大小
        if len(self.short_term_memory) > self.max_short_term_memory:
            self.short_term_memory.pop(0)  # 移除最舊的記憶
        
        # 檢查是否為問題輸入，如果是，增加計數器但不寫入長期記憶
        if self._is_problematic_input(user_text):
            self.problematic_input_count += 1
            logging.warning(f"檢測到問題輸入，不儲存到長期記憶。計數: {self.problematic_input_count}")
            return
        else:
            # 重置計數器
            self.problematic_input_count = 0
        
        # 寫入長期向量記憶
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
            # 檢查並更新角色記憶庫
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

        # 提取關鍵詞或主題 - 使用簡單方法
        words = [w for w in user_text.split() if len(w) > 1]
        if words:
            query_parts.append(f"相關關鍵詞: {' '.join(words[:5])}")

        return "\n".join(query_parts) # Use newline for better structure in logs/debugging


    def _format_retrieved_memories(self, memory_contents: List[str]) -> str:
        """智能格式化記憶，去除冗餘，突出重點"""
        if not memory_contents:
            return "無相關記憶"

        # 基於MMR檢索，理論上重複性已降低，但可以做基礎過濾
        unique_contents = set()
        formatted_memories = []
        
        for content in memory_contents:
            normalized_content = "".join(content.split())
            if normalized_content not in unique_contents:
                formatted_memories.append(content)
                unique_contents.add(normalized_content)

        # 返回前 K 個獨特記憶
        memory_limit = min(len(formatted_memories), settings.VECTOR_MEMORY_K)
        return "\n---\n".join(formatted_memories[:memory_limit]) # Use separator for clarity

    def _check_and_update_persona_memory(self, user_text: str, ai_response: str):
        """檢查並更新角色記憶（如有新的重要信息）- 增強版"""
        # 判斷是否包含關於角色的新信息
        keywords = ["我是", "我叫", "我的名字", "我的身份", "我喜歡", "我討厭", "我的感覺"]
        user_questions = ["你是", "你叫", "你的名字", "你喜歡", "你討厭", "你的感覺", "你為什麼"]
        
        should_update = False
        
        # 檢查AI回應是否包含關於自己的陳述
        if any(keyword in ai_response for keyword in keywords):
            should_update = True
            
        # 檢查用戶是否詢問關於角色的問題
        if any(question in user_text.lower() for question in user_questions):
            should_update = True
            
        if should_update:
            memory_entry = f"關於{self.persona_name}: 當用戶問 '{user_text}', 回答 '{ai_response}'"
            
            try:
                # 檢查是否已有非常相似的記憶
                existing = self.persona_memory.similarity_search(memory_entry, k=1)
                if not existing or self._text_similarity(memory_entry, existing[0].page_content) < 0.85:
                    # 添加額外的元數據標記這是學習到的信息
                    self.persona_memory.add_texts(
                        texts=[memory_entry],
                        metadatas=[{
                            "type": "learned_identity", 
                            "timestamp": time.time(),
                            "user_question": user_text,
                            "persistent": True  # 標記為持久記憶
                        }]
                    )
                    logging.info(f"添加新的角色相關記憶: {memory_entry[:50]}...")
            except Exception as e:
                 logging.error(f"更新角色記憶失敗: {e}", exc_info=True)

    def _is_problematic_input(self, text: str) -> bool:
        """判斷輸入是否為問題輸入（無意義、亂碼等）"""
        # 檢查是否為超短輸入
        if len(text.strip()) <= 2:
            return True
            
        # 檢查是否是無意義重複
        weird_patterns = ["DevOps DevOps", "j8 dl4", "dl4", "GPS GPS", "AAA", "三小"]
        for pattern in weird_patterns:
            if pattern in text:
                return True
                
        # 檢查是否是重複的單詞模式
        words = text.split()
        if len(words) >= 3:
            for i in range(len(words)-2):
                if words[i] == words[i+1] == words[i+2]:
                    return True
                    
        return False

    def _text_similarity(self, text1: str, text2: str) -> float:
        """簡單的文本相似度計算 (Jaccard)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

    def consolidate_memories(self):
        """觸發記憶整合任務 (同步版本)"""
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
        """異步執行記憶整合"""
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
        """執行實際的記憶整合 (同步版本)"""
        if not self.llm:
            logging.warning("沒有提供LLM，無法執行記憶整合")
            return
            
        # 實現記憶整合邏輯
        # 1. 獲取最近的短期記憶
        if len(self.short_term_memory) < 3:
            logging.info("短期記憶不足，跳過整合")
            return
            
        # 從向量數據庫獲取最近的對話，而不僅僅使用短期記憶
        try:
            recent_conversations = self.conversation_memory.get(
                limit=20,
                where={"timestamp": {"$gt": time.time() - 86400}}  # 獲取過去24小時的對話
            )
            
            if not recent_conversations["ids"]:
                logging.info("沒有找到最近24小時的對話記錄，跳過整合")
                return
                
            # 生成摘要並存儲
            self._generate_and_store_summaries(recent_conversations)
            
            # 清理舊的或低質量的記憶（可選）
            # self._clean_up_old_memories()
            
            logging.info("記憶整合完成")
            
        except Exception as e:
            logging.error(f"記憶整合失敗: {e}", exc_info=True)
            
    async def _async_perform_memory_consolidation(self):
        """執行實際的記憶整合 (異步版本)"""
        if not self.llm:
            logging.warning("沒有提供LLM，無法執行記憶整合")
            return
            
        # 從向量數據庫獲取最近的對話
        try:
            recent_conversations = self.conversation_memory.get(
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
            
    def _generate_and_store_summaries(self, recent_conversations):
        """生成對話摘要並存儲 (同步版本)"""
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
            self.summary_memory.add_texts(
                texts=[summary],
                metadatas=[{
                    "type": "conversation_summary",
                    "timestamp": time.time(),
                    "source": "recent_conversations",
                    "conversation_count": len(conversation_texts[:10])
                }]
            )
            
            logging.info(f"生成並存儲了新的對話摘要: {summary[:50]}...")
            
        except Exception as e:
            logging.error(f"生成摘要失敗: {e}", exc_info=True)
            
    async def _async_generate_and_store_summaries(self, recent_conversations):
        """生成對話摘要並存儲 (異步版本)"""
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
            self.summary_memory.add_texts(
                texts=[summary_text],
                metadatas=[{
                    "type": "conversation_summary",
                    "timestamp": time.time(),
                    "source": "recent_conversations",
                    "conversation_count": len(conversation_texts[:10])
                }]
            )
            
            logging.info(f"生成並存儲了新的對話摘要: {summary_text[:50]}...")
            
        except Exception as e:
            logging.error(f"異步生成摘要失敗: {e}", exc_info=True)
            
    def _clean_up_old_memories(self):
        """清理舊的或低質量的記憶 (謹慎使用)"""
        # 保留所有角色核心記憶
        # 清理一個月前的普通對話記憶
        one_month_ago = time.time() - 30 * 86400  # 30天前的時間戳
        
        try:
            # 獲取舊記憶的IDs
            old_conversations = self.conversation_memory.get(
                where={"timestamp": {"$lt": one_month_ago}}
            )
            
            if old_conversations["ids"]:
                # 刪除舊對話記憶
                self.conversation_memory.delete(ids=old_conversations["ids"])
                logging.info(f"清理了 {len(old_conversations['ids'])} 條舊對話記憶")
        except Exception as e:
            logging.error(f"清理舊記憶失敗: {e}", exc_info=True) 