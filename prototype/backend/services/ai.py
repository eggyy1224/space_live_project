import google.generativeai as genai
from typing import Dict, Optional, List, Any, Tuple
from core.config import settings
from core.exceptions import AIServiceException
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
import json
import os
import logging
import random
import time

# 基本日誌配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIService:
    """增強型AI對話服務 - 多層記憶架構與自適應對話生成"""
    
    def __init__(self):
        # 配置Google API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # 角色固定屬性
        self.persona_name = "星際小可愛"
        
        # 創建LangChain LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.AI_MODEL_NAME,
            temperature=settings.GENERATION_TEMPERATURE, 
            top_p=settings.GENERATION_TOP_P, 
            top_k=settings.GENERATION_TOP_K,
            max_output_tokens=settings.GENERATION_MAX_TOKENS,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # 創建嵌入模型
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY)
        
        # 建立記憶系統 - 分類記憶庫
        if not os.path.exists(settings.VECTOR_DB_PATH):
            os.makedirs(settings.VECTOR_DB_PATH)
            
        # 主要對話記憶庫
        self.conversation_memory = Chroma(
            persist_directory=os.path.join(settings.VECTOR_DB_PATH, "conversation_memory"),
            embedding_function=self.embeddings,
            collection_name="conversations"
        )
        
        # 角色信息記憶庫 - 儲存關於角色自身的重要信息
        self.persona_memory = Chroma(
            persist_directory=os.path.join(settings.VECTOR_DB_PATH, "persona_memory"),
            embedding_function=self.embeddings,
            collection_name="persona_info"
        )

        # 初始化角色信息記憶
        self._initialize_persona_memory()
        
        # 定義多樣化檢索器 - 主要對話
        self.conversation_retriever = self.conversation_memory.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.VECTOR_MEMORY_K,
                "fetch_k": settings.VECTOR_MEMORY_K * 3,
                "lambda_mult": 0.75
            }
        )
        
        # 定義角色信息檢索器
        self.persona_retriever = self.persona_memory.as_retriever(
            search_kwargs={"k": 2}  # 只獲取少量最相關的角色信息
        )
        
        # 多層記憶管理
        self.messages = []                  # 短期記憶 (當前會話)
        self.important_memories = []        # 中期記憶 (重要事實)
        self.memory_last_updated = time.time()  # 上次記憶整合時間
        
        # 角色狀態管理
        self.character_state = {
            "health": 100,        # 健康狀態 (0-100)
            "mood": 70,           # 心情 (0-100)
            "energy": 80,         # 能量 (0-100)
            "task_success": 0,    # 任務成功次數
            "days_in_space": 1    # 太空天數
        }
        
        # 任務管理
        self.current_task = None
        self.tasks_history = []
        
        # 對話風格管理
        self.dialogue_styles = {
            "enthusiastic": "充滿活力和熱情，語氣歡快",
            "thoughtful": "思考深入，語氣冷靜，偏向分析",
            "humorous": "幽默風趣，常開玩笑，語氣輕鬆",
            "caring": "關懷體貼，語氣溫和友善",
            "curious": "好奇探索，充滿疑問和思考",
            "tired": "略顯疲倦，語氣平淡但友善"
        }
        
        # 創建動態提示模板
        self.prompt_template = PromptTemplate(
            input_variables=["conversation_history", "relevant_memories", "persona_info", "user_message", "character_state", "current_task", "dialogue_style", "persona_name"],
            template="""
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
            {user_message}
            """
        )
        
        # 創建RunnableSequence
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
    def _initialize_persona_memory(self):
        """初始化角色核心記憶 - 只在首次運行時執行"""
        # 檢查是否已有數據
        if self.persona_memory.get()["ids"]:
            logging.info("角色記憶已存在，跳過初始化")
            return
            
        # 添加核心角色信息
        core_memories = [
            "我的名字是星際小可愛，是一名業餘太空網紅，在太空站生活一年。",
            "我喜歡探索太空的奧秘，分享太空生活的點滴。",
            "我的個性活潑開朗，但有時也會因為太空的孤獨而感到寂寞。",
            "我有時會想念地球上的自然環境、美食和親友。",
            "我在太空站做各種日常任務，也會進行一些科學實驗和觀測。"
        ]
        
        self.persona_memory.add_texts(
            texts=core_memories,
            metadatas=[{"type": "core_identity"} for _ in core_memories]
        )
        logging.info("角色核心記憶初始化完成")
        
    async def generate_response(self, user_text: str, current_emotion: str = None) -> str:
        """增強版回應生成流程"""
        try:
            # 1. 進行多層記憶檢索
            relevant_memories, persona_info = await self._retrieve_memories(user_text)
            
            # 2. 將使用者訊息添加到歷史
            self.messages.append(HumanMessage(content=user_text))
            
            # 3. 從歷史中格式化對話
            recent_messages = self.messages[-settings.MEMORY_MAX_HISTORY:]
            conversation_history = "\n".join([f"{'用戶' if isinstance(msg, HumanMessage) else '助手'}: {msg.content}" 
                                    for msg in recent_messages])
            
            # 4. 動態選擇對話風格，基於角色狀態和情境
            dialogue_style = self._select_dialogue_style()
            
            # 日誌記錄
            logging.info(f"--- Current Dialogue Style ---")
            logging.info(dialogue_style)
            logging.info(f"--- Conversation History ---")
            logging.info(conversation_history)
            logging.info(f"--- Relevant Memories ---")
            logging.info(relevant_memories)
            logging.info(f"--- Persona Info ---")
            logging.info(persona_info)
            
            # 5. 構建輸入參數
            inputs = {
                "user_message": user_text,
                "character_state": self._format_character_state(),
                "current_task": self.current_task if self.current_task else "無特定任務",
                "relevant_memories": relevant_memories,
                "persona_info": persona_info,
                "conversation_history": conversation_history,
                "dialogue_style": dialogue_style,
                "persona_name": self.persona_name
            }
            
            # 6. 生成回應
            ai_response = await self.chain.ainvoke(inputs)
            
            # 7. 後處理 - 移除潛在的固定開場白模式
            ai_response = self._post_process_response(ai_response)
            
            # 8. 記錄回應
            self.messages.append(AIMessage(content=ai_response))
            
            # 9. 更新記憶系統
            self._update_memory(user_text, ai_response)
            
            # 10. 定期整合記憶
            if time.time() - self.memory_last_updated > 1800:  # 30分鐘
                self._consolidate_memories()
                self.memory_last_updated = time.time()
            
            return ai_response
            
        except Exception as e:
            logging.error(f"生成AI回應失敗: {str(e)}", exc_info=True)
            raise AIServiceException(f"生成AI回應失敗: {str(e)}")
    
    async def _retrieve_memories(self, query: str) -> Tuple[str, str]:
        """多層次記憶檢索"""
        # 1. 獲取最近消息用於增強查詢
        enhanced_query = self._build_enhanced_query(query)
        
        # 2. 檢索相關對話記憶
        relevant_docs = await self.conversation_retriever.ainvoke(enhanced_query)
        
        # 3. 檢索角色相關記憶
        persona_docs = await self.persona_retriever.ainvoke(query)
        
        # 4. 處理並格式化檢索到的記憶
        relevant_memories = self._format_retrieved_memories(relevant_docs)
        persona_info = "\n".join([doc.page_content for doc in persona_docs])
        
        return relevant_memories, persona_info
        
    def _build_enhanced_query(self, user_text: str) -> str:
        """構建增強查詢 - 結合上下文和用戶意圖"""
        # 獲取最近的幾條消息
        recent_history = self.messages[-min(3, len(self.messages)):] if self.messages else []
        
        # 提取可能的主題詞或關鍵詞
        potential_topics = []
        if recent_history:
            all_text = " ".join([msg.content for msg in recent_history]) + " " + user_text
            # 這裡可以添加更複雜的主題提取邏輯，目前簡化處理
            words = all_text.split()
            potential_topics = [word for word in words if len(word) > 1 and "。" not in word and "，" not in word][:5]
        
        # 構建查詢
        query_parts = []
        
        # 加入簡化的最近對話摘要
        if recent_history:
            last_user_msg = next((msg.content for msg in reversed(recent_history) if isinstance(msg, HumanMessage)), None)
            if last_user_msg:
                query_parts.append(f"最近用戶問了: {last_user_msg}")
        
        # 添加當前問題
        query_parts.append(f"當前問題: {user_text}")
        
        # 添加可能的主題
        if potential_topics:
            query_parts.append(f"相關主題可能包括: {', '.join(potential_topics)}")
        
        # 合併查詢
        return " ".join(query_parts)
        
    def _format_retrieved_memories(self, docs) -> str:
        """智能格式化記憶，去除冗餘，突出重點"""
        if not docs:
            return "無相關記憶"
            
        # 去除重複或高度相似的記憶片段
        unique_memories = []
        for doc in docs:
            content = doc.page_content.strip()
            # 簡單的重複檢測 - 可以用更複雜的方法改進
            if not any(self._text_similarity(content, existing) > 0.7 for existing in unique_memories):
                unique_memories.append(content)
        
        # 格式化記憶
        return "\n".join(unique_memories[:settings.VECTOR_MEMORY_K])
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """簡單的文本相似度計算 - 可以用更複雜的方法改進"""
        # 這是一個非常簡化的實現，實際應用可能需要更複雜的算法
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
            
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total if total > 0 else 0.0
        
    def _select_dialogue_style(self) -> str:
        """基於角色狀態和情境動態選擇對話風格"""
        # 考慮角色能量
        if self.character_state["energy"] < 30:
            return self.dialogue_styles["tired"]
            
        # 考慮角色心情
        if self.character_state["mood"] > 80:
            candidates = ["enthusiastic", "humorous"]
        elif self.character_state["mood"] < 40:
            candidates = ["thoughtful", "tired"]
        else:
            candidates = ["caring", "curious", "humorous", "thoughtful"]
            
        # 隨機選擇，增加多樣性
        style_key = random.choice(candidates)
        return self.dialogue_styles[style_key]
        
    def _format_character_state(self) -> str:
        """將數值狀態轉換為描述性文本"""
        energy_desc = "精力充沛" if self.character_state["energy"] > 70 else \
                     "狀態普通" if self.character_state["energy"] > 40 else "有些疲倦"
                     
        mood_desc = "心情愉快" if self.character_state["mood"] > 70 else \
                   "情緒平穩" if self.character_state["mood"] > 40 else "心情低落"
                   
        health_desc = "健康良好" if self.character_state["health"] > 70 else \
                     "身體尚可" if self.character_state["health"] > 40 else "健康狀況欠佳"
                     
        return f"{energy_desc}，{mood_desc}，{health_desc}。在太空已待了{self.character_state['days_in_space']}天。"
        
    def _post_process_response(self, response: str) -> str:
        """後處理回應，移除固定模式"""
        # 移除固定開場白模式
        fixed_intros = [
            f"嗨，我是{self.persona_name}！",
            f"你好，我是{self.persona_name}！",
            f"哈囉，我是{self.persona_name}！"
        ]
        
        processed_response = response
        for intro in fixed_intros:
            if processed_response.startswith(intro):
                processed_response = processed_response[len(intro):].strip()
        
        return processed_response
        
    def _update_memory(self, user_text: str, ai_response: str) -> None:
        """更新記憶系統"""
        # 1. 保存到對話記憶庫
        conversation_entry = f"""
        input: {user_text}
        output: {ai_response}
        """
        
        self.conversation_memory.add_texts(
            texts=[conversation_entry],
            metadatas=[{
                "type": "conversation",
                "timestamp": time.time(),
                "user_input": user_text,
                "ai_response": ai_response
            }]
        )
        
        # 2. 檢測是否包含重要信息（關於角色的新事實等）
        if any(keyword in user_text.lower() for keyword in ["你是", "你叫", "你的名字", "身份"]):
            # 可能包含角色身份相關信息，考慮添加到角色記憶
            self._check_and_update_persona_memory(user_text, ai_response)
    
    def _check_and_update_persona_memory(self, user_text: str, ai_response: str) -> None:
        """檢查並更新角色記憶（如有新的重要信息）"""
        # 這是一個簡化的實現，實際應用可能需要更複雜的邏輯
        # 例如使用LLM來判斷對話中是否包含關於角色的新事實
        
        # 目前僅簡單保存可能包含角色信息的對話
        if any(keyword in user_text.lower() for keyword in ["你是", "你叫", "你的名字", "身份"]):
            memory_entry = f"用戶問: {user_text}\n我回答: {ai_response}"
            
            self.persona_memory.add_texts(
                texts=[memory_entry],
                metadatas=[{"type": "identity_related", "timestamp": time.time()}]
            )
    
    def _consolidate_memories(self) -> None:
        """整合和優化記憶（定期執行）"""
        # 這個方法可以實現更高級的記憶管理，如:
        # 1. 識別並強化重要記憶
        # 2. 淡化不重要或過時的記憶
        # 3. 生成記憶摘要
        # 目前是簡化版本
        logging.info("執行記憶整合...")
        
        # 這裡可以添加更複雜的記憶整合邏輯
        # 例如使用LLM生成對話摘要，並存儲為高級記憶
            
    def update_character_state(self, updates: Dict[str, Any]) -> None:
        """更新角色狀態"""
        for key, value in updates.items():
            if key in self.character_state:
                self.character_state[key] = value
                
                # 確保值在合理範圍內
                if key in ["health", "mood", "energy"]:
                    self.character_state[key] = max(0, min(100, self.character_state[key]))
                    
    def set_current_task(self, task: str) -> None:
        """設置當前任務"""
        if self.current_task:
            self.tasks_history.append(self.current_task)
        
        self.current_task = task
        
    def complete_current_task(self, success: bool = True) -> None:
        """完成當前任務"""
        if self.current_task:
            task_result = {
                "task": self.current_task,
                "success": success,
                "day": self.character_state["days_in_space"]
            }
            self.tasks_history.append(task_result)
            
            if success:
                self.character_state["task_success"] += 1
                self.character_state["mood"] += 5
            else:
                self.character_state["mood"] -= 5
                
            self.current_task = None
            
    def advance_day(self) -> None:
        """推進一天時間並更新相關狀態"""
        self.character_state["days_in_space"] += 1
        
        # 能量每天自然恢復一些
        self.character_state["energy"] = min(100, self.character_state["energy"] + 10)
        
        # 如果沒有任務，心情可能下降
        if not self.current_task:
            self.character_state["mood"] = max(0, self.character_state["mood"] - 2) 