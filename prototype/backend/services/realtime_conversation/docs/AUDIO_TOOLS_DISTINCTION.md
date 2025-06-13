# 音頻工具功能區分說明

## 🚨 重要：兩種音頻工具的關鍵區別

### 🎤 play_audio（角色音效唱歌工具）
**功能定位**：從角色嘴巴發出的聲音，表現角色行為
- **聲音來源**：角色本身
- **用途**：唱歌、呼叫、驚呼、表達情緒
- **性質**：角色的行為表現
- **檔案來源**：`prototype/backend/songs/` 目錄
- **API路徑**：`/songs-file/` 前綴

**使用範例**：
```json
{
  "filename": "暴龍吼叫.mp3"    // 角色發出驚呼
}
{
  "filename": "歌劇1.mp3"       // 角色唱歌
}
{
  "filename": "狂喜.mp3"        // 角色表達興奮
}
```

### 🎼 background_audio（背景氛圍控制工具）
**功能定位**：環境背景音樂和氛圍音效，不從角色發出
- **聲音來源**：環境背景
- **用途**：營造氛圍、設置BGM、環境音效
- **性質**：場景氛圍營造
- **檔案來源**：`prototype/frontend/public/audio/` 目錄
- **API路徑**：`/audio/BGM/` 和 `/audio/effects/` 前綴

**使用範例**：
```json
{
  "bgmUrl": "/audio/BGM/spacelive_theme.mp3"    // 背景音樂
}
{
  "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"    // 環境音效
}
{
  "bgmPlaying": false    // 暫停背景音樂
}
```

## 📋 使用場景對比

| 情境 | play_audio（角色） | background_audio（環境） |
|------|-------------------|------------------------|
| 角色唱歌 | ✅ 歌劇1.mp3 | ❌ |
| 角色驚呼 | ✅ 暴龍吼叫.mp3 | ❌ |
| 角色表達興奮 | ✅ 狂喜.mp3 | ❌ |
| 設置對話氛圍 | ❌ | ✅ spacelive_theme.mp3 |
| 太空船環境音 | ❌ | ✅ spaceship_ambience_01.mp3 |
| 搞笑綜藝氛圍 | ❌ | ✅ taiwan_variety_sfx_01.mp3 |

## 🎯 正確的組合使用

### 完美三重組合
1. **emotion_trajectory**：表情動畫配合說話
2. **play_audio**：角色音效表現行為
3. **background_audio**：背景氛圍營造環境

### 使用範例
當用戶說「哇！太空好美啊！」時：

```
1. emotion_trajectory(duration=3.0, keyframes=[
   {"tag": "surprised", "proportion": 0.0},
   {"tag": "awe", "proportion": 0.5},
   {"tag": "joyful", "proportion": 1.0}
])

2. play_audio(filename="狂喜.mp3")  // 角色發出驚喜聲

3. background_audio(bgmUrl="/audio/BGM/spacelive_theme.mp3")  // 設置太空主題背景音樂
```

## ⚠️ 常見錯誤避免

### ❌ 錯誤用法
- 用 play_audio 播放背景音樂
- 用 background_audio 表現角色唱歌
- 混淆兩者的檔案路徑和用途

### ✅ 正確理解
- **play_audio** = 角色的聲音行為
- **background_audio** = 環境的氛圍音樂
- 兩者可以同時使用，功能互補

## 🔧 技術路徑

### play_audio 調用鏈
```
AI工具調用 → api_integrations.py → /api/control/play-audio → WebSocket: play-audio → 前端播放（角色音效）
```

### background_audio 調用鏈
```
AI工具調用 → api_integrations.py → /api/control/background-audio → WebSocket: audio-control → 前端播放（背景音樂）
```

## 📝 AI 提示詞關鍵點

在 AI 指令中已經強調：
- **角色音效** vs **環境氛圍** 的明確區分
- 不同的觸發情境和使用時機
- 完全不同的檔案來源和API路徑
- 組合使用的最佳實踐

這樣的區分確保 AI 能正確理解並使用兩種不同的音頻功能，避免混淆和誤用。 