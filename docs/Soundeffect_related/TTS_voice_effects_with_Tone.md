# Tone.js TTS語音效果處理設計文檔

本文檔描述如何使用Tone.js為人工智能合成的TTS語音添加音效處理能力，包括音色調整、效果添加和實時控制等功能。

## 1. 概述

### 1.1 目標

- 使用Tone.js為TTS語音添加實時音效處理能力
- 支持多種預設音效組合（如機器人聲、空間感、廣播效果等）
- 與現有的`AudioCoordinator`和音效系統無縫集成
- 提供簡單的UI面板，用於調整和預覽音效
- 實現音效參數的實時調整

### 1.2 技術基礎

Tone.js是一個基於Web Audio API的高級框架，提供了豐富的音頻處理能力，包括效果器、合成器和調度功能。我們將利用Tone.js的以下特性：

- **效果器**：用於處理TTS語音
- **音頻節點連接**：創建音頻處理鏈
- **參數控制**：實時調整效果參數
- **預設效果組合**：創建可重用的效果鏈

## 2. 系統架構

### 2.1 整體架構

```
                   ┌─────────────────┐
                   │                 │
TTS Audio Stream ──┤  Voice Effects  ├── Output
                   │  Processor      │
                   │  (Tone.js)      │
                   └─────────────────┘
                          │
                          │ Controls
                          ▼
                   ┌─────────────────┐
                   │  Voice Effects  │
                   │  UI Panel       │
                   └─────────────────┘
```

### 2.2 核心組件

1. **VoiceEffectsProcessor**：基於Tone.js的核心處理服務
2. **VoiceEffectsPanel**：用於控制和預覽效果的UI組件
3. **預設效果配置**：定義常用的效果組合
4. **AudioCoordinator集成**：將音效處理納入統一的音頻時間軸管理

## 3. 技術實現

### 3.1 VoiceEffectsProcessor服務設計

```typescript
// src/services/VoiceEffectsProcessor.ts

import * as Tone from 'tone';

export interface EffectPreset {
  id: string;
  name: string;
  description: string;
  effects: EffectConfig[];
}

export interface EffectConfig {
  type: string;
  params: Record<string, any>;
  enabled: boolean;
}

export class VoiceEffectsProcessor {
  private player: Tone.Player | null = null;
  private effects: Map<string, Tone.Effect> = new Map();
  private effectChain: Tone.Effect[] = [];
  private outputNode: Tone.Gain;
  private isReady: boolean = false;
  private currentPreset: string | null = null;

  constructor() {
    this.outputNode = new Tone.Gain(1).toDestination();
    Tone.start(); // 需要用戶交互
  }

  // 初始化播放器和效果器
  async initialize(): Promise<void> {
    try {
      this.player = new Tone.Player().connect(this.outputNode);
      
      // 創建常用效果器
      this.effects.set('reverb', new Tone.Reverb(1.5));
      this.effects.set('delay', new Tone.FeedbackDelay('8n', 0.5));
      this.effects.set('distortion', new Tone.Distortion(0.8));
      this.effects.set('pitchShift', new Tone.PitchShift(0));
      this.effects.set('chorus', new Tone.Chorus(4, 2.5, 0.5));
      this.effects.set('filter', new Tone.Filter(1000, 'lowpass'));
      this.effects.set('eq3', new Tone.EQ3(0, 0, 0));
      this.effects.set('compressor', new Tone.Compressor(-30, 3));
      
      // 默認情況下不連接任何效果
      this.resetEffects();
      
      this.isReady = true;
      return Promise.resolve();
    } catch (error) {
      console.error('初始化VoiceEffectsProcessor失敗:', error);
      return Promise.reject(error);
    }
  }

  // 載入TTS音頻
  async loadTTSAudio(audioUrl: string): Promise<void> {
    if (!this.player || !this.isReady) {
      await this.initialize();
    }
    
    try {
      if (this.player) {
        await this.player.load(audioUrl);
        return Promise.resolve();
      }
      return Promise.reject('播放器未初始化');
    } catch (error) {
      console.error('載入TTS音頻失敗:', error);
      return Promise.reject(error);
    }
  }

  // 直接播放已加載的TTS音頻
  playTTS(): void {
    if (this.player && this.isReady) {
      this.player.start();
    } else {
      console.warn('播放器未準備就緒');
    }
  }

  // 停止播放
  stopTTS(): void {
    if (this.player) {
      this.player.stop();
    }
  }

  // 應用預設效果組合
  applyPreset(presetId: string): boolean {
    const preset = EFFECT_PRESETS.find(p => p.id === presetId);
    if (!preset) return false;
    
    this.resetEffects();
    
    preset.effects.forEach(effectConfig => {
      const effect = this.effects.get(effectConfig.type);
      if (effect && effectConfig.enabled) {
        // 設置效果參數
        Object.entries(effectConfig.params).forEach(([param, value]) => {
          if (param in effect) {
            (effect as any)[param].value = value;
          }
        });
        
        // 添加到效果鏈
        this.effectChain.push(effect);
      }
    });
    
    // 重新連接效果鏈
    this.connectEffectChain();
    this.currentPreset = presetId;
    return true;
  }

  // 清除所有效果
  resetEffects(): void {
    // 斷開當前連接的效果鏈
    if (this.player) {
      this.player.disconnect();
      this.player.connect(this.outputNode);
    }
    
    // 重置效果參數
    this.effects.forEach(effect => {
      effect.disconnect();
    });
    
    this.effectChain = [];
    this.currentPreset = null;
  }

  // 連接效果鏈
  private connectEffectChain(): void {
    if (!this.player || this.effectChain.length === 0) return;
    
    this.player.disconnect();
    
    // 依次連接效果
    if (this.effectChain.length === 1) {
      this.player.chain(this.effectChain[0], this.outputNode);
    } else {
      // 多個效果依次連接
      this.player.connect(this.effectChain[0]);
      for (let i = 0; i < this.effectChain.length - 1; i++) {
        this.effectChain[i].connect(this.effectChain[i + 1]);
      }
      this.effectChain[this.effectChain.length - 1].connect(this.outputNode);
    }
  }

  // 調整特定效果參數
  setEffectParameter(effectType: string, paramName: string, value: number): boolean {
    const effect = this.effects.get(effectType);
    if (!effect || !(paramName in effect)) return false;
    
    try {
      (effect as any)[paramName].value = value;
      return true;
    } catch (error) {
      console.error(`設置效果參數失敗: ${effectType}.${paramName}:`, error);
      return false;
    }
  }

  // 獲取當前應用的預設
  getCurrentPreset(): string | null {
    return this.currentPreset;
  }

  // 獲取預設列表
  getPresets(): EffectPreset[] {
    return EFFECT_PRESETS;
  }

  // 設置主輸出音量
  setOutputVolume(volume: number): void {
    if (this.outputNode) {
      this.outputNode.gain.value = Math.max(0, Math.min(1, volume));
    }
  }
}

// 預設效果組合
export const EFFECT_PRESETS: EffectPreset[] = [
  {
    id: 'robot',
    name: '機器人聲',
    description: '模擬機器人般的機械聲音',
    effects: [
      { type: 'pitchShift', params: { pitch: -12 }, enabled: true },
      { type: 'distortion', params: { distortion: 0.4 }, enabled: true },
      { type: 'filter', params: { frequency: 2000, Q: 1 }, enabled: true }
    ]
  },
  {
    id: 'space',
    name: '太空感',
    description: '模擬太空艙內通訊效果',
    effects: [
      { type: 'reverb', params: { decay: 5, wet: 0.6 }, enabled: true },
      { type: 'filter', params: { frequency: 4000, type: 'lowpass' }, enabled: true },
      { type: 'delay', params: { delayTime: 0.2, feedback: 0.2 }, enabled: true }
    ]
  },
  {
    id: 'radio',
    name: '廣播效果',
    description: '模擬老式廣播的效果',
    effects: [
      { type: 'filter', params: { frequency: 2500, type: 'bandpass', Q: 1 }, enabled: true },
      { type: 'distortion', params: { distortion: 0.2 }, enabled: true },
      { type: 'eq3', params: { low: -10, mid: 2, high: -8 }, enabled: true }
    ]
  },
  {
    id: 'underwater',
    name: '水下效果',
    description: '模擬水下說話的效果',
    effects: [
      { type: 'filter', params: { frequency: 700, type: 'lowpass', Q: 1.5 }, enabled: true },
      { type: 'reverb', params: { decay: 3, wet: 0.7 }, enabled: true },
      { type: 'chorus', params: { frequency: 0.5, depth: 0.9 }, enabled: true }
    ]
  },
  {
    id: 'phone',
    name: '電話效果',
    description: '模擬電話通話效果',
    effects: [
      { type: 'filter', params: { frequency: 2000, type: 'bandpass', Q: 1 }, enabled: true },
      { type: 'compressor', params: { threshold: -20, ratio: 6 }, enabled: true },
      { type: 'eq3', params: { low: -15, mid: 5, high: -10 }, enabled: true }
    ]
  }
];

// 單例導出
export default new VoiceEffectsProcessor();
```

### 3.2 使用Hook封裝語音效果處理器

```typescript
// src/hooks/useVoiceEffects.ts

import { useState, useEffect, useCallback } from 'react';
import voiceEffectsProcessor, { EffectPreset } from '../services/VoiceEffectsProcessor';

interface UseVoiceEffectsReturn {
  isReady: boolean;
  presets: EffectPreset[];
  currentPreset: string | null;
  isPlaying: boolean;
  applyPreset: (presetId: string) => boolean;
  resetEffects: () => void;
  setEffectParameter: (effectType: string, paramName: string, value: number) => boolean;
  loadAndPlayTTS: (url: string) => Promise<void>;
  stopTTS: () => void;
  setVolume: (volume: number) => void;
}

export function useVoiceEffects(): UseVoiceEffectsReturn {
  const [isReady, setIsReady] = useState<boolean>(false);
  const [presets, setPresets] = useState<EffectPreset[]>([]);
  const [currentPreset, setCurrentPreset] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  useEffect(() => {
    const initProcessor = async () => {
      try {
        await voiceEffectsProcessor.initialize();
        setPresets(voiceEffectsProcessor.getPresets());
        setIsReady(true);
      } catch (error) {
        console.error('初始化語音效果處理器失敗:', error);
      }
    };

    initProcessor();
  }, []);

  const applyPreset = useCallback((presetId: string): boolean => {
    const success = voiceEffectsProcessor.applyPreset(presetId);
    if (success) {
      setCurrentPreset(presetId);
    }
    return success;
  }, []);

  const resetEffects = useCallback(() => {
    voiceEffectsProcessor.resetEffects();
    setCurrentPreset(null);
  }, []);

  const setEffectParameter = useCallback(
    (effectType: string, paramName: string, value: number): boolean => {
      return voiceEffectsProcessor.setEffectParameter(effectType, paramName, value);
    },
    []
  );

  const loadAndPlayTTS = useCallback(async (url: string): Promise<void> => {
    try {
      await voiceEffectsProcessor.loadTTSAudio(url);
      voiceEffectsProcessor.playTTS();
      setIsPlaying(true);
      
      // 監聽播放結束
      const player = (voiceEffectsProcessor as any).player;
      if (player) {
        player.onstop = () => {
          setIsPlaying(false);
        };
      }
    } catch (error) {
      console.error('加載並播放TTS失敗:', error);
      setIsPlaying(false);
    }
  }, []);

  const stopTTS = useCallback(() => {
    voiceEffectsProcessor.stopTTS();
    setIsPlaying(false);
  }, []);

  const setVolume = useCallback((volume: number) => {
    voiceEffectsProcessor.setOutputVolume(volume);
  }, []);

  return {
    isReady,
    presets,
    currentPreset,
    isPlaying,
    applyPreset,
    resetEffects,
    setEffectParameter,
    loadAndPlayTTS,
    stopTTS,
    setVolume,
  };
}
```

### 3.3 Voice Effects UI面板設計

```typescript
// src/components/VoiceEffectsPanel.tsx

import React, { useState, useEffect } from 'react';
import { useVoiceEffects } from '../hooks/useVoiceEffects';
import styles from './VoiceEffectsPanel.module.css';

interface VoiceEffectsPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

const VoiceEffectsPanel: React.FC<VoiceEffectsPanelProps> = ({ isVisible, onClose }) => {
  const {
    isReady,
    presets,
    currentPreset,
    isPlaying,
    applyPreset,
    resetEffects,
    setEffectParameter,
    loadAndPlayTTS,
    stopTTS,
    setVolume
  } = useVoiceEffects();

  const [volume, setVolumeState] = useState<number>(1);
  const [testAudioUrl, setTestAudioUrl] = useState<string>('/audio/voice/test_sample.mp3');
  const [activeTab, setActiveTab] = useState<'presets' | 'custom'>('presets');

  // 效果參數調整狀態
  const [effectParams, setEffectParams] = useState({
    reverb: { decay: 1.5, wet: 0.5 },
    pitchShift: { pitch: 0 },
    filter: { frequency: 1000, Q: 1 },
    distortion: { distortion: 0.4 }
  });

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolumeState(newVolume);
    setVolume(newVolume);
  };

  const handlePlayTest = async () => {
    if (isPlaying) {
      stopTTS();
    } else {
      await loadAndPlayTTS(testAudioUrl);
    }
  };

  const handleParameterChange = (
    effectType: string,
    paramName: string,
    value: number
  ) => {
    setEffectParams(prev => ({
      ...prev,
      [effectType]: {
        ...prev[effectType as keyof typeof prev],
        [paramName]: value
      }
    }));
    setEffectParameter(effectType, paramName, value);
  };

  if (!isVisible) return null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2>語音效果控制</h2>
        <button onClick={onClose} className={styles.closeButton}>
          ✕
        </button>
      </div>

      <div className={styles.statusBar}>
        <span
          className={`${styles.statusDot} ${
            isReady ? styles.statusReady : styles.statusNotReady
          }`}
        ></span>
        <span>{isReady ? '系統已就緒' : '正在初始化...'}</span>
      </div>

      <div className={styles.tabs}>
        <button
          className={`${styles.tabButton} ${
            activeTab === 'presets' ? styles.activeTab : ''
          }`}
          onClick={() => setActiveTab('presets')}
        >
          預設效果
        </button>
        <button
          className={`${styles.tabButton} ${
            activeTab === 'custom' ? styles.activeTab : ''
          }`}
          onClick={() => setActiveTab('custom')}
        >
          自訂效果
        </button>
      </div>

      <div className={styles.content}>
        {activeTab === 'presets' && (
          <div className={styles.presetList}>
            <div className={styles.presetItem}>
              <button
                className={`${styles.presetButton} ${
                  currentPreset === null ? styles.activePreset : ''
                }`}
                onClick={resetEffects}
              >
                原聲
              </button>
              <span className={styles.presetDescription}>
                不套用任何效果
              </span>
            </div>
            {presets.map(preset => (
              <div key={preset.id} className={styles.presetItem}>
                <button
                  className={`${styles.presetButton} ${
                    currentPreset === preset.id ? styles.activePreset : ''
                  }`}
                  onClick={() => applyPreset(preset.id)}
                  disabled={!isReady}
                >
                  {preset.name}
                </button>
                <span className={styles.presetDescription}>
                  {preset.description}
                </span>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'custom' && (
          <div className={styles.customControls}>
            <div className={styles.effectControl}>
              <h3>混響</h3>
              <div className={styles.paramControl}>
                <label>衰減時間:</label>
                <input
                  type="range"
                  min="0.1"
                  max="10"
                  step="0.1"
                  value={effectParams.reverb.decay}
                  onChange={e =>
                    handleParameterChange(
                      'reverb',
                      'decay',
                      parseFloat(e.target.value)
                    )
                  }
                />
                <span>{effectParams.reverb.decay}s</span>
              </div>
              <div className={styles.paramControl}>
                <label>混合比例:</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={effectParams.reverb.wet}
                  onChange={e =>
                    handleParameterChange(
                      'reverb',
                      'wet',
                      parseFloat(e.target.value)
                    )
                  }
                />
                <span>{Math.round(effectParams.reverb.wet * 100)}%</span>
              </div>
            </div>

            <div className={styles.effectControl}>
              <h3>音高調整</h3>
              <div className={styles.paramControl}>
                <label>音高偏移:</label>
                <input
                  type="range"
                  min="-24"
                  max="24"
                  step="1"
                  value={effectParams.pitchShift.pitch}
                  onChange={e =>
                    handleParameterChange(
                      'pitchShift',
                      'pitch',
                      parseFloat(e.target.value)
                    )
                  }
                />
                <span>{effectParams.pitchShift.pitch} 半音</span>
              </div>
            </div>

            <div className={styles.effectControl}>
              <h3>濾波器</h3>
              <div className={styles.paramControl}>
                <label>頻率:</label>
                <input
                  type="range"
                  min="50"
                  max="10000"
                  step="10"
                  value={effectParams.filter.frequency}
                  onChange={e =>
                    handleParameterChange(
                      'filter',
                      'frequency',
                      parseFloat(e.target.value)
                    )
                  }
                />
                <span>{effectParams.filter.frequency} Hz</span>
              </div>
            </div>

            <div className={styles.effectControl}>
              <h3>失真</h3>
              <div className={styles.paramControl}>
                <label>失真度:</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={effectParams.distortion.distortion}
                  onChange={e =>
                    handleParameterChange(
                      'distortion',
                      'distortion',
                      parseFloat(e.target.value)
                    )
                  }
                />
                <span>{Math.round(effectParams.distortion.distortion * 100)}%</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className={styles.controls}>
        <div className={styles.volumeControl}>
          <label>主音量:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={handleVolumeChange}
          />
          <span>{Math.round(volume * 100)}%</span>
        </div>

        <div className={styles.testSection}>
          <h3>測試音頻</h3>
          <div className={styles.testAudio}>
            <input
              type="text"
              value={testAudioUrl}
              onChange={e => setTestAudioUrl(e.target.value)}
              placeholder="輸入TTS音頻URL測試效果"
              className={styles.audioUrlInput}
            />
            <button
              onClick={handlePlayTest}
              className={`${styles.playButton} ${
                isPlaying ? styles.stopButton : ''
              }`}
              disabled={!isReady}
            >
              {isPlaying ? '停止' : '播放測試'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceEffectsPanel;
```

### 3.4 AudioCoordinator集成

為了將語音效果處理整合到音頻時間軸，需要在AudioCoordinator中添加相關功能：

```typescript
// src/services/AudioCoordinator.ts (部分代碼)

import voiceEffectsProcessor from './VoiceEffectsProcessor';

// 添加到AudioEvent類型
interface AudioEvent {
  // 現有字段...
  voiceEffect?: {
    preset?: string;
    parameters?: Record<string, Record<string, number>>;
  };
}

// AudioCoordinator類中添加的方法
triggerEvent(event: AudioEvent): void {
  // 現有代碼...
  
  // 處理語音效果
  if (event.type === 'tts' && event.track === 'voice' && event.voiceEffect) {
    // 應用預設效果
    if (event.voiceEffect.preset) {
      voiceEffectsProcessor.applyPreset(event.voiceEffect.preset);
    } 
    // 應用自定義參數
    else if (event.voiceEffect.parameters) {
      voiceEffectsProcessor.resetEffects();
      Object.entries(event.voiceEffect.parameters).forEach(([effectType, params]) => {
        Object.entries(params).forEach(([paramName, value]) => {
          voiceEffectsProcessor.setEffectParameter(effectType, paramName, value);
        });
      });
    }
    
    // 將TTS音頻URL傳給效果處理器
    if (event.url) {
      voiceEffectsProcessor.loadTTSAudio(event.url)
        .then(() => voiceEffectsProcessor.playTTS())
        .catch(error => console.error('TTS效果處理失敗:', error));
    }
  }
  
  // 繼續現有邏輯...
}
```

## 4. 實現步驟

### 4.1 基礎結構實現

1. 創建`VoiceEffectsProcessor`服務
2. 實現基礎的效果器加載和連接邏輯
3. 定義預設效果組合配置

### 4.2 用戶界面開發

1. 實現`useVoiceEffects` Hook來封裝服務
2. 開發`VoiceEffectsPanel`組件用於控制和預覽
3. 設計和實現CSS樣式

### 4.3 AudioCoordinator整合

1. 擴展`AudioEvent`接口以支持語音效果參數
2. 在`AudioCoordinator`中添加處理語音效果的邏輯
3. 測試並優化系統性能

### 4.4 TTS系統整合

1. 修改現有的TTS處理流程以支持效果處理
2. 實現後端配置與前端交互機制
3. 優化音頻流程以減少延遲

## 5. 可擴展性和未來方向

### 5.1 效果庫擴展

- 添加更多預設效果組合
- 支持用戶創建和保存自定義效果組合
- 實現效果參數的自動化處理（隨時間變化）

### 5.2 頻譜分析和可視化

- 添加實時頻譜分析功能
- 提供波形和頻譜可視化
- 支持參數與音頻特性的實時映射

### 5.3 AI輔助效果選擇

- 基於文本內容自動選擇合適的效果
- 支持情感分析驅動的效果變化
- 實現上下文感知的音效處理

## 6. 性能考慮

- 使用Web Audio API的工作線程進行音頻處理以避免主線程阻塞
- 實現效果器的延遲加載策略
- 添加音頻緩衝和預處理機制
- 監控CPU使用率並實現自動降級策略

## 7. 總結

本設計提供了一個完整的方案，使用Tone.js為TTS語音添加豐富的音效處理能力。通過這些工具，可以實現機器人聲、太空感、電話效果等多種聲音變化，增強用戶體驗。該方案與現有的AudioCoordinator無縫集成，支持實時調整和預覽，可作為音效系統重構的重要組成部分。 