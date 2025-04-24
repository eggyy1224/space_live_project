"""
Utility functions for MurmurService.

This module contains helper functions for the murmur service, including text processing and similarity checking.
"""

import re
from typing import List, Set

from . import config

def clean_murmur_prefix(text: str) -> str:
    """
    清理文本中的輕聲自語前綴，但保留連續性標記。
    
    Args:
        text: 原始murmur文本
        
    Returns:
        清理後的文本
    """
    patterns = [
        r"^\s*\(輕聲自語\)\s*",
        r"^\s*（輕聲自語）\s*",
        r"^\s*\(自言自語\)\s*",
        r"^\s*（自言自語）\s*",
        r"^\s*\(喃喃自語\)\s*", 
        r"^\s*（喃喃自語）\s*",
        r"^\s*\(murmur\)\s*",
        r"^\s*（murmur）\s*",
        r"^\s*\(murmuring\)\s*",
        r"^\s*（murmuring）\s*"
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # 保留連接詞，但移除多餘空格
    for marker in config.CONTINUITY_MARKERS:
        if text.startswith(marker):
            # 保留標記但格式化為「標記，」的格式
            text = re.sub(f"^\s*{marker}\s*", f"{marker}，", text)
            break
    
    return text

def is_murmur_too_similar(new_murmur: str, existing_murmurs: Set[str], threshold: float = config.MURMUR_SIMILARITY_THRESHOLD) -> bool:
    """
    檢查新的murmur是否與現有murmur太相似。
    
    Args:
        new_murmur: 新生成的murmur文本
        existing_murmurs: 現有的murmur文本集合
        threshold: 相似度閾值，超過此值視為太相似
        
    Returns:
        如果太相似返回True，否則返回False
    """
    # 如果完全相同，直接拒絕
    if new_murmur in existing_murmurs:
        return True
    
    # 只檢查最近的3個murmur，而不是全部
    recent_list = list(existing_murmurs)[-3:] if len(existing_murmurs) > 3 else existing_murmurs
    
    # 檢查與最近的murmur的相似度
    for existing_murmur in recent_list:
        # 簡化的相似度檢測，只檢查包含關係
        if (new_murmur in existing_murmur or existing_murmur in new_murmur):
            return True
        
    return False

def calculate_similarity_threshold(thinking_thread_continuity: int, has_continuity_marker: bool) -> float:
    """
    根據思考連貫性情況計算相似度閾值。
    
    Args:
        thinking_thread_continuity: 已經連續的思考次數
        has_continuity_marker: 是否包含連續性標記
        
    Returns:
        計算後的相似度閾值
    """
    if thinking_thread_continuity > 0:
        # 使用連續模式的閾值
        similarity_threshold = config.SIMILARITY_THRESHOLD_CONTINUOUS
        # 如果包含連續性標記，進一步降低相似度要求
        if has_continuity_marker:
            similarity_threshold *= 0.8
    else:
        # 使用一般模式的閾值
        similarity_threshold = config.MURMUR_SIMILARITY_THRESHOLD
    
    return similarity_threshold

def has_continuity_marker(text: str) -> bool:
    """
    檢查文本是否包含連續性標記。
    
    Args:
        text: 要檢查的文本
        
    Returns:
        如果包含連續性標記返回True，否則返回False
    """
    return any(marker in text for marker in config.CONTINUITY_MARKERS) 