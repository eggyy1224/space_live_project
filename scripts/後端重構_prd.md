了解，我會為你撰寫一份完整的後端重構計畫 PRD（產品需求文件），包含近期與長期規劃，並針對目前 `space_live_project` 專案的實作與問題做分析整理。

這份文件將採用 Markdown 格式，適合放入 GitHub 儲存庫（如 claude-task-master），內容將涵蓋：重構背景與目標、模組優化建議、效能與穩定性提升計畫、技術選型考量、優先順序與 Milestone 等，方便後續追蹤與實作。

我會馬上整理成檔案並回傳給你。

# 後端重構計畫 PRD

## 1. 背景與重構動機

目前「星際小可愛」後端存在多處技術債，導致維護和擴充困難。首先，**murmur（自言自語）模組**的邏輯高度複雜且深度嵌套，目前實作上緊密耦合在 WebSocket 事件循環中，須依賴許多外部狀態變數 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=match%20at%20L598%20nonlocal%20speaking_state%2C,last_murmur_timestamp%2C%20recent_murmurs%2C%20current_emotion))。這使得要調整或關閉 murmur 功能變得困難。其次，**工具使用功能**與對話流程耦合度過高：現在若要停用某些工具，需要改動核心代碼路徑（例如強制設定 `has_tool_intent` 為 False、清空 `available_tools` 列表等 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=3.%20%E5%9C%A8%20,%E3%80%82))），缺乏簡單的開關或介面來管理工具，顯示出模組邊界不清。最後，**資料夾結構**雖已有初步劃分（如 `services/ai` 下含 `dialogue_graph.py`、`memory_system.py` 等），但**模組化程度不足**：關鍵邏輯分散在單一大型模組中，各部分職責未明確分離（如 WebSocket 模組同時處理對話流程、記憶檢索、工具執行等）。以上痛點導致代碼難以測試和擴展，也可能影響執行效能與穩定性。因此，我們有必要進行後端重構，以解決耦合與結構問題，提升系統的可維護性、性能和穩定性。

## 2. 重構目標

本次重構將分為近期與長期兩類目標，明確我們期望達成的成果：

- **近期目標**：（代碼結構與可維護性）
  - **模組獨立與開關控制**：將目前深度耦合的 murmur 自言自語邏輯拆分為獨立模組，例如建立一個專責的 `MurmurService`。此模組應支援**上下文記憶開關**，允許在產生 murmur 時選擇是否考慮之前累積的 murmur 內容（目前實作會將最近幾句 murmur 納入上下文 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=%E5%BE%9E%E6%9C%80%E8%BF%91%E7%9A%84%20murmur%20%E4%B8%AD%E6%A7%8B%E5%BB%BA%E6%80%9D%E8%80%83%E7%B7%9A%E7%B4%A2))）。透過引入開關，可靈活控制 murmur 是否連貫思考上下文，方便針對不同情境開啟或關閉記憶延續功能。
  - **降低耦合度，明確介面邊界**：重構後端各功能模組，使它們透過清晰的介面交互。特別是工具使用、記憶檢索等功能，應能獨立於對話主流程之外進行演算，主流程僅調用其介面。這樣可以讓我們在不影響核心對話邏輯的前提下替換或修改工具/記憶相關實現。
  - **重構 WebSocket 對話處理**：整理 WebSocket 連接處理流程，將對話狀態管理、事件處理等邏輯從單一函數中分離，改由專門的類別或協程管理，消除大量非本地變數與閉包依賴，使代碼結構更清晰可讀。

- **長期目標**：（性能與擴展性）
  - **記憶檢索效能提升**：優化記憶系統，使每次對話記憶查詢的平均耗時低於 **500ms**。為達成此目標，我們將採取多種措施（詳見後續優化方案），確保無論對話歷史多長，相關記憶的提取都能在半秒內完成，提供即時的回應體驗。
  - **系統穩定性與可伸縮性**：重構後端架構以支撐長期發展。代碼需易於擴充新功能（例如加入新的工具或記憶類型）且對未來可能的分散式部署友好。我們期望經過重構，後端服務能在高併發用戶下保持穩定，並能方便地透過水平擴展或快取等手段進一步提升吞吐量。
  - **可維護性與測試**：重構完成後，各模組將具有清晰的介面和職責範圍，開發者可以更輕鬆地為關鍵邏輯撰寫單元測試。長期而言，這有助於在引入新功能時降低回歸風險，並加速開發迭代。

上述目標將指引我們的重構工作，確保在優先解決當前痛點的同時，為未來的功能成長和性能提升打下良好基礎。

## 3. 模組重構建議

針對後端目前幾個較為複雜或高度耦合的模組，提出如下重構建議，以實現模組化、介面抽象，以及抽取重複邏輯：

- **WebSocket 模組 (`websocket.py`)**：將 WebSocket 處理流程內部的大型函式拆解為多個協作單元。建議引入一個專門的對話會話管理類別（如 `ConversationSession`），負責跟蹤會話狀態（如當前對話階段、speaking_state 等）及處理事件。WebSocket endpoint 的主要職責將簡化為：接收前端消息 -> 調用對話管理服務處理 -> 將結果發送回前端。這樣可以去除 WebSocket 模組內部對各種全域或外部變數的非本地引用 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=match%20at%20L598%20nonlocal%20speaking_state%2C,last_murmur_timestamp%2C%20recent_murmurs%2C%20current_emotion))，改以明確的對象屬性維護狀態。同時，將 murmur 觸發、工具檢測等邏輯移出，由相應服務模組提供接口給 WebSocket 調用。此重構將提高 WebSocket 處理的清晰度，降低單個模組的負擔。

- **對話流程圖模組 (`dialogue_graph.py`)**：目前的 `dialogue_graph.py` 負責構建AI對話狀態機或工作流，其中包含對記憶檢索、工具使用、回應生成等節點的串接邏輯。建議對此進行**介面抽象**與拆分：
  - **狀態圖構建與定義拆分**：將對話狀態圖的**定義**（各節點的行為、轉移條件）與**構建執行**解耦。可在 `graph_nodes/` 資料夾中定義各種節點類型（如 ToolIntentDetectionNode、MemoryFetchNode 等），以及它們的組裝配置；`dialogue_graph.py` 則專注於根據配置構建圖並執行。這樣能更直觀地添加/移除節點類型，而不用深入修改主要邏輯。
  - **工具與正常對話路徑分離**：狀態圖中目前將「有無工具意圖」作為路徑分支 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=lambda%20state%3A%20,normal_path))。建議透過策略模式或明確的子工作流來處理工具邏輯。例如，把工具相關的一系列節點（檢測意圖→解析參數→執行工具→格式化結果→整合結果）獨立為一個子圖或模組，使主對話圖在需要時調用該工具子流程的接口。如此一來，對話主流程和工具處理流程各自清晰，未來新增其他類型工具或改變順序時，影響範圍更可控。
  - **重用通用邏輯**：抽取對話圖中重複出現的邏輯片段，例如判斷使用哪條路徑、合併記憶結果等，封裝成輔助函數或方法，避免不同節點各自實現相似功能。這將減少程式碼重複並降低出錯機率。

- **記憶檢索模組 (`memory_retriever.py`)**：記憶檢索相關代碼目前橫跨 query 構建、記憶庫查詢、結果格式化等多個步驟，建議進一步模組化：
  - **Query 構建與結果格式化**：維持目前的 `query_builder` 和 `formatter` 子模組，但確保所有記憶類型（對話記憶、角色記憶等）的 query 構建與格式化都有對應的方法，並避免不同記憶類型的處理邏輯交叉混雜。可考慮為每種記憶源制定介面協定（如每個記憶源實現 `retrieve(query, k) -> results` 及 `format(results) -> text`），`memory_retriever.py` 則調用這些介面來取得並整理結果。
  - **異步與快取**：目前記憶檢索已引入 `asyncio.gather` 進行並行查詢 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))。重構時可更明確地將**並行檢索**封裝在 MemoryRetriever 類中，例如方法 `retrieve_all()` 內部實現對多個記憶庫的並行查詢及超時控制。另建議在此層引入**結果快取**機制：對於重複的查詢（尤其是短時間內相同的使用者提問），可先檢查快取以避免頻繁查詢向量資料庫。可以使用 Redis 作為快取儲存層來暫存最近的記憶檢索結果，顯著降低熱點查詢的延遲。
  - **錯誤隔離與回退**：為增強穩定性，MemoryRetriever 在查詢任一記憶源失敗時不應影響整體流程。可在模組內部對各記憶源查詢包裹 try/except，一旦某個記憶庫超時或報錯，記錄警告日誌並提供空結果，使對話流程能**優雅降級**繼續運作（例如僅依靠其他記憶源或乾脆無記憶回答，而非整體失敗）。

- **工具使用邏輯**：目前工具相關的檢測與執行散落於對話圖與工具函式中，耦合緊密。建議**重構為獨立的工具執行模組**（如 `ToolExecutor` 或 `tool_service`）：
  - **工具意圖檢測**：由獨立組件負責分析使用者輸入是否需要使用工具（例如透過關鍵字或LLM判斷），對話主流程僅調用 `ToolExecutor.has_tool_intent(text)` 獲取布林值，而不關心內部實現。這樣可以隨時更換或優化意圖判斷邏輯（例如引入更複雜的NLU模型）而不用改變主程式。
  - **工具執行與結果整合**：將執行具體工具的細節從對話流程中抽離。對於每一種工具，在 `ToolExecutor` 中定義對應的執行方法，例如 `execute_web_search(query)`、`execute_space_action(params)` 等，內部封裝API調用或業務邏輯。對話主流程只需呼叫統一的 `ToolExecutor.execute(tool_name, params)`，並獲取標準化的結果物件。執行完工具後的結果格式化與合併也在 ToolExecutor 層處理，最終將結果文本返回給對話流程。
  - **工具清單與配置**：提供集中管理可用工具的配置，例如透過 `available_tools` 列表或配置檔，讓新工具的加入僅需在一處註冊。未來若需暫時停用某工具，也可通過配置開關實現，而非深入代碼修改判斷邏輯。總之，確保工具處理的開關和擴展都**對開發者透明**且低風險。

- **Murmur 自言自語邏輯**：將 murmur 從目前對話流程中獨立出來成為可重用的服務模組。例如實作 `MurmurService` 類別，管理自言自語的計時觸發和內容生成。`MurmurService` 應有明確的接口，如 `maybe_trigger_murmur(current_state)` 方法根據閒置時間等條件決定是否產生 murmur，以及 `generate_murmur(context)` 方法負責與 AI 模型交互生成內容。透過這種封裝，我們可以在需要 murmur 時調用服務，無需在 WebSocket 主流程中埋入複雜判斷。同時，該服務內部將提供**上下文開關**支持：例如可配置是否傳入歷史 murmur 作為 prompt 的一部分。當開關關閉時，`MurmurService` 僅基於預設人格或隨機想法產生自言自語；當開啟時則會考慮之前的 murmur 內容以保持話題連貫。這樣的模組化設計讓 murmur 功能的調整影響範圍局限於 `MurmurService` 內，不會波及對話主流程其他部分。

透過上述對各模組的重構建議，我們期望將目前糾結在一起的功能分離開來，建立清晰的層次與介面關係。最終的結果是每個模組各司其職，彼此通過明確契約互動，方便開發者在日後獨立地調試和優化某一部分而不影響全局。

## 4. 資料夾與代碼結構優化

為了支援上述模組重構，我們將調整 `prototype/backend` 的資料夾結構，讓目錄層級直接反映後端主要功能模組。重構後建議的目錄結構如下：

```
prototype/backend/
├── api/                      # FastAPI 路由與接口定義（保持不變）
│   ├── endpoints/            # 各 API endpoint，包含 websocket、health 等
│   └── ... 
├── core/                     # 核心配置與資料模型（保持不變）
├── services/                 # 後端主要服務邏輯
│   ├── murmur_service/       # Murmur 自言自語服務模組
│   │   ├── __init__.py
│   │   ├── murmur_service.py # MurmurService 類別實作，處理自言自語生成
│   │   └── config.py         # Murmur相關配置（如觸發閾值、開關）
│   ├── memory_system/        # 記憶系統模組
│   │   ├── __init__.py
│   │   ├── retriever.py      # MemoryRetriever 類別實作，調度各記憶源檢索
│   │   ├── query_builder.py  # Query 構建子模組
│   │   ├── formatter.py      # 檢索結果格式化子模組
│   │   ├── stores/           # 記憶庫接口實作（如向量資料庫、角色資訊庫）
│   │   └── processing/       # 記憶預處理/後處理（如摘要生成等）
│   ├── tool_executor/        # 工具執行模組
│   │   ├── __init__.py
│   │   ├── tool_service.py   # ToolExecutor 類別，封裝工具意圖檢測與執行
│   │   └── tools/            # 各具體工具實作或適配器 (web_search.py, etc.)
│   ├── dialogue_manager/     # 對話管理模組
│   │   ├── __init__.py
│   │   ├── dialogue_graph.py # 對話狀態圖構建與管理（可進一步拆分）
│   │   └── graph_nodes/      # 對話圖節點定義
│   └── ai_service/           # AI模型調用與回應生成模組
│       ├── __init__.py
│       ├── generator.py      # 負責與LLM交互生成對話或murmur內容
│       └── prompts.py        # 提示詞模板管理
└── utils/                    # 通用工具函式（保持不變或視需要拆分）
```

> **說明**：上述結構重點在於將原本雜糅在一起的功能區分開來。例如 `murmur_service` 獨立出來後，專注處理自言自語的計時與內容生成；`memory_system` 下細分 retriever、stores、processing 等，清晰劃分記憶檢索各步驟；`tool_executor` 下統一管理所有外部工具的調用邏輯；`dialogue_manager` 用於組織對話流程（透過圖或其他形式）；`ai_service` 專門與外部AI模型（如 OpenAI API）交互。這種分層使得每個子資料夾對應單一關注點，開發人員在定位代碼時可以直接根據功能找到相應模組，未來新增功能（例如新工具、新記憶類型）也可以通過新增子模組實現而不影響其他部分。

在實施此結構調整時，我們也將同步更新引用路徑與初始化代碼（如確保新的子模組都在 `services/__init__.py` 或對應位置正確載入）。短期內，可以在保持舊功能行為不變的前提下進行目錄調整與類別拆分，重構後的代碼庫將更具模組化，可讀性與可維護性都大大提高。

## 5. 效能與穩定性優化規劃

重構不僅針對代碼結構，也旨在解決當前後端服務的效能瓶頸並提升穩定性。以下列出幾項目前的瓶頸問題及對應的優化方案：

- **記憶檢索耗時**：隨著對話記錄增多，從向量資料庫檢索相關記憶的延遲可能顯著增加，影響整體回應速度。為改善這一點：
  - **限制檢索範圍**：為每次查詢設定最大檢索條數 `k`，避免不加限制地搜索過多記憶。 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))已體現此優化思路——透過限制 `k` 值，確保無論記憶庫多大，都只取相關性最高的少量結果。
  - **結果快取**：引入快取機制（例如使用 Redis）存儲近期的檢索結果。對於短時間內重複的相似查詢，可直接返回快取結果而無需再次執行向量比對。這對頻繁出現的對話話題能大幅節省時間。
  - **異步並行**：保持並完善目前的並行檢索策略，即同時向多個記憶源發出查詢並等待所有結果 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))。進一步的優化是在合理情況下允許記憶查詢與AI文字生成並行進行（例如先行請求記憶，同步請求AI生成答覆，在兩者完成後合併），以最大化地利用等待時間。但需注意控制併發量與順序，確保在使用記憶結果拼接 prompt 時不出現競態問題。

- **首次響應延遲**：如果使用者的第一句話即觸發了完整的記憶檢索與AI生成，可能出現較長的等待。為提升體驗：
  - **跳過無效記憶檢索**：對明顯不需要檢索記憶的輸入（例如使用者只是簡單問好「hello」），直接略過繁重的記憶查詢步驟 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=%E5%84%AA%E5%8C%96%EF%BC%9A%E6%AA%A2%E6%9F%A5%E8%BC%B8%E5%85%A5%E9%A1%9E%E5%9E%8B%EF%BC%8C%E5%B0%8D%E7%B0%A1%E5%96%AE%E5%95%8F%E5%80%99%E8%B7%B3%E9%81%8E%E8%A8%98%E6%86%B6%E6%AA%A2%E7%B4%A2))。實作上可在對話開始時檢測問候語或寒暄，一旦匹配，僅提供預設的回應或簡單回答，而不進行向量搜索和知識整合。
  - **預先加載/預熱**：在系統啟動或空閒時，預先將AI模型上下文、人設記憶等加載到內存，或進行一次空查詢以喚醒後端服務。這樣可避免首次請求時的冷啟動開銷。如有可能，也可讓記憶系統在啟動時就將角色 persona 信息查詢並快取好，確保第一個 user query 來時直接可用。

- **外部API穩定性**：本專案嚴重依賴外部API（如 OpenAI 接口）來生成對話和自言自語。一旦這些服務延遲增加或發生錯誤，可能導致我們的回應超時或失敗。為此：
  - **API調用回退策略**：實現對AI生成接口的容錯機制。例如設定一個合理的請求超時，若超過閾值未得到回應，立即採取回退方案（如改用備用的API金鑰/服務器、或改用本地較小模型產生一個簡單回覆）。確保用戶在最差情況下也能獲得及時的回應，而不會一直掛起等待。
  - **重試與排除**：對於偶發的API錯誤，可嘗試快速重試一次；如連續失敗，則記錄錯誤並暫時停止調用該功能路徑，同時通知開發者介入調查。藉助指標監控（見下節），我們也能及早發現外部依賴的異常情況。

- **系統資源利用**：在多用戶併發時，後端需要高效使用 CPU、IO 等資源，否則可能出現性能瓶頸或阻塞。
  - **非同步IO與任務併發**：確保所有與外部交互（如資料庫、API請求、文件IO）的操作都使用非同步IO，避免因單一 slow I/O 阻塞整個事件loop。如果某些計算較重（如大型文本摘要），可考慮使用背景執行（例如透過任務佇列）以避免佔用主請求流程的時間。
  - **資源隔離**：對於每個 WebSocket 會話，可設定資源配額或採取限流措施，防止單一用戶請求過於頻繁導致系統壓力過大。例如限制每個連線每分鐘觸發 murmur 的次數，或對連續大量工具請求的行為進行節制，從而保護整體服務品質。

- **錯誤監控與自我修復**：提高後端對異常情況的監控和容錯：
  - **記錄與警報**：加強日誌記錄，對於各種超時、失敗、未預期狀況記錄詳細訊息。同時配置監控告警，當某類錯誤在單位時間內連續出現多次時，觸發告警通知管理員。
  - **自我重啟**：針對可能的資源泄漏或狀態異常（例如某 websocket 會話長期佔用資源未釋放），可以定期執行健康檢查，發現問題時自動重啟相關子模組或整個服務（配合容器編排的重啟策略）。此外，引入健康檢查端點（如已有 `health.py`）供上層監控系統定期調用，一旦無回應即可重啟實例，確保服務長時間運行的穩定性。

通過以上優化措施，我們預期後端在重構後能達到**更快的響應**和**更強的穩定性**。特別是記憶檢索部分，結合範圍限制、快取和異步並行， ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=%E5%84%AA%E5%8C%96%EF%BC%9A%E6%AA%A2%E6%9F%A5%E8%BC%B8%E5%85%A5%E9%A1%9E%E5%9E%8B%EF%BC%8C%E5%B0%8D%E7%B0%A1%E5%96%AE%E5%95%8F%E5%80%99%E8%B7%B3%E9%81%8E%E8%A8%98%E6%86%B6%E6%AA%A2%E7%B4%A2)) ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))等改進已在近期 commit 中有所體現，未來配合基礎建設（如 Redis 快取）可進一步將延遲控制在500ms以內。同時，多層次的容錯和監控機制將使服務在面對不可預期情況時更具韌性，提供持續穩定的用戶體驗。

## 6. 技術選型與基礎建設建議

在重構過程中，除了代碼本身，也需要引入適當的技術工具與基礎建設來支援性能優化和監控。以下是幾項具體建議：

- **背景任務處理**：對於無法在請求周期內完成的繁重任務（例如長對話記憶的離線總結、批量資料庫維護等），建議引入 **Celery** 這類的任務佇列框架。Celery 結合 Redis 或 RabbitMQ 作為broker，可以將耗時操作丟到背景執行，執行完再通知主應用。舉例而言，可將定期的記憶庫清理/壓縮、或需要與LLM進行長文本總結的任務交由 Celery worker 執行，主程式不被阻塞。這種架構提升了後端的**非同步處理能力**，確保即使面對高延遲操作也能保持對其他請求的即時響應。

- **快取和資料庫**：建議使用 **Redis** 作為快取層以及短期資料存儲。Redis 可用於：
  - **會話狀態快取**：暫存每個用戶最近對話的關鍵上下文（如最近一輪對話或 murmur），快速供後端檢索，減少每次都從零開始重建上下文的開銷。
  - **記憶檢索結果快取**：如前節所述，快取最近的向量查詢結果或LLM回應，避免短時間內重複計算。
  - **任務佇列 Broker**：如採用 Celery，Redis 可同時作為其 broker 和 result backend，統一技術棧。
  Redis 作為成熟的記憶體型資料庫，讀寫性能極高，適合作上述即時性要求的場景。但需注意資料過期策略，確保快取不至於無限制成長影響記憶體。

- **APM 與監控**：為了在重構後持續追蹤性能瓶頸與錯誤，建議整合 **OpenTelemetry** 進行分佈式追蹤和應用性能監控（APM）。透過 OpenTelemetry，我們可以對每個請求的關鍵步驟（例如記憶檢索、AI生成、資料庫查詢）埋點追蹤，收集延遲數據。在本地或者雲端部署一套 APM 解決方案（如 Jaeger, Zipkin 或 SigNoz 等），即可視覺化這些追蹤資料，找出耗時最長的環節。另外也建議引入 **Prometheus/Grafana** 用於監控關鍵指標（如每分鐘請求數、各模組平均執行時間、錯誤率等），或使用雲服務的監控套件。透過儀表板及時了解系統健康狀況，一旦某指標異常（如記憶查詢時間突然升高），可馬上展開調查並調整。最後，在錯誤監控方面，可以使用 **Sentry** 之類的日誌集中與錯誤追蹤工具，及時發現未處理的例外和 stack trace，提升問題發現與修復效率。

- **資料庫與向量庫選型**：目前記憶系統可能使用現有的向量資料庫或內建方案。長期來看，如對話記憶量級持續增長，需評估專門的向量資料庫服務（如 Pinecone、Weaviate）或自架 Elasticsearch/OpenSearch 向量插件，以確保檢索性能和可擴展性。如果現有方案性能足夠，可以暫時通過快取與優化參數應對；但若未來需要支持**語意搜尋**更多內容，選用專門的向量相似度搜尋服務會更穩健。在關係型資料方面，如角色資訊、用戶資料等，可繼續使用 PostgreSQL/MySQL 等，並透過適當的 ORM 層簡化操作。

- **配置管理與環境區分**：重構後引入更多組件（Redis、任務隊列等），需完善配置管理。建議使用 **dotenv** 或類似方案管理不同環境（本地開發、staging、production）的環境變數，將敏感資訊（API Key 等）與配置統一從程式碼中分離。在 repo 中提供 `.env.example` 模版（目前已有 ([space_live_project/prototype/backend at main · eggyy1224/space_live_project · GitHub](https://github.com/eggyy1224/space_live_project/tree/main/prototype/backend#:~:text=))），並在文件中說明新增的環境變數用途（如 Redis 連接位址、OpenTelemetry 收集端點等），方便部署時調整。

綜上，適當的技術選型與基礎設施將為後端重構保駕護航。Celery+Redis 提供了**異步處理**與**快取能力**，OpenTelemetry 等監控框架確保我們能**量化**重構帶來的性能改善並及時發現問題。這些技術都是業界驗證的成熟方案，融入後端架構後，將顯著提升系統的穩定快速表現和可維護性。

## 7. 開發節奏與優先順序

為了有效推進重構並降低風險，開發計畫將按照里程碑（Milestone）分階段進行。各階段明確範圍和優先事項，以確保逐步交付可用的改進成果：

1. **Milestone 1（近期重構：重點解耦與模組分離）** – *目標在於快速解決最明顯的架構問題，提高代碼可讀性和穩定性*。預計用時：2~3 週  
   **主要任務**：  
   - **Murmur 模組化**：建立 `MurmurService`，將 `websocket.py` 中自言自語相關的函數移植至此。確保 murmur 觸發與生成邏輯在新模組中運作良好，並透過設定檔支持開/關。完成後，開發者可以一鍵停用 murmur（例如在 `.env` 中設定 `ENABLE_MURMUR=false`），驗證自言自語對話不再出現。  
   - **工具耦合解耦**：重構對話流程中的工具調用。實作 `ToolExecutor` 類，將 `dialogue_graph.py` 中有關工具意圖判斷與執行的程式碼遷移至 `tool_executor/`。修改對話狀態圖使其呼叫新接口（例如 `ToolExecutor.detect_intent()`），確保對話主流程在工具執行成功/失敗兩種情況下均能得到合理的結果。此階段完成後，停用工具將只需更改配置或參數，而非修改核心代碼。  
   - **記憶檢索優化（基礎）**：在不改變對外行為的前提下，優化 `memory_retriever.py` 內部：加入簡單的結果快取（可先以本地全域變數字典模擬），以及設定檢索上限 `k`。同時，將近期 commit 中的改動（並行檢索、問候語跳過等）穩定整合進新代碼基底，確認記憶查詢平均耗時有所下降（可撰寫簡單基準測試比較開關前後的查詢延遲）。  
   - **資料夾調整**：按照第4節規劃初步調整目錄結構。創建對應的子資料夾和檔案，將原有代碼片段移動過去。確保引用路徑更新正確，單元測試（如有）可通過。此階段目標不是最終定稿的結構，但要奠定基本框架，使之更接近理想模組劃分。  

   **驗收標準**：所有單元測試與基本功能測試通過（對話、murmur、工具使用等功能運作正常）。代碼結構清晰度明顯提升 —— 開發者打開 `services/` 子目錄能直觀理解各模組職責。murmur 開關和工具開關能通過配置輕鬆控制。記憶檢索的效能相較重構前有可測量的改善（例如平均延遲降低了30%以上）。

2. **Milestone 2（中期重構：性能提升與架構優化）** – *在模組分離完成後，專注深入的性能優化和架構鞏固*。預計用時：3~4 週  
   **主要任務**：  
   - **引入 Redis 快取與 Celery**：將 Milestone 1 中設計的快取機制切換為 Redis 實現，確保多進程部署時快取一致。搭建 Celery 任務佇列範例，挑選一兩個適合作為背景執行的功能進行改造（例如定時清理過期記憶項、異步執行較長的工具操作）。撰寫相關說明文件，指導團隊如何啟動 Celery worker 及配置 Redis。  
   - **OpenTelemetry APM 整合**：在關鍵路徑加入 OpenTelemetry trace。如 WebSocket 接收->回應 全流程、記憶檢索子流程、工具執行子流程等。部署本地監控服務（Jaeger等）驗證追蹤資料是否正確送出。這將為後續持續優化提供量化依據。  
   - **對話狀態管理重構**：進一步整理 `dialogue_graph` 或對話管理相關代碼。考慮引入狀態機庫或者簡化當前 workflow 的實作方式。例如，如果目前的對話節點以硬編碼方式連結，嘗試將其資料化（data-driven）配置，使後續調整對話流程不需大改程式。確保重構後對話輪廓依舊符合預期，包括正常對話、跨話題切換以及帶工具的對話流程都正常。  
   - **增強錯誤處理**：審視各模組對異常的處理策略，補充缺失的錯誤捕獲。例如 MemoryRetriever 在某記憶源失敗時的回退已在Milestone1著手，這裡進一步測試非常規情況並完善日誌。在工具執行方面，模擬第三方API錯誤，確保我們的系統能妥善記錄並回覆預設訊息而不崩潰。  
   - **性能測試與調優**：對重構後的後端進行壓力測試與基準測試。重點關注：單一會話長對話情境下的平均延遲、多會話併發時的資源佔用與響應時間。根據結果調整參數（如快取大小、併發數限制）或發現新的瓶頸並優化。目標是在10並發用戶、每人連續對話10輪的情境下，系統保持穩定，且每輪回應平均在2秒以內完成。

   **驗收標準**：整體後端服務在真實場景下表現出**明顯優於**重構前的性能：記憶檢索耗時達到目標（<500ms) ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))，對話響應速度提升，用戶體驗流暢。OpenTelemetry 可在測試環境成功收集到追蹤資料，顯示各步驟耗時分佈，無嚴重單點瓶頸。系統經過壓力測試無崩潰，錯誤處理完善（未出現未捕獲異常）。Milestone 2 完成後，後端架構已相當穩固，具備支撐實際應用的性能和穩定性。

3. **Milestone 3（長期優化：功能擴展與代碼完善）** – *持續改善和未來展望，根據需要進行的延伸重構*。這部分無嚴格時間線，可並行於正常功能開發逐步進行  
   **可能的任務方向**：  
   - **完善測試與文檔**：為重構後的關鍵模組補齊單元測試和文件說明。尤其是 `murmur_service`、`memory_system`、`tool_executor` 等核心部分，需要詳細的使用說明和設計文檔（可以寫入 `docs/後端相關/`），以方便日後交接和新成員上手。同時，引入自動化測試流程（如GitHub Actions CI）在每次推送時跑測試，防止回歸。  
   - **新功能模組的模版**：基於重構後的經驗，制定添加新工具、新記憶類型、新對話節點的**開發指南**或模版代碼。例如：如何新增一個 “天氣查詢” 工具：需要在 `tool_executor/tools/` 中建檔案，實現特定接口，並在配置中打開即可。這些指南有助於保持未來代碼的一致性。  
   - **監控與調優迭代**：運行一段時間後，根據 OpenTelemetry 及日誌反饋的數據，持續調整。比如如果發現某些工具使用率極低且每次加載代價高，可以改為懶加載或按需載入。又或者觀察到記憶庫查詢命中率下降，可能需要優化向量索引或增加語義壓縮策略。這些屬於持續優化工作，作為長期里程碑將反覆進行。  
   - **架構前瞻**：評估是否需要將某些模組獨立部署（微服務化）以應對更大負載。例如將 `memory_system` 作為獨立服務（因其可能需要占用較多記憶體進行向量搜索），或將 `tool_executor` 部分拆成雲函數。此舉只有在流量或複雜度大幅上升時才考慮。在現階段，一體化架構足以支撐，但我們會為未來的擴展預留可能性，如保持代碼的微服務轉換友好（低耦合、使用接口通信等）。

   **驗收標準**：Milestone 3 並非一個「完成」狀態，而更像持續改進的過程。判斷其成功與否在於：重構後的後端是否達到了易於擴展和演進的狀態——團隊能夠較輕鬆地在其上新增重大功能而不破壞原有結構，並且系統在未來一段時間內保持穩定高效運行。隨著這些長期優化的進行，「星際小可愛」後端將準備好迎接更多使用者和更複雜的互動場景挑戰。

透過以上里程碑分階段實施，我們可以在**降低風險**的同時有序推進重構。每一階段完成後都將產出可衡量的改善，並為下一階段鋪平道路。這種循序漸進的方式確保我們不會在重構過程中中斷核心功能對外提供服務，同時也便於在每個里程碑結束時回顧調整策略，最終達成全面的重構目標。

## 8. 附錄：近期 Commits 技術分析摘要

為了指導本次重構，以下對近期幾個重要的 commit 進行簡要分析，這些更動透露出系統現有問題和優化方向，可作為重構設計的參考起點：

- **Murmur 系列提交** – 包括 `murmur_refine`, `murmur_logic`, `murmuradjust`, `change_murmur_tone` 等（日期：2025/04/24）。這組 commits 重點改善了 **自言自語 (murmur)** 功能的細節：
  - **觸發頻率調整**：縮短了閒置觸發 murmur 的時間間隔，從原先15秒縮減為12秒 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=IDLE_TIMEOUT_SECONDS%20%3D%2012%20,%E5%8E%9F%E7%82%BA15%E7%A7%92%EF%BC%8C%E7%B8%AE%E7%9F%AD%E4%BB%A5%E5%A2%9E%E5%8A%A0%E9%A0%BB%E7%8E%87))，以及將兩次 murmur 間的最小間隔從25秒縮短為20秒 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=match%20at%20L265%20MURMUR_MIN_INTERVAL_SECONDS%20%3D,%E5%8E%9F%E7%82%BA25%E7%A7%92%EF%BC%8C%E7%B8%AE%E7%9F%AD%E4%BB%A5%E4%BD%BF%E9%80%A3%E7%BA%8C%E6%80%9D%E8%80%83%E6%9B%B4%E6%B5%81%E6%9A%A2))。調整後虛擬主播在空閒時會更頻繁地自言自語，增強存在感。
  - **移除次數上限**：刪除了對連續 murmur 次數的上限限制，原本代碼中限制最多連續3次 murmur，如今不再限制 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=match%20at%20L271%20MURMUR_MAX_COUNT%20%3D,%E7%A7%BB%E9%99%A4%EF%BC%9A%E4%B8%8D%E5%86%8D%E9%99%90%E5%88%B6%E9%80%A3%E7%BA%8C%20murmur%20%E6%AC%A1%E6%95%B8))。這表示只要主播持續處於閒置且有“思考線索”，理論上可以一直自言自語下去。重構時我們會考慮保留此改動，同時透過參數配置允許調整上限（以備未來需要重新限制時不用改動代碼）。
  - **狀態與語氣調整**：引入了 `SpeakingState.PLAYING_MURMUR` 狀態來標記當前正在播放 murmur ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=match%20at%20L632%20speaking_state%20%3D,PLAYING_MURMUR))，並在生成 murmur 前切換到該狀態以區分於正常對話。在 `change_murmur_tone` commit 中，可能對 murmur 的語氣生成做了調整，使其與正常回答有所區別（例如更低語調或帶有沉思性）。這暗示我們在重構 murmur 模組時，需要允許不同語氣/風格的生成，可通過對 prompt 或語音合成參數的調整實現。
  - **上下文連貫**：murmur 系列改動還體現在保持 murmur 內容的連貫性上。代碼中新增邏輯，將最近的幾句 murmur 文本作為後續 murmur 的生成上下文 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=%E5%BE%9E%E6%9C%80%E8%BF%91%E7%9A%84%20murmur%20%E4%B8%AD%E6%A7%8B%E5%BB%BA%E6%80%9D%E8%80%83%E7%B7%9A%E7%B4%A2))。這讓虛擬主播的自言自語形成一條連續的“思考線索”，更具真實感。然而，長期連貫也可能累積錯誤或無效內容。因此，重構時我們會將此「記憶上下文」設為可選項，如前述目標所提，讓開發者決定 murmur 是否需維持連貫話題。

  *分析結論：* Murmur 系列 commits 顯示開發者希望增強虛擬主播閒置時的互動性和自然度。同時也暴露出 murmur 功能邏輯散佈在各處（狀態管理、計時觸發、內容生成皆在 WebSocket 主循環內）。這進一步證明將 murmur 獨立為模組的必要性。我們在重構中將把上述參數調整做更乾淨的封裝，提供配置化支持，並確保 murmur 狀態與對話主流程解耦。

- **`performance_refine` 提交** – （commit `fc91ccf`, 日期：2025/04/24）這次提交針對**系統性能**進行了一系列優化修改：
  - **跳過簡單問候的記憶檢索**：新增了對使用者輸入的類型檢查，如果判定為簡單問候語，如 “hi”、 “hello”，則不執行完整的記憶檢索流程，只提取必要的角色persona資訊即可 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=%E5%84%AA%E5%8C%96%EF%BC%9A%E6%AA%A2%E6%9F%A5%E8%BC%B8%E5%85%A5%E9%A1%9E%E5%9E%8B%EF%BC%8C%E5%B0%8D%E7%B0%A1%E5%96%AE%E5%95%8F%E5%80%99%E8%B7%B3%E9%81%8E%E8%A8%98%E6%86%B6%E6%AA%A2%E7%B4%A2))。透過這種早期短路，節省了無用的計算資源，加快了常見寒暄場合的響應速度。
  - **限制記憶檢索範圍**：在記憶檢索時增加了對 `k` 的控制，以及其他過濾策略。例如只檢索最近的記憶項，避免無限制地搜索全量歷史 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=match%20at%20L1976%20%E5%84%AA%E5%8C%96%EF%BC%9A%E9%99%90%E5%88%B6%E6%AA%A2%E7%B4%A2%E7%AF%84%E5%9C%8D%EF%BC%8C%E8%A8%AD%E7%BD%AE%E6%9C%80%E5%A4%A7k%E5%80%BC%E9%81%BF%E5%85%8D%E6%AA%A2%E7%B4%A2%E9%81%8E%E5%A4%9A%E8%A8%98%E6%86%B6))。這直接降低了每次檢索需要處理的文本/向量數量，提升速度並減少不相關干擾。
  - **移除摘要優化路徑**：先前系統可能會從長對話中產生“摘要記憶”以優化長上下文處理。但 `performance_refine` 中註解掉了摘要相關的檢索和合併邏輯 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=)) ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))。也就是說，不再檢索“摘要記憶庫”，只保留原始對話記憶和角色記憶。這麼做的原因可能是摘要生成本身耗時且效果未必理想，反而拖累性能。重構方案會採納這一經驗教訓：除非有可靠的摘要方案，否則先專注於優化原始記憶，而非引入額外的摘要層。
  - **並行化記憶查詢**：核心的改進在於使用 `asyncio.gather` 并行執行記憶檢索任務 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))。以前可能是順序檢索對話記憶、角色記憶、摘要記憶等，而現在改為同時發出，減少總等待時間。在 commit 中也可以看到為了實現並行，將記憶查詢任務組裝成列表再一次性 await。在重構中，我們將保留這一設計，並進一步完善錯誤處理（避免某一子任務失敗卡死整個 `gather`）。
  - **工具執行路徑調整**：值得注意的是，此 commit 還提及了 "disable_tools.md" 和對工具相關節點的處理 ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=3.%20%E5%9C%A8%20,%E3%80%82)) ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=workflow.add_node%28))。看起來開發者嘗試了暫時禁用工具以測試性能，以及隨後恢復工具路徑的變更。這佐證了**工具功能**與主流程的耦合影響性能，因此重構需要考慮提供啟用/停用工具的簡便機制，以及在性能關鍵路徑上減少不必要的工具判斷開銷。例如，可在配置中全局關閉工具相關流程的初始化，以免每次請求都經過檢查。

  *分析結論：* `performance_refine` commit 彰顯了當前系統瓶頸主要在記憶檢索與多餘流程上。透過有針對性地並行化、篩選和跳過，性能獲得提升。這些改動方向與本次重構的**效能優化**目標不謀而合。我們將在重構中徹底實現這些優化：例如正式引入 Redis 快取輔助跳過重複查詢、在MemoryRetriever中內建並行處理架構等。同時，從工具禁用的嘗試可以反映出未來需要**更靈活的系統配置**（Feature Toggle），以便在不同部署模式下權衡性能與功能。重構後的架構應允許我們輕鬆地開啟或關閉某些進階功能（如工具、murmur），從而在性能緊張時提供降級選項。

綜上，近期的 commit 為我們提供了實際數據點和經驗教訓，證明了某些重構方向的價值。例如，**模組解耦與開關**可以帶來靈活性、**並行處理與範圍控制**確實有效優化性能、**去除冗餘層**可以減少不必要開銷。藉由消化這些 commit 所呈現的資訊並融入到本 PRD 的重構計畫中，我們有信心讓下一版後端既保留這些短期改進成果，又能從更高層面解決底層架構問題，達成一個模組清晰、穩定快速的虛擬主播後端服務。 ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=IDLE_TIMEOUT_SECONDS%20%3D%2012%20,%E5%8E%9F%E7%82%BA15%E7%A7%92%EF%BC%8C%E7%B8%AE%E7%9F%AD%E4%BB%A5%E5%A2%9E%E5%8A%A0%E9%A0%BB%E7%8E%87)) ([murmur_refine · eggyy1224/space_live_project@9ac0c83 · GitHub](https://github.com/eggyy1224/space_live_project/commit/9ac0c83002cc6705fa2e56aadd193b14c6c0464d#:~:text=match%20at%20L271%20MURMUR_MAX_COUNT%20%3D,%E7%A7%BB%E9%99%A4%EF%BC%9A%E4%B8%8D%E5%86%8D%E9%99%90%E5%88%B6%E9%80%A3%E7%BA%8C%20murmur%20%E6%AC%A1%E6%95%B8)) ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=%E5%84%AA%E5%8C%96%EF%BC%9A%E6%AA%A2%E6%9F%A5%E8%BC%B8%E5%85%A5%E9%A1%9E%E5%9E%8B%EF%BC%8C%E5%B0%8D%E7%B0%A1%E5%96%AE%E5%95%8F%E5%80%99%E8%B7%B3%E9%81%8E%E8%A8%98%E6%86%B6%E6%AA%A2%E7%B4%A2)) ([performance_refine · eggyy1224/space_live_project@fc91ccf · GitHub](https://github.com/eggyy1224/space_live_project/commit/fc91ccf8d84d0ad65cd73e9db30484e20bb8e80d#:~:text=))

