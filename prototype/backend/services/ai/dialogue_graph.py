"""
基於 LangGraph 的對話流程圖 - 更靈活的對話管理
"""

import logging
import asyncio
import json
import random
import re # 導入 re 模組
from typing import Dict, List, Any, TypedDict, Optional, Annotated, Literal
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, END
from langgraph.graph.message import MessageGraph

from .memory_system import MemorySystem

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 對話提示模板
DIALOGUE_PROMPT_TEMPLATE = """
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
{relevant_memories}

【最近的對話歷史】
{conversation_history}

【互動原則】
1. 自然使用你的名字，但避免刻板的自我介紹。
2. 融合相關記憶，但不要明顯引用「根據我的記憶」。
3. 當發現之前的回答有矛盾，自然地修正。
4. 當用戶要求你做某事(如回憶或提供特定信息)，請盡力完成。
5. **處理模糊指令：如果用戶指令模糊（例如'做吧'、'開始'），但最近的對話歷史明確暗示了要執行的動作（例如回憶記憶、執行任務），請嘗試執行該動作，而不是僅僅要求澄清。如果上下文也模糊，才要求澄清。**
6. 根據你的狀態自然調整語氣，低能量時可能更簡短。
7. 偶爾展現對宇宙的好奇和對地球的思念。

請用自然、靈活的方式回應以下輸入，**再次強調：絕不使用任何 Emoji 或表情符號**：
用戶說: {user_message}
"""

# 定義對話圖的狀態結構
class DialogueState(TypedDict):
    # 輸入與記憶
    user_input: str  # 使用者輸入
    messages: List[BaseMessage]  # 完整對話歷史
    relevant_memories: str  # 從記憶系統檢索的相關記憶
    persona_info: str  # 角色信息記憶
    
    # 對話生成相關
    conversation_history: str  # 格式化後的對話歷史（用於提示）
    dialogue_style: str  # 選定的對話風格
    character_state_prompt: str  # 格式化後的角色狀態（用於提示）
    prompt_inputs: Dict[str, Any]  # 提示模板的輸入參數
    
    # 角色狀態與任務
    character_state: Dict[str, Any]  # 角色狀態（健康、心情等）
    current_task: Optional[str]  # 當前任務
    tasks_history: List[Dict]  # 任務歷史
    
    # 回應生成結果
    ai_response_raw: str  # LLM生成的原始回應
    ai_response: str  # 後處理後的最終回應

# 風格選項
DIALOGUE_STYLES = {
    "enthusiastic": "充滿活力和熱情，語氣歡快",
    "thoughtful": "思考深入，語氣冷靜，偏向分析",
    "humorous": "幽默風趣，常開玩笑，語氣輕鬆",
    "caring": "關懷體貼，語氣溫和友善",
    "curious": "好奇探索，充滿疑問和思考",
    "tired": "略顯疲倦，語氣平淡但友善"
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
        self.prompt_template = PromptTemplate(
            template=DIALOGUE_PROMPT_TEMPLATE,
            input_variables=[
                "conversation_history", "relevant_memories", "persona_info",
                "user_message", "character_state", "current_task",
                "dialogue_style", "persona_name"
            ]
        )
        
        # 構建基本的 LLM 鏈（在節點中使用）
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
        # 構建對話圖
        self.graph = self._build_graph()
        
        # 編譯圖
        self.app = self.graph.compile()
        
        logging.info("DialogueGraph 初始化完成")
        
    def _build_graph(self) -> StateGraph:
        """構建對話圖"""
        
        # 創建狀態圖
        workflow = StateGraph(DialogueState)
        
        # 添加節點
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("prepare_context", self._prepare_context_node)
        workflow.add_node("build_prompt", self._build_prompt_node)
        workflow.add_node("call_llm", self._call_llm_node)
        workflow.add_node("post_process", self._post_process_node)
        workflow.add_node("store_memory", self._store_memory_node)
        
        # 定義邊 (流程)
        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "prepare_context")
        workflow.add_edge("prepare_context", "build_prompt")
        workflow.add_edge("build_prompt", "call_llm")
        workflow.add_edge("call_llm", "post_process")
        workflow.add_edge("post_process", "store_memory")
        workflow.add_edge("store_memory", END)
        
        # 添加條件邊（將來擴展）
        # 可以在這裡添加條件邊，例如錯誤重試、工具調用等
        
        return workflow
    
    async def _retrieve_memory_node(self, state: DialogueState) -> Dict[str, Any]:
        """檢索記憶節點 - 從記憶系統獲取相關記憶和角色信息"""
        user_text = state["user_input"]
        messages = state["messages"]
        
        # 檢索相關記憶 (最近N條消息用於構建上下文)
        history_for_retrieval = messages[-5:] if len(messages) >= 5 else messages
        
        try:
            relevant_memories, persona_info = await self.memory_system.retrieve_context(
                user_text, history_for_retrieval
            )
            logging.info(f"記憶檢索成功: {len(relevant_memories)} 字符的相關記憶")
            
            return {
                "relevant_memories": relevant_memories,
                "persona_info": persona_info
            }
        except Exception as e:
            logging.error(f"記憶檢索失敗: {e}", exc_info=True)
            return {
                "relevant_memories": "無相關記憶（檢索失敗）",
                "persona_info": f"我是{self.persona_name}，一位太空網紅。"
            }
    
    def _prepare_context_node(self, state: DialogueState) -> Dict[str, Any]:
        """準備上下文節點 - 格式化歷史對話、選擇風格、準備角色狀態"""
        
        # 格式化對話歷史
        messages = state["messages"]
        history_limit = 10  # 取最近10條消息用於提示
        history = messages[-history_limit:] if len(messages) >= history_limit else messages
        conversation_history = "\n".join([
            f"{'用戶' if isinstance(msg, HumanMessage) else self.persona_name}: {msg.content}" 
            for msg in history
        ])
        
        # 選擇對話風格
        dialogue_style = self._select_dialogue_style(state["character_state"])
        
        # 格式化角色狀態描述
        character_state_prompt = self._format_character_state(state["character_state"])
        
        logging.debug(f"對話歷史格式化完成: {len(conversation_history)} 字符")
        
        return {
            "conversation_history": conversation_history,
            "dialogue_style": dialogue_style,
            "character_state_prompt": character_state_prompt
        }
    
    def _build_prompt_node(self, state: DialogueState) -> Dict[str, Any]:
        """構建提示節點 - 準備傳給 LLM 的輸入參數"""
        
        # 構建提示輸入
        prompt_inputs = {
            "user_message": state["user_input"],
            "conversation_history": state["conversation_history"],
            "relevant_memories": state["relevant_memories"],
            "persona_info": state["persona_info"],
            "character_state": state["character_state_prompt"],
            "current_task": state["current_task"] if state["current_task"] else "無特定任務",
            "dialogue_style": state["dialogue_style"],
            "persona_name": self.persona_name
        }
        
        logging.debug(f"提示輸入已構建: {len(json.dumps(prompt_inputs))} 字符")
        
        return {
            "prompt_inputs": prompt_inputs
        }
    
    async def _call_llm_node(self, state: DialogueState) -> Dict[str, Any]:
        """調用 LLM 節點 - 使用提示輸入調用大型語言模型"""
        try:
            ai_response_raw = await self.chain.ainvoke(state["prompt_inputs"])
            logging.info(f"LLM 調用成功: {len(ai_response_raw)} 字符的回應")
            
            return {
                "ai_response_raw": ai_response_raw
            }
        except Exception as e:
            logging.error(f"LLM 調用失敗: {e}", exc_info=True)
            # 返回一個友好的錯誤消息
            error_responses = [
                "哎呀，我的訊號好像不太穩定，你能再說一次嗎？",
                "嗯... 我的處理器好像卡了一下，可以再問一次嗎？",
                "太空干擾有點強，我沒聽清楚，麻煩再說一遍！"
            ]
            return {
                "ai_response_raw": random.choice(error_responses)
            }
    
    def _post_process_node(self, state: DialogueState) -> Dict[str, Any]:
        """後處理節點 - 處理 LLM 回應，移除固定模式"""
        ai_response_raw = state["ai_response_raw"]
        processed_response = self._post_process_response(ai_response_raw)
        
        logging.info(f"後處理完成: 從 {len(ai_response_raw)} 到 {len(processed_response)} 字符")
        
        return {
            "ai_response": processed_response
        }
    
    async def _store_memory_node(self, state: DialogueState) -> Dict[str, Any]:
        """儲存記憶節點 - 將完成的對話輪次儲存到記憶系統"""
        user_text = state["user_input"]
        ai_response = state["ai_response"]
        
        # 更新消息列表
        new_messages = state["messages"].copy()
        new_messages.append(AIMessage(content=ai_response))
        
        try:
            # 儲存對話到記憶系統
            self.memory_system.store_conversation_turn(user_text, ai_response)
            logging.info("對話成功儲存到記憶系統")
            
            # 可選: 觸發記憶整合
            self.memory_system.consolidate_memories()
            
            return {
                "messages": new_messages
            }
        except Exception as e:
            logging.error(f"儲存對話到記憶系統失敗: {e}", exc_info=True)
            return {
                "messages": new_messages
            }
    
    def _select_dialogue_style(self, character_state: Dict[str, Any]) -> str:
        """根據角色狀態選擇對話風格"""
        
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
    
    def _post_process_response(self, response: str) -> str:
        """後處理回應，移除固定模式和 Emoji"""
        processed_response = response.strip()

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

        # 新增：移除常見的 Emoji 字符 (雙重保險)
        # 這個正則表達式涵蓋了大部分常見的 Emoji
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
        processed_response = emoji_pattern.sub(r'', processed_response).strip() # 移除並再次去除首尾空格

        # 確保回應不為空
        if not processed_response:
            # 如果移除後變空，可以返回一個通用回應或原始回應
            logging.warning("後處理移除了整個回應，返回原始回應")
            return response.strip() # 返回原始的回應（去除首尾空格）

        return processed_response
    
    async def generate_response(self, user_text: str, messages: List[BaseMessage], 
                               character_state: Dict[str, Any], current_task: Optional[str] = None,
                               tasks_history: Optional[List[Dict]] = None) -> str:
        """生成回應主方法 - 驅動整個對話圖"""
        
        # 準備初始狀態
        initial_state: DialogueState = {
            # 輸入
            "user_input": user_text,
            "messages": messages + [HumanMessage(content=user_text)],  # 添加當前用戶輸入
            
            # 記憶 (將在流程中填充)
            "relevant_memories": "",
            "persona_info": "",
            
            # 對話生成 (將在流程中填充)
            "conversation_history": "",
            "dialogue_style": "",
            "character_state_prompt": "",
            "prompt_inputs": {},
            
            # 角色狀態
            "character_state": character_state.copy(),
            "current_task": current_task,
            "tasks_history": tasks_history or [],
            
            # 回應 (將在流程中填充)
            "ai_response_raw": "",
            "ai_response": ""
        }
        
        try:
            # 執行圖，獲取最終狀態
            logging.info(f"開始執行對話圖: 用戶輸入 {user_text[:20]}...")
            final_state = await self.app.ainvoke(initial_state)
            
            # 從最終狀態提取回應和更新的消息列表
            ai_response = final_state["ai_response"]
            updated_messages = final_state["messages"]
            
            return ai_response, updated_messages
            
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