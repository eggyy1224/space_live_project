import logging
import time
from typing import Dict, Any

from ..stores import BaseMemoryStore

class PersonaUpdater:
    """
    負責在對話中檢測並更新角色記憶
    """
    
    def __init__(self, persona_store: BaseMemoryStore, persona_name: str = "星際小可愛"):
        """
        初始化角色記憶更新器
        
        Args:
            persona_store: 角色記憶儲存
            persona_name: AI角色名稱
        """
        self.persona_store = persona_store
        self.persona_name = persona_name
    
    def check_and_update_persona_memory(self, user_text: str, ai_response: str) -> bool:
        """
        檢查並更新角色記憶（如有新的重要信息）
        
        Args:
            user_text: 用戶輸入
            ai_response: AI回應
            
        Returns:
            如果更新了角色記憶則返回 True，否則返回 False
        """
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
                existing = self.persona_store.retrieve(memory_entry, k=1)
                if not existing or self._text_similarity(memory_entry, existing[0]['page_content']) < 0.85:
                    # 添加額外的元數據標記這是學習到的信息
                    self.persona_store.add(
                        text=memory_entry,
                        metadata={
                            "type": "learned_identity", 
                            "timestamp": time.time(),
                            "user_question": user_text,
                            "persistent": True  # 標記為持久記憶
                        }
                    )
                    logging.info(f"添加新的角色相關記憶: {memory_entry[:50]}...")
                    return True
            except Exception as e:
                 logging.error(f"更新角色記憶失敗: {e}", exc_info=True)
        
        return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        簡單的文本相似度計算 (Jaccard)
        
        Args:
            text1: 第一個文本
            text2: 第二個文本
            
        Returns:
            兩個文本的相似度分數 (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0
    
    def initialize_core_persona_memory(self) -> bool:
        """
        初始化角色核心記憶 - 只在首次運行或數據庫為空時執行
        
        Returns:
            如果執行了初始化則返回 True，否則返回 False
        """
        try:
            # 檢查是否已有數據
            if not self.persona_store.is_empty():
                logging.info("角色記憶已存在，跳過初始化")
                return False
        except Exception as e:
             # 可能在 collection 為空時拋出異常，這裡捕獲並繼續初始化
             logging.warning(f"檢查角色記憶時發生異常 (可能為空): {e}")

        # 添加核心角色信息
        core_memories = [
            f"我的名字是{self.persona_name}，是一名業餘太空網紅，在太空站生活一年。",
            "我喜歡探索太空的奧秘，分享太空生活的點滴。",
            "我的個性活潑開朗，但有時也會因為太空的孤獨而感到寂寞。",
            "我有時會想念地球上的自然環境、美食和親友。",
            "我在太空站做各種日常任務，也會進行一些科學實驗和觀測。"
        ]

        self.persona_store.add(
            text=core_memories,
            metadata=[{"type": "core_identity", "timestamp": time.time(), "persistent": True} for _ in core_memories]
        )
        logging.info("角色核心記憶初始化完成")
        return True 