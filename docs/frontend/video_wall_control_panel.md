# VideoWallControlPanel

The **VideoWallControlPanel** component exposes real-time controls for a three-screen video wall. It is rendered only when `VITE_DIRECTOR` is set to `true`.

## Features

- Displays the current video and visibility state for each screen.
- Allows selecting a new clip from the predefined list in `resources.ts`.
- Visibility of each screen can be toggled independently.
- State is kept in the `videoScreens` slice of the Zustand store, so updates are reflected immediately in the 3D scene.

## Usage

```tsx
import VideoWallControlPanel from '@/components/VideoWallControlPanel';

// ... inside App
<VideoWallControlPanel />
```
