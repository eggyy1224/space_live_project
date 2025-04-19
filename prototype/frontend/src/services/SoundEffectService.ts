import * as Tone from 'tone';
import logger, { LogCategory } from '../utils/LogManager';

/**
 * 音效服務單例 - 負責管理Tone.js音效播放邏輯
 */
class SoundEffectService {
  private static instance: SoundEffectService;
  private players: Record<string, Tone.Player>;
  private isReady: boolean;
  private isLoading: boolean;
  private globalVolume: Tone.Volume;
  private contextStarted: boolean;
  
  /**
   * 私有構造函數，初始化Tone.js相關資源
   */
  private constructor() {
    this.players = {};
    this.isReady = false;
    this.isLoading = false;
    this.contextStarted = false;
    
    // 創建全局音量控制
    this.globalVolume = new Tone.Volume(0).toDestination();
    logger.info('[SoundEffectService] Service initialized', LogCategory.AUDIO);
  }

  /**
   * 獲取單例實例
   */
  public static getInstance(): SoundEffectService {
    if (!SoundEffectService.instance) {
      SoundEffectService.instance = new SoundEffectService();
    }
    return SoundEffectService.instance;
  }

  /**
   * 解鎖AudioContext（需要在用戶互動後調用）
   */
  public async unlockAudioContext(): Promise<boolean> {
    if (this.contextStarted) {
      return true;
    }
    
    try {
      logger.info('[SoundEffectService] Starting Tone.js context...', LogCategory.AUDIO);
      await Tone.start();
      this.contextStarted = true;
      logger.info('[SoundEffectService] Tone.js context started successfully', LogCategory.AUDIO);
      return true;
    } catch (error) {
      logger.error('[SoundEffectService] Failed to start Tone.js context:', LogCategory.AUDIO, error);
      return false;
    }
  }

  /**
   * 加載音效資源
   * @param soundEffects 音效映射表 (name -> url)
   */
  public async loadSoundEffects(soundEffects: Record<string, string>): Promise<boolean> {
    if (this.isLoading) {
      logger.warn('[SoundEffectService] Sound effects already loading, ignoring request', LogCategory.AUDIO);
      return false;
    }
    
    this.isLoading = true;
    this.isReady = false;
    let loadSuccess = true;
    
    try {
      logger.info(`[SoundEffectService] Loading ${Object.keys(soundEffects).length} sound effects...`, LogCategory.AUDIO);
      
      // 創建加載所有音效的Promise陣列
      const loadPromises = Object.entries(soundEffects).map(async ([name, url]) => {
        try {
          // 如果已經存在相同名稱的播放器，先釋放資源
          if (this.players[name]) {
            this.players[name].dispose();
          }
          
          // 創建新的播放器實例
          const player = new Tone.Player({
            url,
            onload: () => logger.debug(`[SoundEffectService] Loaded sound: ${name}`, LogCategory.AUDIO),
            onerror: (e) => logger.error(`[SoundEffectService] Error loading sound ${name}:`, LogCategory.AUDIO, e)
          }).connect(this.globalVolume);
          
          // 添加到播放器字典
          this.players[name] = player;
          
          return true;
        } catch (error) {
          logger.error(`[SoundEffectService] Failed to load sound ${name}:`, LogCategory.AUDIO, error);
          return false;
        }
      });
      
      // 等待所有音效加載完成
      const results = await Promise.all(loadPromises);
      loadSuccess = results.every(Boolean);
      
      if (loadSuccess) {
        logger.info('[SoundEffectService] All sound effects loaded successfully', LogCategory.AUDIO);
      } else {
        logger.warn('[SoundEffectService] Some sound effects failed to load', LogCategory.AUDIO);
      }
    } catch (error) {
      logger.error('[SoundEffectService] Error in loadSoundEffects:', LogCategory.AUDIO, error);
      loadSuccess = false;
    } finally {
      this.isLoading = false;
      this.isReady = loadSuccess;
    }
    
    return loadSuccess;
  }

  /**
   * 播放單個音效
   * @param name 音效名稱
   * @param volume 可選的音量覆蓋（0-1）
   */
  public playSingleSoundEffect(name: string, volume?: number): boolean {
    if (!this.isReady) {
      logger.warn(`[SoundEffectService] Cannot play sound ${name}: Service not ready`, LogCategory.AUDIO);
      return false;
    }
    
    if (!this.players[name]) {
      logger.warn(`[SoundEffectService] Sound not found: ${name}`, LogCategory.AUDIO);
      return false;
    }
    
    try {
      const player = this.players[name];
      
      // 如果提供了特定音量，則使用它
      if (volume !== undefined) {
        const volumeDB = this.linearToDecibels(volume);
        player.volume.value = volumeDB;
      }
      
      // 確保從頭開始播放
      player.stop();
      player.start();
      
      logger.info(`[SoundEffectService] Playing sound: ${name}${volume !== undefined ? ` (volume: ${volume})` : ''}`, LogCategory.AUDIO);
      return true;
    } catch (error) {
      logger.error(`[SoundEffectService] Error playing sound ${name}:`, LogCategory.AUDIO, error);
      return false;
    }
  }

  /**
   * 使用Tone.js合成器動態產生音效
   * @param type 音效類型
   * @param options 音效參數
   */
  public playSynthSound(type: string, options: any = {}): boolean {
    try {
      // 確保音頻上下文已啟動
      if (!this.contextStarted) {
        logger.warn('[SoundEffectService] Cannot play synth sound: AudioContext not started', LogCategory.AUDIO);
        return false;
      }
      
      switch (type) {
        case 'beep': {
          // 簡單的嗶聲
          const synth = new Tone.Synth({
            oscillator: {
              type: options.wavetype || 'sine'
            },
            envelope: {
              attack: 0.005,
              decay: 0.1,
              sustain: 0.3,
              release: 0.2
            }
          }).connect(this.globalVolume);
          
          const frequency = options.frequency || 880;
          const duration = options.duration || 0.2;
          const volume = options.volume !== undefined ? options.volume : 0.7;
          
          synth.volume.value = this.linearToDecibels(volume);
          synth.triggerAttackRelease(frequency, duration);
          
          // 設定延遲處置
          setTimeout(() => synth.dispose(), (duration * 1000) + 500);
          
          logger.info(`[SoundEffectService] Playing synth beep: ${frequency}Hz, ${duration}s`, LogCategory.AUDIO);
          return true;
        }
        
        case 'sweep': {
          // 頻率掃描音效
          const synth = new Tone.Synth({
            oscillator: {
              type: options.wavetype || 'sine'
            },
            envelope: {
              attack: 0.01,
              decay: 0.3,
              sustain: 0.7,
              release: 0.2
            }
          }).connect(this.globalVolume);
          
          const startFreq = options.startFreq || 220;
          const endFreq = options.endFreq || 880;
          const duration = options.duration || 0.5;
          const volume = options.volume !== undefined ? options.volume : 0.7;
          
          synth.volume.value = this.linearToDecibels(volume);
          synth.triggerAttack(startFreq);
          synth.frequency.rampTo(endFreq, duration);
          setTimeout(() => synth.triggerRelease(), duration * 1000);
          
          // 設定延遲處置
          setTimeout(() => synth.dispose(), (duration * 1000) + 1000);
          
          logger.info(`[SoundEffectService] Playing frequency sweep: ${startFreq}Hz -> ${endFreq}Hz, ${duration}s`, LogCategory.AUDIO);
          return true;
        }
        
        case 'noise': {
          // 噪音效果
          const noise = new Tone.Noise({
            type: options.noiseType || 'white',
            volume: this.linearToDecibels(options.volume !== undefined ? options.volume : 0.5)
          }).connect(this.globalVolume);
          
          const duration = options.duration || 0.3;
          
          // 添加濾波器使聲音更平滑
          if (options.filter) {
            const filter = new Tone.Filter({
              type: options.filter.type || 'lowpass',
              frequency: options.filter.frequency || 1000,
              Q: options.filter.Q || 1
            });
            
            noise.chain(filter, this.globalVolume);
          }
          
          noise.start();
          noise.stop('+' + duration);
          
          // 設定延遲處置
          setTimeout(() => noise.dispose(), (duration * 1000) + 500);
          
          logger.info(`[SoundEffectService] Playing ${options.noiseType || 'white'} noise: ${duration}s`, LogCategory.AUDIO);
          return true;
        }
        
        case 'laser': {
          // 雷射槍音效
          const synth = new Tone.Synth({
            oscillator: {
              type: 'sawtooth'
            },
            envelope: {
              attack: 0.005,
              decay: 0.1,
              sustain: 0.1,
              release: 0.1
            }
          }).connect(this.globalVolume);
          
          const filter = new Tone.Filter({
            type: 'lowpass',
            frequency: 1000,
            Q: 10
          });
          
          synth.chain(filter, this.globalVolume);
          
          const startFreq = options.startFreq || 3000;
          const endFreq = options.endFreq || 500;
          const duration = options.duration || 0.2;
          const volume = options.volume !== undefined ? options.volume : 0.7;
          
          synth.volume.value = this.linearToDecibels(volume);
          synth.triggerAttack(startFreq);
          synth.frequency.exponentialRampTo(endFreq, duration);
          setTimeout(() => synth.triggerRelease(), duration * 1000);
          
          // 設定延遲處置
          setTimeout(() => {
            synth.dispose();
            filter.dispose();
          }, (duration * 1000) + 500);
          
          logger.info(`[SoundEffectService] Playing laser sound: ${duration}s`, LogCategory.AUDIO);
          return true;
        }
        
        case 'explosion': {
          // 爆炸音效
          const noise = new Tone.Noise({
            type: 'brown',
            volume: this.linearToDecibels(options.volume !== undefined ? options.volume : 0.8)
          });
          
          const filter = new Tone.Filter({
            type: 'lowpass',
            frequency: 800
          });
          
          const envelope = new Tone.AmplitudeEnvelope({
            attack: 0.01,
            decay: 0.2,
            sustain: 0.3,
            release: 0.4
          }).connect(this.globalVolume);
          
          noise.chain(filter, envelope);
          
          const duration = options.duration || 0.8;
          
          noise.start();
          envelope.triggerAttackRelease(duration);
          
          // 設定延遲處置
          setTimeout(() => {
            noise.dispose();
            filter.dispose();
            envelope.dispose();
          }, (duration * 1000) + 1000);
          
          logger.info(`[SoundEffectService] Playing explosion sound: ${duration}s`, LogCategory.AUDIO);
          return true;
        }
        
        case 'powerUp': {
          // 能量充能音效
          const synth = new Tone.Synth({
            oscillator: {
              type: 'sine'
            },
            envelope: {
              attack: 0.01,
              decay: 0.1,
              sustain: 0.5,
              release: 0.5
            }
          });
          
          const chorus = new Tone.Chorus({
            frequency: 1.5,
            delayTime: 3.5,
            depth: 0.7,
            wet: 0.5
          });
          
          synth.chain(chorus, this.globalVolume);
          
          const startFreq = options.startFreq || 200;
          const endFreq = options.endFreq || 800;
          const duration = options.duration || 1;
          const volume = options.volume !== undefined ? options.volume : 0.6;
          
          synth.volume.value = this.linearToDecibels(volume);
          synth.triggerAttack(startFreq);
          
          // 指數增長頻率，創造充能效果
          synth.frequency.exponentialRampTo(endFreq, duration);
          setTimeout(() => synth.triggerRelease(), duration * 1000);
          
          // 設定延遲處置
          setTimeout(() => {
            synth.dispose();
            chorus.dispose();
          }, (duration * 1000) + 1000);
          
          logger.info(`[SoundEffectService] Playing power up sound: ${duration}s`, LogCategory.AUDIO);
          return true;
        }
        
        default:
          logger.warn(`[SoundEffectService] Unknown synth sound type: ${type}`, LogCategory.AUDIO);
          return false;
      }
    } catch (error) {
      logger.error(`[SoundEffectService] Error playing synth sound ${type}:`, LogCategory.AUDIO, error);
      return false;
    }
  }

  /**
   * 播放合成器音效序列
   * @param effects 音效序列陣列
   */
  public playSynthSequence(effects: Array<{
    type: string;
    options?: any;
    startTime?: number;
  }>): boolean {
    if (!this.contextStarted) {
      logger.warn('[SoundEffectService] Cannot play synth sequence: AudioContext not started', LogCategory.AUDIO);
      return false;
    }
    
    if (!effects || !Array.isArray(effects) || effects.length === 0) {
      logger.warn('[SoundEffectService] Invalid sequence: empty or invalid effects array', LogCategory.AUDIO);
      return false;
    }
    
    try {
      logger.info(`[SoundEffectService] Processing synth sequence with ${effects.length} effects`, LogCategory.AUDIO);
      
      const now = Tone.now();
      
      effects.forEach((effect, index) => {
        const { type, options = {}, startTime = 0 } = effect;
        
        if (!type) {
          logger.warn(`[SoundEffectService] Effect #${index} - Missing type parameter`, LogCategory.AUDIO);
          return; // 繼續處理下一個
        }
        
        // 計算播放時間 (當前時間 + 延遲)
        const playTime = now + (startTime / 1000); // 轉換毫秒為秒
        
        try {
          // 安排在指定時間播放
          Tone.Transport.schedule((time) => {
            this.playSynthSound(type, options);
          }, playTime);
          
          logger.info(`[SoundEffectService] Scheduled synth effect #${index}: ${type} at ${startTime}ms`, LogCategory.AUDIO);
        } catch (error) {
          logger.error(`[SoundEffectService] Error scheduling synth effect #${index} (${type}):`, LogCategory.AUDIO, error);
        }
      });
      
      return true;
    } catch (error) {
      logger.error('[SoundEffectService] Error processing synth sequence:', LogCategory.AUDIO, error);
      return false;
    }
  }

  /**
   * 處理音效序列指令
   * @param effects 音效序列陣列
   */
  public playSoundEffectFromCommand(effects: Array<{
    name: string;
    type?: string;
    params?: { volume?: number };
    startTime?: number;
  }>): boolean {
    if (!this.isReady) {
      logger.warn('[SoundEffectService] Cannot play command: Service not ready', LogCategory.AUDIO);
      return false;
    }
    
    if (!effects || !Array.isArray(effects) || effects.length === 0) {
      logger.warn('[SoundEffectService] Invalid command: empty or invalid effects array', LogCategory.AUDIO);
      return false;
    }
    
    try {
      logger.info(`[SoundEffectService] Processing command with ${effects.length} effects`, LogCategory.AUDIO);
      
      const now = Tone.now();
      
      effects.forEach((effect, index) => {
        const { name, params, startTime = 0 } = effect;
        
        if (!name || !this.players[name]) {
          logger.warn(`[SoundEffectService] Effect #${index} - Sound not found: ${name}`, LogCategory.AUDIO);
          return; // 繼續處理下一個
        }
        
        const player = this.players[name];
        
        // 檢查播放器緩衝區是否已載入完成
        if (!player.buffer.loaded) {
          logger.warn(`[SoundEffectService] Effect #${index} - Buffer not loaded for sound: ${name}`, LogCategory.AUDIO);
          return; // 跳過未載入的音效
        }
        
        // 計算播放時間 (當前時間 + 延遲)
        const playTime = now + (startTime / 1000); // 轉換毫秒為秒
        
        // 獲取音量參數
        const volume = params?.volume;
        
        try {
          // 如果有音量參數
          if (volume !== undefined) {
            const volumeDB = this.linearToDecibels(volume);
            player.volume.value = volumeDB;
          }
          
          // 安排在指定時間播放
          player.stop();
          player.start(playTime);
          
          logger.info(`[SoundEffectService] Scheduled effect #${index}: ${name} at ${startTime}ms ${volume !== undefined ? `(volume: ${volume})` : ''}`, LogCategory.AUDIO);
        } catch (error) {
          logger.error(`[SoundEffectService] Error scheduling effect #${index} (${name}):`, LogCategory.AUDIO, error);
        }
      });
      
      return true;
    } catch (error) {
      logger.error('[SoundEffectService] Error processing command:', LogCategory.AUDIO, error);
      return false;
    }
  }

  /**
   * 設置全局音量
   * @param volume 線性音量值 (0-1)
   */
  public setGlobalVolume(volume: number): void {
    try {
      // 確保音量在有效範圍內
      const safeVolume = Math.max(0, Math.min(1, volume));
      
      // 將線性音量轉換為分貝
      const volumeDB = this.linearToDecibels(safeVolume);
      
      // 設置全局音量
      this.globalVolume.volume.value = volumeDB;
      
      logger.info(`[SoundEffectService] Global volume set to ${safeVolume.toFixed(2)} (${volumeDB.toFixed(2)} dB)`, LogCategory.AUDIO);
    } catch (error) {
      logger.error('[SoundEffectService] Error setting global volume:', LogCategory.AUDIO, error);
    }
  }

  /**
   * 停止所有音效播放
   */
  public stopAllSounds(): void {
    try {
      Object.values(this.players).forEach(player => {
        player.stop();
      });
      logger.info('[SoundEffectService] Stopped all sounds', LogCategory.AUDIO);
    } catch (error) {
      logger.error('[SoundEffectService] Error stopping sounds:', LogCategory.AUDIO, error);
    }
  }

  /**
   * 停止特定音效播放
   * @param name 音效名稱
   */
  public stopSound(name: string): boolean {
    if (!this.players[name]) {
      logger.warn(`[SoundEffectService] Cannot stop sound ${name}: not found`, LogCategory.AUDIO);
      return false;
    }
    
    try {
      this.players[name].stop();
      logger.info(`[SoundEffectService] Stopped sound: ${name}`, LogCategory.AUDIO);
      return true;
    } catch (error) {
      logger.error(`[SoundEffectService] Error stopping sound ${name}:`, LogCategory.AUDIO, error);
      return false;
    }
  }

  /**
   * 獲取服務狀態
   */
  public getStatus(): { isReady: boolean; isLoading: boolean } {
    return {
      isReady: this.isReady,
      isLoading: this.isLoading
    };
  }
  
  /**
   * 獲取全部已加載的音效名稱
   */
  public getLoadedSounds(): string[] {
    return Object.keys(this.players);
  }

  /**
   * 將線性音量轉換為分貝
   * 0 -> -Infinity (靜音)
   * 1 -> 0 dB (原始音量)
   */
  private linearToDecibels(volume: number): number {
    // 避免 log(0) 出現 -Infinity
    if (volume <= 0.0001) {
      return -100; // 實際靜音
    }
    return 20 * Math.log10(volume);
  }
}

export default SoundEffectService;