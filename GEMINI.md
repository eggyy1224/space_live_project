# Space Live Project - Gemini CLI 整合記錄

## 資源管理 API 開發 (2024-01-XX)

### 新增功能

#### 1. 後端資源查詢 API 端點 (`/api/resources/*`)

創建了完整的媒體資源查詢 API，包含以下端點：

- `GET /api/resources/songs` - 查詢後端歌曲目錄
- `GET /api/resources/bgm` - 查詢前端背景音樂目錄  
- `GET /api/resources/effects` - 查詢前端音效目錄
- `GET /api/resources/videos` - 查詢前端影片目錄
- `GET /api/resources/animations` - 查詢前端動畫目錄
- `GET /api/resources/all` - 查詢所有資源總覽
- `GET /api/resources/search` - 搜索媒體資源
- `GET /api/resources/config` - 查詢前端資源配置

#### 2. MCP 工具函數

在 MCP 伺服器中新增了以下工具：

- `get_available_songs()` - 取得所有歌曲檔案
- `get_available_bgm()` - 取得所有背景音樂檔案
- `get_available_effects()` - 取得所有音效檔案
- `get_available_videos()` - 取得所有影片檔案
- `get_available_animations()` - 取得所有動畫檔案
- `get_all_resources()` - 取得資源總覽統計
- `search_resources(query, resource_type, limit)` - 搜索媒體資源

### 技術實現

#### 後端架構
- 使用 FastAPI Router 模式
- 支援多種檔案格式 (音訊、影片、動畫、圖像)
- 自動掃描目錄並提供檔案資訊 (檔名、大小、路徑等)
- 完整的錯誤處理和異常捕獲

#### MCP 整合
- 所有工具都提供中文回應
- 統一的錯誤處理和連線檢查
- 友善的輸出格式，包含檔案統計和清單

### 目錄結構對應

```
prototype/backend/songs/              -> /api/resources/songs
prototype/frontend/public/audio/BGM/  -> /api/resources/bgm  
prototype/frontend/public/audio/effects/ -> /api/resources/effects
prototype/frontend/public/videos/     -> /api/resources/videos
prototype/frontend/public/animations/ -> /api/resources/animations
```

### 使用場景

這些 API 和 MCP 工具主要用於：

1. **Gemini CLI 查詢資源** - 讓 AI 助手能夠了解系統中有哪些可用的媒體檔案
2. **動態內容生成** - 根據可用資源動態產生表演腳本
3. **資源驗證** - 在使用音樂、音效、影片前確認檔案存在
4. **開發輔助** - 開發者可以快速查看和搜索專案中的媒體資源

### 後續計畫

- [ ] 添加檔案預覽功能
- [ ] 實現資源標籤和分類管理
- [ ] 整合前端資源配置的動態更新
- [ ] 添加資源使用統計和分析

---

## 注意事項

- 確保後端服務器在 `http://localhost:8000` 運行
- MCP 工具需要後端 API 服務正常運作
- 大型媒體檔案的掃描可能需要較長時間 