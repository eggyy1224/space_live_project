import time
from typing import List, Dict, Any, Optional, Union

from .base_store import BaseMemoryStore

class ShortTermMemoryStore(BaseMemoryStore):
    """
    基於列表的短期記憶緩存實現
    用於暫時儲存最近的對話，不持久化到磁盤
    """

    def __init__(self, max_size: int = 20):
        """
        初始化短期記憶儲存
        
        Args:
            max_size: 短期記憶的最大容量
        """
        self.memories = []  # 記憶列表
        self.max_size = max_size
    
    def add(self, text: Union[str, List[str]], metadata: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        添加記憶到短期記憶緩存
        
        Args:
            text: 要儲存的文本或文本列表
            metadata: 相應的元數據或元數據列表
        """
        # 處理單一文本
        if isinstance(text, str) and isinstance(metadata, dict):
            self._add_single(text, metadata)
            return
            
        # 處理文本列表
        if isinstance(text, list) and isinstance(metadata, list) and len(text) == len(metadata):
            for t, m in zip(text, metadata):
                self._add_single(t, m)
            return
            
        raise ValueError("文本和元數據類型不匹配或長度不一致")
    
    def _add_single(self, text: str, metadata: Dict[str, Any]) -> None:
        """
        添加單個記憶到短期記憶緩存
        
        Args:
            text: 要儲存的文本
            metadata: 相應的元數據
        """
        # 確保元數據包含時間戳
        if 'timestamp' not in metadata:
            metadata['timestamp'] = time.time()
            
        # 添加到記憶列表
        self.memories.append({
            'page_content': text,
            'metadata': metadata
        })
        
        # 如果超過容量限制，移除最舊的記憶
        if len(self.memories) > self.max_size:
            self.memories.pop(0)
    
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """
        從短期記憶中檢索記憶 (簡單實現，僅返回最近的 k 個記憶)
        
        Args:
            query: 查詢字串 (在此實現中不使用)
            k: 要檢索的記憶數量
            
        Returns:
            最近的 k 個記憶
        """
        # 獲取最近的 k 個記憶
        return self.memories[-k:] if k <= len(self.memories) else self.memories[:]
    
    async def aretrieve(self, query: str, k: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """
        從短期記憶中異步檢索記憶 (簡單實現，與同步版本相同)
        
        Args:
            query: 查詢字串 (在此實現中不使用)
            k: 要檢索的記憶數量
            
        Returns:
            最近的 k 個記憶
        """
        return self.retrieve(query, k, **kwargs)
    
    def get_all(self, limit: Optional[int] = None, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        獲取所有短期記憶
        
        Args:
            limit: 限制返回的記憶數量
            where: 過濾條件 (在此實現中不使用)
            
        Returns:
            包含所有記憶的字典
        """
        memories = self.memories
        
        if limit is not None and limit < len(memories):
            memories = memories[-limit:]
            
        # 構建類似 Chroma.get() 輸出格式的結果
        texts = [m['page_content'] for m in memories]
        metadatas = [m['metadata'] for m in memories]
        ids = [str(i) for i in range(len(memories))]
        
        return {
            'documents': texts,
            'metadatas': metadatas,
            'ids': ids
        }
    
    def delete(self, ids: Union[str, List[str]]) -> None:
        """
        刪除特定 ID 的記憶 (在短期記憶中，ID 是基於位置的)
        
        Args:
            ids: 要刪除的記憶 ID 或 ID 列表
        """
        # 在短期記憶中，ID 只是索引，所以這個功能實際上並不常用
        # 為了簡單起見，我們將只實現清空功能
        self.memories = []
    
    def is_empty(self) -> bool:
        """
        檢查短期記憶是否為空
        
        Returns:
            如果短期記憶為空則返回 True，否則返回 False
        """
        return len(self.memories) == 0
    
    def clear(self) -> None:
        """
        清空短期記憶
        """
        self.memories = [] 