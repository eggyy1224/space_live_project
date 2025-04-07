import { useState, useEffect, useRef } from 'react';
import ModelService from './ModelService';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

// 後端API URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

// 音頻服務類
class AudioService {
  private static instance: AudioService;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private mediaStream: MediaStream | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;
  private audioChunks: Blob[] = [];
  private audioBlob: Blob | null = null;
  private playbackAudio: HTMLAudioElement | null = null;
  private animationFrameId: number | null = null;
  private mouthAnimationIntervalId: number | null = null;
  private modelService: ModelService;

  // 單例模式
  public static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  constructor() {
    this.initializeAudioContext();
    this.modelService = ModelService.getInstance();
  }

  private initializeAudioContext(): void {
    if (!this.audioContext) {
      try {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        logger.info('AudioContext initialized successfully.', LogCategory.AUDIO);
      } catch (e) {
        logger.error('Web Audio API is not supported in this browser.', LogCategory.AUDIO, e);
        return;
      }
    }
    // 確保在用戶互動後恢復 AudioContext
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume().then(() => {
        logger.info('AudioContext resumed after user interaction.', LogCategory.AUDIO);
      });
    }
  }

  public async startRecording(onStop: (audioBlob: Blob | null) => void): Promise<void> {
    this.initializeAudioContext(); // 確保 AudioContext 已初始化
    if (!this.audioContext || useStore.getState().isRecording) return;

    logger.info('Starting audio recording...', LogCategory.AUDIO);
    this.audioChunks = []; // 清空之前的音頻塊
    useStore.getState().setRecording(true); // <-- 更新 Zustand 狀態

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.sourceNode.connect(this.analyser);
      // 注意：這裡不連接到 destination，避免回聲

      this.startMouthAnimation(); // 開始嘴型動畫

      // 使用 MediaRecorder 處理錄音
      const recorder = new MediaRecorder(this.mediaStream);
      recorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      recorder.onstop = () => {
        // 添加日誌
        logger.info('[AudioService] MediaRecorder onstop triggered.', LogCategory.AUDIO);
        this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        
        try {
            // 調用從 UI 傳來的回調
            onStop(this.audioBlob);
            logger.info('[AudioService] onStop callback executed.', LogCategory.AUDIO);
        } catch (callbackError) {
            logger.error('[AudioService] Error executing onStop callback:', LogCategory.AUDIO, callbackError);
        }
        
        useStore.getState().setRecording(false);
        this.stopMouthAnimation(); // 停止嘴型動畫
        logger.info('Recording stopped, audio blob created.', LogCategory.AUDIO);
        
        // 停止所有軌道以釋放資源
        this.mediaStream?.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
        this.sourceNode?.disconnect();
        this.sourceNode = null;
        this.analyser = null;
      };

      recorder.start(); // 開始錄製

    } catch (error) {
      logger.error('Error starting recording:', LogCategory.AUDIO, error);
      useStore.getState().setRecording(false); // <-- 更新 Zustand 狀態
      this.stopMouthAnimation();
    }
  }

  public stopRecording(): void {
    if (!useStore.getState().isRecording || !this.mediaStream) return;
    // 添加日誌
    logger.info('[AudioService] stopRecording called. Stopping media tracks...', LogCategory.AUDIO);
    this.mediaStream.getTracks().forEach(track => track.stop());
    logger.info('Stopped recording via track stop.', LogCategory.AUDIO);
  }

  private startMouthAnimation(): void {
    this.stopMouthAnimation(); // 確保之前的動畫已停止
    this.animationFrameId = requestAnimationFrame(this.updateMouthShape.bind(this));
    logger.debug('Started mouth animation loop.', LogCategory.AUDIO);
    
    // 移除多餘的 setInterval fallback
    /*
    this.mouthAnimationIntervalId = window.setInterval(() => {
        if (useStore.getState().isRecording && this.analyser) {
            const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            this.analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            const average = sum / dataArray.length;
            const mouthOpenValue = Math.min(1, (average / 128) * 1.5); // 根據音量計算嘴巴開合度
            // 移除日誌
            // console.log(`[AudioService Interval] Average: ${average.toFixed(2)}, MouthOpen: ${mouthOpenValue.toFixed(2)}`);

            // 直接讀取和更新 Zustand 狀態
            // const currentMorphs = useStore.getState().morphTargets;
            // const updatedMorphs = { ...currentMorphs, jawOpen: mouthOpenValue };
            // 使用 updateMorphTarget 更新，避免覆蓋其他表情
            useStore.getState().updateMorphTarget('jawOpen', mouthOpenValue);
            // logger.debug({ msg: 'Fallback mouth animation update', details: { jawOpen: mouthOpenValue }}, LogCategory.AUDIO);
        }
    }, 250); // 每 250ms 更新一次 fallback
    */

  }

  private stopMouthAnimation(): void {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    // 不再需要清除 interval ID
    /*
    if (this.mouthAnimationIntervalId) {
      clearInterval(this.mouthAnimationIntervalId);
      this.mouthAnimationIntervalId = null;
    }
    */
    // 重置嘴型到關閉狀態
    useStore.getState().updateMorphTarget('jawOpen', 0);
    logger.debug('Stopped mouth animation loop and reset jawOpen.', LogCategory.AUDIO);
  }

  private updateMouthShape = (): void => {
    if (!this.analyser) {
      this.mouthAnimationIntervalId = null;
      return;
    }

    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(dataArray);
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    const normalizedAverage = Math.min(1, average / 128); 

    const mouthOpenValue = normalizedAverage;

    // 移除日誌
    // logger.debug(`[AudioService Frame] Average: ${average.toFixed(2)}, MouthOpen: ${mouthOpenValue.toFixed(2)}`, LogCategory.AUDIO);

    // 修正: 使用 updateMorphTarget 只更新 jawOpen，而不是 setMorphTargets 覆蓋整個狀態
    // useStore.getState().setMorphTargets({'jawOpen': mouthOpenValue});
    useStore.getState().updateMorphTarget('jawOpen', mouthOpenValue);

    // 修正：遞迴調用應該賦值給 animationFrameId
    // this.mouthAnimationIntervalId = requestAnimationFrame(this.updateMouthShape);
    this.animationFrameId = requestAnimationFrame(this.updateMouthShape);
  };

  // 播放音頻 Blob 或 URL
  public playAudio(audioData: Blob | string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.stopPlayback(); // 停止任何正在播放的音頻
      this.initializeAudioContext();

      let audioUrl: string;
      if (audioData instanceof Blob) {
        audioUrl = URL.createObjectURL(audioData);
      } else {
        audioUrl = audioData;
      }

      this.playbackAudio = new Audio(audioUrl);

      // --- AudioContext 分析節點設置 (用於播放時的嘴型動畫) ---
      let playbackSourceNode: MediaElementAudioSourceNode | null = null;
      if (this.audioContext && this.playbackAudio) {
          try {
              playbackSourceNode = this.audioContext.createMediaElementSource(this.playbackAudio);
              this.analyser = this.audioContext.createAnalyser();
              this.analyser.fftSize = 2048;
              playbackSourceNode.connect(this.analyser);
              this.analyser.connect(this.audioContext.destination); // 播放需要連接到輸出
              logger.info('AudioContext analyser connected for playback.', LogCategory.AUDIO);
          } catch (err) {
              logger.error('Failed to connect analyser for playback:', LogCategory.AUDIO, err);
              this.analyser = null; // 連接失敗則不使用分析器
          }
      }
      // -------

      this.playbackAudio.oncanplaythrough = () => {
        logger.info('Audio ready for playback.', LogCategory.AUDIO);
        if (!this.playbackAudio) return;

        // 將播放邏輯放回 .then()
        this.playbackAudio.play()
          .then(() => {
            useStore.getState().setPlaying(true);
            logger.info('Audio playback started successfully within .then().', LogCategory.AUDIO); // 修改日誌
            if (this.analyser) {
                this.startMouthAnimation(); 
            } else {
                logger.warn('Analyser not available for playback mouth animation.', LogCategory.AUDIO);
            }
            
            if (this.audioContext?.state === 'suspended') {
              this.audioContext.resume();
            }
          })
          .catch(error => {
            logger.error('Error playing audio:', LogCategory.AUDIO, error);
            useStore.getState().setPlaying(false);
            this.stopMouthAnimation();
            if (audioData instanceof Blob) URL.revokeObjectURL(audioUrl);
            if (playbackSourceNode) playbackSourceNode.disconnect();
            if (this.analyser) this.analyser.disconnect();
            reject(error); // 將錯誤 reject 出去
          });
      };

      this.playbackAudio.onended = () => {
        logger.info('Audio playback finished.', LogCategory.AUDIO);
        useStore.getState().setPlaying(false);
        this.stopMouthAnimation();
        if (audioData instanceof Blob) URL.revokeObjectURL(audioUrl);
        if (playbackSourceNode) playbackSourceNode.disconnect();
        if (this.analyser) this.analyser.disconnect();
        resolve(); // 正常結束
      };

      this.playbackAudio.onerror = (e) => {
        logger.error('Error loading or playing audio:', LogCategory.AUDIO, e);
        useStore.getState().setPlaying(false);
        this.stopMouthAnimation();
        if (audioData instanceof Blob) URL.revokeObjectURL(audioUrl);
        if (playbackSourceNode) playbackSourceNode.disconnect();
        if (this.analyser) this.analyser.disconnect();
        reject(e); // 出錯，reject promise
      };

      // 預加載音頻
      this.playbackAudio.load();
    });
  }

  // 停止播放
  public stopPlayback(): void {
    if (this.playbackAudio && useStore.getState().isPlaying) {
      this.playbackAudio.pause();
      this.playbackAudio.currentTime = 0; // 重置播放時間
      useStore.getState().setPlaying(false); // <-- 更新 Zustand 狀態
      this.stopMouthAnimation();
      logger.info('Audio playback stopped manually.', LogCategory.AUDIO);
      // 如果是 Blob URL，則釋放它
      if (this.playbackAudio.src.startsWith('blob:')) {
        URL.revokeObjectURL(this.playbackAudio.src);
      }
      // 斷開 analyser 連接 (如果存在)
      // 這裡獲取 playbackSourceNode 比較困難，暫時只斷開 analyser
      // 更好的做法是在 playAudio 創建時保存 sourceNode 引用
      if (this.analyser) {
          try {
              this.analyser.disconnect();
          } catch(e) { /* ignore */ }
      }
      this.playbackAudio = null;
    }
  }

  public getIsRecording(): boolean {
    return useStore.getState().isRecording;
  }

  // 檢查麥克風權限
  public async checkMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // 立即釋放麥克風
      stream.getTracks().forEach(track => track.stop());
      
      // 使用 Zustand 更新 micPermission 狀態
      useStore.getState().setMicPermission('granted');
      logger.info('麥克風權限已授權', LogCategory.AUDIO);
      return true;
    } catch (error) {
      // 使用 Zustand 更新 micPermission 狀態
      useStore.getState().setMicPermission('denied');
      logger.error('麥克風權限被拒絕', LogCategory.AUDIO, error);
      return false;
    }
  }

  // 獲取麥克風權限狀態
  public getMicrophonePermission(): string {
    return useStore.getState().micPermission;
  }

  // 獲取當前錄音狀態 (使用 Zustand)
  public isCurrentlyRecording(): boolean {
    return useStore.getState().isRecording;
  }

  // 獲取當前語音播放狀態 (使用 Zustand)
  public isCurrentlySpeaking(): boolean {
    return useStore.getState().isPlaying;
  }

  // 獲取當前處理狀態 (使用 Zustand)
  public isCurrentlyProcessing(): boolean {
    return useStore.getState().isProcessing;
  }

  // 設置處理狀態 (使用 Zustand)
  private setProcessing(processing: boolean): void {
    const currentProcessing = useStore.getState().isProcessing;
    if (currentProcessing !== processing) {
      useStore.getState().setProcessing(processing);
    }
  }
}

// React Hook - 使用音頻服務
export function useAudioService() {
  // 直接從 Zustand 獲取相關狀態
  const isRecording = useStore((state) => state.isRecording);
  const isPlaying = useStore((state) => state.isPlaying);
  const isProcessing = useStore((state) => state.isProcessing);
  const micPermission = useStore((state) => state.micPermission);
  
  // 獲取 AudioService 實例
  const audioService = useRef<AudioService>(AudioService.getInstance());

  // 包裝 startRecording 以記錄 onStop 回調
  const startRecording = async (onStop: (audioBlob: Blob | null) => void) => {
    const wrappedOnStop = (audioBlob: Blob | null) => {
        logger.info('[useAudioService] Wrapped onStop called.', LogCategory.AUDIO);
        try {
            onStop(audioBlob); // 執行原始的回調
            logger.info('[useAudioService] Original onStop executed successfully.', LogCategory.AUDIO);
        } catch(err) {
            logger.error('[useAudioService] Error in original onStop callback:', LogCategory.AUDIO, err);
        }
    };
    await audioService.current.startRecording(wrappedOnStop);
  };
  
  const stopRecording = () => {
    audioService.current.stopRecording();
  };
  
  const playAudio = async (audioData: Blob | string) => {
    // 包裝播放以捕獲可能的錯誤
    try {
        await audioService.current.playAudio(audioData);
    } catch (error) {
        logger.error('[useAudioService] Error during audio playback:', LogCategory.AUDIO, error);
        // 可以在這裡添加 UI 提示
    }
  };
  
  const checkMicrophonePermission = async () => {
    return await audioService.current.checkMicrophonePermission();
  };
  
  // 返回狀態和方法
  return {
    isRecording,
    isPlaying,
    isProcessing,
    micPermission,
    startRecording,
    stopRecording,
    playAudio,
    checkMicrophonePermission
  };
}

export default AudioService; 
