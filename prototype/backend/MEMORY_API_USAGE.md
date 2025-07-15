# 記憶系統 API 使用說明

## 概述

本專案新增了記憶系統 API，讓您可以直接操作 AI 角色的記憶資料。這些 API 已經整合到後端服務器中，並透過 MCP (Model Context Protocol) 提供給 MCP 客戶端使用。

## API 端點

### 1. 儲存記憶 - `POST /api/memory/save`

儲存新的記憶到指定的記憶庫中。

**請求格式：**
```json
{
  "memory_type": "conversation|persona|summary",
  "content": "記憶內容",
  "metadata": {
    "type": "記憶類型",
    "category": "分類",
    "其他自定義欄位": "值"
  }
}
```

**回應格式：**
```json
{
  "success": true,
  "message": "成功儲存 persona 記憶",
  "data": {
    "memory_type": "persona",
    "content_length": 25
  }
}
```

**範例：**
```bash
curl -X POST http://localhost:8000/api/memory/save \
  -H "Content-Type: application/json" \
  -d '{
    "memory_type": "persona",
    "content": "我喜歡在太空中觀察星星",
    "metadata": {
      "type": "learned_preference",
      "category": "hobby"
    }
  }'
```

### 2. 獲取記憶 - `POST /api/memory/get`

從指定的記憶庫中獲取記憶資料。

**請求格式：**
```json
{
  "memory_type": "conversation|persona|summary",
  "query": "搜尋關鍵字（可選）",
  "limit": 10,
  "include_metadata": true
}
```

**回應格式：**
```json
{
  "success": true,
  "message": "成功獲取 5 條 persona 記憶",
  "data": {
    "memories": [
      {
        "id": "記憶ID",
        "content": "記憶內容",
        "metadata": {
          "type": "core_identity",
          "timestamp": 1641234567.89
        }
      }
    ]
  },
  "count": 5
}
```

**範例：**
```bash
# 獲取所有人格記憶
curl -X POST http://localhost:8000/api/memory/get \
  -H "Content-Type: application/json" \
  -d '{
    "memory_type": "persona",
    "limit": 10
  }'

# 語義搜尋
curl -X POST http://localhost:8000/api/memory/get \
  -H "Content-Type: application/json" \
  -d '{
    "memory_type": "persona",
    "query": "太空 星星",
    "limit": 5
  }'
```

### 3. 記憶統計 - `GET /api/memory/stats`

獲取記憶系統的統計資訊。

**回應格式：**
```json
{
  "success": true,
  "message": "成功獲取記憶系統統計資訊",
  "data": {
    "stats": {
      "conversation": {
        "count": 150,
        "status": "active"
      },
      "persona": {
        "count": 12,
        "status": "active"
      },
      "summary": {
        "count": 8,
        "status": "active"
      }
    }
  }
}
```

**範例：**
```bash
curl -X GET http://localhost:8000/api/memory/stats
```

## 記憶類型說明

### 1. `conversation` - 對話記憶
- **用途**: 儲存用戶與 AI 的對話記錄
- **格式**: `input: 用戶輸入\noutput: AI回應`
- **生命週期**: 約 30 天後會被清理，但會保留摘要

### 2. `persona` - 人格記憶
- **用途**: 儲存 AI 角色的人格特質和偏好
- **格式**: 自然語言描述
- **生命週期**: 永久保存

### 3. `summary` - 摘要記憶
- **用途**: 儲存對話的摘要和重要事件
- **格式**: 經過 LLM 處理的摘要文本
- **生命週期**: 永久保存

## MCP 工具

透過 MCP 服務器，您可以使用以下工具：

### 1. `get_memory`
```python
get_memory(
    memory_type="persona",
    query="太空 星星",  # 可選
    limit=10,
    include_metadata=True
)
```

### 2. `save_memory`
```python
save_memory(
    memory_type="persona",
    content="我喜歡觀察星星",
    metadata={"type": "hobby"}  # 可選
)
```

### 3. `get_memory_stats`
```python
get_memory_stats()
```

## 使用步驟

### 1. 啟動後端服務器
```bash
cd prototype/backend
source venv/bin/activate  # 啟用虛擬環境
python main.py
```

### 2. 測試 API
```bash
# 執行測試腳本
python test_memory_api.py
```

### 3. 使用 MCP 工具
```bash
# 啟動 MCP 服務器
python mcp_server/main.py
```

然後在支援 MCP 的客戶端中使用相關工具。

## 注意事項

1. **權限**: 目前 API 沒有身份驗證，請在生產環境中添加適當的安全措施。

2. **效能**: 語義搜尋可能需要較長時間，特別是在大量記憶的情況下。

3. **資料格式**: 記憶內容建議使用 UTF-8 編碼的文本。

4. **錯誤處理**: API 會返回詳細的錯誤訊息，請根據 `success` 欄位判斷操作是否成功。

5. **記憶庫初始化**: 首次使用時，系統會自動初始化核心人格記憶。

## 故障排除

### 常見問題

1. **連接錯誤**: 確認後端服務器是否在 `http://localhost:8000` 運行
2. **記憶庫為空**: 首次使用時是正常的，系統會自動初始化
3. **搜尋無結果**: 嘗試使用更廣泛的關鍵字或檢查記憶類型是否正確

### 除錯方法

1. 檢查後端日誌：
```bash
tail -f prototype/backend/logs/app.log
```

2. 使用測試腳本驗證功能：
```bash
python test_memory_api.py
```

3. 直接查看資料庫內容（開發用）：
```bash
# 需要先安裝 chromadb
pip install chromadb
python -c "
import chromadb
client = chromadb.PersistentClient(path='data/chroma_db/persona_memory')
collection = client.get_collection('persona_info')
print(collection.get())
"
``` 