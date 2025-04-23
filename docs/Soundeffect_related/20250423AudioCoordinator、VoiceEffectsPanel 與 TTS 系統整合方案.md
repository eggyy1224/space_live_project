# AudioCoordinator、VoiceEffectsPanel 與 TTS 系統整合方案

## 方案概述

本文檔描述 AudioCoordinator（聲音協調系統）與 VoiceEffectsPanel（語音效果面板）及 TTS（文字轉語音）系統的整合架構，以實現統一、高效的語音效果管理與播放。

### 核心定位

**AudioCoordinator**：作為中央協調器，專注於「決定何時播放什麼」，而非「如何播放」。其職責是管理請求、優先級排序、資源分配和事件協調，但實際播放邏輯則委託給專門的 Player 組件。

**VoiceEffectsPanel**：負責提供語音效果的用戶介面，允許用戶選擇、預覽和套用各種語音效果。不直接處理音頻播放，而是通過 AudioCoordinator 發送請求。

**TTS 系統**：負責文字到語音的轉換，生成角色語音音頻。與 AudioCoordinator 整合以確保語音播放的協調和同步。

## 整體架構

整個聲音系統分為以下主要組件：

### 1. 核心協調器（AudioCoordinator）

- 系統的中央決策引擎
- 接收並評估播放請求
- 維護全局聲音狀態
- 管理播放隊列與排程
- 處理優先級衝突
- 分發事件到相關組件
- **不直接處理實際播放邏輯**

### 2. 播放器組件（Players）

- **TonePlayer**：處理基於 Tone.js 的合成音效
- **PreRecordedPlayer**：處理預錄音效的播放
- **TTSPlayer**：專門處理 TTS 語音的播放
- 每個 Player 都實現統一介面但專注於特定音頻類型
- 負責實際音頻播放邏輯
- 向協調器報告播放狀態和事件

### 3. 聲音來源模組

- **SongLibraryPanel**：管理和提供背景音樂
- **FreesoundPanel**：提供通用音效庫
- **BandEffectsPanel**：提供樂器和音樂效果
- **VoiceEffectsPanel**：提供語音和 TTS 相關功能
- 這些模組只發送請求，不直接處理播放

### 4. 事件總線（Event Bus）

- 基於 mitt 實現的事件通信系統
- 連接各組件的通信基礎設施
- 確保組件間鬆耦合

## AudioCoordinator 設計原則

1. **協調而非播放**：AudioCoordinator 專注於決策邏輯、資源調度、優先級管理，不參與實際播放實現。

2. **統一入口**：所有聲音請求必須通過 AudioCoordinator 處理，確保集中式決策邏輯和全局資源管理。

3. **優先級管理**：明確定義不同類型聲音的優先級處理規則（如語音優先於背景音樂）。

4. **事件驅動設計**：採用事件機制實現鬆耦合設計，便於各組件獨立發展。

5. **可擴展性**：設計支持輕鬆添加新的聲音類型和處理邏輯。

## VoiceEffectsPanel 整合職責

1. **用戶介面提供**：
   - 提供語音效果選擇和參數調整界面
   - 顯示當前語音處理狀態和歷史記錄

2. **請求發送**：
   - 通過 AudioCoordinator API 發送語音播放請求
   - 提供優先級和軌道信息
   - 不直接調用音頻播放 API

3. **狀態接收**：
   - 訂閱 AudioCoordinator 事件獲取播放狀態
   - 根據播放狀態更新 UI 顯示

## TTS 系統整合職責

1. **語音生成**：
   - 將文字轉換為語音音頻數據
   - 支持流式處理（即邊生成邊播放）
   - 提供語音標記點（用於表情/嘴型同步）

2. **與 AudioCoordinator 對接**：
   - 向 AudioCoordinator 提供音頻數據和標記
   - 由 AudioCoordinator 調度何時播放
   - TTSPlayer 負責實際播放實現

3. **狀態報告**：
   - 向 AudioCoordinator 報告生成進度和狀態
   - 提供關鍵標記點事件（用於表情同步）

## 語音播放基本工作流程

1. **用戶操作**：
   - 用戶在 VoiceEffectsPanel 中選擇語音效果
   - 用戶觸發播放按鈕或自動播放條件

2. **請求處理**：
   - VoiceEffectsPanel 向 AudioCoordinator 發送播放請求
   - 請求包含優先級、軌道、來源等信息
   - 例如：
     ```typescript
     audioCoordinator.play({
       track: "voice",
       type: "tts",
       source: ttsResult,
       priority: 80,
       player: "tts",
       options: {
         syncPoints: markersForFacialSync
       }
     });
     ```

3. **協調決策**：
   - AudioCoordinator 評估請求優先級
   - 決定是否可以立即播放或需要排隊
   - 如有需要，中斷或降低其他聲音（如背景音樂）音量

4. **播放執行**：
   - AudioCoordinator 選擇合適的 Player（如 TTSPlayer）
   - 分發播放命令給選定的 Player
   - Player 執行實際播放
   - 播放進度和狀態變更通過事件通知 AudioCoordinator

5. **狀態反饋**：
   - AudioCoordinator 將播放狀態通過事件傳回 VoiceEffectsPanel
   - VoiceEffectsPanel 更新 UI 顯示當前狀態

## 事件通信設計

### 請求事件（Panel → Coordinator）

- **audio:play** - 請求播放聲音
- **audio:stop** - 請求停止播放
- **audio:pause** - 請求暫停播放
- **audio:resume** - 請求恢復播放

### 狀態事件（Coordinator → Panel）

- **audio:started** - 聲音開始播放
- **audio:ended** - 聲音播放結束
- **audio:paused** - 聲音暫停
- **audio:resumed** - 聲音恢復播放
- **audio:error** - 播放出錯

### 控制事件（Coordinator → Player）

- **player:load** - 加載音頻資源
- **player:play** - 開始播放
- **player:stop** - 停止播放
- **player:pause** - 暫停播放
- **player:resume** - 恢復播放
- **player:duck** - 降低音量
- **player:restore** - 恢復音量

### 同步事件（Player → 其他系統）

- **voice:start** - 語音開始（用於表情同步）
- **voice:marker** - 到達語音標記點
- **voice:end** - 語音結束

## 具體實現詳解

### AudioCoordinator 核心 API

```typescript
interface AudioCoordinator {
  // 播放控制
  play(request: PlayRequest): Promise<string>; // 返回請求ID
  stop(trackOrId: string): Promise<boolean>;
  pause(trackOrId: string): Promise<boolean>;
  resume(trackOrId: string): Promise<boolean>;
  
  // 音量控制
  setVolume(track: string, volume: number): void;
  getVolume(track: string): number;
  
  // 狀態查詢
  getActiveSound(track?: string): SoundInfo[];
  getQueue(track?: string): SoundInfo[];
  
  // 事件訂閱
  on(event: string, callback: Function): void;
  off(event: string, callback: Function): void;
}

// 播放請求格式
interface PlayRequest {
  track: string;         // 目標軌道
  type: string;          // 聲音類型
  source: any;           // 聲音源（URL、參數等）
  priority: number;      // 優先級（0-100，越高越優先）
  player?: string;       // 指定播放器
  options?: {            // 播放選項
    loop?: boolean;      // 循環播放
    volume?: number;     // 初始音量
    rate?: number;       // 播放速率
    startAt?: number;    // 起始位置
    endAt?: number;      // 結束位置
    syncPoints?: any[];  // 同步點（例如表情同步）
  };
}
```

### Player 通用介面

```typescript
interface IAudioPlayer {
  // 資源管理
  load(src: any, opts?: PlayerOptions): Promise<void>;
  unload(): void;
  
  // 播放控制
  play(at?: number): void;
  stop(): void;
  pause(): void;
  resume(): void;
  
  // 參數控制
  setVolume(volume: number): void;
  setRate(rate: number): void;
  
  // 狀態查詢
  getState(): PlayerState;
  getDuration(): number;
  getCurrentTime(): number;
  
  // 事件處理
  on(event: PlayerEventType, callback: Function): void;
  off(event: PlayerEventType, callback: Function): void;
}
```

### TTSPlayer 特殊功能

TTSPlayer 是專門用於處理 TTS 語音播放的播放器，具有一些特殊功能：

1. **流式播放**：
   - 支持邊接收 TTS 生成數據邊播放
   - 處理分段到達的音頻數據

2. **標記點處理**：
   - 處理 TTS 語音中包含的標記點
   - 在到達標記點時發出相應事件

3. **時間對齊**：
   - 處理語音與表情時間軸的對齊
   - 支持時間軸伸縮和校準

### VoiceEffectsPanel 對接實現

```typescript
// VoiceEffectsPanel 中的播放請求示例
function playVoiceEffect(text: string, effect: VoiceEffect) {
  // 1. 準備 TTS 請求
  const ttsRequest = prepareTTSRequest(text, effect);
  
  // 2. 獲取 TTS 結果（可能是流式的）
  ttsService.generate(ttsRequest).then(ttsResult => {
    // 3. 通過 AudioCoordinator 發送播放請求
    audioCoordinator.play({
      track: "voice",
      type: "tts",
      source: ttsResult,
      priority: 80, // 語音通常為高優先級
      player: "tts",
      options: {
        volume: currentVoiceVolume,
        rate: playbackRate,
        syncPoints: ttsResult.markers // 用於表情同步的標記
      }
    }).then(requestId => {
      // 保存 requestId 以便後續控制
      currentPlayingId = requestId;
    });
  });
}

// 監聽播放狀態
function setupAudioStatusListeners() {
  audioCoordinator.on("audio:started", (data) => {
    if (data.track === "voice") {
      updateUIPlayingState(true);
    }
  });
  
  audioCoordinator.on("audio:ended", (data) => {
    if (data.track === "voice") {
      updateUIPlayingState(false);
      checkQueueAndPlayNext();
    }
  });
}
```

## 一般優先級定義

系統定義以下軌道優先級關係：

1. **語音軌（Voice Track）**：優先級 70-90
   - TTS 語音：80-90
   - 預錄語音：70-80

2. **音效軌（Effect Track）**：優先級 40-70
   - 重要交互音效：60-70
   - 一般 UI 音效：40-50

3. **環境軌（Ambient Track）**：優先級 20-40
   - 特殊環境音效：30-40
   - 背景環境音：20-30

4. **音樂軌（Music Track）**：優先級 10-20
   - 背景音樂：10-20

這些優先級數值用於決定不同聲音的播放順序和中斷策略。

## 同步機制設計

### 語音與表情同步

1. **基於事件的同步**：
   - 語音開始播放時觸發 `voice:start` 事件
   - 語音結束時觸發 `voice:end` 事件
   - 表情系統訂閱這些事件來協調表情變化

2. **標記點同步**：
   - TTS 生成時包含時間標記
   - 播放過程中到達標記點時觸發 `voice:marker` 事件
   - 可用於精確同步特定表情（如眨眼、點頭等）

3. **時間軸校準**：
   - 提供機制處理語音和表情時間軸可能的偏差
   - 支持手動或自動調整延遲

## 實施路徑

### 第一階段：基礎整合（2 週）

1. 設計並實現 AudioCoordinator 核心架構
2. 實現基本 Player 介面和 TTSPlayer 初版
3. 建立事件總線系統
4. VoiceEffectsPanel 初步對接 AudioCoordinator

### 第二階段：功能完善（3 週）

1. 完善 TTSPlayer 流式播放支持
2. 實現語音與表情同步基本機制
3. 添加優先級系統和 ducking 功能
4. 改進 VoiceEffectsPanel UI 與狀態顯示

### 第三階段：整合與優化（3 週）

1. 完整整合 TTS 系統與 AudioCoordinator
2. 添加高級播放控制功能（如排隊、預加載等）
3. 優化播放性能和資源使用
4. 系統測試與問題修復

## 挑戰與解決方案

### 挑戰 1：流式 TTS 處理

**問題**：TTS 生成可能需要時間，等待完整生成可能導致播放延遲。

**解決方案**：
- 實現流式處理機制，邊生成邊播放
- 使用緩衝區管理音頻片段
- 提供進度指示器減輕用戶等待感

### 挑戰 2：同步精確性

**問題**：語音與表情同步需要精確的時間控制。

**解決方案**：
- 使用 Web Audio API 的精確時間控制
- 添加可配置的延遲補償
- 提供校準機制處理設備差異

### 挑戰 3：資源管理

**問題**：過多音頻資源可能佔用過多記憶體。

**解決方案**：
- 實現智能資源管理策略
- 自動釋放不活躍資源
- 建立預加載優先級系統

## 結論

通過本整合方案，AudioCoordinator 將作為統一的聲音協調中心，使 VoiceEffectsPanel 和 TTS 系統能夠緊密協作，提供流暢且統一的語音體驗。清晰的職責分離（AudioCoordinator 負責協調，Player 負責播放）確保了系統的可維護性和可擴展性。

事件驅動設計確保系統各部分能夠鬆耦合運作，便於未來功能擴展。優先級系統則確保不同聲音類型能夠按照預期順序播放，避免混亂。

隨著系統的實施和完善，我們期望能夠顯著提升用戶的聽覺體驗和整體互動流暢度。