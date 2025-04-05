import wikipedia
import logging
import asyncio

# 配置基本日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 注意：wikipedia 庫是同步的，但在異步環境中使用 run_in_executor 將其變為非阻塞
async def search_wikipedia(query: str) -> str:
    """從維基百科查詢指定主題的簡短摘要。

    Args:
        query (str): 要查詢的主題或關鍵字。

    Returns:
        str: 包含查詢結果或錯誤信息的格式化字串。
    """
    loop = asyncio.get_running_loop()
    try:
        # 在執行器中運行同步的 wikipedia 庫函數
        def run_sync_wikipedia():
            try:
                wikipedia.set_lang("zh-tw") # 設置語言為繁體中文
                # 獲取摘要，句子數量可根據需要調整
                summary = wikipedia.summary(query, sentences=2)
                logging.info(f"維基百科查詢 '{query}' 成功。")
                return f"這是維基百科上關於 '{query}' 的摘要：{summary}"
            except wikipedia.exceptions.PageError:
                logging.warning(f"維基百科找不到頁面：'{query}'")
                return f"抱歉，維基百科上找不到關於 '{query}' 的頁面。"
            except wikipedia.exceptions.DisambiguationError as e:
                logging.warning(f"維基百科查詢 '{query}' 存在歧義：{e.options}")
                options_str = ", ".join(e.options[:3])
                return f"你問的 '{query}' 可能指多個意思，例如：{options_str}。能說得更具體一點嗎？這有助於我找到更精確的資訊。"
            except Exception as sync_e:
                # 捕獲同步函數內的異常
                logging.error(f"維基百科同步查詢 '{query}' 時內部出錯: {sync_e}", exc_info=True)
                return f"抱歉，我在維基百科內部查詢 '{query}' 時遇到了技術問題。"

        # 使用 asyncio 在線程池執行器中運行同步代碼
        result = await loop.run_in_executor(None, run_sync_wikipedia)
        return result

    except Exception as e:
        # 捕獲 run_in_executor 或 asyncio 本身的異常
        logging.error(f"異步執行維基百科查詢 '{query}' 時出錯: {e}", exc_info=True)
        return f"抱歉，我在嘗試查詢維基百科時遇到了系統層面的問題。"

# 可以在這裡添加其他網頁工具，例如搜尋引擎查詢等 