from typing import List, Dict, Any


class MemoryFormatter:
    """
    負責將檢索到的記憶格式化為適合模型使用的輸出
    """
    
    def __init__(self):
        """
        初始化記憶格式化器
        """
        pass
    
    def format_retrieved_memories(self, memory_results: List[Dict[str, Any]], max_memories: int = None) -> str:
        """
        智能格式化檢索到的記憶
        
        Args:
            memory_results: 檢索結果列表，每個元素是包含 page_content 和 metadata 的字典
            max_memories: 要保留的最大記憶數量
            
        Returns:
            格式化後的記憶字串
        """
        if not memory_results:
            return "無相關記憶"
        
        # 從結果中提取文本內容
        memory_contents = [result['page_content'] for result in memory_results]
        
        # 對記憶去重
        unique_contents = set()
        formatted_memories = []
        
        for content in memory_contents:
            # 標準化內容以便比較 (去除空格)
            normalized_content = "".join(content.split())
            if normalized_content not in unique_contents:
                formatted_memories.append(content)
                unique_contents.add(normalized_content)
        
        # 如果設置了最大記憶數量，應用限制
        if max_memories is not None and len(formatted_memories) > max_memories:
            formatted_memories = formatted_memories[:max_memories]
        
        # 使用分隔符連接記憶，使其更易於閱讀
        return "\n---\n".join(formatted_memories)
    
    def format_persona_info(self, persona_results: List[Dict[str, Any]]) -> str:
        """
        格式化檢索到的角色信息
        
        Args:
            persona_results: 角色信息檢索結果
            
        Returns:
            格式化後的角色信息字串
        """
        if not persona_results:
            return ""
        
        # 提取角色信息內容
        persona_contents = [result['page_content'] for result in persona_results]
        
        # 對不同類型的角色信息進行分類和組織
        core_identity = []
        learned_info = []
        
        for idx, content in enumerate(persona_contents):
            if idx < len(persona_results) and 'metadata' in persona_results[idx]:
                metadata = persona_results[idx]['metadata']
                if metadata.get('type') == 'core_identity':
                    core_identity.append(content)
                else:
                    learned_info.append(content)
        
        # 構建格式化輸出
        formatted_parts = []
        
        # 核心身份信息放在最前面
        if core_identity:
            formatted_parts.append("【核心身份】")
            formatted_parts.append("\n".join(core_identity))
        
        # 學習到的信息
        if learned_info:
            if formatted_parts:  # 如果已經有核心身份，加個分隔
                formatted_parts.append("\n")
            formatted_parts.append("【學習到的信息】")
            formatted_parts.append("\n".join(learned_info))
        
        return "\n".join(formatted_parts) 