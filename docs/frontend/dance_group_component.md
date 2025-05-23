# DanceGroup 元件

`DanceGroup` 會在場景中渲染三個同步的 `BodyModel` 實例，以舞群方式展示角色動畫。所有實例共用同一組模型與動畫資料，藉由 React Three Fiber 的 `useGLTF` 快取避免重複載入。

## 使用方式

```tsx
import DanceGroup from '@/components/DanceGroup';

// 在 Canvas 或其他三維場景內
<DanceGroup />
```

### 調整位置與縮放

元件接受 `positions` 與 `scale` props，可自訂每個角色的位置與整體縮放：

```tsx
<DanceGroup
  scale={5}
  positions={[
    [-4, 0, 0],
    [0, 0, 0],
    [4, 0, 0]
  ]}
/>
```

## 整合

`SceneContainer.tsx` 已改為使用 `DanceGroup` 取代單一 `BodyModel`，因此導入元件即可呈現舞群效果。

