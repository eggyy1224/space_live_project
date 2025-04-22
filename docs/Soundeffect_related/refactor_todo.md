# 音效系統重構 TODO 清單

本文件列出音效系統重構的具體任務和步驟，基於重構計畫書中提出的架構變更。分階段實施可確保順利過渡到新架構，同時不影響現有功能。

## 一、前端介面擴展與資源整合（優先級：最高）

- [ ] **重構音效控制面板 (`SoundEffectPanel`)**  
  _目標：將目前龐大的元件拆分為可獨立開發與測試的子模組，並為後續 AudioCoordinator 整合預留插槽。_
  - [ ] **模組化拆分**  
    - [ ] 將原面板拆為三個子元件：`SongLibraryPanel`, `SynthPanel`, `FreesoundPanel`  
    - [ ] 建立 `SoundEffectPanelLayout` 作為頂層容器，僅負責 Tab 與共用狀態傳遞  
  - [ ] **SongLibraryPanel MVP**  
    - [ ] 顯示 `sampleSongs`（或後端 API 回傳）清單：縮圖 / 標題 / 長度  
    - [ ] **(調整)** 使用統一的 `AudioPlayerService` 或直接調用 `AudioCoordinator` API 播放、暫停、跳轉；播放期間自動更新 Coordinator 狀態  
    - [ ] 於列表中標示 `animationCues`，Hover 時高亮對應時間點（方便測試時間軸）  
    - [ ] 測試驗證：點擊播放 => 聲音正常 + Coordinator 狀態切換正確
    - [ ] **(新增)** 將默認音效替換為更豐富的歌曲庫，包含各類風格的音樂資源
    - [ ] **(新增)** 支援音樂的分類顯示和快速篩選功能
    - [ ] **(新增)** 提供歌曲播放時的簡易波形可視化
  - [ ] **SynthPanel MVP**  
    - [ ] 保留 Tone.js 測試按鈕 + JSON 編輯器  
    - [ ] 新增「快速模板」下拉，方便插入常用序列  
    - [ ] 測試驗證：按下模板 → JSON 區域更新 → 執行後可聽見對應音效 (透過 Coordinator)
  - [ ] **VoiceEffectsPanel MVP**  
    - [ ] 顯示內建角色 / 環境預設 (機器人、太空艙、電話、洞穴…)，並包含「原聲」  
    - [ ] 允許即時切換預設並預聽，調整混響、PitchShift、Filter、Distortion 等參數  
    - [ ] 與 `AudioCoordinator` 溝通 (`updateVoiceEffect`) 以動態修改 `voiceEffect` 參數  
    - [ ] 支援輸入自訂 TTS URL 進行效果測試  
    - [ ] (進階) 拖放式效果鏈 UI、預設儲存/載入
  - [ ] **FreesoundPanel MVP**  
    - [ ] 使用 `useFreesoundAPI` 實作搜尋 / 分頁 / 預覽 / 收藏  
    - [ ] 新增「我的收藏」子 Tab，顯示 IndexedDB 快取列表  
    - [ ] 測試驗證：搜尋關鍵字 → 點擊預覽 → 能聽到音效且快取狀態更新

- [ ] **實現音效資源庫**
  - [ ] 建立統一的資源管理系統
    - [ ] 設計音效、歌曲和Freesound資源的統一存儲結構
    - [ ] 實現資源上傳、導入和管理功能
    - [ ] **(新增)** 支持歌曲庫與音效資源的分類標記
  - [ ] 添加本地資源與 Freesound 資源的統一瀏覽
  - [ ] 實現基本的標籤和分類系統
  - [ ] **(新增)** 建立音樂和音效資源的元數據管理系統，包括來源、時長、類型等

- [ ] **建立簡化版時間軸編輯器**
  - [ ] 設計簡單的時間軸 UI 組件
  - [ ] 實現基本的音效排程和預覽功能
  - [ ] 支援音效序列的保存和載入
  - [ ] **(新增)** 集成動畫時間軸編輯，實現聲音和動畫的統一規劃

## 二、後端支援與資源整合（優先級：高）

- [ ] **建立歌曲管理 API**
  - [ ] 創建歌曲上傳和存儲端點
  - [ ] 實現歌曲元數據管理（標題、演出者、時長等）
  - [ ] 添加歌曲搜索和過濾功能
  - [ ] **(新增)** 支持歌曲與表情/動作時間軸數據的關聯存儲

- [ ] **增強 FreeSound 後端代理**
  - [ ] 實現更完整的 Freesound API 覆蓋
  - [ ] 添加資源下載與處理功能
  - [ ] 實現資源緩存和管理
  - [ ] **(新增)** 整合Freesound資源與歌曲庫的統一管理

- [ ] **定義統一的音頻資源標準**
  - [ ] 設計統一的音頻資源 JSON 格式
  - [ ] 建立資源分級 (Tier-0/1/2) 的配置結構
  - [ ] 實現資源驗證和處理工具
  - [ ] **(新增)** 支持多種音頻來源的標準化處理流程

## 三、核心架構設計（優先級：高）

- [ ] **定義 AudioTimeline JSON 格式**
  - [ ] 設計完整的 JSON Schema，包含時間、類型（`tts`, `song`, `sfx` 等）、資源（ID, URL, Freesound ID）、參數（音量, 循環）等字段。
  - [ ] 建立範例集，涵蓋各種音訊事件場景（後端 TTS 回應、前端歌曲播放、UI 音效）。
  - [ ] 實現基本的驗證器確保 JSON 結構符合要求。
  - [ ] **(關鍵)** 包含觸發表情/動作的 `animationCues` 數據結構 (可選)，供後續高層協調使用。
  - [ ] 明確區分需要表情動畫的聲音事件 (`voice`) 與純音效事件 (`sfx`) 的 `track` 或 `pipeline` 屬性。

- [ ] **實作 AudioCoordinator（統一聲音管線）** <!-- 原 TimelineCoordinator -->
  - [ ] 建立 `src/services/AudioCoordinator.ts` (或沿用 TimelineService.ts 結構)，內含：
    - [ ] `AudioEvent` 型別（基於 AudioTimeline JSON 格式）
    - [ ] 單例 `AudioCoordinator`，提供 API：
      - `scheduleFromJson(json: AudioTimeline): void` - 解析 JSON 並排程事件。
      - `playNow(event: AudioEvent): void` - 立即播放單一事件。
      - `pause()`, `resume()`, `stop()`, `seek()` 等控制方法。
      - `getEvents(): AudioEvent[]` - 獲取當前排程的事件列表。
      - `getPlayhead(): number` - 獲取當前播放頭時間。
      - `isCoordinatorRunning(): boolean` - 獲取運行狀態。
    - [ ] `connectVoiceSource(node: AudioNode): void` - 將任意語音 AudioNode 連接到 `VoiceEffectsProcessor`  
    - [ ] `updateVoiceEffect(config: VoiceEffectConfig): void` - 即時更新語音效果參數
  - [ ] **事件觸發邏輯 `triggerEvent(event: AudioEvent)`：**
    - 根據 `event.type` / `track` 呼叫相應服務：
      - `tts`/`song` (`voice` track) → `AudioService.playAudio()` (可能需要重構 AudioService 以接受 URL/Blob)
      - `sfx` (`sfx` track) → `SoundEffectService.playSingleSoundEffect()`
      - 若 `event.track === 'voice'` 且包含 `voiceEffect`，將效果參數傳遞給 `VoiceEffectsProcessor`
  - [ ] **後端 TTS 整合：**
    - `WebSocketService` 收到後端 TTS 回應 (含音檔 URL 和文字) 後，轉換為 `AudioTimeline` JSON。
    - 調用 `AudioCoordinator.scheduleFromJson()` 處理。
    - (需與後端溝通確認最終 JSON 格式)
  - [ ] 提供狀態給 `TimelineInspector` (見第九部分)。

- [ ] **重構 SoundEffectManager/Service**
  - [ ] 聚焦於音效資源管理 (Tone.js、原生音效) 和基礎播放。
  - [ ] 移除排程邏輯，由 `AudioCoordinator` 負責。
  - [ ] 提供清晰的 API 供 `AudioCoordinator` 調用。
  - [ ] **實作 VoiceEffectsProcessor 服務**  
    - [ ] 建立 `src/services/VoiceEffectsProcessor.ts`，管理 Tone.js 效果器、處理鏈及輸出  
    - [ ] 提供 `applyPreset`, `resetEffects`, `setEffectParameter`, `connectInput(node)` API  
    - [ ] 支援角色/環境預設與 JSON 參數

## 四、語音與音效系統整合（優先級：高）

- [ ] **統一語音與音效播放管線 (由 AudioCoordinator 實現)**
  - [X] **創建口型與動作同步的標準化資料結構** (已定義 AnimationCue 接口並用於歌曲)
  - [ ] **解決音頻衝突問題** (後端 TTS vs 前端歌曲)
    - [ ] 在 `AudioCoordinator` 中實現協調策略（例如：互斥播放、自動降低背景音量 ducking、優先級系統）。

- [ ] **實現自動音量調整 (在 AudioCoordinator 中)**
  - [ ] 添加語音播放時背景音量自動降低 (ducking) 功能 (處理 `voice` vs `sfx` track)。
  - [ ] 實現音效與語音混合時的優先級系統。

- [ ] **合成語音調整功能**
  - [ ] 使用 Tone.js 效果器應用於TTS語音，實現音色調整
  - [ ] 支持語音的音高、音調和效果處理
  - [ ] 提供預設的語音效果組合（如機器人聲、空間感等）
  - [ ] 整合至 `AudioCoordinator` 的 `voice` track 處理流程

- [ ] **與 `VoiceEffectsPanel` 互動：即時調整效果**

## 五、資源管理與快取系統（優先級：中）

- [ ] **實現 FreeSound 資源分級**
  - [ ] 設計 Tier-0/1/2 資源分類標準
  - [ ] 建立資源元數據資料庫
  - [ ] 實現基於使用頻率的自動級別調整

- [ ] **開發快取機制**
  - [ ] 實現 IndexedDB 儲存體系
  - [ ] 建立資源下載與驗證流程
  - [ ] 設計快取淘汰策略與空間管理
  - [ ] 添加音訊解碼與預處理功能

- [ ] **離線支援功能**
  - [ ] 實現必要資源的離線可用性
  - [ ] 建立資源可用性檢查機制
  - [ ] 處理網絡中斷情況下的降級策略

## 六、進階功能與優化（優先級：中）

- [ ] **Combo 音效系統**
  - [ ] 實現 Combo 音效定義與管理
  - [ ] 開發 Combo 編輯工具
  - [ ] 建立 Combo 測試與調整界面

- [ ] **背景音樂功能增強**
  - [ ] 實現跨場景背景音樂淡入淡出
  - [ ] 支援節拍同步的音效觸發
  - [ ] 添加模式切換（環境音與歌曲切換）

- [ ] **效能優化**
  - [ ] 音訊處理線程優化
  - [ ] 記憶體使用優化
  - [ ] 音訊載入策略精細化

## 七、文檔與測試（優先級：低）

- [ ] **文檔與示例**
  - [ ] 更新 API 文檔
  - [ ] 建立開發者指南
  - [ ] 創建常見場景的使用示例

- [ ] **監控與診斷工具**
  - [ ] 實現音效系統狀態監控
  - [ ] 建立效能指標收集
  - [ ] 設計診斷與調試介面

- [ ] **整合測試**
  - [ ] 設計端到端測試案例
  - [ ] 驗證前後端通訊的穩定性與正確性
  - [ ] 壓力測試大量音效事件並發情況

## 八、聲音分類與表情動畫協調（優先級：高）

- [ ] **聲音類型分類系統**
  - [ ] 在 `AudioTimeline` JSON 格式中體現分類 (e.g., `track: 'voice' | 'sfx'`)。
  - [ ] `AudioCoordinator` 根據分類執行不同邏輯 (e.g., ducking)。

- [ ] **雙管線協調機制 (由 AudioCoordinator 實現)**
  - [ ] Voice Pipeline (`voice` track) vs SFX Pipeline (`sfx` track)。
  - [ ] `AudioCoordinator` 負責實現管線間優先權、衝突處理。

- [ ] **表情動畫同步系統**
  - [X] **設計聲音-表情映射標準** (已定義 AnimationCue 接口並用於歌曲)
  - [ ] **(調整)** `AudioCoordinator` 在觸發 `voice` 事件時，根據 `animationCues` 呼叫 `HeadService`/`BodyService`。 (注意：此處僅觸發，非管理)
  - [ ] **(未來考量)** 是否需要更高層級的 `MasterCoordinator` 來精確同步 Audio, Head, Body？
  - [ ] **(新增)** 強化動畫與聲音的整合，實現更準確的表情與歌詞/語音同步
  - [ ] **(新增)** 支持情緒狀態與歌曲風格的智能映射
  - [ ] **(新增)** 為歌曲庫中的歌曲增加動畫時間軸編輯功能

- [ ] **統一事件系統**
  - [ ] `AudioCoordinator` 應能發出事件 (e.g., `onEventStart`, `onEventEnd`, `onTimelineEnd`) 供 UI 或其他系統訂閱。

## 九、開發與調試工具（優先級：中）

- [ ] 性能計數器：顯示每秒音效/服務呼叫統計。
- [ ] 錄製 / 匯出 TimelineEvents 到 JSON，用於回歸測試。
- [ ] **TimelineInspector（開發/調試工具）** <!-- 移至此處，待 AudioCoordinator 完成後實施 -->
  _目標：提供 AudioCoordinator 事件流的即時視覺化與除錯能力。_
  - [ ] React + CSS Grid 實作簡易時間軸視圖（多軌：Voice / SFX / Expression / Action）。
  - [ ] 從 `AudioCoordinator` 讀取事件列表 (`getEvents()`) 與播放頭位置 (`getPlayhead()`)，每 1/30 秒更新。
  - [ ] 點擊事件可跳出 payload 詳情。
  - [ ] 提供發送測試 JSON 到 `AudioCoordinator.scheduleFromJson()` 的功能。
  - [ ] 透過左下角 toggle 按鈕控制顯示。
  - [ ] **(新增)** 支持音頻波形與音量可視化顯示

## 實施策略

重構應採用漸進式方法，確保核心功能優先實現：

1.  **階段一 (進行中)**: **重構 `SoundEffectPanel`** → 模組化拆分 (SongLibrary / Synth / Freesound)，準備與 Coordinator 對接。
2.  **階段二**: **設計並實作 `AudioCoordinator` MVP** → 核心 API (`scheduleFromJson`, `playNow` 等)、`AudioTimeline` JSON 格式定義、整合 TTS/歌唱/SFX 基礎播放邏輯。
3.  **階段三**: **後端 TTS 協作改造** → 與後端確認並實現透過 WebSocket 傳輸 `AudioTimeline` JSON。
4.  **階段四**: **`SoundEffectPanel` 與 `AudioCoordinator` 串接** → 驗證所有聲音來源皆由 Coordinator 控制。
5.  **階段五**: **恢復並增強 `TimelineInspector`** → 作為 `AudioCoordinator` 的調試工具，可發送測試 JSON。
6.  **階段六**: 實現聲音分類、雙管線協調（ducking、衝突處理）、表情動作觸發（初步）。
7.  **階段七**: **整合語音效果處理** → 實作 `VoiceEffectsProcessor`、`VoiceEffectsPanel`，加入 AudioNode 路由支援。
8.  **階段八**: 完善資源管理、進階功能與效能優化。

## 下一步優先任務

1.  **重構 `SoundEffectPanel`（拆分子元件）並推出 `SongLibraryPanel` MVP**。
2.  **設計並實作 `AudioCoordinator` MVP**（API 骨架、JSON 格式草案、基礎事件觸發）。
3.  **定義 `AudioTimeline` JSON 格式**，並與後端溝通確認 TTS 回應格式。
4.  **將 `SoundEffectPanel` (初步) 與 `AudioCoordinator` 串接**，驗證基本播放。
5.  **重新啟用 `TimelineInspector`**，用於測試 `AudioCoordinator`。
6.  強化 Freesound 整合與歌曲庫。
7.  建立聲音分類系統與雙管線協調機制。
8.  擴充 SynthPanel；完成 VoiceEffectsPanel & Processor 與 Coordinator 的整合。

這個順序將確保先實現對前端用戶有用的功能，同時為後續的深度架構重構打下基礎。 

### 調整重點 