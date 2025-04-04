"""
處理用戶輸入的相關節點和邏輯。
提供輸入預處理、分類、重複檢測等功能。
"""

import logging
import re
import asyncio
from typing import Dict, List, Any, TypedDict, Optional

from langchain_core.messages import BaseMessage, HumanMessage

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 存放最近的用戶輸入 (在模組層級維護，以供不同的對話圖實例共享)
_recent_user_inputs = []
_max_recent_inputs = 10

async def preprocess_input_node(state: TypedDict) -> Dict[str, Any]:
    """輸入預處理節點 - 分析和處理用戶輸入"""
    user_text = state["raw_user_input"]
    messages = state["messages"]
    
    # 基本清理
    cleaned_text = user_text.strip()
    
    # 輸入分類邏輯
    input_classification = await classify_input(cleaned_text, messages)
    
    # 更新最近輸入列表
    update_recent_inputs(cleaned_text)
    
    logging.info(f"輸入分類結果: {input_classification}")
    
    # 決定是否進一步處理輸入
    processed_input = cleaned_text
    if input_classification["type"] in ["gibberish", "highly_repetitive"]:
        # 對於亂碼和高度重複的輸入，可以添加標記或特殊處理
        logging.warning(f"檢測到問題輸入: {input_classification['type']}")
    
    return {
        "processed_user_input": processed_input,
        "input_classification": input_classification,
        "error_count": 0,  # 初始化錯誤計數
        "system_alert": None  # 初始化系統警告
    }

async def classify_input(text: str, messages: List[BaseMessage]) -> Dict[str, Any]:
    """分類用戶輸入 - 識別重複、亂碼、情緒等"""
    result = {
        "type": "normal",
        "sentiment": "neutral",
        "repetition_level": 0,
        "complexity": "medium"
    }
    
    # 檢查輸入是否過短
    if len(text.strip()) <= 2:
        result["type"] = "very_short"
        result["complexity"] = "low"
        return result
    
    # 檢查文本是否看起來像「亂碼」
    gibberish_patterns = [
        r"^[a-zA-Z0-9]{1,3}$",  # 1-3個字母或數字
        r"^[^\w\s]+$",           # 只含特殊字符
    ]
    for pattern in gibberish_patterns:
        if re.match(pattern, text.strip()):
            result["type"] = "gibberish"
            return result
    
    # 檢查重複度
    repetition_level = check_repetition(text)
    result["repetition_level"] = repetition_level
    if repetition_level > 0.8:
        result["type"] = "highly_repetitive"
    elif repetition_level > 0.5:
        result["type"] = "moderately_repetitive"
    
    # 簡單情感分析
    negative_words = ["不", "沒", "討厭", "煩", "不要", "別", "滾", "笨", "蠢", "白痴", "智障"]
    positive_words = ["喜歡", "愛", "好", "棒", "讚", "謝謝", "感謝", "開心", "快樂"]
    
    negative_count = sum(1 for word in negative_words if word in text)
    positive_count = sum(1 for word in positive_words if word in text)
    
    if negative_count > positive_count:
        result["sentiment"] = "negative"
    elif positive_count > negative_count:
        result["sentiment"] = "positive"
    
    # 檢測問題
    if "?" in text or "？" in text or text.startswith(("什麼", "為什麼", "怎麼", "如何", "何時", "誰", "哪")):
        result["type"] = "question"
    
    return result

def check_repetition(text: str) -> float:
    """檢查與先前輸入的重複度"""
    global _recent_user_inputs
    
    if not _recent_user_inputs:
        return 0.0
    
    # 檢查是否與先前輸入完全相同
    for prev_input in _recent_user_inputs:
        if text == prev_input:
            return 1.0
    
    # 檢查部分重複
    for prev_input in _recent_user_inputs:
        common_length = len(set(text).intersection(set(prev_input)))
        if common_length > 0:
            similarity = common_length / max(len(set(text)), len(set(prev_input)))
            if similarity > 0.7:  # 如果有70%以上相同字符
                return similarity
    
    return 0.0

def update_recent_inputs(text: str):
    """更新最近輸入列表"""
    global _recent_user_inputs, _max_recent_inputs
    
    _recent_user_inputs.insert(0, text)
    if len(_recent_user_inputs) > _max_recent_inputs:
        _recent_user_inputs.pop()

def reset_recent_inputs():
    """重置最近輸入列表，供測試或重置使用"""
    global _recent_user_inputs
    _recent_user_inputs = [] 