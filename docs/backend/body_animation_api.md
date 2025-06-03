# Body Animation Control API

後端提供此 API 以即時控制前端舞者動畫，包含單一動畫或動畫序列的播放、暫停與停止。

## 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
|`POST`|`/api/control/body-animation`|傳送舞者動畫指令|

### 請求範例
```bash
curl -X POST http://localhost:8000/api/control/body-animation \
  -H 'Content-Type: application/json' \
  -d '{
    "state": "play",
    "animation": "HipHopDance",
    "loop": true,
    "transitionDuration": 0.5
  }'
```

### 參數說明
- `state`：`play`、`pause`、`resume`、`stop` 之一。
- `animation`：欲播放的單一動畫名稱。
- `sequence`：若需播放多段動畫，提供 `{name, proportion}` 陣列。
- `loop`：是否循環播放。
- `loopCount`：循環次數，`null` 代表無限循環。
- `speed`：播放速度倍率。
- `transitionDuration`：動畫切換的淡入淡出時間（秒）。

### 回應
成功時回傳：
```json
{ "success": true }
```
