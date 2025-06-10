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

前端在傳送新的語音片段時，應立即中斷目前播放中的回覆，以確保對話能即時切換。


