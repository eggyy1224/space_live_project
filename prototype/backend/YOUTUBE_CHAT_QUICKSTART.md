# YouTube 聊天室監控功能 - 快速開始指南

## 🚀 功能概述

這個新功能讓您可以即時監控 YouTube 直播聊天室的訊息，完美整合到現有的 perception 模組中。

## 📋 前置需求

1. 確保後端服務正在運行
2. 安裝新的依賴包：`pytchat==0.5.5`
3. 有一個正在直播的 YouTube 頻道

## 🎯 您的直播頻道

**直播 URL**: https://youtube.com/live/vs4gTWg5pGk
**頻道 ID**: UCV60MYR7dQJM8TqY5eXb7YA

## 🆕 新功能：智能頻道監控

現在您可以使用頻道 ID 直接開始監控，系統會自動：
- 🔍 檢測當前正在進行的直播
- 🎯 自動提取 video ID
- 🚀 立即開始聊天室監控

**再也不用手動複製直播網址了！** 🎉

## 🛠️ 安裝步驟

### 1. 安裝依賴
```bash
cd prototype/backend
pip install pytchat==0.5.5
# 或者重新安裝所有依賴
pip install -r requirements.txt
```

### 2. 啟動後端服務
```bash
cd prototype/backend
python main.py
```

### 3. 測試功能
```bash
python test_youtube_chat_monitor.py
```

## 🎮 基本使用

### 1. 開始監控（推薦方法 ⭐）
```bash
# 使用頻道 ID - 自動獲取當前直播
curl -X POST "http://localhost:8000/api/perception/youtube-chat/start-by-channel" \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "UCV60MYR7dQJM8TqY5eXb7YA"}'
```

### 1.1 開始監控（傳統方法）
```bash
# 使用具體的直播網址
curl -X POST "http://localhost:8000/api/perception/youtube-chat/start" \
  -H "Content-Type: application/json" \
  -d '{"video_url_or_id": "https://youtube.com/live/vs4gTWg5pGk"}'
```

### 2. 查詢狀態
```bash
curl -X GET "http://localhost:8000/api/perception/youtube-chat/status"
```

### 3. 取得最新訊息
```bash
curl -X GET "http://localhost:8000/api/perception/youtube-chat/messages?limit=10"
```

### 4. 停止監控
```bash
curl -X POST "http://localhost:8000/api/perception/youtube-chat/stop"
```

## 🔧 API 端點列表

| 方法 | 路徑 | 功能 |
|------|------|------|
| POST | `/api/perception/youtube-chat/start-by-channel` ⭐ | **開始監控聊天室（頻道 ID）** |
| POST | `/api/perception/youtube-chat/start` | 開始監控聊天室（直播網址） |
| POST | `/api/perception/youtube-chat/stop` | 停止監控聊天室 |
| GET | `/api/perception/youtube-chat/status` | 查詢監控狀態 |
| GET | `/api/perception/youtube-chat/messages` | 取得最近訊息 |
| POST | `/api/perception/youtube-chat/search` | 搜尋特定關鍵字 |
| POST | `/api/perception/youtube-chat/user-messages` | 取得特定使用者訊息 |
| DELETE | `/api/perception/youtube-chat/clear` | 清空訊息緩衝區 |

## 📊 訊息格式

每條聊天訊息包含以下資訊：
```json
{
  "id": "訊息ID",
  "author": "作者名稱",
  "message": "訊息內容",
  "timestamp": "時間戳記",
  "datetime": "格式化時間",
  "message_type": "訊息類型",
  "is_verified": "是否為認證用戶",
  "is_owner": "是否為頻道擁有者",
  "is_sponsor": "是否為贊助者",
  "is_moderator": "是否為管理員"
}
```

## 🎯 實際應用場景

1. **即時互動**: 監控觀眾聊天，讓 AI 角色即時回應
2. **情緒分析**: 分析聊天室氛圍，調整表演內容
3. **關鍵字觸發**: 特定關鍵字觸發特殊動作或回應
4. **統計分析**: 分析觀眾參與度和興趣點

## 🔍 進階功能

### 搜尋特定內容
```python
import requests

search_data = {
    "keyword": "太空",
    "limit": 20
}

response = requests.post(
    "http://localhost:8000/api/perception/youtube-chat/search",
    json=search_data
)
```

### 監控特定使用者
```python
user_data = {
    "username": "太空愛好者",
    "limit": 10
}

response = requests.post(
    "http://localhost:8000/api/perception/youtube-chat/user-messages",
    json=user_data
)
```

## 🚨 注意事項

1. **網路連線**: 需要穩定的網路連線
2. **直播狀態**: 只能監控正在進行的公開直播
3. **訊息緩衝**: 預設保留最近 100 條訊息
4. **資源使用**: 監控會佔用一定的 CPU 和記憶體資源

## 🐛 常見問題

### Q: 無法開始監控
**A**: 檢查直播是否正在進行，確認 URL 正確

### Q: 收不到訊息
**A**: 確認聊天室有人在說話，且聊天功能已開啟

### Q: 監控突然停止
**A**: 可能是網路問題或直播結束，檢查狀態並重新開始

## 📈 效能優化建議

1. 適當設定 `limit` 參數避免過多資料
2. 定期清空訊息緩衝區釋放記憶體
3. 監控時避免頻繁查詢狀態

## 🎉 開始使用

現在您可以開始使用這個強大的 YouTube 聊天室監控功能了！

1. 確保您的直播正在進行
2. 執行測試腳本驗證功能
3. 整合到您的 AI 角色互動邏輯中

**祝您使用愉快！** 🎊