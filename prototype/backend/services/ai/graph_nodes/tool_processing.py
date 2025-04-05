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
    parameter_definitions = tool_info.get("parameters", [])

    if not parameter_definitions:
        logging.info(f"工具 '{potential_tool}' 無需參數。")
        return {"tool_parameters": {}} # 無需參數，直接返回

    # 構建提示讓 LLM 提取參數
    if potential_tool == 'search_wikipedia':
        param_name = 'query'
        param_description = next((p["description"] for p in parameter_definitions if p["name"] == param_name), "查詢的主題")

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
    
    # --- 新增：處理 get_moon_phase 的 date_str 參數 ---
    elif potential_tool == 'get_moon_phase':
        param_name = 'date_str'
        param_info = next((p for p in parameter_definitions if p["name"] == param_name), None)
        if param_info:
            param_description = param_info.get("description", "查詢的日期")
            
            prompt_template = PromptTemplate.from_template(
                "用戶想要查詢月相。你需要為工具 '{tool_name}' 提取可選參數 '{param_name}'。\n"\
                "參數描述: {param_description}\n"\
                "最近對話歷史 (僅供參考):\n{conversation_history}\n\n"\
                "最新用戶輸入: \"{user_input}\"\n\n"\
                "請分析用戶輸入，判斷用戶是否指定了日期。支持的格式為 YYYY-MM-DD、'今天'、'明天'、'昨天'。\n"\
                "如果用戶明確指定了日期（例如 '2024-05-10'、'明天'），請只返回該日期字符串。\n"\
                "如果用戶沒有指定日期，或者你不確定用戶指的是哪個日期，請回答 '未指定'。\n"\
                "不要返回任何其他解釋性文字。"
            )
            
            history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-4:]])
            chain = prompt_template | llm | StrOutputParser()
            
            try:
                logging.info(f"調用 LLM 提取工具 '{potential_tool}' 的可選參數 '{param_name}'...")
                extracted_value = await chain.ainvoke({
                    "tool_name": potential_tool,
                    "param_name": param_name,
                    "param_description": param_description,
                    "conversation_history": history_str,
                    "user_input": processed_input
                })
                extracted_value = extracted_value.strip()
                logging.info(f"LLM 提取到的日期參數值: '{extracted_value}'")
                
                # 只有當 LLM 返回了非'未指定'的值時才設置參數
                if extracted_value and extracted_value.lower() not in ['未指定', '']:
                    tool_parameters[param_name] = extracted_value
                else:
                    logging.info(f"LLM 未提取到明確的日期參數或用戶未指定，將使用默認日期（今天）。")
                    # 不設置參數，讓工具函數使用默認值
            
            except Exception as e:
                logging.error(f"LLM 日期參數提取失敗: {e}", exc_info=True)
                # 提取失敗，不設置參數，讓工具函數使用默認值
                tool_parameters = {}
    # --- 結束新增 ---
    
    # --- 新增：處理 search_space_news 的多個參數 ---
    elif potential_tool == 'search_space_news':
        # 準備對話歷史供 LLM 參考
        history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-4:]])
        
        # 提取 keywords 參數
        keywords_prompt = PromptTemplate.from_template(
            "用戶想要搜索太空新聞。你需要從用戶輸入中提取關鍵詞。\n"\
            "最近對話歷史 (僅供參考):\n{conversation_history}\n\n"\
            "最新用戶輸入: \"{user_input}\"\n\n"\
            "請分析用戶輸入，判斷用戶是否在尋找特定主題或關鍵詞的太空新聞。\n"\
            "例如，如果用戶說'看看關於SpaceX的新聞'，關鍵詞就是'SpaceX'。\n"\
            "如果用戶說'被困在太空站的太空人相關新聞'，關鍵詞就是'被困 太空站 太空人'。\n"\
            "注意：時間範圍（如'今年'、'去年'、'2020年'、'2005'等）不應被視為關鍵詞，將由其他參數處理。\n"\
            "如果用戶輸入是'今年的太空新聞'，'2018太空新聞'等，其中的時間詞不是關鍵詞，應回答'未指定'。\n"\
            "請只專注於提取主題關鍵詞，不要提取時間相關的詞。\n"\
            "如果用戶沒有明確指定任何特定主題，請回答 '未指定'。\n"\
            "請只返回關鍵詞或'未指定'，不要添加任何解釋、引號或附加信息。"
        )
        
        # 提取時間範圍參數
        time_period_prompt = PromptTemplate.from_template(
            "用戶想要搜索太空新聞。你需要從用戶輸入中提取時間範圍。\n"\
            "最近對話歷史 (僅供參考):\n{conversation_history}\n\n"\
            "最新用戶輸入: \"{user_input}\"\n\n"\
            "請分析用戶輸入，判斷用戶是否指定了特定的時間範圍。\n"\
            "支持的時間範圍包括: \n"\
            "1. 一般時間：'今天'、'昨天'、'本週'、'上週'、'本月'、'上個月'、'今年'、'去年'等\n"\
            "2. 相對時間：'X天前'或'X天後'的格式\n"\
            "3. 特定年份：例如 '2020年'、'2019年'、'2005' 等年份數字\n"\
            "如果用戶明確指定了時間範圍，請只返回該時間範圍字符串。\n"\
            "以下是一些例子：\n"\
            "- 用戶說'查看2020年的太空新聞'，請返回 '2020年'\n"\
            "- 用戶說'2005 太空新聞'，請返回 '2005'\n"\
            "- 用戶說'2018太空發展'，請返回 '2018'\n"\
            "- 用戶說'五年前的太空新聞'，請返回 '五年前'\n"\
            "- 用戶說'今年的太空新聞'，請返回 '今年'\n"\
            "請特別注意解析'今年的太空新聞'中的'今年'，'去年太空發展'中的'去年'等\n"\
            "請特別注意提取數字年份，即使它出現在句子的開頭或中間。\n"\
            "如果用戶沒有指定時間範圍，請回答 '未指定'。\n"\
            "請只返回時間範圍或'未指定'，不要添加任何解釋、引號或附加信息。"
        )
        
        keywords_chain = keywords_prompt | llm | StrOutputParser()
        time_period_chain = time_period_prompt | llm | StrOutputParser()
        
        try:
            # 並行執行參數提取任務
            logging.info(f"調用 LLM 提取工具 '{potential_tool}' 的參數...")
            keywords_task = keywords_chain.ainvoke({
                "conversation_history": history_str,
                "user_input": processed_input
            })
            
            time_period_task = time_period_chain.ainvoke({
                "conversation_history": history_str,
                "user_input": processed_input
            })
            
            # 等待所有參數提取完成
            keywords_result, time_period_result = await asyncio.gather(
                keywords_task, time_period_task
            )
            
            # 處理結果
            keywords = keywords_result.strip()
            time_period = time_period_result.strip()
            
            logging.info(f"LLM 提取到的關鍵詞: '{keywords}'")
            logging.info(f"LLM 提取到的時間範圍: '{time_period}'")
            
            # 將有效參數添加到參數字典
            if keywords and keywords.lower() != '未指定':
                tool_parameters['keywords'] = keywords
            
            if time_period and time_period.lower() != '未指定':
                tool_parameters['time_period'] = time_period
                
            # 默認參數
            tool_parameters['limit'] = 3  # 默認返回3條新聞
            
        except Exception as e:
            logging.error(f"LLM 參數提取失敗: {e}", exc_info=True)
            # 提取失敗時，使用默認參數
            tool_parameters = {'limit': 3}
    # --- 結束新增 ---
    
    # else: # 在這裡添加其他工具的參數提取邏輯
    #    pass 

    logging.info(f"解析出的工具參數: {tool_parameters}")
    return {"tool_parameters": tool_parameters}

async def execute_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """執行指定的工具並獲取結果（處理結構化輸出/錯誤）"""
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
    parameter_definitions = tool_info.get("parameters", [])

    if not tool_func:
        logging.error(f"工具 '{tool_name}' 已註冊但未找到有效的執行函數。")
        return {
            "tool_execution_result": f"抱歉，工具 '{tool_name}' 內部配置似乎有誤。",
            "tool_execution_status": "failed_internal_error",
            "tool_used": tool_name
        }

    # *** 關鍵修改：檢查必需參數是否缺失 ***
    missing_required_params = []
    for param_def in parameter_definitions:
        param_name = param_def["name"]
        # 檢查參數是否被定義為必需 (如果未定義 required，則默認為 True)
        is_required = param_def.get("required", True) 
        # 如果參數是必需的，並且在解析出的參數中不存在，則添加到缺失列表
        if is_required and param_name not in tool_parameters:
            missing_required_params.append(param_name)

    if missing_required_params:
        error_msg = f"我需要知道 \'{', '.join(missing_required_params)}\' 才能執行這個操作。你能提供嗎？"
        logging.warning(f"執行工具 {tool_name} 失敗: 缺少必需參數 {missing_required_params}")
        return {
            "tool_execution_result": error_msg,
            "tool_execution_status": "failed_missing_params",
            "tool_used": tool_name
        }

    # 執行工具 (如果沒有缺失必需參數)
    try:
        logging.info(f"開始異步執行工具: {tool_name}，參數: {tool_parameters}")
        # 異步執行工具函數
        result_obj = await tool_func(**tool_parameters) 

        # *** 關鍵修改：檢查返回的是否為包含 error 的字典 ***
        if isinstance(result_obj, dict) and "error" in result_obj:
            # 重要修正：檢查 error 值是否為 False，如果是 False 則表示成功而非錯誤
            if result_obj.get("error") is False:
                # 此情況表示工具成功執行，不應該視為錯誤
                logging.info(f"工具 {tool_name} 成功執行，返回結構化數據，error 字段為 False")
            else:
                # 真正的錯誤情況：error 不為 False（可能是 True 或錯誤消息）
                error_message = str(result_obj["error"])
                logging.warning(f"工具 {tool_name} 執行完成，但返回內部錯誤: {error_message[:100]}...")
                return {
                    "tool_execution_result": error_message, # 返回錯誤信息字符串
                    "tool_execution_status": "failed_tool_error",
                    "tool_used": tool_name
                }
        
        # 成功執行，將結果對象（可能是字典）轉換為 JSON 字符串
        try:
            result_str = json.dumps(result_obj, ensure_ascii=False)
        except TypeError as json_err:
            logging.error(f"工具 {tool_name} 返回結果無法序列化為 JSON: {json_err}", exc_info=True)
            result_str = str(result_obj) # 回退到普通字符串轉換
        
        logging.info(f"工具執行成功: {tool_name}")
        return {
            "tool_execution_result": result_str, # 返回 JSON 字符串或普通字符串
            "tool_execution_status": "success",
            "tool_used": tool_name
        }

    except Exception as e:
        error_message = f"執行工具 {tool_name} 時發生錯誤: {str(e)}"
        logging.error(error_message, exc_info=True)
        return {
            "tool_execution_result": f"抱歉，我在嘗試執行 '{tool_name}' 操作時遇到了技術問題。",
            "tool_execution_status": "failed_exception", # 標記為執行時的異常
            "tool_used": tool_name
        }

def format_tool_result_for_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """格式化工具執行結果以便 LLM 理解"""
    tool_name = state.get("tool_used")
    result = state.get("tool_execution_result")
    status = state.get("tool_execution_status")

    if status == "success":
        # 基礎格式
        formatted = f"\n【你剛剛獲取的資訊】\n"
        
        # 嘗試解析 JSON 結果
        try:
            result_obj = json.loads(result)
            
            # 針對特定工具的特殊格式化
            if tool_name == "search_space_news":
                return format_space_news_result(result_obj)
            elif tool_name == "get_moon_phase":
                return format_moon_phase_result(result_obj)
            # 其他工具類型可在此添加
        except json.JSONDecodeError:
            # 如果不是有效的JSON，使用原始字符串
            pass
        
        formatted += f"這是你透過內部工具找到的相關資訊：\n"
        formatted += f"`\n{result}\n`"
        
        logging.info(f"工具 {tool_name} 結果已格式化，準備整合。長度: {len(formatted)}")
        # 返回 formatted_tool_result 而不是 tool_result (與原始結構保持一致)
        return {
            "formatted_tool_result": formatted,
            "tool_result_summary": result[:150] + "..." if len(result) > 150 else result
        }
    elif status and "failed" in status:
        # 對於失敗，不需要格式化
        return {"formatted_tool_result": None}
    else:
        # 其他狀態（如 skipped）
        return {"formatted_tool_result": None}

def format_space_news_result(result_obj: Dict[str, Any]) -> Dict[str, Any]:
    """格式化太空新聞搜索結果"""
    if result_obj.get("error", False):
        # 如果有錯誤
        return {
            "formatted_tool_result": f"\n【太空新聞搜索失敗】\n{result_obj.get('message', '未知錯誤')}",
            "tool_result_summary": "太空新聞搜索失敗"
        }
    
    search_description = result_obj.get("search_description", "最新")
    search_params = result_obj.get("search_params", {})
    articles = result_obj.get("articles", [])
    count = result_obj.get("count", 0)
    total_count = result_obj.get("total_count", 0)
    note = result_obj.get("note", "")
    
    if count == 0:
        # 針對年份搜索提供更具體的提示
        time_period = search_params.get("time_period", "")
        year_match = re.search(r'(\d{4})', time_period) if time_period else None
        
        if year_match and int(year_match.group(1)) < 2010:
            # 針對過早年份(2010年之前)提供特別說明
            formatted = f"\n【太空新聞搜索結果】\n"
            formatted += f"抱歉，我找不到{search_description}的太空新聞。"
            formatted += f"\n\n請注意，我們使用的太空新聞API可能對較早年份的數據支持有限。"
            formatted += f"\n如果你對{time_period}的太空發展感興趣，可以嘗試詢問更具體的事件或任務，我會盡力提供相關信息。"
            
            return {
                "formatted_tool_result": formatted,
                "tool_result_summary": f"找不到{search_description}的太空新聞，可能因為年代較早"
            }
        else:
            # 一般情況
            return {
                "formatted_tool_result": f"\n【太空新聞搜索結果】\n找不到{search_description}的太空新聞。",
                "tool_result_summary": f"找不到{search_description}的太空新聞"
            }
    
    # 構建格式化的新聞內容
    formatted = f"\n【太空新聞搜索結果】\n"
    
    # 如果有備註，說明是備選新聞
    if note:
        formatted += f"未找到完全符合「{search_description}」的太空新聞，以下是最新太空新聞：\n\n"
    else:
        formatted += f"關於「{search_description}」的太空新聞，找到 {count} 條結果（共 {total_count} 條匹配）：\n\n"
    
    for i, article in enumerate(articles):
        formatted += f"【新聞 {i+1}】{article.get('title')}\n"
        formatted += f"來源: {article.get('news_site')} | 發布時間: {article.get('published_at')}\n"
        formatted += f"摘要: {article.get('summary')}\n"
        if i < len(articles) - 1:  # 如果不是最後一條新聞，添加分隔符
            formatted += f"\n{'='*50}\n\n"
    
    # 提取關鍵信息作為摘要
    if note:
        summary = f"找不到{search_description}的太空新聞，改顯示最新太空新聞"
    else:
        summary = f"{search_description}太空新聞 {count} 條"
        if articles:
            first_title = articles[0].get('title', '')
            summary = f"{summary}: {first_title[:30]}..."
    
    return {
        "formatted_tool_result": formatted,
        "tool_result_summary": summary
    }

def format_moon_phase_result(result_obj: Dict[str, Any]) -> Dict[str, Any]:
    """格式化月相查詢結果"""
    if "error" in result_obj:
        return {
            "formatted_tool_result": f"\n【月相查詢失敗】\n{result_obj.get('error', '未知錯誤')}",
            "tool_result_summary": "月相查詢失敗"
        }
    
    query_date = result_obj.get("query_date", "未知日期")
    phase_name_en = result_obj.get("phase_name_en", "未知月相")
    phase_name_zh = result_obj.get("phase_name_zh", "未知月相")
    
    formatted = f"\n【月相查詢結果】\n"
    formatted += f"日期: {query_date}\n"
    formatted += f"英文月相名稱: {phase_name_en}\n"
    formatted += f"中文月相名稱: {phase_name_zh}\n"
    
    # 提供月相描述和觀測建議
    phase_descriptions = {
        "New Moon": "新月時，月球在地球和太陽之間，月球被陰影覆蓋，幾乎不可見。",
        "Waxing Crescent": "眉月呈現為一道細細的弧光，這時可以看到月球的一小部分被陽光照亮。",
        "First Quarter": "上弦月時，月球的一半被照亮，呈現為'D'形。",
        "Waxing Gibbous": "盈凸月時，月球大部分被照亮，接近但還未到達滿月。",
        "Full Moon": "滿月時，整個月球表面都被陽光照亮，是最亮的月相。",
        "Waning Gibbous": "虧凸月是滿月後的階段，月球光亮面積逐漸減少。",
        "Last Quarter": "下弦月時，月球的另一半被照亮，呈現為'C'形。",
        "Waning Crescent": "殘月是月相周期的最後階段，只有一小部分月球被照亮。"
    }
    
    if phase_name_en in phase_descriptions:
        formatted += f"\n描述: {phase_descriptions[phase_name_en]}\n"
    
    return {
        "formatted_tool_result": formatted,
        "tool_result_summary": f"{query_date} 的月相是 {phase_name_zh}"
    }

def integrate_tool_result(state: Dict[str, Any]) -> Dict[str, Any]:
    """將工具執行結果整合到對話狀態中 - 處理結構化結果或錯誤字符串"""
    status = state.get("tool_execution_status")
    # tool_execution_result 現在可能是 JSON 字符串 (成功) 或錯誤信息字符串 (失敗)
    result_str = state.get("tool_execution_result", "") 
    tool_used = state.get("tool_used")

    update_dict = {}

    if status == "success":
        logging.info(f"工具 {tool_used} 執行成功，設置 tool_response 模板和結果。")
        # 將成功的 JSON 字符串設置到 tool_result
        update_dict["tool_result"] = result_str 
        update_dict["prompt_template_key"] = "tool_response"
        update_dict["tool_error"] = None
    elif status and "failed" in status: # 包括 failed_tool_error, failed_exception 等
        logging.warning(f"工具 {tool_used} 執行失敗 (狀態: {status})，設置 tool_error_response 模板和錯誤信息。")
        update_dict["prompt_template_key"] = "tool_error_response"
        update_dict["tool_error"] = result_str # 將錯誤信息字符串設置到 tool_error
        update_dict["tool_result"] = None
    else:
        logging.debug(f"工具狀態為 {status}，不改變提示模板或錯誤狀態。")

    return update_dict 