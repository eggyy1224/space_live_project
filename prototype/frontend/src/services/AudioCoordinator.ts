/**
 * AudioCoordinator - 音頻協調器
 * 提供統一的聲音播放介面，協調不同音頻類型與通道間的關係
 */

import mitt, { Emitter } from 'mitt';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

// 音頻類型定義
export type AudioKind = 'song' | 'sfx' | 'synth' | 'voice';

// 音頻事件定義
export interface AudioEvent {
  id: string;
  kind: AudioKind;
  url: string;
  volume?: number;
  loop?: boolean;
  meta?: Record<string, any>;
  animationCues?: Array<{
    time: number;
    type: string;
    value: string;
  }>;
}

// 時間軸事件定義
export interface AudioTimelineEvent extends AudioEvent {
  track: 'voice' | 'sfx';
  startTime: number;
  duration?: number;
}

// 完整時間軸定義
export interface AudioTimeline {
  timeline: AudioTimelineEvent[];
}

// 事件類型定義
export type AudioCoordinatorEventType = 
  | 'play_start' 
  | 'play_end' 
  | 'voice:start' 
  | 'voice:end' 
  | 'music:start' 
  | 'music:end' 
  | 'sfx:start' 
  | 'sfx:end' 
  | 'ducking_on' 
  | 'ducking_off' 
  | 'timeline_start' 
  | 'timeline_end';

// 事件監聽器類型
type AudioCoordinatorEventListener = (event: any) => void;

// 聲音效果類型
interface SoundEffect {
  id: string;
  name: string;
  path: string;
  category: string;
  volume: number;
  loop: boolean;
}

// 語音效果類型
interface VoiceEffect {
  id: string;
  name: string;
  parameters: {
    pitch?: number;
    rate?: number;
    volume?: number;
    // 其他語音處理參數
  };
}

// TTS 配置類型
interface TTSConfig {
  enabled: boolean;
  voice: string;
  pitch: number;
  rate: number;
  volume: number;
}

// 音頻協調器狀態
interface AudioCoordinatorState {
  // 聲音效果管理
  soundEffects: Record<string, SoundEffect>;
  currentSoundEffect: string | null;
  soundVolume: number;
  
  // 語音效果管理
  voiceEffects: Record<string, VoiceEffect>;
  currentVoiceEffect: string | null;
  voiceVolume: number;
  
  // TTS 配置
  ttsConfig: TTSConfig;
  
  // 播放實例管理
  activeSounds: Record<string, HTMLAudioElement>;
  
  // 方法
  setSoundVolume: (volume: number) => void;
  setVoiceVolume: (volume: number) => void;
  updateTTSConfig: (config: Partial<TTSConfig>) => void;
  
  // 聲音效果方法
  addSoundEffect: (effect: SoundEffect) => void;
  removeSoundEffect: (id: string) => void;
  playSoundEffect: (id: string) => void;
  stopSoundEffect: (id: string) => void;
  stopAllSoundEffects: () => void;
  
  // 語音效果方法
  addVoiceEffect: (effect: VoiceEffect) => void;
  removeVoiceEffect: (id: string) => void;
  selectVoiceEffect: (id: string | null) => void;
  
  // TTS 方法
  speakText: (text: string) => void;
  cancelSpeech: () => void;
}

/**
 * AudioCoordinator 介面 - 提供給組件使用
 */
export interface IAudioCoordinator {
  playNow: (event: AudioEvent) => void;
  stop: (id?: string) => void;
  scheduleFromJson: (timeline: AudioTimeline) => void;
  stopTimeline: () => void;
  setGlobalVolume: (volume: number) => void;
  addEventListener: (type: AudioCoordinatorEventType, listener: AudioCoordinatorEventListener) => () => void;
  removeEventListener: (type: AudioCoordinatorEventType, listener: AudioCoordinatorEventListener) => void;
}

/**
 * AudioCoordinator 類別 - 聲音協調控制中心
 */
class AudioCoordinator implements IAudioCoordinator {
  private static instance: AudioCoordinator;
  private eventBus: Emitter<Record<string, any>>;
  private activeAudioSources: Map<string, HTMLAudioElement | null> = new Map();
  private currentTimelineEvents: AudioTimelineEvent[] = [];
  private timelineTimeouts: number[] = [];
  private isTimelinePlaying: boolean = false;
  
  // 音頻通道增益節點 (暫存，後續將使用 Web Audio API)
  private voiceVolume: number = 1.0;
  private musicVolume: number = 1.0;
  private sfxVolume: number = 1.0;

  /**
   * 私有構造函數 (單例模式)
   */
  private constructor() {
    this.eventBus = mitt();
    logger.info('[AudioCoordinator] Initialized', LogCategory.AUDIO);
  }

  /**
   * 獲取單例實例
   */
  public static getInstance(): AudioCoordinator {
    if (!AudioCoordinator.instance) {
      AudioCoordinator.instance = new AudioCoordinator();
    }
    return AudioCoordinator.instance;
  }

  /**
   * 立即播放音頻事件
   * @param event 音頻事件
   */
  public playNow(event: AudioEvent): void {
    logger.debug(`[AudioCoordinator] playNow: ${event.kind} - ${event.id}`, LogCategory.AUDIO);
    
    // 檢查如果是 voice 類型，需確保獨占播放
    if (event.kind === 'voice') {
      this.stopAllVoice(); // 停止所有當前的 voice 事件
    }
    
    // 暫時實現：直接創建 Audio 元素播放
    // 後續將替換為使用 Web Audio API 和已有的 AudioPlayerService/SoundEffectService
    const audio = new Audio(event.url);
    this.activeAudioSources.set(event.id, audio);
    
    // 設置基本參數
    if (event.volume !== undefined) {
      audio.volume = event.volume;
    }
    
    if (event.loop) {
      audio.loop = true;
    }
    
    // 根據類型應用不同音量設置
    this.applyVolumeForKind(audio, event.kind);
    
    // 事件監聽
    audio.addEventListener('play', () => {
      logger.debug(`[AudioCoordinator] ${event.kind} started: ${event.id}`, LogCategory.AUDIO);
      this.eventBus.emit(`${event.kind}:start`, { id: event.id });
      
      // 如果是語音類型，啟動 ducking 效果
      if (event.kind === 'voice') {
        this.applyDucking(true);
        
        // 設置全局的 speaking 狀態
        useStore.getState().setSpeaking(true);
        
        // 如果有動畫提示，將在這裡處理
        if (event.animationCues && event.animationCues.length > 0) {
          // 未來實現: 將 animationCues 傳遞給動畫系統
          logger.debug(`[AudioCoordinator] Voice has ${event.animationCues.length} animation cues`, LogCategory.AUDIO);
        }
      }
    });
    
    audio.addEventListener('ended', () => {
      logger.debug(`[AudioCoordinator] ${event.kind} ended: ${event.id}`, LogCategory.AUDIO);
      this.eventBus.emit(`${event.kind}:end`, { id: event.id });
      
      // 如果是語音類型，關閉 ducking 效果
      if (event.kind === 'voice') {
        this.applyDucking(false);
        
        // 重置全局的 speaking 狀態
        useStore.getState().setSpeaking(false);
      }
      
      // 清理資源
      this.activeAudioSources.delete(event.id);
    });
    
    // 開始播放
    audio.play().catch(err => {
      logger.error(`[AudioCoordinator] Error playing ${event.id}:`, LogCategory.AUDIO, err);
      this.activeAudioSources.delete(event.id);
    });
  }

  /**
   * 停止特定 ID 的音頻
   * @param id 音頻ID，不提供則停止所有音頻
   */
  public stop(id?: string): void {
    if (id) {
      const audio = this.activeAudioSources.get(id);
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
        this.activeAudioSources.delete(id);
        logger.debug(`[AudioCoordinator] Stopped: ${id}`, LogCategory.AUDIO);
      }
    } else {
      // 停止所有音頻
      this.activeAudioSources.forEach((audio, id) => {
        if (audio) {
          audio.pause();
          audio.currentTime = 0;
        }
      });
      this.activeAudioSources.clear();
      logger.debug(`[AudioCoordinator] Stopped all audio`, LogCategory.AUDIO);
      
      // 確保全局狀態更新
      useStore.getState().setSpeaking(false);
      this.applyDucking(false);
    }
  }

  /**
   * 停止所有語音類型音頻
   */
  private stopAllVoice(): void {
    this.activeAudioSources.forEach((audio, id) => {
      if (id.startsWith('voice_') && audio) {
        audio.pause();
        audio.currentTime = 0;
        this.activeAudioSources.delete(id);
      }
    });
    
    // 確保全局狀態更新
    useStore.getState().setSpeaking(false);
  }

  /**
   * 從 JSON 排程音頻時間軸
   * @param timeline 時間軸 JSON
   */
  public scheduleFromJson(timeline: AudioTimeline): void {
    logger.info(`[AudioCoordinator] Scheduling timeline with ${timeline.timeline.length} events`, LogCategory.AUDIO);
    
    // 先停止已有的時間軸
    this.stopTimeline();
    
    // 保存新的時間軸事件
    this.currentTimelineEvents = [...timeline.timeline];
    this.isTimelinePlaying = true;
    
    // 按開始時間排序
    this.currentTimelineEvents.sort((a, b) => a.startTime - b.startTime);
    
    // 發出時間軸開始事件
    this.eventBus.emit('timeline_start', { 
      totalEvents: this.currentTimelineEvents.length 
    });
    
    // 為每個事件設置定時器
    this.currentTimelineEvents.forEach(event => {
      const timeoutId = window.setTimeout(() => {
        // 如果時間軸仍在播放中才執行
        if (this.isTimelinePlaying) {
          this.playNow({
            id: event.id,
            kind: event.kind,
            url: event.url,
            volume: event.volume,
            loop: event.loop,
            meta: event.meta,
            animationCues: event.animationCues
          });
        }
      }, event.startTime * 1000); // 轉換為毫秒
      
      this.timelineTimeouts.push(timeoutId);
    });
    
    // 設置時間軸結束事件
    if (this.currentTimelineEvents.length > 0) {
      const lastEvent = this.currentTimelineEvents[this.currentTimelineEvents.length - 1];
      const endTime = lastEvent.startTime + (lastEvent.duration || 0);
      
      const timelineEndTimeout = window.setTimeout(() => {
        if (this.isTimelinePlaying) {
          this.eventBus.emit('timeline_end', {});
          this.isTimelinePlaying = false;
        }
      }, endTime * 1000 + 100); // 加一點緩衝時間
      
      this.timelineTimeouts.push(timelineEndTimeout);
    }
  }
  
  /**
   * 停止當前時間軸播放
   */
  public stopTimeline(): void {
    if (!this.isTimelinePlaying) return;
    
    // 清除所有定時器
    this.timelineTimeouts.forEach(id => clearTimeout(id));
    this.timelineTimeouts = [];
    
    // 停止所有當前播放的聲音
    this.stop();
    
    this.isTimelinePlaying = false;
    this.currentTimelineEvents = [];
    
    logger.debug(`[AudioCoordinator] Timeline stopped`, LogCategory.AUDIO);
  }

  /**
   * 設置全局音量
   * @param volume 音量值 (0-1)
   */
  public setGlobalVolume(volume: number): void {
    // 將在以後使用 Web Audio API 實現
    // 暫時只更新當前播放的音頻元素
    this.activeAudioSources.forEach(audio => {
      if (audio) {
        audio.volume = volume;
      }
    });
    
    logger.debug(`[AudioCoordinator] Global volume set to ${volume}`, LogCategory.AUDIO);
  }

  /**
   * 根據音頻類型應用相應的音量設置
   * @param audio 音頻元素
   * @param kind 音頻類型
   */
  private applyVolumeForKind(audio: HTMLAudioElement, kind: AudioKind): void {
    switch (kind) {
      case 'voice':
        audio.volume *= this.voiceVolume;
        break;
      case 'song':
        audio.volume *= this.musicVolume;
        break;
      case 'sfx':
      case 'synth':
        audio.volume *= this.sfxVolume;
        break;
    }
  }

  /**
   * 應用音頻降低效果 (ducking)
   * @param isDucking 是否啟用 ducking
   */
  private applyDucking(isDucking: boolean): void {
    if (isDucking) {
      // 降低非語音音量
      this.activeAudioSources.forEach((audio, id) => {
        if (audio && !id.startsWith('voice_')) {
          // 記錄原始音量
          const originalVolume = audio.volume;
          audio._originalVolume = originalVolume;
          // 降低音量 (降至原來的 30%)
          audio.volume = originalVolume * 0.3;
        }
      });
      
      logger.debug(`[AudioCoordinator] Ducking enabled`, LogCategory.AUDIO);
      this.eventBus.emit('ducking_on', {});
    } else {
      // 恢復原始音量
      this.activeAudioSources.forEach((audio, id) => {
        if (audio && !id.startsWith('voice_') && audio._originalVolume !== undefined) {
          audio.volume = audio._originalVolume;
          delete audio._originalVolume;
        }
      });
      
      logger.debug(`[AudioCoordinator] Ducking disabled`, LogCategory.AUDIO);
      this.eventBus.emit('ducking_off', {});
    }
  }

  /**
   * 添加事件監聽器
   * @param type 事件類型
   * @param listener 監聽器回調
   * @returns 用於移除監聽器的函數
   */
  public addEventListener(type: AudioCoordinatorEventType, listener: AudioCoordinatorEventListener): () => void {
    this.eventBus.on(type, listener);
    return () => this.eventBus.off(type, listener);
  }
  
  /**
   * 移除事件監聽器
   * @param type 事件類型
   * @param listener 監聽器回調
   */
  public removeEventListener(type: AudioCoordinatorEventType, listener: AudioCoordinatorEventListener): void {
    this.eventBus.off(type, listener);
  }
}

// 聲明類型擴展
declare global {
  interface HTMLAudioElement {
    _originalVolume?: number;
  }
}

// 創建音頻協調器 store
const useAudioCoordinatorStore = create<AudioCoordinatorState>()(
  persist(
    (set, get) => ({
      // 初始狀態
      soundEffects: {},
      currentSoundEffect: null,
      soundVolume: 0.5,
      
      voiceEffects: {},
      currentVoiceEffect: null,
      voiceVolume: 0.7,
      
      ttsConfig: {
        enabled: true,
        voice: 'default',
        pitch: 1.0,
        rate: 1.0,
        volume: 0.8
      },
      
      activeSounds: {},
      
      // 音量控制
      setSoundVolume: (volume) => set({ soundVolume: volume }),
      setVoiceVolume: (volume) => set({ voiceVolume: volume }),
      
      // TTS 配置更新
      updateTTSConfig: (config) => set((state) => ({
        ttsConfig: { ...state.ttsConfig, ...config }
      })),
      
      // 聲音效果方法
      addSoundEffect: (effect) => set((state) => ({
        soundEffects: { ...state.soundEffects, [effect.id]: effect }
      })),
      
      removeSoundEffect: (id) => set((state) => {
        const { [id]: removed, ...rest } = state.soundEffects;
        // 如果正在播放，停止播放
        if (state.activeSounds[id]) {
          state.activeSounds[id].pause();
          const { [id]: removedSound, ...restSounds } = state.activeSounds;
          return { soundEffects: rest, activeSounds: restSounds };
        }
        return { soundEffects: rest };
      }),
      
      playSoundEffect: (id) => {
        const state = get();
        const effect = state.soundEffects[id];
        
        if (!effect) return;
        
        // 停止當前效果如果已經在播放
        if (state.activeSounds[id]) {
          state.activeSounds[id].pause();
        }
        
        // 創建新的音頻元素
        const audio = new Audio(effect.path);
        audio.volume = effect.volume * state.soundVolume;
        audio.loop = effect.loop;
        
        // 播放並存儲引用
        audio.play().catch(console.error);
        
        set((state) => ({
          activeSounds: { ...state.activeSounds, [id]: audio },
          currentSoundEffect: id
        }));
        
        // 如果不是循環播放，播放完成後自動清理
        if (!effect.loop) {
          audio.onended = () => {
            set((state) => {
              const { [id]: ended, ...rest } = state.activeSounds;
              return { 
                activeSounds: rest,
                currentSoundEffect: state.currentSoundEffect === id ? null : state.currentSoundEffect
              };
            });
          };
        }
      },
      
      stopSoundEffect: (id) => {
        const state = get();
        if (state.activeSounds[id]) {
          state.activeSounds[id].pause();
          set((state) => {
            const { [id]: stopped, ...rest } = state.activeSounds;
            return { 
              activeSounds: rest,
              currentSoundEffect: state.currentSoundEffect === id ? null : state.currentSoundEffect
            };
          });
        }
      },
      
      stopAllSoundEffects: () => {
        const state = get();
        Object.values(state.activeSounds).forEach(audio => audio.pause());
        set({ activeSounds: {}, currentSoundEffect: null });
      },
      
      // 語音效果方法
      addVoiceEffect: (effect) => set((state) => ({
        voiceEffects: { ...state.voiceEffects, [effect.id]: effect }
      })),
      
      removeVoiceEffect: (id) => set((state) => {
        const { [id]: removed, ...rest } = state.voiceEffects;
        return { 
          voiceEffects: rest,
          currentVoiceEffect: state.currentVoiceEffect === id ? null : state.currentVoiceEffect
        };
      }),
      
      selectVoiceEffect: (id) => set({ currentVoiceEffect: id }),
      
      // TTS 方法
      speakText: (text) => {
        const state = get();
        if (!state.ttsConfig.enabled || !window.speechSynthesis) return;
        
        // 取消正在進行的朗讀
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.volume = state.ttsConfig.volume * state.voiceVolume;
        utterance.rate = state.ttsConfig.rate;
        utterance.pitch = state.ttsConfig.pitch;
        
        // 如果有選擇的語音
        if (state.ttsConfig.voice !== 'default') {
          const voices = window.speechSynthesis.getVoices();
          const selectedVoice = voices.find(voice => voice.name === state.ttsConfig.voice);
          if (selectedVoice) utterance.voice = selectedVoice;
        }
        
        // 應用當前選擇的語音效果
        if (state.currentVoiceEffect) {
          const effect = state.voiceEffects[state.currentVoiceEffect];
          if (effect) {
            if (effect.parameters.pitch) utterance.pitch = effect.parameters.pitch;
            if (effect.parameters.rate) utterance.rate = effect.parameters.rate;
            if (effect.parameters.volume) utterance.volume = effect.parameters.volume * state.voiceVolume;
          }
        }
        
        window.speechSynthesis.speak(utterance);
      },
      
      cancelSpeech: () => {
        if (window.speechSynthesis) {
          window.speechSynthesis.cancel();
        }
      }
    }),
    {
      name: 'audio-coordinator-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        soundEffects: state.soundEffects,
        voiceEffects: state.voiceEffects,
        soundVolume: state.soundVolume,
        voiceVolume: state.voiceVolume,
        ttsConfig: state.ttsConfig,
        currentVoiceEffect: state.currentVoiceEffect
      })
    }
  )
);

// React Hook 包裝器
export const useAudioCoordinator = () => useAudioCoordinatorStore();

// 默認導出
export default useAudioCoordinatorStore; 