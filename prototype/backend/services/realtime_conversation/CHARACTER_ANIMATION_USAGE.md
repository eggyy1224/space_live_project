# 角色內建動畫控制工具 (character_animation)

## 📋 功能概述

`character_animation` 是新增的 **第9個超能力工具**，專門用於控制 3D 角色模型的內建動畫。這個工具讓 AI 可以透過 realtime conversation 直接控制角色播放各種生動的動作，大幅增強角色的表現力和互動性。

## 🎭 可用動畫列表

根據角色模型 `character0611.glb` 的實際動畫，共有 **13 個內建動畫**：

### 🏃‍♂️ 運動系列
- **運動1** - 基礎運動動畫
- **運動2** - 進階運動動畫

### 🌙 漂浮系列  
- **漂浮** - 優雅的漂浮動作
- **漂浮2** - 變化的漂浮效果
- **飛1** - 飛行動畫1
- **飛2** - 飛行動畫2

### 💃 舞蹈系列
- **舞步1** - 基礎舞蹈動作
- **舞步2** - 進階舞蹈動作  
- **舞步3** - 高級舞蹈動作

### 🎯 日常系列
- **Tpose** - T-pose 基礎待機姿勢
- **划手機** - 現代生活動作
- **臥躺** - 休息放鬆動作
- **不穩** - 搞笑不穩定動作

## 🔧 工具配置

### 參數說明
```json
{
  "animation": "string (必需) - 動畫名稱",
  "loop": "boolean (可選) - 是否循環播放，預設 true", 
  "speed": "number (可選) - 播放速度倍率，範圍 0.5-3.0，預設 1.0"
}
```

### 使用範例
```json
{
  "animation": "舞步1",
  "loop": true,
  "speed": 1.0
}
```

## 🎪 AI 使用策略

### 情境對應表
| 對話主題 | 推薦動畫 | 使用時機 |
|---------|----------|----------|
| 舞蹈、音樂 | 舞步1/2/3 | 談論音樂、展示才藝 |
| 太空生活 | 漂浮、飛1/2 | 描述無重力體驗 |
| 運動健身 | 運動1/2 | 健康話題、活力展現 |
| 現代科技 | 划手機 | 科技討論、日常分享 |
| 放鬆休息 | 臥躺 | 疲累、休息話題 |
| 搞笑時刻 | 不穩 | 開玩笑、製造幽默 |
| 基本待機 | Tpose | 正式介紹、回歸中性 |

### 完美組合範例

#### 🎭 舞蹈表演組合
```javascript
character_animation({animation: "舞步1", loop: true, speed: 1.2})
+ emotion_trajectory({duration: 4, keyframes: [
    {tag: "excited", proportion: 0.0},
    {tag: "joyful", proportion: 0.5}, 
    {tag: "triumphant", proportion: 1.0}
]})
+ play_audio({filename: "歌劇1.mp3"})
+ background_audio({bgmUrl: "/audio/BGM/spacelive_theme.mp3"})
```

#### 🚀 太空漂浮組合
```javascript
character_animation({animation: "漂浮", loop: true, speed: 0.8})
+ emotion_trajectory({duration: 5, keyframes: [
    {tag: "neutral", proportion: 0.0},
    {tag: "awe", proportion: 0.3},
    {tag: "serene", proportion: 0.7},
    {tag: "content", proportion: 1.0}
]})
+ play_audio({filename: "winds_blowing.mp3"})
+ background_audio({sfxUrl: "/audio/effects/spaceship_ambience_01.mp3"})
```

#### 📱 現代生活組合
```javascript  
character_animation({animation: "划手機", loop: true})
+ emotion_trajectory({duration: 3, keyframes: [
    {tag: "interested", proportion: 0.0},
    {tag: "amused", proportion: 0.6},
    {tag: "content", proportion: 1.0}
]})
+ play_audio({filename: "電子音樂.mp3"})
```

## 🔗 整合架構

### 系統流程
1. **AI 決策** → 根據對話內容選擇合適動畫
2. **工具調用** → OpenAI Realtime API 觸發 `character_animation`
3. **API 處理** → `api_integrations.py` 的 `_handle_character_animation()`
4. **HTTP 請求** → 調用 `/api/control/character/animation` 端點
5. **WebSocket 廣播** → 推送到前端所有連接
6. **前端更新** → 角色模型播放對應動畫

### 技術實現
- **後端 API**: `/api/control/character/animation` (已存在)
- **Realtime 工具**: `character_animation` (新增)
- **處理函數**: `_handle_character_animation()` (新增)
- **前端同步**: WebSocket 即時推送

## ⚡ 使用要求

### AI 指令更新
- 超能力數量：8個 → **9個**
- 新增角色內建動畫控制能力
- 要求主動且頻繁使用
- 與其他工具組合使用

### 強制使用情境
- **舞蹈話題** → 必須使用舞步系列
- **太空描述** → 必須使用漂浮/飛行系列  
- **運動健身** → 必須使用運動系列
- **日常分享** → 適時使用划手機
- **搞笑時刻** → 使用不穩製造效果

## 🧪 測試驗證

### 功能測試
```bash
# 直接 API 測試
curl -X POST "http://localhost:8000/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{"animation": "舞步1", "loop": true, "speed": 1.0}'
```

### Realtime 測試
- 透過語音對話觸發
- 觀察 AI 自動選擇動畫
- 驗證前端角色動作同步

### 語法驗證
```bash
# 檢查配置文件語法
python3 -m py_compile prototype/backend/services/realtime_conversation/session_config.py
python3 -m py_compile prototype/backend/services/realtime_conversation/api_integrations.py
```

## 🎯 預期效果

### 增強體驗
- **豐富表現力**：角色動作配合說話內容
- **沉浸感提升**：視覺與聽覺雙重刺激  
- **個性展現**：透過動作展現角色特質
- **互動性強化**：動態回應對話情境

### 太空人設強化
- 多用漂浮、飛行動畫強化設定
- 配合太空背景音效
- 營造無重力環境感受
- 增強角色可信度

### 表演多樣化
- 13種不同動畫提供豐富選擇
- 速度控制增加變化性
- 循環播放維持連續性
- 與其他工具完美結合

## 📊 成功指標

- ✅ **語法正確**：Python 編譯無錯誤
- ✅ **API 正常**：HTTP 請求返回成功
- ✅ **工具註冊**：Realtime API 識別工具
- ✅ **前端同步**：WebSocket 消息推送成功
- ✅ **動畫播放**：前端角色正確執行動作

這個新增的角色動畫控制功能將大幅提升 AI 角色的表現力和互動體驗！🎉 