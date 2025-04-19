# 音效模組 (Tone.js 整合) TODO

此文件記錄整合 Tone.js 以實現音效功能的待辦事項。 **開發順序已調整：先做面板 -> 定義API -> 整合後端**

## 1. 前端：音效控制面板 (優先開發)

### 1.1. 建立音效控制面板元件 (用於調試與手動觸發)
-   [ ] **建立 `SoundEffectPanel.tsx`**: 
    -   UI 設計：
        -   建立一個**彈出式 (pop-up)** 的音效控制面板，定位在畫面右下角附近。
        -   **主要功能**: 提供按鈕列表，每個按鈕對應一個預設的綜藝/科幻音效 (如 登場、Whoosh、掌聲、雷射、轉場)。點擊按鈕可立即播放對應音效。
        -   (進階) 顯示總音量控制滑桿 (連接到 `useSoundEffects().setGlobalVolume`)。
        -   (進階) 狀態指示燈 (顯示 `isReady`, `isLoading`)。
        -   (未來擴充) 提供一個輸入框，允許貼上 JSON 指令，模擬後端發送 Combo 指令進行測試。
        -   包含關閉面板的按鈕或機制。
-   [ ] **在佈局元件 (如 `AppUI.tsx`) 中加入觸發圖標**: 
    -   在右下角控制區域 (與聊天/設定圖標一起) 新增一個音效圖標 (例如 🎵 或 🔊)。
    -   綁定點擊事件到該圖標，用於觸發面板的顯示/隱藏。
-   [ ] **在 `appSlice.ts` 中新增狀態管理**: 
    -   加入 `isSoundEffectPanelVisible: boolean` 狀態。
    -   加入 `toggleSoundEffectPanel` action 來切換此狀態。
-   [ ] **在佈局元件中實現條件渲染**: 
    -   根據 `isSoundEffectPanelVisible` 狀態決定是否渲染 `<SoundEffectPanel />`。

### 1.2. 新增核心音效服務與 Hook (支撐面板功能)
-   [ ] **建立 `SoundEffectService.ts`**:
    -   負責初始化 Tone.js (`Tone.start()` 在使用者互動後觸發)。
    -   管理 Tone.Player 實例的字典 (key 為音效 name)。
    -   提供預載音效資源的方法 (`loadSoundEffects`)，接收音效列表 (name -> url)。
    -   **提供播放單個音效的方法** (`playSingleSoundEffect`) 給面板按鈕調用，參數可包括 name 和可選的 volume。
    -   (進階) 提供處理後端 JSON 指令的核心方法 (`playSoundEffectFromCommand`)，接收 `effects` 陣列，處理 `startTime`, `volume` 等參數，並使用 Tone.js 的調度功能安排播放 (供後續 API 整合使用)。
    -   處理 Tone.js 相關錯誤 (資源載入失敗、播放錯誤) 並記錄日誌。
    -   提供設定總音量的方法 (`setGlobalVolume`)。
    -   (可選) 提供停止所有/特定音效的方法。
-   [ ] **建立 `useSoundEffects.ts` Hook**:
    -   作為 `SoundEffectService` 的介面，供元件使用。
    -   返回狀態 (如 `isReady`, `isLoading`, `globalVolume`) 和操作方法 (`playSingleSoundEffect`, `playSoundEffectFromCommand`, `loadSoundEffects`, `setGlobalVolume`)。
    -   在 Hook 初始化時調用 `SoundEffectService` 的初始化和預載邏輯。
    -   處理 AudioContext 解鎖邏輯 (例如，提供一個 `unlockAudioContext` 方法，由主應用在適當時機調用)。

### 1.3. 資源準備與配置 (支撐面板功能)
-   [ ] **收集/製作音效檔案**: 準備 MVP 所需的音效檔案 (登場音, Whoosh, 掌聲, 雷射, 轉場)。
-   [ ] **確定音效檔案存放位置**: 將音效檔案放在 `public/audio/effects/` 目錄下。
-   [ ] **建立音效配置文件**: 在 `src/config/` 或類似位置建立 `soundEffectsConfig.ts`，定義音效列表及其 URL 路徑：
    ```typescript
    export const soundEffects: Record<string, string> = {
      'entrance': '/audio/effects/entrance.mp3',
      'whoosh': '/audio/effects/whoosh.wav',
      'applause': '/audio/effects/applause.mp3',
      'laser': '/audio/effects/laser.wav',
      'transition': '/audio/effects/transition.wav',
      // ... 可擴充
    };
    ```
-   [ ] **在 `SoundEffectService` 中引入配置**，用於預載資源和面板按鈕列表生成。

### 1.4. AudioContext 解鎖 (支撐面板功能)
-   [ ] **在應用啟動或使用者首次互動時觸發 `Tone.start()`**:
    -   找到合適的觸發點，例如使用者點擊「開始直播」按鈕或主畫面的任意點擊事件。
    -   調用 `useSoundEffects().unlockAudioContext()` (如果設計了此方法) 或直接觸發 `SoundEffectService` 中的解鎖邏輯。

## 2. API 定義與面板整合 (第二階段)

-   [ ] **確立 WebSocket 指令格式 (JSON)**:
    -   後端推送的訊息格式：
      ```json
      {
        "type": "audio-effect", // 事件類型
        "payload": {
          "module": "AudioEffect",
          "effects": [
            {
              "name": "entrance",
              "type": "variety", // 前端主要依賴 name，type 供參考
              "params": { "volume": 0.8 },
              "startTime": 0 // 相對於指令接收時間的延遲 (毫秒)
            },
            {
              "name": "applause",
              "type": "variety",
              "params": { "volume": 1.0 },
              "startTime": 1000
            }
            // ... more effects for combo
          ]
        }
      }
      ```
-   [ ] **與後端開發者確認指令格式和事件類型名稱 (`audio-effect`)**。
-   [ ] **修改 `SoundEffectPanel.tsx`** (或其他面板元件):
    -   加入 JSON 輸入框和「執行指令」按鈕。
    -   點擊按鈕時，調用 `useSoundEffects().playSoundEffectFromCommand` 方法，傳入解析後的 JSON `effects` 陣列。
-   [ ] **完善 `SoundEffectService` 中的 `playSoundEffectFromCommand` 方法**，確保能正確處理 startTime 和並發/串行播放。

## 3. 後端整合與 WebSocket (第三階段)

### 3.1. 整合 WebSocket 接收指令
-   [ ] **修改 `WebSocketService.ts` 或相關處理邏輯**:
    -   註冊 `audio-effect` 事件類型處理器。
    -   當收到 `audio-effect` 類型的訊息時，解析 JSON 指令的 `payload`。
    -   調用 `SoundEffectService` 的 `playSoundEffectFromCommand` 方法執行指令。
-   [ ] **確保 `SoundEffectService` 能被 `WebSocketService` 的處理器訪問** (可能需要調整 Service 的實例化或依賴注入方式)。

### 3.2. 後端實現 (與後端開發者協作)
-   [ ] **LangGraph / LLM 邏輯**:
    -   根據對話語意、場景事件或腳本，判斷觸發音效的時機和類型。
    -   生成符合前端 API 定義的 JSON 指令。
-   [ ] **WebSocket 推送**:
    -   實現將生成的音效 JSON 指令透過 WebSocket 推送給前端的邏輯。
    -   確保指令發送給正確的使用者/會話。
-   [ ] **音效列表同步**: 後端需要知道前端支援哪些音效 `name`，以生成有效的指令。

## 4. EventBus / 狀態管理 (視需求評估)

-   [ ] **評估是否需要 EventBus**:
    -   主要音效觸發來自後端推送。EventBus 可能用於前端內部元件間的狀態同步 (例如，某個 UI 操作觸發一個簡單提示音，不經過後端)。
    -   如果需要，可利用現有 Zustand 或實作簡單的 EventBus。
    -   目前架構下，直接由 `WebSocketService` 調用 `SoundEffectService` 可能是最直接的方式。

## 5. 測試 (貫穿各階段)

-   [ ] **前端單元測試**:
    -   測試 `SoundEffectService` 的初始化、資源載入、播放邏輯 (mock Tone.js)。
    -   測試 `useSoundEffects` Hook 的狀態和方法。
    -   測試 WebSocket 接收指令並正確調用播放方法。
-   [ ] **面板功能測試**:
    -   手動點擊面板按鈕，驗證對應音效是否播放。
    -   (進階) 手動輸入 JSON，驗證 Combo 效果是否按時序播放。
-   [ ] **整合測試**:
    -   手動觸發後端發送指令，驗證前端是否按預期播放音效 (包括音量、延遲)。
    -   測試音效與語音 (`AudioService` 播放的 AI 語音) 是否能同時播放且音量協調。
-   [ ] **端對端測試**:
    -   模擬完整直播場景 (開場、互動、轉場)，驗證後端 LLM -> 指令生成 -> WebSocket 推送 -> 前端接收 -> Tone.js 播放的完整流程。
    -   在不同瀏覽器和裝置上測試。

## 附註

*   後端實現細節需與後端開發者進一步討論。
*   測試應貫穿整個開發過程。 