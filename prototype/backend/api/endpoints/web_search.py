import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5
    language: str = "zh-TW"
    safe_search: str = "active"

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    display_link: str

class WebSearchResponse(BaseModel):
    success: bool
    query: str
    results: List[SearchResult]
    total_results: Optional[str] = None
    search_time: Optional[float] = None

@router.post("/web-search", response_model=WebSearchResponse)
async def web_search(request: WebSearchRequest):
    """
    使用 Google Custom Search API 進行網頁搜尋
    
    需要設定環境變數：
    - GOOGLE_SEARCH_API_KEY: Google API 金鑰
    - GOOGLE_SEARCH_ENGINE_ID: 自訂搜尋引擎 ID
    """
    try:
        # 檢查環境變數
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            raise HTTPException(
                status_code=500, 
                detail="Google Search API 配置不完整。請設定 GOOGLE_SEARCH_API_KEY 和 GOOGLE_SEARCH_ENGINE_ID 環境變數。"
            )
        
        # Google Custom Search API 端點
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": request.query,
            "num": min(request.num_results, 10),  # Google API 限制最多 10 個結果
            "lr": f"lang_{request.language[:2]}" if request.language else None,
            "safe": request.safe_search,
            "fields": "items(title,link,snippet,displayLink),searchInformation(totalResults,searchTime)"
        }
        
        # 移除 None 值
        params = {k: v for k, v in params.items() if v is not None}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            
        data = response.json()
        
        # 解析搜尋結果
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    display_link=item.get("displayLink", "")
                ))
        
        # 取得搜尋資訊
        search_info = data.get("searchInformation", {})
        total_results = search_info.get("totalResults")
        search_time = search_info.get("searchTime")
        
        logger.info(f"Google 搜尋成功：查詢 '{request.query}' 返回 {len(results)} 個結果")
        
        return WebSearchResponse(
            success=True,
            query=request.query,
            results=results,
            total_results=total_results,
            search_time=float(search_time) if search_time else None
        )
        
    except httpx.TimeoutException:
        logger.error(f"Google 搜尋超時：{request.query}")
        raise HTTPException(status_code=408, detail="搜尋請求超時")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Google API 錯誤 {e.response.status_code}：{e.response.text}")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="搜尋 API 配額已用完，請稍後再試")
        elif e.response.status_code == 403:
            raise HTTPException(status_code=403, detail="Google API 金鑰無效或權限不足")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=f"Google API 錯誤：{e.response.text}")
            
    except Exception as e:
        logger.error(f"網頁搜尋時發生錯誤：{str(e)}")
        raise HTTPException(status_code=500, detail=f"搜尋時發生內部錯誤：{str(e)}")

@router.get("/web-search/test")
async def test_web_search():
    """
    測試網頁搜尋 API 配置
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    return {
        "api_key_configured": bool(api_key),
        "search_engine_id_configured": bool(search_engine_id),
        "status": "ready" if (api_key and search_engine_id) else "需要配置環境變數"
    } 