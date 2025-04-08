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
    // Ensure permission first
    if (useStore.getState().micPermission !== 'granted') {
      const granted = await this.requestMicPermission();
      if (!granted) {
        logger.warn('Microphone permission denied, cannot start recording.', LogCategory.AUDIO);
        return;
      }
    }

    this.initializeAudioContext(); 
    if (!this.audioContext || useStore.getState().isRecording) return;

    logger.info('Starting audio recording...', LogCategory.AUDIO);
    this.audioChunks = [];
    useStore.getState().setRecording(true); 
    useStore.getState().setSpeaking(true); // Use the correct state
    useStore.getState().setAudioStartTime(null); 

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.sourceNode.connect(this.analyser);

      const recorder = new MediaRecorder(this.mediaStream);
      recorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      recorder.onstop = () => {
        logger.info('[AudioService] MediaRecorder onstop triggered.', LogCategory.AUDIO);
        this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        
        try {
            onStop(this.audioBlob);
            logger.info('[AudioService] onStop callback executed.', LogCategory.AUDIO);
        } catch (callbackError) {
            logger.error('[AudioService] Error executing onStop callback:', LogCategory.AUDIO, callbackError);
        }
        
        useStore.getState().setRecording(false);
        useStore.getState().setSpeaking(false); // Use the correct state
        this.stopMouthAnimation(); 
        logger.info('Recording stopped, audio blob created.', LogCategory.AUDIO);
        
        this.mediaStream?.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
        this.sourceNode?.disconnect();
        this.sourceNode = null;
        this.analyser = null;
      };

      recorder.start();

    } catch (error) {
      logger.error('Error starting recording:', LogCategory.AUDIO, error);
      useStore.getState().setRecording(false); 
      useStore.getState().setSpeaking(false); // Use the correct state
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
    logger.debug('Started mouth animation loop (for analysis only).', LogCategory.AUDIO);
    
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
    logger.debug('Stopped mouth animation loop (analysis only).', LogCategory.AUDIO);
  }

  private updateMouthShape = (): void => {
    if (!this.analyser || !useStore.getState().isRecording) {
      this.stopMouthAnimation(); 
      return;
    }
    // Only analysis, no state update here
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(dataArray);
    // const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    // const normalizedAverage = Math.min(1, average / 128); 

    if (useStore.getState().isRecording) {
        this.animationFrameId = requestAnimationFrame(this.updateMouthShape);
    }
  };

  // 播放音頻 Blob 或 URL
  public playAudio(audioData: Blob | string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.stopPlayback(); 
      this.initializeAudioContext();

      let audioUrl: string;
      if (audioData instanceof Blob) {
        audioUrl = URL.createObjectURL(audioData);
      } else {
        audioUrl = audioData;
      }

      this.playbackAudio = new Audio(audioUrl);

      const onPlay = () => {
        logger.info(`Audio playback started: ${audioUrl}`, LogCategory.AUDIO);
        useStore.getState().setSpeaking(true);
        useStore.getState().setAudioStartTime(performance.now());
      };

      const onEnded = () => {
        logger.info(`Audio playback finished: ${audioUrl}`, LogCategory.AUDIO);
        useStore.getState().setSpeaking(false);
        useStore.getState().setAudioStartTime(null);
        this.cleanupPlayback();
        resolve();
      };

      const onError = (e: Event | string) => {
        logger.error(`Error during audio playback: ${audioUrl}`, LogCategory.AUDIO, e);
        useStore.getState().setSpeaking(false);
        useStore.getState().setAudioStartTime(null);
        this.cleanupPlayback();
        reject(new Error(`Playback failed: ${String(e)}`)); // Ensure e is stringified
      };

      this.playbackAudio.addEventListener('play', onPlay, { once: true });
      this.playbackAudio.addEventListener('ended', onEnded, { once: true });
      this.playbackAudio.addEventListener('error', onError, { once: true });

      this.playbackAudio.play().catch(onError); 
    });
  }

  // 停止播放
  public stopPlayback(): void {
    if (this.playbackAudio) {
      logger.info('Stopping audio playback manually.', LogCategory.AUDIO);
      this.playbackAudio.pause();
      this.playbackAudio.currentTime = 0; 
      this.cleanupPlayback(); 
      useStore.getState().setSpeaking(false);
      useStore.getState().setAudioStartTime(null);
    }
  }

  private cleanupPlayback(): void {
     // Simple cleanup: just nullify the reference
     // Proper listener removal is complex without storing references
     if (this.playbackAudio) {
        if (this.playbackAudio.src.startsWith('blob:')) {
            URL.revokeObjectURL(this.playbackAudio.src);
            logger.debug('Revoked object URL.', LogCategory.AUDIO);
        }
        this.playbackAudio = null;
     }
  }

  public getIsRecording(): boolean {
    return useStore.getState().isRecording;
  }

  // --- Microphone Permission Handling ---
  public async checkMicPermission(): Promise<'prompt' | 'granted' | 'denied'> {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      logger.error('MediaDevices API not supported.', LogCategory.AUDIO);
      useStore.getState().setMicPermission('denied'); // Update state via AppSlice
      return 'denied';
    }
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      useStore.getState().setMicPermission(permissionStatus.state); // Update state via AppSlice
      logger.info(`Mic permission status: ${permissionStatus.state}`, LogCategory.AUDIO);
      // Handle changes
      permissionStatus.onchange = () => {
        logger.info(`Mic permission status changed: ${permissionStatus.state}`, LogCategory.AUDIO);
        useStore.getState().setMicPermission(permissionStatus.state); // Update state via AppSlice
      };
      return permissionStatus.state;
    } catch (error) {
      logger.error('Error querying microphone permission:', LogCategory.AUDIO, error);
      useStore.getState().setMicPermission('denied'); // Update state via AppSlice on error
      return 'denied';
    }
  }

  public async requestMicPermission(): Promise<boolean> {
    const currentPermission = useStore.getState().micPermission;
    if (currentPermission === 'granted') return true;
    
    logger.info('Requesting microphone permission...', LogCategory.AUDIO);
    try {
      // Request permission by trying to get the stream
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Immediately stop the tracks if we only wanted to check permission
      stream.getTracks().forEach(track => track.stop());
      useStore.getState().setMicPermission('granted'); // Update state via AppSlice
      logger.info('Microphone permission granted.', LogCategory.AUDIO);
      return true;
    } catch (error: any) {
      logger.error('Error requesting microphone permission:', LogCategory.AUDIO, error);
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        useStore.getState().setMicPermission('denied'); // Update state via AppSlice
      } else {
        // Handle other errors if necessary, maybe keep as prompt?
        useStore.getState().setMicPermission('prompt');
      }
      return false;
    }
  }
  // --- End Microphone Permission Handling ---

  // 獲取當前錄音狀態 (使用 Zustand)
  public isCurrentlyRecording(): boolean {
    return useStore.getState().isRecording;
  }

  // 獲取當前語音播放狀態 (使用 Zustand)
  public isCurrentlySpeaking(): boolean {
    return useStore.getState().isSpeaking;
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

  // Add getIsSpeaking for convenience if needed elsewhere
  public getIsSpeaking(): boolean {
      return useStore.getState().isSpeaking;
  }
}

// React Hook - 使用音頻服務
export function useAudioService() {
  // 直接從 Zustand 獲取相關狀態
  const isRecording = useStore((state) => state.isRecording);
  const isSpeaking = useStore((state) => state.isSpeaking);
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
  
  const checkMicPermission = async () => {
    return await audioService.current.checkMicPermission();
  };
  
  // 返回狀態和方法
  return {
    isRecording,
    isSpeaking,
    isProcessing,
    micPermission,
    startRecording,
    stopRecording,
    playAudio,
    checkMicPermission
  };
}

export default AudioService; 
