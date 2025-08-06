import logging
import time
import os
import asyncio
import uuid
from datetime import datetime
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
        self.chat_memory_store = self._init_memory_store("chat_memory", "youtube_chat_messages")
        self.short_term_store = ShortTermMemoryStore(max_size=20)
        
        # 初始化記憶處理組件
        self.input_filter = InputFilter(max_problematic_threshold=3)
        self.persona_updater = PersonaUpdater(self.persona_store, persona_name)
        self.summarizer = ConversationSummarizer(
            conversation_store=self.conversation_store,
            summary_store=self.summary_store,
            llm=llm,
            persona_name=persona_name
        )
        
        # 初始化記憶檢索組件
        self.memory_retriever = MemoryRetriever(
            conversation_store=self.conversation_store,
            persona_store=self.persona_store,
            summary_store=self.summary_store,
            persona_name=persona_name
        )
        
        logging.info(f"記憶系統初始化完成，角色名稱: {persona_name}")

    def _enrich_metadata(self, memory_type: str, content: str, source: str = "memory_system", additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        豐富記憶的metadata，自動添加系統級資訊
        
        Args:
            memory_type: 記憶類型
            content: 記憶內容
            source: 記憶來源
            additional_metadata: 額外的metadata
            
        Returns:
            豐富的metadata字典
        """
        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        
        # 基礎系統metadata
        enriched_metadata = {
            # 時間相關
            "timestamp": current_time,
            "datetime": current_datetime.isoformat(),
            "date": current_datetime.strftime("%Y-%m-%d"),
            "time": current_datetime.strftime("%H:%M:%S"),
            "weekday": current_datetime.strftime("%A"),
            
            # 記憶相關
            "memory_type": memory_type,
            "memory_id": str(uuid.uuid4()),
            "content_length": len(content),
            "word_count": len(content.split()) if content else 0,
            
            # 系統相關
            "source": source,
            "version": "1.0",
            "persona_name": self.persona_name
        }
        
        # 根據記憶類型添加特定metadata
        if memory_type == "conversation":
            enriched_metadata.update({
                "interaction_type": "dialogue_turn",
                "is_dialogue": True
            })
        elif memory_type == "persona":
            enriched_metadata.update({
                "persona_category": "system_learned",
                "is_personality_trait": True
            })
        elif memory_type == "summary":
            enriched_metadata.update({
                "summary_type": "auto_generated",
                "is_summary": True
            })
        elif memory_type == "chat_message":
            enriched_metadata.update({
                "interaction_type": "youtube_chat",
                "is_audience_message": True,
                "platform": "youtube"
            })
        
        # 合併額外的metadata
        if additional_metadata:
            for key, value in additional_metadata.items():
                # 保護重要的系統字段不被覆蓋
                if key not in {"timestamp", "datetime", "memory_id", "memory_type", "source"}:
                    enriched_metadata[key] = value
                else:
                    enriched_metadata[f"user_{key}"] = value
        
        return enriched_metadata

    def _init_memory_store(self, dir_name: str, collection_name: str) -> ChromaMemoryStore:
        """
        初始化記憶儲存
        
        Args:
            dir_name: 目錄名稱
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
        conversation_content = f"input: {user_text}\noutput: {ai_response}"
        
        # 準備基礎對話metadata
        base_metadata = {
            "type": "conversation",
            "user_input": user_text,
            "ai_response": ai_response
        }
        
        # 先加入短期記憶（使用豐富的metadata）
        short_term_metadata = self._enrich_metadata(
            memory_type="conversation",
            content=conversation_content,
            source="short_term_memory",
            additional_metadata=base_metadata
        )
        
        self.short_term_store.add(
            text=conversation_content,
            metadata=short_term_metadata
        )
        
        # 檢查是否為問題輸入，如果是，不寫入長期記憶
        if not self.input_filter.should_store_input(user_text):
            logging.warning(f"檢測到問題輸入，不儲存到長期記憶。計數: {self.input_filter.problematic_input_count}")
            return
        
        # 寫入長期向量記憶（使用豐富的metadata）
        try:
            long_term_metadata = self._enrich_metadata(
                memory_type="conversation",
                content=conversation_content,
                source="long_term_memory",
                additional_metadata=base_metadata
            )
            
            self.conversation_store.add(
                text=conversation_content,
                metadata=long_term_metadata
            )
            
            # 檢查並更新角色記憶
            self.persona_updater.check_and_update_persona_memory(user_text, ai_response)
            
            # 觸發記憶整合 (這是異步操作，不阻塞主流程)
            self.summarizer.consolidate_memories()
            
            logging.debug(f"對話輪次已儲存，記憶ID: {long_term_metadata['memory_id']}")
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
    
    def store_chat_message(self, message_data: dict):
        """
        儲存 YouTube 聊天室留言到記憶庫
        
        Args:
            message_data: 聊天室留言資料，包含 author, message, timestamp 等
        """
        try:
            author = message_data.get("author", "觀眾")
            message_text = message_data.get("message", "")
            timestamp = message_data.get("timestamp", "")
            datetime_str = message_data.get("datetime", "")
            
            # 過濾掉空訊息或太短的訊息
            if not message_text.strip() or len(message_text.strip()) < 2:
                logging.debug(f"聊天室留言太短，跳過儲存: '{message_text}'")
                return
            
            # 構造留言內容
            chat_content = f"[YouTube 觀眾 {author}]: {message_text}"
            
            # 準備聊天室留言的基礎metadata
            base_metadata = {
                "type": "chat_message",
                "author": author,
                "message": message_text,
                "original_timestamp": timestamp,
                "chat_datetime": datetime_str,
                "message_type": message_data.get("message_type", "textMessage"),
                "is_verified": message_data.get("is_verified", False),
                "is_owner": message_data.get("is_owner", False),
                "is_sponsor": message_data.get("is_sponsor", False),
                "is_moderator": message_data.get("is_moderator", False),
                "author_channel_id": message_data.get("author_channel_id", ""),
                "platform": "youtube",
                "chat_source": "live_stream"
            }
            
            # 豐富化metadata
            enriched_metadata = self._enrich_metadata(
                memory_type="chat_message",
                content=chat_content,
                source="youtube_chat_monitor",
                additional_metadata=base_metadata
            )
            
            # 儲存到聊天室記憶存儲
            self.chat_memory_store.add(
                text=chat_content,
                metadata=enriched_metadata
            )
            
            logging.info(f"成功儲存聊天室留言到記憶庫: {author} - {message_text[:50]}...")
            
        except Exception as e:
            logging.error(f"儲存聊天室留言失敗: {e}", exc_info=True)
    
    def retrieve_chat_memories(self, query: str, k: int = 5, author_filter: str = None) -> List[Dict[str, Any]]:
        """
        檢索聊天室留言記憶
        
        Args:
            query: 搜尋查詢
            k: 檢索數量
            author_filter: 可選的作者過濾器
            
        Returns:
            檢索到的聊天室留言記憶列表
        """
        try:
            results = self.chat_memory_store.retrieve(query=query, k=k)
            
            # 如果有作者過濾器，進一步過濾結果
            if author_filter:
                filtered_results = []
                for result in results:
                    metadata = result.get("metadata", {})
                    if metadata.get("author", "").lower() == author_filter.lower():
                        filtered_results.append(result)
                results = filtered_results
            
            return results
            
        except Exception as e:
            logging.error(f"檢索聊天室留言記憶失敗: {e}", exc_info=True)
            return []
    
    def get_recent_chat_messages(self, limit: int = 20, author_filter: str = None) -> List[Dict[str, Any]]:
        """
        獲取最近的聊天室留言
        
        Args:
            limit: 限制數量
            author_filter: 可選的作者過濾器
            
        Returns:
            最近的聊天室留言列表
        """
        try:
            # 使用 where 條件過濾聊天室留言
            where_conditions = {"memory_type": "chat_message"}
            if author_filter:
                where_conditions["author"] = author_filter
            
            results = self.chat_memory_store.get_all(limit=limit, where=where_conditions)
            
            if results and "metadatas" in results:
                # 按時間戳排序，最新的在前
                chat_messages = []
                contents = results.get("documents", [])
                metadatas = results.get("metadatas", [])
                
                for content, metadata in zip(contents, metadatas):
                    chat_messages.append({
                        "page_content": content,
                        "metadata": metadata
                    })
                
                # 按時間戳排序
                chat_messages.sort(
                    key=lambda x: x["metadata"].get("timestamp", 0), 
                    reverse=True
                )
                
                return chat_messages[:limit]
            
            return []
            
        except Exception as e:
            logging.error(f"獲取最近聊天室留言失敗: {e}", exc_info=True)
            return []
    
    def clean_up_old_memories(self, days: int = 30):
        """
        清理舊的記憶 - 為了保持向後兼容而保留的方法
        
        Args:
            days: 清理多少天前的記憶
        """
        self.summarizer.clean_up_old_memories(days) 