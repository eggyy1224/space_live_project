class InputFilter:
    """
    負責檢測和過濾低質量或問題輸入
    """
    
    def __init__(self, max_problematic_threshold: int = 3):
        """
        初始化輸入過濾器
        
        Args:
            max_problematic_threshold: 連續問題輸入的閾值
        """
        self.problematic_input_count = 0
        self.max_problematic_threshold = max_problematic_threshold
    
    def is_problematic_input(self, text: str) -> bool:
        """
        判斷輸入是否為問題輸入（無意義、亂碼等）
        
        Args:
            text: 要檢查的輸入文本
            
        Returns:
            如果是問題輸入則返回 True，否則返回 False
        """
        # 檢查是否為超短輸入
        if len(text.strip()) <= 2:
            self.problematic_input_count += 1
            return True
            
        # 檢查是否是無意義重複
        weird_patterns = ["DevOps DevOps", "j8 dl4", "dl4", "GPS GPS", "AAA", "三小"]
        for pattern in weird_patterns:
            if pattern in text:
                self.problematic_input_count += 1
                return True
                
        # 檢查是否是重複的單詞模式
        words = text.split()
        if len(words) >= 3:
            for i in range(len(words)-2):
                if words[i] == words[i+1] == words[i+2]:
                    self.problematic_input_count += 1
                    return True
        
        # 如果不是問題輸入，重置計數器
        self.problematic_input_count = 0
        return False
    
    def should_store_input(self, text: str) -> bool:
        """
        判斷輸入是否應該存儲到長期記憶
        
        Args:
            text: 用戶輸入文本
            
        Returns:
            如果應該存儲則返回 True，否則返回 False
        """
        # 如果是問題輸入，不存儲
        if self.is_problematic_input(text):
            return False
            
        # 超短輸入也不存儲 (作為額外檢查)
        if len(text.strip()) < 5:
            return False
            
        return True
    
    def exceeds_threshold(self) -> bool:
        """
        檢查是否超過連續問題輸入閾值
        
        Returns:
            如果超過閾值則返回 True，否則返回 False
        """
        return self.problematic_input_count >= self.max_problematic_threshold
    
    def reset_counter(self) -> None:
        """重置問題輸入計數器"""
        self.problematic_input_count = 0 