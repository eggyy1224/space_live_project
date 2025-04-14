# 專案部署 TODO 清單 (使用 Docker + Zeabur)

## 一、 準備階段 (本地環境)

-   [ ] **後端 Dockerfile 建立**
    -   在 `prototype/backend/` 資料夾下建立 `Dockerfile`。
    -   選擇合適的 Python 基礎映像 (如 `python:3.10-slim`)。
    -   複製後端程式碼。
    -   安裝 `requirements.txt` 中的依賴。
    -   設定工作目錄。
    -   定義容器啟動指令 (使用 `uvicorn main:app --host 0.0.0.0 --port 8000`)。
    -   確保暴露正確的埠口 (使用 `EXPOSE 8000`)。
    -   處理 `.env` 環境變數 (確保 Dockerfile 不包含敏感金鑰，部署時透過環境變數傳入)。
-   [ ] **前端 Dockerfile 建立 (已更新)**
    -   在專案根目錄建立 `frontend.Dockerfile`，使用多階段構建方式：
    -   **第一階段 (builder)：**
        -   使用 `node:18-alpine` 作為基礎映像。
        -   設定工作目錄為 `/app`。
        -   複製前端代碼到 `/app/prototype/frontend/`。
        -   複製腳本目錄到 `/app/scripts/`。
        -   設置工作目錄到 `/app/prototype/frontend`。
        -   安裝依賴（`npm install`）。
        -   確保動畫目錄和配置目錄存在（`mkdir -p /app/prototype/frontend/public/animations /app/prototype/shared/config`）。
        -   運行動畫同步腳本（`cd /app/scripts && node sync_animations.js`）。
        -   執行建構指令（`npm run build -- --force`）。
    -   **第二階段：**
        -   使用 `nginx:alpine` 作為基礎映像。
        -   複製 Nginx 配置文件。
        -   從構建階段複製編譯好的檔案（`COPY --from=builder /app/prototype/frontend/dist /usr/share/nginx/html`）。
        -   暴露 80 端口。
        -   啟動 Nginx 伺服器。
-   [ ] **為 Zeabur 調整 Dockerfile 名稱**
    -   由於 Zeabur 支援依照服務名稱命名的 Dockerfile，建議將後端 Dockerfile 重命名為 `backend.Dockerfile` 或 `Dockerfile.backend`。
    -   同樣，將前端 Dockerfile 重命名為 `frontend.Dockerfile` 或 `Dockerfile.frontend`。
    -   確保這些 Dockerfile 都放置在專案根目錄下，以便 Zeabur 能正確識別。
-   [ ] **本地 Docker 環境測試**
    -   執行 `docker build -f backend.Dockerfile -t space-backend .` 建構後端映像。
    -   執行 `docker build -f frontend.Dockerfile -t space-frontend .` 建構前端映像。
    -   執行 `docker run -p 8000:8000 --env-file .env space-backend` 測試後端服務。
    -   執行 `docker run -p 80:80 space-frontend` 測試前端服務。
    -   **測試點:**
        -   訪問前端 URL (例如 `http://localhost`)，確認網頁正常載入。
        -   測試後端健康檢查 API (例如 `curl http://localhost:8000/api/health`)，確認回傳 `{"status": "ok"}`。
        -   透過前端介面測試核心功能 (聊天、語音輸入/輸出)，檢查瀏覽器開發者工具的網路請求是否成功到達後端。
        -   檢查 Docker 容器的日誌 (`docker logs <container_id>`) 是否有錯誤訊息。

## 二、 部署選項 A：使用 Zeabur YAML 模板 (推薦)

這種方法可以一次性部署所有相關服務，簡化操作流程，適合需要重複部署或在多環境中部署的情況。

-   [ ] **建立 Zeabur 模板 YAML 檔案**
    -   在專案根目錄建立 `space-live.yaml` 檔案，包含以下內容：
    ```yaml
    apiVersion: zeabur.com/v1
    kind: Template
    metadata:
        name: SpaceLiveAssistant
    spec:
        description: 虛擬太空人助理專案，提供即時語音與文字互動功能
        icon: https://raw.githubusercontent.com/your-repo/your-project/main/logo.png  # 替換為您的專案 logo URL
        variables:
            - key: OPENAI_API_KEY
              type: STRING
              name: OpenAI API Key
              description: 您的 OpenAI API 金鑰，用於語音識別和生成回應
            - key: FRONTEND_DOMAIN
              type: DOMAIN
              name: 前端網域
              description: 設定前端服務的網域名稱 (例如輸入 myapp 將得到 myapp.zeabur.app)
            - key: BACKEND_DOMAIN
              type: DOMAIN
              name: 後端網域
              description: 設定後端服務的網域名稱 (例如輸入 myapi 將得到 myapi.zeabur.app)
        services:
            - name: space-backend
              template: PREBUILT
              spec:
                source:
                    context: "."
                    dockerfile: backend.Dockerfile
                ports:
                    - id: web
                      port: 8000
                      type: HTTP
                env:
                    OPENAI_API_KEY:
                        default: ${OPENAI_API_KEY}
                        readonly: true
                    CHROMADB_HOST:
                        default: chromadb.zeabur.internal
                    CHROMADB_PORT:
                        default: "8000"
                instructions:
                    - type: TEXT
                      title: 後端服務 URL
                      content: ${SERVICE_DOMAIN}
                    - type: TEXT
                      title: WebSocket URL
                      content: wss://${SERVICE_DOMAIN}/ws
                
            - name: space-frontend
              template: PREBUILT
              spec:
                source:
                    context: "."
                    dockerfile: frontend.Dockerfile
                ports:
                    - id: web
                      port: 80
                      type: HTTP
                env:
                    VITE_API_BASE_URL:
                        default: "https://${BACKEND_DOMAIN}"
                    VITE_WS_URL:
                        default: "wss://${BACKEND_DOMAIN}/ws"
                instructions:
                    - type: DOMAIN
                      title: 前端網站
                      content: https://${SERVICE_DOMAIN}
            
            - name: chromadb
              template: PREBUILT
              spec:
                source:
                    image: chromadb/chroma:latest
                ports:
                    - id: chroma-api
                      port: 8000
                      type: HTTP
                volumes:
                    - id: chroma-data
                      dir: /chroma/.chroma/index
    ```

-   [ ] **使用 Zeabur CLI 部署模板**
    -   安裝 Zeabur CLI (若尚未安裝)：
      ```bash
      npm install -g zeabur
      ```
    -   登入 Zeabur CLI：
      ```bash
      zeabur login
      ```
    -   部署模板：
      ```bash
      zeabur template deploy -f space-live.yaml
      ```
    -   根據提示選擇專案和填入變數 (如 `OPENAI_API_KEY` 等)。

-   [ ] **驗證已部署的服務**
    -   確認 Zeabur 控制台中顯示所有三個服務 (frontend, backend, chromadb) 都已正常部署。
    -   檢查各服務的日誌，確保沒有錯誤訊息。
    -   測試前端網站是否可以正常訪問。
    -   繼續執行「三、驗證和測試階段」中的步驟以驗證功能性。

-   [ ] **(可選) 上架模板到 Zeabur 市集**
    -   如果需要頻繁重複部署或與團隊分享，可以考慮上架模板：
      ```bash
      zeabur template create -f space-live.yaml
      ```
    -   記錄生成的模板 URL，可以分享給團隊成員使用。

## 三、 部署選項 B：Zeabur 手動部署階段

如果不使用 YAML 模板，也可以通過以下步驟手動部署：

-   [ ] **註冊並準備 Zeabur 環境**
    -   在 [Zeabur 官網](https://zeabur.com) 註冊/登入帳戶。
    -   建立新專案。
    -   設定專案環境（開發/生產）。

-   [ ] **部署前端服務**
    -   點選「Add Service」→ 選擇「Git」(如果從 GitHub 部署) 或「Prebuilt Images」→「自定義」。
    -   如果使用 Git:
        -   選擇專案儲存庫。
        -   設定服務名稱 (例如 `space-frontend`)。
        -   選擇使用 `frontend.Dockerfile` 或 `Dockerfile.frontend` (可以使用 `ZBPACK_DOCKERFILE_NAME=frontend` 環境變數指定)。
    -   如果使用自定義 Prebuilt:
        -   如果有現成的 Docker 映像，可直接指定映像名稱。
        -   設定服務名稱。
    -   設定前端服務埠：
        -   Port Name 設定為 `web` 或自訂名稱。
        -   Port 設定為 `80`。
        -   Port Type 選擇 `HTTP`。
    -   設定前端環境變數：
        -   `VITE_API_BASE_URL`：設為後端 API 的 URL (可以等後端部署完成後再設定)。
        -   `VITE_WS_URL`：設為後端 WebSocket 的 URL (通常是 `wss://後端服務URL/ws`)。
    -   啟動服務部署。

-   [ ] **部署後端服務**
    -   再次點選「Add Service」→ 選擇「Git」或「Prebuilt Images」→「自定義」。
    -   如果使用 Git:
        -   選擇相同的專案儲存庫。
        -   設定服務名稱 (例如 `space-backend`)。
        -   選擇使用 `backend.Dockerfile` 或 `Dockerfile.backend` (可以使用 `ZBPACK_DOCKERFILE_NAME=backend` 環境變數指定)。
    -   如果使用自定義 Prebuilt:
        -   如果有現成的後端 Docker 映像，可直接指定映像名稱。
    -   設定後端服務埠：
        -   Port Name 設定為 `web` 或自訂名稱。
        -   Port 設定為 `8000`。
        -   Port Type 選擇 `HTTP`。
    -   設定敏感環境變數：
        -   `OPENAI_API_KEY`：OpenAI API 金鑰。
        -   其他需要的 API 金鑰和配置參數。
    -   預留 ChromaDB 連接的環境變數 (稍後設定)。
    -   啟動服務部署。

-   [ ] **部署 ChromaDB 服務**
    -   點選「Add Service」→ 選擇「Prebuilt Images」→「自定義」。
    -   在 Image 欄位輸入 `chromadb/chroma:latest`。
    -   設定服務名稱 (例如 `chromadb`)。
    -   設定 ChromaDB 服務埠：
        -   Port Name 設定為自訂名稱 (例如 `chroma-api`)。
        -   Port 設定為 `8000`。
        -   Port Type 選擇 `HTTP`。
    -   設定持久化存儲：
        -   Volume id 設定為自訂名稱 (例如 `chroma-data`)。
        -   Path 設定為 `/chroma/.chroma/index`。
    -   啟動服務部署。

-   [ ] **設定服務間連接**
    -   服務部署完成後，需要讓它們能互相通信：
    -   更新後端服務環境變數：
        -   `CHROMADB_HOST`：設定為 `chromadb.zeabur.internal` (Zeabur 內部服務網路名稱)。
        -   `CHROMADB_PORT`：設定為 `8000`。
    -   更新前端服務環境變數：
        -   `VITE_API_BASE_URL`：設定為後端服務的 URL (例如 `https://space-backend.zeabur.app`)。
        -   `VITE_WS_URL`：設定為後端 WebSocket 的 URL (例如 `wss://space-backend.zeabur.app/ws`)。

-   [ ] **設定網域與公開訪問**
    -   前往前端服務的設定頁，選擇「公開存取」標籤。
    -   可以使用 Zeabur 提供的預設子網域 (如 `space-frontend.zeabur.app`) 或綁定自定義網域。
    -   對於後端服務，同樣可以設定公開訪問，以便前端可以從公網連接。
    -   確認 HTTPS 已自動配置 (Zeabur 預設提供)。

-   [ ] **檢查服務狀態和日誌**
    -   部署完成後，檢查各服務的運行狀態。
    -   查看服務日誌，確認沒有錯誤訊息。
    -   如有需要，可以使用 Zeabur 提供的「即時日誌」功能跟踪服務運行情況。

## 四、 驗證和測試階段

-   [ ] **基本連線測試**
    -   **前端:** 從公開網路訪問部署的前端 URL (例如 `https://space-frontend.zeabur.app`)。
        -   **成功:** 網頁介面正常載入，主要元件 (3D 模型、聊天框) 可見。
        -   **失敗:** 網頁無法訪問 (檢查 Zeabur 服務狀態、服務日誌)。
    -   **後端:** 測試健康檢查 API (例如 `curl https://space-backend.zeabur.app/api/health`)。
        -   **成功:** 回傳 `{"status": "ok"}`。
        -   **失敗:** 無法連線或回傳錯誤 (檢查後端服務日誌、環境變數設定)。

-   [ ] **核心功能測試**
    -   **WebSocket 連線:** 
        -   檢查瀏覽器開發者工具的網路(Network)標籤，確認 WebSocket 連線 (`/ws`) 是否成功建立 (狀態碼 101 Switching Protocols)。
        -   **成功:** 連線建立，無錯誤訊息。
        -   **失敗:** 連線失敗 (檢查後端 WebSocket 端點、前端 WebSocket URL 設定)。
    -   **聊天功能:**
        -   發送文字訊息。
        -   **成功:** 訊息出現在聊天框，AI 有文字回覆，瀏覽器控制台無錯誤。
        -   **失敗:** 訊息發送失敗、AI 無回應、介面卡住 (檢查 WebSocket 通訊、後端 AI Service 日誌)。
    -   **語音輸入 (STT):**
        -   嘗試使用麥克風錄音輸入。
        -   **成功:** 錄音正常，前端顯示識別出的文字，後端收到語音請求並成功處理。
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
        -   **失敗:** 模型不顯示、破圖、互動無反應、表情不變 (檢查前端 Three.js 相關程式碼、模型檔案路徑)。

-   [ ] **ChromaDB 功能測試**
    -   執行一次向量查詢功能，確認後端能成功連接到 ChromaDB。
    -   確認資料持久化正常 (例如，重啟後端服務後，先前儲存的向量資料依然可用)。
    -   **成功:** 向量查詢正常，返回預期結果。
    -   **失敗:** 連接錯誤或查詢失敗 (檢查 ChromaDB 連接設定、ChromaDB 服務日誌)。

-   [ ] **效能測試 (可選)**
    -   測試在正常負載下的響應時間。
    -   測試同時多個用戶連接時的系統穩定性。
    -   監控資源使用情況 (可在 Zeabur 控制台查看)。
    -   **成功:** 系統響應時間合理，多用戶測試無明顯延遲或錯誤。
    -   **失敗:** 響應緩慢、系統不穩定 (考慮調整服務配置或優化程式碼)。

## 五、 Zeabur 特殊注意事項

-   [ ] **環境變數設定技巧**
    -   使用 Zeabur 的環境變數功能來儲存敏感資訊，避免硬編碼在代碼中。
    -   如果需要在多階段 Dockerfile 中使用建置時環境變數，使用 `ARG` 和 `ENV` 組合：
      ```Dockerfile
      ARG BUILDTIME_ENV_EXAMPLE
      ENV BUILDTIME_ENV_EXAMPLE=${BUILDTIME_ENV_EXAMPLE}
      ```
    -   利用 Zeabur 的變數暴露 (Expose) 功能在不同服務之間共享環境變數。

-   [ ] **Dockerfile 指定技巧**
    -   如果不想使用現有的 Dockerfile，可設定環境變數 `ZBPACK_IGNORE_DOCKERFILE=true`。
    -   如果需要指定使用特定名稱的 Dockerfile，可設定環境變數 `ZBPACK_DOCKERFILE_NAME=backend`。
    -   如果有多個 Dockerfile，確保它們遵循 `[服務名稱].Dockerfile` 或 `Dockerfile.[服務名稱]` 的命名模式。

-   [ ] **服務內網通訊**
    -   在 Zeabur 中，服務可以通過 `[服務名稱].zeabur.internal` 網域名稱進行內部通訊。
    -   內部通訊不會產生額外流量費用，且更安全、更快速。
    -   確保後端服務使用這種方式連接 ChromaDB (例如 `chromadb.zeabur.internal:8000`)。

-   [ ] **持久化儲存管理**
    -   定期檢查持久化存儲的使用情況，避免空間不足。
    -   考慮設定儲存空間的備份策略 (Zeabur 提供備份功能)。
    -   監控儲存費用，必要時進行清理或優化。

-   [ ] **監控與擴展**
    -   使用 Zeabur 的監控功能追蹤服務健康狀況和資源使用情況。
    -   根據流量和使用模式，考慮調整服務的資源配置。
    -   設置自動擴展策略 (如果 Zeabur 支援且專案需要)。

完成以上所有測試點且均成功，即可認為部署成功。若有任何失敗，根據失敗的測試點和相關日誌進行排查。可以參考 [Zeabur 文檔](https://zeabur.com/docs/zh-TW/deploy/customize-prebuilt) 及 [Zeabur 模板文檔](https://zeabur.com/docs/zh-TW/template/template-in-code) 獲取更多幫助。

## 六、已完成的項目

-   [x] **前端 Docker 映像檔建立與測試**
    -   前端 Dockerfile 已建立在專案根目錄，檔名為 `frontend.Dockerfile`。
    -   Docker 映像檔已成功構建，採用了以下特殊處理：
        -   複製整個專案到容器中，確保腳本目錄可以正確訪問。
        -   正確處理動畫同步腳本，實現動畫資源管理。
        -   跳過 TypeScript 檢查，直接使用 Vite 構建靜態檔案。
        -   使用多階段建構，採用 Nginx 作為靜態檔案伺服器。
    -   映像檔已成功構建為 `space-frontend`。
    -   映像檔已成功運行測試，並映射至主機的 80 端口。
    -   驗證方法：在瀏覽器訪問 http://localhost 查看前端頁面。

-   [ ] **後端 Docker 映像檔建立與測試**
    -   等待後端開發團隊的進一步指示。