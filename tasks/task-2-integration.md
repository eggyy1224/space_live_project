# VoiceEffectsPanel與TTS系統整合方案

## 整合目標

本文檔描述如何將VoiceEffectsPanel（語音效果面板）與TTS（文字轉語音）系統整合到AudioCoordinator架構中，以實現語音效果的實時處理和統一管理。

主要目標包括：
1. 實現VoiceEffectsPanel的UI組件
2. 設計VoiceEffectsProcessor服務
3. 將TTS系統與AudioCoordinator整合
4. 定義語音處理與表情同步機制

## 架構關係

整合後的系統架構關係如下：

```
                 +----------------------+
                 |    AudioCoordinator  |
                 +-----------+----------+
                             |
            +----------------+----------------+
            |                                 |
 +----------v----------+         +-----------v-----------+
 |    TTSPlayer        |-------->| VoiceEffectsProcessor |
 +---------------------+         +-----------+-----------+
                                             |
                                 +-----------v-----------+
                                 |   VoiceEffectsPanel   |
                                 +-----------------------+
```

- `VoiceEffectsPanel`：提供語音效果選擇和參數調整的UI界面
- `VoiceEffectsProcessor`：語音效果處理服務，負責應用音效處理
- `TTSPlayer`：TTS播放器，負責處理TTS音頻的播放
- `AudioCoordinator`：聲音協調中心，協調各個組件之間的通信

## VoiceEffectsPanel 設計

VoiceEffectsPanel是一個React組件，負責提供用戶界面來控制語音效果。

### 功能需求

1. 提供預設語音效果列表選擇
2. 允許調整效果參數（如混響、音調、均衡器等）
3. 支持實時預覽效果
4. 顯示當前應用的效果和參數
5. 與AudioCoordinator集成，應用效果到TTS播放

### 界面設計

```tsx
// src/components/VoiceEffectsPanel.tsx
import React, { useState, useEffect } from 'react';
import { Select, Slider, Button, Card, Tabs } from 'antd';
import { useAudioCoordinator } from '../hooks/useAudioCoordinator';

const { TabPane } = Tabs;
const { Option } = Select;

// 預設效果列表
const PRESETS = [
  { id: 'default', name: '預設語音' },
  { id: 'robot', name: '機器人' },
  { id: 'alien', name: '外星人' },
  { id: 'echo', name: '回音' },
  { id: 'underwater', name: '水下效果' },
  { id: 'telephone', name: '電話' },
  { id: 'concert-hall', name: '音樂廳' },
];

export const VoiceEffectsPanel: React.FC = () => {
  const [activePreset, setActivePreset] = useState<string>('default');
  const [reverbAmount, setReverbAmount] = useState<number>(0);
  const [pitchShift, setPitchShift] = useState<number>(0);
  const [filterFreq, setFilterFreq] = useState<number>(1000);
  const audioCoordinator = useAudioCoordinator();
  
  // 應用預設效果
  const applyPreset = (presetId: string) => {
    setActivePreset(presetId);
    audioCoordinator.applyVoiceEffect(presetId);
  };
  
  // 重置效果
  const resetEffects = () => {
    setActivePreset('default');
    setReverbAmount(0);
    setPitchShift(0);
    setFilterFreq(1000);
    audioCoordinator.resetVoiceEffects();
  };
  
  // 調整混響參數
  const handleReverbChange = (value: number) => {
    setReverbAmount(value);
    audioCoordinator.setVoiceEffectParameter('reverb', 'wet', value / 100);
  };
  
  // 調整音調參數
  const handlePitchChange = (value: number) => {
    setPitchShift(value);
    audioCoordinator.setVoiceEffectParameter('pitch', 'pitch', value);
  };
  
  // 調整濾波器參數
  const handleFilterChange = (value: number) => {
    setFilterFreq(value);
    audioCoordinator.setVoiceEffectParameter('filter', 'frequency', value);
  };
  
  // 預覽效果
  const previewEffect = () => {
    audioCoordinator.previewVoiceEffect();
  };
  
  return (
    <Card title="語音效果控制" style={{ width: '100%' }}>
      <Tabs defaultActiveKey="presets">
        <TabPane tab="預設效果" key="presets">
          <div style={{ marginBottom: 16 }}>
            <Select
              style={{ width: '100%' }}
              value={activePreset}
              onChange={applyPreset}
            >
              {PRESETS.map(preset => (
                <Option key={preset.id} value={preset.id}>
                  {preset.name}
                </Option>
              ))}
            </Select>
          </div>
          <Button type="primary" onClick={previewEffect} style={{ marginRight: 8 }}>
            預覽效果
          </Button>
          <Button onClick={resetEffects}>
            重置效果
          </Button>
        </TabPane>
        
        <TabPane tab="進階設定" key="advanced">
          <div style={{ marginBottom: 16 }}>
            <div>混響量</div>
            <Slider 
              min={0} 
              max={100} 
              value={reverbAmount} 
              onChange={handleReverbChange}
            />
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <div>音調調整</div>
            <Slider 
              min={-12} 
              max={12} 
              value={pitchShift} 
              onChange={handlePitchChange}
              marks={{ 
                '-12': '-12', 
                '-6': '-6', 
                '0': '0', 
                '6': '+6', 
                '12': '+12' 
              }}
            />
          </div>
          
          <div style={{ marginBottom: 16 }}>
            <div>濾波器頻率</div>
            <Slider 
              min={100} 
              max={10000} 
              value={filterFreq} 
              onChange={handleFilterChange}
              marks={{ 
                '100': '100Hz', 
                '1000': '1kHz', 
                '10000': '10kHz' 
              }}
              step={100}
            />
          </div>
        </TabPane>
      </Tabs>
    </Card>
  );
};
```

## VoiceEffectsProcessor 設計

VoiceEffectsProcessor是一個服務類，負責實際處理語音效果。它基於Web Audio API和Tone.js實現各種效果。

### 功能需求

1. 初始化Tone.js效果鏈
2. 提供預設效果的快速應用
3. 支持個別效果參數調整
4. 加載和處理TTS音頻
5. 處理表情同步標記點

### 實現設計

```typescript
// src/services/VoiceEffectsProcessor.ts
import * as Tone from 'tone';
import mitt from 'mitt';

// 效果預設配置
const EFFECT_PRESETS = {
  default: {},
  robot: {
    pitch: { pitch: -4 },
    filter: { frequency: 700, type: 'bandpass', Q: 2 },
    distortion: { distortion: 0.4 }
  },
  alien: {
    pitch: { pitch: 7 },
    phaser: { frequency: 0.5, octaves: 3, wet: 0.7 },
    reverb: { decay: 10, wet: 0.5 }
  },
  // 其他預設...
};

export class VoiceEffectsProcessor {
  private player: Tone.Player | null = null;
  private effects: Map<string, any> = new Map();
  private effectChain: any[] = [];
  private syncPoints: any[] = [];
  private eventEmitter = mitt();
  
  constructor() {
    this.initializeEffects();
  }
  
  // 初始化效果鏈
  private initializeEffects(): void {
    // 創建各種效果
    this.effects.set('reverb', new Tone.Reverb({ decay: 1.5, wet: 0 }).toDestination());
    this.effects.set('pitch', new Tone.PitchShift(0).connect(this.effects.get('reverb')));
    this.effects.set('filter', new Tone.Filter({ frequency: 1000 }).connect(this.effects.get('pitch')));
    this.effects.set('distortion', new Tone.Distortion(0).connect(this.effects.get('filter')));
    this.effects.set('phaser', new Tone.Phaser({ frequency: 0.5, octaves: 3, wet: 0 }).connect(this.effects.get('distortion')));
    
    // 建立效果順序
    this.effectChain = [
      this.effects.get('phaser'),
      this.effects.get('distortion'),
      this.effects.get('filter'),
      this.effects.get('pitch'),
      this.effects.get('reverb')
    ];
    
    // 初始化播放器
    this.player = new Tone.Player().connect(this.effects.get('phaser'));
    
    // 音頻完成事件
    this.player.onstop = () => this.eventEmitter.emit('ended', {});
  }
  
  // 應用預設效果
  public applyPreset(presetId: string): void {
    if (!EFFECT_PRESETS[presetId]) {
      console.warn(`Preset ${presetId} not found, using default`);
      this.resetEffects();
      return;
    }
    
    this.resetEffects(); // 先重置
    
    // 應用預設參數
    const preset = EFFECT_PRESETS[presetId];
    Object.entries(preset).forEach(([effectName, params]) => {
      if (this.effects.has(effectName)) {
        const effect = this.effects.get(effectName);
        Object.entries(params).forEach(([param, value]) => {
          effect[param] = value;
        });
      }
    });
    
    console.log(`Applied voice effect preset: ${presetId}`);
  }
  
  // 設置效果參數
  public setEffectParameter(effectName: string, param: string, value: any): void {
    if (this.effects.has(effectName)) {
      const effect = this.effects.get(effectName);
      effect[param] = value;
      console.log(`Set ${effectName}.${param} = ${value}`);
    } else {
      console.warn(`Effect ${effectName} not found`);
    }
  }
  
  // 重置所有效果
  public resetEffects(): void {
    this.effects.get('reverb').wet.value = 0;
    this.effects.get('pitch').pitch = 0;
    this.effects.get('filter').frequency.value = 1000;
    this.effects.get('distortion').distortion = 0;
    this.effects.get('phaser').wet.value = 0;
    console.log('Reset all voice effects');
  }
  
  // 加載TTS音頻
  public async loadTTSAudio(src: string): Promise<void> {
    if (!this.player) return;
    
    await Tone.loaded();
    this.player.load(src);
    console.log(`Loaded TTS audio: ${src}`);
  }
  
  // 設置同步點
  public setSyncPoints(points: any[]): void {
    this.syncPoints = points;
  }
  
  // 播放TTS
  public async playTTS(): Promise<void> {
    if (!this.player) return;
    
    try {
      // 確保音頻上下文已啟動
      await Tone.start();
      
      // 如果已有同步點，設置標記點事件
      if (this.syncPoints && this.syncPoints.length > 0) {
        let prevTime = 0;
        
        this.syncPoints.forEach(point => {
          const timeInSeconds = point.time;
          const marker = point.marker;
          
          // 設置計時器在適當時間觸發標記點事件
          setTimeout(() => {
            this.eventEmitter.emit('marker', { 
              time: timeInSeconds,
              marker
            });
          }, (timeInSeconds - prevTime) * 1000);
          
          prevTime = timeInSeconds;
        });
      }
      
      // 開始播放
      this.player.start();
      console.log('Started TTS playback');
      
      this.eventEmitter.emit('started', {});
    } catch (error) {
      console.error('Failed to play TTS:', error);
      this.eventEmitter.emit('error', { error });
    }
  }
  
  // 停止播放
  public stopTTS(): void {
    if (this.player) {
      this.player.stop();
      console.log('Stopped TTS playback');
    }
  }
  
  // 事件處理
  public on(event: string, callback: any): void {
    this.eventEmitter.on(event, callback);
  }
  
  public off(event: string, callback: any): void {
    this.eventEmitter.off(event, callback);
  }
}
```

## TTSPlayer 設計

TTSPlayer是實現IAudioPlayer接口的類，負責處理TTS音頻的播放。

```typescript
// src/services/players/TTSPlayer.ts
import { IAudioPlayer } from './IAudioPlayer';

export class TTSPlayer implements IAudioPlayer {
  private currentSoundId: string | null = null;
  private isPlaying: boolean = false;
  private eventEmitter = mitt();
  
  constructor(
    public readonly id: string, 
    private voiceEffectsProcessor: VoiceEffectsProcessor
  ) {
    // 監聽VoiceEffectsProcessor的事件
    this.voiceEffectsProcessor.on('started', () => {
      this.isPlaying = true;
      this.eventEmitter.emit('player:started', {
        playerId: this.id,
        soundId: this.currentSoundId
      });
    });
    
    this.voiceEffectsProcessor.on('ended', () => {
      this.isPlaying = false;
      this.eventEmitter.emit('player:ended', {
        playerId: this.id,
        soundId: this.currentSoundId
      });
      this.currentSoundId = null;
    });
    
    this.voiceEffectsProcessor.on('marker', (data) => {
      this.eventEmitter.emit('player:marker', {
        playerId: this.id,
        soundId: this.currentSoundId,
        marker: data.marker,
        time: data.time
      });
    });
    
    this.voiceEffectsProcessor.on('error', (data) => {
      this.isPlaying = false;
      this.eventEmitter.emit('player:error', {
        playerId: this.id,
        soundId: this.currentSoundId,
        error: data.error
      });
    });
  }
  
  // IAudioPlayer接口實現
  async load(src: any, opts?: any): Promise<void> {
    // 保存當前聲音ID
    this.currentSoundId = opts?.soundId || `tts_${Date.now()}`;
    
    // 設置同步點（如果有）
    if (opts?.syncPoints) {
      this.voiceEffectsProcessor.setSyncPoints(opts.syncPoints);
    }
    
    // 加載音頻
    await this.voiceEffectsProcessor.loadTTSAudio(src);
  }
  
  unload(): void {
    this.stop();
    this.currentSoundId = null;
  }
  
  play(): void {
    if (this.currentSoundId) {
      this.voiceEffectsProcessor.playTTS();
    }
  }
  
  stop(): void {
    this.voiceEffectsProcessor.stopTTS();
    this.isPlaying = false;
  }
  
  pause(): void {
    // Tone.js Player目前不支持暫停，需要擴展實現
    console.warn('TTSPlayer: pause not implemented');
  }
  
  resume(): void {
    // Tone.js Player目前不支持恢復，需要擴展實現
    console.warn('TTSPlayer: resume not implemented');
  }
  
  setVolume(volume: number): void {
    // 需要實現音量控制
    console.warn('TTSPlayer: setVolume not implemented');
  }
  
  setRate(rate: number): void {
    // 需要實現速率控制
    console.warn('TTSPlayer: setRate not implemented');
  }
  
  getCurrentTime(): number {
    // 需要從底層獲取當前播放位置
    return 0;
  }
  
  getDuration(): number {
    // 需要從底層獲取總時長
    return 0;
  }
  
  isPlaying(): boolean {
    return this.isPlaying;
  }
  
  on(event: string, callback: Function): void {
    this.eventEmitter.on(event, callback);
  }
  
  off(event: string, callback: Function): void {
    this.eventEmitter.off(event, callback);
  }
}
```

## AudioCoordinator 與 TTS 系統整合

為了將TTS系統與AudioCoordinator整合，需要在AudioCoordinator中添加相關功能。

```typescript
// src/services/AudioCoordinator.ts (添加TTS相關功能)
class AudioCoordinator {
  // 其他代碼...
  
  constructor() {
    // 其他初始化...
    
    // 初始化VoiceEffectsProcessor
    this.voiceEffectsProcessor = new VoiceEffectsProcessor();
    
    // 註冊TTSPlayer
    const ttsPlayer = new TTSPlayer('tts', this.voiceEffectsProcessor);
    this.registerPlayer('tts', ttsPlayer);
    
    // 監聽標記點事件，用於表情同步
    ttsPlayer.on('player:marker', (data) => {
      // 轉發給表情系統
      this.eventBus.emit('voice:marker', {
        soundId: data.soundId,
        marker: data.marker,
        time: data.time
      });
    });
  }
  
  // 處理TTS播放請求
  async playTTS(text: string, options?: {
    priority?: number,
    voiceEffect?: string,
    syncPoints?: any[]
  }): Promise<string> {
    // 這裡假設TTS音頻已由後端生成，前端直接獲取URL
    // 實際使用時根據項目需求調整
    const ttsUrl = options?.syncPoints?.ttsUrl || `api/tts/${encodeURIComponent(text)}`;
    
    // 創建播放請求
    const request: PlayRequest = {
      track: 'voice',
      type: 'tts',
      source: ttsUrl,
      priority: options?.priority || 80, // 語音通常高優先級
      player: 'tts',
      options: {
        syncPoints: options?.syncPoints
      }
    };
    
    // 應用語音效果
    if (options?.voiceEffect) {
      this.voiceEffectsProcessor.applyPreset(options.voiceEffect);
    }
    
    // 交由通用播放邏輯處理
    return await this.play(request);
  }
  
  // 語音效果相關方法
  applyVoiceEffect(preset: string): void {
    this.voiceEffectsProcessor.applyPreset(preset);
  }
  
  setVoiceEffectParameter(effectName: string, param: string, value: any): void {
    this.voiceEffectsProcessor.setEffectParameter(effectName, param, value);
  }
  
  resetVoiceEffects(): void {
    this.voiceEffectsProcessor.resetEffects();
  }
  
  previewVoiceEffect(): void {
    // 使用測試語音片段預覽效果
    this.playTTS('這是一段測試語音，用於預覽效果', {
      priority: 90,
      voiceEffect: 'current' // 使用當前效果
    });
  }
  
  // 其他代碼...
}
```

## 表情與語音同步

為了實現角色表情與語音的同步，我們需要在TTS系統中生成帶有時間標記的同步點，並在前端播放時觸發對應的表情變化。

### 同步點數據格式

```typescript
interface SyncPoint {
  time: number;       // 相對於音頻開始的時間（秒）
  marker: string;     // 標記類型（如"mouth_open", "mouth_close", "eye_blink"等）
  value?: number;     // 可選參數，如嘴巴開合度
  duration?: number;  // 可選參數，表示該狀態持續時間
}
```

### 後端準備

後端在生成TTS音頻時，需要同時生成同步點數據，例如：

```json
{
  "ttsUrl": "https://example.com/tts/12345.mp3",
  "text": "你好，世界！",
  "duration": 2.5,
  "syncPoints": [
    { "time": 0.1, "marker": "mouth_open", "value": 0.3 },
    { "time": 0.3, "marker": "mouth_close" },
    { "time": 0.5, "marker": "mouth_open", "value": 0.8 },
    { "time": 1.0, "marker": "mouth_close" },
    { "time": 1.2, "marker": "eye_blink" },
    { "time": 1.8, "marker": "mouth_open", "value": 0.5 },
    { "time": 2.3, "marker": "mouth_close" }
  ]
}
```

### 前端處理

前端需要監聽這些標記點事件，並觸發對應的表情動畫：

```typescript
// 在角色表情控制組件中
useEffect(() => {
  // 訂閱標記點事件
  const handleMarker = (data) => {
    switch (data.marker) {
      case 'mouth_open':
        characterRef.current.setMouthOpen(data.value || 0.5);
        break;
      case 'mouth_close':
        characterRef.current.setMouthOpen(0);
        break;
      case 'eye_blink':
        characterRef.current.triggerBlink();
        break;
      // 其他表情處理...
    }
  };
  
  audioCoordinator.on('voice:marker', handleMarker);
  
  return () => {
    audioCoordinator.off('voice:marker', handleMarker);
  };
}, [audioCoordinator]);
```

## 整合測試計劃

為確保VoiceEffectsPanel與TTS系統順利整合到AudioCoordinator架構中，需要進行以下測試：

1. **基本功能測試**
   - VoiceEffectsPanel界面渲染
   - 預設效果切換
   - 參數調整響應

2. **音效處理測試**
   - 不同預設效果音質驗證
   - 參數調整對聲音的影響
   - 效果加載和切換性能

3. **TTS播放測試**
   - 基本TTS播放功能
   - 語音效果應用到TTS
   - 播放狀態和事件觸發

4. **同步功能測試**
   - 表情標記點事件觸發
   - 表情與語音同步精確度
   - 長句子和複雜表情序列測試

5. **整合穩定性測試**
   - 連續切換效果時的穩定性
   - 多個TTS請求的處理
   - 與其他音效同時播放時的表現

## 實現路徑

建議按以下順序實現整合：

1. 實現VoiceEffectsProcessor核心功能
2. 實現TTSPlayer並與VoiceEffectsProcessor整合
3. 在AudioCoordinator中添加TTS和語音效果支持
4. 實現VoiceEffectsPanel UI組件
5. 添加表情同步支持
6. 進行整合測試和優化

## 結論

通過將VoiceEffectsPanel與TTS系統整合到AudioCoordinator架構中，我們能夠實現統一的語音效果管理和播放控制。這種整合使得角色語音具有更豐富的表現力，同時保持了系統的模組化和可維護性。

語音效果與表情同步的結合，將大大提升虛擬角色的真實感和互動性，為用戶提供更加生動的體驗。 