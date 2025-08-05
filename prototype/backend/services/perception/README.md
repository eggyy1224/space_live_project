# Perception 模組

Perception 模組是用於偵測和感知現在即時狀況的系統，目前包含 OBS 畫面截圖功能。

## 功能特色

### OBS 截圖功能
- ✅ 整合 OBS WebSocket API v5
- ✅ 支援程式輸出截圖
- ✅ 支援特定來源截圖  
- ✅ 支援特定場景截圖
- ✅ 可自訂解析度和圖片格式
- ✅ 自動檔案管理和下載

### YouTube 聊天室監控功能
- ✅ 即時監控 YouTube 直播聊天室
- ✅ 自動解析 YouTube URL 或 video_id
- ✅ 訊息緩衝區管理（預設保留最近100條）
- ✅ 支援訊息搜尋和過濾
- ✅ 支援特定使用者訊息查詢
- ✅ 背景執行緒監控，不阻塞主程序
- ✅ 完整的錯誤處理和重連機制

## 安裝與設定

### 1. 安裝依賴套件

```bash
cd prototype/backend
pip install -r requirements.txt
# 新增了 pytchat==0.5.5 用於 YouTube 聊天室監控
```

### 2. OBS Studio 設定

1. 開啟 OBS Studio
2. 前往 `工具` > `WebSocket 伺服器設定`
3. 勾選 `啟用 WebSocket 伺服器`
4. 設定端口（預設 4455）
5. 設定密碼（可選）
6. 點擊 `確定`

### 3. 啟動後端服務

```bash
cd prototype/backend
python main.py
```

## API 端點

### 1. 查詢 OBS 狀態
```
GET /api/perception/obs/status
```

**回應範例:**
```json
{
  "connected": true,
  "obs_version": "30.0.2",
  "websocket_version": "5.4.4",
  "current_scene": "Scene",
  "streaming": false,
  "recording": false
}
```

### 2. 擷取截圖
```
POST /api/perception/obs/screenshot
```

**請求參數:**
```json
{
  "source_name": "可選-來源名稱",
  "scene_name": "可選-場景名稱", 
  "width": 1920,
  "height": 1080,
  "image_format": "png"
}
```

**回應範例:**
```json
{
  "success": true,
  "filename": "program_output_20241231_143022_123.png",
  "file_path": "prototype/backend/screenshots/program_output_20241231_143022_123.png",
  "file_size": 1234567,
  "timestamp": "20241231_143022_123",
  "width": 1920,
  "height": 1080,
  "format": "png",
  "source_type": "program_output",
  "source_name": "program_output"
}
```

### 3. 取得場景列表
```
GET /api/perception/obs/scenes
```

### 4. 取得來源列表
```
GET /api/perception/obs/sources
```

### 5. 下載截圖檔案
```
GET /api/perception/obs/screenshot/{filename}
```

### 6. 設定 OBS 連接
```
POST /api/perception/obs/connection
```

**請求參數:**
```json
{
  "host": "localhost",
  "port": 4455,
  "password": "",
  "timeout": 10
}
```

### 7. 中斷 OBS 連接
```
DELETE /api/perception/obs/disconnect
```

## YouTube 聊天室監控 API 端點

### 1. 開始監控聊天室（使用直播網址）
```
POST /api/perception/youtube-chat/start
```

**請求參數:**
```json
{
  "video_url_or_id": "https://youtube.com/live/vs4gTWg5pGk"
}
```

**回應範例:**
```json
{
  "success": true,
  "message": "成功開始監控 YouTube 聊天室",
  "monitoring": true,
  "video_id": "vs4gTWg5pGk"
}
```

### 1.1. 開始監控聊天室（使用頻道 ID - 自動獲取當前直播）⭐ **推薦**
```
POST /api/perception/youtube-chat/start-by-channel
```

**請求參數:**
```json
{
  "channel_id": "UCV60MYR7dQJM8TqY5eXb7YA"
}
```

**回應範例:**
```json
{
  "success": true,
  "message": "成功開始監控 YouTube 聊天室",
  "monitoring": true,
  "video_id": "o4hIfVv1vMM"
}
```

**✨ 優勢:**
- 🚀 不需要手動輸入直播網址
- 🔄 自動獲取當前正在進行的直播
- 📱 只需要記住固定的頻道 ID

### 2. 停止監控聊天室
```
POST /api/perception/youtube-chat/stop
```

**回應範例:**
```json
{
  "success": true,
  "message": "成功停止 YouTube 聊天室監控",
  "monitoring": false
}
```

### 3. 查詢監控狀態
```
GET /api/perception/youtube-chat/status
```

**回應範例:**
```json
{
  "monitoring": true,
  "video_id": "vs4gTWg5pGk",
  "message_count": 25,
  "chat_alive": true
}
```

### 4. 取得最近訊息
```
GET /api/perception/youtube-chat/messages?limit=10
```

**回應範例:**
```json
{
  "success": true,
  "count": 3,
  "messages": [
    {
      "id": "msg_123",
      "author": "太空愛好者",
      "message": "太空人好帥！",
      "timestamp": "1703123456789",
      "datetime": "2023-12-21 10:30:56",
      "message_type": "textMessage",
      "is_verified": false,
      "is_owner": false,
      "is_sponsor": true,
      "is_moderator": false
    }
  ]
}
```

### 5. 搜尋訊息
```
POST /api/perception/youtube-chat/search
```

**請求參數:**
```json
{
  "keyword": "太空",
  "limit": 20
}
```

### 6. 取得特定使用者訊息
```
POST /api/perception/youtube-chat/user-messages
```

**請求參數:**
```json
{
  "username": "太空愛好者",
  "limit": 10
}
```

### 7. 清空訊息緩衝區
```
DELETE /api/perception/youtube-chat/clear
```

## 使用範例

### Python 客戶端範例

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. 檢查 OBS 狀態
response = requests.get(f"{BASE_URL}/perception/obs/status")
print(json.dumps(response.json(), indent=2))

# 2. 擷取截圖
screenshot_request = {
    "width": 1280,
    "height": 720,
    "image_format": "png"
}

response = requests.post(
    f"{BASE_URL}/perception/obs/screenshot",
    json=screenshot_request
)

if response.status_code == 200:
    result = response.json()
    if result["success"]:
        print(f"截圖成功: {result['filename']}")
        
        # 下載截圖檔案
        download_url = f"{BASE_URL}/perception/obs/screenshot/{result['filename']}"
        file_response = requests.get(download_url)
        
        with open(f"downloaded_{result['filename']}", 'wb') as f:
            f.write(file_response.content)
        
        print("檔案下載完成")
```

### YouTube 聊天室監控範例

```python
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

# 1. 開始監控聊天室（推薦：使用頻道 ID）
channel_id = "UCV60MYR7dQJM8TqY5eXb7YA"
start_request = {"channel_id": channel_id}

response = requests.post(
    f"{BASE_URL}/perception/youtube-chat/start-by-channel",
    json=start_request
)

# 或者使用直播網址的方法：
# video_url = "https://youtube.com/live/vs4gTWg5pGk"
# start_request = {"video_url_or_id": video_url}
# response = requests.post(f"{BASE_URL}/perception/youtube-chat/start", json=start_request)

if response.status_code == 200:
    result = response.json()
    print(f"監控開始: {result['message']}")
    video_id = result['video_id']
    
    # 2. 等待一段時間累積訊息
    print("等待訊息累積...")
    time.sleep(30)
    
    # 3. 取得最近的聊天訊息
    response = requests.get(f"{BASE_URL}/perception/youtube-chat/messages?limit=5")
    if response.status_code == 200:
        messages = response.json()
        print(f"共收到 {messages['count']} 條訊息:")
        for msg in messages['messages']:
            print(f"  [{msg['author']}] {msg['message']}")
    
    # 4. 搜尋包含特定關鍵字的訊息
    search_request = {"keyword": "太空", "limit": 10}
    response = requests.post(
        f"{BASE_URL}/perception/youtube-chat/search",
        json=search_request
    )
    if response.status_code == 200:
        search_results = response.json()
        print(f"找到 {search_results['count']} 條包含 '太空' 的訊息")
    
    # 5. 停止監控
    response = requests.post(f"{BASE_URL}/perception/youtube-chat/stop")
    if response.status_code == 200:
        result = response.json()
        print(f"監控停止: {result['message']}")
```

### curl 範例

```bash
# 檢查 OBS 狀態
curl -X GET "http://localhost:8000/api/perception/obs/status"

# 擷取截圖
curl -X POST "http://localhost:8000/api/perception/obs/screenshot" \
  -H "Content-Type: application/json" \
  -d '{
    "width": 1280,
    "height": 720,
    "image_format": "png"
  }'

# 下載截圖（請替換 filename）
curl -X GET "http://localhost:8000/api/perception/obs/screenshot/program_output_20241231_143022_123.png" \
  --output screenshot.png

# YouTube 聊天室監控
# 開始監控（推薦：使用頻道 ID）
curl -X POST "http://localhost:8000/api/perception/youtube-chat/start-by-channel" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "UCV60MYR7dQJM8TqY5eXb7YA"
  }'

# 開始監控（使用直播網址）
curl -X POST "http://localhost:8000/api/perception/youtube-chat/start" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url_or_id": "https://youtube.com/live/vs4gTWg5pGk"
  }'

# 查詢狀態
curl -X GET "http://localhost:8000/api/perception/youtube-chat/status"

# 取得最近訊息
curl -X GET "http://localhost:8000/api/perception/youtube-chat/messages?limit=10"

# 搜尋訊息
curl -X POST "http://localhost:8000/api/perception/youtube-chat/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "太空",
    "limit": 20
  }'

# 停止監控
curl -X POST "http://localhost:8000/api/perception/youtube-chat/stop"
```

## 測試

使用提供的測試腳本來驗證功能：

### OBS 功能測試
```bash
cd prototype/backend
python test_obs_perception.py
```

確保測試前：
1. OBS Studio 已開啟
2. WebSocket 服務已啟用
3. 後端服務已啟動

### YouTube 聊天室監控測試
```bash
cd prototype/backend
python test_youtube_chat_monitor.py
```

確保測試前：
1. 後端服務已啟動
2. 有可用的 YouTube 直播頻道
3. 網路連線正常

## 故障排除

### 常見問題

**1. 無法連接到 OBS**
- 確認 OBS Studio 已開啟
- 檢查 WebSocket 設定是否正確啟用
- 驗證端口和密碼設定

**2. 截圖失敗**
- 確認目前有活動的場景
- 檢查來源名稱是否正確
- 查看 OBS 日誌檔案

**3. 檔案無法下載**
- 檢查檔案權限
- 確認 screenshots 目錄存在
- 驗證檔案路徑

**4. YouTube 聊天室監控失敗**
- 確認 YouTube 直播正在進行
- 檢查網路連線是否穩定
- 驗證 video_id 是否正確
- 查看是否為私人直播（無法監控）

**5. 無法取得聊天訊息**
- 確認直播有聊天功能開啟
- 檢查直播是否有觀眾在聊天
- 驗證監控狀態是否為 true

### 日誌檢查

後端日誌會記錄詳細的操作資訊：

```bash
# 查看即時日誌
tail -f prototype/backend/logs/app.log
```

## 未來功能

計劃中的功能擴展：
- [ ] 即時畫面分析
- [ ] 物件偵測
- [ ] 場景變化監控
- [ ] 自動截圖觸發
- [ ] 影片錄製片段擷取
- [x] YouTube 聊天室即時監控
- [ ] 聊天室情緒分析
- [ ] 自動回應機制
- [ ] 聊天室統計分析
- [ ] 多平台聊天室整合（Twitch、Facebook Live等）

## 技術架構

```
Perception 模組
├── services/perception/
│   ├── __init__.py               # 模組初始化
│   ├── obs_screenshot.py         # OBS 截圖服務
│   ├── vision_analysis.py        # 視覺分析服務
│   ├── youtube_chat_monitor.py   # YouTube 聊天室監控服務
│   └── README.md                # 使用說明
├── api/endpoints/
│   └── perception.py            # API 端點
├── dtos/
│   ├── requests.py              # 請求模型（包含 YouTube 聊天室相關）
│   └── responses.py             # 回應模型（包含 YouTube 聊天室相關）
├── screenshots/                 # 截圖存放目錄
└── test_youtube_chat_monitor.py # YouTube 聊天室監控測試腳本
```

## 相關連結

### OBS 相關
- [OBS WebSocket API 文檔](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md)
- [obsws-python SDK](https://github.com/aatikturk/obsws-python)

### YouTube 聊天室監控相關
- [pytchat GitHub 專案](https://github.com/taizan-hokuto/pytchat)
- [YouTube API 文檔](https://developers.google.com/youtube/v3)

### 框架相關
- [FastAPI 文檔](https://fastapi.tiangolo.com/) 