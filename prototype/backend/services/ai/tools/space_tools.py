import logging
import asyncio
import httpx # 用於異步 HTTP 請求
from typing import List, Dict, Any, Optional

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

# --- 新增 ISS 資訊工具 ---
OPEN_NOTIFY_ISS_NOW_URL = "http://api.open-notify.org/iss-now.json"
OPEN_NOTIFY_ASTROS_URL = "http://api.open-notify.org/astros.json"

async def get_iss_info() -> str:
    """獲取國際太空站 (ISS) 的即時經緯度位置和當前在太空中的宇航員人數。"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 並行獲取位置和人數信息
            iss_now_task = client.get(OPEN_NOTIFY_ISS_NOW_URL)
            astros_task = client.get(OPEN_NOTIFY_ASTROS_URL)
            
            responses = await asyncio.gather(iss_now_task, astros_task, return_exceptions=True)
            
            iss_now_response, astros_response = responses
            
            # 處理位置信息
            iss_position = None
            if isinstance(iss_now_response, httpx.Response):
                iss_now_response.raise_for_status()
                iss_data = iss_now_response.json()
                if iss_data.get('message') == 'success':
                    iss_position = iss_data.get('iss_position')
                    logging.info(f"成功獲取 ISS 位置: {iss_position}")
                else:
                    logging.warning(f"獲取 ISS 位置 API 返回非成功消息: {iss_data.get('message')}")
            elif isinstance(iss_now_response, Exception):
                logging.error(f"請求 ISS 位置時出錯: {iss_now_response}", exc_info=iss_now_response)

            # 處理人數信息
            astronaut_count = None
            astronaut_names = []
            if isinstance(astros_response, httpx.Response):
                astros_response.raise_for_status()
                astros_data = astros_response.json()
                if astros_data.get('message') == 'success':
                    astronaut_count = astros_data.get('number')
                    people = astros_data.get('people', [])
                    astronaut_names = [p['name'] for p in people if p.get('craft') == 'ISS'] # 只計算 ISS 上的
                    logging.info(f"成功獲取太空人數: {astronaut_count}, ISS 上: {len(astronaut_names)}")
                else:
                    logging.warning(f"獲取太空人數 API 返回非成功消息: {astros_data.get('message')}")
            elif isinstance(astros_response, Exception):
                 logging.error(f"請求太空人數時出錯: {astros_response}", exc_info=astros_response)
            
            # 組合結果
            results = []
            if iss_position:
                lat = float(iss_position.get('latitude', 0))
                lon = float(iss_position.get('longitude', 0))
                results.append(f"國際太空站目前的位置大約在緯度 {lat:.2f} 度，經度 {lon:.2f} 度。")
            else:
                 results.append("無法獲取國際太空站的即時位置。")
                 
            if astronaut_count is not None:
                results.append(f"目前總共有 {astronaut_count} 位宇航員在太空中，其中在國際太空站上有 {len(astronaut_names)} 位。")
                # 可以選擇性地列出名字，如果需要
                # if astronaut_names:
                #    results.append(f"他們是：{', '.join(astronaut_names)}.")
            else:
                results.append("無法獲取當前在太空中的宇航員人數。")
                
            return "\n".join(results)

    except httpx.HTTPStatusError as e:
        logging.error(f"請求 Open Notify API 時發生 HTTP 錯誤: {e.response.status_code}", exc_info=True)
        return f"抱歉，我在查詢太空站資訊時遇到了網絡錯誤 (狀態碼: {e.response.status_code})。"
    except httpx.RequestError as e:
        logging.error(f"請求 Open Notify API 時發生連接錯誤: {e}", exc_info=True)
        return "抱歉，我在連接太空站資訊服務時遇到了問題。"
    except Exception as e:
        logging.error(f"處理太空站資訊時發生未知錯誤: {e}", exc_info=True)
        return "抱歉，處理太空站資訊時發生了內部錯誤。"

# --- 新增月相工具 ---
from datetime import date, timedelta

# 更新 URL 以符合實際 API
USNO_MOON_PHASE_URL = "https://aa.usno.navy.mil/api/moon/phases/date"

async def get_moon_phase(date_str: Optional[str] = None) -> Dict[str, Any]:
    """獲取指定日期的月相名稱。如果未指定日期，則默認查詢當天。
    
    Returns:
        Dict[str, Any]: 包含查詢日期、英文月相、中文月相的字典，或包含 error 鍵的錯誤字典。
    """
    target_date = date.today()
    query_date_str = target_date.strftime("%Y-%m-%d") # 預設查詢日期字符串

    if date_str:
        try:
            # 非常基礎的日期解析，僅支持 YYYY-MM-DD
            # TODO: 添加更強健的日期解析，支持 "今天", "明天" 等
            if date_str.lower() == '今天':
                target_date = date.today()
            elif date_str.lower() == '明天':
                target_date = date.today() + timedelta(days=1)
            elif date_str.lower() == '昨天':
                 target_date = date.today() - timedelta(days=1)
            else:
                target_date = date.fromisoformat(date_str)
            query_date_str = target_date.strftime("%Y-%m-%d") # 更新查詢日期字符串
        except ValueError:
            logging.warning(f"無效的日期格式: {date_str}，無法查詢。")
            # 返回錯誤字典
            return {"error": f"你提供的日期格式 '{date_str}' 我看不懂欸，請用 YYYY-MM-DD 的格式告訴我。"}

    params = {
        'date': query_date_str
        # 注意：新 API 不使用 nump 參數
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(USNO_MOON_PHASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('error'):
                error_msg = data.get('errormsg', '未知 API 錯誤')
                logging.error(f"USNO 月相 API 返回錯誤: {error_msg}")
                # 返回錯誤字典
                return {"error": f"查詢月相時出錯了: {error_msg}"}
            
            # 新 API 數據格式有所不同，使用 phasedata 陣列
            phasedata = data.get('phasedata')
            if phasedata and len(phasedata) > 0:
                phase_name_en = phasedata[0].get('phase', 'Unknown Phase')
                # 簡單翻譯常見月相名稱 (可擴充)
                phase_translation = {
                    "New Moon": "新月 (朔月)",
                    "Waxing Crescent": "眉月",
                    "First Quarter": "上弦月",
                    "Waxing Gibbous": "盈凸月",
                    "Full Moon": "滿月 (望月)",
                    "Waning Gibbous": "虧凸月",
                    "Last Quarter": "下弦月",
                    "Waning Crescent": "殘月"
                }
                phase_name_zh = phase_translation.get(phase_name_en, phase_name_en)
                
                logging.info(f"成功獲取日期 {target_date} 的月相: {phase_name_en} ({phase_name_zh})")
                
                # *** 返回結構化字典 ***
                return {
                    "query_date": query_date_str,
                    "phase_name_en": phase_name_en,
                    "phase_name_zh": phase_name_zh
                }
            else:
                logging.warning("USNO 月相 API 返回數據中未找到月相信息。")
                # 返回錯誤字典
                return {"error": "抱歉，我沒能查到那天的月相信息。"}

    except httpx.HTTPStatusError as e:
        logging.error(f"請求 USNO 月相 API 時發生 HTTP 錯誤: {e.response.status_code}", exc_info=True)
        # 返回錯誤字典
        return {"error": f"抱歉，我在查詢月相時遇到了網絡錯誤 (狀態碼: {e.response.status_code})。"}
    except httpx.RequestError as e:
        logging.error(f"請求 USNO 月相 API 時發生連接錯誤: {e}", exc_info=True)
        # 返回錯誤字典
        return {"error": "抱歉，我在連接月相查詢服務時遇到了問題。"}
    except Exception as e:
        logging.error(f"處理月相查詢時發生未知錯誤: {e}", exc_info=True)
        # 返回錯誤字典
        return {"error": "抱歉，處理月相查詢時發生了內部錯誤。"} 