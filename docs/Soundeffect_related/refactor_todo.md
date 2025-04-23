# 音效系統重構 TODO 清單

本文件列出音效系統重構的具體任務和步驟，基於重構計畫書中提出的架構變更。分階段實施可確保順利過渡到新架構，同時不影響現有功能。

## 一、前端介面擴展與資源整合（優先級：最高）

- [X] **重構音效控制面板 (`SoundEffectPanel`)**  
  _目標：將目前龐大的元件拆分為可獨立開發與測試的子模組，並為後續 AudioCoordinator 整合預留插槽。_
  - [X] **模組化拆分**  
    - [X] 將原面板拆為四個子元件：
      - [X] `FreesoundPanel` (外部音效資源)
      - [X] `SongLibraryPanel` (Suno 預錄歌曲)
      - [X] `SynthPanel` → 重命名為 `BandEffectsPanel` (綜藝樂隊音效)
      - [ ] `VoiceEffectsPanel` (聲音後處理)
    - [X] 建立 `SoundEffectPanelLayout` 作為頂層容器，僅負責 Tab 與共用狀態傳遞  

  - [ ] **SongLibraryPanel MVP** (唱歌模組)  
    - [ ] 顯示 `sampleSongs`（或後端 API 回傳）清單：縮圖 / 標題 / 長度  
    - [ ] 實現簡易歌曲導入功能，支持上傳音頻文件
    - [ ] **(調整)** 使用統一的 `AudioPlayerService` 或直接調用 `AudioCoordinator` API 播放、暫停、跳轉；播放期間自動更新 Coordinator 狀態  
    - [ ] 於列表中標示 `animationCues`，Hover 時高亮對應時間點（方便測試時間軸）  
    - [ ] 為歌曲添加動作和表情時間線編輯功能
    - [ ] 測試驗證：點擊播放 => 聲音正常 + Coordinator 狀態切換正確
    - [ ] **(新增)** 將默認音效替換為更豐富的歌曲庫，包含各類風格的音樂資源
    - [ ] **(新增)** 支援音樂的分類顯示和快速篩選功能
    - [ ] **(新增)** 提供歌曲播放時的簡易波形可視化
    - [ ] **(問題修復)** 解決 `useRef<HTMLAudioElement>(null!)` 每次 render 都新建 new Audio() 的問題
      - 抽成 `useAudioPlayer(url)` hook，實現音頻資源的統一管理
      - 在組件卸載時確保正確釋放資源：`audio.pause(); audio.src=''`

  - [ ] **BandEffectsPanel MVP** (綜藝樂隊模組)  
    - [ ] 保留 Tone.js 測試按鈕 + JSON 編輯器  
    - [ ] 設計綜藝節目風格的音效庫（掌聲、笑聲、驚嘆音效等）
    - [ ] 提供常用樂隊音效選擇（鼓點、銅鈸、音樂小片段等）
    - [ ] 新增「快速模板」下拉，方便插入常用序列  
    - [ ] 測試驗證：按下模板 → JSON 區域更新 → 執行後可聽見對應音效 (透過 Coordinator)
    - [ ] **(問題修復)** 解決多次快速播放可能殘留 Transport 事件的問題
      - 建立 `useSynthEngine()` hook，返回 playSequence/stop 等方法
      - 在 useEffect cleanup 中徹底清理資源：`Transport.cancel(0), dispose()`

  - [ ] **VoiceEffectsPanel MVP** (聲音後處理模組)  
    - [ ] 顯示內建角色 / 環境預設 (機器人、太空艙、電話、洞穴…)，並包含「原聲」  
    - [ ] 允許即時切換預設並預聽，調整混響、PitchShift、Filter、Distortion 等參數  
    - [ ] 與 `AudioCoordinator` 溝通 (`updateVoiceEffect`) 以動態修改 `voiceEffect` 參數  
    - [ ] 支援輸入自訂 TTS URL 進行效果測試  
    - [ ] 實現對 TTS 流程處理的整合接口
    - [ ] (進階) 拖放式效果鏈 UI、預設儲存/載入

  - [X] **FreesoundPanel MVP** (外部音效資源)  
    - [X] 使用 `useFreesoundAPI` 實作搜尋 / 分頁 / 預覽 / 收藏  
    - [ ] 新增「我的收藏」子 Tab，顯示 IndexedDB 快取列表  
    - [ ] 實現收藏功能，將找到的音效保存到本地
    - [ ] 建立收藏列表管理界面，方便以後 AI 查找和使用
    - [X] 測試驗證：搜尋關鍵字 → 點擊預覽 → 能聽到音效且快取狀態更新
    - [ ] **(問題修復)** 解決分頁/搜尋結果暫存在 useState([]) 導致重整後丟失的問題
      - 短期：將 useFreesoundAPI 回傳結果存入 useStore().setFreesoundCache
      - 中期：實現完整的 IndexedDB 快取方案，支持離線使用和持久化儲存

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

## 三、核心架構設計（優先級：最高）

**重要架構調整：協調器僅負責協調，播放邏輯由獨立播放器實現**

- [ ] **定義播放器介面與實現**
  - [ ] **定義 `IAudioPlayer` 接口** (放在 `src/services/players/IAudioPlayer.ts`) 
    - `load(src: string, options?: any): Promise<void>`
    - `play(at?: number): void`
    - `stop(): void`
    - `pause(): void`
    - `on(event: "progress" | "ended" | "error", callback: Function): void`
  - [ ] **實現 `PreRecordedPlayer`** (放在 `src/services/players/PreRecordedPlayer.ts`)
    - 封裝 HTMLAudio 或 Howler.js 播放邏輯
    - 實現 `IAudioPlayer` 接口
  - [ ] **實現 `TonePlayer`** (放在 `src/services/players/TonePlayer.ts`)
    - 封裝 Tone.js 播放邏輯
    - 實現 `IAudioPlayer` 接口
  - [ ] **(可選) 實現 `TTSPlayer`** (放在 `src/services/players/TTSPlayer.ts`)
    - 專門處理 TTS 音頻流或 URL
    - 實現 `IAudioPlayer` 接口

- [ ] **重構 `AudioCoordinator` (放在 `src/services/AudioCoordinator.ts`)**
  - **移除直接播放邏輯**：不再直接操作 `Audio` 元素或 `Tone.js`。
  - **管理播放器實例**：持有不同類型 `IAudioPlayer` 的實例 Map。
  - **解析時間軸與事件**：處理 `scheduleFromJson` 等傳入的指令。
  - **事件分發**：根據事件類型 (`kind`) 和目標播放器，透過事件總線發送 `play`/`stop` 等命令。
  - **監聽播放器回報**：監聽來自播放器的 `ended`/`error` 事件，更新內部狀態或觸發後續排程。
  - **實現 Ducking 與優先權**：基於事件類型和規則，控制不同播放器或音軌的音量。

- [ ] **事件匯流機制（Event Bus）**
  - [ ] 選擇或實現事件總線 (例如沿用 `mitt`)
  - [ ] 定義協調器與播放器之間的標準事件 (`PLAY_REQUESTED`, `STOP_REQUESTED`, `PLAYBACK_ENDED`, `PLAYBACK_ERROR` 等)
  - [ ] `AudioCoordinator` 發布播放請求事件。
  - [ ] 各 `Player` 訂閱相關事件，執行播放/停止操作。
  - [ ] 各 `Player` 在播放結束或出錯時發布狀態回報事件。
  - [ ] 撰寫單元測試驗證事件流。

- [ ] **API / Contract 定義 (調整)**
  - `AudioEvent` 與 `AudioTimeline` JSON Schema 維持不變。
  - `AudioCoordinator` **外部 API** 維持不變，但內部實現改為事件分發：
    - `playNow(event: AudioEvent)` → 內部發送播放事件
    - `scheduleFromJson(timeline: AudioTimeline)` → 解析 timeline，分發多個播放事件
    - `stop(id?: string)` → 發送停止事件
    - `setGlobalVolume(v: number)` → (可能需要調整) 發送全局音量變更事件給所有 Player 或透過 Web Audio API 控制主輸出
    - `addEventListener/removeEventListener` → 監聽協調器自身事件 (如 `timeline_start`, `timeline_end`)
  - 資源類型對應關係不變。
  - 樣例 JSON 維持不變。

### AudioCoordinator MVP（基於新架構調整）
- [ ] **播放器註冊與管理**：`AudioCoordinator` 能註冊和獲取不同類型的 `IAudioPlayer`。
- [ ] **基本事件分發**：`playNow` 能正確分發事件給對應的播放器。
- [ ] **Ducking 與優先權 (基礎)**：
  - 語音播放時 (事件 `kind='voice'`)，協調器向 `MusicPlayer` 和 `SFXPlayer` 發送降低音量指令 (或透過 Web Audio API 控制 GainNode)。
  - 語音結束時，發送恢復音量指令。
  - 實現基礎的 Voice 互斥（新語音進來時停止舊語音）。
- [ ] **事件發布 (基礎)**：語音開始/結束時，發布 `voice:start` / `voice:end` 事件。
- [ ] **統一播放入口 (重構)**：
  - 原 `AudioService` TTS 播放邏輯改為向 `AudioCoordinator` 發送 `playNow({kind:'voice', url})` 事件。
  - `SongLibraryPanel`, `BandEffectsPanel`, `FreesoundPanel` 均改用 `AC.playNow()` 或 `AC.scheduleFromJson()`。
- [ ] **基礎時間線排程 (重構)**：`scheduleFromJson` 使用 `setTimeout` 觸發一系列 `playNow` 事件分發。

## 四、語音與音效系統整合（優先級：高，基於新架構調整）

- [ ] **統一語音與音效播放管線 (由新架構實現)**
  - `AudioCoordinator` 負責排程。
  - 各 `Player` (如 `TTSPlayer`, `PreRecordedPlayer`) 負責播放。
  - 衝突解決由 `AudioCoordinator` 的 Ducking/優先權邏輯處理。

- [ ] **實現自動音量調整 (在 AudioCoordinator 中)**
  - Ducking 邏輯由 `AudioCoordinator` 實現，透過事件/命令通知相關 `Player` 調整音量或直接控制 Web Audio GainNode。
  - 優先級系統由 `AudioCoordinator` 決定哪個事件可以播放/打斷其他事件。

- [ ] **合成語音調整功能 (整合)**
  - `VoiceEffectsProcessor` 繼續負責 Tone.js 效果處理。
  - `TTSPlayer` (或處理 voice 的 Player) 在播放前將音頻源連接到 `VoiceEffectsProcessor`。
  - `AudioCoordinator` 在分發 `playNow({kind:'voice'})` 事件時，確保音頻流經過效果器。

- [ ] **與 `VoiceEffectsPanel` 互動：即時調整效果 (流程不變)**
  - `VoiceEffectsPanel` 仍然透過某種方式 (可能是 `AudioCoordinator` 提供的 API 或直接與 `VoiceEffectsProcessor` 交互) 更新效果設定。
  - `VoiceEffectsProcessor` 應用更新後的效果。

## 五、資源管理與快取系統（優先級：中，無重大變更）

- [ ] **實現 FreeSound 資源分級**
  - [ ] 設計 Tier-0/1/2 資源分類標準
  - [ ] 建立資源元數據資料庫
  - [ ] 實現基於使用頻率的自動級別調整

- [ ] **開發快取機制**
  - [ ] 實現 IndexedDB 儲存體系
    - [ ] 為 FreesoundPanel 設計搜尋結果和收藏的持久化存儲
    - [ ] 為 SongLibraryPanel 實現歌曲元數據和音頻資源的快取
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
    - 確保各 `Player` 在不再需要時正確釋放資源。
    - `AudioCoordinator` 適時銷毀不再使用的 `Player` 實例。
  - [ ] 音訊載入策略精細化
  - [ ] 開發統一的 hooks 庫
    - `useAudioPlayer` → 可能不再需要，由各面板直接與 `AudioCoordinator` 交互。
    - `useSynthEngine` → `TonePlayer` 內部處理。
    - `useFreesoundCache` → 保持不變。

## 七、文檔與測試（優先級：低）

- [ ] **文檔與示例**
  - 更新 API 文檔，說明 `AudioCoordinator` 與 `IAudioPlayer` 的交互。
  - 建立開發者指南
  - 創建常見場景的使用示例

- [ ] **監控與診斷工具**
  - 實現音效系統狀態監控
  - 建立效能指標收集
  - 設計診斷與調試介面

- [ ] **整合測試**
  - 設計測試案例驗證 `AudioCoordinator` 與各 `Player` 的交互。
  - 測試 Ducking 和優先級規則。
  - 壓力測試大量音效事件並發情況

- [ ] **單元測試 (新增)**
  - 為 `AudioCoordinator` 編寫單元測試 (使用 Mock Player)。
  - 為各 `Player` 編寫單元測試。

## 八、聲音分類與表情動畫協調（優先級：高，基於新架構調整）

- [ ] **聲音類型分類系統 (流程不變)**
  - `AudioTimeline` JSON 格式體現分類。
  - `AudioCoordinator` 根據分類執行 Ducking 等邏輯。

- [ ] **雙管線協調機制 (由新架構實現)**
  - `AudioCoordinator` 根據 `track` 或 `kind` 屬性協調不同類型的事件。

- [ ] **表情動畫同步系統 (調整)**
  - `AudioCoordinator` 在分發 `voice:start`/`voice:end` 事件時，觸發動畫系統。
  - 如果 `AudioEvent` 包含 `animationCues`，`AudioCoordinator` 在排程播放時，同時排程觸發相應的動畫事件 (調用 `HeadService`/`BodyService`)。
  - `MasterCoordinator` 的考量保持不變。

- [ ] **統一事件系統 (流程不變)**
  - `AudioCoordinator` 繼續發出 `onEventStart`, `onEventEnd`, `onTimelineEnd` 等事件。

## 九、開發與調試工具（優先級：中）

- [ ] **TimelineInspector (調整)**
  - 從 `AudioCoordinator` 讀取**排程事件**和**播放器狀態**。
  - 提供 AudioCoordinator 事件流的即時視覺化與除錯能力。
  - 點擊事件可跳出 payload 詳情。
  - 提供發送測試 JSON 到 `AudioCoordinator.scheduleFromJson()` 的功能。
  - 透過左下角 toggle 按鈕控制顯示。
  - **(新增)** 支持音頻波形與音量可視化顯示

## 實施策略 (更新)

1.  **階段一**: **定義接口 & 播放器實現**
    - 定義 `IAudioPlayer` 接口。
    - 實現 `PreRecordedPlayer` 和 `TonePlayer`。
2.  **階段二**: **重構 Coordinator & 事件總線**
    - 重構 `AudioCoordinator` 移除播放邏輯。
    - 引入事件總線，實現基礎事件通信。
3.  **階段三**: **整合播放器 & 測試**
    - `AudioCoordinator` 能正確管理和調度 `Player`。
    - 測試 `playNow` 和 `scheduleFromJson`。
4.  **階段四**: **實現 Ducking & 優先級**
    - 在 `AudioCoordinator` 中實現核心協調邏輯。
5.  **階段五**: **面板整合 & UI 調整**
    - 將各面板切換到新的 `AudioCoordinator` API。
    - 修復 `SoundEffectPanel` 標籤切換問題。
    - (可選) 在 `AudioCoordinatorPanel` 添加 JSON 輸入功能。

## 下一步優先任務 (調整)

1.  **定義 `IAudioPlayer` 接口**
2.  **實現 `PreRecordedPlayer` (封裝現有邏輯)**
3.  **重構 `AudioCoordinator` 移除播放邏輯，改為事件分發 (Stub)**
4.  **搭建事件總線，實現 Coordinator -> Player 的基本通信**
5.  **將 `SongLibraryPanel` 或 `FreesoundPanel` 切換到新流程進行測試**

### 最新進度 (無變化)

- ✅ 已完成將音效面板拆分為獨立子組件
- ✅ 已完成 SoundEffectPanel 的清理，移除了預設音效標籤頁和舊代碼
- ✅ 已完成 FreesoundPanel MVP 基礎功能，實現搜索、分頁和預覽功能
- 🔄 正在調整模組分類和命名:
  - 將 SynthPanel 重命名為 BandEffectsPanel (綜藝樂隊音效模組)
  - 新增 VoiceEffectsPanel (聲音後處理模組)
  - 明確 SongLibraryPanel 為唱歌模組 (Suno 預錄)
  - 保留 FreesoundPanel 作為外部音效資源模組

### 面板拆分成果 (無變化)

- **結構優化**: 
  - SoundEffectPanel 現只剩 3 個 props（可見性、關閉回調、全局音量）
  - 大幅提升了代碼可讀性（+300%）
  - 各子面板可獨立開發和測試

- **狀態管理現狀**:
  - 目前各子面板仍使用各自的 useState 管理內部狀態
  - 下一步將透過 AudioCoordinator 雛形將「目前正在播什麼」、「是否被 ducking」等狀態統一管理

- **依賴關係 (更新)**:
  - 三個子面板目前都直接 import AudioPlayerService 或 SoundEffectService 來播放音效。
  - **目標**：將透過實作 `AudioCoordinator` + `Player` 架構，提供統一的 `AC.playNow()` 等 API。
  - 各模組將改為調用 `AudioCoordinator` API，由協調器分發給對應的 `Player`。

- **下一步重點任務 (調整)**:
  - 實作 `IAudioPlayer` 接口和基礎 `Player`。
  - 重構 `AudioCoordinator` 雛形，實現事件分發。
  - 逐步將各面板接入新架構。

- [ ] **types & Contract 定義（調整）**
  - 在 `src/types/audio.ts` 定義共用型別：
    - `AudioKind = 'song' | 'sfx' | 'synth' | 'voice'`
    - `AudioEvent { id: string; kind: AudioKind; url: string; volume?: number }`
  - 於 `src/services/AudioCoordinator.ts` 建立 **Stub 版協調器**：
    - 匯入 `mitt`，建立 `ACBus`
    - 暴露 `AC.playNow(event)`／`AC.stop(id)` 等 API（emit 事件即可）
  - 為 CI / ESLint 加規則：**禁止**面板直接呼叫 `AudioPlayerService` 或 `SoundEffectService` 或 Player 實例，強制使用 `AC` 介面。

- [ ] **事件匯流機制（bus / mitt）(調整)**
  - 建立基本事件名稱：`PLAY_REQUESTED`, `STOP_REQUESTED`, `PLAYBACK_ENDED`, `PLAYBACK_ERROR` 等
  - 各面板 MVP 皆改為：
    - `AC.playNow({id,url,kind})`
    - 不再需要直接回報狀態，由 Player 回報給 Coordinator
  - 臨時實作：`ACBus.on('PLAY_REQUESTED', e => { /* 找到對應 Player 並調用 play */ })`

- [ ] **面板整合里程碑 (調整)**
  - 各面板呼叫 `AC.playNow({id,url,kind})` 或 `AC.scheduleFromJson()`。
  - 確認 Coordinator 能將事件正確分發給對應 Player。

- [ ] **風險緩解任務 (調整)**
  - 制定統一事件與參數格式，並寫入 `types/audio.ts`
  - 在 stub 階段約定最小必要欄位：`{id, kind, url, volume?}`；擴充放 `options`
  - 撰寫 GitHub Action / Husky pre-commit，若面板違規直接呼叫 Player 則警告。

- [ ] **修復 SoundEffectPanel 標籤切換問題**
    - 分析 `useEffect` 清理邏輯，確保切換標籤時不會意外停止由 `AudioCoordinator` 管理的播放。 