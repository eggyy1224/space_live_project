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

## 安裝與設定

### 1. 安裝依賴套件

```bash
cd prototype/backend
pip install -r requirements.txt
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
```

## 測試

使用提供的測試腳本來驗證功能：

```bash
cd prototype/backend
python test_obs_perception.py
```

確保測試前：
1. OBS Studio 已開啟
2. WebSocket 服務已啟用
3. 後端服務已啟動

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

## 技術架構

```
Perception 模組
├── services/perception/
│   ├── __init__.py          # 模組初始化
│   ├── obs_screenshot.py    # OBS 截圖服務
│   └── README.md           # 使用說明
├── api/endpoints/
│   └── perception.py       # API 端點
├── dtos/
│   ├── requests.py         # 請求模型
│   └── responses.py        # 回應模型
└── screenshots/            # 截圖存放目錄
```

## 相關連結

- [OBS WebSocket API 文檔](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md)
- [obsws-python SDK](https://github.com/aatikturk/obsws-python)
- [FastAPI 文檔](https://fastapi.tiangolo.com/) 