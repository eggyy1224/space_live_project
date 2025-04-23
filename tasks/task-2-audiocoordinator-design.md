# AudioCoordinator 組件設計

## 核心定位

AudioCoordinator（聲音協調系統）是系統的核心組件，**專注於決策邏輯、資源調度和優先級管理**，而不參與實際的播放行為。它決定「何時播放什麼」，而實際的播放執行則委託給專門的Player組件。

## 設計原則

1. **協調而非播放**：清晰分離職責，AudioCoordinator專注決策，Player專注執行。
2. **統一入口**：所有聲音播放請求必須通過AudioCoordinator處理。
3. **優先級管理**：實現智能的優先級管理和聲音讓步（Ducking）機制。
4. **事件驅動**：基於事件系統實現組件間鬆耦合通信。
5. **可擴展設計**：支持輕鬆添加新的聲音類型和處理邏輯。

## 架構設計

### 組件關係圖

```
[UI組件] --> [AudioCoordinator] --> [Player組件]
    ^                |                   |
    |                v                   v
    +------ [Event Bus] <----------------+
```

- **UI組件**發送播放請求給AudioCoordinator
- **AudioCoordinator**處理請求並委派給適當的Player
- **Player組件**執行實際播放並報告狀態
- **Event Bus**連接所有組件，實現鬆耦合通信

### 核心接口設計

#### AudioCoordinator 接口

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
  
  // 時間軸解析
  scheduleFromJson(timeline: AudioTimeline): Promise<string[]>;
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

// 音頻信息
interface SoundInfo {
  id: string;            // 請求ID
  track: string;         // 所在軌道
  type: string;          // 聲音類型
  source: any;           // 聲音源
  priority: number;      // 優先級
  state: SoundState;     // 當前狀態
  startTime?: number;    // 開始播放時間
  endTime?: number;      // 預計結束時間
  options: any;          // 播放選項
}

// 聲音狀態
enum SoundState {
  PENDING = 'pending',   // 等待播放
  LOADING = 'loading',   // 加載中
  PLAYING = 'playing',   // 播放中
  PAUSED = 'paused',     // 暫停
  STOPPED = 'stopped',   // 已停止
  FINISHED = 'finished', // 播放完成
  ERROR = 'error'        // 錯誤
}

// 時間軸結構
interface AudioTimeline {
  timeline: TimelineEvent[];
}

interface TimelineEvent {
  track: string;         // 目標軌道
  startTime: number;     // 開始時間
  type: string;          // 聲音類型
  resource: string;      // 資源ID或URL
  duration?: number;     // 持續時間
  [key: string]: any;    // 其他屬性
}
```

#### Player 接口

```typescript
interface IAudioPlayer {
  // 基本信息
  readonly id: string;
  readonly type: string;
  
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
  isPlaying(): boolean;
  getCurrentTime(): number;
  getDuration(): number;
  
  // 事件處理
  on(event: string, callback: Function): void;
  off(event: string, callback: Function): void;
}
```

## 功能實現

### 1. 軌道管理

AudioCoordinator需要管理多個獨立的聲音軌道：

```typescript
class AudioCoordinator {
  private tracks: Map<string, Track> = new Map();
  
  constructor() {
    // 初始化默認軌道
    this.tracks.set('voice', new Track('voice', 100)); // 最高優先級
    this.tracks.set('sfx', new Track('sfx', 70));
    this.tracks.set('ambient', new Track('ambient', 50));
    this.tracks.set('music', new Track('music', 30)); // 最低優先級
  }
  
  // 獲取軌道
  private getTrack(trackName: string): Track {
    if (!this.tracks.has(trackName)) {
      this.tracks.set(trackName, new Track(trackName, 50)); // 默認中等優先級
    }
    return this.tracks.get(trackName)!;
  }
}

class Track {
  private queue: SoundInfo[] = [];
  private activeSounds: Map<string, SoundInfo> = new Map();
  private volume: number = 1.0;
  
  constructor(
    public readonly name: string,
    public readonly basePriority: number
  ) {}
  
  // 軌道方法實現...
}
```

### 2. 優先級處理

AudioCoordinator需要實現智能的優先級管理：

```typescript
class AudioCoordinator {
  // 處理優先級衝突
  private handlePriorityConflict(track: Track, request: PlayRequest): PriorityResolution {
    const activeSounds = track.getActiveSounds();
    
    if (activeSounds.length === 0) {
      return { canPlay: true }; // 沒有衝突
    }
    
    // 檢查是否有更高優先級的聲音正在播放
    const higherPrioritySounds = activeSounds.filter(sound => 
      sound.priority > request.priority
    );
    
    if (higherPrioritySounds.length > 0) {
      if (track.name === 'voice') {
        // 語音軌道通常一次只播一段語音，所以排隊
        return { canPlay: false, action: 'queue' };
      } else {
        // 其他軌道可以混合或並行播放
        return { canPlay: true, action: 'parallel', volumeAdjust: 0.7 };
      }
    }
    
    // 如果新的聲音優先級更高，則可以打斷現有聲音
    return { 
      canPlay: true, 
      action: 'interrupt',
      soundsToStop: activeSounds.map(sound => sound.id)
    };
  }
}

interface PriorityResolution {
  canPlay: boolean;
  action?: 'queue' | 'parallel' | 'interrupt';
  volumeAdjust?: number;
  soundsToStop?: string[];
}
```

### 3. Ducking 機制

當重要聲音播放時，自動降低其他軌道音量：

```typescript
class AudioCoordinator {
  // 應用Ducking效果
  private applyDucking(activeTrack: string): void {
    // 語音軌道播放時，降低其他軌道音量
    if (activeTrack === 'voice') {
      for (const [trackName, track] of this.tracks.entries()) {
        if (trackName !== 'voice') {
          // 保存原始音量
          const originalVolume = track.getVolume();
          track.setDuckingState(true, originalVolume);
          
          // 根據軌道類型設置不同的降低程度
          let duckVolume = 0.3; // 默認降至30%
          if (trackName === 'music') duckVolume = 0.2; // 音樂降得更多
          if (trackName === 'ambient') duckVolume = 0.4; // 環境音降得稍少
          
          track.setVolume(originalVolume * duckVolume);
          
          // 通知相關播放器調整音量
          track.getActiveSounds().forEach(sound => {
            const player = this.getPlayer(sound.type);
            if (player) {
              player.setVolume(track.getVolume());
            }
          });
        }
      }
    }
  }
  
  // 恢復Ducking效果
  private restoreDucking(exceptTrack?: string): void {
    for (const [trackName, track] of this.tracks.entries()) {
      if (trackName !== exceptTrack && track.isDucking()) {
        track.setVolume(track.getOriginalVolume());
        track.setDuckingState(false);
        
        // 通知相關播放器恢復音量
        track.getActiveSounds().forEach(sound => {
          const player = this.getPlayer(sound.type);
          if (player) {
            player.setVolume(track.getVolume());
          }
        });
      }
    }
  }
}

class Track {
  private ducking: boolean = false;
  private originalVolume: number = 1.0;
  
  setDuckingState(ducking: boolean, originalVolume?: number): void {
    this.ducking = ducking;
    if (originalVolume !== undefined) {
      this.originalVolume = originalVolume;
    }
  }
  
  isDucking(): boolean {
    return this.ducking;
  }
  
  getOriginalVolume(): number {
    return this.originalVolume;
  }
}
```

### 4. 時間軸處理

處理後端傳來的AudioTimeline JSON：

```typescript
class AudioCoordinator {
  // 從JSON排程播放
  async scheduleFromJson(timeline: AudioTimeline): Promise<string[]> {
    const requestIds: string[] = [];
    
    // 排序時間軸事件
    const sortedEvents = [...timeline.timeline].sort((a, b) => 
      a.startTime - b.startTime
    );
    
    const now = this.getCurrentTime();
    
    // 處理每個事件
    for (const event of sortedEvents) {
      // 轉換為播放請求
      const request: PlayRequest = {
        track: event.track,
        type: this.getTypeFromEvent(event),
        source: this.resolveResource(event.resource, event.type),
        priority: this.getPriorityFromEvent(event),
        options: {
          startAt: event.startTime,
          duration: event.duration,
          loop: event.loop,
          volume: event.volume,
          // 其他選項轉換...
        }
      };
      
      // 若為Combo類型，展開為多個事件
      if (event.type === 'combo') {
        const comboIds = await this.expandCombo(event, now);
        requestIds.push(...comboIds);
      } else {
        // 計算實際播放時間
        const playTime = now + event.startTime;
        
        // 若時間尚未到，設置計時器
        if (playTime > now) {
          const timeout = playTime - now;
          setTimeout(() => {
            this.play(request).catch(err => {
              console.error(`Failed to play scheduled event: ${err.message}`);
            });
          }, timeout * 1000);
          requestIds.push(`scheduled_${Date.now()}_${Math.random()}`);
        } else {
          // 時間已到或過期，立即播放
          try {
            const id = await this.play(request);
            requestIds.push(id);
          } catch (err) {
            console.error(`Failed to play timeline event: ${err.message}`);
          }
        }
      }
    }
    
    return requestIds;
  }
  
  // 展開Combo事件
  private async expandCombo(
    comboEvent: TimelineEvent, 
    baseTime: number
  ): Promise<string[]> {
    const comboIds: string[] = [];
    const comboDefinition = await this.getComboDefinition(comboEvent.resource);
    
    if (!comboDefinition || !comboDefinition.sequence) {
      throw new Error(`Combo definition not found: ${comboEvent.resource}`);
    }
    
    let currentOffset = 0;
    
    // 處理序列中的每個音效
    for (const item of comboDefinition.sequence) {
      const request: PlayRequest = {
        track: comboEvent.track,
        type: item.type || 'sfx',
        source: this.resolveResource(item.resource, item.type),
        priority: this.getPriorityFromEvent(comboEvent),
        options: {
          startAt: baseTime + comboEvent.startTime + currentOffset,
          duration: item.duration,
          volume: item.volume !== undefined ? item.volume : comboEvent.volume,
          // 其他選項...
        }
      };
      
      // 計算下一個音效的時間偏移
      currentOffset += item.duration || 0.5; // 默認0.5秒
      
      // 設置計時器
      const timeout = (comboEvent.startTime + currentOffset - 
        (Date.now() / 1000 - baseTime)) * 1000;
      
      if (timeout > 0) {
        setTimeout(() => {
          this.play(request).catch(err => {
            console.error(`Failed to play combo item: ${err.message}`);
          });
        }, timeout);
        comboIds.push(`combo_${Date.now()}_${Math.random()}`);
      } else {
        try {
          const id = await this.play(request);
          comboIds.push(id);
        } catch (err) {
          console.error(`Failed to play combo item: ${err.message}`);
        }
      }
    }
    
    return comboIds;
  }
}
```

## 事件處理機制

使用事件總線實現鬆耦合通信：

```typescript
class AudioCoordinator {
  private eventBus: EventEmitter;
  
  constructor() {
    this.eventBus = new EventEmitter();
    
    // 訂閱Player事件
    this.eventBus.on('player:ended', this.handlePlaybackEnded.bind(this));
    this.eventBus.on('player:error', this.handlePlaybackError.bind(this));
    // 其他事件處理...
  }
  
  // 處理播放結束事件
  private handlePlaybackEnded(data: { playerId: string, soundId: string }): void {
    // 找到對應的聲音信息
    const sound = this.findSoundById(data.soundId);
    if (!sound) return;
    
    // 更新狀態
    sound.state = SoundState.FINISHED;
    
    // 從活動列表中移除
    const track = this.getTrack(sound.track);
    track.removeActiveSound(sound.id);
    
    // 檢查是否需要恢復Ducking
    if (sound.track === 'voice' && track.getActiveSounds().length === 0) {
      this.restoreDucking('voice');
    }
    
    // 檢查隊列中是否有等待的聲音
    const nextSound = track.dequeueSound();
    if (nextSound) {
      // 播放下一個排隊的聲音
      this.playSound(nextSound).catch(err => {
        console.error(`Failed to play queued sound: ${err.message}`);
      });
    }
    
    // 發送事件通知
    this.eventBus.emit('audio:ended', {
      id: sound.id,
      track: sound.track,
      type: sound.type
    });
  }
  
  // 向外部訂閱事件
  on(event: string, callback: Function): void {
    this.eventBus.on(event, callback);
  }
  
  off(event: string, callback: Function): void {
    this.eventBus.off(event, callback);
  }
}
```

## 與其他系統的整合

### 與VoiceEffectsProcessor整合

```typescript
class AudioCoordinator {
  private voiceEffectsProcessor: VoiceEffectsProcessor;
  
  constructor(voiceEffectsProcessor?: VoiceEffectsProcessor) {
    // 其他初始化...
    
    this.voiceEffectsProcessor = voiceEffectsProcessor || new VoiceEffectsProcessor();
    
    // 註冊TTSPlayer
    const ttsPlayer = new TTSPlayer('tts', this.voiceEffectsProcessor);
    this.registerPlayer('tts', ttsPlayer);
  }
  
  // 應用語音效果
  applyVoiceEffect(preset: string): void {
    this.voiceEffectsProcessor.applyPreset(preset);
  }
  
  resetVoiceEffects(): void {
    this.voiceEffectsProcessor.resetEffects();
  }
}
```

### 與TTS系統整合

```typescript
class TTSPlayer implements IAudioPlayer {
  constructor(
    private id: string,
    private voiceEffectsProcessor: VoiceEffectsProcessor
  ) {}
  
  async load(src: any, opts?: PlayerOptions): Promise<void> {
    // 加載TTS音頻
    await this.voiceEffectsProcessor.loadTTSAudio(src);
    
    // 設置同步點
    if (opts?.syncPoints) {
      this.voiceEffectsProcessor.setSyncPoints(opts.syncPoints);
    }
  }
  
  play(at?: number): void {
    // 播放並處理同步點事件
    this.voiceEffectsProcessor.playTTS();
    
    // 添加標記點事件監聽
    this.voiceEffectsProcessor.on('marker', (marker) => {
      this.emit('marker', {
        playerId: this.id,
        marker
      });
    });
  }
  
  // 其他方法實現...
}
```

## 實現路徑

實現AudioCoordinator的推薦路徑：

1. **定義接口階段**：首先定義所有接口、類型和事件規範
2. **基礎功能階段**：實現核心播放控制和軌道管理
3. **優先級系統階段**：添加優先級處理和Ducking機制
4. **時間軸解析階段**：實現JSON解析和事件排程
5. **播放器整合階段**：整合各種播放器和處理器
6. **測試與優化階段**：全面測試各種場景和邊緣情況

## 預期成果

成功實現AudioCoordinator將帶來以下好處：

1. **統一的聲音管理**：所有聲音請求通過單一協調器處理
2. **智能優先級處理**：重要聲音不會被次要聲音干擾
3. **自動音量調整**：角色說話時背景音自動降低
4. **模組化架構**：各組件職責清晰，易於維護和擴展
5. **標準化接口**：前後端通過標準JSON格式通信 