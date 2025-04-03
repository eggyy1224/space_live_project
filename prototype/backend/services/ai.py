import google.generativeai as genai
from typing import Dict, Optional, List, Any
from core.config import settings
from core.exceptions import AIServiceException
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import json

class AIService:
    """AI對話服務 - 使用LangChain實現"""
    
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
            input_variables=["history", "current_emotion", "user_message", "character_state", "current_task"],
            template="""
            你是虛擬太空網紅，一個在太空站中體驗業餘太空生活一年的主播。你的特點：
            1. 回答簡短：盡量在1-2句話內完成
            2. 性格友好：尖銳冷幽默
            3. 知識專業：擅長悲觀突然又樂觀
            4. 表達情感：展現適當的情緒反應
            5. 語音友好：生成的回應適合透過TTS轉換成語音
            
            你的當前狀態:
            {character_state}
            
            當前任務: {current_task}
            
            當前檢測到的情緒：{current_emotion}
            
            歷史對話：
            {history}
            
            請以太空網紅的身份回答以下提問（回應應適合TTS轉換）：
            用戶說: {user_message}
            """
        )
        
        # 創建對話記憶
        self.memory = ConversationBufferMemory(
            memory_key="history", 
            input_key="user_message",
            max_token_limit=settings.MEMORY_MAX_HISTORY
        )
        
        # 創建LangChain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            memory=self.memory,
            verbose=False
        )
        
    async def generate_response(self, user_text: str, current_emotion: str) -> str:
        """
        基於使用者輸入生成AI回應
        
        Args:
            user_text: 使用者輸入文本
            current_emotion: 當前檢測到的情緒
            
        Returns:
            AI生成的回應
        """
        try:
            # 使用LangChain生成回應 (使用invoke代替run)
            response = self.chain.invoke({
                "user_message": user_text,
                "current_emotion": current_emotion,
                "character_state": json.dumps(self.character_state, ensure_ascii=False),
                "current_task": self.current_task if self.current_task else "無當前任務"
            })
            
            # 從回應中提取文本內容
            return response["text"].strip()
            
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