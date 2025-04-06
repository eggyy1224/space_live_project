import { useState, useEffect, useRef } from 'react';
import WebSocketService from './WebSocketService';
import AudioService from './AudioService';
import { v4 as uuidv4 } from 'uuid';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

// 聊天消息類型
export interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
}

// 情緒狀態類型
export interface EmotionState {
  emotion: string;
  confidence: number;
}

// 聊天服務類
class ChatService {
  private static instance: ChatService;
  private wsService: WebSocketService;
  private audioService: AudioService;

  // 單例模式
  public static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  constructor() {
    this.wsService = WebSocketService.getInstance();
    this.audioService = AudioService.getInstance();
    this.setupMessageHandlers();
  }

  // 設置WebSocket消息處理器
  private setupMessageHandlers(): void {
    // 處理bot回應
    this.wsService.registerHandler('response', (data) => {
      logger.info('收到後端回應', LogCategory.CHAT, data);
      // 添加AI回應到聊天
      if (data.content) {
        logger.debug({ msg: '添加機器人文字回應', details: { content: data.content } }, LogCategory.CHAT);
        this.addMessage({
          role: 'bot',
          content: data.content
        });
      }
      
      // 更新情緒狀態
      if (data.emotion) {
        logger.debug({ msg: '更新情緒狀態', details: { emotion: data.emotion, confidence: data.confidence } }, LogCategory.CHAT);
        this.updateEmotion(data.emotion, data.confidence || 0);
      }
      
      // 處理語音回應
      if (data.hasSpeech && data.audio) {
        logger.debug('觸發音訊播放', LogCategory.CHAT);
        this.audioService.playAudio(`data:audio/mp3;base64,${data.audio}`);
      }
      
      this.setProcessing(false);
    });
    
    // 處理錯誤
    this.wsService.registerHandler('error', (data) => {
      logger.error('收到後端錯誤消息', LogCategory.CHAT, data);
      this.addMessage({
        role: 'bot',
        content: `發生錯誤: ${data.message || '未知錯誤'}`
      });
      
      this.setProcessing(false);
    });
  }

  // 獲取所有消息
  public getMessages(): ChatMessage[] {
    return useStore.getState().messages;
  }

  // 添加消息 (使用 Zustand)
  public addMessage(messageData: Omit<ChatMessage, 'id'>): void {
    const newMessage: ChatMessage = {
      ...messageData,
      id: uuidv4()
    };
    useStore.getState().addMessage(newMessage);
  }

  // 清空消息 (使用 Zustand)
  public clearMessages(): void {
    useStore.getState().setMessages([]);
  }

  // 發送文本消息
  public sendMessage(content: string): boolean {
    if (!content.trim()) {
      return false;
    }
    
    logger.info({ msg: '用戶嘗試發送消息', details: { content } }, LogCategory.CHAT);
    
    // 添加用戶消息到聊天
    this.addMessage({
      role: 'user',
      content
    });
    
    // 設置處理中狀態
    this.setProcessing(true);
    
    // 使用WebSocket發送消息
    const sent = this.wsService.sendTextMessage(content);
    
    // 如果消息發送失敗
    if (!sent) {
      logger.error('通過WebSocket發送消息失敗', LogCategory.CHAT, { content });
      this.addMessage({
        role: 'bot',
        content: '發送消息失敗，請檢查網絡連接。'
      });
      this.setProcessing(false);
    }
    
    return sent;
  }

  // 獲取處理狀態 (使用 Zustand)
  public isCurrentlyProcessing(): boolean {
    return useStore.getState().isProcessing;
  }

  // 設置處理狀態 (使用 Zustand)
  public setProcessing(processing: boolean): void {
    const currentProcessing = useStore.getState().isProcessing;
    if (currentProcessing !== processing) {
      logger.debug(`設置處理狀態: ${processing}`, LogCategory.CHAT);
      useStore.getState().setProcessing(processing);
    }
  }

  // 獲取當前情緒 (使用 Zustand)
  public getCurrentEmotion(): EmotionState {
    const { emotion, confidence } = useStore.getState().currentEmotion;
    return {
      emotion,
      confidence
    };
  }

  // 更新情緒 (使用 Zustand)
  public updateEmotion(emotion: string, confidence: number): void {
    const currentEmotion = useStore.getState().currentEmotion;
    if (currentEmotion.emotion !== emotion || currentEmotion.confidence !== confidence) {
      logger.debug(`更新情緒: ${emotion}, Confidence: ${confidence.toFixed(2)}`, LogCategory.CHAT);
      useStore.getState().setEmotion(emotion, confidence);
    }
  }
}

// React Hook - 使用聊天服務 (使用 Zustand)
export function useChatService() {
  // 直接從 Zustand 獲取聊天相關狀態
  const messages = useStore((state) => state.messages);
  const isProcessing = useStore((state) => state.isProcessing);
  const emotion = useStore((state) => state.currentEmotion);
  const [userInput, setUserInput] = useState<string>('');
  
  const chatService = useRef<ChatService>(ChatService.getInstance());

  useEffect(() => {
    // 不再需要註冊/取消註冊回調，直接從 Zustand 獲取狀態
  }, []);

  // 封裝 sendMessage 函數，使其能讀取 hook 內部狀態
  const sendMessage = () => {
    if (userInput.trim()) {
      const success = chatService.current.sendMessage(userInput);
      if (success) {
        setUserInput(''); // 發送成功後清空輸入框
      }
    }
  };

  // 封裝 clearMessages 函數
  const clearMessages = () => {
    chatService.current.clearMessages();
  };

  // 返回狀態和封裝後的函數
  return {
    messages,
    isProcessing,
    emotion,
    userInput,
    setUserInput, // 直接返回 useState 的 setter
    sendMessage, // 返回封裝後的函數
    clearMessages // 返回封裝後的函數
  };
}

export default ChatService; 