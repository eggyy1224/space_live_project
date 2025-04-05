import logging
import asyncio
import httpx # 用於異步 HTTP 請求
from typing import List, Dict, Any

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spaceflight News API v4 端點
SPACEFLIGHT_NEWS_API_URL = "https://api.spaceflightnewsapi.net/v4/articles/"

async def search_space_news(limit: int = 3) -> str:
    """獲取最新的太空飛行相關新聞。

    Args:
        limit (int): 要獲取的新聞數量，默認為 3。

    Returns:
        str: 包含最新新聞標題和摘要的格式化字串，或錯誤訊息。
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client: # 設置超時
            response = await client.get(SPACEFLIGHT_NEWS_API_URL, params={'limit': limit})
            response.raise_for_status() # 如果狀態碼不是 2xx，則引發異常

            data = response.json()
            articles = data.get('results', [])

            if not articles:
                logging.info("Spaceflight News API 返回了空的新聞列表。")
                return "目前沒有獲取到最新的太空新聞。"

            # 格式化新聞結果
            news_items = []
            for i, article in enumerate(articles):
                title = article.get('title', '無標題')
                summary = article.get('summary', '無摘要')
                # 限制摘要長度
                summary = summary[:100] + '...' if len(summary) > 100 else summary 
                news_items.append(f"{i+1}. {title}\n   摘要: {summary}")
            
            formatted_news = "\n\n".join(news_items)
            logging.info(f"成功從 Spaceflight News API 獲取到 {len(articles)} 條新聞。")
            return f"這是最新的幾條太空新聞：\n\n{formatted_news}"

    except httpx.HTTPStatusError as e:
        logging.error(f"請求 Spaceflight News API 時發生 HTTP 錯誤: {e.response.status_code} - {e.response.text}", exc_info=True)
        return f"抱歉，我在獲取太空新聞時遇到了網絡錯誤 (狀態碼: {e.response.status_code})。"
    except httpx.RequestError as e:
        logging.error(f"請求 Spaceflight News API 時發生連接錯誤: {e}", exc_info=True)
        return "抱歉，我在連接太空新聞服務時遇到了問題，請稍後再試。"
    except Exception as e:
        logging.error(f"處理太空新聞時發生未知錯誤: {e}", exc_info=True)
        return "抱歉，處理太空新聞時發生了內部錯誤。"

# 可以在此文件中添加其他與太空數據相關的工具函數
# 例如 get_iss_location 等 