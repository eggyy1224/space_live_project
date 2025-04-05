"""
基於 LangGraph 的對話流程圖 - 增強版
提供更健壯的對話管理、輸入處理、與多層記憶架構
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, TypedDict, Optional, Tuple

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, END

from .memory_system import MemorySystem
from .prompts import DIALOGUE_STYLES, PROMPT_TEMPLATES
from .graph_nodes.input_processing import preprocess_input_node
from .graph_nodes.memory_handling import retrieve_memory_node, filter_memory_node, store_memory_node
from .graph_nodes.prompting import select_prompt_and_style_node, build_prompt_node, format_character_state
from .graph_nodes.llm_interaction import call_llm_node, handle_llm_error, post_process_node
from .graph_nodes.tool_processing import detect_tool_intent, parse_tool_parameters, execute_tool, format_tool_result_for_llm, integrate_tool_result
from .tools.web_tools import search_wikipedia
from .tools.space_tools import search_space_news
from .tools.space_tools import get_iss_info, get_moon_phase

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定義對話圖的狀態結構
class DialogueState(TypedDict):
    # --- 輸入與上下文 ---
    raw_user_input: str           # 原始用戶輸入
    processed_user_input: str     # 經過初步處理/淨化的用戶輸入
    input_classification: Dict[str, Any]  # 輸入分類結果 (e.g., {'type': 'normal'/'repetitive'/'gibberish'/'question', 'sentiment': 'positive'})
    messages: List[BaseMessage]   # 完整對話歷史
    
    # --- 記憶 ---
    retrieved_memories: List[Any] # 原始檢索到的記憶
    filtered_memories: str        # 經過篩選和格式化的記憶 (用於提示)
    persona_info: str             # 檢索到的角色資訊
    
    # --- 意圖與任務 ---
    current_intent: Optional[str] # 識別出的使用者意圖
    current_task: Optional[str]   # 當前任務 (若有)
    tasks_history: List[Dict]     # 任務歷史
    
    # --- 工具呼叫 ---
    has_tool_intent: Optional[bool]         # 是否需要使用工具
    potential_tool: Optional[str]           # 可能要使用的工具
    tool_confidence: Optional[float]        # 工具意圖識別的信心度
    tool_parameters: Optional[Dict[str, Any]]  # 工具參數
    tool_execution_result: Optional[str]    # 工具執行結果
    tool_execution_status: Optional[str]    # 工具執行狀態
    tool_used: Optional[str]                # 實際使用的工具
    formatted_tool_result: Optional[str]    # 格式化後的工具結果 (中間步驟)
    tool_result: Optional[str]              # 最終給模板使用的工具結果
    tool_error: Optional[str]               # 最終給模板使用的工具錯誤
    
    # --- 生成控制 ---
    prompt_template_key: str      # 選用的提示模板名稱 (e.g., 'standard', 'clarification', 'error')
    prompt_inputs: Dict[str, Any] # 最終構建的提示輸入
    dialogue_style: str           # 選定的對話風格
    character_state_prompt: str   # 格式化的角色狀態
    
    # --- 角色狀態 ---
    character_state: Dict[str, Any] # 角色狀態
    
    # --- 回應與狀態 ---
    llm_response_raw: str         # LLM原始回應
    final_response: str           # 最終處理後的回應
    error_count: int              # 連續錯誤計數
    system_alert: Optional[str]   # 系統內部的警告或標註 (e.g., 'high_repetition_detected')
    should_store_memory: bool     # 是否應該儲存這輪對話到長期記憶
    
    # --- 上下文與依賴 ---
    _context: Dict[str, Any]      # 儲存上下文依賴 (memory_system, llm 等)

class DialogueGraph:
    """基於 LangGraph 的對話圖 - 實現更複雜的有狀態對話流程"""
    
    def __init__(self, memory_system: MemorySystem, llm: ChatGoogleGenerativeAI, persona_name: str = "星際小可愛"):
        self.memory_system = memory_system
        self.llm = llm
        self.persona_name = persona_name
        
        # 保存初始角色狀態
        self.initial_character_state = {
            "health": 100,
            "mood": 70,
            "energy": 80,
            "task_success": 0,
            "days_in_space": 1
        }
        
        # 初始化提示模板
        self.prompt_templates = {
            key: PromptTemplate(
                template=template,
                input_variables=[
                    "conversation_history", "filtered_memories", "persona_info",
                    "user_message", "character_state", "current_task",
                    "dialogue_style", "persona_name", "tool_result", "tool_error"
                ] if "tool" in key else [
                    "conversation_history", "filtered_memories", "persona_info",
                    "user_message", "character_state", "current_task",
                    "dialogue_style", "persona_name"
                ]
            ) for key, template in PROMPT_TEMPLATES.items()
        }
        
        # 註冊可用的工具
        self.available_tools = {
            "search_wikipedia": {
                "function": search_wikipedia,
                "description": "當用戶詢問關於特定人物、地點、事件或概念的定義或一般知識時，使用此工具從維基百科查找信息。",
                "parameters": [
                    {"name": "query", "type": "string", "description": "要查詢的主題或關鍵字"}
                ]
            },
            "search_space_news": {
                "function": search_space_news,
                "description": "獲取最新的幾條太空探索、天文發現或航天工業相關的新聞標題和摘要。",
                "parameters": [] # 此工具通常不需要參數
            },
            "get_iss_info": {
                "function": get_iss_info,
                "description": "查詢國際太空站 (ISS) 的即時位置（經緯度）以及當前在太空中的總人數和在 ISS 上的人數。",
                "parameters": [] # 無需參數
            },
            "get_moon_phase": {
                "function": get_moon_phase,
                "description": "查詢指定日期的月相。如果用戶沒有指定日期，則默認查詢今天。",
                "parameters": [
                    {"name": "date_str", "type": "string", "description": "要查詢的日期，格式可以是 YYYY-MM-DD，或者是 '今天'、'明天'、'昨天'。如果省略，則為今天。", "required": False}
                ]
            }
        }
        
        # 構建對話圖
        self.graph = self._build_graph()
        
        # 編譯圖
        self.app = self.graph.compile()
        
        logging.info("增強版 DialogueGraph 初始化完成，已註冊工具")
        
    def _build_graph(self) -> StateGraph:
        """構建對話圖"""
        
        # 創建狀態圖
        workflow = StateGraph(DialogueState)
        
        # 添加節點 - 輸入處理和記憶檢索
        workflow.add_node("preprocess_input", self._preprocess_input_node_wrapper)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node_wrapper)
        workflow.add_node("filter_memory", filter_memory_node)
        
        # 添加節點 - 工具處理
        workflow.add_node("detect_tool_intent", self._detect_tool_intent_wrapper)
        workflow.add_node("parse_tool_parameters", self._parse_tool_parameters_wrapper)
        workflow.add_node("execute_tool", self._execute_tool_wrapper)
        workflow.add_node("format_tool_result", format_tool_result_for_llm)
        workflow.add_node("integrate_tool_result", integrate_tool_result)
        
        # 添加節點 - 提示構建和 LLM 生成
        workflow.add_node("select_prompt_and_style", select_prompt_and_style_node)
        workflow.add_node("build_prompt", self._build_prompt_node_wrapper)
        workflow.add_node("call_llm", self._call_llm_node_wrapper)
        workflow.add_node("post_process", post_process_node)
        workflow.add_node("store_memory", self._store_memory_node_wrapper)
        
        # 定義基本流程
        workflow.set_entry_point("preprocess_input")
        workflow.add_edge("preprocess_input", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "filter_memory")
        workflow.add_edge("filter_memory", "detect_tool_intent")
        
        # 分支流程 - 工具處理
        workflow.add_conditional_edges(
            "detect_tool_intent",
            lambda state: "tool_path" if state.get("has_tool_intent") else "normal_path",
            {
                "tool_path": "parse_tool_parameters",
                "normal_path": "select_prompt_and_style"
            }
        )
        
        # 工具處理流程
        workflow.add_edge("parse_tool_parameters", "execute_tool")
        workflow.add_edge("execute_tool", "format_tool_result")
        workflow.add_edge("format_tool_result", "integrate_tool_result")
        workflow.add_edge("integrate_tool_result", "select_prompt_and_style")
        
        # 正常處理流程
        workflow.add_edge("select_prompt_and_style", "build_prompt")
        workflow.add_edge("build_prompt", "call_llm")
        
        # LLM 調用後處理
        workflow.add_conditional_edges(
            "call_llm",
            handle_llm_error,
            {
                "retry": "select_prompt_and_style",
                "continue": "post_process"
            }
        )
        
        workflow.add_edge("post_process", "store_memory")
        workflow.add_edge("store_memory", END)
        
        return workflow
    
    # 節點包裝器 - 負責將依賴注入到節點的 state 中
    async def _preprocess_input_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝輸入預處理節點，注入上下文"""
        # 將類的實例依賴注入 state 的 _context 中
        if "_context" not in state:
            state["_context"] = {}
        return await preprocess_input_node(state)
    
    async def _retrieve_memory_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝記憶檢索節點，注入記憶系統"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["memory_system"] = self.memory_system
        return await retrieve_memory_node(state)
    
    async def _detect_tool_intent_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝工具意圖檢測節點，注入可用工具列表"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["available_tools"] = self.available_tools
        state["_context"]["llm"] = self.llm
        return await detect_tool_intent(state)
    
    async def _parse_tool_parameters_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝工具參數解析節點，注入可用工具列表"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["available_tools"] = self.available_tools
        state["_context"]["llm"] = self.llm
        return await parse_tool_parameters(state)
    
    async def _execute_tool_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝工具執行節點，注入可用工具列表"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["available_tools"] = self.available_tools
        return await execute_tool(state)
    
    def _build_prompt_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝提示構建節點，注入角色名稱"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["persona_name"] = self.persona_name
        return build_prompt_node(state)
    
    async def _call_llm_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝 LLM 調用節點，注入 LLM 和提示模板"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["llm"] = self.llm
        state["_context"]["prompt_templates"] = self.prompt_templates
        return await call_llm_node(state)
    
    async def _store_memory_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝記憶儲存節點，注入記憶系統"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["memory_system"] = self.memory_system
        return await store_memory_node(state)
    
    async def generate_response(self, user_text: str, messages: List[BaseMessage], 
                                character_state: Dict[str, Any], current_task: Optional[str] = None,
                                tasks_history: Optional[List[Dict]] = None,
                                current_intent: Optional[str] = None) -> Tuple[str, List[BaseMessage]]:
        """生成回應主方法 - 驅動整個對話圖"""
        
        # 準備初始狀態
        initial_state: DialogueState = {
            # 輸入
            "raw_user_input": user_text,
            "processed_user_input": user_text,  # 將在流程中處理
            "input_classification": {},  # 將在流程中填充
            "messages": messages + [HumanMessage(content=user_text)],  # 添加當前用戶輸入
            
            # 記憶 (將在流程中填充)
            "retrieved_memories": [],
            "filtered_memories": "",
            "persona_info": "",
            
            # 意圖與任務
            "current_intent": current_intent,
            "current_task": current_task,
            "tasks_history": tasks_history or [],
            
            # 工具呼叫 (將在流程中填充，並確保關鍵鍵存在)
            "has_tool_intent": False,
            "potential_tool": None,
            "tool_confidence": 0.0,
            "tool_parameters": {},
            "tool_execution_result": "",
            "tool_execution_status": "not_started",
            "tool_used": None,
            "formatted_tool_result": None, # 初始為 None
            "tool_result": None,           # 初始為 None
            "tool_error": None,            # 初始為 None
            
            # 生成控制 (將在流程中填充)
            "prompt_template_key": "standard",
            "prompt_inputs": {},
            "dialogue_style": "",
            "character_state_prompt": "",
            
            # 角色狀態
            "character_state": character_state.copy(),
            
            # 回應與錯誤處理 (將在流程中填充)
            "llm_response_raw": "",
            "final_response": "",
            "error_count": 0,
            "system_alert": None,
            "should_store_memory": True,
            
            # 上下文和依賴
            "_context": {
                "memory_system": self.memory_system,
                "llm": self.llm,
                "prompt_templates": self.prompt_templates,
                "persona_name": self.persona_name,
                "available_tools": self.available_tools
            }
        }
        
        try:
            # 執行圖，獲取最終狀態
            logging.info(f"開始執行對話圖: 用戶輸入 {user_text[:20]}...")
            final_state = await self.app.ainvoke(initial_state)
            
            # 從最終狀態提取回應和更新的消息列表
            final_response = final_state["final_response"]
            updated_messages = final_state["messages"]
            
            # 如果使用了工具，記錄相關信息
            if final_state.get("tool_used"):
                logging.info(f"成功使用工具: {final_state['tool_used']}")
                
                # 添加一個系統消息到對話歷史，記錄工具使用情況
                tool_summary = f"系統: 使用工具 '{final_state['tool_used']}' 處理請求"
                if "tool_result_summary" in final_state:
                    tool_summary += f"\n結果: {final_state['tool_result_summary']}"
                
                # 將系統消息添加到內部跟踪，但不返回給用戶
                system_message = SystemMessage(content=tool_summary)
                updated_messages.append(system_message)
            
            # 確保將最終的 AIMessage 加入 updated_messages
            if updated_messages and isinstance(updated_messages[-1], HumanMessage):
                updated_messages.append(AIMessage(content=final_response))
            elif not updated_messages:
                # 處理初始消息列表為空的情況
                updated_messages = [HumanMessage(content=user_text), AIMessage(content=final_response)]
            
            return final_response, updated_messages
            
        except Exception as e:
            logging.error(f"對話圖執行失敗: {e}", exc_info=True)
            error_response = "抱歉，我的系統出了點問題，請稍後再試。"
            updated_messages = messages + [HumanMessage(content=user_text), AIMessage(content=error_response)]
            return error_response, updated_messages
    
    def update_character_state(self, character_state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新角色狀態，支持增量更新，返回更新後的新狀態"""
        updated_state = character_state.copy()
        changed = False
        
        for key, value in updates.items():
            if key in updated_state:
                old_value = updated_state[key]
                current_value = old_value
                try:
                    # 嘗試增量更新 (例如 'mood': '+5' 或 'energy': '-10')
                    if isinstance(value, str) and value.startswith(('+', '-')):
                        delta = int(value)
                        if isinstance(current_value, (int, float)):
                            current_value += delta
                        else:
                            logging.warning(f"無法對非數值狀態 '{key}' 進行增量更新: {value}")
                            continue
                    else:
                        # 嘗試直接設置數值或字串
                        try:
                            # 嘗試轉換為數值類型
                            num_value = int(value) if isinstance(updated_state[key], int) else float(value)
                            current_value = num_value
                        except (ValueError, TypeError):
                            # 直接賦值 (非數值狀態)
                            current_value = value
                    
                    # 只有當值確實改變時才更新
                    if current_value != old_value:
                        updated_state[key] = current_value
                        changed = True
                        
                        # 確保數值在合理範圍內
                        if isinstance(current_value, (int, float)) and key in ["health", "mood", "energy"]:
                            updated_state[key] = max(0, min(100, current_value))
                        
                        logging.info(f"角色狀態更新: {key} 從 {old_value} 變為 {updated_state[key]}")
                
                except Exception as e:
                    logging.warning(f"處理狀態更新時出錯: {key}={value}, 錯誤: {e}")
        
        # 記錄更新後的狀態
        if changed:
            state_text = format_character_state(updated_state)
            logging.info(f"更新後角色狀態: {state_text}")
        
        return updated_state
    
    def reset(self) -> Dict[str, Any]:
        """重置角色狀態為初始值"""
        return self.initial_character_state.copy() 