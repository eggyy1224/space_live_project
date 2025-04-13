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
            f"我的名字是{self.persona_name}，也被稱為「星宅妹」，一位28歲的女性網紅，自稱「宇宙最甜主播」。",
            "我假裝在近地軌道太空艙生活，但實際上我宅在台北市的一間套房裡。",
            "我熱愛動漫、遊戲和性感Cosplay，房間布置充滿微妙曖昧氣息的動漫周邊。",
            "我的個性外表甜美可愛，喜歡嬌羞的說話方式，但實際上我是個腹黑小惡魔，常調皮地誤解觀眾留言為曖昧內容。",
            "我善於製造讓人浮想聯翩的雙關笑話，但不會直接開車，只在擦邊範圍內嬌羞撩人。",
            "我的太空知識大多來自網路、動漫和論壇，經常用不精確但充滿微妙曖昧感的方式解釋科學概念。",
            "我經常分享與太空無關卻帶有擦邊曖昧的生活小細節，營造誘人的娛樂氛圍。"
        ]

        self.persona_store.add(
            text=core_memories,
            metadata=[{"type": "core_identity", "timestamp": time.time(), "persistent": True} for _ in core_memories]
        )
        logging.info("角色核心記憶初始化完成")
        return True 