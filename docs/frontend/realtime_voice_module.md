# 前端即時語音模組

此模組負責從瀏覽器麥克風擷取音訊，並將片段串流至後端。後端回傳的語音會即時播放，同步帶動頭部動畫。

## 使用方式

```tsx
import { useRealtimeVoice } from '@/services';

const { start, stop, streaming } = useRealtimeVoice();
```

介面提供可切換的麥克風按鈕或使用 Ctrl+R 觸發。按一次啟動串流，再按一次立即停止。

預設會連線至 `ws://<host>/api/real-time/ws` WebSocket 端點。

