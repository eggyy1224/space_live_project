# Camera System

本文件說明 `CameraManager` 的設計與使用方式，可在 React Three Fiber 環境中實現多預設視角、自動追蹤與平滑轉場。

## 設計概念

- **相機預設 (CameraPreset)**：每個預設包含相機位置、觀察目標與 FOV。可任意新增或移除。
- **平滑轉場**：透過二次方緩動函式 (easeInOutQuad) 在指定時間內插值相機位置與目標。
- **動態追蹤**：若指定追蹤目標物件，未在轉場時會自動 `lookAt` 目標。
- **模組化 API**：`addPreset`、`removePreset`、`transitionTo` 等方法方便操作。

## 基本使用

```tsx
import { useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { useCameraManager, CameraPreset } from '../src/camera';

const presets: CameraPreset[] = [
  { name: 'default', position: [0, 1, 5], target: [0, 0, 0], fov: 50 },
  { name: 'close', position: [0, 0.5, 2], target: [0, 0.5, 0], fov: 40 },
];

function Scene() {
  const { camera } = useThree();
  const manager = useCameraManager(camera as THREE.PerspectiveCamera, presets, 'default');

  // 依事件轉換視角
  function handleEvent() {
    manager.transitionTo('close', 2); // 2 秒轉場至 close
  }

  return null;
}

export default function Example() {
  return (
    <Canvas>
      <Scene />
    </Canvas>
  );
}
```

上述範例建立兩個相機預設，預設從 `default` 開始，接收到事件後平滑切換到 `close`。

## 與事件整合

`CameraManager` 僅管理狀態，不直接處理事件。可在應用邏輯中根據音訊強度、角色移動或其他條件呼叫 `transitionTo` 與 `track` 來改變視角。例如：

```ts
if (beatDetected) manager.transitionTo('close', 0.5);
manager.track(characterObject);
```

此設計可依照專案需求擴充，將決策邏輯放在 React 狀態或 Zustand store 中。詳細 API 參考原始碼註解。
