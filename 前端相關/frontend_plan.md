## 虛擬太空人互動裝置前端需求規劃

### 一、React 應用程式架構設計

#### 元件樹結構

```
App
├── WebSocketProvider（即時通訊管理 - 使用Socket.IO）
│   └── InteractionManager（互動管理中心）
│       ├── UIControls（互動介面）
│       ├── ConversationPanel（對話顯示）
│       └── ThreeScene（3D場景入口）
│           ├── AstronautModel（太空人模型元件 - GLB格式）
│           │   ├── ExpressionController（Morph Targets表情管理）
│           │   └── AnimationController（骨骼動畫管理）
│           ├── SceneLighting（光源配置）
│           └── CameraControls（攝影機控制）
└── GlobalStyles（全域CSS樣式）
```

#### 路由管理
- 使用 `react-router-dom` 控制不同模式或測試畫面（如展演模式、調試模式）。

#### 狀態管理
- 使用 React Context API + useReducer 管理全域狀態（語音播放狀態、動畫狀態、表情狀態、互動控制指令）。
- 使用 Socket.IO 實現即時同步狀態，確保跨裝置同步。

### 二、Three.js 場景渲染管理

#### 場景配置
- 主場景包含太空艙內部環境與背景星空，並載入虛擬太空人3D模型。
- 使用 `Canvas` 元件透過 react-three-fiber 進行渲染管理。

#### 光源配置
- 主光源：DirectionalLight，模擬太陽光效果。
- 輔助光源：AmbientLight，提供柔和環境照明。
- 特效光源：PointLight，強化局部視覺效果。

#### 攝影機配置
- 使用透視攝影機（PerspectiveCamera），搭配 OrbitControls 實現自由視角控制。

### 三、react-three-fiber 整合與效能優化

#### 技術整合
- 以 react-three-fiber 作為 React 和 Three.js 之間的橋接工具。
- 使用 drei 提供便利元件，例如模型載入、控制元件。

#### 效能優化策略
- 使用 `useMemo`、`useCallback` 避免重複渲染。
- 使用 `<Suspense>` 實施資源懶加載。
- 啟用 Frustum Culling 和 Level of Detail（LOD）控制模型渲染細節。
- 使用 Chrome DevTools、React Profiler 定期評估及驗證效能。

### 四、表情管理器（Morph Targets）設計

#### 狀態管理
- 使用 ExpressionController 元件控制表情狀態（透過useState或Context管理）。
- 透過 Socket.IO 接收後端即時指令，更新 Morph Targets。

#### 同步邏輯
- 根據動畫循環即時更新 Morph Target 權重。
- 配合語音播放進度，同步表情與嘴型。

### 五、骨骼動畫管理器設計

#### 動畫載入
- 使用 GLTFLoader 明確指定資源路徑，統一動畫資源載入策略。

#### 動畫調度與過渡處理
- AnimationMixer 管理動畫播放。
- AnimationController 提供動畫狀態切換，明確使用 crossFade 技術進行過渡。
- 提供清晰動畫控制 API，透過 Socket.IO 即時控制。

### 六、語音播放器同步設計

#### 播放控制
- 使用 HTML5 Audio 或 Web Audio API 實現語音播放。

#### 同步表情與動作
- 使用 audio 元素事件（如onPlay, onEnded, onTimeUpdate）同步觸發表情與動作。
- 建立精確的時間軸控制，以確保視覺與聽覺元素同步呈現。

### 前端開發階段規劃

| 階段           | 日期             | 任務                           |
|----------------|------------------|--------------------------------|
| 第一階段       | 4/05 - 4/25      | React 架構、WebSocket、基本場景 |
| 第二階段       | 4/26 - 5/20      | 語音整合、表情與動畫管理       |
| 第三階段       | 5/21 - 6/15      | 完整動畫與語音同步、互動調校   |
| 第四階段       | 6/16 - 7/05      | 效能優化、場景視覺調整         |
| 第五階段       | 7/06 - 7/15      | 展場測試與微調                 |

### 效率提升與成本降低建議
- 動畫資源標準化：建立清晰的資源路徑及載入規範。
- 模型精簡與LOD：動態調整模型精細度，優化系統負擔。
- 表情與動作資源預處理：透過腳本化批次處理減少手動調整時間與成本。

