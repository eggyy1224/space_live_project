"""
工具呼叫處理模塊 - 處理 LLM 工具呼叫相關邏輯

此模塊包含用於識別、解析、執行工具呼叫，並將結果整合回對話流程的方法。
處理工具呼叫的不同階段，包括識別工具意圖、解析參數、執行工具動作等。
"""

import logging
import json
import re
import asyncio
from typing import Dict, Any, List, Tuple, Optional

# 從 langchain_core 導入所需的消息類
from langchain_core.messages import AIMessage, SystemMessage 
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 輔助函數：格式化工具描述給 LLM ---
def _format_tool_descriptions(available_tools: Dict[str, Dict]) -> str:
    descriptions = []
    for name, info in available_tools.items():
        params = info.get("parameters", [])
        param_str = ", ".join([f'{p["name"]}({p["type"]})' for p in params])
        descriptions.append(f'- {name}({param_str}): {info.get("description", "")}')
    return "\n".join(descriptions)

async def detect_tool_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    檢測用戶輸入是否有執行工具的意圖 - 使用 LLM 判斷。
    
    檢測邏輯:
    1. 分析用戶輸入中是否包含明確的工具請求模式
    2. 檢查用戶意圖分類中是否指向工具使用
    3. 與已註冊的工具功能比較，找出最匹配的工具
    
    返回:
    更新後的狀態，包含 has_tool_intent 和 potential_tool 字段
    """
    processed_input = state["processed_user_input"]
    messages = state.get("messages", [])
    # 從 context 獲取依賴
    available_tools = state.get("_context", {}).get("available_tools", {})
    llm = state.get("_context", {}).get("llm")

    # 初始化默認值
    has_tool_intent = False
    potential_tool = None
    tool_confidence = 0.0

    if not llm or not available_tools:
        logging.warning("detect_tool_intent: LLM 或可用工具列表未提供，跳過工具檢測")
        return {
            "has_tool_intent": False,
            "potential_tool": None,
            "tool_confidence": 0.0
        }

    # 獲取格式化的工具描述
    tool_descriptions = _format_tool_descriptions(available_tools)

    # 構建提示讓 LLM 判斷
    prompt_template = PromptTemplate.from_template(
        "可用工具列表:\n{tool_descriptions}\n\n"\
        "最近對話歷史 (僅供參考):\n{conversation_history}\n\n"\
        "最新用戶輸入: \"{user_input}\"\n\n"\
        "根據最新的用戶輸入，判斷是否應使用以及最適合使用上述哪個工具來回應？\n"\
        "如果用戶的意圖是進行常規對話、閒聊或表達情感，則不需要工具。\n"\
        "如果用戶的意圖是查詢具體信息、執行特定操作，且與某個工具描述匹配，則選擇該工具。\n"\
        "如果不需要工具，請只回答 'none'。\n"\
        "如果需要工具，請只回答該工具的名稱 (例如 'search_wikipedia')。"
    )

    # 準備對話歷史摘要 (可選，取最近幾輪)
    history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-4:]]) # 取最近4條

    chain = prompt_template | llm | StrOutputParser()

    try:
        logging.info("調用 LLM 進行工具意圖檢測...")
        llm_decision = await chain.ainvoke({
            "tool_descriptions": tool_descriptions,
            "conversation_history": history_str,
            "user_input": processed_input
        })
        llm_decision = llm_decision.strip().lower()
        logging.info(f"LLM 工具意圖判斷結果: {llm_decision}")

        if llm_decision != 'none' and llm_decision in available_tools:
            has_tool_intent = True
            potential_tool = llm_decision
            tool_confidence = 0.9 # 假設 LLM 判斷的可信度較高
            logging.info(f"LLM 建議使用工具: {potential_tool}")
        else:
            logging.info("LLM 判斷無需使用工具或選擇了無效工具。")

    except Exception as e:
        logging.error(f"LLM 工具意圖檢測失敗: {e}", exc_info=True)
        # 出錯時，保守起見不使用工具
        has_tool_intent = False
        potential_tool = None
        tool_confidence = 0.0

    return {
        "has_tool_intent": has_tool_intent,
        "potential_tool": potential_tool,
        "tool_confidence": tool_confidence
    }

async def parse_tool_parameters(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    從用戶輸入中解析工具參數 - 使用 LLM 提取。
    
    根據識別的工具類型，嘗試從用戶輸入中提取所需參數。
    例如，如果是太空物體查詢工具，會嘗試提取物體名稱或類型。
    
    返回:
    更新後的狀態，包含工具參數字典
    """
    if not state.get("has_tool_intent", False) or not state.get("potential_tool"):
        return {"tool_parameters": {}}

    processed_input = state["processed_user_input"]
    potential_tool = state["potential_tool"]
    messages = state.get("messages", [])
    # 從 context 獲取依賴
    available_tools = state.get("_context", {}).get("available_tools", {})
    llm = state.get("_context", {}).get("llm")

    tool_parameters = {}

    if not llm or potential_tool not in available_tools:
        logging.warning("parse_tool_parameters: LLM 或工具信息缺失，無法解析參數")
        # 返回空參數，讓 execute_tool 處理缺少參數的情況
        return {"tool_parameters": {}}

    tool_info = available_tools[potential_tool]
    required_params = tool_info.get("parameters", [])

    if not required_params:
        logging.info(f"工具 '{potential_tool}' 無需參數。")
        return {"tool_parameters": {}} # 無需參數，直接返回

    # 構建提示讓 LLM 提取參數
    # 對於 search_wikipedia，我們需要提取 query
    if potential_tool == 'search_wikipedia':
        param_name = 'query'
        param_description = next((p["description"] for p in required_params if p["name"] == param_name), "查詢的主題")

        prompt_template = PromptTemplate.from_template(
            "你需要為工具 '{tool_name}' 提取參數 '{param_name}'。\n"\
            "參數描述: {param_description}\n"\
            "最近對話歷史 (僅供參考):\n{conversation_history}\n\n"\
            "最新用戶輸入: \"{user_input}\"\n\n"\
            "請分析用戶輸入和對話歷史，找出最符合參數描述的值。\n"\
            "請只返回提取到的參數值，不要包含任何其他解釋性文字、引號或標籤。\n"\
            "如果無法從用戶輸入中明確找到參數值，請回答 '無法確定'。"
        )

        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-4:]])
        chain = prompt_template | llm | StrOutputParser()

        try:
            logging.info(f"調用 LLM 提取工具 '{potential_tool}' 的參數 '{param_name}'...")
            extracted_value = await chain.ainvoke({
                "tool_name": potential_tool,
                "param_name": param_name,
                "param_description": param_description,
                "conversation_history": history_str,
                "user_input": processed_input
            })
            extracted_value = extracted_value.strip()
            logging.info(f"LLM 提取到的參數值: {extracted_value}")

            if extracted_value and extracted_value.lower() != '無法確定':
                tool_parameters[param_name] = extracted_value
            else:
                logging.warning(f"LLM 未能提取工具 '{potential_tool}' 的參數 '{param_name}'")
                # 可以在這裡觸發澄清流程，或者讓 execute_tool 處理缺少參數

        except Exception as e:
            logging.error(f"LLM 參數提取失敗: {e}", exc_info=True)
            # 提取失敗，返回空參數
            tool_parameters = {}
    
    # else: # 在這裡添加其他工具的參數提取邏輯
    #    pass 

    logging.info(f"解析出的工具參數: {tool_parameters}")
    return {"tool_parameters": tool_parameters}

async def execute_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    執行指定的工具並獲取結果
    
    根據前面步驟識別的工具和解析的參數，調用相應工具函數。
    處理工具可能的錯誤，並格式化工具執行結果。
    
    返回:
    更新後的狀態，包含工具執行結果和狀態
    """
    if not state.get("has_tool_intent", False) or not state.get("potential_tool"):
        return {
            "tool_execution_result": "",
            "tool_execution_status": "skipped"
        }

    tool_name = state["potential_tool"]
    tool_parameters = state.get("tool_parameters", {})
    # 從 context 獲取可用工具
    available_tools = state.get("_context", {}).get("available_tools", {})

    # 從可用工具字典中獲取工具信息和函數
    if tool_name not in available_tools:
        logging.warning(f"找不到已註冊的工具: {tool_name}")
        return {
            "tool_execution_result": f"抱歉，我內部找不到名為 '{tool_name}' 的工具。",
            "tool_execution_status": "failed_unknown_tool",
            "tool_used": tool_name
        }
    
    tool_info = available_tools[tool_name]
    tool_func = tool_info.get("function")
    required_params = [p["name"] for p in tool_info.get("parameters", [])]

    if not tool_func:
        logging.error(f"工具 '{tool_name}' 已註冊但未找到有效的執行函數。")
        return {
            "tool_execution_result": f"抱歉，工具 '{tool_name}' 內部配置似乎有誤。",
            "tool_execution_status": "failed_internal_error",
            "tool_used": tool_name
        }

    # 檢查必要參數是否缺失
    missing_params = [p for p in required_params if p not in tool_parameters]
    if missing_params:
        error_msg = f"我需要知道 '{', '.join(missing_params)}' 才能執行這個操作。你能提供嗎？"
        logging.warning(f"執行工具 {tool_name} 失敗: 缺少參數 {missing_params}")
        return {
            "tool_execution_result": error_msg,
            "tool_execution_status": "failed_missing_params",
            "tool_used": tool_name
        }

    # 執行工具
    try:
        logging.info(f"開始異步執行工具: {tool_name}，參數: {tool_parameters}")
        # 異步執行工具函數
        result = await tool_func(**tool_parameters) 

        # 確保結果是字符串
        tool_result = str(result)

        logging.info(f"工具執行成功: {tool_name}")
        return {
            "tool_execution_result": tool_result,
            "tool_execution_status": "success",
            "tool_used": tool_name
        }

    except Exception as e:
        error_message = f"執行工具 {tool_name} 時發生錯誤: {str(e)}"
        logging.error(error_message, exc_info=True)
        return {
            "tool_execution_result": f"抱歉，我在嘗試執行 '{tool_name}' 操作時遇到了技術問題。",
            "tool_execution_status": "failed_exception",
            "tool_used": tool_name
        }

def format_tool_result_for_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化工具結果以便於 LLM 處理
    
    將工具執行結果轉換為適合 LLM 使用的格式，包括添加適當的上下文和指導說明。
    
    返回:
    更新後的狀態，包含格式化的工具結果
    """
    tool_execution_status = state.get("tool_execution_status", "skipped")
    tool_result = state.get("tool_execution_result", "")
    tool_name = state.get("tool_used", "unknown")

    # 如果工具執行失敗，也將錯誤信息格式化給 LLM
    if tool_execution_status != "success":
        formatted_result = f"工具 '{tool_name}' 執行失敗。原因: {tool_result}"
        tool_context = f"""
【工具執行失敗提示】
{formatted_result}

請告知用戶你無法完成請求，並簡要說明原因 (如果錯誤信息適合展示)。
"""
    else:
        # 格式化成功結果
        formatted_result = tool_result
        # 如果工具結果太長，進行截斷處理
        max_result_length = 800
        if len(formatted_result) > max_result_length:
            summary_length = max_result_length // 2
            result_summary = formatted_result[:summary_length] + "... [結果過長已截斷] ..." + formatted_result[-summary_length:]
        else:
            result_summary = formatted_result
        
        tool_context = f"""
【工具執行結果】
工具: {tool_name}
結果摘要: 
{result_summary}

請根據以上工具執行結果，自然地融入你的回應中，告知用戶查詢結果。不要只是複述結果。
"""

    return {
        "formatted_tool_result": tool_context,
        # 保留一個簡短摘要，可能用於內部記錄或調試
        "tool_result_summary": formatted_result[:150] + "..." if len(formatted_result) > 150 else formatted_result
    }

def integrate_tool_result(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    將工具結果整合到對話流程中
    
    根據工具執行狀態和結果，更新對話狀態，包括調整提示模板、添加系統消息等。
    
    返回:
    更新後的狀態，包括整合工具結果後的對話狀態
    """
    tool_execution_status = state.get("tool_execution_status", "skipped")
    formatted_tool_result = state.get("formatted_tool_result", "")
    messages = state.get("messages", [])

    # 將格式化的工具結果作為一個特殊的 "tool" 訊息添加到歷史記錄中
    # 以便後續的提示構建節點可以包含它
    if formatted_tool_result:
        # LangChain 目前沒有標準的 ToolMessage 類型，我們可以用 SystemMessage 或 AIMessage 模擬
        # 使用 AIMessage 可能更適合，因為它是工具代表 AI 執行的結果
        # 或者定義一個自定義 Message 類型
        # 這裡暫時用 AIMessage，並在 content 中標註是工具結果
        # 需要確認 AIMessage 是否支持 role 參數，如果不支持，則使用 SystemMessage
        # 假設 AIMessage 支持 role:
        tool_message = AIMessage(content=formatted_tool_result, role="tool") 
        # 如果 AIMessage 不支持 role，則使用 SystemMessage:
        # tool_message = SystemMessage(content=f"[工具執行結果]\n{formatted_tool_result}")
        
        # 添加到消息列表
        updated_messages = messages + [tool_message]
    else:
        updated_messages = messages

    # 根據工具執行狀態選擇提示模板
    prompt_template_key = state.get("prompt_template_key", "standard")
    if tool_execution_status != "skipped":
        # 如果工具被調用（無論成功或失敗），可能需要使用特定的提示模板來處理工具結果
        # 例如 'tool_response' 或 'tool_error_response' (需要在 prompts.py 中定義)
        if tool_execution_status == 'success':
            prompt_template_key = 'tool_response' 
        else: # failed_*
             prompt_template_key = 'tool_error_response'

    return {
        "messages": updated_messages,
        "prompt_template_key": prompt_template_key # 更新提示模板鍵
    } 