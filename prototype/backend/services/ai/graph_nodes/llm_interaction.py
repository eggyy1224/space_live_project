"""
處理 LLM 調用、錯誤處理和回應後處理的相關節點邏輯。
負責與大型語言模型交互的核心邏輯。
"""

import logging
import asyncio
import random
import re
import time
from typing import Dict, List, Any, TypedDict, Optional, Tuple

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def call_llm_node(state: TypedDict) -> Dict[str, Any]:
    """調用 LLM 節點 - 使用提示輸入調用大型語言模型"""
    prompt_template_key = state["prompt_template_key"]
    prompt_inputs = state["prompt_inputs"]
    error_count = state["error_count"]
    llm = state.get("_context", {}).get("llm")
    prompt_templates = state.get("_context", {}).get("prompt_templates")
    
    if not llm or not prompt_templates:
        logging.error("LLM 或提示模板未在上下文中提供")
        return {
            "llm_response_raw": "抱歉，我的系統似乎出了點問題...",
            "error_count": error_count + 1,
            "system_alert": "llm_not_found"
        }
    
    # 選擇提示模板
    prompt_template = prompt_templates.get(prompt_template_key, prompt_templates["standard"])
    
    # 構建 LLM 鏈
    chain = prompt_template | llm | StrOutputParser()
    
    for attempt in range(2):  # 最多嘗試2次
        try:
            llm_response_raw = await chain.ainvoke(prompt_inputs)
            logging.info(f"LLM 調用成功: {len(llm_response_raw)} 字符的回應")
            
            return {
                "llm_response_raw": llm_response_raw,
                "error_count": 0,  # 成功調用，重置錯誤計數
                "system_alert": None  # 清除系統警告
            }
        except Exception as e:
            logging.error(f"LLM 調用失敗 (嘗試 {attempt+1}/2): {e}", exc_info=True)
            if attempt < 1:  # 如果不是最後一次嘗試
                continue  # 重試
    
    # 所有嘗試都失敗，返回友好的錯誤消息
    error_responses = [
        "哎呀，我的訊號好像不太穩定，你能再說一次嗎？",
        "嗯... 我的處理器好像卡了一下，可以再問一次嗎？",
        "太空干擾有點強，我沒聽清楚，麻煩再說一遍！"
    ]
    
    return {
        "llm_response_raw": random.choice(error_responses),
        "error_count": error_count + 1,
        "system_alert": "llm_error_all_attempts_failed"
    }

def handle_llm_error(state: TypedDict) -> str:
    """處理 LLM 調用錯誤的條件路由"""
    if state.get("system_alert") and "llm_error" in state["system_alert"]:
        return "retry"
    return "continue"

def post_process_node(state: TypedDict) -> Dict[str, Any]:
    """後處理節點 - 處理 LLM 回應，移除固定模式"""
    llm_response_raw = state["llm_response_raw"]
    input_classification = state["input_classification"]
    prompt_template_key = state["prompt_template_key"]
    
    processed_response, was_heavily_modified = post_process_response_simplified(
        llm_response_raw, 
        template_key=prompt_template_key
    )
    
    logging.info(f"後處理完成: 從 {len(llm_response_raw)} 到 {len(processed_response)} 字符")
    
    # 決定是否將對話存儲到記憶庫
    should_store_memory = True
    system_alert = state.get("system_alert")
    
    # 如果是工具回應或輸入有問題，不儲存到記憶
    if prompt_template_key in ["tool_response", "tool_error_response", "error"] or \
       input_classification["type"] in ["gibberish", "highly_repetitive"]:
        should_store_memory = False
        system_alert = system_alert or "response_processing_skipped"
    
    return {
        "final_response": processed_response,
        "should_store_memory": should_store_memory,
        "system_alert": system_alert
    }

def post_process_response_simplified(response: str, template_key: str) -> Tuple[str, bool]:
    """
    極簡化的後處理回應函數。
    只進行基本的清理 (strip)。
    返回: (處理後的回應, 是否大幅修改 - 始終為 False)
    """
    processed_response = response.strip()
    
    # 可選：如果需要，可以保留非常特定的清理邏輯，例如移除特定開頭/結尾符號
    # processed_response = processed_response.strip('" \n')
    
    # 始終返回 False，表示未進行可能改變語義的大幅修改
    return processed_response, False 