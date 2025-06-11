# Real-time 系統中 Emotion Trajectory 阻塞問題修復

## 問題描述

在 real-time 語音對話系統中，emotion trajectory（情緒軌跡）的處理會阻塞新的語音請求，導致用戶在AI表情動畫播放期間無法立即獲得新的語音回應。

### 主要阻塞點

1. **後端 WebSocket 同步發送**：emotion trajectory 在主執行緒中同步發送
2. **前端狀態處理阻塞**：emotion trajectory 處理會影響新語音請求的狀態更新
3. **Real-time 服務任務競爭**：音頻處理和事件響應在同一上下文中競爭資源

## 修復方案

### 1. 後端修復 (websocket.py)

**修改前：**
```python
# 同步發送，會阻塞後續處理
await websocket.send_json({
    "type": "emotionalTrajectory",
    "payload": {
        "duration": audio_duration,
        "keyframes": emotional_keyframes
    }
})
```

**修改後：**
```python
# 異步任務發送，不等待完成
asyncio.create_task(
    websocket.send_json({
        "type": "emotionalTrajectory",
        "payload": {
            "duration": audio_duration,
            "keyframes": emotional_keyframes
        }
    })
)
```

### 2. 前端 Hook 修復 (useEmotionalSpeaking.ts)

**修改前：**
```typescript
// 直接更新狀態，可能阻塞其他操作
setCurrentTrajectory(trajectoryData);
setLocalReferenceTime(null);
setTrajectoryActive(true);
```

**修改後：**
```typescript
// 使用 setTimeout 確保異步處理
setTimeout(() => {
  setCurrentTrajectory(trajectoryData);
  setLocalReferenceTime(null);
  setTrajectoryActive(true);
  trajectoryCompleted.current = false;
}, 0); // 異步執行，不阻塞當前執行緒
```

### 3. Real-time 語音服務修復 (RealtimeVoiceService.ts)

**音頻中斷處理優化：**
```typescript
// 使用 requestAnimationFrame 確保非阻塞處理
requestAnimationFrame(() => {
  if (audioPlayerRef.current) {
    audioPlayerRef.current.immediateStopPlayback();
  }
});
```

**音頻播放處理優化：**
```typescript
// 完全異步處理音頻片段
setTimeout(async () => {
  try {
    const arrayBuffer = await data.arrayBuffer();
    if (audioPlayerRef.current) {
      await audioPlayerRef.current.addAudioChunk(arrayBuffer);
    }
  } catch (error) {
    console.error('Failed to process audio chunk:', error);
  }
}, 0);
```

### 4. Real-time 後端服務修復 (realtime_conversation.py)

**事件處理並行化：**
```python
# 每個 OpenAI 事件使用獨立的異步任務處理
async for message in ws:
    asyncio.create_task(
        self._process_openai_event(message, audio_queue, interrupt_queue, text_queue)
    )
```

**隊列操作非阻塞化：**
```python
# 使用 put_nowait 避免阻塞
try:
    audio_queue.put_nowait(wav_data)
except asyncio.QueueFull:
    logger.warning("Audio queue is full, skipping audio chunk")
```

## 技術原理

### 異步任務分離

1. **語音處理**：維持在主執行緒，確保實時性
2. **表情動畫**：移至獨立的異步任務，不影響語音流
3. **狀態更新**：使用 requestAnimationFrame 和 setTimeout 實現非阻塞更新

### 隊列管理優化

- **有界隊列**：防止記憶體過度使用
- **非阻塞操作**：使用 put_nowait/get_nowait 避免等待
- **優雅降級**：隊列滿時跳過非關鍵數據

### 前端狀態隔離

- **emotion trajectory** 和 **語音狀態** 完全獨立
- 使用異步狀態更新避免渲染阻塞
- 確保新語音請求不受表情動畫影響

## 測試驗證

使用提供的測試腳本 `test_realtime_emotion_fix.py` 可以驗證修復效果：

```bash
python test_realtime_emotion_fix.py
```

### 預期結果

- ✅ 第二個語音請求在 3 秒內收到回應
- ✅ emotion trajectory 正常發送和處理
- ✅ 音頻播放和表情動畫並行運行

## 性能優化

### 記憶體管理

- 音頻隊列限制為 50 個項目
- 中斷隊列限制為 10 個項目
- 文字隊列限制為 100 個項目

### CPU 優化

- 使用異步任務避免 CPU 阻塞
- 表情計算在獨立的 requestAnimationFrame 中進行
- 音頻處理使用 Web Audio API 的原生並行能力

## 兼容性考慮

- 保持現有 API 接口不變
- 向下兼容舊的前端代碼
- 錯誤處理機制增強，避免單點故障

## 監控和調試

### 日誌增強

- 添加詳細的時間戳記錄
- 區分語音和表情處理的日誌
- 隊列狀態監控

### 性能指標

- 語音響應時間
- 表情動畫延遲
- 隊列堆積情況

## 總結

通過將 emotion trajectory 處理改為完全異步和非阻塞的方式，成功解決了 real-time 系統中語音和表情動畫的競爭問題。現在用戶可以在AI表情動畫播放期間立即獲得新的語音回應，大大提升了系統的響應性和用戶體驗。 