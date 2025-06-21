import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

# 為了能夠呼叫 send_message_to_frontend，我們需要從 control 模組匯入它
# 但直接匯入可能會產生循環依賴，更好的方法是將其邏輯重構為可共享的服務
# 暫時為了快速實現，我們先嘗試一種可以運作的方式
# 理想情況下: from services.messaging import send_message_service
from ..endpoints.control import send_message_to_frontend, SendMessageRequest

logger = logging.getLogger(__name__)
router = APIRouter()

class NewsRequest(BaseModel):
    limit: int = 3
    intro_text: Optional[str] = "各位觀眾，這裡是太空頻道，為您帶來最新頭條新聞。"

async def speak_news(request: NewsRequest):
    """獲取最新太空新聞並讓角色朗讀"""
    try:
        # 1. 獲取太空新聞
        news_api_url = "https://api.spaceflightnewsapi.net/v4/articles/"
        params = {"limit": request.limit}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(news_api_url, params=params)
            response.raise_for_status()
        
        data = response.json()
        articles = data.get("results", [])
        
        if not articles:
            # 如果沒有新聞，也讓角色說一聲
            await send_message_to_frontend(SendMessageRequest(content="抱歉，我目前找不到最新的太空新聞。"))
            return {"success": True, "message": "No news found, informed user."}

        # 2. 格式化新聞內容
        formatted_news = [f"第{i+1}則，{article['title']}。" for i, article in enumerate(articles)]
        full_content = f"{request.intro_text} " + " ".join(formatted_news)

        # 3. 使用 send_message 端點的邏輯讓角色說話
        # 我們直接傳遞一個 SendMessageRequest 物件
        await send_message_to_frontend(SendMessageRequest(content=full_content))
        
        logger.info(f"成功獲取並播報 {len(articles)} 則太空新聞。")
        
        return {
            "success": True,
            "message": f"Successfully fetched and broadcasted {len(articles)} news articles.",
            "news_content": full_content
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"從 Spaceflight News API 獲取新聞失敗: {e}")
        await send_message_to_frontend(SendMessageRequest(content="抱歉，新聞服務暫時無法連線。"))
        raise HTTPException(status_code=e.response.status_code, detail=f"Spaceflight News API error: {e.response.text}")
    except Exception as e:
        logger.error(f"處理太空新聞時發生錯誤: {e}")
        await send_message_to_frontend(SendMessageRequest(content="抱歉，處理新聞時發生內部錯誤。"))
        raise HTTPException(status_code=500, detail="An internal error occurred while processing space news.")

@router.post("/speak-latest-news")
async def speak_latest_news_endpoint(request: NewsRequest):
    return await speak_news(request) 