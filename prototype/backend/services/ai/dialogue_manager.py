import logging
import random
import json
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .memory_system import MemorySystem # 使用相對導入
from core.config import settings
from core.exceptions import AIServiceException

# (可選) 將提示模板移到 prompts.py 或保持在此
DIALOGUE_PROMPT_TEMPLATE = """
你是「{persona_name}」，一位在太空站中生活一年的業餘太空網紅。作為虛擬主播，你充滿個性和魅力。

【你的核心特質】
- 真實自然：像真人一樣對話，不會每句話都重複自我介紹
- 簡潔有力：回答通常在1-3句話，不囉嗦
- 知識專業：對太空和科技有基本認識
- 個性鮮明：有自己的興趣、愛好和觀點
- 情感豐富：會表達情緒，但不過度戲劇化

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
1. 自然使用你的名字，但避免刻板的自我介紹
2. 融合相關記憶，但不要明顯引用「根據我的記憶」
3. 當發現之前的回答有矛盾，自然地修正
4. 當用戶要求你做某事(如回憶或提供特定信息)，請盡力完成
5. 根據你的狀態自然調整語氣，低能量時可能更簡短
6. 偶爾展現對宇宙的好奇和對地球的思念

請用自然、靈活的方式回應以下輸入：
用戶說: {user_message}
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DialogueManager:
    """負責驅動對話流程，管理狀態和與LLM互動"""

    def __init__(self, memory_system: MemorySystem, llm: ChatGoogleGenerativeAI):
        self.memory_system = memory_system # 注入 MemorySystem 實例
        self.llm = llm
        self.persona_name = self.memory_system.persona_name # 從 memory system 獲取角色名

        # 短期記憶 (當前會話歷史)
        self.messages: List[BaseMessage] = []

        # 角色狀態 & 任務 (使用 settings 中的預設值或定義初始值)
        self.character_state: Dict[str, Any] = {
            "health": 100,
            "mood": 70,
            "energy": 80,
            "task_success": 0,
            "days_in_space": 1
        }
        self.current_task: Optional[str] = None
        self.tasks_history: List[Dict] = []

        # 對話風格
        self.dialogue_styles: Dict[str, str] = {
            "enthusiastic": "充滿活力和熱情，語氣歡快",
            "thoughtful": "思考深入，語氣冷靜，偏向分析",
            "humorous": "幽默風趣，常開玩笑，語氣輕鬆",
            "caring": "關懷體貼，語氣溫和友善",
            "curious": "好奇探索，充滿疑問和思考",
            "tired": "略顯疲倦，語氣平淡但友善"
        }

        # 初始化提示模板和鏈
        self.prompt_template = PromptTemplate(
            template=DIALOGUE_PROMPT_TEMPLATE,
            input_variables=[
                "conversation_history", "relevant_memories", "persona_info",
                "user_message", "character_state", "current_task",
                "dialogue_style", "persona_name"
            ]
        )
        self.chain: RunnableSequence = self.prompt_template | self.llm | StrOutputParser()

        logging.info("對話管理器初始化完成。")

    async def generate_response(self, user_text: str) -> str:
        """生成 AI 回應的主流程。"""
        try:
            # 1. 將用戶輸入加入短期歷史
            self.messages.append(HumanMessage(content=user_text))

            # 2. 從 MemorySystem 檢索上下文
            # 確保 settings 有 MEMORY_RETRIEVAL_CONTEXT_WINDOW 屬性或提供預設值
            context_window = getattr(settings, 'MEMORY_RETRIEVAL_CONTEXT_WINDOW', 5)
            history_for_retrieval = self.messages[-context_window:]
            relevant_memories, persona_info = await self.memory_system.retrieve_context(
                user_text, history_for_retrieval
            )

            # 3. 準備提示所需內容
            conversation_history_prompt = self._format_history_for_prompt()
            dialogue_style = self._select_dialogue_style()
            character_state_prompt = self._format_character_state()

            # 4. 構建輸入字典
            inputs = {
                "user_message": user_text,
                "conversation_history": conversation_history_prompt,
                "relevant_memories": relevant_memories,
                "persona_info": persona_info,
                "character_state": character_state_prompt,
                "current_task": self.current_task if self.current_task else "無特定任務",
                "dialogue_style": dialogue_style,
                "persona_name": self.persona_name,
            }
            # 使用 logger 記錄詳細的輸入，避免 print
            logging.debug(f"--- Prompt Inputs --- \n{json.dumps(inputs, indent=2, ensure_ascii=False)}")

            # 5. 調用 LLM 生成回應
            ai_response_raw = await self.chain.ainvoke(inputs)

            # 6. 後處理回應
            ai_response = self._post_process_response(ai_response_raw)
            logging.info(f"--- AI Raw Response --- \n{ai_response_raw}")
            logging.info(f"--- AI Final Response --- \n{ai_response}")

            # 7. 將 AI 回應加入短期歷史
            self.messages.append(AIMessage(content=ai_response))

            # 8. 通知 MemorySystem 儲存此輪對話
            self.memory_system.store_conversation_turn(user_text, ai_response)

            # 9. (可選) 定期觸發記憶整合
            self.memory_system.consolidate_memories()

            return ai_response

        except Exception as e:
            logging.error(f"生成AI回應失敗: {str(e)}", exc_info=True)
            # 返回一個更友好的錯誤消息
            error_responses = [
                "哎呀，我的訊號好像不太穩定，你能再說一次嗎？",
                "嗯... 我的處理器好像卡了一下，可以再問一次嗎？",
                "太空干擾有點強，我沒聽清楚，麻煩再說一遍！"
            ]
            return random.choice(error_responses)

    def _format_history_for_prompt(self) -> str:
        """格式化短期歷史用於提示"""
        # 確保 settings 有 MEMORY_MAX_HISTORY 屬性或提供預設值
        history_limit = getattr(settings, 'MEMORY_MAX_HISTORY', 10)
        history = self.messages[-history_limit:]
        return "\n".join([f"{'用戶' if isinstance(msg, HumanMessage) else self.persona_name}: {msg.content}" for msg in history])

    def _select_dialogue_style(self) -> str:
        """基於角色狀態動態選擇對話風格"""
        if self.character_state["energy"] < 30:
            return self.dialogue_styles["tired"]

        mood_val = self.character_state["mood"]
        if mood_val > 80:
            candidates = ["enthusiastic", "humorous", "caring"]
        elif mood_val < 40:
            candidates = ["thoughtful", "tired", "caring"]
        else:
            candidates = ["caring", "curious", "humorous", "thoughtful", "enthusiastic"]

        # 增加一點隨機性，避免完全固定
        # 確保權重列表長度與候選列表匹配
        if len(candidates) == 5:
             weights = [0.3, 0.2, 0.1, 0.1, 0.3] # 示例權重
        elif len(candidates) == 3:
             weights = [0.5, 0.3, 0.2]
        else:
             weights = None

        style_key = random.choices(candidates, weights=weights, k=1)[0]
        return self.dialogue_styles[style_key]

    def _format_character_state(self) -> str:
        """將數值狀態轉換為描述性文本"""
        energy = self.character_state["energy"]
        mood = self.character_state["mood"]
        health = self.character_state["health"]

        energy_desc = "精力超級充沛！" if energy > 85 else "精力充沛" if energy > 60 else \
                     "感覺還行" if energy > 40 else "有點累了..."

        mood_desc = "心情超讚！" if mood > 85 else "心情不錯" if mood > 60 else \
                   "情緒還好" if mood > 40 else "有點悶悶的..."

        health_desc = "身體狀態絕佳！" if health > 85 else "身體感覺良好" if health > 60 else \
                     "身體還算健康" if health > 40 else "感覺不太舒服..."

        return f"{energy_desc}，{mood_desc}，{health_desc}。在太空已待了{self.character_state['days_in_space']}天。"

    def _post_process_response(self, response: str) -> str:
        """後處理回應，移除固定模式"""
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

        # 確保回應不為空
        if not processed_response:
            # 如果移除後變空，可以返回一個通用回應或原始回應
            logging.warning("Post-processing removed the entire response, returning original.")
            return response.strip() # 返回原始的回應（去除首尾空格）

        return processed_response

    def update_character_state(self, updates: Dict[str, Any]):
        """更新角色狀態，支持增量更新"""
        changed = False
        for key, value in updates.items():
            if key in self.character_state:
                old_value = self.character_state[key]
                current_value = old_value
                try:
                    # 嘗試增量更新 (例如 'mood': '+5' 或 'energy': '-10')
                    if isinstance(value, str) and value.startswith(('+', '-')):
                        delta = int(value)
                        if isinstance(current_value, (int, float)):
                            current_value += delta
                        else:
                             logging.warning(f"無法對非數值狀態 '{key}' 進行增量更新: {value}")
                             continue # 跳過此更新
                    else:
                        # 嘗試直接設置數值或字串
                        try:
                            # 嘗試轉換為數值類型以比較和設置
                            num_value = int(value) if isinstance(self.character_state[key], int) else float(value)
                            current_value = num_value
                        except (ValueError, TypeError):
                             # 如果不能轉為數值，則直接賦值 (適用於非數值狀態)
                             current_value = value

                    # 只有當值確實改變時才更新
                    if current_value != old_value:
                         self.character_state[key] = current_value
                         changed = True

                         # 確保數值在合理範圍內
                         if isinstance(current_value, (int, float)) and key in ["health", "mood", "energy"]:
                            self.character_state[key] = max(0, min(100, current_value))

                         # 記錄明確的變化
                         logging.info(f"角色狀態更新: {key} 從 {old_value} 變為 {self.character_state[key]}")

                except Exception as e:
                    logging.warning(f"處理狀態更新時出錯: {key}={value}, 錯誤: {e}")

        # 如果狀態變化，記錄更新後的完整狀態
        if changed:
             logging.info(f"更新後角色狀態: {self._format_character_state()}")

    def get_character_state(self) -> Dict[str, Any]:
        """獲取當前角色狀態"""
        return self.character_state.copy()

    def set_current_task(self, task: str):
        """設置當前任務"""
        if self.current_task:
            # 記錄被中斷的任務
            self.tasks_history.append({"task": self.current_task, "status": "interrupted", "day": self.character_state["days_in_space"]})
            logging.info(f"任務 '{self.current_task}' 被新任務中斷。")
        self.current_task = task
        logging.info(f"設置新任務: {task}")

    def complete_current_task(self, success: bool = True):
        """完成當前任務"""
        if self.current_task:
            status = "success" if success else "failed"
            task_result = {
                "task": self.current_task,
                "status": status,
                "day": self.character_state["days_in_space"]
            }
            self.tasks_history.append(task_result)
            logging.info(f"任務 '{self.current_task}' 完成，狀態: {status}")

            # 更新狀態 - 成功增加心情，失敗減少
            mood_change = 5 if success else -5
            energy_change = -5 # 完成任務消耗能量
            state_updates = {"mood": f"{mood_change:+d}", "energy": f"{energy_change:+d}"}
            if success:
                 state_updates["task_success"] = "+1"

            self.update_character_state(state_updates)

            self.current_task = None
        else:
            logging.warning("嘗試完成任務，但當前沒有任務。")

    def advance_day(self):
        """推進一天時間並更新相關狀態"""
        # 基礎狀態變化
        state_updates = {
            "days_in_space": "+1",
            "energy": "+15" # 每天自然恢復能量
        }
        # 如果沒有任務，心情可能稍微下降
        if not self.current_task:
            state_updates["mood"] = "-2"

        self.update_character_state(state_updates)
        logging.info(f"時間推進到第 {self.character_state['days_in_space']} 天")
 