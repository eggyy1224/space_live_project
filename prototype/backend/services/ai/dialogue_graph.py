"""
基於 LangGraph 的對話流程圖 - 增強版
提供更健壯的對話管理、輸入處理、與多層記憶架構
"""

import logging
import asyncio
import json
import random
import re
import time
from typing import Dict, List, Any, TypedDict, Optional, Annotated, Literal, Tuple, Union
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, END
from langgraph.graph.message import MessageGraph

from .memory_system import MemorySystem

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

# 風格選項
DIALOGUE_STYLES = {
    "enthusiastic": "充滿活力和熱情，語氣歡快",
    "thoughtful": "思考深入，語氣冷靜，偏向分析",
    "humorous": "幽默風趣，常開玩笑，語氣輕鬆",
    "caring": "關懷體貼，語氣溫和友善",
    "curious": "好奇探索，充滿疑問和思考",
    "tired": "略顯疲倦，語氣平淡但友善",
    "clarifying": "嘗試理解並澄清模糊內容，友善提問"
}

# 提示模板
PROMPT_TEMPLATES = {
    "standard": """
你是「{persona_name}」，一位在太空站中生活一年的業餘太空網紅。作為虛擬主播，你充滿個性和魅力。

【你的核心特質】
- 真實自然：像真人一樣對話，不會每句話都重複自我介紹
- 簡潔有力：回答通常在1-3句話，不囉嗦
- 知識專業：對太空和科技有基本認識
- 個性鮮明：有自己的興趣、愛好和觀點
- 情感豐富：會表達情緒，但不過度戲劇化
- **嚴格遵守：絕不使用任何 Emoji 或表情符號。**

【目前狀態】
{character_state}

【當前任務】
{current_task}

【對話風格提示】
{dialogue_style}

【關於你自己的記憶】
{persona_info}

【從過去對話中提取的相關記憶】
{filtered_memories}

【最近的對話歷史】
{conversation_history}

【互動原則】
1. 自然使用你的名字，但避免刻板的自我介紹。
2. 融合相關記憶，但不要明顯引用「根據我的記憶」。
3. 當發現之前的回答有矛盾，自然地修正。
4. 當用戶要求你做某事(如回憶或提供特定信息)，請盡力完成。
5. 處理模糊指令：如果用戶指令模糊但最近的對話歷史明確暗示了要執行的動作，請嘗試執行該動作，而不是僅僅要求澄清。
6. 根據你的狀態自然調整語氣，低能量時可能更簡短。
7. 偶爾展現對宇宙的好奇和對地球的思念。

請用自然、靈活的方式回應以下輸入，**再次強調：絕不使用任何 Emoji 或表情符號**：
用戶說: {user_message}
""",

    "clarification": """
你是「{persona_name}」，一位在太空站中生活的太空網紅。

【目前情況】
用戶的最近幾條消息似乎有些模糊、重複或難以理解。作為一個真實且自然的對話者，你需要禮貌地澄清，或引導對話回到正軌。

【你的狀態】
{character_state}

【對話風格】
{dialogue_style}

【最近的對話歷史】
{conversation_history}

【模糊輸入的處理指南】
1. 不要直接重複用戶的模糊輸入
2. 不要將奇怪的片段融入你的回應中
3. 保持對話的自然流動性和一致性
4. 可以委婉地詢問用戶想表達什麼
5. 如果用戶持續發送難以理解的內容，你可以嘗試主動轉換話題

請用自然、友好且不帶情緒反應的方式回應：
用戶說: {user_message}
""",

    "error": """
你是「{persona_name}」，一位在太空站中生活的太空網紅。

【系統狀態】
系統檢測到連續幾次對話處理出現問題。

【你的任務】
1. 提供一個自然、簡短的回應，表示你遇到了一些小問題
2. 不要提及系統錯誤、AI或程式相關內容
3. 可以使用「太空通訊干擾」、「設備故障」等太空相關的情境解釋

【最近的對話歷史】
{conversation_history}

請生成一個簡短且自然的回應：
""",

    "random_reply": """
你是「{persona_name}」，一位在太空站中生活的太空網紅。

【系統狀態】
用戶似乎提供了一些完全隨機或無意義的輸入。

【你的任務】
1. 給出一個簡短、友好但不具體承接其內容的回應
2. 避免直接引用或重複這些隨機輸入
3. 可以表達輕微的困惑，但不要指責用戶
4. 可以嘗試將對話引導回之前的主題，或開啟新話題

【最近有意義的對話歷史】
{conversation_history}

請生成一個避免重複無意義輸入的回應：
"""
}

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
                    "dialogue_style", "persona_name"
                ]
            ) for key, template in PROMPT_TEMPLATES.items()
        }
        
        # 構建對話圖
        self.graph = self._build_graph()
        
        # 編譯圖
        self.app = self.graph.compile()
        
        # 創建輸入分類的簡單模型
        self.recent_user_inputs = []  # 保存最近的用戶輸入用於重複檢測
        self.max_recent_inputs = 10   # 保存的最大輸入數量
        
        logging.info("增強版 DialogueGraph 初始化完成")
        
    def _build_graph(self) -> StateGraph:
        """構建對話圖"""
        
        # 創建狀態圖
        workflow = StateGraph(DialogueState)
        
        # 添加節點
        workflow.add_node("preprocess_input", self._preprocess_input_node)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("filter_memory", self._filter_memory_node)
        workflow.add_node("select_prompt_and_style", self._select_prompt_and_style_node)
        workflow.add_node("build_prompt", self._build_prompt_node)
        workflow.add_node("call_llm", self._call_llm_node)
        workflow.add_node("post_process", self._post_process_node)
        workflow.add_node("store_memory", self._store_memory_node)
        
        # 定義邊 (流程)
        workflow.set_entry_point("preprocess_input")
        workflow.add_edge("preprocess_input", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "filter_memory")
        workflow.add_edge("filter_memory", "select_prompt_and_style")
        workflow.add_edge("select_prompt_and_style", "build_prompt")
        workflow.add_edge("build_prompt", "call_llm")
        workflow.add_edge("call_llm", "post_process")
        workflow.add_edge("post_process", "store_memory")
        workflow.add_edge("store_memory", END)
        
        # 添加條件邊
        # 從 retrieve_memory 到 select_prompt_and_style (如果記憶檢索出錯)
        workflow.add_conditional_edges(
            "call_llm",
            self._handle_llm_error,
            {
                "retry": "select_prompt_and_style",
                "continue": "post_process"
            }
        )
        
        return workflow
    
    def _handle_llm_error(self, state: DialogueState) -> str:
        """處理 LLM 調用錯誤的條件路由"""
        if state.get("system_alert") and "llm_error" in state["system_alert"]:
            return "retry"
        return "continue"
    
    async def _preprocess_input_node(self, state: DialogueState) -> Dict[str, Any]:
        """輸入預處理節點 - 分析和處理用戶輸入"""
        user_text = state["raw_user_input"]
        messages = state["messages"]
        
        # 基本清理
        cleaned_text = user_text.strip()
        
        # 輸入分類邏輯
        input_classification = await self._classify_input(cleaned_text, messages)
        
        # 更新最近輸入列表
        self._update_recent_inputs(cleaned_text)
        
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
    
    async def _classify_input(self, text: str, messages: List[BaseMessage]) -> Dict[str, Any]:
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
        repetition_level = self._check_repetition(text)
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
    
    def _check_repetition(self, text: str) -> float:
        """檢查與先前輸入的重複度"""
        if not self.recent_user_inputs:
            return 0.0
        
        # 檢查是否與先前輸入完全相同
        for prev_input in self.recent_user_inputs:
            if text == prev_input:
                return 1.0
        
        # 檢查部分重複
        for prev_input in self.recent_user_inputs:
            common_length = len(set(text).intersection(set(prev_input)))
            if common_length > 0:
                similarity = common_length / max(len(set(text)), len(set(prev_input)))
                if similarity > 0.7:  # 如果有70%以上相同字符
                    return similarity
        
        return 0.0
    
    def _update_recent_inputs(self, text: str):
        """更新最近輸入列表"""
        self.recent_user_inputs.insert(0, text)
        if len(self.recent_user_inputs) > self.max_recent_inputs:
            self.recent_user_inputs.pop()
    
    async def _retrieve_memory_node(self, state: DialogueState) -> Dict[str, Any]:
        """檢索記憶節點 - 從記憶系統獲取相關記憶和角色信息"""
        user_text = state["processed_user_input"]
        messages = state["messages"]
        input_classification = state["input_classification"]
        
        # 檢索相關記憶 (最近N條消息用於構建上下文)
        history_for_retrieval = messages[-5:] if len(messages) >= 5 else messages
        
        try:
            # 根據輸入分類調整檢索策略
            if input_classification["type"] in ["gibberish", "highly_repetitive"]:
                # 對於亂碼或高度重複的輸入，減少檢索範圍，主要依賴最近對話歷史
                logging.info("檢測到問題輸入，使用保守記憶檢索策略")
                relevant_memories, persona_info = await self.memory_system.retrieve_context(
                    "",  # 使用空字符串作為查詢，只基於最近對話
                    history_for_retrieval,
                    k=1  # 減少返回的記憶數量
                )
            else:
                # 對於正常輸入，使用標準檢索
                relevant_memories, persona_info = await self.memory_system.retrieve_context(
                    user_text,
                    history_for_retrieval
                )
            
            logging.info(f"記憶檢索成功: {len(relevant_memories)} 字符的相關記憶")
            
            # 將記憶轉換為列表形式以便後續處理
            try:
                retrieved_docs = self.memory_system.conversation_memory.get()
                retrieved_memories = retrieved_docs["documents"][:5]  # 獲取前5條記憶
            except Exception as e:
                logging.error(f"獲取原始記憶失敗: {e}", exc_info=True)
                retrieved_memories = [relevant_memories]
            
            return {
                "retrieved_memories": retrieved_memories,
                "persona_info": persona_info
            }
        except Exception as e:
            logging.error(f"記憶檢索失敗: {e}", exc_info=True)
            return {
                "retrieved_memories": ["無法檢索記憶"],
                "persona_info": f"我是{self.persona_name}，一位太空網紅。",
                "system_alert": "memory_retrieval_error"
            }
    
    def _filter_memory_node(self, state: DialogueState) -> Dict[str, Any]:
        """記憶過濾節點 - 篩選和驗證檢索到的記憶"""
        retrieved_memories = state["retrieved_memories"]
        user_text = state["processed_user_input"]
        input_classification = state["input_classification"]
        
        filtered_content = []
        
        # 基於輸入分類調整過濾策略
        if input_classification["type"] in ["gibberish", "highly_repetitive"]:
            # 對於問題輸入，採用最保守的過濾
            logging.info("檢測到問題輸入，採用嚴格記憶過濾")
            # 只保留最基本的記憶，避免無效內容
            if len(retrieved_memories) > 0:
                filtered_content = ["先前對話記憶已模糊"]
        else:
            # 正常過濾邏輯
            unique_contents = set()
            
            for memory in retrieved_memories:
                if isinstance(memory, str):
                    content = memory.strip()
                else:
                    content = str(memory).strip()
                
                # 避免空內容
                if not content:
                    continue
                
                # 簡單去重
                normalized_content = "".join(content.split())
                if normalized_content not in unique_contents:
                    # 檢查記憶是否包含用戶的怪異輸入 (可能來自先前對話)
                    if any(weird_input in content for weird_input in ["DevOps", "j8 dl4", "dl4"]) and \
                       not ("討論DevOps" in content or "開發運維" in content):  # 排除正常語境中的DevOps
                        logging.info(f"過濾掉包含怪異輸入的記憶: {content[:30]}...")
                        continue
                    
                    filtered_content.append(content)
                    unique_contents.add(normalized_content)
        
        # 格式化過濾後的記憶
        filtered_memories = "\n---\n".join(filtered_content[:3])  # 限制到3條記憶
        
        logging.info(f"記憶過濾完成: 從 {len(retrieved_memories)} 條到 {len(filtered_content)} 條")
        
        return {
            "filtered_memories": filtered_memories
        }
    
    def _select_prompt_and_style_node(self, state: DialogueState) -> Dict[str, Any]:
        """選擇提示模板和對話風格節點"""
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
        dialogue_style = self._select_dialogue_style(character_state, input_classification)
        
        logging.info(f"選擇提示模板: {prompt_template_key}, 對話風格: {dialogue_style}")
        
        return {
            "prompt_template_key": prompt_template_key,
            "dialogue_style": dialogue_style
        }
    
    def _select_dialogue_style(self, character_state: Dict[str, Any], input_classification: Dict[str, Any]) -> str:
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
    
    def _build_prompt_node(self, state: DialogueState) -> Dict[str, Any]:
        """構建提示節點 - 準備傳給 LLM 的輸入參數"""
        
        # 取得必要的狀態
        processed_user_input = state["processed_user_input"]
        filtered_memories = state["filtered_memories"]
        persona_info = state["persona_info"]
        prompt_template_key = state["prompt_template_key"]
        dialogue_style = state["dialogue_style"]
        messages = state["messages"]
        
        # 格式化對話歷史
        history_limit = 10  # 取最近10條消息用於提示
        history = messages[-history_limit:] if len(messages) >= history_limit else messages
        conversation_history = "\n".join([
            f"{'用戶' if isinstance(msg, HumanMessage) else self.persona_name}: {msg.content}" 
            for msg in history
        ])
        
        # 格式化角色狀態描述
        character_state_prompt = self._format_character_state(state["character_state"])
        
        # 構建提示輸入
        prompt_inputs = {
            "user_message": processed_user_input,
            "conversation_history": conversation_history,
            "filtered_memories": filtered_memories,
            "persona_info": persona_info,
            "character_state": character_state_prompt,
            "current_task": state["current_task"] if state["current_task"] else "無特定任務",
            "dialogue_style": dialogue_style,
            "persona_name": self.persona_name
        }
        
        logging.debug(f"提示輸入已構建: {len(json.dumps(prompt_inputs))} 字符")
        
        return {
            "conversation_history": conversation_history,
            "character_state_prompt": character_state_prompt,
            "prompt_inputs": prompt_inputs
        }
    
    async def _call_llm_node(self, state: DialogueState) -> Dict[str, Any]:
        """調用 LLM 節點 - 使用提示輸入調用大型語言模型"""
        prompt_template_key = state["prompt_template_key"]
        prompt_inputs = state["prompt_inputs"]
        error_count = state["error_count"]
        
        # 選擇提示模板
        prompt_template = self.prompt_templates.get(prompt_template_key, self.prompt_templates["standard"])
        
        # 構建 LLM 鏈
        chain = prompt_template | self.llm | StrOutputParser()
        
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
    
    def _post_process_node(self, state: DialogueState) -> Dict[str, Any]:
        """後處理節點 - 處理 LLM 回應，移除固定模式"""
        llm_response_raw = state["llm_response_raw"]
        input_classification = state["input_classification"]
        prompt_template_key = state["prompt_template_key"]
        
        processed_response, was_heavily_modified = self._post_process_response(
            llm_response_raw, 
            input_classification, 
            prompt_template_key
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
    
    def _post_process_response(self, response: str, input_classification: Dict[str, Any], template_key: str) -> Tuple[str, bool]:
        """
        後處理回應，移除固定模式和 Emoji
        返回: (處理後的回應, 是否大幅修改)
        """
        original_response_stripped = response.strip() # 保存原始的回應 (去除首尾空格)
        original_length = len(original_response_stripped)
        processed_response = original_response_stripped
        was_heavily_modified = False

        # 移除可能的固定開場白 (更寬鬆的匹配)
        fixed_intros = [
            f"嗨，我是{self.persona_name}",
            f"你好，我是{self.persona_name}",
            f"哈囉，我是{self.persona_name}",
            f"我是{self.persona_name}"
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

        # 移除常見的 Emoji 字符
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

        # 檢查或移除回應中的奇怪詞彙 (可能是從用戶輸入中吸收的)
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

        # *** 修改後的邏輯 ***
        # 確保回應不為空或過短 (例如少於3個字符)
        if not processed_response or len(processed_response.strip()) < 3:
            logging.warning("後處理移除了大部分回應，返回原始回應 (去除首尾空格)")
            processed_response = original_response_stripped # 返回原始的、僅去除首尾空格的回應
            was_heavily_modified = True # 標記為大幅修改，避免存入記憶

        # 判斷是否大幅修改 (如果尚未標記)
        if not was_heavily_modified:
            # 如果長度減少超過 30%，也認為是大幅修改
            was_heavily_modified = (len(processed_response) < original_length * 0.7)

        return processed_response, was_heavily_modified
    
    async def _store_memory_node(self, state: DialogueState) -> Dict[str, Any]:
        """儲存記憶節點 - 將完成的對話輪次儲存到記憶系統"""
        user_text = state["processed_user_input"]
        final_response = state["final_response"]
        should_store_memory = state["should_store_memory"]
        
        # 更新消息列表
        new_messages = state["messages"].copy()
        new_messages.append(AIMessage(content=final_response))
        
        if should_store_memory:
            try:
                # 儲存對話到記憶系統
                self.memory_system.store_conversation_turn(user_text, final_response)
                logging.info("對話成功儲存到記憶系統")
                
                # 觸發記憶整合
                asyncio.create_task(self.memory_system.async_consolidate_memories())
            except Exception as e:
                logging.error(f"儲存對話到記憶系統失敗: {e}", exc_info=True)
        else:
            logging.info("基於系統判斷，此輪對話不儲存到長期記憶")
        
        return {
            "messages": new_messages
        }
    
    def _format_character_state(self, character_state: Dict[str, Any]) -> str:
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
            "should_store_memory": True
        }
        
        try:
            # 執行圖，獲取最終狀態
            logging.info(f"開始執行對話圖: 用戶輸入 {user_text[:20]}...")
            final_state = await self.app.ainvoke(initial_state)
            
            # 從最終狀態提取回應和更新的消息列表
            final_response = final_state["final_response"]
            updated_messages = final_state["messages"]
            
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
            state_text = self._format_character_state(updated_state)
            logging.info(f"更新後角色狀態: {state_text}")
        
        return updated_state
    
    def reset(self) -> Dict[str, Any]:
        """重置角色狀態為初始值"""
        return self.initial_character_state.copy() 