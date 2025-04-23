好，我會針對你目前 `feature/sound_effcets` 分支的架構，深入研究以下內容：

1. AudioCoordinator 在現有 code base 下的最佳架構設計與實作方式（高階設計，非實作細節）
2. 各個面板（SongLibraryPanel, FreesoundPanel, BandEffectsPanel, VoiceEffectsPanel）應如何對接協調器
3. JSON 控制音效排程的格式定義、流入點與解析策略
4. 聲音 ducking 與優先權策略的設計
5. 最終提供一份整合的技術藍圖與高階整合計畫書（不含程式碼，強調架構觀與模組邏輯）

這份內容會根據你現有 commit 狀況與程式架構去設計，讓我們把這條聲音協調的主幹架得漂亮、擴充穩健。
我完成後會第一時間回報你。

# AudioCoordinator 聲音協調系統：架構藍圖與整合計畫

## 系統目的

AudioCoordinator 是一套中央音頻排程架構，負責管理各種聲音來源，確保有序播放與優先級管理。它解決了多個聲音模塊各自獨立運行時產生的混亂，建立一個統一的協調系統。

**核心定位**：AudioCoordinator **僅負責決策與協調**（即決定「何時播放什麼」），而將實際播放執行（「如何播放」）委託給專門的 Player 組件。

## 核心設計原則

### 1. 協調而非播放

明確職責分離：
- **AudioCoordinator**：專注於決策邏輯、資源調度、優先級管理和事件分發
- **Player 組件**：專注於特定類型聲音的實際播放技術實現

這種分離確保了系統的靈活性和可擴展性，使各部分能夠專注於各自的職責領域。AudioCoordinator 僅負責「決定什麼時候播放什麼」，而將「如何播放」的職責完全委託給專門的 Player 組件。

### 2. 統一入口

所有聲音播放請求必須通過 AudioCoordinator 處理：
- 集中式決策邏輯
- 統一的優先級規則
- 全局資源管理
- 減少組件間耦合

### 3. 優先級管理

建立明確的優先級系統：
- 不同聲音類型的優先級（如緊急通知 > 語音 > 音效 > 背景音樂）
- 相同類型聲音的處理策略（如排隊、替換或並行）
- 提供優先級讓步機制（如背景音樂自動降低音量讓位給語音）

### 4. 事件驅動架構

採用事件機制實現鬆耦合設計：
- 基於事件總線（如 mitt）實現組件間通信
- 使用事件傳遞請求、狀態更新和控制指令
- 允許各組件獨立發展和替換

### 5. 可擴展設計

考慮未來擴展的需求：
- 輕鬆添加新的聲音類型和處理邏輯
- 支持插件式擴展
- 提供開放接口供外部系統整合

## 技術架構

### 整體架構

AudioCoordinator 系統由以下主要部分組成：

1. **核心協調器（AudioCoordinator）**
   - 系統的中央決策引擎
   - 接收並評估播放請求
   - 維護全局聲音狀態
   - 管理播放隊列與排程
   - 處理優先級衝突
   - 分發事件到相關組件
   - **不直接參與實際播放行為**

2. **播放器組件（Players）**
   - 實現實際播放功能的組件
   - 每種類型聲音有專門的 Player 實現
   - 向協調器報告播放狀態和事件
   - 接收協調器的控制指令
   - **完全負責「如何播放」的實作細節**

3. **事件總線（Event Bus）**
   - 連接各組件的通信基礎設施
   - 傳遞播放請求、狀態更新和控制指令
   - 確保協調器與播放器之間的鬆耦合
   - **作為協調器與播放器之間的唯一橋接**

### 主要 Player 組件

系統定義多種專門的 Player 組件：

1. **TonePlayer**：處理基於 Tone.js 的音樂合成與節奏音效
   - 實現節奏控制、音色合成等功能
   - 支援參數化音效生成

2. **PreRecordedPlayer**：處理預錄音效的播放（如 MP3、WAV 文件）
   - 管理音頻緩存與預加載
   - 提供淡入淡出、循環播放等功能

3. **TTSPlayer**：專門處理 TTS 語音播放
   - 支援流式播放（邊生成邊播放）
   - 管理語音元數據（如標記、時間戳）
   - 處理語音與表情/動畫同步所需的時間標記

### 聲音軌道設計

系統將聲音分為不同的軌道，便於管理：

1. **語音軌（Voice Track）**：處理所有語音內容（如 TTS）
2. **音效軌（Effect Track）**：處理一般音效（如提示音、交互音效）
3. **環境軌（Ambient Track）**：處理環境音效（如雨聲、風聲）
4. **音樂軌（Music Track）**：處理背景音樂

每個軌道可以有獨立的音量控制、優先級規則和隊列管理策略。

### 優先級系統實現

優先級系統包含多個層面：

1. **軌道間優先級**：
   - 語音軌 > 音效軌 > 環境軌 > 音樂軌
   - 高優先級軌道可以中斷或降低低優先級軌道音量

2. **軌道內優先級**：
   - 每個聲音請求可以指定軌道內的優先級
   - 同一軌道內的優先級衝突由特定策略處理

3. **優先級策略**：
   - **中斷策略**：高優先級直接中斷當前低優先級聲音
   - **排隊策略**：聲音按優先級排隊依次播放
   - **並行策略**：允許多個聲音同時播放，可能調整各自音量
   - **讓步策略**：降低音量但不完全中斷（如背景音樂音量降低）

## 實現方案

### 核心介面設計

**AudioCoordinator 核心 API**：

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
  
  // 播放器管理
  registerPlayer(type: string, player: IAudioPlayer): void;
  getPlayer(type: string): IAudioPlayer | undefined;
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

**Player 通用介面**：

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

// Player 事件類型
enum PlayerEventType {
  LOAD_START = 'load:start',
  LOAD_COMPLETE = 'load:complete',
  LOAD_ERROR = 'load:error',
  PLAY_START = 'play:start',
  PLAY_END = 'play:end',
  PLAY_PAUSE = 'play:pause',
  PLAY_RESUME = 'play:resume',
  PLAY_ERROR = 'play:error',
  TIME_UPDATE = 'time:update',
  MARKER_REACHED = 'marker:reached'
}

// Player 狀態
enum PlayerState {
  IDLE = 'idle',
  LOADING = 'loading',
  READY = 'ready',
  PLAYING = 'playing',
  PAUSED = 'paused',
  ERROR = 'error'
}
```

### 事件設計

系統定義以下主要事件類型：

#### 請求事件（Source → Coordinator）

- **audio:play** - 請求播放聲音
- **audio:stop** - 請求停止播放
- **audio:pause** - 請求暫停播放
- **audio:resume** - 請求恢復播放

#### 狀態事件（Coordinator → Source）

- **audio:started** - 聲音開始播放
- **audio:ended** - 聲音播放結束
- **audio:paused** - 聲音暫停
- **audio:resumed** - 聲音恢復播放
- **audio:error** - 播放出錯

#### 控制事件（Coordinator → Player）

- **player:load** - 加載音頻資源
- **player:play** - 開始播放
- **player:stop** - 停止播放
- **player:pause** - 暫停播放
- **player:resume** - 恢復播放
- **player:duck** - 降低音量
- **player:restore** - 恢復音量

#### 跨系統事件

- **voice:start** - 語音開始（用於表情同步）
- **voice:marker** - 到達語音標記點
- **voice:end** - 語音結束

### 實現步驟建議

1. **基礎架構**（第一階段）
   - 實現核心 AudioCoordinator 框架
   - 設計 Player 介面和基本抽象類
   - 建立事件總線系統
   - 實現基本的軌道和優先級概念

2. **基本播放功能**（第二階段）
   - 實現 PreRecordedPlayer 完整功能
   - 實現基本軌道和優先級系統
   - 添加音量控制和 ducking 功能
   - 與現有 SoundEffectPanel 初步整合

3. **軌道系統與進階功能**（第三階段）
   - 實現 TonePlayer 完整功能
   - 添加更複雜的優先級策略和隊列管理
   - 完善錯誤處理機制
   - 整合更多現有音頻系統

4. **TTS 整合**（第四階段）
   - 實現 TTSPlayer 及流式播放支持
   - 添加語音與表情同步機制
   - 整合 TTS 服務
   - 建立 VoiceEffectsPanel 初版

5. **優化與擴展**（第五階段）
   - 性能優化
   - 添加資源管理和預加載功能
   - 完善錯誤處理和恢復機制
   - 提供插件擴展接口

## 與現有系統整合

### 整合 SoundEffectPanel

1. **修改 SoundEffectPanel 發送播放請求**：
   - 將直接播放調用改為通過 AudioCoordinator 發送請求
   - 添加優先級和軌道信息

2. **接收狀態更新**：
   - 監聽 AudioCoordinator 發出的狀態事件
   - 更新 UI 顯示當前播放狀態

### 整合背景音樂系統

1. **通過 AudioCoordinator 控制背景音樂**：
   - 所有背景音樂播放請求通過協調器
   - 自動處理與其他聲音的優先級

2. **實現 ducking 機制**：
   - 語音播放時自動降低背景音樂音量
   - 語音結束時恢復正常音量

### 與表情系統整合

1. **同步事件機制**：
   - 語音開始/結束時發送事件給表情系統
   - 在語音重要節點發送標記事件

2. **時間軸對齊**：
   - 確保語音時間軸與表情時間軸同步
   - 提供調整機制處理延遲

## 開發實施計劃

### 第一階段：基礎框架（時間估計：2 週）

- 設計和實現 AudioCoordinator 核心結構
- 實現基本事件系統
- 定義 Player 介面和抽象類
- 建立基礎測試框架

### 第二階段：基本功能實現（時間估計：3 週）

- 實現 PreRecordedPlayer 完整功能
- 實現基本軌道和優先級系統
- 添加音量控制和 ducking 功能
- 與現有 SoundEffectPanel 初步整合

### 第三階段：進階功能（時間估計：3 週）

- 實現 TonePlayer 完整功能
- 添加更複雜的優先級策略和隊列管理
- 完善錯誤處理機制
- 整合更多現有音頻系統

### 第四階段：TTS 整合（時間估計：4 週）

- 實現 TTSPlayer 及流式播放支持
- 添加語音與表情同步機制
- 整合 TTS 服務
- 建立 VoiceEffectsPanel 初版

### 第五階段：完善與優化（時間估計：2 週）

- 性能測試與優化
- 完善錯誤處理和恢復機制
- 添加日誌和監控功能
- 撰寫詳細文檔和使用範例

## 進度追蹤與評估

### 關鍵成果指標

1. **功能完整性**：實現所有規劃功能
2. **性能指標**：聲音播放延遲 < 100ms，CPU 使用率 < 5%
3. **穩定性**：測試覆蓋率 > 80%，無嚴重崩潰問題
4. **可用性**：現有聲音系統順利遷移到新架構

### 風險與緩解策略

1. **性能風險**：
   - 採用事件驅動可能引入額外延遲
   - 緩解：實施性能測試，優化事件處理路徑

2. **整合風險**：
   - 現有系統可能難以適應新架構
   - 緩解：分階段整合，提供過渡適配層

3. **TTS 同步風險**：
   - 語音與表情同步可能存在技術挑戰
   - 緩解：建立彈性的同步機制，允許手動調整

## 參考資源

- [Web Audio API 文檔](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [Tone.js 文檔](https://tonejs.github.io/)
- [mitt 事件庫](https://github.com/developit/mitt)
- 團隊內部 TTS 系統文檔

### 協調器與播放器交互流程

AudioCoordinator 與 Player 之間的交互遵循以下流程：

1. **初始化階段**
   - 各類型 Player 註冊到 AudioCoordinator
   - 設置默認音量和配置

2. **播放請求處理**
   - Panel 或其他組件向 AudioCoordinator 發送播放請求
   - AudioCoordinator 評估請求的優先級和目標軌道
   - 決定是否允許播放，可能需要中斷現有聲音或調整音量

3. **播放執行**
   - AudioCoordinator 選擇合適的 Player（基於 request.type 或 request.player）
   - 通過事件或直接調用，指示 Player 加載資源
   - Player 完成加載後通知 AudioCoordinator
   - AudioCoordinator 指示 Player 開始播放，可能指定起始時間

4. **播放監控**
   - Player 定期報告播放進度（通過 time:update 事件）
   - Player 在遇到標記點時發送 marker:reached 事件
   - AudioCoordinator 根據需要更新內部狀態並可能觸發其他系統（如表情同步）

5. **播放結束處理**
   - Player 在播放結束時發送 play:end 事件
   - AudioCoordinator 更新內部狀態，可能從隊列中取出下一個請求
   - 可能恢復之前因優先級讓步而調整過音量的其他 Player

6. **錯誤處理**
   - Player 在遇到錯誤時發送 play:error 事件
   - AudioCoordinator 記錄錯誤並採取適當的恢復措施

### 具體 Player 實現示例

#### TonePlayer 實現概要

```typescript
// TonePlayer.ts
import * as Tone from 'tone';
import { IAudioPlayer, PlayerEventType, PlayerState, PlayerOptions } from './IAudioPlayer';
import mitt from 'mitt';

export class TonePlayer implements IAudioPlayer {
  private emitter = mitt();
  private state: PlayerState = PlayerState.IDLE;
  private sequence: Tone.Sequence | null = null;
  private currentVolume: number = 1;
  
  async load(src: any, opts?: PlayerOptions): Promise<void> {
    this.emitter.emit(PlayerEventType.LOAD_START);
    
    try {
      // 解析音頻序列參數（假設src是Tone.js序列定義）
      await Tone.start(); // 確保音頻上下文已啟動
      this.sequence = new Tone.Sequence(...);
      this.state = PlayerState.READY;
      this.emitter.emit(PlayerEventType.LOAD_COMPLETE);
    } catch (error) {
      this.state = PlayerState.ERROR;
      this.emitter.emit(PlayerEventType.LOAD_ERROR, error);
      throw error;
    }
  }
  
  play(at?: number): void {
    if (this.state !== PlayerState.READY && this.state !== PlayerState.PAUSED) {
      return;
    }
    
    // 在指定時間開始播放序列
    const startTime = at ? Tone.now() + at : Tone.now();
    this.sequence?.start(startTime);
    this.state = PlayerState.PLAYING;
    this.emitter.emit(PlayerEventType.PLAY_START, { time: startTime });
    
    // 設置播放結束監聽
    this.monitorPlaybackEnd();
  }
  
  // ... 其他方法實現 ...
  
  on(event: PlayerEventType, callback: Function): void {
    this.emitter.on(event, callback as any);
  }
  
  off(event: PlayerEventType, callback: Function): void {
    this.emitter.off(event, callback as any);
  }
  
  private monitorPlaybackEnd(): void {
    // 因為Tone.js序列沒有內建的結束事件，需要手動計算
    // 這裡假設我們知道序列的總時長
    const duration = this.calculateDuration();
    setTimeout(() => {
      if (this.state === PlayerState.PLAYING) {
        this.state = PlayerState.READY;
        this.emitter.emit(PlayerEventType.PLAY_END);
      }
    }, duration * 1000);
  }
  
  private calculateDuration(): number {
    // 計算序列總時長的邏輯
    // ...
    return 0; // 示例
  }
}
```

#### PreRecordedPlayer 實現概要

```typescript
// PreRecordedPlayer.ts
import { IAudioPlayer, PlayerEventType, PlayerState, PlayerOptions } from './IAudioPlayer';
import mitt from 'mitt';

export class PreRecordedPlayer implements IAudioPlayer {
  private emitter = mitt();
  private audioElement: HTMLAudioElement | null = null;
  private state: PlayerState = PlayerState.IDLE;
  
  constructor() {
    this.audioElement = new Audio();
    this.setupAudioElementEvents();
  }
  
  async load(src: string, opts?: PlayerOptions): Promise<void> {
    this.emitter.emit(PlayerEventType.LOAD_START);
    
    try {
      if (!this.audioElement) {
        this.audioElement = new Audio();
        this.setupAudioElementEvents();
      }
      
      this.state = PlayerState.LOADING;
      this.audioElement.src = src;
      
      // 等待音頻加載完成
      await new Promise<void>((resolve, reject) => {
        const onCanPlay = () => {
          this.audioElement?.removeEventListener('canplaythrough', onCanPlay);
          this.audioElement?.removeEventListener('error', onError);
          resolve();
        };
        
        const onError = (e: ErrorEvent) => {
          this.audioElement?.removeEventListener('canplaythrough', onCanPlay);
          this.audioElement?.removeEventListener('error', onError);
          reject(new Error(`Failed to load audio: ${e.message}`));
        };
        
        this.audioElement?.addEventListener('canplaythrough', onCanPlay, { once: true });
        this.audioElement?.addEventListener('error', onError, { once: true });
      });
      
      this.state = PlayerState.READY;
      this.emitter.emit(PlayerEventType.LOAD_COMPLETE);
    } catch (error) {
      this.state = PlayerState.ERROR;
      this.emitter.emit(PlayerEventType.LOAD_ERROR, error);
      throw error;
    }
  }
  
  play(at?: number): void {
    if (!this.audioElement || this.state !== PlayerState.READY && this.state !== PlayerState.PAUSED) {
      return;
    }
    
    // 如果指定了開始時間，設置currentTime
    if (at !== undefined) {
      this.audioElement.currentTime = at;
    }
    
    // 開始播放
    this.audioElement.play()
      .then(() => {
        this.state = PlayerState.PLAYING;
        this.emitter.emit(PlayerEventType.PLAY_START, { time: this.audioElement?.currentTime || 0 });
      })
      .catch(error => {
        this.state = PlayerState.ERROR;
        this.emitter.emit(PlayerEventType.PLAY_ERROR, error);
      });
  }
  
  // ... 其他方法實現 ...
  
  private setupAudioElementEvents(): void {
    if (!this.audioElement) return;
    
    this.audioElement.addEventListener('ended', () => {
      this.state = PlayerState.READY;
      this.emitter.emit(PlayerEventType.PLAY_END);
    });
    
    this.audioElement.addEventListener('timeupdate', () => {
      if (this.state === PlayerState.PLAYING) {
        this.emitter.emit(PlayerEventType.TIME_UPDATE, {
          time: this.audioElement?.currentTime || 0,
          duration: this.audioElement?.duration || 0
        });
      }
    });
    
    this.audioElement.addEventListener('error', (e) => {
      this.state = PlayerState.ERROR;
      this.emitter.emit(PlayerEventType.PLAY_ERROR, e);
    });
  }
}
```

### AudioCoordinator 實現概要

以下是 AudioCoordinator 的核心實現概要：

```typescript
// AudioCoordinator.ts
import mitt from 'mitt';
import { IAudioPlayer, PlayerEventType, PlayerState } from './IAudioPlayer';

type AudioCoordinatorEvents = {
  'request:start': { id: string, info: SoundInfo };
  'request:end': { id: string, info: SoundInfo };
  'request:error': { id: string, info: SoundInfo, error: any };
  'track:status': { track: string, active: boolean };
  'marker:reached': { id: string, marker: string, time: number };
};

export class AudioCoordinator {
  private emitter = mitt<AudioCoordinatorEvents>();
  private players: Map<string, IAudioPlayer> = new Map();
  private activeSounds: Map<string, SoundInfo> = new Map();
  private queues: Map<string, SoundInfo[]> = new Map();
  private defaultTrack: string = 'default';
  private trackVolumes: Map<string, number> = new Map();
  private playerTypeDefault: string = 'audio'; // 預設播放器類型
  
  constructor(config?: AudioCoordinatorConfig) {
    this.setupTracks(config?.tracks || [this.defaultTrack]);
    this.trackVolumes.set(this.defaultTrack, 1);
  }
  
  registerPlayer(type: string, player: IAudioPlayer): void {
    this.players.set(type, player);
    
    // 轉發播放器事件
    player.on(PlayerEventType.PLAY_END, () => {
      // 尋找與此播放器相關的活動聲音
      const endedSoundEntry = [...this.activeSounds.entries()].find(
        ([id, info]) => info.playerInstance === player
      );
      
      if (endedSoundEntry) {
        const [id, info] = endedSoundEntry;
        this.activeSounds.delete(id);
        this.emitter.emit('request:end', { id, info });
        
        // 處理隊列
        this.processQueue(info.track);
      }
    });
    
    // 設置其他事件處理...
  }
  
  async play(request: PlayRequest): Promise<string> {
    const id = this.generateRequestId();
    const track = request.track || this.defaultTrack;
    const playerType = request.type || this.playerTypeDefault;
    
    const player = this.getPlayer(playerType);
    if (!player) {
      throw new Error(`No player registered for type: ${playerType}`);
    }
    
    const soundInfo: SoundInfo = {
      id,
      track,
      source: request.source,
      type: playerType,
      priority: request.priority || 0,
      startTime: request.startTime,
      playerInstance: player
    };
    
    const canPlayNow = this.canPlayOnTrack(track, soundInfo.priority);
    
    if (canPlayNow) {
      try {
        // 加載並播放
        await player.load(request.source, request.options);
        
        // 設置音量（結合軌道音量和請求音量）
        const trackVolume = this.getVolume(track);
        const requestVolume = request.volume !== undefined ? request.volume : 1;
        player.setVolume(trackVolume * requestVolume);
        
        // 開始播放
        player.play(request.startTime);
        
        // 更新狀態
        this.activeSounds.set(id, soundInfo);
        this.emitter.emit('request:start', { id, info: soundInfo });
        
        return id;
      } catch (error) {
        this.emitter.emit('request:error', { id, info: soundInfo, error });
        throw error;
      }
    } else {
      // 加入隊列
      if (!this.queues.has(track)) {
        this.queues.set(track, []);
      }
      this.queues.get(track)?.push(soundInfo);
      return id;
    }
  }
  
  // ... 其他方法實現 ...
  
  private canPlayOnTrack(track: string, priority: number): boolean {
    const currentActive = [...this.activeSounds.values()].filter(s => s.track === track);
    
    if (currentActive.length === 0) {
      return true;
    }
    
    // 檢查是否有正在播放的聲音優先級低於當前請求
    return currentActive.some(sound => sound.priority < priority);
  }
  
  private processQueue(track: string): void {
    const queue = this.queues.get(track) || [];
    if (queue.length === 0) {
      return;
    }
    
    // 按優先級排序隊列
    queue.sort((a, b) => b.priority - a.priority);
    
    const nextSound = queue.shift();
    if (nextSound && this.canPlayOnTrack(track, nextSound.priority)) {
      // 更新隊列
      this.queues.set(track, queue);
      
      // 創建新的播放請求
      this.play({
        source: nextSound.source,
        track: nextSound.track,
        type: nextSound.type,
        priority: nextSound.priority,
        startTime: nextSound.startTime
      }).catch(error => {
        console.error('Failed to play queued sound:', error);
      });
    }
  }
  
  private setupTracks(tracks: string[]): void {
    tracks.forEach(track => {
      this.trackVolumes.set(track, 1);
      this.queues.set(track, []);
    });
  }
  
  private generateRequestId(): string {
    return `sound_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
  }
}
```

## 與前端面板的整合

// ... existing code ...