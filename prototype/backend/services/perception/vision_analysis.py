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
仔細分析畫面中出現的人物特徵：

**人物描述**：
- 人數和性別
- 年齡特徵
- 外貌特徵（髮型、服裝、配件等）
- 表情和情緒狀態
- 動作和姿態
- 彼此的互動方式

請簡潔具體地描述每個人的特徵，用繁體中文回答。
""",

            "screen_output": """
客觀描述這張 OBS 主螢幕輸出截圖的內容：

**畫面內容描述**：
- 主要顯示內容：畫面中出現什麼？
- 人物狀況：如有人物，描述其位置、動作、表情
- 介面元素：文字、按鈕、圖標、邊框等
- 背景環境：場景、燈光、色調
- 特效層次：是否有疊加的圖層、特效、字幕

**技術狀態觀察**：
- 畫面完整性：是否完整顯示，有無黑邊或異常區域
- 清晰度狀況：畫面是否清晰可見
- 色彩表現：顏色是否正常顯示

請用繁體中文客觀且具體地描述所見內容，避免主觀評價。
""",

            "exhibition_field": """
分析展場現場狀況：

**展場活動狀況**：
- 人流密度：觀眾數量和分布
- 互動熱度：觀眾參與程度
- 展品狀態：展示設備是否正常
- 環境氛圍：燈光、音響、整體感受
- 安全狀況：秩序、通道暢通等

**觀眾行為**：
- 觀眾在做什麼？
- 對展品的反應如何？
- 有沒有排隊或聚集？

請用繁體中文描述，重點關注展場運營狀況。
""",

            "web_content": """
客觀描述網頁瀏覽器畫面內容：

**網頁內容**：
- 網站類型：所訪問的網站性質
- 頁面內容：主要顯示的文字、圖片、影片等
- 介面元素：導航欄、按鈕、表單、選單等
- 瀏覽器狀態：網址欄、標籤頁、工具列等

**顯示狀況**：
- 頁面載入狀態：是否完整顯示
- 錯誤提示：如有錯誤訊息，具體描述
- 內容完整性：頁面元素是否正常呈現

請用繁體中文客觀描述所見內容。
""",

            "camera_feed": """
客觀描述攝影機畫面內容：

**畫面內容**：
- 拍攝場景：攝影機所對準的環境或空間
- 主體對象：畫面中的主要人物或物件
- 人物狀況：如有人物，描述其位置、動作、數量
- 環境背景：周圍的環境、物品、裝飾等

**視覺狀況**：
- 畫面角度：攝影機的拍攝角度和範圍
- 光線情況：亮度、陰影、光源方向
- 清晰度：畫面是否清楚可見
- 色彩表現：顏色的呈現狀況

請用繁體中文客觀描述攝影機捕捉到的內容。
""",

            "desktop_capture": """
分析桌面截圖：

**桌面狀況**：
- 開啟的應用程式
- 正在進行的工作
- 桌面佈局和組織
- 系統狀態指示

**工作流程**：
- 使用者在做什麼？
- 工作效率如何？
- 有沒有異常狀況？

請用繁體中文描述桌面使用狀況。
"""
        }
        
        return prompts.get(analysis_type, prompts["general"])