# BGM 和音效控制工具使用說明

## 🎼 background_audio 工具

`background_audio` 工具讓 AI 角色可以控制背景音樂（BGM）和音效（SFX），與 `play_audio` 不同，這些音頻是背景播放，不會從角色嘴巴發出。

## 📋 功能特色

### 1. **BGM 控制**
- 播放背景音樂營造氛圍
- 切換不同音樂風格
- 暫停/恢復播放
- 停止音樂

### 2. **音效播放**
- 播放環境音效增強場景感
- 搭配對話內容的音效
- 快速連續音效播放

### 3. **智能組合**
- 同時控制 BGM 和 SFX
- 靈活的參數組合

## 🎵 可用的 BGM 音樂

```
太空主題：
- /audio/BGM/spacelive_theme.mp3        # 太空直播主題曲
- /audio/BGM/spacelive_theme2.mp3       # 太空直播主題曲2

鄉村風格：
- /audio/BGM/space_live_country_theme1.mp3
- /audio/BGM/space_live_country_theme2.mp3

重金屬風格：
- /audio/BGM/heavy_metal_bgm_01.mp3
- /audio/BGM/heavy_metal_bgm_02.mp3
- /audio/BGM/heavy_metal_bgm_03.mp3

輕鬆風格：
- /audio/BGM/hihi.mp3
- /audio/BGM/hihi (1).mp3
- /audio/BGM/hihi (2).mp3
- /audio/BGM/hihi (3).mp3
```

## 🔊 可用的音效

```
台灣綜藝音效：
- /audio/effects/taiwan_variety_sfx_01.mp3
- /audio/effects/taiwan_variety_sfx_02.mp3
- /audio/effects/taiwan_variety_sfx_03.mp3
- /audio/effects/taiwan_variety_sfx_04.mp3

太空船環境音效：
- /audio/effects/spaceship_ambience_01.mp3
- /audio/effects/spaceship_ambience_02.mp3
- /audio/effects/spaceship_ambience_03.mp3
- /audio/effects/spaceship_ambience_04.mp3

通用音效：
- /audio/effects/winds_blowing.mp3        # 風聲效果
- /audio/effects/Energetic_fast_pace.mp3  # 快節奏音效
- /audio/effects/Ambient_keyboard_cli_2.mp3 # 環境鍵盤音效

測試音效：
- /audio/effects/測試音效1.mp3
- /audio/effects/測試音效2.mp3
- /audio/effects/測試音效3.mp3
- /audio/effects/測試音效4.mp3
- /audio/effects/測試音效5.mp3
```

## 🚀 使用範例

### 1. 播放背景音樂
```json
{
  "bgmUrl": "/audio/BGM/spacelive_theme.mp3"
}
```

### 2. 播放音效
```json
{
  "sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"
}
```

### 3. 暫停 BGM
```json
{
  "bgmPlaying": false
}
```

### 4. 恢復 BGM
```json
{
  "bgmPlaying": true
}
```

### 5. 停止 BGM
```json
{
  "bgmUrl": ""
}
```

### 6. 組合使用
```json
{
  "bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3",
  "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"
}
```

## 🎭 AI 使用場景建議

### 情境 1：營造太空氛圍
```
用戶：我想感受一下太空的感覺
AI：
1. background_audio(bgmUrl="/audio/BGM/spacelive_theme.mp3")
2. emotion_trajectory(duration=3.0, keyframes=[...])
3. 說話：「現在讓我們一起進入太空的世界吧！」
```

### 情境 2：搞笑時刻
```
用戶：說個笑話吧
AI：
1. background_audio(sfxUrl="/audio/effects/taiwan_variety_sfx_01.mp3")
2. emotion_trajectory(duration=2.0, keyframes=[{"tag": "amused", "proportion": 0.0}])
3. 說話：「哈哈！聽我說個有趣的故事」
```

### 情境 3：切換音樂風格
```
用戶：想要更有活力的音樂
AI：
1. background_audio(bgmUrl="/audio/BGM/heavy_metal_bgm_01.mp3")
2. emotion_trajectory(duration=2.5, keyframes=[{"tag": "excited", "proportion": 0.0}])
3. 說話：「讓我們來點重金屬的節奏！」
```

### 情境 4：安靜時刻
```
用戶：想要安靜一點
AI：
1. background_audio(bgmUrl="")  # 停止音樂
2. emotion_trajectory(duration=2.0, keyframes=[{"tag": "serene", "proportion": 0.0}])
3. 說話：「好的，現在讓我們享受寧靜的時光」
```

## 💡 最佳實踐

### 1. **適時使用**
- 對話開始時播放歡迎 BGM
- 根據談話內容調整音樂風格
- 重要時刻使用音效強調

### 2. **組合搭配**
- `background_audio` + `emotion_trajectory` + `play_audio`
- 三種工具配合使用效果最佳

### 3. **使用時機**
- 🎵 BGM：長期氛圍營造
- 🔊 SFX：短期情境增強
- ⏯️ 控制：根據對話節奏調整

### 4. **注意事項**
- BGM 和 SFX 可以同時播放
- 空字串 `""` 可以停止 BGM
- `bgmPlaying` 控制播放/暫停狀態

## 🔧 技術實現

新的 `background_audio` 工具已集成到 `realtime_conversation` 模組中：

- **配置檔案**：`session_config.py` - 工具定義
- **處理邏輯**：`api_integrations.py` - API 整合
- **API 端點**：`/api/control/background-audio`
- **WebSocket 訊息**：`audio-control` 類型

工具會自動調用後端 API，通過 WebSocket 發送音頻控制訊息到前端播放。 