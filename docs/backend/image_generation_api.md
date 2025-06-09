# Image Generation & Display API

利用 Gemini 模型產生圖像或顯示現有圖像，並透過 WebSocket 廣播結果。

## 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
|`POST`|`/api/generate-image`|根據描述產生圖像，回傳圖片 URL 並廣播|
|`POST`|`/api/show-existing-image`|顯示已存在的圖像，支援所有顯示配置選項|
|`POST`|`/api/take-selfie`|拍攝自拍照，支援參考圖像和多模態 AI 生成|
|`POST`|`/api/continue-selfie`|繼續自拍（自動使用最新自拍作為參考）|

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

### 3. 自拍功能 `/api/take-selfie`

### 功能特色
- **多模態 AI 生成**：支援圖像+文字輸入，真正基於參考圖像生成新自拍
- **自動時間戳章**：在圖片右下角添加時間戳水印
- **參考圖像系統**：可指定任何現有自拍或生成圖像作為參考
- **自動最新參考**：可設定自動使用最新自拍作為參考圖像

### 請求格式

```json
{
  "description": "拍一張自拍照",
  "reference_image": "selfie_1749441340870.png",
  "modification": "換個開心的表情，但保持相似的風格和構圖",
  "use_latest_selfie": false,
  "position": "center",
  "size": "large",
  "duration": 15.0,
  "aspect_ratio": "portrait",
  "add_timestamp": true
}
```

### 回應範例

```json
{
  "success": true,
  "url": "/generated-images/selfie_1749441340870.png",
  "caption": "📸 自拍照：AI 生成的自拍描述",
  "display_config": {
    "position": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
    "size": {"width": "450px", "height": "360px"}
  },
  "duration": 15.0,
  "aspect_ratio": "portrait",
  "selfie_filename": "selfie_1749441340870.png",
  "reference_image": "202506091142.png"
}
```

## 4. 繼續自拍 `/api/continue-selfie`

### 功能特色
- **自動參考**：自動使用最新的自拍作為參考圖像
- **簡化操作**：只需提供修改指令即可快速生成新自拍
- **連續演進**：支援表情、姿勢的連續變化演進

### 請求格式

```json
{
  "modification": "變成很驚訝的表情，眼睛睜大",
  "position": "center",
  "size": "large",
  "duration": 20.0
}
```

### 回應範例

```json
{
  "success": true,
  "url": "/generated-images/selfie_1749441363180.png",
  "caption": "📸 自拍照：",
  "display_config": {
    "position": {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
    "size": {"width": "450px", "height": "360px"}
  },
  "duration": 20.0,
  "aspect_ratio": "portrait",
  "selfie_filename": "selfie_1749441363180.png",
  "reference_image": "selfie_1749441340870.png"
}
```

## 自拍系統特性

### 時間戳章功能
- **自動添加**：預設在圖片右下角添加時間戳水印
- **格式**：`YYYY/MM/DD HH:MM:SS` (例如：`2025/06/09 14:32:18`)
- **樣式**：白色文字，黑色半透明背景
- **控制**：可透過 `add_timestamp: false` 關閉

### 多模態參考系統
- **真正視覺參考**：Gemini AI 可「看到」參考圖像，基於視覺內容生成新自拍
- **參考圖像來源**：支援 `selfies/` 和 `generated_images/` 目錄中的圖像
- **自動最新參考**：`use_latest_selfie: true` 自動選擇最新自拍
- **錯誤回退**：如果多模態輸入失敗，自動回退到純文字生成

### 自拍演進序列
- **連續性**：每次「繼續自拍」都基於前一張的實際視覺內容
- **構圖保持**：保持相似的角度和構圖，但允許表情、姿勢變化
- **表情演進**：支援豐富的表情變化指令

### 檔案系統
- **儲存位置**：`prototype/backend/selfies/` (源檔案)
- **前端存取**：`prototype/backend/generated_images/` (複製供前端存取)
- **檔名格式**：`selfie_{timestamp}.png` (例如：`selfie_1749441340870.png`)

## 使用範例

**基本自拍生成：**
```bash
curl -X POST http://localhost:8000/api/take-selfie \
  -H "Content-Type: application/json" \
  -d '{"description": "拍一張自拍照", "position": "center", "size": "large", "duration": 25.0}'
```

**基於參考圖像的自拍：**
```bash
curl -X POST http://localhost:8000/api/take-selfie \
  -H "Content-Type: application/json" \
  -d '{"description": "拍一張自拍照", "reference_image": "202506091142.png", "modification": "換個開心的表情", "add_timestamp": true}'
```

**快速繼續自拍：**
```bash
curl -X POST http://localhost:8000/api/continue-selfie \
  -H "Content-Type: application/json" \
  -d '{"modification": "變成很酷的表情，眉毛挑高一點", "duration": 20.0}'
```

**連續自拍演進序列：**
```bash
# 第一張：基於參考圖像
curl -X POST http://localhost:8000/api/take-selfie \
  -H "Content-Type: application/json" \
  -d '{"reference_image": "202506091142.png", "modification": "開心笑容"}'

# 第二張：基於第一張
curl -X POST http://localhost:8000/api/continue-selfie \
  -H "Content-Type: application/json" \
  -d '{"modification": "酷的表情"}'

# 第三張：基於第二張
curl -X POST http://localhost:8000/api/continue-selfie \
  -H "Content-Type: application/json" \
  -d '{"modification": "驚訝表情"}'
```

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
