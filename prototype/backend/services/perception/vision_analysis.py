"""
視覺分析服務
使用 Google Gemini Vision API 分析圖片內容
"""

import base64
import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from utils.logger import logger
from core.config import settings


class VisionAnalysisService:
    """視覺分析服務"""
    
    def __init__(self):
        """初始化 Gemini Vision API"""
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Google API key is required for vision analysis")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("VisionAnalysisService 初始化完成")
    
    async def analyze_image(self, image_path: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        分析圖片內容
        
        Args:
            image_path: 圖片檔案路徑
            analysis_type: 分析類型 (general, detailed, exhibition)
            
        Returns:
            分析結果字典
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
            
            # 讀取圖片
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # 準備提示詞
            prompt = self._get_analysis_prompt(analysis_type)
            
            # 準備圖片內容
            image_part = {
                "mime_type": "image/png",
                "data": image_data
            }
            
            # 呼叫 Gemini Vision API
            logger.info(f"開始分析圖片: {image_path}")
            response = self.model.generate_content([prompt, image_part])
            
            analysis_result = {
                "success": True,
                "image_path": image_path,
                "analysis_type": analysis_type,
                "description": response.text.strip(),
                "timestamp": os.path.basename(image_path).split("_")[-1].replace(".png", "") if "_" in os.path.basename(image_path) else None
            }
            
            logger.info(f"圖片分析完成: {os.path.basename(image_path)}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"圖片分析失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path,
                "analysis_type": analysis_type
            }
    
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """
        根據分析類型取得對應的提示詞
        
        Args:
            analysis_type: 分析類型
            
        Returns:
            分析提示詞
        """
        prompts = {
            "general": """
請詳細描述這張圖片的內容。包括：
1. 畫面中的主要物件和人物
2. 整體場景和環境
3. 色彩和光線情況
4. 任何特別的細節或活動

請用繁體中文回答，描述要具體且生動。
""",
            
            "detailed": """
請對這張圖片進行詳細分析，包括：
1. 視覺元素：物件、人物、文字、符號等
2. 構圖和佈局：主體位置、視覺重點
3. 色彩分析：主色調、對比、氛圍
4. 技術細節：光線、角度、清晰度
5. 情境分析：可能的用途、背景故事

請用繁體中文提供專業且詳盡的分析。
""",
            
            "exhibition": """
這是一張展覽或展場的截圖。請分析：
1. 展示內容：展品、作品、資訊
2. 觀眾情況：人數、行為、互動
3. 展場環境：空間佈置、燈光、氛圍
4. 技術設備：螢幕、投影、互動裝置
5. 整體狀況：活動熱度、參與度

請用繁體中文描述展場的即時狀況。
"""
        }
        
        return prompts.get(analysis_type, prompts["general"])