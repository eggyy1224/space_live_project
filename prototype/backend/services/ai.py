import google.generativeai as genai
from typing import Dict, Optional, List, Any
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

class AIService:
    """AI對話服務 - 使用LangChain和Chroma實現記憶"""
    
    def __init__(self):
        # 配置Google API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
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
        
        # 創建或加載Chroma向量資料庫
        if not os.path.exists(settings.VECTOR_DB_PATH):
            os.makedirs(settings.VECTOR_DB_PATH)
            
        self.vectorstore = Chroma(
            persist_directory=settings.VECTOR_DB_PATH, 
            embedding_function=self.embeddings,
            collection_name="conversation_memory" # 顯式指定集合名稱
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": settings.VECTOR_MEMORY_K})
        
        # 使用消息列表替代ChatMessageHistory
        self.messages = []
        
        # 角色狀態管理
        self.character_state = {
            "health": 100,        # 健康狀態 (0-100)
            "mood": 70,           # 心情 (0-100)
            "energy": 80,         # 能量 (0-100)
            "task_success": 0,    # 任務成功次數
            "days_in_space": 1    # 太空天數
        }
        
        # 任務管理
        self.current_task = None  # 當前任務
        self.tasks_history = []   # 任務歷史
        
        # 創建提示模板
        self.prompt_template = PromptTemplate(
            input_variables=["history", "relevant_context", "current_emotion", "user_message", "character_state", "current_task"],
            template="""
            你是虛擬太空網紅，一個在太空站中體驗業餘太空生活一年的主播。你的特點：
            1. 回答簡短：盡量在1-3句話內完成
            2. 性格友好：親切且幽默
            3. 知識專業：擅長太空、科技領域知識
            4. 表達情感：展現適當的情緒反應
            5. 語音友好：生成的回應適合透過TTS轉換成語音
            
            你的當前狀態:
            {character_state}
            
            當前任務: {current_task}
            
            從你過去的對話中提取的相關背景資訊：
            {relevant_context}
            
            當前檢測到的情緒：{current_emotion}
            
            歷史對話：
            {history}
            
            請以太空網紅的身份回答以下提問（回應應適合TTS轉換，不要使用emoji）：
            用戶說: {user_message}
            """
        )
        
        # 創建RunnableSequence替代LLMChain
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
    async def generate_response(self, user_text: str, current_emotion: str) -> str:
        """
        基於使用者輸入和記憶生成AI回應
        
        Args:
            user_text: 使用者輸入文本
            current_emotion: 當前檢測到的情緒
            
        Returns:
            AI生成的回應
        """
        try:
            # 1. 檢索相關記憶 (使用 invoke 替代棄用的 get_relevant_documents)
            relevant_docs = await self.retriever.ainvoke(user_text)
            relevant_context = "\n".join([doc.page_content for doc in relevant_docs])
            
            # 2. 將使用者訊息添加到歷史
            self.messages.append(HumanMessage(content=user_text))
            
            # 3. 從歷史中格式化對話 (取最後 X 條消息，避免超出上下文長度)
            messages = self.messages[-settings.MEMORY_MAX_HISTORY:]
            history_text = "\n".join([f"{'用戶' if isinstance(msg, HumanMessage) else '助手'}: {msg.content}" 
                                    for i, msg in enumerate(messages)])
            
            # 4. 構建輸入參數
            inputs = {
                "user_message": user_text,
                "current_emotion": current_emotion,
                "character_state": json.dumps(self.character_state, ensure_ascii=False),
                "current_task": self.current_task if self.current_task else "無當前任務",
                "relevant_context": relevant_context if relevant_context else "無相關記憶",
                "history": history_text
            }
            
            # 5. 使用RunnableSequence生成回應
            ai_response_text = await self.chain.ainvoke(inputs)
            
            # 6. 將AI回應添加到歷史
            self.messages.append(AIMessage(content=ai_response_text))
            
            # 7. 將當前對話保存到向量儲存
            self.vectorstore.add_texts(
                texts=[f"用戶: {user_text}\n助手: {ai_response_text}"],
                metadatas=[{"type": "conversation"}]
            )
            
            # 8. 不再需要顯式調用 persist，新版 Chroma 會自動保存
            
            return ai_response_text
            
        except Exception as e:
            raise AIServiceException(f"生成AI回應失敗: {str(e)}")
            
    def update_character_state(self, updates: Dict[str, Any]) -> None:
        """
        更新角色狀態
        
        Args:
            updates: 要更新的狀態字典
        """
        for key, value in updates.items():
            if key in self.character_state:
                self.character_state[key] = value
                
                # 確保值在合理範圍內
                if key in ["health", "mood", "energy"]:
                    self.character_state[key] = max(0, min(100, self.character_state[key]))
                    
    def set_current_task(self, task: str) -> None:
        """
        設置當前任務
        
        Args:
            task: 任務描述
        """
        if self.current_task:
            # 將當前任務添加到歷史
            self.tasks_history.append(self.current_task)
        
        self.current_task = task
        
    def complete_current_task(self, success: bool = True) -> None:
        """
        完成當前任務
        
        Args:
            success: 任務是否成功
        """
        if self.current_task:
            # 記錄任務結果
            task_result = {
                "task": self.current_task,
                "success": success,
                "day": self.character_state["days_in_space"]
            }
            self.tasks_history.append(task_result)
            
            # 更新相關狀態
            if success:
                self.character_state["task_success"] += 1
                self.character_state["mood"] += 5
            else:
                self.character_state["mood"] -= 5
                
            # 重置當前任務
            self.current_task = None
            
    def advance_day(self) -> None:
        """推進一天時間並更新相關狀態"""
        self.character_state["days_in_space"] += 1
        
        # 能量每天自然恢復一些
        self.character_state["energy"] = min(100, self.character_state["energy"] + 10)
        
        # 如果沒有任務，心情可能下降
        if not self.current_task:
            self.character_state["mood"] = max(0, self.character_state["mood"] - 2) 