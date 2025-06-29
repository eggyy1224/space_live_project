# ElevenLabs 即時音效生成功能

## 功能概述

這個功能讓 Space Live 專案能夠使用 ElevenLabs API 即時生成客製化音效，為直播增加更豐富的音效體驗。

## 系統架構

```
使用者/AI → MCP 工具 → FastAPI 端點 → ElevenLabs API
                                    ↓
生成的音效 → 保存到 generated_sounds → 前端播放系統
```

## 設置步驟

### 1. 獲取 ElevenLabs API Key

1. 前往 [ElevenLabs](https://elevenlabs.io/app/speech-synthesis/account)
2. 註冊帳號並獲取 API key
3. 在後端目錄創建 `.env` 文件：

```bash
cd prototype/backend
touch .env
```

4. 在 `.env` 文件中添加你的 API key：

```
ELEVENLABS_API_KEY=your_api_key_here
```

### 2. 確認依賴

確認 `requirements.txt` 包含所需的套件（已包含）：
- `requests` - 用於 API 請求
- `fastapi` - Web 框架
- `pydantic` - 資料驗證

### 3. 啟動服務

```bash
cd prototype/backend
python main.py
```

## 使用方式

### 1. 透過 MCP 工具（推薦）

使用 `generate_sound_effect` MCP 工具：

```python
generate_sound_effect(
    prompt="太空船引擎啟動的聲音",
    duration_seconds=3.0,
    prompt_influence=0.6,
    filename="spaceship_engine",
    play_immediately=True
)
```

### 2. 直接 API 調用

```bash
curl -X POST "http://localhost:8000/api/control/generate-sound-effect" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "電子音效配合機械故障",
    "duration_seconds": 2.5,
    "prompt_influence": 0.6,
    "filename": "malfunction_sound",
    "play_immediately": true
  }'
```

## 參數說明

| 參數 | 類型 | 範圍 | 說明 |
|------|------|------|------|
| `prompt` | string | - | 音效描述文字 |
| `duration_seconds` | float | 0.5-22.0 | 音效長度（秒） |
| `prompt_influence` | float | 0.0-1.0 | 對描述的遵循度 |
| `filename` | string | 可選 | 自訂檔名（不含副檔名） |
| `play_immediately` | boolean | 可選 | 是否立即播放 |

## 音效提示詞範例

⚠️ **重要：prompt 必須使用精確的英文描述，中文會導致音效品質不佳！**

### 太空主題（推薦英文 prompt）
- "spaceship engine humming and vibrating steadily" (太空船引擎穩定嗡嗡聲)
- "deep space ambient cosmic wind and distant rumbling" (深空環境宇宙風和遠方隆隆聲)
- "airlock door sealing with pneumatic hiss" (氣閘門密封配氣動嘶聲)
- "alien communication signal with electronic beeps" (外星通訊信號配電子嗶聲)

### 機械/電子（推薦英文 prompt）
- "electronic malfunction with sparks crackling and warning beeps" (電子故障配電火花和警報聲)
- "robot walking with heavy metallic footsteps" (機器人重金屬腳步聲)
- "computer system booting up with electronic chirps" (電腦系統啟動配電子鳴叫)
- "laser beam charging with high-pitched whine" (雷射光束充能高頻嗚咽聲)

### 環境音效（推薦英文 prompt）
- "distant thunder rumbling with gentle rain pattering" (遠方雷聲隆隆配輕柔雨聲)
- "forest birds chirping with wind rustling leaves" (森林鳥鳴配風吹樹葉聲)
- "city traffic humming with occasional car horn" (城市車流嗡嗡聲偶有喇叭聲)
- "ocean waves crashing against rocky shore" (海浪拍打岩石海岸)

## 文件結構

生成的音效會保存在：
```
prototype/frontend/public/audio/generated_sounds/
├── generated_1640995200_spaceship_engine.mp3
├── spaceship_engine.mp3  (如果指定了檔名)
└── ...
```

## 測試

運行測試腳本：

```bash
cd integration_tests/generate_sound_effect
python test_sound_effect_generation.py
```

## 成本考量

- ElevenLabs API 按使用量收費
- 未指定長度：100 credits/次
- 指定長度：20 credits × 秒數
- 建議合理控制使用頻率

## 故障排除

### 常見問題

1. **API Key 未配置**
   ```
   ElevenLabs API key not configured
   ```
   解決：確認 `.env` 文件中有正確的 `ELEVENLABS_API_KEY`

2. **請求超時**
   ```
   音效生成超時
   ```
   解決：ElevenLabs API 通常需要 10-30 秒，請耐心等待

3. **音效無法播放**
   - 檢查前端音效系統是否正常
   - 確認文件已保存到正確目錄
   - 檢查瀏覽器音頻權限

### 除錯步驟

1. 檢查後端日志：
   ```bash
   cd prototype/backend
   tail -f logs/app.log
   ```

2. 測試 API 連接：
   ```bash
   curl http://localhost:8000/api/control/status
   ```

3. 檢查生成的文件：
   ```bash
   ls -la prototype/frontend/public/audio/generated_sounds/
   ```

## 整合到直播流程

音效生成可以與其他 Space Live 功能結合：

```python
# 生成並播放緊急警報音效
generate_sound_effect("太空艙緊急警報聲", duration_seconds=2.0)

# 配合角色動作
character_animation("漂浮", loop=True, speed=0.5)
generate_sound_effect("太空中的靜謐與微弱電子聲", duration_seconds=5.0)

# 搭配場景切換
set_camera_preset("dramatic_angle_1", duration=3.0)
generate_sound_effect("戲劇性的音效增強場景張力", duration_seconds=3.0)
```

這樣就完成了 ElevenLabs 即時音效生成功能的整合！ 