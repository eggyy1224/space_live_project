# 專案部署 TODO 清單 (使用 Docker)

## 一、 準備階段 (本地環境)

-   [ ] **後端 Dockerfile 建立**
    -   在 `prototype/backend/` 資料夾下建立 `Dockerfile`。
    -   選擇合適的 Python 基礎映像 (如 `python:3.10-slim`)。
    -   複製後端程式碼。
    -   安裝 `requirements.txt` 中的依賴。
    -   設定工作目錄。
    -   定義容器啟動指令 (使用 `uvicorn main:app --host 0.0.0.0 --port 8000`)。
    -   處理 `.env` 環境變數 (確保 Dockerfile 不包含敏感金鑰，部署時透過環境變數傳入)。
-   [ ] **前端 Dockerfile 建立**
    -   在 `prototype/frontend/` 資料夾下建立 `Dockerfile`。
    -   選擇合適的 Node.js 基礎映像 (如 `node:18-alpine`) 作為建構階段。
    -   複製前端程式碼。
    -   安裝 `package.json` 中的依賴 (`npm install` 或 `yarn install`)。
    -   執行建構指令 (`npm run build` 或 `yarn build`)。
    -   使用多階段建構 (multi-stage build)：
        -   建立一個輕量級的 Web 伺服器映像 (如 `nginx:alpine`) 作為最終階段。
        -   從建構階段複製 `dist` 目錄下的靜態檔案到 Nginx 的網站根目錄。
        -   配置 Nginx (例如建立 `nginx.conf`) 來正確提供 SPA 服務 (處理路由 fallback)。
-   [ ] **Docker Compose 文件建立**
    -   在專案根目錄建立 `docker-compose.yml`。
    -   定義 `frontend` 服務：
        -   指向 `prototype/frontend/Dockerfile`。
        -   設定端口映射 (例如 `80:80` 或 `8080:80`)。
        -   設定 `build context` 為 `prototype/frontend`。
    -   定義 `backend` 服務：
        -   指向 `prototype/backend/Dockerfile`。
        -   設定端口映射 (例如 `8000:8000`)。
        -   設定 `build context` 為 `prototype/backend`。
        -   設定必要的環境變數 (從本地 `.env` 讀取或直接定義，注意安全)。
        -   可能需要設定 `depends_on` (雖然前後端分離通常不需要)。
        -   設定網路 (確保前後端在同一個 Docker 網路)。
-   [ ] **本地 Docker 環境測試**
    -   執行 `docker-compose build` 建構前後端映像。
    -   執行 `docker-compose up` 啟動服務。
    -   **測試點:**
        -   訪問前端 URL (例如 `http://localhost:8080`)，確認網頁正常載入。
        -   測試後端健康檢查 API (例如 `curl http://localhost:8000/api/health`)，確認回傳 `{"status": "ok"}`。
        -   透過前端介面測試核心功能 (聊天、語音輸入/輸出)，檢查瀏覽器開發者工具的網路請求是否成功到達後端 (例如 `http://localhost:8000/api/...` 或 WebSocket 連線)。
        -   檢查 `docker-compose logs` 是否有錯誤訊息。

## 二、 部署階段 (目標環境)

*選擇一種部署方式 (以下以常見的 VPS/雲主機為例)*

-   [ ] **準備目標伺服器**
    -   安裝 Docker。
    -   安裝 Docker Compose。
    -   設定防火牆規則 (開放前端、後端所需端口)。
-   [ ] **複製專案程式碼**
    -   將整個專案 (包含 Dockerfile 和 docker-compose.yml) 複製到伺服器。
    -   (或者) 設定 CI/CD 流程，自動從 Git 拉取程式碼並建構映像。
-   [ ] **設定環境變數**
    -   在伺服器上安全地設定後端所需的環境變數 (例如建立 `.env` 檔案供 `docker-compose.yml` 讀取，或使用系統環境變數)。**確保 `.env` 文件權限安全且不在 Git 中**。
-   [ ] **建構與啟動服務**
    -   在伺服器上執行 `docker-compose build` (如果尚未在本地推送映像到 Registry)。
    -   執行 `docker-compose up -d` 在後台啟動服務。

## 三、 驗證階段 (部署後)

-   [ ] **基本連線測試**
    -   **前端:** 從公開網路訪問部署後的前端 URL (例如 `http://your_domain.com` 或 `http://your_server_ip`)。
        -   **成功:** 網頁介面正常載入，主要元件 (3D 模型、聊天框) 可見。
        -   **失敗:** 網頁無法訪問 (檢查防火牆、Nginx 設定、Docker 容器是否運行)。
    -   **後端:** (可選，若 API 可公開訪問) 測試健康檢查 API (例如 `curl http://your_domain.com/api/health` 或 `http://your_server_ip:8000/api/health`)。
        -   **成功:** 回傳 `{"status": "ok"}`。
        -   **失敗:** 無法連線或回傳錯誤 (檢查防火牆、後端容器日誌、端口映射)。
-   [ ] **核心功能測試 (透過前端)**
    -   **WebSocket 連線:** 檢查瀏覽器開發者工具的網路(Network)標籤，確認 WebSocket 連線 (`/ws`) 是否成功建立 (狀態碼 101 Switching Protocols)。
        -   **成功:** 連線建立，無錯誤訊息。
        -   **失敗:** 連線失敗 (檢查後端 WebSocket 端點是否正常、網路設定)。
    -   **聊天功能:**
        -   發送文字訊息。
        -   **成功:** 訊息出現在聊天框，AI 有文字回覆，瀏覽器控制台無錯誤，後端 Docker 日誌顯示處理訊息。
        -   **失敗:** 訊息發送失敗、AI 無回應、介面卡住 (檢查 WebSocket 通訊、後端 AI Service 日誌)。
    -   **語音輸入 (STT):**
        -   嘗試使用麥克風錄音輸入。
        -   **成功:** 錄音正常，前端顯示識別出的文字，後端收到語音請求並成功處理 (檢查後端日誌 `/api/speech-to-text`)。
        -   **失敗:** 無法錄音、識別失敗、請求錯誤 (檢查瀏覽器麥克風權限、前端 AudioService 邏輯、後端 STT Service 日誌、OpenAI API 金鑰)。
    -   **語音輸出 (TTS):**
        -   確認 AI 回覆時是否有語音播放。
        -   **成功:** 聽到 AI 的語音回覆，嘴型大致同步。
        -   **失敗:** 沒有聲音、播放錯誤 (檢查後端 TTS Service 日誌、OpenAI API 金鑰、前端 AudioService 播放邏輯)。
    -   **3D 模型與互動:**
        -   確認 3D 太空人模型正常顯示。
        -   嘗試控制表情或動畫 (如果控制介面已部署)。
        -   確認 AI 回覆時表情有變化 (情緒同步)。
        -   **成功:** 模型顯示正確，互動正常，表情隨情緒變化。
        -   **失敗:** 模型不顯示、破圖、互動無反應、表情不變 (檢查前端 Three.js 相關程式碼、模型檔案路徑、WebSocket 狀態更新)。
-   [ ] **日誌監控**
    -   檢查後端容器日誌 (`docker-compose logs backend`) 是否有持續的錯誤或警告訊息。
    -   檢查前端 Nginx 容器日誌 (`docker-compose logs frontend`) 是否有異常。
        -   **成功:** 日誌乾淨，只有正常的請求記錄。
        -   **失敗:** 出現大量錯誤堆疊、資源找不到 (404) 等。
-   [ ] **資源使用情況檢查 (可選)**
    -   使用 `docker stats` 或伺服器監控工具檢查容器的 CPU 和記憶體使用率是否在合理範圍。
        -   **成功:** 資源使用穩定。
        -   **失敗:** CPU 或記憶體佔用過高 (可能存在程式碼效能問題或資源洩漏)。

完成以上所有測試點且均成功，即可認為部署成功。若有任何失敗，根據失敗的測試點和相關日誌進行排查。 