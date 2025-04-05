import logging
import asyncio
import httpx # 用於異步 HTTP 請求
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spaceflight News API v4 端點
SPACEFLIGHT_NEWS_API_URL = "https://api.spaceflightnewsapi.net/v4/articles/"

# 擴展 search_space_news 函數，支持更多搜索參數
async def search_space_news(
    keywords: Optional[str] = None,
    time_period: Optional[str] = None, 
    search_fields: Optional[str] = "both", 
    limit: int = 3
) -> Dict[str, Any]:
    """智能搜索太空飛行相關新聞，支持關鍵詞和時間範圍。
    
    Args:
        keywords (str, optional): 要搜索的關鍵詞，默認為 None (搜索所有新聞)
        time_period (str, optional): 時間範圍，例如"今天"、"昨天"、"本週"、"本月"、"今年"、"去年"，也支持"2020年"這樣的特定年份，默認為 None (所有時間)
        search_fields (str, optional): 搜索關鍵詞的字段，可選值為"title"(僅標題)、"summary"(僅摘要)、"both"(標題和摘要)，默認為 "both"
        limit (int): 要獲取的新聞數量，默認為 3
        
    Returns:
        Dict[str, Any]: 包含搜索結果的字典，或包含錯誤信息的字典
    """
    params = {'limit': limit}
    
    # 檢查 keywords 是否為年份，如果是，則轉換為時間範圍
    if keywords and re.match(r'^\d{4}年?$', keywords):
        logging.info(f"關鍵詞是年份: {keywords}，將其轉換為時間範圍搜索而非關鍵詞搜索")
        # 提取年份並設置為時間範圍
        year_match = re.match(r'^(\d{4})年?$', keywords)
        if year_match:
            time_period = keywords
            keywords = None  # 清空關鍵詞，改用時間範圍搜索
    
    # 處理日期範圍
    dates = parse_time_period(time_period)
    if dates:
        start_date, end_date = dates
        if start_date:
            params['published_at_gte'] = start_date
        if end_date:
            params['published_at_lte'] = end_date
    
    # 處理關鍵詞搜索
    if keywords:
        # 根據 search_fields 參數決定搜索的字段
        if search_fields == "title" or search_fields == "both":
            params['title_contains'] = keywords
        if search_fields == "summary" or search_fields == "both":
            params['summary_contains'] = keywords
    
    # 記錄實際搜索參數
    logging.info(f"搜索太空新聞，參數: {params}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client: # 設置超時
            response = await client.get(SPACEFLIGHT_NEWS_API_URL, params=params)
            response.raise_for_status() # 如果狀態碼不是 2xx，則引發異常

            data = response.json()
            articles = data.get('results', [])
            total_count = data.get('count', 0)

            if not articles:
                logging.info("Spaceflight News API 返回了空的新聞列表。")
                search_description = format_search_description(keywords, time_period, search_fields)
                
                # 如果有時間範圍但沒有結果，嘗試僅搜索較新的新聞
                if time_period and ('今年' in time_period or re.search(r'2025年?', time_period)):
                    logging.info("搜索今年新聞但無結果，嘗試取最新新聞")
                    async with httpx.AsyncClient(timeout=10.0) as retry_client:
                        # 只限制數量，不加其他條件
                        retry_params = {'limit': limit}
                        retry_response = await retry_client.get(SPACEFLIGHT_NEWS_API_URL, params=retry_params)
                        retry_response.raise_for_status()
                        retry_data = retry_response.json()
                        retry_articles = retry_data.get('results', [])
                        
                        if retry_articles:
                            logging.info(f"成功獲取到 {len(retry_articles)} 條最新新聞作為備選")
                            return {
                                "error": False,
                                "count": len(retry_articles),
                                "total_count": retry_data.get('count', 0),
                                "search_params": {
                                    "keywords": keywords,
                                    "time_period": time_period,
                                    "search_fields": search_fields
                                },
                                "search_description": search_description,
                                "articles": format_articles(retry_articles),
                                "note": "未找到完全符合條件的新聞，改為顯示最新新聞"
                            }
                
                return {
                    "error": False,
                    "count": 0,
                    "search_params": {
                        "keywords": keywords,
                        "time_period": time_period,
                        "search_fields": search_fields
                    },
                    "search_description": search_description,
                    "message": f"找不到{search_description}的太空新聞。"
                }

            # 使用封裝函數格式化新聞
            formatted_articles = format_articles(articles)
            
            logging.info(f"成功從 Spaceflight News API 獲取到 {len(articles)} 條新聞，總匹配數: {total_count}。")
            
            search_description = format_search_description(keywords, time_period, search_fields)
            return {
                "error": False,
                "count": len(articles),
                "total_count": total_count,
                "search_params": {
                    "keywords": keywords,
                    "time_period": time_period,
                    "search_fields": search_fields
                },
                "search_description": search_description,
                "articles": formatted_articles
            }

    except httpx.HTTPStatusError as e:
        logging.error(f"請求 Spaceflight News API 時發生 HTTP 錯誤: {e.response.status_code} - {e.response.text}", exc_info=True)
        return {
            "error": True,
            "message": f"抱歉，我在獲取太空新聞時遇到了網絡錯誤 (狀態碼: {e.response.status_code})。"
        }
    except httpx.RequestError as e:
        logging.error(f"請求 Spaceflight News API 時發生連接錯誤: {e}", exc_info=True)
        return {
            "error": True,
            "message": "抱歉，我在連接太空新聞服務時遇到了問題，請稍後再試。"
        }
    except Exception as e:
        logging.error(f"處理太空新聞時發生未知錯誤: {e}", exc_info=True)
        return {
            "error": True,
            "message": "抱歉，處理太空新聞時發生了內部錯誤。"
        }

def parse_time_period(time_period: Optional[str]) -> Optional[tuple]:
    """解析時間範圍字符串，返回起止日期元組 (開始日期, 結束日期)"""
    if not time_period:
        return None
    
    today = date.today()
    
    # 嘗試從字符串中識別時間範圍
    time_period = time_period.lower()
    logging.info(f"解析時間範圍: '{time_period}'")
    
    # 首先嘗試從字符串中提取四位數年份，不限於開頭
    year_match = re.search(r'(\d{4})\s*年?', time_period)
    if year_match:
        year = int(year_match.group(1))
        if 1900 <= year <= 2100:  # 合理年份範圍
            start_date = date(year, 1, 1).isoformat()
            end_date = date(year, 12, 31).isoformat()
            logging.info(f"成功解析出年份: {year}，設置日期範圍: {start_date} 至 {end_date}")
            return (start_date, end_date)
    
    # 特定時間範圍
    if time_period in ["今天", "今日"]:
        start_date = today.isoformat()
        end_date = today.isoformat()
        logging.info(f"識別為今天: {start_date}")
    elif time_period in ["昨天", "昨日"]:
        yesterday = today - timedelta(days=1)
        start_date = yesterday.isoformat()
        end_date = yesterday.isoformat()
        logging.info(f"識別為昨天: {start_date}")
    elif time_period in ["本週", "這週", "這一週"]:
        # 本週的第一天 (星期一)
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week.isoformat()
        end_date = today.isoformat()
        logging.info(f"識別為本週: {start_date} 至 {end_date}")
    elif time_period in ["上週", "上一週", "前一週"]:
        # 上週的第一天 (星期一)
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        start_date = start_of_last_week.isoformat()
        end_date = end_of_last_week.isoformat()
    elif time_period in ["本月", "這個月"]:
        # 本月的第一天
        start_of_month = date(today.year, today.month, 1)
        start_date = start_of_month.isoformat()
        end_date = today.isoformat()
    elif time_period in ["上個月", "前一個月"]:
        # 計算上個月
        if today.month == 1:
            previous_month = 12
            previous_year = today.year - 1
        else:
            previous_month = today.month - 1
            previous_year = today.year
        
        # 上個月的第一天
        start_of_prev_month = date(previous_year, previous_month, 1)
        
        # 上個月的最後一天
        if previous_month == 12:
            end_of_prev_month = date(previous_year, previous_month, 31)
        else:
            end_of_prev_month = date(previous_year, previous_month + 1, 1) - timedelta(days=1)
        
        start_date = start_of_prev_month.isoformat()
        end_date = end_of_prev_month.isoformat()
    elif time_period in ["今年", "本年"]:
        start_of_year = date(today.year, 1, 1)
        start_date = start_of_year.isoformat()
        end_date = today.isoformat()
    elif time_period in ["去年", "上一年"]:
        start_of_prev_year = date(today.year - 1, 1, 1)
        end_of_prev_year = date(today.year - 1, 12, 31)
        start_date = start_of_prev_year.isoformat()
        end_date = end_of_prev_year.isoformat()
    # 正則表達式捕獲「X 天前」或「X 天後」的模式
    elif re.match(r'(\d+)天(前|後|后)', time_period):
        match = re.match(r'(\d+)天(前|後|后)', time_period)
        days = int(match.group(1))
        direction = match.group(2)
        
        if direction in ["前"]:
            target_date = today - timedelta(days=days)
            start_date = target_date.isoformat()
            end_date = target_date.isoformat()
        else:  # "後" or "后"
            target_date = today + timedelta(days=days)
            start_date = target_date.isoformat()
            end_date = target_date.isoformat()
    else:
        # 如果無法識別時間範圍，返回 None
        logging.warning(f"無法識別的時間範圍: {time_period}")
        return None
    
    return (start_date, end_date)

def format_search_description(keywords: Optional[str], time_period: Optional[str], search_fields: Optional[str]) -> str:
    """格式化搜索描述"""
    description_parts = []
    
    if time_period:
        description_parts.append(f"{time_period}")
    
    if keywords:
        field_description = ""
        if search_fields == "title":
            field_description = "標題中包含"
        elif search_fields == "summary":
            field_description = "摘要中包含"
        else:  # both
            field_description = "標題或摘要中包含"
        
        description_parts.append(f"{field_description}'{keywords}'的")
    
    if description_parts:
        return "".join(description_parts)
    else:
        return "最新"

def format_articles(articles: List[Dict]) -> List[Dict]:
    """統一格式化新聞結果的函數"""
    formatted_articles = []
    for article in articles:
        published_at = article.get('published_at')
        if published_at:
            try:
                # 將 UTC 時間轉換為本地時間並格式化
                dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%Y年%m月%d日 %H:%M")
            except ValueError:
                formatted_date = published_at
        else:
            formatted_date = "未知日期"
        
        formatted_articles.append({
            "title": article.get('title', '無標題'),
            "summary": article.get('summary', '無摘要'),
            "news_site": article.get('news_site', '未知來源'),
            "published_at": formatted_date,
            "url": article.get('url', '')
        })
    
    return formatted_articles

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