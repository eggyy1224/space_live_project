# 音效系統重構 TODO 清單

本文件列出音效系統重構的具體任務和步驟，基於重構計畫書中提出的架構變更。分階段實施可確保順利過渡到新架構，同時不影響現有功能。

## 一、前端介面擴展與資源整合（優先級：最高）

- [ ] **重構音效控制面板 (`SoundEffectPanel`)**  
  _目標：將目前龐大的元件拆分為可獨立開發與測試的子模組，並為後續時間軸整合預留插槽。_
  - [ ] **模組化拆分**  
    - [ ] 將原面板拆為三個子元件：`SongLibraryPanel`, `SynthPanel`, `FreesoundPanel`  
    - [ ] 建立 `SoundEffectPanelLayout` 作為頂層容器，僅負責 Tab 與共用狀態傳遞  
    - [ ] 透過 Storybook/Dev Route 為每個子元件建立獨立測試場景（驗證 UI 與功能）
  - [ ] **SongLibraryPanel MVP**  
    - [ ] 顯示 `sampleSongs`（或後端 API 回傳）清單：縮圖 / 標題 / 長度  
    - [ ] 使用 `AudioPlayerService` 播放、暫停、跳轉；播放期間自動設定 `isSpeaking=true`，結束時復原  
    - [ ] 於列表中標示 `animationCues`，Hover 時高亮對應時間點（方便測試時間軸）  
    - [ ] 測試驗證：點擊播放 => 聲音正常 + `isSpeaking` 狀態切換正確
  - [ ] **SynthPanel MVP**  
    - [ ] 保留 Tone.js 測試按鈕 + JSON 編輯器  
    - [ ] 新增「快速模板」下拉，方便插入常用序列  
    - [ ] 測試驗證：按下模板 → JSON 區域更新 → 執行後可聽見對應音效
  - [ ] **FreesoundPanel MVP**  
    - [ ] 使用 `useFreesoundAPI` 實作搜尋 / 分頁 / 預覽 / 收藏  
    - [ ] 新增「我的收藏」子 Tab，顯示 IndexedDB 快取列表  
    - [ ] 測試驗證：搜尋關鍵字 → 點擊預覽 → 能聽到音效且快取狀態更新

- [ ] **TimelineInspector（開發模式）**  
  _目標：提供時間軸即時視覺化與除錯能力，可持續驗證 TimelineCoordinator 行為。_
  - [ ] React + CSS Grid 實作簡易時間軸視圖（多軌：Voice / SFX / Expression / Action）  
  - [ ] 從 `TimelineCoordinator` 讀取事件列表與播放頭位置，每 1/30 秒更新  
  - [ ] 點擊事件可跳出 payload 詳情（名稱、參數）  
  - [ ] （調整中）改為面板右下角/左下角 toggle 按鈕控制顯示，可於正式環境透過開關啟用

- [ ] **實現音效資源庫**
  - [ ] 建立統一的資源管理系統
    - [ ] 設計音效和歌曲的統一存儲結構
    - [ ] 實現資源上傳、導入和管理功能
  - [ ] 添加本地資源與 Freesound 資源的統一瀏覽
  - [ ] 實現基本的標籤和分類系統

- [ ] **建立簡化版時間軸編輯器**
  - [ ] 設計簡單的時間軸 UI 組件
  - [ ] 實現基本的音效排程和預覽功能
  - [ ] 支援音效序列的保存和載入

## 二、後端支援與資源整合（優先級：高）

- [ ] **建立歌曲管理 API**
  - [ ] 創建歌曲上傳和存儲端點
  - [ ] 實現歌曲元數據管理（標題、演出者、時長等）
  - [ ] 添加歌曲搜索和過濾功能

- [ ] **增強 FreeSound 後端代理**
  - [ ] 實現更完整的 Freesound API 覆蓋
  - [ ] 添加資源下載與處理功能
  - [ ] 實現資源緩存和管理

- [ ] **定義統一的音頻資源標準**
  - [ ] 設計統一的音頻資源 JSON 格式
  - [ ] 建立資源分級 (Tier-0/1/2) 的配置結構
  - [ ] 實現資源驗證和處理工具

## 三、核心架構設計（優先級：高）

- [ ] **定義 AudioTimeline JSON 格式**
  - [ ] 設計完整的 JSON Schema，包含時間、類型、資源、參數等字段
  - [ ] 建立範例集，涵蓋各種音訊事件場景（歌曲、音效、語音等）
  - [ ] 實現基本的驗證器確保 JSON 結構符合要求
  - [ ] **明確區分需要表情動畫的聲音事件與純音效事件**
    - [ ] 為聲音事件添加 `requiresAnimation` 或 `track` 屬性以區分管線
    - [X] 定義動畫同步所需的附加數據結構（viseme、表情標記等） (已定義 AnimationCue 接口)

- [ ] **實作 AudioCoordinator（統一聲音管線）**
  - [ ] 建立 `src/services/TimelineService.ts`，內含：  
    - [X] `TimelineEvent` 型別（time / type / payload）  
    - [X] 單例 `TimelineCoordinator`，含 `scheduleEvents`, `start`, `pause`, `resume`, `stop`, `seek` 方法  
  - [ ] `triggerEvent()` 具體整合各服務：  
    - [ ] **整合現有服務呼叫** — 將下列服務包裝為能自動向 TimelineCoordinator 報到的接口：  
      - [ ] `AudioService` → 播放語音 / 音樂 時自動推送 `voice` 事件  
      - [ ] `SoundEffectService` → 播放效果音時推送 `sfx` 事件  
      - [ ] `HeadService` → 套用表情 preset 時推送 `expression` 事件  
      - [ ] `BodyService` → 選擇動畫時推送 `action` 事件  
    - [ ] 建立 `ServiceEventAdapter`/HOC，集中管理包裝邏輯  
    - [ ] 在 `ChatService`、`WebSocketService` 中將後端指令轉為 `TimelineEvent` 並 `timeline.start(...)`
  - [ ] 提供 `getPlayhead()` 與事件列表給 TimelineInspector  
  - [ ] 單元測試：排程多事件 → 快進 playhead → 檢查服務呼叫次數與順序
  - [ ] 整合 `ChatService`：解析 AI 回覆 → 產生 TimelineEvents → `timeline.start(events)`  
  - [ ] 修改 `WebSocketService` 處理 `audio-effect`：若 Timeline 運行中，轉換為事件加入；否則直接播放
  - [ ] 驗證：文字 + 語音 + 表情 + 動作事件能準時執行，TimelineInspector 播放頭同步

- [ ] **重構 SoundEffectManager**
  - [ ] 剔除排程邏輯，聚焦於資源管理
  - [ ] 增強對 Tone.js 與原生音效的統一接口
  - [ ] 添加對播放狀態的監控機制
  - [ ] 實現資源預載與卸載功能

## 四、語音與音效系統整合（優先級：高）

- [ ] **統一語音與音效播放管線**
  - [ ] 設計 TTS 與歌曲功能的共享接口
  - [ ] 實現語音音檔與表情時間點的關聯機制
  - [X] **創建口型與動作同步的標準化資料結構** (已定義 AnimationCue 接口並用於歌曲)
  - [X] **建立與角色動畫系統的連接點** (已在 SoundEffectPanel 中實現 action 觸發)
  - [ ] **解決音頻衝突問題** (後端 TTS vs 前端歌曲)
    - [ ] 分析衝突原因和場景
    - [ ] 確定協調策略（例如：互斥播放、自動降低背景音量 ducking、優先級系統）
    - [ ] 在相關服務 (AudioService, AudioPlayerService, Coordinator) 中實現協調邏輯

- [ ] **實現自動音量調整**
  - [X] 添加語音播放時背景音量自動降低 (ducking) 功能 (需擴展至處理前端歌曲)
  - [ ] 實現音效與語音混合時的優先級系統
  - [ ] 添加自定義混音配置選項

- [ ] **合成語音調整功能**
  - [ ] 整合 Tone.js 對語音的加工處理
  - [ ] 添加效果器（回聲、混響、音調變化等）
  - [ ] 實現實時語音效果預覽功能

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
  - [ ] 建立聲音事件分類標準
    - [ ] **需要表情動畫的聲音：** TTS 語音、唱歌聲音、角色發出的感嘆聲
    - [ ] **純音效類型：** 背景音樂、環境聲、UI 音效、特效音、Combo 音效
  - [ ] 在音效配置中添加分類標記
  - [ ] 實現基於分類的資源加載和處理策略

- [ ] **雙管線協調機制**
  - [ ] 設計 Voice Pipeline（語音管線）與 SFX Pipeline（音效管線）分離策略
    - [ ] Voice Pipeline 負責角色直接發出的聲音，需與表情動畫同步
    - [ ] SFX Pipeline 負責所有背景和環境音效，無需表情聯動
  - [ ] 實現管線間優先權系統
    - [X] 角色講話時自動調整背景音量（ducking 機制）(需確認是否能處理前端歌曲播放的場景)
    - [ ] 防止多個角色聲音事件重疊播放的衝突處理
    - [ ] **明確解決後端 TTS 與前端歌曲播放的衝突**
  - [ ] 添加管線狀態監控
    - [ ] 跟踪正在播放的語音和音效事件
    - [ ] 提供當前各管線活動狀態的查詢接口

- [ ] **表情動畫同步系統**
  - [X] **設計聲音-表情映射標準** (已定義 AnimationCue 接口並用於歌曲)
  - [X] **實現語音事件的表情觸發機制** (已在 SoundEffectPanel 中實現歌曲的 action/emotion 觸發)
  - [ ] 添加表情預覽和測試工具
    - [ ] 在音效面板中允許預覽語音對應的表情
    - [ ] 支持手動調整表情時間點

- [ ] **統一事件系統**
  - [ ] 設計聲音事件通知機制
    - [ ] 語音開始/結束觸發表情系統事件
    - [ ] 音效播放狀態變更通知界面更新
  - [ ] 實現跨模組事件訂閱
    - [ ] 表情系統訂閱語音事件
    - [ ] UI 系統訂閱音效事件以更新視覺元素

## 九、開發與調試工具（優先級：中）

- [ ] **TimelineInspector** （詳見前端介面段落）
- [ ] 性能計數器：顯示每秒音效/服務呼叫統計
- [ ] 錄製 / 匯出 TimelineEvents 到 JSON，用於回歸測試

## 實施策略

重構應採用漸進式方法，但考慮到前端需求的優先性，建議以下實施順序：

1. **階段一**: 優先改進前端介面，添加歌曲庫和增強 Freesound 整合，提供可用的工作界面。 **(進行中，需重構 Panel)**
2. **階段二（進行中）**: 重構 **SoundEffectPanel** → 模組化拆分 (SongLibrary / Synth / Freesound) 並使用統一的 AudioPlayerService。  
3. **階段三**: 實現 **AudioCoordinator** 核心，串接 AudioService、SoundEffectService 等，並提供排程 API。  
4. **階段四**: 將 SoundEffectPanel 與 AudioCoordinator 串聯，確保所有聲音事件皆經由 Coordinator 控制。  
5. **階段五**: 重新恢復 TimelineInspector 與 AudioTimeline 功能，使用 Coordinator 提供的事件流。  
6. **階段六**: 進一步擴充資源管理、效能優化與進階功能。

## 下一步優先任務

1. **重構 `SoundEffectPanel`（拆分子元件）並推出 `SongLibraryPanel` MVP**。
2. **設計並實作 AudioCoordinator MVP**（替代 TimelineCoordinator，負責所有聲音事件）。
3. **將 SoundEffectPanel 與 AudioCoordinator 串接，驗證播放、暫停、排程功能。**
4. 強化 Freesound 整合（搜尋 + 預覽 + 收藏 IndexedDB）。
5. 建立聲音分類系統（需/不需表情），並更新資源加載策略。
6. 重新啟用 TimelineInspector，顯示 AudioCoordinator 事件流。
7. 擴充 SynthPanel：加入 Tone.js 模板與即時參數調整介面。

這個順序將確保先實現對前端用戶有用的功能，同時為後續的深度架構重構打下基礎。 