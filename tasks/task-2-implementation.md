# 音效系統重構實現計劃

根據前面的分析和設計文檔，本文定義了音效系統重構的具體實現步驟、優先級和時間表。

## 重構目標

- 將龐大的`SoundEffectPanel`拆分為多個專注的組件
- 實現中央音效協調器（AudioCoordinator）
- 建立統一的音效播放和優先級管理機制
- 支持語音效果處理和TTS系統整合
- 增強音效資源管理和擴展能力

## 優先級和開發階段

### 階段1：基礎架構設計與核心接口定義（高優先級）

**目標**：定義清晰的接口和數據結構，為後續實現打下基礎

1. **定義IAudioPlayer接口**
   - 文件：`src/services/players/IAudioPlayer.ts`
   - 內容：播放器通用方法（load, play, stop等）
   - 估計時間：1天

2. **定義音效系統數據模型**
   - 文件：`src/models/sound.ts`
   - 內容：PlayRequest, SoundInfo, AudioTimeline等數據結構
   - 估計時間：1天

3. **設計事件系統**
   - 文件：`src/services/AudioEventSystem.ts`
   - 內容：基於mitt的事件定義和處理
   - 估計時間：1天

### 階段2：組件拆分與基本UI層重構（高優先級）

**目標**：將龐大的SoundEffectPanel拆分為多個專注的UI組件

1. **創建SoundEffectPanelLayout**
   - 文件：`src/components/SoundEffectPanelLayout.tsx`
   - 內容：Tab切換與共享狀態容器
   - 估計時間：2天

2. **實現SongLibraryPanel**
   - 文件：`src/components/SongLibraryPanel.tsx`
   - 內容：歌曲清單呈現與播放控制
   - 估計時間：2天

3. **實現SynthPanel**
   - 文件：`src/components/SynthPanel.tsx`
   - 內容：Tone.js合成器與JSON序列編輯
   - 估計時間：2天

4. **實現FreesoundPanel**
   - 文件：`src/components/FreesoundPanel.tsx`
   - 內容：Freesound API搜尋與收藏功能
   - 估計時間：3天

5. **實現VoiceEffectsPanel**
   - 文件：`src/components/VoiceEffectsPanel.tsx`
   - 內容：語音效果選擇與參數控制
   - 估計時間：2天

### 階段3：播放器實現（高優先級）

**目標**：實現各種專用的音效播放器

1. **實現PreRecordedPlayer**
   - 文件：`src/services/players/PreRecordedPlayer.ts`
   - 內容：預錄音效的播放邏輯（基於HTMLAudio/Howler）
   - 估計時間：2天

2. **實現TonePlayer**
   - 文件：`src/services/players/TonePlayer.ts`
   - 內容：Tone.js播放邏輯實現
   - 估計時間：3天

3. **實現TTSPlayer**
   - 文件：`src/services/players/TTSPlayer.ts`
   - 內容：TTS播放邏輯實現，支持同步點
   - 估計時間：3天

### 階段4：協調器實現（最高優先級）

**目標**：實現音效協調中心，管理所有播放請求和優先級

1. **AudioCoordinator核心功能**
   - 文件：`src/services/AudioCoordinator.ts`
   - 內容：播放控制、軌道管理、播放器註冊
   - 估計時間：4天

2. **優先級管理與Ducking機制**
   - 文件：`src/services/AudioCoordinator.ts`
   - 內容：優先級衝突處理、音量自動調整
   - 估計時間：3天

3. **時間軸處理邏輯**
   - 文件：`src/services/AudioCoordinator.ts`
   - 內容：從JSON排程播放、Combo處理
   - 估計時間：3天

### 階段5：效果處理服務（中優先級）

**目標**：實現語音效果處理服務，支持實時音效應用

1. **VoiceEffectsProcessor實現**
   - 文件：`src/services/VoiceEffectsProcessor.ts`
   - 內容：Tone.js效果鏈、預設效果應用
   - 估計時間：4天

2. **音效參數控制**
   - 文件：`src/services/VoiceEffectsProcessor.ts`
   - 內容：動態參數調整、效果切換
   - 估計時間：2天

### 階段6：資源管理與擴展（中優先級）

**目標**：實現高效的音效資源管理與系統擴展機制

1. **SoundResourceManager實現**
   - 文件：`src/services/SoundResourceManager.ts`
   - 內容：資源加載、快取管理、分級策略
   - 估計時間：4天

2. **ComboManager實現**
   - 文件：`src/services/ComboManager.ts`
   - 內容：Combo定義與處理
   - 估計時間：3天

3. **插件系統實現**
   - 文件：`src/plugins/AudioPluginSystem.ts`
   - 內容：插件接口與管理器
   - 估計時間：3天

### 階段7：系統整合與測試（高優先級）

**目標**：整合所有組件並進行全面測試

1. **協調器與UI整合**
   - 文件：各UI組件與協調器
   - 內容：連接UI事件與協調器方法
   - 估計時間：3天

2. **TTS系統整合**
   - 文件：`src/services/TTSPlayer.ts`, `src/services/AudioCoordinator.ts`
   - 內容：表情同步點處理、TTS流式播放
   - 估計時間：3天

3. **單元測試**
   - 文件：`tests/`目錄下的測試文件
   - 內容：各組件的單元測試
   - 估計時間：4天

4. **整合測試**
   - 文件：`tests/`目錄下的整合測試文件
   - 內容：系統級別的整合測試
   - 估計時間：3天

## 實現策略

為了確保重構的順利進行，我們將採用以下策略：

### 1. 增量式重構

- **小步驟漸進**：每次變更範圍控制在可管理的範圍內
- **持續集成**：每完成一個組件就進行整合和測試
- **功能保持**：確保重構過程中不破壞現有功能

### 2. 並行開發

- **UI組件**：UI層可與協調器同時開發，基於明確的接口
- **播放器**：各播放器可並行開發，它們之間沒有強依賴
- **協調器與效果處理**：由於相互依賴，需要更緊密的協調

### 3. 迭代開發模式

1. **最小可行產品**：首先實現基本的協調器和播放器
2. **功能擴展**：逐步添加優先級管理、Ducking等功能
3. **UI優化**：在基礎功能穩定後進行UI體驗優化

## 實現時間表

| 週次 | 主要任務 | 里程碑 |
|------|---------|--------|
| 第1週 | 基礎架構設計、接口定義、UI拆分 | 完成基本接口和數據模型設計 |
| 第2週 | 基本播放器實現、協調器核心功能 | UI組件框架完成，基本播放功能可用 |
| 第3週 | 協調器優先級管理、時間軸處理 | 協調器核心功能完成 |
| 第4週 | 效果處理服務、TTS整合 | 語音效果與TTS系統整合完成 |
| 第5週 | 資源管理、擴展機制、系統測試 | 全系統整合和測試完成 |

## 實現計劃文件結構

```
src/
├── components/                  # UI組件
│   ├── SoundEffectPanelLayout.tsx  # 頂層面板容器
│   ├── SongLibraryPanel.tsx     # 歌曲庫面板
│   ├── SynthPanel.tsx           # 合成音效面板
│   ├── FreesoundPanel.tsx       # 音效搜尋面板
│   └── VoiceEffectsPanel.tsx    # 語音效果面板
│
├── services/                    # 核心服務
│   ├── AudioCoordinator.ts      # 音效協調中心
│   ├── VoiceEffectsProcessor.ts # 語音效果處理
│   ├── SoundResourceManager.ts  # 音效資源管理
│   ├── ComboManager.ts          # 組合音效管理
│   ├── AudioEventSystem.ts      # 事件系統
│   │
│   └── players/                 # 播放器實現
│       ├── IAudioPlayer.ts      # 播放器接口
│       ├── PreRecordedPlayer.ts # 預錄音效播放器
│       ├── TonePlayer.ts        # Tone.js播放器
│       └── TTSPlayer.ts         # TTS播放器
│
├── models/                      # 數據模型
│   ├── sound.ts                 # 音效相關模型
│   └── ComboDefinition.ts       # 組合音效定義
│
├── plugins/                     # 插件系統
│   └── AudioPluginSystem.ts     # 插件管理
│
└── hooks/                       # React Hooks
    ├── useAudioCoordinator.ts   # 協調器Hook
    └── useFreesoundAPI.ts       # Freesound API Hook
```

## 風險與緩解策略

| 風險 | 影響 | 緩解策略 |
|------|------|---------|
| Tone.js整合複雜度高 | 可能延遲TonePlayer和效果處理服務 | 提前研究Tone.js API，建立概念驗證 |
| 優先級衝突處理邏輯複雜 | 可能導致音效播放異常 | 設計簡單明確的優先級規則，增加測試覆蓋 |
| 表情同步精確度問題 | 可能影響用戶體驗 | 實現更靈活的同步機制，支持微調 |
| 性能問題（多音效同時播放） | 可能導致卡頓或崩潰 | 實現播放數量限制，加強資源管理 |
| 瀏覽器兼容性問題 | 部分功能在某些瀏覽器不可用 | 添加特性檢測和降級處理 |

## 下一步行動

1. **開發環境設置**
   - 確保所有開發者工具和依賴安裝正確
   - 設置測試環境和自動化測試

2. **任務分配**
   - 分配接口設計和核心架構任務給有經驗的團隊成員
   - 按照UI、服務和播放器分類分配任務

3. **開發啟動**
   - 從階段1的接口定義開始
   - 同時開始UI組件拆分
   - 建立每日或每週同步會議 