# 前端即時語音模組

此模組負責從瀏覽器麥克風擷取音訊，並將片段串流至後端。後端回傳的語音會即時播放，同步帶動頭部動畫。

## 使用方式

```tsx
import { useRealtimeVoice } from '@/services';

const { start, stop, streaming } = useRealtimeVoice();
```

在介面上提供一個獨立的麥克風按鈕，按下開始串流，放開即停止。


