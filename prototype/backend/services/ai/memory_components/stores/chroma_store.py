import os
import logging
from typing import List, Dict, Any, Optional, Union

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from .base_store import BaseMemoryStore

class ChromaMemoryStore(BaseMemoryStore):
    """
    基於 ChromaDB 的記憶儲存實現
    """

    def __init__(
        self, 
        embedding_function: Embeddings, 
        persist_directory: str,
        collection_name: str
    ):
        """
        初始化 ChromaDB 記憶儲存
        
        Args:
            embedding_function: 用於將文本轉換為向量的嵌入函數
            persist_directory: 持久化目錄路徑
            collection_name: 集合名稱
        """
        self.embedding_function = embedding_function
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # 確保目錄存在
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            logging.info(f"創建向量數據庫目錄: {persist_directory}")
            
        # 初始化 Chroma 向量存儲
        self.store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_function,
            collection_name=collection_name
        )
        
        # 為不同的檢索方式初始化檢索器
        self.default_retriever = self.store.as_retriever(
            search_kwargs={"k": 3}
        )
        self.mmr_retriever = self.store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 3,
                "fetch_k": 15,
                "lambda_mult": 0.75  # 平衡相關性和多樣性
            }
        )

    def add(self, text: Union[str, List[str]], metadata: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        添加文本到記憶儲存中
        
        Args:
            text: 要儲存的單一文本或文本列表
            metadata: 相應的元數據字典或元數據字典列表
        """
        # 確保 text 和 metadata 都是列表
        if isinstance(text, str):
            text = [text]
        if isinstance(metadata, dict):
            metadata = [metadata]
        
        # 添加到 Chroma
        self.store.add_texts(texts=text, metadatas=metadata)
    
    def retrieve(self, query: str, k: int = 3, use_mmr: bool = False, **kwargs) -> List[Dict[str, Any]]:
        """
        檢索與查詢相關的記憶
        
        Args:
            query: 查詢字串
            k: 要檢索的記憶數量
            use_mmr: 是否使用 MMR 檢索策略 (增加多樣性)
            **kwargs: 額外的檢索參數
            
        Returns:
            檢索結果的列表，每個元素是包含 page_content 和 metadata 的字典
        """
        # 選擇檢索器
        retriever = self.mmr_retriever if use_mmr else self.default_retriever
        
        # 如果傳入自定義 k 值，覆蓋檢索器的配置
        if k is not None and k != 3:
            retriever.search_kwargs["k"] = k
            if use_mmr:
                retriever.search_kwargs["fetch_k"] = k * 5
        
        # 進行檢索
        docs = retriever.invoke(query, **kwargs)
        
        # 將 Document 對象轉換為字典格式
        results = []
        for doc in docs:
            results.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return results
    
    async def aretrieve(self, query: str, k: int = 3, use_mmr: bool = False, **kwargs) -> List[Dict[str, Any]]:
        """
        異步檢索與查詢相關的記憶
        
        Args:
            query: 查詢字串
            k: 要檢索的記憶數量
            use_mmr: 是否使用 MMR 檢索策略 (增加多樣性)
            **kwargs: 額外的檢索參數
            
        Returns:
            檢索結果的列表，每個元素是包含 page_content 和 metadata 的字典
        """
        # 選擇檢索器
        retriever = self.mmr_retriever if use_mmr else self.default_retriever
        
        # 如果傳入自定義 k 值，覆蓋檢索器的配置
        if k is not None and k != 3:
            retriever.search_kwargs["k"] = k
            if use_mmr:
                retriever.search_kwargs["fetch_k"] = k * 5
        
        # 進行異步檢索
        docs = await retriever.ainvoke(query, **kwargs)
        
        # 將 Document 對象轉換為字典格式
        results = []
        for doc in docs:
            results.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return results
    
    def get_all(self, limit: Optional[int] = None, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        獲取儲存中的所有記憶或特定條件的記憶
        
        Args:
            limit: 限制返回的記憶數量
            where: 過濾條件
            
        Returns:
            包含記憶內容和元數據的字典
        """
        kwargs = {}
        if limit is not None:
            kwargs["limit"] = limit
        if where is not None:
            kwargs["where"] = where
            
        return self.store.get(**kwargs)
    
    def delete(self, ids: Union[str, List[str]]) -> None:
        """
        刪除特定 ID 的記憶
        
        Args:
            ids: 要刪除的記憶 ID 或 ID 列表
        """
        self.store.delete(ids=ids)
    
    def is_empty(self) -> bool:
        """
        檢查記憶儲存是否為空
        
        Returns:
            如果記憶儲存為空則返回 True，否則返回 False
        """
        # 嘗試獲取一個記錄來判斷是否為空
        try:
            result = self.store.get(limit=1)
            return len(result["ids"]) == 0
        except Exception:
            # 某些 Chroma 版本可能在集合為空時拋出異常
            return True 