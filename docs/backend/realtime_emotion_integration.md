# Realtime API Emotion Trajectory 整合

## 概覽

我們成功將 emotion trajectory 功能整合到 OpenAI Realtime API 中，讓 GPT-4o-mini-realtime-preview 能夠在對話過程中自動調用表情動畫控制。

## 功能特點

### 1. Function Calling 整合
- **工具定義**: 在 `RealtimeConversationService` 中定義了 `emotion_trajectory` 工具
- **自動調用**: AI 在說話時會自動決定是否需要使用表情動畫
- **參數驗證**: 完整的參數格式驗證和錯誤處理
- **格式修復**: 修正了工具定義格式，使用 Realtime API 的正確結構

### 2. 完整的情緒標籤支援
我們已經整合了前端 `emotionMappings.ts` 中的所有情緒標籤：

#### 基礎狀態
- `neutral`, `listening`, `thinking`

#### 正面情緒
- `happy`, `joyful`, `content`, `amused`, `excited`, `interested`
- `affectionate`, `proud`, `relieved`, `grateful`, `hopeful`, `serene`
- `playful`, `triumphant`

#### 負面情緒
- `sad`, `gloomy`, `disappointed`, `worried`, `angry`, `irritated`
- `frustrated`, `fearful`, `nervous`, `disgusted`, `contemptuous`
- `pain`, `embarrassed`, `jealous`, `regretful`, `guilty`, `ashamed`
- `despairing`, `spiteful`

#### 其他狀態
- `surprised`, `confused`, `skeptical`, `bored`, `sleepy`, `scheming`
- `determined`, `impatient`, `shy`, `bashful`, `smug`, `awe`, `doubtful`

**總計：49 個情緒標籤**

### 3. 工具參數格式
```json
{
  "duration": 3.0,
  "keyframes": [
    {"tag": "neutral", "proportion": 0.0},
    {"tag": "happy", "proportion": 0.5},
    {"tag": "joyful", "proportion": 1.0}
  ]
}
```

## 技術實作

### 1. 工具定義修復
```python
# 修正前（錯誤格式）
{
    "type": "function",
    "function": {
        "name": "emotion_trajectory",
        # ...
    }
}

# 修正後（正確格式）
{
    "type": "function",
    "name": "emotion_trajectory",
    # ...
}
```

### 2. Session 配置
在 `_send_session_update` 方法中：
```python
session_event = {
    "type": "session.update",
    "session": {
        "tools": tools,
        "tool_choice": "auto",
        # ...
    }
}
```

### 3. Function Calling 處理
在 `_process_openai_event` 方法中處理：
- `response.output_item.done` 事件
- 執行 `_execute_tool_function`
- 發送 `conversation.item.create` 回應
- 觸發 `response.create` 繼續對話

### 4. 系統整合
- 直接調用現有的 WebSocket 管理器
- 重用現有的 `emotionalTrajectory` 消息格式
- 完全相容前端的 emotion mapping 系統

## 修復歷程

### 問題：工具定義格式錯誤
```
Missing required parameter: 'session.tools[0].name'
```

### 解決方案
1. **格式修正**: 將 nested 的 `"function"` 結構改為平面結構
2. **標籤完善**: 整合所有 49 個情緒標籤
3. **描述優化**: 更新描述以反映完整的 emotion mapping 對應

## 使用範例

AI 現在可以自動在對話中使用表情動畫：

```
用戶：「告訴我一個好笑的笑話！」
AI：「好啊！為什麼程式設計師不喜歡大自然？」
    + 自動調用: emotion_trajectory(happy → playful → amused)
AI：「因為外面沒有 WiFi 啦！」
    + 自動調用: emotion_trajectory(neutral → joyful → triumphant)
```

## 狀態

✅ **已完成**
- 工具定義格式修復
- 完整情緒標籤整合
- Function calling 事件處理
- 系統整合測試

✅ **已驗證**
- OpenAI Realtime API 連接成功
- 工具定義無錯誤
- 情緒標籤完整對應

🎯 **後續優化**
- 添加更多控制工具（camera, body animation 等）
- 優化情緒選擇的智能程度
- 增加動畫時序的精確控制

## AI 指令整合

在 AI 的系統指令中加入了工具使用指南：

```
## 工具使用指南：
當你想要表達情緒或增強表演效果時，你可以使用emotion_trajectory工具來控制你的表情動畫。
- 在說話時搭配合適的情緒表現
- 可以使用多個情緒關鍵幀來創造豐富的表情變化
- 情緒標籤包括：happy, sad, angry, surprised, neutral, excited, thinking, confused等
```

## 使用範例

### 基本情緒表達
AI 說："哇！今天天氣真好！"
同時調用：
```json
{
  "duration": 3.0,
  "keyframes": [
    {"tag": "neutral", "proportion": 0.0},
    {"tag": "excited", "proportion": 0.3},
    {"tag": "happy", "proportion": 1.0}
  ]
}
```

### 複雜情緒變化
AI 說："剛開始我很困惑，但現在我明白了，真的很開心！"
同時調用：
```json
{
  "duration": 5.0,
  "keyframes": [
    {"tag": "confused", "proportion": 0.0},
    {"tag": "thinking", "proportion": 0.4},
    {"tag": "surprised", "proportion": 0.7},
    {"tag": "joyful", "proportion": 1.0}
  ]
}
```

## 錯誤處理

### 1. 參數驗證
- 檢查必要參數 `duration` 和 `keyframes`
- 驗證 keyframes 格式和內容
- 確保 emotion tags 在允許的範圍內

### 2. 連接檢查
- 檢查是否有活躍的前端連接
- 處理 WebSocket 廣播失敗的情況

### 3. 日誌記錄
- 詳細的執行日誌
- 錯誤追蹤和調試信息

## 測試

使用提供的測試腳本：
```bash
python test_emotion_realtime.py
```

## 相容性

- ✅ 與現有的 emotion trajectory 系統完全相容
- ✅ 不影響現有的 REST API `/api/control/emotion-trajectory`
- ✅ 保持前端 `useEmotionalSpeaking` hook 的正常運作
- ✅ 支援同時使用 Realtime API 和傳統 WebSocket

## 下一步擴展

1. **增加更多工具**: 可以加入其他控制功能如 `camera_control`, `body_animation` 等
2. **更細緻的情緒控制**: 支援更多情緒參數如強度、速度等
3. **情境感知**: 根據對話內容自動選擇合適的情緒表達
4. **多模態整合**: 結合語音、文字和視覺效果的統一控制

## 注意事項

1. **黃金法則依然適用**: AI 的語音和表情必須同步，emotion trajectory 在說話時才有最佳效果
2. **工具調用延遲**: Function calling 會增加少許延遲，但通常在可接受範圍內
3. **成本考慮**: Function calling 會消耗額外的 tokens，但emotion control 通常參數較少

這個整合為 SpaceLive 系統帶來了真正的即時互動體驗，讓 AI 角色能夠在對話中自然地表達情緒。 