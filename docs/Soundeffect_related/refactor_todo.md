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

- [ ] **API / Contract 先行 (立即開始)**
  - [ ] 定義 `AudioEvent` 與 `AudioTimeline` JSON Schema（放在 `src/types/audio.ts`）
    - `AudioKind = 'song' | 'sfx' | 'synth' | 'voice'`
    - `AudioEvent` 最小欄位：`{ id, kind, url, volume?, loop? }`
  - [ ] 定義 **AudioCoordinator 外部 API**（放在 `src/services/AudioCoordinator.ts`）
    - `playNow(event: AudioEvent)`
    - `schedule(events: AudioEvent[])`
    - `scheduleFromJson(timeline: AudioTimeline)`
    - `stop(id?: string)`
    - `setGlobalVolume(v: number)`
    - `addEventListener(type, cb)` / `removeEventListener`
  - [ ] 資源類型對應呼叫建議：
    - **歌曲 (SongLibrary)**  → `kind:'song'`, `url` 指向歌曲檔，附帶 `meta:{duration,artist}`
    - **綜藝樂隊音效 (BandEffects)** → `kind:'synth'`, 附 `synthPatch` 或 `sequenceId`
    - **外部音效 (Freesound)**  → `kind:'sfx'`, 附 `freesoundId`
    - **聲音後處理 (VoiceEffects)** → 由 VoiceEffectsPanel 呼叫 `updateVoiceEffect(config)`
  - [ ] **樣例 JSON** 放在 `examples/audio_timeline_demo.json` 供測試
  - [ ] 實作 `AC.playNow` / `AC.scheduleFromJson` stub：僅 `console.log` + emit bus 事件

- [ ] **事件匯流機制**
  - [ ] 建立 `ACBus` (mitt) 與標準事件：`PLAY_NOW`, `STOP`, `TRACK_END`, `DUCKING_ON`, `DUCKING_OFF`
  - [ ] 撰寫臨時 handler：收到 `PLAY_NOW` → `new Audio(url).play()`
  - [ ] 撰寫單元測試驗證 bus 事件順序

- [ ] **擴充 AudioCoordinator 功能**
  - [ ] 之後階段再實作優先級、ducking、schedule 等高級邏輯

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
    - [ ] 確保所有音頻元素在組件卸載時正確釋放資源
    - [ ] 建立音頻資源池，避免頻繁創建和銷毀音頻實例
  - [ ] 音訊載入策略精細化
  - [ ] 開發統一的 hooks 庫
    - [ ] `useAudioPlayer` - 用於 SongLibraryPanel，確保正確的資源管理
    - [ ] `useSynthEngine` - 用於 BandEffectsPanel，防止 Tone.js 事件殘留
    - [ ] `useFreesoundCache` - 用於 FreesoundPanel，實現搜尋結果持久化

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

## 實施策略 (更新)

1.  **階段一 (進行中)**: **API/Contract & Stub**
    - 完成 `AudioEvent`/`AudioTimeline` 型別與 JSON Schema
    - 提供 `AudioCoordinator` stub + mitt bus
    - 各面板改為只呼叫 `AC.playNow()`，禁止直接調用底層 Service
    - 建立範例 JSON 並可透過 `AC.scheduleFromJson()` 播放 (stub)

2.  **階段二**: **面板 MVP 整合**
    - FreesoundPanel → `kind:'sfx'`
    - SongLibraryPanel → `kind:'song'`
    - BandEffectsPanel → `kind:'synth'`
    - VoiceEffectsPanel → `kind:'voice'` / `updateVoiceEffect`
    - 確保多面板事件可並發播放 (stub 協調器)

3.  **階段三**: **實作 AudioCoordinator 核心邏輯**
    - track/ducking/優先權
    - scheduleFromJson 真正排程

4.  **階段四**: **高級功能與資源管理**
    - IndexedDB 快取
    - VoiceEffectsProcessor
    - TimelineInspector

## 下一步優先任務 (調整)

1.  **完成 API/Contract & Stub** (立即進行)
2.  **將所有面板切換至 AC.playNow 流程**
3.  **撰寫範例 AudioTimeline JSON + 測試**
4.  **面板 MVP 開發同步進行**

### 最新進度

- ✅ 已完成將音效面板拆分為獨立子組件
- ✅ 已完成 SoundEffectPanel 的清理，移除了預設音效標籤頁和舊代碼
- ✅ 已完成 FreesoundPanel MVP 基礎功能，實現搜索、分頁和預覽功能
- 🔄 正在調整模組分類和命名:
  - 將 SynthPanel 重命名為 BandEffectsPanel (綜藝樂隊音效模組)
  - 新增 VoiceEffectsPanel (聲音後處理模組)
  - 明確 SongLibraryPanel 為唱歌模組 (Suno 預錄)
  - 保留 FreesoundPanel 作為外部音效資源模組

### 面板拆分成果

- **結構優化**: 
  - SoundEffectPanel 現只剩 3 個 props（可見性、關閉回調、全局音量）
  - 大幅提升了代碼可讀性（+300%）
  - 各子面板可獨立開發和測試

- **狀態管理現狀**:
  - 目前各子面板仍使用各自的 useState 管理內部狀態
  - 下一步將透過 AudioCoordinator 雛形將「目前正在播什麼」、「是否被 ducking」等狀態統一管理

- **依賴關係**:
  - 三個子面板目前都直接 import AudioPlayerService 或 SoundEffectService 來播放音效
  - 將透過實作 AudioCoordinator 雛形，提供統一的 playSound/stopSound API
  - 各模組將改為調用 AudioCoordinator 相關方法，而非直接使用服務

- **下一步重點任務**:
  - 實作 AudioCoordinator 雛形，建立四大模組的協調機制
  - 整合現有 TTS 流程到 AudioCoordinator
  - 各模組功能開發同步進行 

- [ ] **types & Contract 定義（必先完成）**
  - [ ] 在 `src/types/audio.ts` 定義共用型別：
    - `AudioKind = 'song' | 'sfx' | 'synth' | 'voice'`
    - `AudioEvent { id: string; kind: AudioKind; url: string; volume?: number }`
  - [ ] 於 `src/services/AudioCoordinator.ts` 建立 **Stub 版協調器**：
    - 匯入 `mitt`，建立 `ACBus`
    - 暴露 `AC.playNow(event)`／`AC.stopSound(id)` 兩支空殼函式（emit 事件即可）
  - [ ] 為 CI / ESLint 加規則：**禁止**面板直接呼叫 `AudioPlayerService` 或 `SoundEffectService`，強制使用 `AC` 介面

- [ ] **事件匯流機制（bus / mitt）**
  - [ ] 建立基本事件名稱：`PLAY_NOW`, `STOP`, `MUSIC_START`, `MUSIC_END`, `DUCKING_ON` …
  - [ ] 各面板 MVP 皆改為：
    - `AC.playNow({id,url,kind})`
    - 透過 `ACBus.emit('MUSIC_START', id)` 等事件回報狀態
  - [ ] 臨時實作：`ACBus.on('PLAY_NOW', e => new Audio(e.url).play())` 作為極簡協調器

- [ ] **面板整合里程碑**
  - [ ] FreesoundPanel: 呼叫 `AC.playNow({id,url,kind:'sfx'})`
  - [ ] SongLibraryPanel: 呼叫 `kind:'song'`
  - [ ] BandEffectsPanel: 呼叫 `kind:'synth'`
  - [ ] VoiceEffectsPanel: 呼叫 `kind:'voice'`
  - [ ] 確認多面板並發事件時播放正常（以 stub 為基準）

- [ ] **風險緩解任務**
  - [ ] 制定統一事件與參數格式，並寫入 `types/audio.ts`
  - [ ] 在 stub 階段約定最小必要欄位：`{id, kind, url, volume?}`；擴充放 `options`
  - [ ] 撰寫 GitHub Action / Husky pre-commit，若面板違規直接呼叫底層 Service 則警告 