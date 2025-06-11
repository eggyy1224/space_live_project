# 鏡位控制工具使用說明

## 📹 camera_control 工具

`camera_control` 工具讓 AI 角色可以控制攝影機視角和鏡位，與其他功能配合創造電影感的視覺體驗。

## 📋 功能特色

### 1. **預設鏡位控制**
- 使用前端定義的預設鏡位
- 支援多種情境的專業視角
- 可設定轉換時間

### 2. **自定義角度控制**
- 精確設定 pitch、yaw、roll 角度
- 立即切換或平滑轉換
- 完全自由的視角控制

### 3. **智能情境搭配**
- 配合 AI 角色情緒和對話內容
- 與表情、音效、背景音樂完美組合

## 📷 可用的預設鏡位

```
基礎視角：
- overview              # 全景概覽，適合介紹環境
- head_close_up         # 頭部特寫，適合重要對話
- side_view             # 側面視角，適合展示輪廓
- frontal_dynamic_low   # 正面動態低角度
- frontal_dynamic_high  # 正面動態高角度

軌道視角：
- center_orbit_high_1   # 高軌道中心視角1
- center_orbit_high_2   # 高軌道中心視角2
- center_orbit_low_1    # 低軌道中心視角1
- center_orbit_low_2    # 低軌道中心視角2
- orbit_head_1          # 頭部軌道視角1
- orbit_head_2          # 頭部軌道視角2

創意視角：
- low_angle_head        # 低角度頭部，適合威嚴感
- top_down_center       # 俯視中心，適合上帝視角
- dramatic_angle_1      # 戲劇角度1，適合情緒高潮
- dramatic_angle_2      # 戲劇角度2，適合情緒高潮
- behind_head_looking_out # 頭後望外，適合展示背景

動感視角：
- dance_circle_view     # 舞蹈圓環視角，適合動感時刻
- fly_by_left          # 左側飛越視角
- fly_by_right         # 右側飛越視角
- full_shot_dancers    # 全身舞者視角
```

## 🚀 使用範例

### 1. 使用預設鏡位
```json
{
  "action": "set_preset",
  "preset": "overview",
  "duration": 3.0
}
```

### 2. 立即設定角度
```json
{
  "action": "set_angle",
  "pitch": 30,
  "yaw": 45,
  "roll": 0
}
```

### 3. 平滑轉換角度
```json
{
  "action": "transition",
  "pitch": -20,
  "yaw": -30,
  "roll": 15,
  "duration": 6.0
}
```

## 🎭 AI 使用場景建議

### 情境 1：對話開場
```
用戶：嗨！你好
AI：
1. camera_control(action="set_preset", preset="overview", duration=2.0)
2. background_audio(bgmUrl="/audio/BGM/spacelive_theme.mp3")
3. emotion_trajectory(duration=3.0, keyframes=[...])
4. 說話：「歡迎來到我的太空艙！」
```

### 情境 2：重要時刻
```
用戶：告訴我一個重要的秘密
AI：
1. camera_control(action="set_preset", preset="head_close_up", duration=1.5)
2. emotion_trajectory(duration=2.0, keyframes=[{"tag": "mysterious", "proportion": 0.0}])
3. 說話：「仔細聽我說...」
```

### 情境 3：展示太空景色
```
用戶：太空是什麼樣子的？
AI：
1. camera_control(action="set_preset", preset="behind_head_looking_out", duration=3.0)
2. background_audio(sfxUrl="/audio/effects/spaceship_ambience_01.mp3")
3. 說話：「你看，這就是從太空艙看到的美景」
```

### 情境 4：情緒高潮
```
用戶：這太令人驚喜了！
AI：
1. camera_control(action="set_preset", preset="dramatic_angle_1", duration=2.0)
2. play_audio(filename="狂喜.mp3")
3. emotion_trajectory(duration=2.5, keyframes=[{"tag": "excited", "proportion": 0.0}])
4. 說話：「真的super讚啦！」
```

### 情境 5：動感時刻
```
用戶：跳個舞吧！
AI：
1. camera_control(action="set_preset", preset="dance_circle_view", duration=2.5)
2. background_audio(bgmUrl="/audio/BGM/heavy_metal_bgm_01.mp3")
3. 說話：「來跳個太空舞！」
```

## 💡 最佳實踐

### 1. **情境搭配**
- 開場歡迎：`overview` 或 `frontal_dynamic_low`
- 重要對話：`head_close_up`
- 太空話題：`center_orbit_high_1/2`
- 情緒高潮：`dramatic_angle_1/2`
- 展示背景：`behind_head_looking_out`

### 2. **組合使用**
```
完美四重組合：
1. camera_control（設定視角）
2. background_audio（環境氛圍）
3. emotion_trajectory（表情動畫）
4. play_audio（角色音效）
```

### 3. **使用時機**
- 🎬 對話開始設定基礎視角
- 🎭 情境轉換時切換鏡位
- 🎯 重要時刻用特殊角度
- 🚀 太空話題用軌道視角
- 💫 與其他工具完美配合

### 4. **注意事項**
- `duration` 控制轉換時間，不是停留時間
- 預設動作是 `set_preset`，最常用
- 自定義角度需要同時提供 pitch、yaw、roll
- 建議頻繁使用以增強視覺體驗

## 🔧 技術實現

新的 `camera_control` 工具已集成到 `realtime_conversation` 模組中：

- **配置檔案**：`session_config.py` - 工具定義
- **處理邏輯**：`api_integrations.py` - API 整合  
- **API 端點**：
  - `/api/control/camera/set-frontend-preset` - 預設鏡位
  - `/api/control/camera/set-angle` - 立即設定角度
  - `/api/control/camera/transition` - 平滑轉換角度
- **WebSocket 訊息**：`camera-angle` 和 `camera-transition` 類型

工具會自動調用後端 API，通過 WebSocket 發送攝影機控制訊息到前端執行。 