# Real-time Conversation API

實時語音對話模組的端點與串流流程說明。

## WebSocket 端點

| Path | 說明 |
|------|------|
|`/api/real-time/ws`|語音串流 WebSocket，傳入音頻片段，持續回傳語音回應|

### 使用方式

1. 建立 WebSocket 連線。
2. 以二進位訊息傳送音訊 `Blob` 片段。
3. 服務會將收到的語音即時轉寫並透過 OpenAI Real‑time API 產生回覆。
4. 產生的語音會以二進位形式持續傳回，前端可即時播放並同步頭部動畫。

## Configuration

```json
{
  "model": "gpt-4o-realtime-preview",
  "voice": "alloy",
  "turn_detection": {
    "type": "server_vad",
    "threshold": 0.5,
    "prefix_padding_ms": 300,
    "silence_duration_ms": 500
  },
  "transcript_model": "whisper-1",
  "noise_reduction": "none",
  "temperature": 0.84,
  "max_tokens": 4096
}
```

模型將以臺灣閩南語、親切且情感豐富的語氣快速回應，內容保持簡短。

### Example

- User: "What do you think about spicy food?"
  - Assistant: "辣味好食, 小心喔!"
- User: "How's the weather today?"
  - Assistant: "今天天氣無錯啦。"


