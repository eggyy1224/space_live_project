import google.generativeai as genai
from typing import Dict, Optional
from core.config import settings
from core.exceptions import AIServiceException

class AIService:
    """AI對話服務"""
    
    def __init__(self):
        # 配置Google API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
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
            generation_config = {
                "temperature": settings.GENERATION_TEMPERATURE,
                "top_p": settings.GENERATION_TOP_P,
                "top_k": settings.GENERATION_TOP_K,
                "max_output_tokens": settings.GENERATION_MAX_TOKENS,
            }
            
            model = genai.GenerativeModel(
                model_name=settings.AI_MODEL_NAME,
                generation_config=generation_config
            )
            
            prompt = f"""
            你是虛擬太空人，一個專業太空站的助手。你的特點：
            1. 回答簡短：盡量在1-3句話內完成
            2. 性格友好：親切且幽默
            3. 知識專業：擅長太空、科技領域知識
            4. 表達情感：展現適當的情緒反應
            
            當前檢測到的情緒：{current_emotion}
            
            請以太空人的身份回答以下提問：
            用戶說: "{user_text}"
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            raise AIServiceException(f"生成AI回應失敗: {str(e)}") 