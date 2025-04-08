from __future__ import annotations
# --- This line must be the very first line of the file ---

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
from google.generativeai.types import GenerationConfig

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

# --- 新增 Keyframe 相關定義 ---

# 允許的情緒標籤列表 (來自 TODO 文件)
ALLOWED_EMOTION_TAGS = ["neutral", "happy", "sad", "angry", "surprised", "fearful", "disgusted", "thinking", "listening"]

# 用於第二次 LLM 調用的 JSON Schema (期望 LLM 只返回 keyframes 列表)
keyframes_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "tag": {
                "type": "string",
                "enum": ALLOWED_EMOTION_TAGS, # 限制標籤
                "description": "預定義的情緒標籤"
            },
            "proportion": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "情緒發生的相對時間比例 (0.0 到 1.0)"
            }
        },
        "required": ["tag", "proportion"]
    }
}

# 默認的中性關鍵幀 (用於回退)
DEFAULT_NEUTRAL_KEYFRAMES = [{"tag": "neutral", "proportion": 0.0}, {"tag": "neutral", "proportion": 1.0}]

def validate_and_fix_keyframes(raw_keyframes: Optional[List[Dict]]) -> List[Dict]:
    """
    驗證、排序並修正從 LLM 獲取的 keyframes 列表。
    確保格式正確、標籤有效、比例在範圍內，並包含首尾幀。
    如果驗證失敗，返回默認的中性關鍵幀。
    """
    if not isinstance(raw_keyframes, list) or not raw_keyframes:
        logging.warning("收到的 keyframes 不是列表或為空，返回默認值。")
        return DEFAULT_NEUTRAL_KEYFRAMES.copy()

    valid_keyframes = []
    seen_proportions = set()

    for kf in raw_keyframes:
        if not isinstance(kf, dict):
            logging.warning(f"Keyframe 不是字典格式: {kf}，已跳過。")
            continue

        tag = kf.get("tag")
        proportion = kf.get("proportion")

        # 驗證類型和內容
        if not isinstance(tag, str) or tag not in ALLOWED_EMOTION_TAGS:
            logging.warning(f"無效或不允許的情緒標籤: {tag}，已跳過 keyframe: {kf}")
            continue
        if not isinstance(proportion, (int, float)) or not (0.0 <= proportion <= 1.0):
            logging.warning(f"無效的時間比例: {proportion}，必須在 0.0 到 1.0 之間。已跳過 keyframe: {kf}")
            continue
        
        # 避免重複的 proportion
        if proportion in seen_proportions:
            logging.warning(f"發現重複的時間比例: {proportion}，已跳過 keyframe: {kf}")
            continue
            
        valid_keyframes.append({"tag": tag, "proportion": proportion})
        seen_proportions.add(proportion)

    if not valid_keyframes:
        logging.warning("沒有有效的 keyframes 被解析，返回默認值。")
        return DEFAULT_NEUTRAL_KEYFRAMES.copy()

    # 按 proportion 排序
    valid_keyframes.sort(key=lambda x: x["proportion"])

    # 確保首幀 proportion 為 0.0
    if valid_keyframes[0]["proportion"] != 0.0:
        logging.info("Keyframes 缺少 0.0 比例的幀，自動添加 neutral 首幀。")
        # 使用第一個有效幀的 tag 或 neutral
        start_tag = valid_keyframes[0].get("tag", "neutral") 
        valid_keyframes.insert(0, {"tag": start_tag, "proportion": 0.0})


    # 確保尾幀 proportion 為 1.0
    if valid_keyframes[-1]["proportion"] < 1.0:
        logging.info("Keyframes 缺少 1.0 比例的幀，自動添加 neutral 尾幀。")
         # 使用最後一個有效幀的 tag 或 neutral
        end_tag = valid_keyframes[-1].get("tag", "neutral")
        valid_keyframes.append({"tag": end_tag, "proportion": 1.0})
    elif valid_keyframes[-1]["proportion"] > 1.0: # 理論上 schema 會限制，但做個防禦
        logging.warning("最後一個 keyframe 的 proportion 超過 1.0，強制設為 1.0。")
        valid_keyframes[-1]["proportion"] = 1.0


    logging.info(f"Keyframes 驗證和修正完成，共 {len(valid_keyframes)} 幀。")
    return valid_keyframes

# --- 重新添加/確保 Keyframe 分析節點定義在頂層 ---

async def analyze_keyframes_node(state: DialogueState) -> Dict[str, Any]:
    """
    分析 LLM 生成的純文本回應，調用第二次 LLM (使用 JSON 模式) 來提取情緒關鍵幀。
    """
    llm_response_raw = state.get("llm_response_raw", "")
    llm = state.get("_context", {}).get("llm")

    if not llm_response_raw:
        logging.warning("analyze_keyframes_node: 原始回應為空，無法分析 keyframes。返回默認值。")
        return {"emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy()}
    if not llm:
        logging.error("analyze_keyframes_node: LLM 實例未在上下文中提供。返回默認值。")
        return {"emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy()}

    analysis_prompt = f"""
請仔細分析以下這段文本，識別其中表達的情感變化，並生成一個情緒關鍵幀列表 (keyframes)。
每個關鍵幀應包含 'tag' (情緒標籤) 和 'proportion' (相對時間比例 0.0 到 1.0)。
請確保第一個關鍵幀的 proportion 為 0.0，最後一個為 1.0。
允許的情緒標籤為: {', '.join(ALLOWED_EMOTION_TAGS)}。

文本內容：
"{llm_response_raw}"

請嚴格按照以下 JSON Schema 格式輸出結果 (僅輸出 JSON 陣列本身)：
{json.dumps(keyframes_schema, indent=2)}
"""

    generation_config = GenerationConfig(
        response_mime_type='application/json',
    )

    try:
        logging.info("analyze_keyframes_node: 開始調用 LLM 進行 keyframe 分析...")
        analysis_response = await llm.ainvoke(
            analysis_prompt,
            config={"generation_config": generation_config}
        )

        raw_keyframes_data = analysis_response.content
        parsed_keyframes = None

        if isinstance(raw_keyframes_data, str):
            # --- 新增：清理 Markdown 標記 ---
            cleaned_data = raw_keyframes_data.strip()
            if cleaned_data.startswith("```json"):
                cleaned_data = cleaned_data[7:] # 移除 ```json
            if cleaned_data.endswith("```"):
                cleaned_data = cleaned_data[:-3] # 移除 ```
            cleaned_data = cleaned_data.strip() # 再次去除可能的空白
            # --- 清理結束 ---
            try:
                # 使用清理後的數據進行解析
                parsed_keyframes = json.loads(cleaned_data) 
                logging.info(f"analyze_keyframes_node: LLM 返回 JSON 字符串，已成功解析。")
            except json.JSONDecodeError as e:
                # 記錄原始數據和清理後的數據以供調試
                logging.error(f"analyze_keyframes_node: 無法解析 LLM 返回的 JSON 字符串: {e}\n原始字符串: '{raw_keyframes_data}'\n清理後: '{cleaned_data}'")
        elif isinstance(raw_keyframes_data, list):
             parsed_keyframes = raw_keyframes_data
             logging.info(f"analyze_keyframes_node: LLM 直接返回了 keyframes 列表。")
        else:
            logging.warning(f"analyze_keyframes_node: LLM 未按預期返回 JSON 字符串或列表，收到類型 {type(raw_keyframes_data)}。 內容: {raw_keyframes_data}")

        if parsed_keyframes is not None and isinstance(parsed_keyframes, list):
            validated_keyframes = validate_and_fix_keyframes(parsed_keyframes)
            logging.info(f"analyze_keyframes_node: Keyframes 驗證完成，數量: {len(validated_keyframes)}")
            return {"emotional_keyframes": validated_keyframes}
        else:
            logging.error("analyze_keyframes_node: 無法從 LLM 獲取有效的 keyframes 列表。返回默認值。")
            return {"emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy()}

    except Exception as e:
        logging.error(f"analyze_keyframes_node: LLM 調用或處理失敗: {e}", exc_info=True)
        return {"emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy()}

# --- 添加結束 ---

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
    llm_response_raw: str         # LLM原始回應 (純文本)
    emotional_keyframes: Optional[List[Dict]] = None # <--- 新增：用於存儲分析出的情緒關鍵幀
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
                "description": "獲取太空探索、天文發現或航天工業相關的新聞標題和摘要，支持關鍵字搜索和時間範圍篩選（包括特定年份如'2020年'）。",
                "parameters": [
                    {"name": "keywords", "type": "string", "description": "要搜索的關鍵詞或主題，例如 'NASA', 'SpaceX', '火星'", "required": False},
                    {"name": "time_period", "type": "string", "description": "指定的時間範圍，可以是'今天'、'昨天'、'本週'、'本月'、'今年'，或特定年份如'2020年'", "required": False}
                ]
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
        workflow.add_node("analyze_keyframes", self._analyze_keyframes_node_wrapper)
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
                "continue": "analyze_keyframes"
            }
        )
        
        workflow.add_edge("analyze_keyframes", "post_process")
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
    
    async def _analyze_keyframes_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝 Keyframe 分析節點，注入 LLM 實例"""
        if "_context" not in state:
            state["_context"] = {}
        # 確保 LLM 實例在上下文中 (通常 call_llm_node_wrapper 已注入)
        if "llm" not in state["_context"]:
            state["_context"]["llm"] = self.llm
        # 移除冗余的檢查，因為上面已經檢查過
        # if "llm" not in state["_context"]:
        #      logging.error("_analyze_keyframes_node_wrapper: LLM not found in context!")
        #      # 返回一個包含錯誤或默認值的狀態更新
        #      return {"emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(), "system_alert": "LLM context missing for keyframe analysis"}
        return await analyze_keyframes_node(state)
    
    async def _store_memory_node_wrapper(self, state: DialogueState) -> Dict[str, Any]:
        """包裝記憶儲存節點，注入記憶系統"""
        if "_context" not in state:
            state["_context"] = {}
        state["_context"]["memory_system"] = self.memory_system
        return await store_memory_node(state)
    
    async def generate_response(self, user_text: str, messages: List[BaseMessage], 
                                character_state: Dict[str, Any], current_task: Optional[str] = None,
                                tasks_history: Optional[List[Dict]] = None,
                                current_intent: Optional[str] = None) -> Dict[str, Any]:
        """執行對話圖並返回最終回應和情緒關鍵幀"""
        
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
            "tasks_history": tasks_history if tasks_history is not None else [],
            
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
            "emotional_keyframes": None,
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

        # 格式化角色狀態並添加到初始狀態
        initial_state["character_state_prompt"] = format_character_state(initial_state["character_state"])

        try:
            final_state = await self.app.ainvoke(initial_state)
            
            # 從最終狀態提取回應和 keyframes
            final_response = final_state.get("final_response", "對不起，我好像遇到了一些技術問題。")
            emotional_keyframes = final_state.get("emotional_keyframes") # 可能為 None
            updated_messages = final_state.get("messages", messages) # 返回更新後的消息歷史
            
            logging.info(f"Dialogue graph execution successful. Final response: '{final_response}', Keyframes: {emotional_keyframes is not None}")
            
            # 返回包含回應和 keyframes 的字典
            return {
                "final_response": final_response,
                "emotional_keyframes": emotional_keyframes,
                "updated_messages": updated_messages # 同時返回更新後的消息歷史
            }

        except Exception as e:
            logging.error(f"對話圖執行失敗: {e}", exc_info=True)
            # 返回包含錯誤訊息和預設值的字典，避免 Attribute Error
            return {
                "final_response": "糟糕，我的思緒好像打結了，能再說一次嗎？",
                "emotional_keyframes": DEFAULT_NEUTRAL_KEYFRAMES.copy(), # 返回默認值
                "updated_messages": messages, # 返回原始消息
                "error": str(e) # 可選：添加錯誤訊息
            }
    
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