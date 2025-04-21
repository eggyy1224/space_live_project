/**
 * 音頻播放器服務
 * 提供音頻播放、暫停、加載等功能
 */

import { useStore } from '../store'; // 導入 Zustand store
import logger, { LogCategory } from '../utils/LogManager'; // 導入 logger

// 音頻事件類型
export type AudioEventType = 
  | 'load' 
  | 'play' 
  | 'pause' 
  | 'end' 
  | 'progress' 
  | 'timeupdate' 
  | 'error';

// 監聽器類型
type AudioEventListener = (event: CustomEvent) => void;

export class AudioPlayerService {
  private audioElement: HTMLAudioElement;
  private audioContext: AudioContext | null = null;
  private sourceNode: MediaElementAudioSourceNode | null = null;
  private gainNode: GainNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private listeners: Map<AudioEventType, Set<AudioEventListener>> = new Map();
  private isPlaying: boolean = false;
  private currentAudioUrl: string | null = null;
  private eventTarget: EventTarget = new EventTarget();
  private progressInterval: number | null = null;
  private volume: number = 1.0;
  private playbackRate: number = 1.0;

  // 新增：音頻分析相關屬性
  private analysisFrameId: number | null = null;
  private analysisDataArray: Uint8Array | null = null;

  constructor() {
    this.audioElement = new Audio();
    this.audioElement.crossOrigin = "anonymous"; // 允許跨域加載以進行分析
    this.setupAudioElement();
  }

  /**
   * 設置音頻元素事件監聽器
   */
  private setupAudioElement(): void {
    this.audioElement.addEventListener('loadeddata', () => this.dispatchEvent('load'));
    this.audioElement.addEventListener('play', () => this.dispatchEvent('play'));
    this.audioElement.addEventListener('pause', () => {
      this.dispatchEvent('pause');
      this.stopPlaybackAnalysis(); // 暫停時停止分析
    });
    this.audioElement.addEventListener('ended', () => {
      this.isPlaying = false;
      this.dispatchEvent('end');
      this.stopProgressTracking();
      this.stopPlaybackAnalysis(); // 結束時停止分析
    });
    this.audioElement.addEventListener('timeupdate', () => this.dispatchEvent('timeupdate'));
    this.audioElement.addEventListener('error', (e) => {
      console.error('音頻錯誤:', e);
      this.dispatchEvent('error', { error: e });
      this.stopPlaybackAnalysis(); // 出錯時停止分析
    });
  }

  /**
   * 創建或獲取Web Audio API上下文
   * 並創建分析相關節點
   */
  private getAudioContext(): AudioContext {
    if (!this.audioContext) {
      try {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        // 僅在首次創建 Context 時嘗試創建分析節點
        this.setupAnalyserNodes();
      } catch (error) {
        logger.error('[AudioPlayerService] 無法創建 AudioContext:', LogCategory.AUDIO, error);
        throw error; // 重新拋出錯誤
      }
    }
    return this.audioContext;
  }

  // 新增：設置分析節點
  private setupAnalyserNodes(): void {
    if (!this.audioContext || this.sourceNode) return; // 防止重複創建

    try {
      this.sourceNode = this.audioContext.createMediaElementSource(this.audioElement);
      this.analyserNode = this.audioContext.createAnalyser();
      this.analyserNode.fftSize = 256; // 與 AudioService 保持一致
      this.analysisDataArray = new Uint8Array(this.analyserNode.frequencyBinCount);
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = this.volume;

      // 連接: source -> analyser -> gain -> destination
      this.sourceNode.connect(this.analyserNode);
      this.analyserNode.connect(this.gainNode);
      this.gainNode.connect(this.audioContext.destination);
      logger.info('[AudioPlayerService] Web Audio 分析節點已創建並連接', LogCategory.AUDIO);

    } catch (error) {
      logger.error('[AudioPlayerService] 創建或連接分析節點失敗:', LogCategory.AUDIO, error);
      // 清理可能已創建的部分節點
      this.sourceNode?.disconnect();
      this.analyserNode?.disconnect();
      this.gainNode?.disconnect();
      this.sourceNode = null;
      this.analyserNode = null;
      this.gainNode = null;
      this.analysisDataArray = null;
    }
  }

  /**
   * 加載音頻
   * @param url 音頻URL
   * @returns 加載Promise
   */
  public async loadAudio(url: string): Promise<void> {
    return new Promise(async (resolve, reject) => {
      if (this.isPlaying) {
        this.stop();
      }
      this.currentAudioUrl = url;
      this.audioElement.src = url;

      // 確保 AudioContext 和分析節點已準備好
      try {
        this.getAudioContext(); // 會觸發 setupAnalyserNodes (如果需要)
      } catch (error) {
        return reject('無法初始化音頻上下文');
      }

      const onLoad = () => {
        this.audioElement.removeEventListener('loadeddata', onLoad);
        this.audioElement.removeEventListener('error', onError);
        resolve();
      };
      
      const onError = (error: any) => {
        this.audioElement.removeEventListener('loadeddata', onLoad);
        this.audioElement.removeEventListener('error', onError);
        reject(error);
      };
      
      this.audioElement.addEventListener('loadeddata', onLoad);
      this.audioElement.addEventListener('error', onError);
      
      this.audioElement.load();
    });
  }

  /**
   * 播放音頻
   * @returns 是否成功開始播放
   */
  public play(): boolean {
    if (!this.audioElement.src) {
      console.error('沒有加載音頻');
      return false;
    }

    try {
      // 確保 AudioContext 處於運行狀態
      if (this.audioContext && this.audioContext.state === 'suspended') {
        this.audioContext.resume().then(() => {
          logger.info('[AudioPlayerService] AudioContext resumed', LogCategory.AUDIO);
          this._startPlayback();
        }).catch(err => {
           logger.error('[AudioPlayerService] Failed to resume AudioContext', LogCategory.AUDIO, err);
        });
      } else {
        this._startPlayback();
      }
      return true;
    } catch (error) {
      console.error('播放錯誤:', error);
      this.dispatchEvent('error', { error });
      return false;
    }
  }

  // 內部啟動播放邏輯
  private _startPlayback(): void {
    const playPromise = this.audioElement.play();
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          this.isPlaying = true;
          this.startProgressTracking();
          this.startPlaybackAnalysis(); // <--- 開始分析
          this.dispatchEvent('play'); // 手動觸發，因為 play 事件可能已觸發
        })
        .catch(error => {
          logger.error('播放錯誤:', LogCategory.AUDIO, error);
          this.isPlaying = false;
          this.stopPlaybackAnalysis(); // <--- 播放失敗停止分析
          this.dispatchEvent('error', { error });
        });
    }
  }

  /**
   * 暫停音頻
   */
  public pause(): void {
    if (this.isPlaying) {
      this.audioElement.pause();
      this.isPlaying = false;
      this.stopProgressTracking();
      this.stopPlaybackAnalysis(); // 暫停時停止分析
    }
  }

  /**
   * 停止音頻（暫停並重置到開始）
   */
  public stop(): void {
    this.pause();
    this.audioElement.currentTime = 0;
  }

  /**
   * 加載並播放音頻
   * @param url 音頻URL
   * @returns 播放Promise
   */
  public async playAudio(url: string): Promise<boolean> {
    try {
      if (this.currentAudioUrl === url && this.isPlaying) {
        return true; 
      }
      await this.loadAudio(url);
      return this.play();
    } catch (error) {
      console.error('加載並播放音頻失敗:', error);
      this.dispatchEvent('error', { error });
      return false;
    }
  }

  /**
   * 設置音量
   * @param volume 音量值（0-1）
   */
  public setVolume(volume: number): void {
    this.volume = Math.max(0, Math.min(1, volume));
    this.audioElement.volume = this.volume;
    
    if (this.gainNode) {
      this.gainNode.gain.value = this.volume;
    }
  }

  /**
   * 獲取當前音量
   * @returns 音量值
   */
  public getVolume(): number {
    return this.volume;
  }

  /**
   * 設置播放速度
   * @param rate 播放速度（0.5-2.0）
   */
  public setPlaybackRate(rate: number): void {
    this.playbackRate = Math.max(0.5, Math.min(2.0, rate));
    this.audioElement.playbackRate = this.playbackRate;
  }

  /**
   * 獲取播放速度
   * @returns 播放速度
   */
  public getPlaybackRate(): number {
    return this.playbackRate;
  }

  /**
   * 獲取音頻時長
   * @returns 時長（秒）
   */
  public getDuration(): number {
    return this.audioElement.duration || 0;
  }

  /**
   * 獲取當前播放位置
   * @returns 當前時間（秒）
   */
  public getCurrentTime(): number {
    return this.audioElement.currentTime || 0;
  }

  /**
   * 設置當前播放位置
   * @param time 時間（秒）
   */
  public setCurrentTime(time: number): void {
    if (time >= 0 && time <= this.getDuration()) {
      this.audioElement.currentTime = time;
    }
  }

  /**
   * 獲取當前播放狀態
   * @returns 是否正在播放
   */
  public isAudioPlaying(): boolean {
    return this.isPlaying;
  }

  /**
   * 開始跟踪進度並發送進度事件
   */
  private startProgressTracking(): void {
    if (this.progressInterval !== null) {
      this.stopProgressTracking();
    }
    
    this.progressInterval = window.setInterval(() => {
      const currentTime = this.getCurrentTime();
      const duration = this.getDuration();
      const progress = duration > 0 ? currentTime / duration : 0;
      
      this.dispatchEvent('progress', {
        currentTime,
        duration,
        progress
      });
    }, 100); // 每100毫秒更新一次
  }

  /**
   * 停止跟踪進度
   */
  private stopProgressTracking(): void {
    if (this.progressInterval !== null) {
      window.clearInterval(this.progressInterval);
      this.progressInterval = null;
    }
  }

  /**
   * 分發事件
   * @param type 事件類型
   * @param detail 事件詳情
   */
  private dispatchEvent(type: AudioEventType, detail: any = {}): void {
    const event = new CustomEvent(type, { detail });
    this.eventTarget.dispatchEvent(event);
    
    // 通知特定事件的監聽器
    const listeners = this.listeners.get(type);
    if (listeners) {
      for (const listener of listeners) {
        try {
          listener(event);
        } catch (error) {
          console.error(`執行音頻事件監聽器錯誤 (類型: ${type}):`, error);
        }
      }
    }
  }

  /**
   * 添加事件監聽器
   * @param type 事件類型
   * @param listener 監聽器函數
   * @returns 移除監聽器的函數
   */
  public addEventListener(type: AudioEventType, listener: AudioEventListener): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    
    this.listeners.get(type)!.add(listener);
    
    return () => {
      this.removeEventListener(type, listener);
    };
  }

  /**
   * 移除事件監聽器
   * @param type 事件類型
   * @param listener 監聽器函數
   */
  public removeEventListener(type: AudioEventType, listener: AudioEventListener): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      listeners.delete(listener);
    }
  }

  /**
   * 獲取音頻元素
   * @returns HTML音頻元素
   */
  public getAudioElement(): HTMLAudioElement {
    return this.audioElement;
  }

  /**
   * 創建音頻分析器節點
   * @param fftSize FFT大小
   * @returns 分析器節點
   */
  public createAnalyser(fftSize: number = 2048): AnalyserNode | null {
    try {
      const audioContext = this.getAudioContext();
      
      // 創建媒體源節點
      const source = audioContext.createMediaElementSource(this.audioElement);
      
      // 創建分析器節點
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = fftSize;
      
      // 創建增益節點
      const gainNode = audioContext.createGain();
      gainNode.gain.value = this.volume;
      
      // 連接節點
      source.connect(analyser);
      analyser.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // 保存節點引用
      this.sourceNode = source as unknown as MediaElementAudioSourceNode;
      this.analyserNode = analyser;
      this.gainNode = gainNode;
      
      return analyser;
    } catch (error) {
      console.error('創建音頻分析器錯誤:', error);
      return null;
    }
  }

  /**
   * 獲取音頻分析數據
   * @returns 頻率數據
   */
  public getAnalyserData(): Uint8Array | null {
    if (!this.analyserNode) {
      return null;
    }
    
    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyserNode.getByteFrequencyData(dataArray);
    
    return dataArray;
  }

  // --- 新增：音頻分析方法 --- 
  private startPlaybackAnalysis(): void {
    if (this.analysisFrameId !== null || !this.analyserNode) {
      return; // 正在分析或分析器未就緒
    }
    logger.debug('[AudioPlayerService] Starting playback analysis loop.', LogCategory.AUDIO);
    this.analysisFrameId = requestAnimationFrame(this.analysePlaybackFrame);
  }

  private stopPlaybackAnalysis(): void {
    if (this.analysisFrameId !== null) {
      cancelAnimationFrame(this.analysisFrameId);
      this.analysisFrameId = null;
      // 重置嘴型
      useStore.getState().setAudioLipsyncTarget('jawOpen', 0); 
      logger.debug('[AudioPlayerService] Stopped playback analysis loop and reset jawOpen.', LogCategory.AUDIO);
    }
  }

  private analysePlaybackFrame = (): void => {
    if (!this.analyserNode || !this.analysisDataArray || !this.isPlaying) {
      this.stopPlaybackAnalysis();
      return;
    }

    // 獲取音量 RMS
    this.analyserNode.getByteTimeDomainData(this.analysisDataArray);
    let sumOfSquares = 0;
    for (let i = 0; i < this.analysisDataArray.length; i++) {
      const norm = (this.analysisDataArray[i] / 128.0) - 1.0; // Normalize to [-1, 1]
      sumOfSquares += norm * norm;
    }
    const rms = Math.sqrt(sumOfSquares / this.analysisDataArray.length);

    // 映射到 jawOpen
    const sensitivity = 4.0; 
    const threshold = 0.01;
    let jawOpenValue = 0;
    if (rms > threshold) {
      jawOpenValue = Math.min(1.0, rms * sensitivity);
    }

    // 更新 Zustand store
    useStore.getState().setAudioLipsyncTarget('jawOpen', jawOpenValue);

    // 請求下一幀
    this.analysisFrameId = requestAnimationFrame(this.analysePlaybackFrame);
  };
  // --- 音頻分析方法結束 ---
}

// 導出單例實例
const audioPlayer = new AudioPlayerService();
export default audioPlayer; 