from typing import List, Optional

from langchain_core.messages import BaseMessage, HumanMessage


class QueryBuilder:
    """
    負責構建用於記憶檢索的增強查詢
    """
    
    def __init__(self, persona_name: str = "星際小可愛"):
        """
        初始化查詢構建器
        
        Args:
            persona_name: AI角色的名稱
        """
        self.persona_name = persona_name
    
    def build_enhanced_query(self, user_text: str, conversation_history: Optional[List[BaseMessage]] = None) -> str:
        """
        構建增強查詢 - 結合上下文和用戶意圖
        
        Args:
            user_text: 當前用戶輸入
            conversation_history: 最近的對話歷史
            
        Returns:
            增強的查詢字串
        """
        query_parts = []

        # 如果有對話歷史，添加最近幾輪作為上下文
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

        # 使用換行符連接各部分，讓結構更清晰（便於日誌記錄和調試）
        return "\n".join(query_parts)
        
    def build_persona_query(self, user_text: str) -> str:
        """
        構建用於檢索角色信息的查詢
        
        Args:
            user_text: 用戶輸入
            
        Returns:
            針對角色信息的查詢
        """
        # 從用戶輸入中提取可能與角色相關的關鍵詞
        persona_keywords = [
            "你是誰", "你的名字", "你叫什麼", "你的背景",
            "你喜歡", "你討厭", "你的個性", "你的感覺",
            "你為什麼", "你能做什麼", "你的工作"
        ]
        
        # 檢查用戶輸入是否包含角色相關關鍵詞
        contains_persona_keyword = any(keyword in user_text for keyword in persona_keywords)
        
        # 如果包含角色關鍵詞，直接返回用戶輸入
        if contains_persona_keyword:
            return user_text
            
        # 否則，構建基本查詢
        return f"{user_text} 關於{self.persona_name}" 