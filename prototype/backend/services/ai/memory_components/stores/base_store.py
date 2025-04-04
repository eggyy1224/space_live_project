from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class BaseMemoryStore(ABC):
    """
    記憶儲存的抽象基礎類別
    定義了所有記憶儲存實現應該提供的基本方法
    """

    @abstractmethod
    def add(self, text: Union[str, List[str]], metadata: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        添加一個或多個文檔到記憶儲存中

        Args:
            text: 要儲存的文字內容或文字內容列表
            metadata: 相關的元數據字典或元數據字典列表
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, k: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """
        基於查詢檢索最相關的記憶

        Args:
            query: 搜尋查詢字串
            k: 要檢索的記憶數量
            **kwargs: 額外的檢索參數

        Returns:
            包含檢索結果的字典列表，每個字典包含頁面內容和元數據
        """
        pass

    @abstractmethod
    async def aretrieve(self, query: str, k: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """
        基於查詢異步檢索最相關的記憶

        Args:
            query: 搜尋查詢字串
            k: 要檢索的記憶數量
            **kwargs: 額外的檢索參數

        Returns:
            包含檢索結果的字典列表，每個字典包含頁面內容和元數據
        """
        pass

    @abstractmethod
    def get_all(self, limit: Optional[int] = None, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        獲取儲存中的所有記憶或特定條件的記憶

        Args:
            limit: 限制返回的記憶數量
            where: 過濾條件

        Returns:
            包含記憶內容和元數據的字典
        """
        pass

    @abstractmethod
    def delete(self, ids: Union[str, List[str]]) -> None:
        """
        刪除特定 ID 的記憶

        Args:
            ids: 要刪除的記憶 ID 或 ID 列表
        """
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """
        檢查記憶儲存是否為空

        Returns:
            如果記憶儲存為空則返回 True，否則返回 False
        """
        pass 