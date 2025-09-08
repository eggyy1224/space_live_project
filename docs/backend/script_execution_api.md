# 🎬 虛擬太空人腳本執行 API 使用指南

虛擬太空人腳本執行 API 讓您能夠執行預定義的 bash 腳本來編排複雜的虛擬太空人表演。這些腳本將多個 API 調用組合成精心編排的序列，創造出完整的戲劇表演。

## 📋 目錄
- [API 概覽](#api-概覽)
- [可用腳本](#可用腳本)
- [基本使用方法](#基本使用方法)
- [高級功能](#高級功能)
- [安全性考量](#安全性考量)
- [故障排除](#故障排除)
- [最佳實踐](#最佳實踐)

## 🌟 API 概覽

腳本執行 API 提供以下端點：

| 端點 | 方法 | 描述 |
|------|------|------|
| `/api/scripts/list` | GET | 列出所有可用腳本 |
| `/api/scripts/execute` | POST | 執行指定腳本 |
| `/api/scripts/status` | GET | 查看執行狀態 |
| `/api/scripts/stop/{script_name}` | POST | 停止執行中的腳本 |
| `/api/scripts/execute/random-yoga` | POST | 隨機執行瑜伽腳本，支援 `count` 參數 |

## 🎭 可用腳本

目前註冊的腳本（位於 `prototype/backend/experiment_scripts/`）：

### 1. `meta_self.sh` - 《伊始之眼：一個導演的誕生》
- **描述**: 元戲劇腳本，講述 AI 導演自我形成的故事
- **時長**: 約 15-20 分鐘
- **特色**: 多幕劇結構，包含複雜的情感軌跡和鏡頭運動
- **適用場景**: 完整表演、概念展示

### 2. `remix_scene.sh` - 音樂與場景混合劇本
- **描述**: 音樂導向的場景組合表演
- **時長**: 約 10-15 分鐘
- **特色**: 重音樂編排，多種場景切換
- **適用場景**: 音樂表演、氛圍營造

### 3. `space_story_script.sh` - 太空故事腳本
- **描述**: 太空主題的敘事表演
- **時長**: 約 12-18 分鐘
- **特色**: 太空環境設定，探險主題
- **適用場景**: 主題表演、故事敘述

### 4. `news_broadcast.sh` - 新聞播報劇本
- **描述**: 新聞主播風格的表演
- **時長**: 約 8-12 分鐘
- **特色**: 正式播報風格，資訊傳達
- **適用場景**: 資訊播報、正式場合

## 🚀 基本使用方法

### 1. 查看可用腳本
```bash
curl -X GET "http://localhost:8000/api/scripts/list"
```

**回應範例:**
```json
{
  "registered_scripts": [
    {
      "name": "meta_self.sh",
      "description": "《伊始之眼：一個導演的誕生》元戲劇腳本",
      "exists": true,
      "is_running": false
    },
    {
      "name": "remix_scene.sh",
      "description": "音樂與場景混合劇本",
      "exists": true,
      "is_running": false
    }
  ],
  "total_count": 4,
  "running_count": 0
}
```

### 2. 執行腳本（推薦：背景模式）
```bash
curl -X POST "http://localhost:8000/api/scripts/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "meta_self.sh",
    "background": true,
    "args": ["--foo", "bar"]
  }'
```

其中 `args` 陣列為可選，用於向腳本傳遞參數。

**回應範例:**
```json
{
  "success": true,
  "message": "腳本 'meta_self.sh' 已開始在背景執行",
  "script_name": "meta_self.sh",
  "execution_mode": "background"
}
```

### 3. 查看執行狀態
```bash
curl -X GET "http://localhost:8000/api/scripts/status"
```

**回應範例:**
```json
{
  "running_scripts": ["meta_self.sh"],
  "total_running": 1
}
```

### 4. 停止執行中的腳本
```bash
curl -X POST "http://localhost:8000/api/scripts/stop/meta_self.sh"
```

### 5. 隨機播放瑜伽腳本
```bash
curl -X POST "http://localhost:8000/api/scripts/execute/random-yoga" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 3
  }'
```

上述範例將呼叫 `run_yoga_random_playlist.sh` 並播放 3 個隨機瑜伽腳本。

**回應範例:**
```json
{
  "success": true,
  "message": "腳本 'meta_self.sh' 已成功停止",
  "script_name": "meta_self.sh"
}
```

## 🔧 高級功能

### 同步執行模式
對於較短的腳本，您可以使用同步模式等待完成：

```bash
curl -X POST "http://localhost:8000/api/scripts/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "news_broadcast.sh",
    "background": false
  }'
```

**注意**: 同步模式會等待腳本完全執行完畢才返回回應，適用於較短的腳本。

### 腳本執行流程
1. **安全檢查**: 驗證腳本是否在註冊列表中
2. **文件檢查**: 確認腳本文件存在
3. **狀態檢查**: 確保腳本未在執行中
4. **權限設定**: 自動設定腳本為可執行（`chmod 755`）
5. **進程啟動**: 在適當的工作目錄中啟動 bash 進程
6. **狀態追蹤**: 記錄執行狀態供後續查詢

## 🔒 安全性考量

### 白名單機制
- 只有在 `REGISTERED_SCRIPTS` 列表中的腳本才能執行
- 防止任意代碼執行攻擊
- 新腳本需要手動添加到註冊列表

### 進程隔離
- 每個腳本在獨立的 bash 進程中執行
- 設定適當的工作目錄（`experiment_scripts/`）
- 自動進程清理和垃圾回收

### 資源管理
- 同時執行的腳本數量監控
- 優雅終止機制（SIGTERM -> SIGKILL）
- 防止殭屍進程產生

## 🛠️ 故障排除

### 常見問題及解決方案

#### 1. 腳本執行失敗
**症狀**: API 返回 500 錯誤或腳本狀態顯示失敗

**可能原因**:
- 腳本語法錯誤
- 缺少依賴的音檔或影片
- 網路連接問題（API 調用失敗）

**解決方案**:
```bash
# 檢查後端日誌
cd prototype/backend
tail -f logs/app.log

# 手動測試腳本
cd prototype/backend/experiment_scripts
bash meta_self.sh
```

#### 2. 腳本未註冊錯誤
**症狀**: `400 Bad Request` - 腳本未註冊

**解決方案**:
1. 確認腳本名稱正確（區分大小寫）
2. 檢查 `api/endpoints/scripts.py` 中的 `REGISTERED_SCRIPTS` 列表
3. 如需添加新腳本，請更新註冊列表

#### 3. 腳本已在執行中
**症狀**: `409 Conflict` - 腳本正在執行中

**解決方案**:
```bash
# 停止執行中的腳本
curl -X POST "http://localhost:8000/api/scripts/stop/meta_self.sh"

# 或等待腳本自然完成
curl -X GET "http://localhost:8000/api/scripts/status"
```

#### 4. 腳本文件不存在
**症狀**: `404 Not Found` - 腳本文件不存在

**解決方案**:
1. 確認腳本文件在 `prototype/backend/experiment_scripts/` 目錄中
2. 檢查文件權限是否正確
3. 確認文件名與註冊列表中的名稱完全匹配

### 日誌診斷

腳本執行相關的日誌會記錄在：
- **應用日誌**: `prototype/backend/logs/app.log`
- **控制台輸出**: 執行後端時的即時輸出

**重要日誌關鍵字**:
- `準備執行腳本`: 腳本開始執行
- `腳本執行完成`: 腳本成功完成
- `腳本執行失敗`: 腳本執行錯誤
- `背景執行腳本`: 背景模式相關

## 💡 最佳實踐

### 1. 選擇適當的執行模式
- **背景模式（推薦）**: 適用於長時間的完整表演
- **同步模式**: 僅適用於短時間腳本或需要立即回饋的場景

### 2. 執行前檢查
```bash
# 建議的執行流程
# 1. 列出可用腳本
curl -X GET "http://localhost:8000/api/scripts/list"

# 2. 檢查當前狀態
curl -X GET "http://localhost:8000/api/scripts/status"

# 3. 執行腳本
curl -X POST "http://localhost:8000/api/scripts/execute" \
  -H "Content-Type: application/json" \
  -d '{"script_name": "meta_self.sh", "background": true}'

# 4. 定期檢查狀態
curl -X GET "http://localhost:8000/api/scripts/status"
```

### 3. 資源管理
- 避免同時執行多個長時間腳本
- 完成後適時停止不需要的腳本
- 定期檢查執行狀態避免遺留進程

### 4. 腳本開發建議
如果您需要開發新腳本：

1. **遵循現有格式**: 參考 `meta_self.sh` 的結構
2. **添加描述註釋**: 在腳本開頭添加描述性註釋
3. **錯誤處理**: 添加適當的錯誤檢查
4. **測試**: 手動測試腳本後再註冊
5. **註冊**: 在 `REGISTERED_SCRIPTS` 列表中添加新腳本

### 5. 監控和維護
- 定期檢查腳本執行日誌
- 監控系統資源使用情況
- 及時清理失敗的進程
- 保持腳本和依賴資源的同步更新

## 🔗 相關文檔

- [API 控制回應指南](./cursor_api_control_response_guidelines.md) - 完整的 API 使用指南
- [即時情感整合](./realtime_emotion_integration.md) - 情感控制相關
- [圖像生成 API](./image_generation_api.md) - 圖像生成功能
- [鏡頭控制 API](./camera_control_api.md) - 鏡頭運動控制

---

**最後更新**: 2024年12月
**版本**: v1.0
**維護者**: 虛擬太空人開發團隊 