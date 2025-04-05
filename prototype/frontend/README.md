# 虛擬太空人互動原型

這是一個基於 React 和 Three.js 的 3D 人物模型互動應用，結合 FastAPI 後端和 Google Gemini AI 進行自然語言處理和表情控制。

## 功能特點

- 使用 React Three Fiber 渲染 3D 模型
- 支持模型動畫控制和 Morph Target 表情調整
- 語音輸入和輸出功能
- 即時表情變化根據對話情緒
- WebSocket 實時通信
- 支持文本和語音互動

## 系統要求

- Node.js 16+
- Python 3.9+
- Google API 密鑰 (Gemini AI)
- Google Cloud 憑證 (用於文本轉語音和語音轉文本)

## 安裝指南

### 前端設置

1. 安裝依賴：

```bash
cd prototype
npm install
```

2. 啟動開發服務器：

```bash
npm run dev
```

### 後端設置

1. 安裝依賴：

```bash
cd prototype/backend
pip install -r requirements.txt
```

2. 創建 `.env` 文件，根據 `.env.example` 設置環境變數：

```
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=your_google_credentials_json_path_here
```

3. 啟動後端服務器：

```bash
cd prototype/backend
python main.py
```

## 使用說明

1. 打開瀏覽器訪問前端應用（默認為 http://localhost:5173）
2. 等待 3D 模型加載完成
3. 使用應用右側的控制面板來：
   - 控制模型動畫
   - 應用預設表情
   - 手動調整表情參數
   - 與模型進行文本或語音交談

### 聊天功能

- 點擊「聊天」標籤切換到對話界面
- 在文本框中輸入訊息，按「發送」按鈕或按 Enter 鍵發送
- 按住麥克風按鈕進行語音輸入，鬆開時自動發送
- 等待 AI 回應並觀察模型表情變化
- 紅色指示燈亮起表示正在錄音，綠色表示正在播放語音，黃色表示正在處理

### 表情控制

- 點擊「控制」標籤查看表情控制面板
- 使用預設表情按鈕應用常見表情
- 在表情控制列表中，點擊任何表情參數進行選擇
- 使用進度條調整選定表情參數的強度
- 觀察模型臉部表情實時變化

## 技術說明

前端：
- React + TypeScript
- Vite
- React Three Fiber
- Three.js
- WebSockets

後端：
- FastAPI
- Google Gemini AI
- Google Cloud Text-to-Speech
- Google Cloud Speech-to-Text
- WebSockets

## 注意事項

- 首次使用語音功能時需要授予麥克風訪問權限
- 確保 API 密鑰和憑證正確設置在 `.env` 文件中
- 後端默認運行在 8000 端口，前端默認運行在 5173 端口
