# VideoPlayer 元件

`VideoPlayer` 在 3D 場景中顯示一塊 2:3 的影片螢幕，並自動循環播放 `public/videos` 目錄下的影片。

## 功能特點

- 使用 `THREE.VideoTexture` 將 HTML `<video>` 的畫面貼在平面上。
- 影片清單預設包含 `space_live.mp4` 與 `Drive_in_stormy.mp4`，播放完畢後等待 5 秒自動切換下一支。
- 若瀏覽器限制自動播放，畫面會顯示提示，使用者點擊一次即可開始播放。
- 提供播放、暫停、重新開始與音量控制等基本操作。
- 影片平面預設位置在大螢幕旁邊，可透過 `position` 與 `width` 屬性調整。

## 使用方式

```tsx
import VideoPlayer from '@/components/VideoPlayer';

// 在場景中放置影片螢幕
<VideoPlayer />
```

## 效能建議

影片解析度建議控制在 720p 或以下，以減少對 GPU 的負擔。`VideoTexture` 會關閉 Mipmaps 並使用線性過濾，確保在大多數裝置上維持流暢播放。
