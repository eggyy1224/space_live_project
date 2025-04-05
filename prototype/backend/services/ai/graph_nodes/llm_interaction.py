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
    
    processed_response, was_heavily_modified = post_process_response(
        llm_response_raw, 
        input_classification, 
        prompt_template_key,
        state.get("_context", {}).get("persona_name", "星際小可愛")
    )
    
    logging.info(f"後處理完成: 從 {len(llm_response_raw)} 到 {len(processed_response)} 字符")
    
    # 決定是否將對話存儲到記憶庫
    should_store_memory = True
    system_alert = state.get("system_alert")
    
    # 如果回應被大幅修改或輸入有問題，不儲存到記憶
    if was_heavily_modified or input_classification["type"] in ["gibberish", "highly_repetitive"]:
        should_store_memory = False
        system_alert = system_alert or "response_heavily_modified"
    
    return {
        "final_response": processed_response,
        "should_store_memory": should_store_memory,
        "system_alert": system_alert
    }

def post_process_response(response: str, input_classification: Dict[str, Any], template_key: str, persona_name: str = "星際小可愛") -> Tuple[str, bool]:
    """
    後處理回應，移除固定模式和 Emoji
    返回: (處理後的回應, 是否大幅修改)
    """
    original_response_stripped = response.strip() # 保存原始的回應 (去除首尾空格)
    original_length = len(original_response_stripped)
    processed_response = original_response_stripped
    was_heavily_modified = False

    # 1. 移除可能的固定開場白
    fixed_intros = [
        f"嗨，我是{persona_name}",
        f"你好，我是{persona_name}",
        f"哈囉，我是{persona_name}",
        f"我是{persona_name}"
    ]
    # 移除句首的感嘆號和空格
    processed_response = processed_response.lstrip("!！ ")

    for intro in fixed_intros:
        # 移除前導空格和標點進行比較
        normalized_response_start = processed_response.lstrip(",，.。:：!！ ")
        if normalized_response_start.lower().startswith(intro.lower()):
            # 移除開頭並去除多餘的標點或空格
            processed_response = normalized_response_start[len(intro):].lstrip(",，.。:：!！ ")
            break # 匹配到一個就停止

    # 2. 移除常見的 Emoji 字符
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    processed_response = emoji_pattern.sub(r'', processed_response).strip()

    # 3. 檢查或移除回應中的奇怪詞彙 (可能是從用戶輸入中吸收的)
    weird_terms = ["DevOps", "j8 dl4", "AI", "dl4", "GPS"]

    # 特別處理：如果回應是「純」AI，而對話模板不是 error 或 random_reply，考慮替換
    if processed_response.strip() == "AI" and template_key not in ["error", "random_reply"]:
        processed_response = "啊，我好像分心了一下，你剛才說什麼？"
        was_heavily_modified = True

    # 如果是 clarification 或 random_reply 模板，確保不重複用戶的奇怪輸入
    if template_key in ["clarification", "random_reply"]:
        user_input_for_check = input_classification.get("raw_user_input", "") # 使用 raw_user_input 檢查
        for term in weird_terms:
            if term in processed_response and term in user_input_for_check:
                processed_response = processed_response.replace(term, "[...]")
                # was_heavily_modified = True # 移除奇怪詞彙不算重大修改

    # 4. 確保回應不為空或過短 (少於3個字符) - **修改後的邏輯**
    final_processed_length = len(processed_response.strip()) # 計算最終處理後的長度

    if final_processed_length < 3:
        # 如果處理後回應太短
        if original_length >= 5: # 只有當原始回應不算太短 (例如 >= 5) 時
            logging.warning(f"後處理將較長回應 (長度 {original_length}) 縮短至少於 3 個字符，恢復原始回應")
            processed_response = original_response_stripped # 恢復原始回應
            was_heavily_modified = True # 標記為大幅修改
        else:
            # 如果原始回應本身就很短 ( < 5)，無需恢復，接受處理後的短回應 (可能是空字串)
            logging.info(f"後處理後回應過短 (長度 {final_processed_length})，但原始回應也很短 (長度 {original_length})，接受處理結果")
            # 雖然接受了處理結果，但這麼短的回應可能意義不大，仍然標記以便不儲存
            was_heavily_modified = True # 仍然標記，避免儲存價值不大的短回應/空回應
    # else: # 如果處理後長度 >= 3，則正常繼續

    # 5. 判斷是否大幅修改 (如果尚未標記)
    if not was_heavily_modified:
        # 如果長度減少超過 30%，也認為是大幅修改
        was_heavily_modified = (len(processed_response) < original_length * 0.7)

    return processed_response, was_heavily_modified 