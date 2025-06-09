# Image Generation API

利用 Gemini 模型產生圖像並透過 WebSocket 廣播結果。

## 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
|`POST`|`/api/generate-image`|根據描述產生圖像，回傳圖片 URL 並廣播|

`aspect_ratio` 可選值：

- `square` - 1:1 正方形
- `portrait` - 3:4 直向
- `landscape` - 4:3 橫向

### 請求格式

```json
{
  "description": "一段描述文字",
  "duration": 5.0,
 "aspect_ratio": "square"
}
```

### 回應範例

```json
{
  "success": true,
  "url": "/generated-images/image_1700000000000.png",
  "duration": 5.0,
 "aspect_ratio": "square"
}
```

產生的圖片會儲存在 `prototype/backend/generated_images/` 目錄，檔名以時間戳記為基礎。前端會收到 `generated-image` 類型的 WebSocket 訊息，內容包含圖片路徑、`duration` 與 `aspect_ratio`。
