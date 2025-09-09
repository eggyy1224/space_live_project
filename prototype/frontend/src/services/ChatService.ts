import { useEffect, useRef } from 'react';
import WebSocketService from './WebSocketService';
import AudioService from './AudioService';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

// ---> 添加一個全局變數來存儲開始時間 <---
let messageSendTimestamp: number | null = null;

// 消息類型定義
export interface MessageType {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: string;
  audioUrl?: string;
  isError?: boolean;
  isTyping?: boolean;
  fullContent?: string;
  speechDuration?: number;
}

// 後端API URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

// 聊天服務類
class ChatService {
  private static instance: ChatService;
  private websocket: WebSocketService;
  private audioService: AudioService;
  private playbackQueue: { id: string; url: string; interrupt?: boolean }[] = [];
  private currentClip: { id: string; url: string } | null = null;
  private waitingForAck = false;
  // ---> 添加一個映射來存儲每個請求的開始時間 <---
  private messageTimestamps: Map<string, number> = new Map();
  
  // 單例模式
  public static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }
  
  // 建構子
  constructor() {
    // 初始化相關服務
    this.websocket = WebSocketService.getInstance();
    this.audioService = AudioService.getInstance();

    // 註冊 WebSocket 消息處理器
    this.setupMessageHandlers();
  }

  private enqueueAudioClip(clip: { id: string; url: string; interrupt?: boolean }): void {
    if (clip.interrupt) {
      this.audioService.stopPlayback();
      this.playbackQueue = [];
      this.currentClip = null;
      this.waitingForAck = false;
    }
    this.playbackQueue.push(clip);
    this.processPlaybackQueue();
  }

  private async processPlaybackQueue(): Promise<void> {
    if (this.currentClip || this.waitingForAck) return;
    const clip = this.playbackQueue.shift();
    if (!clip) return;
    this.currentClip = { id: clip.id, url: clip.url };
    this.waitingForAck = true;
    try {
      // 防止瀑布式錯誤：為播放加入超時保護，避免卡死在 waitingForAck 狀態
      const PLAYBACK_TIMEOUT_MS = 15000; // 15 秒超時（含慢網路、載入延遲的餘裕）
      await Promise.race([
        this.audioService.playAudio(clip.url),
        new Promise<void>((_, reject) => {
          const timer = setTimeout(() => {
            // 超時：嘗試停止播放並釋放資源，優雅略過此段
            try { this.audioService.stopPlayback(); } catch { /* no-op */ }
            reject(new Error(`Playback timeout after ${PLAYBACK_TIMEOUT_MS}ms for clip ${clip.id}`));
          }, PLAYBACK_TIMEOUT_MS);
          // 透過 finally 清掉計時器（在 Promise.race 外處理）
          // 無法於此處清，改在 finally 中統一處理
          (this as any)._playbackTimeoutTimer = timer;
        })
      ]);
    } catch (err) {
      logger.error('音頻播放失敗', LogCategory.CHAT, err);
    } finally {
      // 清掉可能存在的超時計時器
      const t = (this as any)._playbackTimeoutTimer as number | undefined;
      if (t) {
        clearTimeout(t);
        (this as any)._playbackTimeoutTimer = undefined;
      }
      this.websocket.sendMessage({ type: 'playback_ack', id: clip.id });
      this.currentClip = null;
      this.waitingForAck = false;
      this.processPlaybackQueue();
    }
  }
  
  // 設置 WebSocket 消息處理器
  private setupMessageHandlers(): void {
    // 註冊處理聊天消息的回調
    this.websocket.registerHandler('chat-message', (data: any) => {
      logger.info('收到聊天消息', LogCategory.CHAT, data);
      
      // ---> 計算並記錄響應時間 <---
      const receiveTime = performance.now();
      // 嘗試從 message data 中獲取 user message id (如果後端能夠回傳的話)
      // 假設 message.id 是機器人回覆的 ID，我們需要某種方式關聯到用戶發送的消息
      // 暫時我們先使用全局變數的方式，但這在併發請求下不準確
      if (messageSendTimestamp) {
          const duration = receiveTime - messageSendTimestamp;
          logger.info(`[Performance] Frontend E2E response time: ${duration.toFixed(2)} ms`, LogCategory.PERFORMANCE); // 使用新的 LogCategory
          messageSendTimestamp = null; // 重置時間戳
      }
      // <--- 計時結束 --- >
      
      // ---> 收到回覆後，設置 isProcessing 為 false <---
      useStore.getState().setProcessing(false);
      // <--- 狀態更新結束 --- >
      
      if (!data || !data.message) {
        logger.warn('收到的聊天消息格式無效', LogCategory.CHAT);
        return;
      }
      
      // 將收到的消息添加到聊天歷史
      let message = data.message;
      
      // 如果是機器人消息並且不是錯誤消息，添加打字機效果
      if (message.role === 'bot' && !message.isError) {
        const content = message.content;
        
        // 添加打字機效果屬性
        message.isTyping = true;
        message.fullContent = content;
        
        // 從消息中提取語音持續時間（如果有）
        // 關鍵修改：確保正確設置 speechDuration，這對於文本-音頻同步至關重要
        if (data.speechDuration) {
          message.speechDuration = data.speechDuration;
          logger.info(`語音持續時間: ${data.speechDuration}秒`, LogCategory.CHAT);
        } else if (message.audioUrl) {
          // 如果沒有明確提供持續時間但有音頻，使用更準確的估算值
          // 改進估算算法，根據文字長度和複雜度
          const estimatedDuration = Math.max(1, content.length * 0.08 + 0.5);
          message.speechDuration = estimatedDuration;
          logger.info(`估算語音持續時間: ${estimatedDuration}秒`, LogCategory.CHAT);
        }
      }
      
      // 更新最近消息（用於顯示情緒等）
      useStore.getState().setLastJsonMessage(data);

      // 將目前的語音文字存入 Zustand，供背景顯示
      if (message.role === 'bot') {
        useStore.getState().setSpeechText(message.content);
      }

      this.addMessage(message);
      
      // 關鍵修改：確保在 addMessage 之後再安排音頻播放，這樣文本和音頻能更好地同步
      if (message.audioUrl && message.role === 'bot') {
        // 添加一個小延遲讓打字機效果先開始
        setTimeout(() => {
          const fullAudioUrl = `${API_BASE_URL}${message.audioUrl}`;
          this.enqueueAudioClip({ id: message.id, url: fullAudioUrl });
        }, 50);
      }
    });

    this.websocket.registerHandler('play-audio', (data: any) => {
      if (data && data.url && data.id) {
        const fullUrl = `${API_BASE_URL}${data.url}`;
        this.enqueueAudioClip({ id: data.id, url: fullUrl, interrupt: data.interrupt });
      }
    });
    
    // 註冊處理歷史消息的回調
    this.websocket.registerHandler('chat-history', (data: any) => {
      logger.info('收到聊天歷史', LogCategory.CHAT, data);
      
      if (!data || !Array.isArray(data.messages)) {
        logger.warn('收到的聊天歷史格式無效', LogCategory.CHAT);
        return;
      }
      
      // 使用 Zustand 設置消息歷史
      useStore.getState().setMessages(data.messages);
    });
    
    // 註冊處理錯誤消息的回調
    this.websocket.registerHandler('error', (data: any) => {
      logger.error('收到錯誤消息', LogCategory.CHAT, data);
      
      // ---> 收到錯誤後，也設置 isProcessing 為 false <---
      useStore.getState().setProcessing(false);
      // <--- 狀態更新結束 --- >
      
      if (!data || !data.message) {
        logger.warn('收到的錯誤消息格式無效', LogCategory.CHAT);
        return;
      }
      
      // 顯示錯誤消息
      this.showErrorMessage(data.message);
    });
  }
  
  // 發送聊天消息
  public sendMessage(text: string): void {
    if (!text || text.trim() === '') {
      logger.warn('嘗試發送空消息', LogCategory.CHAT);
      return;
    }
    
    logger.info(`發送消息: ${text}`, LogCategory.CHAT);
    
    // ---> 發送前，設置 isProcessing 為 true <---
    useStore.getState().setProcessing(true);
    // <--- 狀態更新結束 --- >
    
    // ---> 記錄發送時間戳 <---
    messageSendTimestamp = performance.now();
    // <--- 時間戳記錄結束 --- >
    
    // 如果WebSocket已連接，通過WebSocket發送
    if (this.websocket.isConnected()) {
      // 使用正確的方法發送文本消息
      const success = this.websocket.sendTextMessage(text);
      
      // 如果發送失敗，提示用戶
      if (!success) {
        logger.error('消息發送失敗', LogCategory.CHAT);
        // ---> 發送失敗後，設置 isProcessing 為 false <---
        useStore.getState().setProcessing(false);
        // <--- 狀態更新結束 --- >
        this.showErrorMessage('消息發送失敗，請檢查網絡連接');
      }
    } else {
      // WebSocket未連接，顯示錯誤
      logger.error('WebSocket未連接，無法發送消息', LogCategory.CHAT);
      // ---> 連接失敗後，設置 isProcessing 為 false <---
      useStore.getState().setProcessing(false);
      // <--- 狀態更新結束 --- >
      this.showErrorMessage('網絡連接失敗，請檢查您的網絡連接並重試');
      
      // 嘗試重新連接
      this.websocket.connect();
    }
  }
  
  // 添加消息到聊天歷史
  private addMessage(message: MessageType): void {
    // 使用 Zustand 添加消息
    useStore.getState().addMessage(message);
  }
  
  // 清空聊天消息
  public clearMessages(): void {
    // 使用 Zustand 清空消息
    useStore.getState().clearMessages();
    
    // 通知後端清空聊天歷史（如果需要）
    if (this.websocket.isConnected()) {
      this.websocket.sendMessage({
        type: 'clear-chat'
      });
    }
  }
  
  // 顯示錯誤消息
  private showErrorMessage(errorText: string): void {
    // 創建錯誤消息
    const errorMessage: MessageType = {
      id: `error-${Date.now()}`,
      role: 'bot',
      content: `錯誤: ${errorText}`,
      timestamp: new Date().toISOString(),
      isError: true
    };
    
    // 添加到聊天歷史
    this.addMessage(errorMessage);
  }
  
  // 請求表達預設列表
  public async requestExpressionPresets(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/presets`);
      
      if (!response.ok) {
        throw new Error(`API 請求失敗: ${response.status}`);
      }
      
      const data = await response.json();
      logger.info('獲取表達預設成功', LogCategory.CHAT, data);
      
      // 如果資料中包含表情預設，可以考慮將其添加到 store 中
      // 注意：目前的 chatSlice 不包含 setExpressionPresets 方法
      // 如果需要添加此功能，應添加到相應的 slice 中
      
      return data;
    } catch (error) {
      logger.error('獲取表達預設失敗', LogCategory.CHAT, error);
      return { presets: [] };
    }
  }
}

// React Hook - 使用聊天服務
export function useChatService() {
  // 獲取 Zustand 狀態
  const messages = useStore((state) => state.messages);
  const addMessage = useStore((state) => state.addMessage); // <-- 獲取 addMessage
  
  // 獲取服務實例
  const chatService = useRef<ChatService>(ChatService.getInstance());
  
  // 在組件掛載時獲取表達預設
  useEffect(() => {
    chatService.current.requestExpressionPresets();
  }, []);
  
  // 封裝方法
  const sendMessage = (text: string) => {
    // ---> 將用戶消息添加到 store (UI 會立即顯示) <---
    const userMessage: MessageType = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: text,
        timestamp: new Date().toISOString()
    };
    addMessage(userMessage); // <-- 在發送前添加到 store
    // ---> 添加結束 <---
    
    // 調用服務發送消息到後端
    chatService.current.sendMessage(text);
  };
  
  const clearMessages = () => {
    chatService.current.clearMessages();
  };
  
  // 返回狀態和方法
  return {
    messages,
    sendMessage,
    clearMessages
  };
}

export default ChatService; 
