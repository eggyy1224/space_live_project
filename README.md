# 虛擬宇航員互動系統

一個基於React、TypeScript和Three.js的實時虛擬宇航員互動系統，支持3D模型渲染、語音對話和表情動畫。

## 專案概述

本系統是一個結合了AI對話、語音識別、3D角色渲染和實時動畫的虛擬宇航員互動平台。用戶可以通過文字或語音與虛擬宇航員進行對話，系統會實時生成宇航員的語音回應、情緒表情和口型動畫。

## 系統架構

### 前端架構

- **前端框架**：React + TypeScript
- **3D渲染**：Three.js + React Three Fiber + Drei
- **狀態管理**：React Hooks + 服務單例模式
- **通信協議**：WebSocket + RESTful API
- **構建工具**：Vite

主要服務模組：
- **WebSocketService**：處理與後端的實時通信
- **ModelService**：3D模型管理和動畫控制
- **AudioService**：音頻處理和語音交互
- **ChatService**：對話邏輯和消息管理

### 後端架構

- **框架**：FastAPI
- **AI服務**：Google Gemini AI
- **語音服務**：Google Cloud TTS、Google Cloud Speech-to-Text
- **通信**：WebSocket、RESTful API

主要服務模組：
- **WebSocket服務**：處理前端連接和即時通信
- **AI對話服務**：生成對話回應
- **語音處理服務**：語音轉文字和文字轉語音
- **情緒分析服務**：分析文本情緒並生成表情
- **動畫服務**：生成唇型同步和表情過渡

## 核心功能

- **3D模型渲染與控制**：顯示和控制3D宇航員模型
- **實時對話**：支持文本和語音輸入，生成AI回應
- **唇型同步**：根據語音自動生成口型動畫
- **情緒表情**：基於對話內容分析情緒，生成相應表情
- **平滑動畫**：實現表情和唇型的平滑過渡

## 技術亮點

1. **模塊化架構**：採用服務單例模式，實現關注點分離
2. **高效WebSocket通信**：實現消息防抖和節流處理
3. **性能優化**：
   - 高頻消息防抖處理
   - 日誌採樣機制
   - 變更檢測避免不必要更新
4. **錯誤恢復機制**：
   - 自動重連機制
   - 口型動畫備份系統

## 安裝與運行

1. 克隆倉庫
```bash
git clone [repository-url]
cd [repository-name]
```

2. 安裝依賴
```bash
npm install
```

3. 啟動開發服務器
```bash
npm run dev
```

## 未來改進計劃

- **強化後端服務可靠性**：實現服務降級和備選服務機制
- **擴展表情與動畫系統**：添加複合情緒和個性表達
- **增強對話上下文管理**：實現對話歷史和用戶偏好記憶
- **實現離線與低延遲功能**：本地模型緩存和預加載
- **多角色支持**：支持多個虛擬角色切換
- **多模態交互**：增加更多交互方式如圖像和手勢識別

## 貢獻指南

我們歡迎所有形式的貢獻，包括bug報告、功能建議或代碼貢獻。請參考以下步驟：

1. Fork該倉庫
2. 創建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打開Pull Request 