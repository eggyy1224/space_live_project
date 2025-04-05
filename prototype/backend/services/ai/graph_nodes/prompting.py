"""
處理提示模板選擇、風格選擇和提示構建的相關節點邏輯。
負責構建傳給 LLM 的最終提示內容。
"""

import logging
import random
import json
from typing import Dict, List, Any, TypedDict, Optional

from langchain_core.messages import BaseMessage, HumanMessage

from ..prompts import DIALOGUE_STYLES

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def select_prompt_and_style_node(state: TypedDict) -> Dict[str, Any]:
    """選擇提示模板和對話風格節點
    
    如果工具已被執行，則跳過選擇，保留由 integrate_tool_result 設置的模板，
    並確保 tool_result/tool_error 被傳遞下去。
    """
    tool_execution_status = state.get("tool_execution_status", "skipped")
    
    if tool_execution_status != "skipped":
        logging.info(f"工具已執行 (狀態: {tool_execution_status})，跳過主要提示/風格選擇，保留工具相關狀態。")

        # --- 添加 Debugging --- 
        logging.debug(f"Inside select_prompt_and_style_node (tool executed): Received state keys: {list(state.keys())}")
        logging.debug(f"Inside select_prompt_and_style_node (tool executed): State contains tool_result? {'tool_result' in state}")
        logging.debug(f"Inside select_prompt_and_style_node (tool executed): state.get('tool_result') = {state.get('tool_result')}")
        logging.debug(f"Inside select_prompt_and_style_node (tool executed): State contains tool_error? {'tool_error' in state}")
        logging.debug(f"Inside select_prompt_and_style_node (tool executed): state.get('tool_error') = {state.get('tool_error')}")
        # --- End Debugging --- 
        
        # 仍然計算風格
        character_state = state["character_state"]
        input_classification = state["input_classification"]
        dialogue_style = select_dialogue_style(character_state, input_classification)
        
        # *** 關鍵修改：除了返回模板鍵和風格，還要返回工具結果/錯誤 ***
        return_dict = {
            "prompt_template_key": state.get("prompt_template_key"), 
            "dialogue_style": dialogue_style
        }
        tool_result_val = state.get("tool_result") # Get value once
        tool_error_val = state.get("tool_error")   # Get value once

        if tool_result_val is not None:
            return_dict["tool_result"] = tool_result_val
        if tool_error_val is not None:
            return_dict["tool_error"] = tool_error_val
            
        logging.debug(f"Inside select_prompt_and_style_node (tool executed): Returning dict: {return_dict}") # Log what is being returned
        return return_dict

    # --- 只有在工具未執行時，才執行以下選擇邏輯 ---    
    input_classification = state["input_classification"]
    character_state = state["character_state"]
    error_count = state["error_count"]
    system_alert = state["system_alert"]
    
    # 選擇提示模板
    prompt_template_key = "standard"  # 默認使用標準模板
    
    # 根據系統警告和錯誤計數選擇模板
    if system_alert and "llm_error" in system_alert and error_count > 1:
        prompt_template_key = "error"
    elif input_classification["type"] in ["gibberish", "highly_repetitive"]:
        prompt_template_key = "clarification" if error_count < 2 else "random_reply"
    elif input_classification["type"] == "very_short" and input_classification["repetition_level"] > 0.5:
        prompt_template_key = "clarification"
    
    # 選擇對話風格
    dialogue_style = select_dialogue_style(character_state, input_classification)
    
    logging.info(f"選擇提示模板: {prompt_template_key}, 對話風格: {dialogue_style}")
    
    return {
        "prompt_template_key": prompt_template_key,
        "dialogue_style": dialogue_style
        # 工具未執行時，不需要返回 tool_result/error
    }

def select_dialogue_style(character_state: Dict[str, Any], input_classification: Dict[str, Any]) -> str:
    """根據角色狀態和輸入分類選擇對話風格"""
    
    # 特殊情況優先處理
    if input_classification["type"] in ["gibberish", "highly_repetitive", "very_short"]:
        return DIALOGUE_STYLES["clarifying"]
    
    if input_classification["sentiment"] == "negative":
        return DIALOGUE_STYLES["caring"]
    
    # 如果能量低，返回疲倦風格
    if character_state["energy"] < 30:
        return DIALOGUE_STYLES["tired"]
    
    # 根據心情選擇候選風格
    mood_val = character_state["mood"]
    if mood_val > 80:
        candidates = ["enthusiastic", "humorous", "caring"]
    elif mood_val < 40:
        candidates = ["thoughtful", "tired", "caring"]
    else:
        candidates = ["caring", "curious", "humorous", "thoughtful", "enthusiastic"]
    
    # 增加隨機性
    if len(candidates) == 5:
        weights = [0.3, 0.2, 0.1, 0.1, 0.3]
    elif len(candidates) == 3:
        weights = [0.5, 0.3, 0.2]
    else:
        weights = None
        
    style_key = random.choices(candidates, weights=weights, k=1)[0]
    return DIALOGUE_STYLES[style_key]

def build_prompt_node(state: TypedDict) -> Dict[str, Any]:
    """構建提示節點 - 準備傳給 LLM 的輸入參數"""
    
    # 取得必要的狀態
    processed_user_input = state["processed_user_input"]
    filtered_memories = state["filtered_memories"]
    persona_info = state["persona_info"]
    prompt_template_key = state["prompt_template_key"]
    dialogue_style = state["dialogue_style"]
    messages = state["messages"]
    persona_name = state.get("_context", {}).get("persona_name", "星際小可愛")
    
    # --- 添加 Debug Logging ---
    logging.debug(f"Inside build_prompt_node: Received state keys: {list(state.keys())}")
    logging.debug(f"Inside build_prompt_node: prompt_template_key = '{prompt_template_key}'")
    logging.debug(f"Inside build_prompt_node: state contains tool_result? {'tool_result' in state}")
    logging.debug(f"Inside build_prompt_node: state.get('tool_result') = {state.get('tool_result')}")
    logging.debug(f"Inside build_prompt_node: state contains tool_error? {'tool_error' in state}")
    logging.debug(f"Inside build_prompt_node: state.get('tool_error') = {state.get('tool_error')}")
    # --- End Debug Logging ---
    
    # 格式化對話歷史
    history_limit = 10  # 取最近10條消息用於提示
    history = messages[-history_limit:] if len(messages) >= history_limit else messages
    conversation_history = "\n".join([
        f"{'用戶' if isinstance(msg, HumanMessage) else persona_name}: {msg.content}" 
        for msg in history
    ])
    
    # 格式化角色狀態描述
    character_state_prompt = format_character_state(state["character_state"])
    
    # 構建提示輸入 - 基礎部分
    prompt_inputs = {
        "user_message": processed_user_input,
        "conversation_history": conversation_history,
        "filtered_memories": filtered_memories,
        "persona_info": persona_info,
        "character_state": character_state_prompt,
        "current_task": state.get("current_task") or "無特定任務", # 使用 .get 避免 Key Error
        "dialogue_style": dialogue_style,
        "persona_name": persona_name
    }

    # *** 新增：如果模板需要，添加工具結果或錯誤信息 ***
    is_tool_template = "tool" in prompt_template_key
    logging.debug(f"Inside build_prompt_node: Condition '\"tool\" in prompt_template_key ({prompt_template_key})' is {is_tool_template}")
    if is_tool_template:
        tool_result_value = state.get("tool_result")
        tool_error_value = state.get("tool_error")
        logging.debug(f"Inside build_prompt_node: Adding tool results. tool_result_value={tool_result_value}, tool_error_value={tool_error_value}")
        if tool_result_value is not None:
            prompt_inputs["tool_result"] = tool_result_value
        if tool_error_value is not None:
            prompt_inputs["tool_error"] = tool_error_value

    logging.debug(f"提示輸入最終構建完成: {json.dumps(prompt_inputs)}") 
    
    # *** 關鍵修改：僅返回 prompt_inputs ***
    return {"prompt_inputs": prompt_inputs}

def format_character_state(character_state: Dict[str, Any]) -> str:
    """將數值狀態轉換為描述性文本"""
    energy = character_state["energy"]
    mood = character_state["mood"]
    health = character_state["health"]
    
    energy_desc = "精力超級充沛！" if energy > 85 else "精力充沛" if energy > 60 else \
                "感覺還行" if energy > 40 else "有點累了..."
    
    mood_desc = "心情超讚！" if mood > 85 else "心情不錯" if mood > 60 else \
            "情緒還好" if mood > 40 else "有點悶悶的..."
    
    health_desc = "身體狀態絕佳！" if health > 85 else "身體感覺良好" if health > 60 else \
                "身體還算健康" if health > 40 else "感覺不太舒服..."
    
    return f"{energy_desc}，{mood_desc}，{health_desc}。在太空已待了{character_state['days_in_space']}天。" 