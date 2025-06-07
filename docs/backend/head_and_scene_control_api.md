# Head Size & Scene Control API

提供控制頭部模型縮放與房間場景顯示的後端端點，方便前端在運行時調整虛擬環境。

## 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
|`POST`|`/api/control/head-size`|調整前端頭部模型的縮放比|
|`POST`|`/api/control/scene-display`|切換或顯示/隱藏指定場景|

### `/api/control/head-size`

- `scaleFactor`：`0.1` 至 `5.0` 的數值，表示模型縮放倍數。

```bash
curl -X POST http://localhost:8000/api/control/head-size \
  -H 'Content-Type: application/json' \
  -d '{"scaleFactor": 1.5}'
```

### `/api/control/scene-display`

- `displayScene`：布林值，是否顯示房間場景。
- `sceneName`：可選，指定要載入的場景 ID（如 `room-a` 或 `room-b`）。

```bash
curl -X POST http://localhost:8000/api/control/scene-display \
  -H 'Content-Type: application/json' \
  -d '{"displayScene": true, "sceneName": "room-a"}'
```

無效縮放值將回傳 `400 Bad Request`，未知場景名稱則回傳 `404 Not Found`。
