# 太空直播系統 MCP 服務器

這是一個為太空直播系統設計的 Model Context Protocol (MCP) 服務器，讓你可以直接在 Cursor 中與 AI 太空人角色互動。

## 功能

### 💬 訊息通信
- 🚀 **send_message**: 向太空站發送訊息，讓 AI 角色說話

### 🎭 角色控制
- 😊 **set_emotion**: 設置 AI 角色的表情（包含各種情緒狀態）
- 🎪 **emotion_transition**: 創建平滑的表情轉換動畫
- 🎯 **character_animation**: 控制角色的單一動畫動作
- 🎭 **character_animation_mix**: 控制角色的多重動畫混合（新功能！）
- ⏹️ **stop_character_animation_mix**: 停止動畫混合，回到單一動畫模式

### 🎵 音頻控制
- 🎤 **play_song**: 讓角色播放歌曲或音效
- 🎶 **play_background_music**: 播放背景音樂
- 🔇 **stop_background_music**: 停止背景音樂
- 🔊 **play_sound_effect**: 播放一次性音效

### 🎥 視覺控制
- 📹 **set_camera_preset**: 設置相機預設視角
- 🎨 **generate_image_overlay**: 生成圖片疊層
- 🖼️ **generate_background_image**: 生成背景圖片
- 🤳 **take_selfie**: 拍攝自拍照片

### 🌟 其他功能
- 🔗 **即時連接**: 直接與後端系統通信
- 📡 **WebSocket 廣播**: 所有操作會即時傳送到前端顯示

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

### 🚀 send_message

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

### 🎯 character_animation

**功能**: 控制 AI 角色的單一動畫動作

**參數**:
- `animation` (必填): 動畫名稱（空體Action, 運動2, 漂浮, 運動1, Tpose, 不穩, 划手機, 漂浮2, 臥躺, 舞步1, 舞步2, 舞步3, 飛1, 飛2, 瑜珈動作1-20, 漂浮.001）
- `loop` (選填): 是否循環播放，預設 True
- `speed` (選填): 播放速度，預設 1.0

**範例**:
```python
character_animation(
    animation="舞步1",
    loop=True,
    speed=1.2
)
```

### 🎭 character_animation_mix （新功能！）

**功能**: 控制 AI 角色的多重動畫混合，可以同時播放多個動畫並控制它們的權重

- `animations_config` (必填): 動畫配置的 JSON 字串
- `blend_mode` (選填): 混合模式（"normal", "additive", "override"），預設 "normal"
- `transition_duration` (選填): 過渡時間（秒），預設 0.5

**可用動畫（參考）**:
空體Action, 運動2, 漂浮, 運動1, Tpose, 不穩, 划手機, 漂浮2, 臥躺,
舞步1, 舞步2, 舞步3, 飛1, 飛2,
瑜珈動作1, 瑜珈動作2, 瑜珈動作3, 瑜珈動作4, 漂浮.001,
瑜珈動作5, 瑜珈動作6, 瑜珈動作7, 瑜珈動作8, 瑜珈動作9,
瑜珈動作10, 瑜珈動作11, 瑜珈動作12, 瑜珈動作13, 瑜珈動作14,
瑜珈動作15, 瑜珈動作16, 瑜珈動作17, 瑜珈動作18, 瑜珈動作19, 瑜珈動作20

建議先呼叫 `get_available_main_character_animations` 取得最新清單。

**動畫配置格式**:
```json
[
  {
    "name": "動畫名稱",
    "weight": 權重值 (0.0-1.0),
    "loop": 是否循環 (true/false),
    "speed": 播放速度 (數字)
  }
]
```

**範例**:
```python
# 基本混合：70% 運動 + 30% 舞蹈
character_animation_mix(
    animations_config='[{"name": "運動1", "weight": 0.7, "loop": true, "speed": 1.0}, {"name": "舞步1", "weight": 0.3, "loop": true, "speed": 1.2}]',
    blend_mode="normal",
    transition_duration=0.5
)

# 複雜混合：太空漂浮舞蹈
character_animation_mix(
    animations_config='[{"name": "漂浮", "weight": 0.5, "loop": true, "speed": 0.8}, {"name": "舞步2", "weight": 0.3, "loop": true}, {"name": "飛1", "weight": 0.2, "loop": true, "speed": 1.5}]',
    blend_mode="additive"  
)
```

### ⏹️ stop_character_animation_mix

**功能**: 停止角色動畫混合，回到單一動畫模式

**參數**: 無

**範例**:
```python
stop_character_animation_mix()
```

### 😊 set_emotion

**功能**: 設置 AI 角色的表情

**參數**:
- `emotion` (必填): 表情名稱（happy, sad, surprised, neutral 等）
- `duration` (選填): 持續時間（秒），預設 3.0

**範例**:
```python
set_emotion(
    emotion="excited",
    duration=5.0
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

## 最新更新

### ✨ 新增功能 (最新)
- 🎭 **動畫混合系統**: 支援多個動畫同時播放並控制權重
- 🎪 **混合模式**: 支援 normal、additive、override 三種混合模式
- ⚡ **無縫切換**: 與現有單一動畫系統完全兼容
- 🎚️ **權重控制**: 精確控制每個動畫的影響力
- 🔄 **平滑過渡**: 支援自訂過渡時間

### 🚀 使用案例
```python
# 太空漂浮舞蹈
character_animation_mix(
    animations_config='[{"name": "漂浮", "weight": 0.6}, {"name": "舞步1", "weight": 0.4}]'
)

# 運動中的表情
character_animation_mix(
    animations_config='[{"name": "運動1", "weight": 0.8}, {"name": "划手機", "weight": 0.2}]',
    blend_mode="additive"
)
```

## 下一步擴展

準備添加更多工具：
- 🎨 場景切換工具
- 🌍 環境光照控制
- 🤖 舞群動畫控制
- 📺 監視器內容控制

## 開發者說明

- 主要檔案: `main.py` - MCP 服務器主程式
- 設定檔案: `server-info.json` - 工具註冊信息
- 說明檔案: `README.md` - 使用說明

### 🧪 開發指令

```bash
# 檢查工具註冊狀態
fastmcp inspect main.py -o server-info.json

# MCP 服務器啟動
python main.py

# 測試可以使用整合測試
cd ../integration_tests/character
python test_animation_mix.py
``` 