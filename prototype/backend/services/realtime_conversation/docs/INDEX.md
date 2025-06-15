# 📚 文檔索引

歡迎來到 realtime conversation 系統的文檔中心！這裡包含了所有功能模組的詳細使用說明。

## 🗂️ 文檔列表

### 🎵 音頻控制
- **[AUDIO_TOOLS_DISTINCTION.md](./AUDIO_TOOLS_DISTINCTION.md)** - 音頻工具區別說明 
- **[BGM_AUDIO_USAGE.md](./BGM_AUDIO_USAGE.md)** - 背景音樂和環境音效使用指南

### 🎭 角色控制  
- **[CHARACTER_ANIMATION_USAGE.md](./CHARACTER_ANIMATION_USAGE.md)** - 角色內建動畫控制
- **[BODY_ANIMATION_USAGE.md](./BODY_ANIMATION_USAGE.md)** - 身體動畫和舞蹈控制
- **[HEAD_SIZE_CONTROL_USAGE.md](./HEAD_SIZE_CONTROL_USAGE.md)** - 頭部大小動態調整

### 📹 視覺效果
- **[CAMERA_CONTROL_USAGE.md](./CAMERA_CONTROL_USAGE.md)** - 智能攝影機控制和鏡位設定

### 📊 系統監控
- **[WEBSOCKET_LOGGING.md](./WEBSOCKET_LOGGING.md)** - WebSocket 日誌記錄和分析系統

## 🎯 10大超能力對應

| 功能 | 工具名稱 | 文檔參考 |
|------|----------|----------|
| 🎤 角色音效唱歌 | `play_audio` | [AUDIO_TOOLS_DISTINCTION.md](./AUDIO_TOOLS_DISTINCTION.md) |
| 😊 表情動畫 | `emotion_trajectory` | 代碼中的配置 |
| 🎼 背景氛圍控制 | `background_audio` | [BGM_AUDIO_USAGE.md](./BGM_AUDIO_USAGE.md) |
| 📸 自拍功能 | `take_selfie` | 代碼中的配置 |
| 🎨 圖片生成 | `generate_image` | 代碼中的配置 |
| 📹 智能鏡位控制 | `camera_control` | [CAMERA_CONTROL_USAGE.md](./CAMERA_CONTROL_USAGE.md) |
| 📏 頭部大小控制 | `head_size_control` | [HEAD_SIZE_CONTROL_USAGE.md](./HEAD_SIZE_CONTROL_USAGE.md) |
| 🎭 角色內建動畫 | `character_animation` | [CHARACTER_ANIMATION_USAGE.md](./CHARACTER_ANIMATION_USAGE.md) |
| 🎭 智能角色縮放 | `character_scale_control` | 代碼中的配置 |
| 🎭 智能胖瘦控制 | `character_body_shape_control` | [BODY_ANIMATION_USAGE.md](./BODY_ANIMATION_USAGE.md) |

## 📖 使用建議

### 新手指南
1. 從 **[AUDIO_TOOLS_DISTINCTION.md](./AUDIO_TOOLS_DISTINCTION.md)** 開始，了解基本概念
2. 瀏覽各功能文檔，了解可用的工具和參數
3. 參考 **[WEBSOCKET_LOGGING.md](./WEBSOCKET_LOGGING.md)** 學習如何監控系統

### 開發者參考
- 每個文檔都包含完整的參數說明和使用範例
- 所有工具的配置都在 `session_config.py` 中定義
- 日誌分析工具位於 `logging/` 目錄

### 問題排查
- 使用 WebSocket 日誌系統進行問題診斷
- 查看各工具文檔中的常見問題解答
- 參考使用範例確保正確的參數格式

---

🎯 **目標**：這些文檔幫助開發者充分利用系統的10大超能力，創造豐富的即時互動體驗！ 