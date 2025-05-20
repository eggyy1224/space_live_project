# TODO List: 實現結合基礎說話狀態與情緒表情的臉部動畫 (基於 ARKit Blendshapes)

**前言：本次 TODO 的目的**

本 TODO 列表旨在指導前端開發，實現虛擬角色臉部動畫的第一階段目標：**將後端傳遞的角色情緒狀態與基礎的說話指示（嘴巴開合）相結合**，並應用於基於 ARKit Blendshapes 標準的 3D 模型上。我們將優先確保情緒表達的獨立性和說話時嘴巴的基礎開合動作，而**精確的音素級嘴型同步 (Lip-sync) 將作為後續的優化功能 (Bonus)**。此列表基於對現有架構（React, R3F, Zustand, ARKit 模型）的分析，並明確了需要修改和新增的組件與邏輯。

---

## TODO List: 實現結合基礎說話狀態與情緒表情的臉部動畫 (基於 ARKit Blendshapes)

**優先目標：實現情緒表達 + 基礎說話嘴型開合。精確 Lip-sync 為 Bonus。**

### 1. 模型理解與分類 (基於 mixamowomanwithface.glb)

*   [x] **研究 ARKit Blendshapes:** 熟悉模型提供的 51 個 ARKit blendshape 名稱及其視覺效果。
*   [x] **分類 Blendshapes:** 將 51 個 blendshapes 分類為：
    *   **基礎說話嘴型:** 識別主要控制嘴巴**開合**的 blendshape(s) (核心: `jawOpen`, 輔助: `mouthClose`)。
    *   **情緒表達:** 識別控制眉毛、眼睛、臉頰、嘴部（除基礎開合外）、鼻子等的 blendshape。
    *   **其他:** 識別控制視線 (`eyeLook...`)、眨眼 (`eyeBlink...`) 等。
*   [x] **文檔記錄分類:** 記錄每個 blendshape 的分類和預期用途。
*   [x] **測試 Blendshape 組合:** 實驗不同情緒 blendshape 與 `jawOpen`/`mouthClose` 組合的效果。

### 2. 前端狀態管理 (Zustand - `ModelSlice`)

*   [ ] **修改 `ModelSlice.ts`:**
    *   [ ] **移除/棄用舊狀態:** 移除或標記棄用直接用於動畫的 `morphTargets` 狀態 (如果它與新狀態衝突)。
    *   [ ] **新增 `isSpeaking: boolean` 狀態:** 用於指示角色當前是否正在說話 (由音頻播放觸發)。初始值為 `false`。
    *   [ ] **新增 `targetEmotionWeights: Record<string, number>` 狀態:** 儲存由後端指令設定的 **目標** 表情 blendshape 權重。初始值為 `{}`。
    *   [ ] **新增 Action `setIsSpeaking(speaking: boolean)`:** 用於更新 `isSpeaking` 狀態。
    *   [ ] **新增 Action `setTargetEmotionWeights(weights: Record<string, number>)`:** 用於接收後端指令並更新 `targetEmotionWeights`。
*   [ ] **更新組件訂閱:** 確保 `Model.tsx` 正確訂閱 `isSpeaking` 和 `targetEmotionWeights`。

### 3. 前端觸發邏輯

*   [ ] **修改 `AudioService.ts` (或其他音頻處理邏輯):**
    *   [ ] **移除直接更新 `jawOpen`:** 刪除 `updateMouthShape` 中調用 `updateMorphTarget('jawOpen', ...)` 的代碼。
    *   [ ] **觸發 `isSpeaking`:**
        *   在 `playAudio` 開始播放 TTS 音頻時，調用 `useStore.getState().setIsSpeaking(true)`。
        *   在 TTS 音頻播放結束或停止時 (`onended`, `stopPlayback`)，調用 `useStore.getState().setIsSpeaking(false)`。
*   [ ] **實現 WebSocket 情緒指令處理:**
    *   [ ] 在處理 WebSocket 消息的服務中 (可能是 `WebSocketService` 或單獨的 `EmotionHandler`)：
        *   [ ] 監聽來自後端的特定情緒更新消息 (例如 `type: 'emotion_update'`)。
        *   [ ] 解析消息內容，獲取目標表情 blendshape 及其權重。
        *   [ ] 調用 `useStore.getState().setTargetEmotionWeights(parsedWeights)` 來更新 Zustand 中的目標情緒狀態。

### 4. 後端情緒指令系統 (無變更)

*   *保持原計劃:*
    *   [ ] 實現情緒判斷邏輯。
    *   [ ] 映射情緒到目標 ARKit blendshape 權重。
    *   [ ] 定義並通過 WebSocket 發送包含目標 ARKit 權重的消息。

### 5. 前端渲染層合併 (`Model.tsx` - 核心邏輯)

*   [ ] **修改 `Model.tsx` 的 `useFrame((state, delta) => { ... })` 邏輯:**
    *   [ ] **讀取狀態:** 從 Zustand 讀取 `isSpeaking` 和 `targetEmotionWeights`。
    *   [ ] **獲取模型引用:** 確保能訪問 `meshRef.current` 及其 `morphTargetDictionary` 和 `morphTargetInfluences`。
    *   [ ] **計算目標權重映射 (`targetWeights`):** 創建一個臨時的 `targetWeights` 對象，用於儲存 *所有* 受控 blendshape 的 **最終目標值**。
        1.  **初始化:** 將 `targetEmotionWeights` 的內容複製到 `targetWeights`。
        2.  **計算說話目標:**
            *   `targetJawOpen = isSpeaking ? 0.7 : (targetWeights['jawOpen'] || 0)`  (示例：說話優先，強度 0.7)
            *   `targetMouthClose = isSpeaking ? 0 : (targetWeights['mouthClose'] === undefined ? 1 : targetWeights['mouthClose'])` (示例：不說話時默認閉嘴，除非情緒指定)
        3.  **更新 `targetWeights`:** 將計算出的 `targetJawOpen` 和 `targetMouthClose` 更新到 `targetWeights` 對象中 (可能覆蓋情緒對應的值，根據選定的優先級策略)。
    *   [ ] **平滑應用權重 (Lerp):**
        *   遍歷模型的 `morphTargetDictionary` 中的所有 blendshape 名稱。
        *   對於每個 blendshape `name`：
            *   獲取其索引 `index`。
            *   獲取其 **當前** 實際權重 `currentValue = meshRef.current.morphTargetInfluences[index]`。
            *   獲取其 **最終目標** 權重 `targetValue = targetWeights[name] ?? 0`。
            *   **計算 Lerp:** `newValue = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor)` (其中 `lerpFactor` 基於 `delta`，例如 `delta * 15`)。
            *   **應用新值:** `meshRef.current.morphTargetInfluences[index] = newValue`。
    *   [ ] **(可選) 處理眨眼:** 添加獨立的、基於計時器或隨機的邏輯來控制 `eyeBlinkLeft/Right` 的 lerp 目標值。

### 6. 測試與調優

*   [ ] **基礎說話測試:** 驗證音頻播放時 `jawOpen` 是否平滑開合，結束時是否閉合 (`mouthClose`)。
*   [ ] **情緒應用測試:** 單獨測試不同情緒指令是否能正確、平滑地改變對應的表情 blendshapes。
*   [ ] **混合效果測試:** **重點測試** 在不同情緒下觸發說話/停止說話時，表情與嘴巴開合的疊加效果是否自然，驗證步驟 5 中目標權重的計算和混合策略是否符合預期。
*   [ ] **同步測試:** 確保基礎說話狀態與音頻播放的起止大致同步。
*   [ ] **平滑度調優:** 調整 `useFrame` 中 lerp 的 `lerpFactor`，找到最佳的過渡速度。
*   [ ] **視覺效果調整:** 根據測試反饋，微調目標權重計算邏輯（如 `jawOpen` 的目標值、`mouthClose` 的默認值）或混合策略。
*   [ ] **性能監控:** 檢查 `useFrame` 的複雜度是否影響幀率。

### 7. (Bonus) 精確 Lip-sync 系統整合

*   *保持原計劃:*
    *   [ ] 實現 Phoneme-to-ARKit 映射。
    *   [ ] 用 Lip-sync 邏輯替換 `setIsSpeaking` 觸發器，改為更新詳細的 `targetVisemeWeights`。
    *   [ ] 重構 Zustand 狀態以包含 `targetVisemeWeights`。
    *   [ ] 重構 `Model.tsx` 的 `useFrame` 合併邏輯以處理 `targetVisemeWeights` 和 `targetEmotionWeights`。
    *   [ ] 進行詳細的音素同步測試。 

---

## 參考文件：ARKit Blendshape 分類與分析 (基於 mixamowomanwithface.glb)

模型提供了 51 個遵循 Apple ARKit 標準的 Blendshapes。以下是基於其名稱和標準定義的分類，用於指導情緒表達和基礎說話動畫的實現：

**1. 基礎說話嘴型 (Core Speaking Shapes):**
   - `jawOpen`: 控制下巴張開程度，核心。
   - `mouthClose`: 控制嘴唇閉合，用於非說話狀態。

**2. 情緒表達 (Emotional Expression):**
   - **眉毛 (Brow):**
     - `browDownLeft`, `browDownRight`: 皺眉。
     - `browInnerUp`: 眉毛內側向上（悲傷/擔憂）。
     - `browOuterUpLeft`, `browOuterUpRight`: 眉毛外側向上（驚訝/疑問）。
   - **眼睛 (相關表情 - Eye Emotion-Related):**
     - `eyeSquintLeft`, `eyeSquintRight`: 瞇眼（微笑/厭惡）。
     - `eyeWideLeft`, `eyeWideRight`: 睜大眼睛（驚訝/恐懼）。
   - **臉頰 (Cheek):**
     - `cheekPuff`: 鼓臉頰。
     - `cheekSquintLeft`, `cheekSquintRight`: 臉頰擠壓。
   - **嘴部 (表情 - Mouth Emotion):**
     - `mouthDimpleLeft/Right`: 酒窩（微笑）。
     - `mouthFrownLeft/Right`: 嘴角向下（悲傷）。
     - `mouthLeft/Right`: 嘴巴側移。
     - `mouthLowerDownLeft/Right`: 下唇特定移動。
     - `mouthPressLeft/Right`: 嘴角壓緊。
     - `mouthSmileLeft/Right`: 微笑。
     - `mouthStretchLeft/Right`: 嘴角拉伸。
     - `mouthUpperUpLeft/Right`: 上唇特定移動。
   - **鼻子 (Nose):**
     - `noseSneerLeft`, `noseSneerRight`: 鼻子皺起（厭惡）。
   - **下巴 (表情相關 - Jaw Emotion-Related):**
     - `jawForward`: 下巴前突。
     - `jawLeft`, `jawRight`: 下巴側移。

**3. 精確嘴型同步相關 (Viseme-Related - Bonus):**
   - `mouthFunnel`: 發 'oo' 音。
   - `mouthPucker`: 發 'u' 音。
   - `mouthRollLower`, `mouthRollUpper`: 嘴唇內捲。
   - `mouthShrugLower`, `mouthShrugUpper`: 嘴唇皺起。
   - *(部分基礎/情緒 blendshape 也參與精確嘴型)*

**4. 其他 (輔助真實感 - Others for Realism):**
   - `eyeBlinkLeft/Right`: 眨眼。
   - `eyeLookDown/Up/In/Out Left/Right`: 眼球視線。

**組合效果分析 (預期):**

*   **微笑 + 說話:** `mouthSmile*`, `cheekSquint*` (情緒) + `jawOpen` (說話)。效果應自然，需確定 `jawOpen` 混合策略。
*   **悲傷 + 說話:** `browInnerUp`, `mouthFrown*` (情緒) + `jawOpen` (說話)。
*   **驚訝 + 說話:** `brow*Up*`, `eyeWide*`, 可能微弱 `jawOpen` (情緒) + `jawOpen` (說話)。需處理 `jawOpen` 疊加 (取最大值或說話優先)。
*   **憤怒 + 說話:** `browDown*`, `mouthPress*`/`mouthStretch*`, `noseSneer*` (情緒) + `jawOpen` (說話)。需關注嘴角壓緊與下巴張開的視覺協調。

此分類為後續狀態管理、權重計算和混合策略提供了依據。 