import { useState, useEffect, useRef } from 'react';
import ModelService from './ModelService';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

// 後端API URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

// 音頻服務類
class AudioService {
  private static instance: AudioService;
  private audioElement: HTMLAudioElement | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  
  // 仍然保留這些回調以支持舊代碼
  private onSpeakingStartCallbacks: (() => void)[] = [];
  private onSpeakingEndCallbacks: (() => void)[] = [];
  
  private modelService: ModelService;
  private mouthAnimInterval: number | null = null;

  // 單例模式
  public static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  constructor() {
    // 初始化音頻元素
    this.audioElement = new Audio();
    this.setupAudioEvents();

    // 檢查麥克風權限
    this.checkMicrophonePermission();
    
    // 獲取模型服務
    this.modelService = ModelService.getInstance();
  }

  // 設置音頻事件
  private setupAudioEvents(): void {
    if (this.audioElement) {
      // 設置播放結束事件
      this.audioElement.onended = () => {
        logger.info('音頻播放結束', LogCategory.AUDIO);
        // 播放結束後，延遲一下再關閉口型動畫，保持同步
        setTimeout(() => {
          this.stopMouthAnimation();
          
          // 使用 Zustand 更新狀態
          useStore.getState().setPlaying(false);
          this.notifySpeakingEnd();
        }, 300);
      };
    }
  }

  // 啟動口型動畫
  private startMouthAnimation(): void {
    // 如果已經有動畫在運行，先停止
    this.stopMouthAnimation();
    
    // 預先計算一組隨機值，避免頻繁計算
    const mouthValues = Array.from({ length: 10 }, () => ({
      mouthOpen: Math.random() * 0.7,
      jawOpen: Math.random() * 0.6,
      mouthLeft: Math.random() * 0.2,
      mouthRight: Math.random() * 0.2
    }));
    
    let currentIndex = 0;
    
    // 啟動口型動畫後備機制 - 當WebSocket數據不可用時
    this.mouthAnimInterval = window.setInterval(() => {
      // 使用預先計算的隨機值
      const values = mouthValues[currentIndex];
      currentIndex = (currentIndex + 1) % mouthValues.length;
      
      try {
        // 獲取當前表情 (使用淺拷貝避免深度複製開銷)
        const currentMorphs = this.modelService.getMorphTargets();
        
        // 更新口型 (只更新嘴部相關的屬性)
        const updatedMorphs = {
          ...currentMorphs,
          "mouthOpen": values.mouthOpen,
          "jawOpen": values.jawOpen,
          "mouthLeft": values.mouthLeft,
          "mouthRight": values.mouthRight
        };
        
        this.modelService.setMorphTargets(updatedMorphs);
      } catch (error) {
        // 出錯時停止動畫，避免導致崩潰
        logger.error('口型動畫更新錯誤', LogCategory.AUDIO, error);
        this.stopMouthAnimation();
      }
    }, 250); // 降低更新頻率到250毫秒
  }
  
  // 停止口型動畫
  private stopMouthAnimation(): void {
    if (this.mouthAnimInterval) {
      window.clearInterval(this.mouthAnimInterval);
      this.mouthAnimInterval = null;
    }
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

  // 開始語音錄製
  public async startRecording(): Promise<boolean> {
    // 如果已經在錄音，則不執行
    if (useStore.getState().isRecording) {
      return false;
    }

    try {
      // 請求麥克風訪問權限
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          // WebM-Opus格式適用的採樣率
          sampleRate: 48000,
        } 
      });

      logger.info('成功獲取麥克風流', LogCategory.AUDIO);
      
      // 檢查支持的MIME類型
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/ogg'
      ];
      
      let selectedMimeType = '';
      for (const type of mimeTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          selectedMimeType = type;
          logger.info(`找到支持的MIME類型: ${type}`, LogCategory.AUDIO);
          break;
        }
      }
      
      if (!selectedMimeType) {
        logger.error('瀏覽器不支持任何所需的音頻MIME類型', LogCategory.AUDIO);
        return false;
      }
      
      // 創建MediaRecorder
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: selectedMimeType,
        audioBitsPerSecond: 128000
      });
      this.audioChunks = [];
      
      // 設置資料處理
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          logger.info(`收到音頻數據片段, 大小: ${event.data.size} 字節`, LogCategory.AUDIO);
          this.audioChunks.push(event.data);
        } else {
          logger.warn('收到空音頻數據片段', LogCategory.AUDIO);
        }
      };
      
      // 錄音開始處理
      this.mediaRecorder.onstart = () => {
        logger.info(`錄音正式開始，使用MIME類型: ${selectedMimeType}`, LogCategory.AUDIO);
      };
      
      // 錄音結束處理
      this.mediaRecorder.onstop = async () => {
        // 釋放麥克風
        stream.getTracks().forEach(track => track.stop());
        logger.info(`錄音結束，收集了 ${this.audioChunks.length} 個音頻片段`, LogCategory.AUDIO);
        
        // 處理錄音數據
        await this.processRecordedAudio();
      };

      // 錄音錯誤處理
      this.mediaRecorder.onerror = (event) => {
        logger.error('錄音過程中發生錯誤', LogCategory.AUDIO, event);
      };
      
      // 開始錄音 (設置較短的時間片段，增加實時性)
      this.mediaRecorder.start(100);
      logger.info('開始錄音，時間片段間隔: 100ms', LogCategory.AUDIO);
      
      // 使用 Zustand 更新狀態
      useStore.getState().setRecording(true);
      return true;
    } catch (error) {
      logger.error('啟動錄音錯誤', LogCategory.AUDIO, error);
      return false;
    }
  }

  // 停止語音錄製
  public stopRecording(): boolean {
    if (this.mediaRecorder && useStore.getState().isRecording) {
      try {
        logger.info('嘗試停止錄音', LogCategory.AUDIO);
        this.mediaRecorder.stop();
        
        // 使用 Zustand 更新狀態
        useStore.getState().setRecording(false);
        return true;
      } catch (error) {
        logger.error('停止錄音時發生錯誤', LogCategory.AUDIO, error);
        
        // 使用 Zustand 更新狀態
        useStore.getState().setRecording(false);
        return false;
      }
    }
    
    logger.warn('嘗試停止錄音，但沒有活動的錄音', LogCategory.AUDIO);
    return false;
  }
  
  // 處理錄製的音頻數據
  private async processRecordedAudio(): Promise<void> {
    if (this.audioChunks.length === 0) {
      logger.warn('沒有音頻數據可處理', LogCategory.AUDIO);
      // 顯示錯誤通知
      useStore.getState().addToast({
        message: '錄音失敗: 未收集到有效的音頻數據',
        type: 'error',
        duration: 4000
      });
      useStore.getState().setProcessing(false);
      return;
    }
    
    try {
      // 設置處理狀態
      useStore.getState().setProcessing(true);
      
      // 將記錄的音頻塊合併為一個Blob
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      this.audioChunks = []; // 清空以便下次錄製
      
      // 檢查音頻大小，如果太小，可能是誤觸或噪音
      const audioSize = audioBlob.size;
      logger.info(`處理音頻數據，大小：${audioSize} 字節`, LogCategory.AUDIO);
      
      if (audioSize < 1000) { // 小於1KB認為是無效的
        logger.warn('音頻數據太小，可能是噪音或誤觸', LogCategory.AUDIO);
        useStore.getState().addToast({
          message: '錄音太短或聲音太小，請再試一次',
          type: 'info',
          duration: 3000
        });
        useStore.getState().setProcessing(false);
        return;
      }
      
      // 創建FormData對象，用於上傳
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      try {
        // 向伺服器發送POST請求
        const response = await fetch(`${API_BASE_URL}/api/speech-to-text`, {
          method: 'POST',
          body: formData,
          // 不設置Content-Type，讓瀏覽器自動設置帶有boundary的multipart/form-data
        });
        
        if (!response.ok) {
          let errorText = '';
          try {
            // 嘗試讀取錯誤訊息
            const errorData = await response.json();
            errorText = errorData.detail || errorData.error || `伺服器返回錯誤狀態碼: ${response.status}`;
          } catch {
            errorText = `伺服器返回錯誤狀態碼: ${response.status}`;
          }
          
          throw new Error(errorText);
        }
        
        const result = await response.json();
        
        // 處理伺服器響應
        if (result.text) {
          logger.info(`語音識別成功: "${result.text}"`, LogCategory.AUDIO);
          
          // 顯示成功通知
          useStore.getState().addToast({
            message: '語音識別成功',
            type: 'success',
            duration: 2000
          });
          
          // 將識別的文本添加到聊天中，由ChatService處理
          const chatService = (await import('./ChatService')).default.getInstance();
          chatService.sendMessage(result.text);
        } else if (result.error) {
          // 如果伺服器返回了明確的錯誤訊息
          logger.warn(`語音識別返回錯誤: ${result.error}`, LogCategory.AUDIO);
          useStore.getState().addToast({
            message: `語音識別錯誤: ${result.error}`,
            type: 'error',
            duration: 4000
          });
          useStore.getState().setProcessing(false);
        } else {
          logger.warn('語音識別未返回文本', LogCategory.AUDIO);
          useStore.getState().addToast({
            message: '無法識別您的語音，請再試一次',
            type: 'error',
            duration: 3000
          });
          useStore.getState().setProcessing(false);
        }
      } catch (error) {
        // 捕獲網絡請求錯誤
        const errorMessage = error instanceof Error ? error.message : '未知錯誤';
        logger.error(`語音識別請求錯誤: ${errorMessage}`, LogCategory.AUDIO, error);
        
        // 顯示錯誤通知
        useStore.getState().addToast({
          message: `語音處理失敗: ${errorMessage}`,
          type: 'error',
          duration: 5000
        });
        useStore.getState().setProcessing(false);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知錯誤';
      logger.error(`處理音頻數據時發生錯誤: ${errorMessage}`, LogCategory.AUDIO, error);
      
      // 顯示錯誤通知
      useStore.getState().addToast({
        message: `音頻處理錯誤: ${errorMessage}`,
        type: 'error',
        duration: 4000
      });
      useStore.getState().setProcessing(false);
    }
  }
  
  // 播放音頻
  public playAudio(audioUrl: string): void {
    if (!this.audioElement) {
      this.audioElement = new Audio();
      this.setupAudioEvents();
    }
    
    try {
      // 停止當前播放（如果有）
      if (!this.audioElement.paused) {
        this.audioElement.pause();
        this.stopMouthAnimation();
      }
      
      // 設置新的音頻源
      this.audioElement.src = audioUrl;
      
      // 預加載並播放
      this.audioElement.load();
      
      // 添加播放開始事件
      const playPromise = this.audioElement.play();
      
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            logger.info('開始播放音頻', LogCategory.AUDIO);
            // 使用 Zustand 更新狀態
            useStore.getState().setPlaying(true);
            
            // 啟動口型動畫
            this.startMouthAnimation();
            
            // 通知已開始播放
            this.notifySpeakingStart();
          })
          .catch(error => {
            logger.error('播放音頻時發生錯誤', LogCategory.AUDIO, error);
            // 使用 Zustand 更新狀態
            useStore.getState().setPlaying(false);
          });
      }
    } catch (error) {
      logger.error('設置音頻源時發生錯誤', LogCategory.AUDIO, error);
      // 使用 Zustand 更新狀態
      useStore.getState().setPlaying(false);
    }
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

  // 以下方法僅為向後兼容保留
  // =========================================
  
  // 註冊語音開始回調
  public onSpeakingStart(callback: () => void): void {
    this.onSpeakingStartCallbacks.push(callback);
  }

  // 移除語音開始回調
  public offSpeakingStart(callback: () => void): void {
    this.onSpeakingStartCallbacks = this.onSpeakingStartCallbacks.filter(cb => cb !== callback);
  }

  // 觸發語音開始回調
  private notifySpeakingStart(): void {
    this.onSpeakingStartCallbacks.forEach(callback => callback());
  }

  // 註冊語音結束回調
  public onSpeakingEnd(callback: () => void): void {
    this.onSpeakingEndCallbacks.push(callback);
  }

  // 移除語音結束回調
  public offSpeakingEnd(callback: () => void): void {
    this.onSpeakingEndCallbacks = this.onSpeakingEndCallbacks.filter(cb => cb !== callback);
  }

  // 觸發語音結束回調
  private notifySpeakingEnd(): void {
    this.onSpeakingEndCallbacks.forEach(callback => callback());
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
  
  // 封裝服務方法
  const startRecording = async () => {
    return await audioService.current.startRecording();
  };
  
  const stopRecording = () => {
    return audioService.current.stopRecording();
  };
  
  const playAudio = (audioUrl: string) => {
    audioService.current.playAudio(audioUrl);
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