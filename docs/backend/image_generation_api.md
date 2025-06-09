# Image Generation & Display API

利用 Gemini 模型產生圖像或顯示現有圖像，並透過 WebSocket 廣播結果。

## 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
|`POST`|`/api/generate-image`|根據描述產生圖像，回傳圖片 URL 並廣播|
|`POST`|`/api/show-existing-image`|顯示已存在的圖像，支援所有顯示配置選項|

`aspect_ratio` 可選值（傳遞給 Gemini API 決定產生的圖片比例）：

- `square` - 1:1 正方形
- `portrait` - 3:4 直向
- `landscape` - 4:3 橫向

## 1. 圖像生成 `/api/generate-image`

### 請求格式

```json
{
  "description": "一段描述文字",
  "position": "center",
  "size": "large",
  "duration": 10.0,
  "aspect_ratio": "square",
  "custom_position": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
  "custom_size": {"width": "450px", "height": "360px"}
}
```

### 回應範例

```json
{
  "success": true,
  "url": "/generated-images/image_1700000000000.png",
  "caption": "AI 生成的圖像描述文字",
  "display_config": {
    "position": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
    "size": {"width": "450px", "height": "360px"}
  },
  "duration": 10.0,
  "aspect_ratio": "square"
}
```

## 2. 顯示現有圖像 `/api/show-existing-image`

### 請求格式

```json
{
  "filename": "image_1749309153863.png",
  "caption": "自定義說明文字",
  "position": "center",
  "size": "large",
  "duration": 15.0,
  "aspect_ratio": "landscape",
  "custom_position": {"top": "30%", "left": "25%"},
  "custom_size": {"width": "500px", "height": "400px"}
}
```

### 回應範例

```json
{
  "success": true,
  "url": "/generated-images/image_1749309153863.png",
  "caption": "自定義說明文字",
  "display_config": {
    "position": {"top": "30%", "left": "25%"},
    "size": {"width": "500px", "height": "400px"}
  },
  "duration": 15.0,
  "aspect_ratio": "landscape"
}
```

## 顯示配置選項

### 位置預設 (position)
- `center` - 螢幕中央 (預設)
- `center-right` - 右邊中央  
- `center-left` - 左邊中央
- `top-right` - 右上角
- `top-left` - 左上角
- `bottom-right` - 右下角
- `bottom-left` - 左下角

### 尺寸預設 (size)
- `small` - 250px × 200px
- `medium` - 350px × 280px  
- `large` - 450px × 360px (現有圖像預設)

### 自定義配置
- `custom_position` - 自定義 CSS 位置屬性，覆蓋 position 預設
- `custom_size` - 自定義 CSS 尺寸屬性，覆蓋 size 預設

## 重要特性

### 多圖同時顯示
- 前端 `ImageOverlay` 組件支援同時顯示多張圖片
- 每張圖片都有獨立的位置、尺寸和顯示時間
- **同一張圖片可以同時在不同位置顯示多次**

### 圖片存取與處理
- 產生的圖片會儲存在 `prototype/backend/generated_images/` 目錄
- 檔名格式：`image_{timestamp}.png` (例如：`image_1749309153863.png`)
- 圖片可透過 HTTP 直接存取：`http://localhost:8000/generated-images/{filename}`
- 所有圖片都會透過 WebSocket 廣播 `generated-image` 訊息給前端

### AI 圖像生成
- 後端將 `aspect_ratio` 參數直接傳遞給 Gemini 圖像生成 API
- 確保得到的圖片比例與請求一致，無需本地裁切處理
- AI 會自動生成圖片描述作為 `caption`

### 使用範例

**瘋狂顯示多張相同圖片：**
```bash
# 中央大圖
curl -X POST http://localhost:8000/api/show-existing-image \
  -H "Content-Type: application/json" \
  -d '{"filename": "image_1749309153863.png", "position": "center", "size": "large", "duration": 30.0}'

# 右上角小圖  
curl -X POST http://localhost:8000/api/show-existing-image \
  -H "Content-Type: application/json" \
  -d '{"filename": "image_1749309153863.png", "position": "top-right", "size": "small", "duration": 25.0}'

# 自定義位置和尺寸
curl -X POST http://localhost:8000/api/show-existing-image \
  -H "Content-Type: application/json" \
  -d '{"filename": "image_1749309153863.png", "custom_position": {"top": "30%", "left": "25%"}, "custom_size": {"width": "500px", "height": "400px"}, "duration": 35.0}'
```
