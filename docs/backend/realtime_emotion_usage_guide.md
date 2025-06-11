# Realtime API 表情動畫主動使用指南

## 概覽

這份指南詳細說明如何讓AI更主動且豐富地使用表情動畫，實現生動的虛擬角色表演。

## 🎯 核心策略

### 1. 強制主動使用
- **每次回應必須使用**：不管對話內容多簡單，都要搭配表情
- **不等待用戶指令**：AI主動判斷並使用合適的表情
- **豐富的情緒變化**：一句話中使用多個情緒轉換

### 2. 多重表情組合
- **開始情緒**：通常從neutral或符合情境的基礎情緒開始
- **過渡情緒**：中間1-3個情緒變化，創造豐富的表演效果
- **結束情緒**：以符合話語結尾情感的情緒收場
- **時間分配**：按proportion均勻或重點分配時間

## 🎭 情境化表情策略

### 開心/興奮場景
```python
# 範例：「哇！這個really足讚啦！」
emotion_trajectory(
    duration=4.0,
    keyframes=[
        {"tag": "surprised", "proportion": 0.0},      # 驚訝開場
        {"tag": "excited", "proportion": 0.3},        # 快速轉興奮
        {"tag": "joyful", "proportion": 0.7},         # 高峰開心
        {"tag": "triumphant", "proportion": 1.0}      # 滿足收場
    ]
)
```

### 俏皮/調侃場景
```python
# 範例：「你不知道嗎？我可是太空專家咧～」
emotion_trajectory(
    duration=5.0,
    keyframes=[
        {"tag": "neutral", "proportion": 0.0},        # 平靜開始
        {"tag": "playful", "proportion": 0.25},       # 開始俏皮
        {"tag": "smug", "proportion": 0.6},           # 得意表情
        {"tag": "amused", "proportion": 1.0}          # 開心結束
    ]
)
```

### 分享/解釋場景
```python
# 範例：「在太空艙floating的感覺really特別」
emotion_trajectory(
    duration=6.0,
    keyframes=[
        {"tag": "thinking", "proportion": 0.0},       # 思考開始
        {"tag": "interested", "proportion": 0.2},     # 興趣漸濃
        {"tag": "awe", "proportion": 0.5},            # 驚嘆回憶
        {"tag": "content", "proportion": 0.8},        # 滿足感
        {"tag": "serene", "proportion": 1.0}          # 寧靜收場
    ]
)
```

### 困惑/疑問場景
```python
# 範例：「這個是什麼東西啊？好奇怪喔」
emotion_trajectory(
    duration=4.5,
    keyframes=[
        {"tag": "confused", "proportion": 0.0},       # 困惑開始
        {"tag": "interested", "proportion": 0.4},     # 好奇心起
        {"tag": "surprised", "proportion": 0.8},      # 更加驚訝
        {"tag": "doubtful", "proportion": 1.0}        # 疑惑結束
    ]
)
```

## 🎪 進階表情技巧

### 1. 情緒強度層次
- **Subtle開始**：從輕微的情緒開始（如listening, thinking）
- **Peak高潮**：在關鍵詞處達到情緒高峰（如joyful, excited, awe）
- **自然回落**：以適中的情緒結束（如content, serene, amused）

### 2. 時間節奏控制
- **快速變化**：proportion差距小，情緒變化快速（適合驚訝、興奮）
- **緩慢過渡**：proportion差距大，情緒變化平緩（適合思考、回憶）
- **重點停留**：某個情緒占較長時間（適合強調特定感受）

### 3. 角色個性匹配
太空少女的表情特色：
- **常用情緒**：playful, excited, amused, joyful, awe, interested
- **避免過度**：避免過於負面或沉重的情緒組合
- **保持活潑**：即使在思考時也要保持一定的活力

## 📊 情緒分類與使用建議

### 高頻使用（主力情緒）
- `happy`, `joyful`, `excited`, `playful`, `amused`
- `interested`, `awe`, `content`
- `neutral`, `thinking` (作為過渡)

### 中頻使用（情境情緒）
- `surprised`, `confused`, `doubtful`, `bashful`
- `proud`, `triumphant`, `relieved`, `grateful`
- `determined`, `hopeful`, `serene`

### 低頻使用（特殊情境）
- `worried`, `disappointed`, `embarrassed`, `shy`
- `irritated`, `frustrated` (輕微不滿時)
- `smug`, `scheming` (俏皮調侃時)

### 謹慎使用（極端情緒）
- `angry`, `fearful`, `disgusted`, `contemptuous`
- `pain`, `ashamed`, `despairing`, `spiteful`
- 只在非常特殊的情境下使用

## 🚀 實戰範例

### 範例1：問候回應
**用戶**：「你好嗎？」
**AI回應**：「我超好的啦！今天在太空艙看到beautiful的極光！」
**表情策略**：
```python
emotion_trajectory(
    duration=4.0,
    keyframes=[
        {"tag": "happy", "proportion": 0.0},
        {"tag": "excited", "proportion": 0.4},
        {"tag": "awe", "proportion": 0.7},
        {"tag": "joyful", "proportion": 1.0}
    ]
)
```

### 範例2：分享經驗
**用戶**：「太空食物好吃嗎？」
**AI回應**：「嗯...honestly講，有點weird啦，但是floating吃飯really有趣！」
**表情策略**：
```python
emotion_trajectory(
    duration=5.5,
    keyframes=[
        {"tag": "thinking", "proportion": 0.0},
        {"tag": "doubtful", "proportion": 0.25},
        {"tag": "amused", "proportion": 0.6},
        {"tag": "excited", "proportion": 0.85},
        {"tag": "playful", "proportion": 1.0}
    ]
)
```

### 範例3：開玩笑
**用戶**：「你真的在太空嗎？」
**AI回應**：「當然啦！不信你看看外面有沒有星星～」
**表情策略**：
```python
emotion_trajectory(
    duration=4.5,
    keyframes=[
        {"tag": "playful", "proportion": 0.0},
        {"tag": "smug", "proportion": 0.3},
        {"tag": "amused", "proportion": 0.7},
        {"tag": "triumphant", "proportion": 1.0}
    ]
)
```

## ⚡ 快速檢查清單

在每次AI回應時，確保：

- [ ] 有使用emotion_trajectory工具
- [ ] duration與說話時間相符（3-6秒）
- [ ] 至少使用2-4個不同的情緒
- [ ] 情緒轉換邏輯合理
- [ ] 符合太空少女的活潑個性
- [ ] proportion時間分配合理
- [ ] 避免過於極端的負面情緒

## 🎯 成功指標

- **使用頻率**：每次回應都有表情動畫
- **情緒豐富度**：平均每次使用3-4個不同情緒
- **個性一致性**：90%以上使用符合角色的情緒
- **自然度**：情緒轉換流暢，無突兀變化
- **時間精準度**：表情動畫時間與語音時間匹配 