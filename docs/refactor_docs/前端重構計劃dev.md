# Frontend Refactoring Roadmap & Technical Deep Dive (0406)

本文檔旨在作為 `space_live_project` 前端部分的重構記錄、待辦事項清單以及未來技術深化的參考指南。它整合了初始的重構計劃、效能分析、以及針對 3D 動畫和嘴型同步的技術研究，為構建一個穩定、高效、可擴展且生動的 AI 虛擬人前端奠定基礎。

**核心參考文件:**

*   [專案總覽與願景 (README.md)](../../README.md)
*   [現有前端架構分析 (舊)](../前端相關/0402前端架構.md) - *（此文件可能已過時，需基於當前代碼更新）*
*   [前端效能問題分析](./0402前端效能問題分析與優化建議.md) - *（記錄了重構前的主要效能瓶頸）*
*   [前端重構計劃](./0405前端重構計劃.md) - *（定義了重構的五個階段）*
*   [3D 網頁動畫技術研究](../前端相關/3d網頁動畫技術研究.md) - *（比較了 Three.js, R3F, GSAP, anime.js, Babylon.js 在角色動畫和場景切換上的優劣）*
*   [嘴型同步 (Lipsync) 技術研究](../前端相關/lipsync_study.md) - *（探討了 TTS、音素/Viseme 映射及在 Three.js/R3F 中的實現方案）*

---

## 第一階段：效能優化與基礎穩固 (基本完成)

**目標：** 快速解決影響使用者體驗的顯著效能瓶頸，確保核心互動（如 UI 反應、基礎動畫）的流暢性，為後續架構調整鋪平道路。

**主要參考：** [重構計劃第一期](./0405前端重構計劃.md#:~:text=第一期：即時效能提升與基礎重構), [效能問題分析](./0402前端效能問題分析與優化建議.md)

**狀態與待辦：**

*   **[✔] 記憶體洩漏修復：**
    *   [✔] **WebSocket 連線管理：** 已確保 `useWebSocket` Hook 或相關服務在組件卸載或應用退出時調用 `WebSocketService.disconnect()`，防止閒置連線佔用資源 ([分析參考](./0402前端效能問題分析與優化建議.md#:~:text=WebSocket%20連線未適時關閉))。
    *   [✔] **3D 模型資源釋放：** 已在模型切換邏輯 (`ModelService.switchModel` 或相關組件邏輯) 中添加對舊模型 Three.js 資源 (`geometry`, `material`, `texture`) 的 `dispose()` 調用，以緩解頻繁切換模型可能導致的記憶體累積 ([分析參考](./0402前端效能問題分析與優化建議.md#:~:text=3D%20模型資源未釋放))。 *(註：雖然實施了 dispose，但需持續觀察實際效果，並確認是否有 Linter 誤報或未完全釋放的情況)*。
*   **[✔] 減少不必要的 React 重繪：**
    *   [✔] **列表 Key 優化：** 將聊天訊息列表 (`ChatInterface.tsx` 或類似組件) 的 `key` 從不穩定的陣列索引改為基於訊息唯一 ID，減少列表增刪時的重繪開銷 ([分析參考](./0402前端效能問題分析與優化建議.md#:~:text=列表項目使用不穩定的%20key))。
    *   [✔] **Morph Target 更新機制優化：** 將 Morph Target 的狀態管理遷移至 Zustand，避免了早期通過高頻 `setState` 觸發大量 React 組件重繪的問題。現在的更新主要在 `useFrame` 中進行插值，或由服務層直接更新 Zustand store ([分析參考](./0402前端效能問題分析與優化建議.md#:~:text=Morph%20Target%20狀態頻繁更新))。
    *   [✔] **組件 Props 優化：** 在重構過程中，對如 `ControlPanel`, `SceneContainer` 等組件進行了審查，並適當使用了 `React.memo` 和 `useCallback` 來穩定 props 引用，減少因子組件 props 變化引起的父組件或兄弟組件的不必要渲染 ([實踐參考](./0405前端重構計劃.md#:~:text=減少不必要的%20React%20重繪))。
    *   [✔] **Hook 返回值穩定性：** 檢查了 `useAudioService`, `useChatService` 等 Hook 返回的狀態和函數引用，確保其穩定性，避免因 Hook 內部不必要的變化觸發使用方組件的重繪 ([實踐參考](./0405前端重構計劃.md#:~:text=減少不必要的%20React%20重繪))。
*   **[ ] 渲染迴圈 (`useFrame`) 優化 (待細化)：**
    *   [ ] **高頻動畫移入 `useFrame`：** 雖然 Morph Target 的最終應用已在 `useFrame` (`Model.tsx`) 中進行平滑插值，但仍需審查是否有其他高頻更新（如自定義的頭部擺動、呼吸效果等）可以完全移入 `useFrame`，避免通過 Zustand 或 props 觸發 React 更新 ([技術參考](./0405前端重構計劃.md#:~:text=使用%20useFrame%20Hook))。
    *   [ ] **按需渲染 (`frameloop=\"demand\"`)：** 研究在應用閒置（例如用戶長時間無操作、無語音輸入輸出）時，是否可以利用 R3F 的 `frameloop=\"demand\"` 模式或手動調用 `invalidate()` 來停止渲染循環，以節省 CPU/GPU 資源。需謹慎處理恢復渲染的時機 ([技術參考](./0405前端重構計劃.md#:~:text=暫停未使用的動畫迴圈))。
*   **[ ] 動畫與計時器管理 (待細化)：**
    *   [✔] **WebSocket 重連計時器清理：** 已確保 `WebSocketService` 中的重連 `setTimeout` 在成功連接或手動斷開時被清除 ([分析參考](./0402前端效能問題分析與優化建議.md#:~:text=WebSocket%20重連計時器))。
    *   [ ] **本地嘴型動畫暫停：** 當前 `Model.tsx` 中可能仍存在備用的隨機嘴型動畫邏輯 (`FALLBACK_MORPH_KEYS`)。需要確保當接收到來自後端或 `AudioService` 的**有效**嘴型同步數據 (lipsync/viseme) 時，這個備用動畫邏輯被**完全暫停**，避免兩套嘴型動畫衝突或產生不自然的抖動 ([分析參考](./0402前端效能問題分析與優化建議.md#:~:text=過多同時進行的動畫))。需檢查 `useFrame` 中的觸發條件。
*   **[ ] 基礎資源管理 (待審查)：**
    *   [ ] **Three.js 物件重用：** 雖然模型加載已使用 `useGLTF` 快取，但需檢查代碼中是否存在動態創建材質 (`Material`)、幾何體 (`Geometry`) 或其他 Three.js 物件並在每次渲染中重複創建的情況。應使用 `useMemo` 或將這些對象提升到組件外部來緩存和重用 ([技術參考](./0405前端重構計劃.md#:~:text=物件重用與記憶體優化))。

---

## 第二階段：架構重塑與狀態統一 (核心完成)

**目標：** 引入 Zustand 作為全局狀態管理中心，重構服務與組件的交互方式，建立清晰的分層架構，消除舊的狀態管理混亂，提升代碼的可維護性和可擴展性。

**主要參考：** [重構計劃第二期](./0405前端重構計劃.md#:~:text=第二期：代碼模組化與維護性改進), [重構計劃第三期](./0405前端重構計劃.md#:~:text=第三期：引入集中式狀態管理與架構優化)

**狀態與待辦：**

*   **[✔] Zustand 狀態管理引入與遷移：**
    *   [✔] **安裝與創建 Store：** 已成功安裝 Zustand 並創建了 `src/store/index.ts` 和 `src/store/slices/` 結構，定義了包括 `AppSlice`, `WebSocketSlice`, `ChatSlice`, `ModelSlice`, `AudioSlice` 在內的核心狀態與 Actions ([實踐參考](./0405前端重構計劃.md#:~:text=導入%20Zustand%20作為全域狀態儲存))。
    *   [✔] **狀態遷移完成：** 已將原先分散在 `Context`, 各 `Service` 內部或組件 `useState` 中的全局狀態（如連接狀態、聊天記錄、模型變換、音頻狀態、表情參數等）**全部遷移**至 Zustand Store 集中管理。
    *   [✔] **組件訂閱更新：** 已修改 `App.tsx`, `AppUI.tsx`, `ControlPanel.tsx`, `Model.tsx`, `SceneContainer.tsx` 等相關組件，使其直接從 Zustand Store (`useStore(state => ...)` ) 讀取所需狀態，並通過調用 Store Actions 來更新狀態。
*   **[✔] 服務層解耦與 Zustand 整合：**
    *   [✔] **服務層狀態清理：** 已徹底清理 `ModelService.ts`, `WebSocketService.ts`, `AudioService.ts`, `ChatService.ts` 中的舊有內部狀態管理（如本地 `this.morphTargets` 緩存、回調列表 `listeners` 等）。
    *   [✔] **服務層交互模式更新：** 各服務（如 `WebSocketService` 收到消息，`AudioService` 錄音結束）現在通過調用 Zustand Store 的 Actions 來更新全局狀態，而不是直接調用其他服務的方法或觸發組件的回調。例如，`WebSocketService` 收到 `lipsync_update` 後直接調用 `useStore.getState().updateMorphTarget()`。這實現了服務層與表現層的解耦 ([實踐參考](./0405前端重構計劃.md#:~:text=調整服務層與狀態的互動))。
*   **[✔] 核心 Bug 修復（基於新架構）：**
    *   [✔] **錄音上傳 (STT 422 錯誤) 修復：** 定位到問題在於 `services/api.ts` 的 `speechToText` 函數錯誤地使用了 `FormData`。已修改為直接傳送原始 `Blob` 並手動設置 `Content-Type: audio/webm; codecs=opus`，成功解決後端無法處理請求的問題 ([相關代碼](../../prototype/frontend/src/services/api.ts#:~:text=speechToText))。
    *   [✔] **表情控制異常修復：**
        *   **問題定位：** 發現預設表情只能瞬時顯示、控制面板僅剩 `jawOpen` 的根源在於模型加載後，未能正確初始化 Zustand 中的 `morphTargets` 狀態。`Model.tsx` 雖提取了 `morphTargetDictionary`，但 `useModelService` hook 中的 `setMorphTargetData` 回調未能觸發完整的初始化流程（缺少對 `morphTargets` 初始值的設定）。
        *   **解決方案：** 修改了 `useModelService` hook (`ModelService.ts` 末尾) 中的 `setMorphTargetData` 函數，使其在接收到有效的 `dictionary` 時，調用 `ModelService` 實例的 `initialize(dictionary)` 方法。`initialize` 方法內部負責同時更新 Zustand 的 `morphTargetDictionary` 和 `morphTargets` 狀態。
        *   **結果：** 確保了每次模型加載/切換後，Zustand 都持有該模型**完整**的 Morph Target 信息，解決了表情控制的兩個問題 ([相關代碼 - initialize](../../prototype/frontend/src/services/ModelService.ts#:~:text=initialize\(morphTargetDictionary))，[相關代碼 - setMorphTargetData](../../prototype/frontend/src/services/ModelService.ts#:~:text=setMorphTargetData%20%3D%20useCallback))。
*   **[ ] 組件拆分與模組化 (待進行)：**
    *   [ ] **拆分 `App.tsx`：** 當前的 `App.tsx` 仍然承擔了較多職責（初始化服務 Hook、狀態聚合、渲染頂層 UI 和 3D 場景）。應考慮將：
        *   3D 場景部分 (`<SceneContainer>`) 及其相關的 props 傳遞邏輯，封裝到一個更高階的容器組件（例如 `<AvatarExperience>` 或類似）。
        *   UI 部分 (`<AppUI>`) 及其控制邏輯也進一步審查，看是否能將 `ControlPanel`、`ChatInterface` 等完全解耦。
        *   `App.tsx` 最終應只負責最高層的佈局和服務 Hook 的調用 ([計劃參考](./0405前端重構計劃.md#:~:text=拆分大型組件))。
    *   [ ] **審查目錄結構：** 重新評估 `src/components`, `src/services`, `src/hooks`, `src/store`, `src/types`, `src/utils` 等目錄的劃分是否仍然合理，是否有模組可以進一步歸類或拆分，確保職責單一 ([計劃參考](./0405前端重構計劃.md#:~:text=整理目錄結構))。
*   **[ ] 類型與註解 (待補充)：**
    *   [ ] **完善類型定義：** 隨著代碼重構，許多函數簽名、組件 props 和 Zustand state 的類型可能已發生變化或需要更精確的定義。應系統性地檢查並更新 `src/types` 目錄下的接口，以及各文件內的類型註解。
    *   [ ] **補充 JSDoc 註解：** 為核心模組（如各 Service 類、Zustand Slices、關鍵 Hook 和組件）添加清晰的 JSDoc 註解，說明其用途、參數和返回值，方便團隊協作和後續維護 ([計劃參考](./0405前端重構計劃.md#:~:text=增強類型與文件註解))。

---

## 第三階段：賦予靈魂 - 精細動畫控制 (未來規劃)

**目標：** 實現更生動、自然的虛擬人表現，特別是將**頭部/面部表情**控制與**身體動作動畫**控制解耦，允許兩者獨立觸發和組合，並為引入更高級的嘴型同步和動畫技術打下基礎。

**主要參考：** [重構計劃第四期](./0405前端重構計劃.md#:~:text=第四期：頭部表情與身體動畫控制拆分), [3D 網頁動畫技術研究](../前端相關/3d網頁動畫技術研究.md), [嘴型同步 (Lipsync) 技術研究](../前端相關/lipsync_study.md)

**待辦事項 (細化規劃)：**

*   **[ ] 設計與實現分離的動畫控制器：**
    *   [ ] **定義接口：**
        *   `HeadAnimationController`：應包含方法如 `setEmotion(emotionName: string, intensity: number = 1)` (應用基於名稱的預設表情，如'happy', 'sad')，`setMorphTarget(name: string, value: number)` (直接設置單個 morph 值)，`update(delta: number)` (處理表情之間的平滑過渡/插值)。
        *   `BodyAnimationController`：應包含方法如 `playAnimation(animationName: string, loop: boolean = true, transitionDuration: number = 0.5)` (播放骨骼動畫，支持循環和淡入淡出)，`stopAnimation(animationName: string, fadeOutDuration: number = 0.5)`，`setSpeed(animationName: string, speed: number)`，`update(delta: number)` (更新 `AnimationMixer`)。
        ([計劃參考](./0405前端重構計劃.md#:~:text=設計動畫控制模組接口))
    *   [ ] **實現控制器：**
        *   `HeadAnimationController`：內部維護當前目標表情狀態（一組 morph 值），在 `update` 中使用 `THREE.MathUtils.lerp` 或動畫庫 (GSAP/anime.js) 平滑地驅動 `mesh.morphTargetInfluences`。需要能處理來自 `applyPresetExpression` 的指令和可能的實時情緒更新指令。可以參考 [Lipsync 研究](../前端相關/lipsync_study.md#:~:text=在%20Three.js/R3F%20中加載%20GLB%20並控制%20Morph%20Targets%20動畫) 中關於驅動 Morph Target 的方法。
        *   `BodyAnimationController`：利用 R3F 的 `useAnimations` hook 獲取 `actions` 和 `mixer`。控制器內部管理 `actions` 的播放、停止、淡入淡出 (`crossFadeFrom`, `fadeIn`, `fadeOut`) 和循環。可以考慮實現一個簡單的動畫狀態機來管理常見的狀態轉換 (如 Idle -> Walk -> Idle)。([技術參考 - useAnimations](../前端相關/3d網頁動畫技術研究.md#:~:text=React%20Three%20Drei%20(%60useAnimations%60)))
        ([計劃參考](./0405前端重構計劃.md#:~:text=表情控制器實作細節), [計劃參考](./0405前端重構計劃.md#:~:text=身體控制器實作細節))
*   **[ ] 整合控制器到主流程：**
    *   [ ] **修改 `Model.tsx` 或創建新的容器組件：** 在模型加載完成後，實例化 `HeadAnimationController` 和 `BodyAnimationController`，並將必要的模型數據（`mesh`, `animations`）傳遞給它們。
    *   [ ] **移除 `ModelService` 中的舊動畫邏輯：** 將 `ModelService` 中直接操作 `morphTargetInfluences` 或 `AnimationMixer` 的代碼移除，改為調用對應控制器的方法。
    *   [ ] **在 `useFrame` 中調用 `update`：** 在 `Model.tsx` 的 `useFrame` 鉤子中，確保每幀都調用 `headController.update(delta)` 和 `bodyController.update(delta)` 來驅動動畫更新 ([計劃參考](./0405前端重構計劃.md#:~:text=集成控制器至主流程))。
*   **[ ] 狀態驅動動畫控制：**
    *   [ ] **控制器訂閱 Zustand：** 讓 `HeadAnimationController` 監聽 `store.currentEmotion` 或更詳細的表情參數狀態變化；讓 `BodyAnimationController` 監聽 `store.currentAnimation` 或其他觸發身體動作的狀態。
    *   [ ] **Zustand Actions 更新目標：** UI 或服務層通過調用 Zustand Actions (如 `setEmotionState`, `playBodyAnimation`) 來更新狀態，控制器監聽到變化後執行相應的動畫邏輯。確保控制器本身不直接修改全局狀態，避免循環依賴 ([計劃參考](./0405前端重構計劃.md#:~:text=與狀態管理整合))。
*   **[ ] 提升嘴型同步 (Lipsync) 精度：**
    *   [ ] **評估當前方案：** 分析當前基於後端 `lipsync_update` 事件驅動 `morphTargets` 的效果和延遲。
    *   [ ] **研究更優方案（基於 [Lipsync 研究](../前端相關/lipsync_study.md)）：**
        *   **方案一 (增強後端)：** 如果後端 TTS 或 STT 能提供更精確的 Viseme 時間戳（類似 AWS Polly 或 Azure TTS 的 `visemeReceived` 事件），則修改 WebSocket 消息格式傳遞這些時間戳，前端 `HeadAnimationController` 可以更精準地同步嘴型。
        *   **方案二 (前端處理)：** 如果只能獲取音頻和文本，考慮在前端集成輕量級的 Lipsync 庫或算法（例如基於 Web Audio API 分析頻譜，或使用 [Rhubarb Lip Sync](../前端相關/lipsync_study.md#:~:text=Rhubarb%20Lip%20Sync) 的 WebAssembly 版本）來實時或近實時地從音頻生成 Viseme 序列，然後驅動 `HeadAnimationController`。
        *   **方案三 (混合)：** 結合後端提供的單字邊界時間和前端的音素預估算法。
    *   [ ] **模型 Viseme 映射：** 無論哪種方案，都需要確保前端使用的 Viseme 集合與 3D 模型實際擁有的 Morph Target（如 Ready Player Me 的 Oculus Viseme `viseme_aa`, `viseme_CH` 等）精確對應 ([參考 Viseme 映射表](../前端相關/lipsync_study.md#:~:text=音素與嘴型（Viseme）的對應方法))。
*   **[ ] 引入高級動畫技術 (可選，基於 [3D 動畫研究](../前端相關/3d網頁動畫技術研究.md))：**
    *   [ ] **GSAP 時間軸：** 對於特定的、需要精確編排的動畫序列（例如開場動畫、特殊交互反饋），考慮引入 GSAP，利用其 Timeline 功能進行控制，尤其適合協調 3D 動畫與 UI 動畫 ([技術參考](../前端相關/3d網頁動畫技術研究.md#:~:text=GSAP：GSAP%20可說是在場景過場動畫和相機運鏡方面非常強大的工具))。
    *   [ ] **物理動畫 (React Spring)：** 對於需要自然彈性或阻尼效果的交互（例如拖拽模型後的歸位動畫），可以考慮使用 `react-spring` 的 `useSpring` hook 來驅動模型的位置、旋轉或縮放 ([技術參考](../前端相關/3d網頁動畫技術研究.md#:~:text=React%20生態與宣告式動畫))。

---

## 第四階段：打磨與完善 (長期維護)

**目標：** 清理技術負債，統一代碼風格，更新依賴，優化構建與加載，增強健壯性，完善文檔和測試，確保專案長期健康、易於維護和迭代。

**主要參考：** [重構計劃第五期](./0405前端重構計劃.md#:~:text=第五期：技術負債清理與最終優化)

**待辦事項 (持續進行)：**

*   **[ ] 代碼清理：**
    *   [ ] 定期審查並移除因重構、功能迭代而遺留的無用代碼、註解、被註釋掉的代碼塊、以及廢棄的狀態管理邏輯 ([計劃參考](./0405前端重構計劃.md#:~:text=移除冗餘代碼與註解))。
    *   [ ] 清理調試用的 `console.log` 語句，替換為使用項目統一的 `Logger` ([相關代碼](../../prototype/frontend/src/utils/LogManager.ts))。
*   **[ ] 規範統一：**
    *   [ ] 配置並強制執行 ESLint 和 Prettier 規則，確保所有提交的代碼風格一致（縮進、引號、命名等）([計劃參考](./0405前端重構計劃.md#:~:text=統一代碼風格))。
    *   [ ] 建立或遵循團隊的 TypeScript 編碼規範。
*   **[ ] 依賴管理：**
    *   [ ] 定期（例如每季度）審查 `package.json`，使用 `npm outdated` 或類似工具檢查核心依賴（React, R3F, Drei, Zustand, Three.js 等）是否有穩定更新，評估升級的必要性和風險 ([計劃參考](./0405前端重構計劃.md#:~:text=更新依賴與版本))。
    *   [ ] 移除不再使用的 NPM 包。
*   **[ ] 構建與加載優化：**
    *   [ ] **模型資源優化：**
        *   檢查 GLB 模型文件大小，對於過大的模型，研究使用 Draco 壓縮 (`useGLTF` 支持) 或 glTF-Transform 工具進行優化（例如移除未使用數據、合併 Mesh 等）。
        *   考慮對非首屏必需的模型或大型紋理實現**延遲加載** (Lazy Loading)。
        ([計劃參考](./0405前端重構計劃.md#:~:text=優化構建與加載))
    *   [ ] **代碼分割：** 利用 Vite 的自動或手動 chunk 分割能力，將大型第三方庫或非核心功能模塊（如調試工具、不常用的 UI 面板）進行代碼分割，減小初始加載的 JavaScript 包體積。可以使用 `import()` 動態導入。
    *   [ ] **打包分析：** 定期使用 `rollup-plugin-visualizer` 或 `source-map-explorer` 等工具分析生產環境打包結果，找出體積異常的模塊，針對性優化。
*   **[ ] 健壯性提升：**
    *   [ ] **錯誤處理：** 全面審查 API 請求 (`fetchApi` 或 axios 實例)、WebSocket 消息處理、音頻處理等異步操作，確保有健壯的 `try...catch` 錯誤處理、適當的用戶提示和日誌記錄 ([計劃參考](./0405前端重構計劃.md#:~:text=強化錯誤處理與日誌))。
    *   [ ] **邊界條件：** 考慮各種異常情況（如網絡斷開、API 超時、無麥克風權限、模型加載失敗、後端數據格式錯誤等）的處理邏輯。
    *   [ ] **日誌完善：** 在關鍵業務流程、狀態轉換點、錯誤捕獲處添加結構化的日誌輸出，方便線上問題追蹤和調試。
*   **[ ] 文檔更新：**
    *   [ ] **README 更新：** 維護項目根目錄 `README.md`，更新項目簡介、技術棧、本地開發指南、部署說明等。
    *   [ ] **架構文檔：** 更新或創建描述當前前端架構（分層、狀態管理、核心組件交互）的文檔或圖表。
    *   [ ] **核心模塊文檔：** 為 Zustand store 的每個 slice、核心 Service、動畫控制器等編寫詳細說明文檔 ([計劃參考](./0405前端重構計劃.md#:~:text=文件維護))。
*   **[ ] (可選) 自動化測試：**
    *   [ ] **單元測試：** 為 Zustand store 的 reducers/actions、工具函數 (`utils`)、純邏輯 Hook 編寫單元測試（使用 Jest, Vitest 等）。
    *   [ ] **組件測試：** 為可獨立測試的 UI 組件（如按鈕、輸入框）編寫組件測試（使用 React Testing Library）。
    *   [ ] **整合測試/端到端測試：** 考慮為核心用戶流程（如發送消息 -> AI 回應 -> 模型動作、錄音 -> STT -> 文本上屏）編寫整合測試或端到端測試（使用 Cypress, Playwright 等），模擬用戶交互，確保關鍵功能在多次重構後依然穩定 ([計劃參考](./0405前端重構計劃.md#:~:text=編寫測試))。

---

## 未來展望與細化工程方向

基於當前穩定的架構，未來可以探索以下方向以進一步提升虛擬人的表現力和交互體驗：

1.  **更高級的動畫系統：**
    *   **動畫狀態機 (ASM)：** 為 `BodyAnimationController` 引入有限狀態機 (FSM) 或層級狀態機 (HSM) 來管理更複雜的動畫邏輯，例如根據上下文（站立、行走、坐下）自動切換和混合動畫，處理動畫打斷與恢復等。可以研究 XState 等庫。
    *   **過程化動畫/程序動畫 (Procedural Animation)：** 探索基於物理模擬或算法生成的動畫，例如實現更自然的閒置呼吸、頭部跟隨注視點、甚至簡單的 IK（反向動力學）來讓手部觸碰物體等，減少對預錄製動畫的依賴。
    *   **動畫混合樹 (Animation Blending Trees)：** 對於需要精確混合多個動畫層級（例如基礎行走動畫 + 上半身揮手動畫 + 頭部表情）的場景，研究 Three.js `AnimationMixer` 的高級用法或引入更專業的動畫混合方案。

2.  **更逼真的面部表情與嘴型同步：**
    *   **高級 Lipsync 方案：** 深入研究並實施 [Lipsync 研究](../前端相關/lipsync_study.md) 中提到的高精度方案，如利用 Azure/AWS 返回的 Viseme 時間戳，或在前端集成 Rhubarb/OVRLipSync 類型的算法。
    *   **結合面部表情：** 將嘴型同步與基於情感分析 (`ChatSlice.currentEmotion`) 的面部表情（眉毛、眼睛、臉頰等 Morph Target）結合，實現說話時帶有情緒的自然表情變化。`HeadAnimationController` 需要能同時處理這兩類輸入。
    *   **眼動與眨眼：** 添加隨機或基於注視點的眼球運動和自然的眨眼動畫，提升角色的生動感。

3.  **交互性增強：**
    *   **注視點控制 (Gaze Control)：** 讓模型的頭部和眼睛能夠跟隨鼠標指針、攝像頭檢測到的人臉或其他場景中的交互點。
    *   **環境交互：** 探索讓模型與簡單的場景物體進行交互，例如觸摸按鈕、拾取物品（可能需要 IK）。
    *   **實時肢體輸入（實驗性）：** 研究接入攝像頭進行姿態估計 (Pose Estimation, 如 MediaPipe Pose)，並將檢測到的肢體動作映射到模型骨骼上，實現有限的實時動作模仿。

4.  **性能持續優化：**
    *   **GPU 加速動畫：** 對於大量 Morph Target 或骨骼的計算，研究是否可以利用 GPU 計算（例如通過 Compute Shaders 或 WebGPU）來加速。
    *   **LOD (Level of Detail)：** 為模型創建不同細節層次的版本，根據攝像機距離自動切換，在高密度場景中提升性能。
    *   **渲染管線優化：** 深入理解 Three.js/R3F 的渲染流程，優化材質、燈光、陰影和後處理效果的使用，減少繪製調用（Draw Calls）和 GPU 負載。

5.  **可擴展性與可配置性：**
    *   **模型/動畫配置化：** 將模型的 URL、縮放、可用動畫列表、Morph Target 映射關係等配置化，方便更換不同風格或來源的模型。
    *   **插件化架構：** 考慮將某些高級功能（如特定交互、高級動畫模塊）設計成可插拔的插件模式，方便按需加載和組合。

這個詳細的 TODO 和路線圖將作為我們持續迭代和優化前端的指南。
