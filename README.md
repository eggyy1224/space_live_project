# 🚀 星際小可愛 (Space Live Project) 🚀

**歡迎來到「星際小可愛」的宇宙！這是一個正在開發中的 AI 互動專案，旨在創造一個生活在太空站、擁有記憶、個性與情感的虛擬太空網紅。**

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)
![AI Orchestration](https://img.shields.io/badge/AI%20Orchestration-LangGraph-orange.svg)
![Memory](https://img.shields.io/badge/Memory-ChromaDB-purple.svg)

---

## ✨ 專案願景

想像一下，能和一位身處遙遠太空站的 AI 網紅即時聊天，聽她分享太空生活的點滴，感受她的喜怒哀樂，甚至你的話語還能影響她的心情和狀態... 這就是「星際小可愛」想要實現的目標！

本專案不僅僅是一個聊天機器人，我們致力於：

*   **打造有靈魂的角色**: 賦予 AI 獨特的背景故事、鮮明的個性（活潑、好奇、偶爾感性）和專業知識（太空、科技）。
*   **實現有溫度的互動**: 透過即時語音交流，建立用戶與 AI 之間的情感連結。
*   **模擬有記憶的交流**: 利用先進的記憶系統，讓 AI 記得過去的對話，使交流更連貫、更深入。
*   **探索動態的體驗**: AI 的狀態會隨互動和模擬事件變化，帶來不可預測的趣味性。

**目標應用場景:** 展覽互動、教育娛樂、虛擬陪伴、AI Agent 研究等。

---

## 核心功能與技術亮點 (後端 AI 核心)

*   **🎙️ 即時語音互動支持**: 後端設計可接收文本輸入（來自 STT），生成文本回應（傳給 TTS）。
*   **🧠 多層次記憶系統 (`MemorySystem`)**: 
    *   **長期對話記憶**: 使用 ChromaDB 持久化儲存對話歷史。
    *   **角色核心記憶**: 獨立儲存 AI 的身份、背景和學習到的事實。
    *   **智能檢索**: 結合上下文進行向量搜索 (MMR 提高多樣性)，提取相關記憶輔助對話。
*   **🧩 LangGraph 驅動的對話引擎 (`DialogueGraph`)**:
    *   **流程圖化**: 將複雜的對話邏輯拆解為清晰的狀態圖 (StateGraph)，包含記憶檢索、上下文準備、LLM 調用、後處理、記憶儲存等節點。
    *   **狀態管理**: 在圖中顯式管理和傳遞對話狀態 (`DialogueState`)。
    *   **高擴展性**: 便於未來添加工具使用、反思修正循環、條件分支等複雜 Agent 行為。
*   **🎭 動態角色狀態**:
    *   包含心情、能量、健康等多維度狀態。
    *   狀態影響 AI 的回應風格（熱情、疲倦、幽默等）。
    *   可通過互動和模擬事件更新狀態。
*   **🤝 向後兼容接口 (`AIService`)**: 提供穩定的適配器層，方便現有系統集成。

---

## 🏗️ 系統架構 (後端 AI 核心)

本倉庫主要聚焦於後端 AI 核心服務的實現。

```mermaid
graph LR
    subgraph Backend (FastAPI 服務)
        API(WebSocket / HTTP API) -- Text --> AIService[AI 服務接口]
        AIService -- 用戶輸入 / 當前狀態 --> DialogueGraph[對話流程圖引擎]
        DialogueGraph -- 記憶查詢 --> MemorySystem[記憶系統]
        MemorySystem -- 記憶上下文 --> DialogueGraph
        DialogueGraph -- 提示 --> LLM_Service[LLM (Google Gemini)]
        LLM_Service -- 原始回應 --> DialogueGraph
        DialogueGraph -- 儲存對話 --> MemorySystem
        DialogueGraph -- 最終回應 / 更新狀態 --> AIService
        AIService -- 文本回應 --> API
    end

    subgraph AI Core (services/ai)
        AIService -- 協調 --> DialogueGraph
        DialogueGraph -- 使用 --> MemorySystem
        MemorySystem -- 讀寫 --> ChromaDB[(向量數據庫)]
    end

    subgraph External Services (外部依賴)
        LLM_Service
    end

    style Backend fill:#eef,stroke:#333,stroke-width:1px
    style AI Core fill:#dff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style External Services fill:#fff,stroke:#999,stroke-width:1px
```

*   **後端 (FastAPI)**: 處理 API 請求，協調各服務 (部分實現在本倉庫)。
*   **AI 核心 (`services/ai`)**: 
    *   `AIService`: 外部接口和兼容層。
    *   `DialogueGraph`: 使用 LangGraph 編排對話流程。
    *   `MemorySystem`: 管理 ChromaDB 記憶。
*   **外部服務**: 需要配置 Google Gemini API Key。STT/TTS 需另行整合。

---

## 🛠️ 環境設置與運行 (後端 AI 核心)

**1. 環境準備:**

*   Python 3.10 或更高版本
*   Git

**2. 獲取程式碼:**

```bash
git clone <your-repository-url>
cd space_live_project
```

**3. 創建與激活虛擬環境:**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

**4. 安裝核心依賴:**

*   (推薦) 使用 `requirements.txt` (如果提供):
    ```bash
    pip install -r requirements.txt
    ```
*   (手動) 安裝關鍵庫:
    ```bash
    pip install fastapi uvicorn langchain langgraph langchain-google-genai chromadb pydantic python-dotenv loguru
    ```
    *注意：請根據實際 `import` 情況調整。*

**5. 配置環境變數:**

*   創建 `.env` 文件 (可參考 `.env.example` 如果有的話)。
*   在 `.env` 文件中填入你的 Google API Key:
    ```dotenv
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    # 可能需要添加其他配置，如 VECTOR_DB_PATH="./chroma_db"
    ```
*   確保 `prototype/backend/core/config.py` 能正確讀取這些變數。

**6. 啟動後端服務 (用於測試或集成):**

*   假定 FastAPI 應用實例在 `prototype/backend/main.py` 中的 `app`。
    ```bash
    cd prototype/backend
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

**7. 測試與互動:**

*   可以使用 API 測試工具 (如 Postman、Insomnia) 或編寫簡單的客戶端腳本來調用後端 API (通常在 `main.py` 或 `api/` 目錄下定義)。
*   測試 `generate_response` 端點，傳入用戶文本，觀察 AI 回應和日誌。

---

## 📂 專案結構導覽

```
/space_live_project/
├── docs/                    # 文檔 (設計方案、會議記錄等)
│   └── 後端相關/
│       └── 0402記憶系統方案.md # 詳細架構說明
├── prototype/               # 主要程式碼目錄
│   ├── backend/             # 後端 FastAPI 服務
│   │   ├── api/             # API 端點定義 (Routers)
│   │   ├── core/            # 核心配置 (config.py), 異常 (exceptions.py)
│   │   ├── services/        # 業務邏輯服務
│   │   │   └── ai/          # AI 核心模組
│   │   │       ├── __init__.py      # AIService (適配器)
│   │   │       ├── memory_system.py # 長期記憶管理
│   │   │       └── dialogue_graph.py # LangGraph 對話流程引擎
│   │   └── main.py          # FastAPI 應用主入口
│   └── ...
├── venv/                    # (Git忽略) Python 虛擬環境
├── .env                     # (Git忽略) 環境變數
├── .gitignore               # Git 忽略規則
├── README.md                # 就是你正在看的這個文件
└── requirements.txt         # (推薦) Python 依賴列表
```

---

## 🚀 未來展望與擴展 (AI 核心)

基於 LangGraph 的靈活架構，我們可以輕鬆探索更多可能性：

*   **工具使用**: 讓 AI 能夠查詢外部信息、執行計算或控制模擬設備。
*   **反思與學習**: 實現自我修正循環，從錯誤中學習或優化表達。
*   **情境感知**: 根據模擬的太空事件動態調整 AI 行為。
*   **更豐富的情感模型**: 模擬更細膩的情緒變化。

詳細的技術擴展方向請參考 [設計方案文檔](docs/後端相關/0402記憶系統方案.md)。

---

## 🙏 貢獻

(如果你希望開源或接受貢獻，可以在此處添加貢獻指南，例如：)

我們歡迎各種形式的貢獻！無論是發現 Bug、提出功能建議還是直接提交程式碼，請通過 Issue 與我們聯繫或提交 Pull Request。

---

## 📄 授權協議

(請根據你的選擇填寫授權協議，例如：)

本專案採用 [MIT License](LICENSE) 授權。

---

**感謝你的關注，讓我們一起見證「星際小可愛」的成長！** 