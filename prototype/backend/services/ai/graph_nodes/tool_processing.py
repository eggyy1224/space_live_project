"""
工具呼叫處理模塊 - 處理 LLM 工具呼叫相關邏輯

此模塊包含用於識別、解析、執行工具呼叫，並將結果整合回對話流程的方法。
處理工具呼叫的不同階段，包括識別工具意圖、解析參數、執行工具動作等。
"""

import logging
import json
import re
from typing import Dict, Any, List, Tuple, Optional

from .tool_registry import get_available_tools, get_tool_by_name

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_tool_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    檢測用戶輸入是否有執行工具的意圖
    
    檢測邏輯:
    1. 分析用戶輸入中是否包含明確的工具請求模式
    2. 檢查用戶意圖分類中是否指向工具使用
    3. 與已註冊的工具功能比較，找出最匹配的工具
    
    返回:
    更新後的狀態，包含 has_tool_intent 和 potential_tool 字段
    """
    processed_input = state["processed_user_input"]
    input_classification = state["input_classification"]
    
    # 初始化工具意圖標記
    has_tool_intent = False
    potential_tool = None
    tool_confidence = 0.0
    
    # 獲取可用的工具列表
    available_tools = get_available_tools()
    
    # 檢查是否包含明確的工具請求模式
    tool_patterns = [
        r"(?:可以|能不能|請|幫我|給我|要).*(?:查看|查詢|搜索|尋找|顯示).*(?:在太空中的|太空|宇宙|星球|衛星)",  # 查詢太空物體
        r"(?:可以|能不能|請|幫我|給我|要).*(?:分析|評估|檢測|辨識|識別).*(?:這個|目前|當前).*(?:場景|環境|情況)",  # 場景分析
        r"(?:可以|能不能|請|幫我|給我|要).*(?:產生|生成|創造|做|製作).*(?:3D|三維|立體).*(?:模型|物件|物體)",  # 3D生成
    ]
    
    for pattern in tool_patterns:
        if re.search(pattern, processed_input):
            has_tool_intent = True
            logging.info(f"檢測到工具意圖模式: {pattern}")
            break
    
    # 如果用戶輸入明確包含工具名稱
    for tool in available_tools:
        tool_name = tool.get("name", "")
        tool_keywords = tool.get("keywords", [])
        
        # 檢查工具名稱或關鍵詞是否出現在用戶輸入中
        if tool_name in processed_input or any(keyword in processed_input for keyword in tool_keywords):
            potential_tool = tool_name
            tool_confidence = 0.8
            has_tool_intent = True
            logging.info(f"用戶明確提及工具: {tool_name}")
            break
    
    # 如果沒有明確提及工具，但輸入分類暗示可能需要工具
    if not has_tool_intent and input_classification.get("type") == "question":
        # 對於問題類型，嘗試進一步分析是否適合使用工具
        space_related_keywords = ["太空", "宇宙", "星球", "衛星", "軌道", "月球", "地球"]
        if any(keyword in processed_input for keyword in space_related_keywords):
            has_tool_intent = True
            potential_tool = "space_object_query"  # 默認使用太空物體查詢工具
            tool_confidence = 0.6
            logging.info("基於問題分類和太空關鍵詞推斷可能需要使用查詢工具")
    
    return {
        "has_tool_intent": has_tool_intent,
        "potential_tool": potential_tool,
        "tool_confidence": tool_confidence
    }

def parse_tool_parameters(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    從用戶輸入中解析可能的工具參數
    
    根據識別的工具類型，嘗試從用戶輸入中提取所需參數。
    例如，如果是太空物體查詢工具，會嘗試提取物體名稱或類型。
    
    返回:
    更新後的狀態，包含工具參數字典
    """
    if not state.get("has_tool_intent", False):
        return {"tool_parameters": {}}
    
    processed_input = state["processed_user_input"]
    potential_tool = state.get("potential_tool")
    
    tool_parameters = {}
    
    # 根據工具類型解析參數
    if potential_tool == "space_object_query":
        # 嘗試提取太空物體名稱
        object_patterns = [
            r"(?:關於|有關|查詢|了解|尋找).*?([\w\s]+?)(?:的位置|的信息|的資料|的狀態|的軌道|在哪|嗎|$)",
            r"(?:[\w\s]+?)(?:在哪裡|的位置|的信息|的資料)"
        ]
        
        for pattern in object_patterns:
            match = re.search(pattern, processed_input)
            if match:
                object_name = match.group(1).strip()
                if len(object_name) > 2 and not any(stop_word in object_name for stop_word in ["可以", "能不能", "請", "幫我"]):
                    tool_parameters["object_name"] = object_name
                    logging.info(f"解析到太空物體名稱: {object_name}")
                    break
    
    elif potential_tool == "scene_analysis":
        # 場景分析工具通常不需要額外參數，但可以檢測用戶是否有特定分析請求
        analysis_type = None
        if "安全" in processed_input or "危險" in processed_input:
            analysis_type = "safety"
        elif "物體" in processed_input or "識別" in processed_input:
            analysis_type = "object_detection"
        
        if analysis_type:
            tool_parameters["analysis_type"] = analysis_type
            logging.info(f"解析到場景分析類型: {analysis_type}")
    
    # 記錄解析出的參數
    logging.info(f"從用戶輸入中解析出的工具參數: {tool_parameters}")
    
    return {
        "tool_parameters": tool_parameters
    }

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
    
    # 獲取工具函數
    tool_func = get_tool_by_name(tool_name)
    
    if not tool_func:
        logging.warning(f"找不到工具: {tool_name}")
        return {
            "tool_execution_result": f"無法找到工具: {tool_name}",
            "tool_execution_status": "error"
        }
    
    # 執行工具
    try:
        logging.info(f"開始執行工具: {tool_name}，參數: {tool_parameters}")
        result = await tool_func(**tool_parameters)
        
        # 檢查結果格式並處理
        if isinstance(result, dict):
            # 若結果是字典，提取主要內容字段或轉為字符串
            if "content" in result:
                tool_result = result["content"]
            elif "data" in result:
                tool_result = result["data"]
            else:
                tool_result = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            tool_result = str(result)
        
        logging.info(f"工具執行成功: {tool_name}")
        
        return {
            "tool_execution_result": tool_result,
            "tool_execution_status": "success",
            "tool_used": tool_name
        }
    
    except Exception as e:
        error_message = f"執行工具 {tool_name} 時出錯: {str(e)}"
        logging.error(error_message, exc_info=True)
        
        return {
            "tool_execution_result": error_message,
            "tool_execution_status": "error",
            "tool_used": tool_name
        }

def format_tool_result_for_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化工具結果以便於 LLM 處理
    
    將工具執行結果轉換為適合 LLM 使用的格式，包括添加適當的上下文和指導說明。
    
    返回:
    更新後的狀態，包含格式化的工具結果
    """
    if state.get("tool_execution_status") != "success":
        return {}
    
    tool_result = state.get("tool_execution_result", "")
    tool_name = state.get("tool_used", "unknown")
    
    # 為不同工具類型定制格式化邏輯
    formatted_result = tool_result
    
    # 添加工具結果到對話上下文
    tool_context = f"""
【工具執行結果】
工具: {tool_name}
結果: 
{formatted_result}

請根據以上工具執行結果，以自然、友好的方式回應用戶，解釋結果含義。保持回應簡潔，不要重複引用原始數據，而是將信息融入自然對話中。
"""
    
    # 如果工具結果太長，可能需要摘要
    max_result_length = 800  # 工具結果最大長度
    if len(formatted_result) > max_result_length:
        summary_length = max_result_length // 2
        formatted_result = formatted_result[:summary_length] + "...\n[結果太長，已截斷]..." + formatted_result[-summary_length:]
    
    return {
        "formatted_tool_result": tool_context,
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
    
    if tool_execution_status == "skipped":
        # 如果未執行工具，保持對話流程不變
        return {}
    
    updates = {}
    
    if tool_execution_status == "success":
        # 工具成功執行，將結果整合到提示中
        current_prompt_inputs = state.get("prompt_inputs", {})
        current_prompt_inputs["tool_result"] = formatted_tool_result
        
        # 調整提示模板以包含工具結果
        updates["prompt_template_key"] = "tool_result"
        updates["prompt_inputs"] = current_prompt_inputs
        
        # 增加角色心情（因成功使用工具）
        character_state = state.get("character_state", {})
        if "mood" in character_state:
            character_state["mood"] = min(100, character_state.get("mood", 50) + 5)
            updates["character_state"] = character_state
            
        logging.info("工具結果已整合到對話流程，使用工具結果專用提示模板")
        
    elif tool_execution_status == "error":
        # 工具執行失敗，添加友好的錯誤信息到提示
        error_message = state.get("tool_execution_result", "工具執行失敗")
        current_prompt_inputs = state.get("prompt_inputs", {})
        current_prompt_inputs["tool_error"] = f"[系統通知: 工具執行時出現問題，請提供一個友好的解釋，不要直接提及技術錯誤: {error_message}]"
        
        # 使用錯誤處理模板
        updates["prompt_template_key"] = "tool_error"
        updates["prompt_inputs"] = current_prompt_inputs
        
        # 添加系統警告
        updates["system_alert"] = "tool_execution_error"
        
        logging.warning(f"工具執行失敗，使用錯誤處理提示模板: {error_message}")
    
    return updates 