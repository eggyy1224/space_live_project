# DanceGroup 元件

`DanceGroup` 會在場景中渲染多個同步的 `BodyModel` 實例，以舞群方式展示角色動畫。預設會創建30個模型，並根據數量自動選擇最適合的佈局方式。所有實例共用同一組模型與動畫資料，藉由 React Three Fiber 的 `useGLTF` 快取避免重複載入。

## 使用方式

```tsx
import DanceGroup from '@/components/DanceGroup';

// 在 Canvas 或其他三維場景內
<DanceGroup />
```

## 佈局系統

元件會根據舞者數量自動選擇最適合的佈局：

- **1-10個模型**：單排水平排列
- **11-20個模型**：前後兩排排列  
- **21個以上模型**：圓形佈局

### 自訂數量

```tsx
// 創建15個舞者（會使用兩排佈局）
<DanceGroup count={15} />

// 創建50個舞者（會使用圓形佈局）
<DanceGroup count={50} />
```

### 自訂位置與縮放

如果需要完全客製化的位置，可以提供 `positions` 陣列：

```tsx
<DanceGroup
  scale={5}
  positions={[
    [-4, 0, 0],
    [0, 0, 0],
    [4, 0, 0],
    [0, 0, -4]
  ]}
/>
```

## 效能考量

- 每個模型實例都使用 `SkeletonUtils.clone()` 來正確處理骨骼動畫
- 模型和動畫資料會被快取，避免重複載入
- 建議在較低端設備上限制舞者數量以維持流暢的幀率

## 整合

`SceneContainer.tsx` 已改為使用 `DanceGroup` 取代單一 `BodyModel`，預設會顯示30個舞者的圓形佈局。

