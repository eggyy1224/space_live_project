# 整合太空虛擬網紅的外部 API 工具評估

## 即時天氣與地圖資訊工具

即時地面天氣和地圖資料能讓虛擬網紅描述太空站所見的地球情況，增加互動趣味。例如：

- **OpenWeatherMap 天氣 API** – 提供全球各地的即時天氣資訊，回傳格式為 JSON（預設）。回傳資料包含位置座標、天氣概況、溫度、濕度等；甚至有文字描述如“moderate rain”（中雨）及對應的圖示代碼。這種結構化資料方便 AI 擷取關鍵資訊生成對話內容。
    
    [openweathermap.org](https://openweathermap.org/current#:~:text=Access%20current%20weather%20data%20for,JSON%2C%20XML%2C%20or%20HTML%20format)
    
    [openweathermap.org](https://openweathermap.org/current#:~:text=,stations)
    
- **Google 靜態地圖 API** – 提供靜態地圖圖像，透過 HTTP 請求傳回 PNG/JPEG 圖片。開發者可指定地圖中心經緯度、縮放級別、地圖類型及標記等參數，API 即會回傳對應的地圖影像。例如，利用國際太空站即時經緯度取得其下方地球區域的地圖，搭配天氣資料一起展示。
    
    [developers.google.com](https://developers.google.com/maps/documentation/maps-static/start#:~:text=The%20Maps%20Static%20API%20returns,your%20markers%20using%20alphanumeric%20characters)
    
    [developers.google.com](https://developers.google.com/maps/documentation/maps-static/start#:~:text=The%20Maps%20Static%20API%20returns,your%20markers%20using%20alphanumeric%20characters)
    

*資料格式與多模態適配：* 天氣 API 的 JSON 結果易於解析出文字描述（如氣溫、氣象狀態），地圖 API 則提供可直接嵌入的圖片文件。這兩種資料非常適合結合 **Gemini 2.0 Flash** 的多模態生成能力：AI 可以一方面用文字說明當前地球某地的天氣，另一方面前端同步展示該地區地圖或衛星影像。比如，「目前太空站正飛越臺灣上空，底下台中的天氣是晴朗 25°C

[openweathermap.org](https://openweathermap.org/current#:~:text=,stations)

」，同時顯示台中位置的地圖圖片。這種圖文並茂的輸出將大幅提升沉浸感。

*串接方式：* 在 **LangGraph** 對話引擎中，可以新增如`get_weather(location)`的工具節點：由 AI 判斷使用者提問意圖後調用。該工具內部會調用天氣 API 獲取 JSON，解析出關鍵天氣資訊，再調用地圖 API 獲取該地區圖片 URL。後端通過 WebSocket 將文字說明和圖片網址一併傳給前端。前端收到訊息後，可將文字氣象播報和圖片放入動態卡片中展示；若有多張圖片（例如天氣趨勢圖），甚至可做成自動輪播的幻燈片展示。整個過程中，Gemini 模型產生對話內容時可以參考實時取得的天氣數據，確保描述的真實性和即時性。

## 星象模擬與占星數據服務

引入天文星象和占星相關的資料，能讓虛擬網紅適時解讀「宇宙意義」，帶來新穎的互動體驗。例如：

- **美國海軍天文台 (USNO) 月相 API** – 提供月亮盈虧資訊的開放介面。專案中已集成此工具：透過請求USNO的天文資料 API，可取得某日期起的數個主要月相及其發生時間，回傳為 JSON 格式（例如列出接下來幾次的新月、滿月時間）。AI 可據此告知使用者當晚是否滿月，或月相變化對應的傳統意涵。
    
    [github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=,Applications%20API)
    
    [aa.usno.navy.mil](https://aa.usno.navy.mil/data/api#:~:text=This%20data%20service%20generates%20a,the%20list%20and%20the%20number)
    
- **占星資料服務 (AstrologyAPI)** – 這類服務提供星座運勢、行星位置與解讀等占星資訊。例如 AstrologyAPI 平台可產生個人星盤、每日星座運勢和行星運行解釋等豐富內容。使用這類 API，AI 能在對話中給出帶有神秘色彩的“宇宙指引”，如透過當日行星排列給使用者一些鼓勵或建議。
    
    [astrologyapi.com](https://astrologyapi.com/#:~:text=AstrologyAPI%20is%20Astrology,for%20your%20app%20and%20website)
    
    [astrologyapi.com](https://astrologyapi.com/#:~:text=AstrologyAPI%20is%20Astrology,for%20your%20app%20and%20website)
    

*資料格式與多模態適配：* 天文數據多以結構化的 JSON 回傳。例如 USNO 月相接口返回各月相名稱和發生UTC時間

[aa.usno.navy.mil](https://aa.usno.navy.mil/data/api#:~:text=of%20phases%20to%20calculate%2C%20or,data%20service%20may%20be%20found)

；占星運勢則可能以JSON或純文字給出解讀。這些資料可轉化為對話中的文字內容，由 Gemini 多模態模型賦予生動的描述。例如，AI 可以說：「今晚是滿月，根據美國天文台資料，月亮將在20:02升起

[aa.usno.navy.mil](https://aa.usno.navy.mil/data/api#:~:text=This%20data%20service%20generates%20a,the%20list%20and%20the%20number)

。滿月象徵團圓與完成，在這浪漫的月光下，不妨......」。如果需要視覺輔助，也可考慮生成簡單星象圖**（圖片）**：例如透過星空模擬 API 獲取當前夜空星圖，作為對話插圖。這些星象圖與解說文字結合，能加強使用者的沉浸感。

*串接方式：* 在 **LangGraph** 中，星象相關工具如`get_moon_phase(date)`已實現

[github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=,Applications%20API)

。未來可擴充

```
get_horoscope(sign)
```

等接口：AI 偵測到使用者詢問占星話題時，調用對應工具取得運勢文字或行星資訊，然後將結果整合進回應。由於此類內容偏重文字解讀，AI 可以直接將API返回的要點融入對話。例如占星 API 返回「金星進入雙子座，適合溝通表達」，AI 可轉述給使用者並結合上下文給出建議。若有星象圖片，例如星盤或星空圖，後端會像處理其他圖片一樣，將圖片URL與說明文字一同回傳前端，由前端呈現為帶說明的影像卡片。Gemini 模型本身擅長將生硬的數據轉化為引人入勝的語句，使這些宇宙資訊聽起來富有意義且貼近使用者。

## 語音合成與語者風格模擬 API

為了讓虛擬網紅不僅會「說話」，還要聲音有個人特色，我們需要高品質的文字轉語音（TTS）和可能的音色風格調整工具。

- **Google Cloud Text-to-Speech** – 專案目前已採用 Google 的雲端語音合成服務 (從 `.env` 配置可見)。 該 API 支援超過 30 種語音，涵蓋多種語言和語調。Google 的 WaveNet 技術可生成自然流暢的語音，音頻可選格式如 WAV、MP3 等。開發者可指定說話人聲的語言、性別甚至語速、音調等參數來貼合角色形象。當 AI 生成文本回應後，後端會調用此 TTS 服務將文字轉為語音檔，再透過 WebSocket 將音訊串流或網址發送給前端播放。
    
    [github.com](https://github.com/eggyy1224/space_live_project/tree/main/prototype#:~:text=cd%20prototype%2Fbackend%20pip%20install%20,txt)
    
    [docs.ropensci.org](https://docs.ropensci.org/googleLanguageR/articles/text-to-speech.html#:~:text=Google%20Cloud%20Text,across%20many%20applications%20and%20devices)
    
    [docs.ropensci.org](https://docs.ropensci.org/googleLanguageR/articles/text-to-speech.html#:~:text=The%20API%20returns%20an%20audio,by%20the%20next%20API%20call)
    
- **進階語者風格模擬** – 為增強角色個性，可考慮引入更進階的語音服務。例如微軟 Azure TTS 提供**語氣樣式**選擇（新聞播報、歡快等），Amazon Polly 則有部分語言的情感語調。另有 ElevenLabs 等 AI 配音服務可用少量樣本**克隆**特定聲線，生成與角色形象高度契合的語音。這些服務通常透過 API 上傳語音樣本訓練模型，再使用合成接口輸入文字獲得對應音檔。產出的音頻格式與一般TTS相同（如 WAV/MP3），但音色和說話風格更具辨識度。

*資料格式與多模態適配：* 語音合成的主要輸出是音頻文件（如 MP3）。與 Gemini 2.0 的多模態能力結合時，音頻屬於另一種模態：前端會同步播放 AI 的語音回覆，同步帶來聽覺體驗。由於音頻無法以文字形式內嵌模型提示，實際上是由後端在 LLM 結果基礎上附加的。但我們可以在模型生成時考慮語調，例如模型根據上下文決定回答的情感傾向，後端選擇對應風格的語音來合成，達到聲音和內容的一致。例如，當 AI 心情愉快時，後端選用較輕快的聲線或提高語速；當情緒低落時，選擇較平緩低沉的聲線。如果使用的 TTS 支援 SSML（語音合成標記），可在模型輸出中附帶標記調整語速/語調。總之，多模態生成在這裡體現為**文字 + 聲音**的同步輸出，使虛擬網紅不僅“說對話”，還**以獨特的聲音風格說對話**。

*串接方式：* **LangGraph** 本身將語音合成作為後處理的一部分（非 LLM 主動工具調用，而是每次回傳時都執行的步驟）。後端的 `TTSService` 接收 LLM 最終文本，調用 Google TTS API 獲得音頻位元組或檔案連結。前端的 `AudioService` 則監聽到新對話訊息時，自動播放隨附的音頻流。為強化風格模擬，可增設一層策略：例如在對話狀態中加入情緒標籤，後端據此切換不同預設的聲音配置（透過選擇不同語者ID或不同合成服務）。未來若採用進階語音 API，只需在後端替換或擴展 TTS 模組，LangGraph 對話流程基本無需改動—因為對使用者而言，差別只在音色品質提升，但交互方式不變。

## NASA 與天文圖像資料工具

太空主題的虛擬網紅自然離不開壯麗的宇宙圖像。整合 NASA 等天文圖庫的資料，能讓 AI 隨時調用太空照片，在對話中直觀呈現宇宙景觀。

- **NASA 天文每日一圖 (APOD) API** – NASA 提供了著名的每日一張天文圖片 (Astronomy Picture of the Day) 接口。調用該 API（輸入日期等參數），可獲得當日的太空照片或影片連結，以及配套的說明文字。回應為 JSON，包含圖片URL、拍攝日期、解說等資訊。例如某天的 APOD 可能是一張星雲照片，API 會給出圖片連結及一段描述其天文意義的說明文字。這讓 AI 可以將圖片直接展示給使用者，同時講述其中蘊含的宇宙知識。
    
    [wilsjame.github.io](https://wilsjame.github.io/how-to-nasa/#:~:text=The%20APOD%20call%20returns%20a,received%20data%20however%20we%20want)
    
    [wilsjame.github.io](https://wilsjame.github.io/how-to-nasa/#:~:text=The%20APOD%20call%20returns%20a,received%20data%20however%20we%20want)
    
- **NASA 圖像與影片資料庫 API** – 可搜尋NASA歷年累積的浩瀚媒體資源。開發者以關鍵字查詢，API 將返回相關的圖片或影片條目列表，包括縮略圖連結、標題、說明等元數據。回傳格式同樣是 JSON。比如，以關鍵字“月球”查詢可得到數十張與月球相關的官方照片。再如 **SpaceX** 或其他太空新聞事件關鍵字，也能透過此API獲取對應照片。利用這項工具，虛擬網紅在談到特定天文主題時，能即時拿出 NASA 影像佐證，增強內容的權威性與視覺吸引力。
    
    [wilsjame.github.io](https://wilsjame.github.io/how-to-nasa/#:~:text=,NASA%20Image%20and%20Video%20Library)
    

*資料格式與多模態適配：* 這類圖像庫 API 基本以**JSON + 圖片URL**形式提供資料。例如 APOD 接口直接給出圖片網址和文字説明

[wilsjame.github.io](https://wilsjame.github.io/how-to-nasa/#:~:text=The%20APOD%20call%20returns%20a,received%20data%20however%20we%20want)

；NASA Image庫查詢則返回多筆結果的JSON清單，其中每筆含圖像文件的鏈接。由於 Gemini 2.0 Flash 能夠在輸出中結合圖像，此類資料源非常適合多模態呈現。AI 可以描述圖片內容或背後故事，前端同時展示實際照片。例如：「這是哈勃望遠鏡拍攝的螺旋星系影像

[wilsjame.github.io](https://wilsjame.github.io/how-to-nasa/#:~:text=The%20APOD%20call%20returns%20a,received%20data%20however%20we%20want)

，【...】」，用戶將看到星系的真實照片而不只是聽AI描述。若一次性取得多張相關圖片（如搜尋結果有多張行星照片），前端可將它們排成可滑動的相簿，由使用者手動瀏覽或自動輪播展示，增強沉浸感。

*串接方式：* 在 **LangGraph** 中，可實現如`get_space_image(query)`或`get_apod(date)`的工具節點。AI 判斷用戶提到天文現象或主動分享太空見聞時，調用這些工具：例如每日固定時間調用`get_apod`取得當日圖片，隨後 AI 自行在對話中說出「我剛從NASA收到一張最新的太空照片…」。工具執行時透過 NASA API 拿到JSON結果，解析出圖片URL清單和說明文字。接著**格式化輸出**：後端將圖片連結嵌入到回复消息中，並附上AI整理過的說明文字。一旦前端收到帶有圖片URL的消息物件，會自動加載圖片並顯示在聊天介面中。若消息包含多個圖片URL，前端則生成滑動畫廊或自動播放的幻燈片，依序展示這些圖片（例如AI一次分享了幾張火星照片）。整體而言，透過這些圖像工具，虛擬網紅的對話將打破純文字限制，真正做到把**宇宙的畫面呈現在用戶眼前**。

## 目前已整合的工具與功能現狀

根據最新的 GitHub commit 記錄，專案已經初步整合了數項外部工具資源：

- **維基百科搜尋** – 已實現`search_wikipedia`工具，用於查詢維基百科條目摘要。它透過 Python 的 `wikipedia` 函式庫調用維基百科（設定為繁體中文）來取得結果。如果使用者問到百科知識類問題，AI 能調用此工具獲取相關條目的概要信息，豐富對話內容。
    
    [github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=)
    
    [github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=match%20at%20L680%20,%EF%BC%9A%E4%BD%BF%E7%94%A8%20Python%20%E7%9A%84%20%60wikipedia%60%20%E5%BA%AB%E3%80%82)
    
- **太空新聞資訊** – 已整合 **Spaceflight News API** 作為`search_space_news`工具。這是一個專門提供太空領域新聞的 API（第4版），後端會請求最新的太空新聞資料，支持按日期範圍過濾。目前實作中該工具預設抓取最近幾則新聞標題和摘要，然後由 AI 組合成對話推送給使用者。例如用戶若問「最近太空有什麼新鮮事？」AI 可返回最新的火箭發射或天文發現消息清單。
    
    [github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=,v4)
    
    [github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=match%20at%20L555%20,%E5%8F%83%E6%95%B8%E3%80%82)
    
- **月相查詢** – 已接入 USNO 月相 API（`get_moon_phase`）。AI 可利用此工具查詢當前或指定日期的月亮相位，如新月、滿月時間等，並在對話中告知使用者。這為虛擬網紅增添了一種根據天文週期主動分享資訊的能力。
    
    [github.com](https://github.com/eggyy1224/space_live_project/commit/5a34857645e5ef66127137c07f3b192feebc5ad1#:~:text=,Applications%20API)
    

以上功能在後端**DialogueGraph**流程中已打通：透過「工具意圖檢測 → 參數解析 → API 調用 → 結果格式化 → 回傳整合」的節點序列，AI 能夠動態擴充其知識和資訊來源。從近期 commit 看，`detect_tool_intent` 等模組均已加入對話狀態圖，當偵測到使用者詢問需要外部資訊時，會走工具分支來獲取答案

[github.com](https://github.com/eggyy1224/space_live_project/commit/d09525dbfa88c0094ec31a241610ba09d5e90594#:~:text=)

[github.com](https://github.com/eggyy1224/space_live_project/commit/d09525dbfa88c0094ec31a241610ba09d5e90594#:~:text=)

。

**已具備能力：** 一般知識查詢、即時太空新聞、基礎天文資訊（如月相）這三方面的對應工具已經具備，並在對話中可用。專案前端也已實現對後端返回內容的即時呈現（包括3D模型表情、文字對話和語音播放）。例如，後端返回的文字消息會通過 WebSocket 推送到前端聊天框，若有對應的語音檔也會一起播放。前端的模型表情還會根據對話情緒即時變化，整體框架已能支撐較豐富的互動。

**尚待擴充：** 目前列出的其他工具類型，如**天氣地圖、深入占星解讀、多媒體天文圖像**等，尚未在現有 commit 中看到實裝跡象，屬於下一步計畫。語音方面，當前應用了 Google TTS 基礎能力，但**語者風格**尚未深度定制，未來可透過引入更多語音接口或參數調整來強化。此外，隨著工具增加，對話引擎的**工具管理**需持續優化，例如擴充`parse_tool_parameters`對更多參數類型的支援，以及`format_tool_result`針對圖片/音訊等特殊內容的處理。後端在回傳消息時，可能也需制定**統一的資料格式**來包含文字、圖像URL、音頻等多模態元素，以便前端可靠解析。根據需求，前端的展示邏輯也要相應加強：例如偵測到多張圖片時，自動切換到畫廊模式；收到長文本時支援滾動顯示等。

值得強調的是，**後端訊息的圖文結構**對前端體驗至關重要。未來在整合更多多模態工具時，後端可以規範每則對話消息為一個 JSON 對象，其中包含`text`字段（AI回答的文字）和可選的`images`列表（一到數個圖片URL），甚至`audio`字段（語音檔案連結或ID）。前端收到消息後，檢查到有多張`images`，就以**輪播圖**形式展示；只有一張圖片則作為插圖貼在文字旁。音頻則由 AudioService 自動播放。目前架構已經透過 WebSocket 實現即時推送，擴充這種結構只需在前後端協議上達成一致。以展示 NASA 圖片為例：後端從API獲得3張圖片，則打包成 `images: [url1, url2, url3]` 隨回答文字一起發出，前端聊天室會生成一個帶有三張可滑動圖片的卡片。用戶可以左右滑動查看，或讓其自動輪播，與此同時，AI的講解文字會固定在旁邊或下方。透過這種方式，**“星際小可愛”**將真正實現動態的圖、文、聲並茂互動，讓使用者彷彿身臨其境與太空站裡的 AI 網紅交流

[developers.google.com](https://developers.google.com/maps/documentation/maps-static/start#:~:text=The%20Maps%20Static%20API%20returns,your%20markers%20using%20alphanumeric%20characters)

[wilsjame.github.io](https://wilsjame.github.io/how-to-nasa/#:~:text=The%20APOD%20call%20returns%20a,received%20data%20however%20we%20want)

。

**總結**：整合上述各類 API 工具後，虛擬太空網紅將具備從天地氣象、星辰運勢、語音表達到宇宙影像講解的全方位互動能力。這些工具以結構化的資料（JSON、影像、音訊等）為 AI 提供了“感知”外部世界的管道，再結合 Gemini 2.0 Flash 模型強大的多模態生成和理解能力，最終經由 LangGraph 的流程編排將資訊無縫融入對話。在前後端通力配合下，用戶體驗到的將是一個有知識、有個性，能隨時分享**即時資訊與視覺內容**的太空站 AI 夥伴。各模組的持續完善和新工具的加入，會讓這個系統不斷進化，朝專案願景中所描繪的栩栩如生的虛擬網紅邁進。

[openweathermap.org](https://openweathermap.org/current#:~:text=Access%20current%20weather%20data%20for,JSON%2C%20XML%2C%20or%20HTML%20format)
