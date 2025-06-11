# 身體動畫控制功能使用指南

## 概述

`body_animation` 工具是第八個超能力，可以控制前端角色的身體動畫和舞蹈動作。這個功能讓 AI 角色能夠展現各種動作、舞蹈和表演，大大增強表現力和視覺效果。

## 功能特點

### 🎭 支援的動畫類型

**基本動作系列**：
- `Idle` - 自然待機動作
- `Happy` - 開心表情動作
- `Thinking` - 思考動作
- `Wave` - 揮手動作
- `clap` - 鼓掌動作
- `PointingGesture` - 指向手勢
- `StandingClap` - 站立鼓掌
- `Cheering` - 歡呼動作

**舞蹈系列**：
- `HipHopDancin` - 嘻哈舞蹈（街舞風格）
- `hiphopdance` - 街舞動作
- `JazzDancing` - 爵士舞
- `SalsaDancing` - 莎莎舞
- `breaking` - 霹靂舞
- `Moonwalk` - 太空漫步（適合太空主題！）
- `twistdance` - 扭擺舞
- `CanCan` - 康康舞
- `DancingTwerk` - 扭臀舞
- `ButterflyTwirl` - 蝴蝶旋轉舞步

**運動系列**：
- `Walking` - 行走動作
- `Jogging` - 慢跑動作
- `Jumping` - 跳躍動作
- `RunningArc` - 弧形奔跑
- `RunningBackward` - 向後奔跑
- `InjuredWalk` - 受傷行走
- `PushUp` - 俯臥撐
- `Situps` - 仰臥起坐
- `Plank` - 平板支撐
- `KickSoccerball` - 踢足球
- `BaseballHit` - 棒球揮擊

**特殊動作**：
- `Roar` - 怒吼動作（配合暴龍音效超棒！）
- `Skateboarding` - 滑板動作
- `GuitarPlaying` - 彈吉他
- `Fishing Cast` - 釣魚動作
- `salute` - 敬禮動作
- `Kiss` - 親吻動作
- `Crying` - 哭泣表情
- `PainGesture` - 痛苦表情
- `LookAround` - 環顧四周
- `ReachingOut` - 伸手觸及
- `Patting` - 輕拍動作
- `Smoking` - 吸菸動作

## 使用方法

### 基本語法

```python
{
    "type": "function",
    "name": "body_animation",
    "arguments": {
        "state": "play",
        "animation": "HipHopDancin",
        "loop": true,
        "speed": 1.0,
        "transitionDuration": 0.5
    }
}
```

### 參數說明

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `state` | string | 否 | 動畫控制狀態：`play`（播放）、`pause`（暫停）、`resume`（恢復）、`stop`（停止），預設為 `play` |
| `animation` | string | 條件 | 要播放的單一動畫名稱（state為play時必填，與sequence二選一） |
| `sequence` | array | 條件 | 動畫序列（與animation二選一） |
| `loop` | boolean | 否 | 是否循環播放，預設為 `true` |
| `loopCount` | number/null | 否 | 循環次數，`null` 表示無限循環 |
| `speed` | number | 否 | 播放速度倍率，範圍 0.5-3.0，預設為 1.0 |
| `transitionDuration` | number | 否 | 動畫切換淡入淡出時間（秒），範圍 0.1-2.0，預設為 0.5 |

## 觸發情境

### 🎯 自動觸發關鍵詞

- **舞蹈話題**：「跳舞」「舞蹈」「dance」「表演」
- **運動話題**：「運動」「跑步」「健身」「鍛鍊」
- **歡迎時刻**：「歡迎」「Hello」「打招呼」
- **開心時刻**：「開心」「高興」「爽」
- **思考時刻**：「想想」「思考」「考慮」
- **表演時刻**：「表演」「show」「演出」
- **太空主題**：「太空」「floating」「無重力」

## 使用範例

### 1. 基本單一動畫

```python
# 開心動作
{
    "animation": "Happy",
    "loop": true
}

# 思考動作（較慢速度）
{
    "animation": "Thinking",
    "loop": true,
    "speed": 0.8
}

# 歡迎手勢（不循環）
{
    "animation": "Wave",
    "loop": false
}
```

### 2. 舞蹈表演

```python
# 嘻哈舞蹈（稍快速度）
{
    "animation": "HipHopDancin",
    "loop": true,
    "speed": 1.2
}

# 太空漫步（配合太空主題）
{
    "animation": "Moonwalk",
    "loop": true,
    "speed": 1.0
}

# 爵士舞（循環3次）
{
    "animation": "JazzDancing",
    "loop": true,
    "loopCount": 3
}
```

### 3. 動畫序列（進階用法）

```python
# 舞蹈序列表演
{
    "sequence": [
        {"name": "StandingClap", "proportion": 0.0, "loopCount": 2},
        {"name": "HipHopDancin", "proportion": 0.2, "loopCount": 3},
        {"name": "JazzDancing", "proportion": 0.5, "loopCount": 2},
        {"name": "SalsaDancing", "proportion": 0.7, "loopCount": 2},
        {"name": "Happy", "proportion": 0.9, "loopCount": null}
    ],
    "transitionDuration": 0.8
}

# 運動序列
{
    "sequence": [
        {"name": "Jogging", "proportion": 0.0, "loopCount": 4},
        {"name": "Jumping", "proportion": 0.4, "loopCount": 3},
        {"name": "Walking", "proportion": 0.7, "loopCount": 2},
        {"name": "Idle", "proportion": 0.9, "loopCount": null}
    ]
}
```

### 4. 動畫控制

```python
# 暫停動畫
{"state": "pause"}

# 恢復動畫
{"state": "resume"}

# 停止動畫
{"state": "stop"}
```

## 完美組合策略

### 🚀 五重組合（最強效果）

結合其他工具使用，創造最震撼的效果：

```python
# 1. 身體動畫
body_animation(animation="Moonwalk", loop=true)

# 2. 背景音樂
background_audio(bgmUrl="/audio/BGM/spacelive_theme.mp3")

# 3. 表情動畫
emotion_trajectory(keyframes=[
    {"tag": "excited", "proportion": 0.0},
    {"tag": "awe", "proportion": 0.3},
    {"tag": "joyful", "proportion": 0.6},
    {"tag": "triumphant", "proportion": 1.0}
], duration=4.0)

# 4. 角色音效
play_audio(filename="winds_blowing.mp3")

# 5. 攝影機視角
camera_control(preset="dance_circle_view", duration=3.0)
```

### 🎵 推薦音效搭配

| 動畫 | 推薦音效 | 表情變化 |
|------|----------|----------|
| `HipHopDancin` | 電子音樂.mp3 | excited→joyful |
| `Happy` | 狂喜.mp3 | happy→triumphant |
| `Roar` | 暴龍吼叫.mp3 | surprised→amused |
| `Thinking` | murmur.mp3 | neutral→thinking |
| `Wave` | 鳥叫.mp3 | friendly→happy |
| `Moonwalk` | winds_blowing.mp3 | awe→content |

## 使用頻率建議

- **每3-4次對話至少使用一次身體動畫**：讓角色更生動
- **舞蹈主題必用舞蹈動畫**：展現各種舞蹈風格
- **開心時刻用開心動作**：Happy、Cheering、StandingClap
- **思考時刻用思考動作**：Thinking 配合 murmur.mp3
- **歡迎時刻用歡迎動作**：Wave 接著其他互動動作

## 注意事項

1. **參數驗證**：確保 speed 在 0.5-3.0 範圍內，transitionDuration 在 0.1-2.0 範圍內
2. **互斥性**：animation 和 sequence 不能同時指定
3. **狀態控制**：pause、resume、stop 狀態不需要提供 animation 參數
4. **與其他工具配合**：建議與表情、音效、攝影機等工具組合使用
5. **適時停止**：重要對話時可以停止動畫專心交流

## 技術實現

- 調用後端 `/api/control/body-animation` API
- 支援 WebSocket 實時通信
- 自動錯誤處理和超時控制
- 詳細的日誌記錄便於調試

此功能是 AI 角色第八個超能力，讓對話更加生動有趣！ 