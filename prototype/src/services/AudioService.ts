import { useState, useEffect, useRef } from 'react';
import ModelService from './ModelService';
import logger, { LogCategory } from '../utils/LogManager';

// 後端API URL
const API_BASE_URL = 'http://localhost:8000';

// 音頻服務類
class AudioService {
  private static instance: AudioService;
  private audioElement: HTMLAudioElement | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private onSpeakingStartCallbacks: (() => void)[] = [];
  private onSpeakingEndCallbacks: (() => void)[] = [];
  private onAudioProcessingCallbacks: ((isProcessing: boolean) => void)[] = [];
  private isRecording = false;
  private isSpeaking = false;
  private isProcessing = false;
  private micPermission: boolean | null = null;
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
          this.isSpeaking = false;
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
      
      this.micPermission = true;
      logger.info('麥克風權限已授權', LogCategory.AUDIO);
      return true;
    } catch (error) {
      this.micPermission = false;
      logger.error('麥克風權限被拒絕', LogCategory.AUDIO, error);
      return false;
    }
  }

  // 獲取麥克風權限狀態
  public getMicrophonePermission(): boolean | null {
    return this.micPermission;
  }

  // 開始語音錄製
  public async startRecording(): Promise<boolean> {
    // 如果已經在錄音，則不執行
    if (this.isRecording) {
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
      this.isRecording = true;
      return true;
    } catch (error) {
      logger.error('啟動錄音錯誤', LogCategory.AUDIO, error);
      return false;
    }
  }

  // 停止語音錄製
  public stopRecording(): boolean {
    if (this.mediaRecorder && this.isRecording) {
      try {
        logger.info('嘗試停止錄音', LogCategory.AUDIO);
        this.mediaRecorder.stop();
        this.isRecording = false;
        return true;
      } catch (error) {
        logger.error('停止錄音時發生錯誤', LogCategory.AUDIO, error);
        this.isRecording = false;
        return false;
      }
    }
    return false;
  }

  // 處理錄製的音頻
  private async processRecordedAudio(): Promise<void> {
    if (this.audioChunks.length === 0) {
      logger.warn('沒有錄製到音頻數據', LogCategory.AUDIO);
      this.setProcessing(false);
      return;
    }
    
    try {
      // 創建音頻Blob - 使用與錄製時相同的MIME類型
      const mimeType = this.mediaRecorder?.mimeType || 'audio/webm;codecs=opus';
      const audioBlob = new Blob(this.audioChunks, { type: mimeType });
      logger.info(`創建音頻Blob，大小: ${audioBlob.size} 字節，MIME類型: ${mimeType}`, LogCategory.AUDIO);
      
      if (audioBlob.size < 100) {
        logger.warn('音頻數據太小，可能沒有捕獲到有效聲音', LogCategory.AUDIO);
        this.setProcessing(false);
        return;
      }
      
      // === 開始處理前，設置 isProcessing = true ===
      this.setProcessing(true);
      
      // 將Blob轉為Base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        try {
          const base64data = reader.result as string;
          // 移除data URL前綴
          const audioData = base64data.split(',')[1];
          logger.info(`音頻Base64編碼完成，長度: ${audioData.length}`, LogCategory.AUDIO);
          
          // === 不再在這裡設置 processing ===
          // this.setProcessing(true); 
          
          // 打印音頻MIME類型和支持的格式
          logger.info(`MediaRecorder支持的MIME類型: ${
            ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg']
              .map(type => `${type}: ${MediaRecorder.isTypeSupported(type) ? '支持' : '不支持'}`)
              .join(', ')
          }`, LogCategory.AUDIO);
          
          // 發送到後端進行STT處理
          logger.info('正在發送音頻到後端處理...', LogCategory.AUDIO);
          const response = await fetch(`${API_BASE_URL}/api/speech-to-text`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              audio_base64: audioData,
              mime_type: mimeType // 同時傳遞MIME類型
            })
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
          }
          
          const data = await response.json();
          logger.info('收到後端回應', LogCategory.AUDIO, data);
          
          // 清理音頻塊
          this.audioChunks = [];
          
          // === 獲取 ChatService 實例 ===
          const ChatService = (await import('./ChatService')).default;
          const chatService = ChatService.getInstance();
          
          // 處理識別結果
          if (data.success) {
            // 如果有識別到文字，更新UI顯示
            if (data.text) {
              logger.info(`語音識別結果: ${data.text}`, LogCategory.AUDIO);
              
              // 將識別的文字添加為用戶消息
              chatService.addMessage({
                role: 'user',
                content: data.text
              });
              
              // 添加 AI 的文字回應到聊天
              if (data.response) {
                  chatService.addMessage({
                    role: 'bot',
                    content: data.response
                  });
              } else {
                  logger.warn('後端回應中缺少 AI 文字回應 (data.response)', LogCategory.AUDIO);
              }
              
              // HTTP API (/api/speech-to-text) 已經處理了語音識別和回應生成
              logger.info(`使用HTTP API處理語音識別`, LogCategory.AUDIO);
            } else {
              logger.warn('未能識別有效的語音內容', LogCategory.AUDIO);
              chatService.addMessage({
                role: 'bot',
                content: '抱歉，我沒有聽清您說的內容，請再試一次。'
              });
            }
            
            // 如果後端API提供了音頻（可能是測試模式），播放它
            if (data.audio) {
              logger.info('API返回了音頻，將直接播放', LogCategory.AUDIO);
              this.playAudio(`data:audio/mp3;base64,${data.audio}`);
            }
          } else {
            // 處理失敗情況
            const errorMsg = data.error || '未知錯誤';
            logger.warn(`語音識別失敗: ${errorMsg}`, LogCategory.AUDIO);
            chatService.addMessage({
              role: 'bot',
              content: '抱歉，我沒有聽清您說的話，請再說一遍或嘗試靠近麥克風。'
            });
          }
          
          // === 所有處理完成後，設置 isProcessing = false ===
          this.setProcessing(false);
          
          // return data; // 這個 return 似乎不需要
        } catch (error) {
          logger.error('處理語音錄製錯誤', LogCategory.AUDIO, error);
          // === 出錯時也要設置 isProcessing = false ===
          this.setProcessing(false);
          // return null; // 這個 return 似乎不需要
        }
      };
    } catch (error) {
      logger.error('處理錄音數據時發生錯誤', LogCategory.AUDIO, error);
      // === 出錯時也要設置 isProcessing = false ===
      this.setProcessing(false);
    }
  }

  // 播放音頻
  public playAudio(audioUrl: string): void {
    if (this.audioElement) {
      try {
        // 停止當前播放的音頻
        this.audioElement.pause();
        this.audioElement.currentTime = 0;
        
        // 設置新的音頻源
        this.audioElement.src = audioUrl;
        
        // 預加載音頻減少延遲
        this.audioElement.load();
        
        // 確保音頻完全加載後再播放
        this.audioElement.oncanplaythrough = () => {
          // 啟動口型動畫
          this.startMouthAnimation();
          
          // 標記為說話狀態
          this.isSpeaking = true;
          this.notifySpeakingStart();
          
          // 延遲極短時間後播放，確保口型同步能夠先啟動
          setTimeout(() => {
            if (this.audioElement) {
              this.audioElement.play()
                .then(() => {
                  logger.info('開始播放音頻', LogCategory.AUDIO);
                })
                .catch(error => {
                  logger.error('播放音頻錯誤', LogCategory.AUDIO, error);
                  this.isSpeaking = false;
                  this.stopMouthAnimation();
                  this.notifySpeakingEnd();
                });
            }
          }, 20);
        };
        
        // 監聽錯誤
        this.audioElement.onerror = (e) => {
          logger.error('音頻加載錯誤', LogCategory.AUDIO, e);
          this.isSpeaking = false;
          this.stopMouthAnimation();
          this.notifySpeakingEnd();
        };
      } catch (error) {
        logger.error('播放音頻時發生意外錯誤', LogCategory.AUDIO, error);
        this.isSpeaking = false;
        this.stopMouthAnimation();
        this.notifySpeakingEnd();
      }
    }
  }

  // 檢查是否正在錄音
  public isCurrentlyRecording(): boolean {
    return this.isRecording;
  }

  // 檢查是否正在說話
  public isCurrentlySpeaking(): boolean {
    return this.isSpeaking;
  }

  // 檢查是否正在處理音頻
  public isCurrentlyProcessing(): boolean {
    return this.isProcessing;
  }

  // 設置處理狀態
  private setProcessing(processing: boolean): void {
    this.isProcessing = processing;
    this.notifyAudioProcessing(processing);
  }

  // 註冊說話開始事件
  public onSpeakingStart(callback: () => void): void {
    this.onSpeakingStartCallbacks.push(callback);
  }

  // 移除說話開始事件
  public offSpeakingStart(callback: () => void): void {
    this.onSpeakingStartCallbacks = this.onSpeakingStartCallbacks.filter(cb => cb !== callback);
  }

  // 觸發說話開始事件
  private notifySpeakingStart(): void {
    this.onSpeakingStartCallbacks.forEach(callback => callback());
  }

  // 註冊說話結束事件
  public onSpeakingEnd(callback: () => void): void {
    this.onSpeakingEndCallbacks.push(callback);
  }

  // 移除說話結束事件
  public offSpeakingEnd(callback: () => void): void {
    this.onSpeakingEndCallbacks = this.onSpeakingEndCallbacks.filter(cb => cb !== callback);
  }

  // 觸發說話結束事件
  private notifySpeakingEnd(): void {
    this.onSpeakingEndCallbacks.forEach(callback => callback());
  }

  // 註冊音頻處理事件
  public onAudioProcessing(callback: (isProcessing: boolean) => void): void {
    this.onAudioProcessingCallbacks.push(callback);
  }

  // 移除音頻處理事件
  public offAudioProcessing(callback: (isProcessing: boolean) => void): void {
    this.onAudioProcessingCallbacks = this.onAudioProcessingCallbacks.filter(cb => cb !== callback);
  }

  // 觸發音頻處理事件
  private notifyAudioProcessing(isProcessing: boolean): void {
    this.onAudioProcessingCallbacks.forEach(callback => callback(isProcessing));
  }
}

// React Hook - 使用音頻服務
export function useAudioService() {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [micPermission, setMicPermission] = useState<boolean | null>(null);
  const audioService = useRef<AudioService>(AudioService.getInstance());

  useEffect(() => {
    // 獲取初始狀態
    setIsRecording(audioService.current.isCurrentlyRecording());
    setIsSpeaking(audioService.current.isCurrentlySpeaking());
    setIsProcessing(audioService.current.isCurrentlyProcessing());
    setMicPermission(audioService.current.getMicrophonePermission());

    // 說話開始事件處理
    const handleSpeakingStart = () => {
      setIsSpeaking(true);
    };

    // 說話結束事件處理
    const handleSpeakingEnd = () => {
      setIsSpeaking(false);
    };

    // 音頻處理事件處理
    const handleAudioProcessing = (processing: boolean) => {
      setIsProcessing(processing);
    };

    // 註冊事件處理
    audioService.current.onSpeakingStart(handleSpeakingStart);
    audioService.current.onSpeakingEnd(handleSpeakingEnd);
    audioService.current.onAudioProcessing(handleAudioProcessing);

    // 檢查麥克風權限
    audioService.current.checkMicrophonePermission().then(
      hasPermission => setMicPermission(hasPermission)
    );

    // 清理函數
    return () => {
      audioService.current.offSpeakingStart(handleSpeakingStart);
      audioService.current.offSpeakingEnd(handleSpeakingEnd);
      audioService.current.offAudioProcessing(handleAudioProcessing);
    };
  }, []);

  // 開始錄音
  const startRecording = async () => {
    const started = await audioService.current.startRecording();
    if (started) {
      setIsRecording(true);
    }
  };

  // 停止錄音
  const stopRecording = () => {
    const stopped = audioService.current.stopRecording();
    if (stopped) {
      setIsRecording(false);
    }
  };

  // 播放音頻
  const playAudio = (audioUrl: string) => {
    audioService.current.playAudio(audioUrl);
  };

  return {
    isRecording,
    isSpeaking,
    isProcessing,
    micPermission,
    startRecording,
    stopRecording,
    playAudio
  };
}

export default AudioService; 