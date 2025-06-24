# 太空直播系統 MCP 服務器

這是一個為太空直播系統設計的 Model Context Protocol (MCP) 服務器，讓你可以直接在 Cursor 中與 AI 太空人角色互動。

## 功能

- 🚀 **send_message**: 向太空站發送訊息，讓 AI 角色說話
- 🔗 **即時連接**: 直接與後端系統通信
- 📡 **WebSocket 廣播**: 訊息會即時傳送到前端顯示

## 安裝和設定

### 1. 安裝依賴

```bash
cd prototype/backend
pip install mcp
```

### 2. 確認後端服務器運行

```bash
cd prototype/backend
python main.py
```

後端應該在 `http://localhost:8000` 運行。

### 3. 檢查 MCP 服務器

```bash
cd prototype/backend
# 檢查 MCP 服務器工具和生成報告
source venv/bin/activate
fastmcp inspect mcp_server/main.py -o mcp_server/server-info.json
```

### 4. 啟動 MCP 服務器

```bash
cd prototype/backend
python mcp_server/main.py
```

## Cursor 配置

在 Cursor 的 `settings.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "space_live": {
      "command": "python3",
      "args": ["prototype/backend/mcp_server/main.py"],
      "cwd": "/Volumes/2024data/space_live_project"
    }
  }
}
```

## 使用方法

1. 在 Cursor 中，確保 MCP 服務器已連接
2. 使用 `send_message` 工具：

```
請使用 send_message 工具讓太空人說："歡迎來到太空站！"
```

## 工具說明

### send_message

**功能**: 向太空直播系統發送訊息，讓 AI 角色說話

**參數**:
- `content` (必填): 要說的內容
- `message_type` (選填): 訊息類型，預設為 "chat-message"

**範例**:
```python
send_message(
    content="大家好，我是太空站的 AI 助手！", 
    message_type="chat-message"
)
```

## 故障排除

### 連接問題

1. **無法連接後端**
   - 確認後端服務器在 `localhost:8000` 運行
   - 檢查防火牆設定

2. **MCP 服務器無法啟動**
   - 確認已安裝 `mcp` 套件
   - 檢查 Python 環境

3. **Cursor 無法連接**
   - 確認 `settings.json` 配置正確
   - 檢查檔案路徑是否正確

### 測試指令

```bash
# 測試後端連接
curl http://localhost:8000/api/health

# 測試 send_message API
curl -X POST http://localhost:8000/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "測試訊息", "message_type": "chat-message"}'
```

## 下一步擴展

準備添加更多工具：
- 🎭 情緒控制工具
- 🎥 相機視角控制
- 🎵 音頻播放控制
- 🎨 場景切換工具

## 開發者說明

- 主要檔案: `main.py` - MCP 服務器主程式
- 測試檔案: `test_mcp.py` - 連接測試工具
- 設定檔案: `README.md` - 使用說明 