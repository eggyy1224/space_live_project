# 已整合外部工具文檔

本文檔說明了目前整合到虛擬太空人後端服務中的外部工具及其運作方式。

## 1. 工具處理流程概觀

系統中的工具處理主要由 `DialogueGraph`（位於 `prototype/backend/services/ai/dialogue_graph.py`）協調，並通過 `tool_processing.py` 中的節點執行。基本流程如下：

1.  **意圖檢測 (`detect_tool_intent`)**：LLM 分析用戶輸入，判斷是否需要使用工具以及哪個工具最合適。
2.  **參數解析 (`parse_tool_parameters`)**：如果確定需要工具，LLM 會根據該工具的定義從用戶輸入中提取所需參數。
3.  **工具執行 (`execute_tool`)**：調用對應的工具函數（例如 `search_space_news`）並傳入解析出的參數。
4.  **結果格式化 (`format_tool_result_for_llm`)**：將工具返回的原始結果（通常是字典或 JSON 字符串）格式化成適合 LLM 理解的文本。
5.  **結果整合 (`integrate_tool_result`)**：根據工具執行狀態（成功或失敗），選擇相應的提示模板（`tool_response` 或 `tool_error_response`）並將格式化結果或錯誤信息注入狀態。

## 2. 已整合工具詳情

目前系統整合了以下三個主要的外部工具：

### 2.1 USNO 月相查詢 (`get_moon_phase`)

*   **功能**：查詢指定日期的月相。
*   **系統內函數**：`get_moon_phase` (位於 `prototype/backend/services/ai/tools/space_tools.py`)
*   **外部 API**：美國海軍天文台 (USNO) Astronomical Applications API
    *   **端點**：`https://aa.usno.navy.mil/api/moon/phases/date`
    *   **文檔**：[https://aa.usno.navy.mil/data/api](https://aa.usno.navy.mil/data/api)
*   **參數**：
    *   `date_str` (Optional[str])：要查詢的日期。
        *   格式：`YYYY-MM-DD`（例如 `2024-05-10`）
        *   特殊值：`今天`, `明天`, `昨天`
        *   如果未提供，默認查詢當天。
*   **內部處理**：
    *   `parse_tool_parameters` 節點使用 LLM 從用戶輸入中提取 `date_str`。
    *   `get_moon_phase` 函數調用 USNO API。
*   **輸出**：
    *   **成功**：返回包含以下鍵的字典（序列化為 JSON 字符串）：
        *   `query_date`: 查詢的日期 (YYYY-MM-DD)
        *   `phase_name_en`: 英文月相名稱
        *   `phase_name_zh`: 中文月相名稱
    *   **失敗**：返回包含 `error` 鍵和錯誤描述的字典。
*   **結果格式化**：`format_moon_phase_result` 函數將成功的 JSON 結果轉換為包含月相名稱和描述的友好文本供 LLM 使用。

### 2.2 Spaceflight News API 搜索 (`search_space_news`)

*   **功能**：搜索太空相關新聞。
*   **系統內函數**：`search_space_news` (位於 `prototype/backend/services/ai/tools/space_tools.py`)
*   **外部 API**：Spaceflight News API v4
    *   **端點**：`https://api.spaceflightnewsapi.net/v4/articles/`
    *   **文檔/瀏覽器**：[https://api.spaceflightnewsapi.net/v4/documentation/](https://api.spaceflightnewsapi.net/v4/documentation/) (API 文檔)，[https://api.spaceflightnewsapi.net/v4/articles/](https://api.spaceflightnewsapi.net/v4/articles/) (API 端點，可直接瀏覽)
*   **參數**：
    *   `keywords` (Optional[str])：搜索的關鍵詞或主題。
    *   `time_period` (Optional[str])：搜索的時間範圍。
        *   支持相對時間：`今天`, `昨天`, `本週`, `上週`, `本月`, `上個月`, `今年`, `去年`, `X天前`, `X天後`
        *   支持特定年份：`YYYY年` 或 `YYYY` (例如 `2020年`, `2005`)
    *   `limit` (int)：返回的新聞數量，默認為 3。
*   **內部處理**：
    *   `parse_tool_parameters` 節點使用 LLM 並行提取 `keywords` 和 `time_period`。特別注意避免將時間範圍誤判為關鍵詞。
    *   `search_space_news` 函數：
        *   如果 `keywords` 是年份格式，則自動將其移至 `time_period` 進行時間範圍搜索。
        *   如果提供了 `time_period` 但沒有 `keywords`，則僅按時間範圍搜索。
        *   調用 Spaceflight News API 時，會根據解析出的 `time_period` 設置 `published_at_gte` 和 `published_at_lte` 參數。
        *   如果用戶查詢「今年」的新聞但 API 返回空結果，會嘗試去除時間限制，再次搜索最新的新聞作為備選。
*   **輸出**：
    *   **成功**：返回包含以下鍵的字典（序列化為 JSON 字符串）：
        *   `error`: `False`
        *   `count`: 返回的文章數量
        *   `total_count`: API 匹配的總文章數
        *   `search_params`: 實際使用的搜索參數
        *   `search_description`: 格式化的搜索描述（例如 "2020年的"）
        *   `articles`: 包含新聞列表的陣列，每條新聞包含 `title`, `summary`, `news_site`, `published_at`, `url`
        *   `note` (Optional[str]): 如果返回的是備選的最新新聞，則包含此說明。
    *   **失敗**：返回包含 `error`: `True` 和 `message` 的字典。
*   **結果格式化**：`format_space_news_result` 函數：
    *   將成功的 JSON 結果格式化為易於閱讀的新聞列表。
    *   如果返回的是備選新聞，會在開頭說明。
    *   如果搜索結果為空，會根據是否搜索舊年份提供不同的提示（例如提示 API 對舊數據支持有限）。

### 2.3 Wikipedia 搜索 (`search_wikipedia`)

*   **功能**：查詢維基百科以獲取特定主題的簡短摘要。
*   **系統內函數**：`search_wikipedia` (位於 `prototype/backend/services/ai/tools/web_tools.py`)
*   **外部 API/庫**：使用 Python 的 `wikipedia` 庫。
*   **參數**：
    *   `query` (str)：要查詢的主題或關鍵字（必需）。
*   **內部處理**：
    *   `parse_tool_parameters` 節點使用 LLM 從用戶輸入中提取 `query` 參數。
    *   `search_wikipedia` 函數調用 `wikipedia` 庫，並設置語言為 `zh-tw`（繁體中文）。
    *   使用 `asyncio.get_running_loop().run_in_executor` 將同步庫調用變為非阻塞。
    *   處理可能的 `PageError`（找不到頁面）和 `DisambiguationError`（歧義）。
*   **輸出**：
    *   **成功**：返回包含摘要的格式化字符串。
    *   **失敗/歧義**：返回相應的錯誤或歧義提示字符串。
*   **結果格式化**：由於此工具直接返回字符串，`format_tool_result_for_llm` 節點通常會將其直接包含在標準格式中。

## 3. 如何添加新工具

1.  **創建工具函數**：在 `tools` 目錄下（例如 `space_tools.py` 或 `web_tools.py`）創建一個 `async` 函數來實現工具邏輯。
    *   函數應接受必要的參數。
    *   函數應返回一個字典（成功時包含結果，失敗時包含 `error` 鍵）或一個字符串。
2.  **註冊工具**：在 `DialogueGraph` 的 `__init__` 方法中，將新工具添加到 `self.available_tools` 字典。
    *   提供工具名稱（鍵）。
    *   提供 `function`（指向你的工具函數）。
    *   提供 `description`（給 LLM 用於意圖判斷）。
    *   定義 `parameters` 列表，描述每個參數的 `name`, `type`, `description`, 和 `required` (默認為 True)。
3.  **更新參數解析**：在 `tool_processing.py` 的 `parse_tool_parameters` 函數中，為你的新工具添加 `elif potential_tool == 'your_tool_name':` 分支，並編寫使用 LLM 提取參數的邏輯（參考現有工具的實現）。
4.  **(可選) 更新結果格式化**：如果希望對工具的成功結果進行特殊格式化，可以在 `tool_processing.py` 的 `format_tool_result_for_llm` 函數中添加對應的處理邏輯（例如創建 `format_your_tool_result` 函數）。如果返回簡單字符串或標準字典，此步驟可能不是必需的。
5.  **重啟服務**：重新啟動後端服務以應用更改。 