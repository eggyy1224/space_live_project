import { useState, useEffect, useRef } from 'react';
import WebSocketService from './WebSocketService';
import AudioService from './AudioService';

// 聊天消息類型
export interface ChatMessage {
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
  private messages: ChatMessage[] = [];
  private isProcessing: boolean = false;
  private currentEmotion: string = 'neutral';
  private emotionConfidence: number = 0;
  private wsService: WebSocketService;
  private audioService: AudioService;
  private onMessagesUpdateCallbacks: ((messages: ChatMessage[]) => void)[] = [];
  private onProcessingChangeCallbacks: ((isProcessing: boolean) => void)[] = [];
  private onEmotionUpdateCallbacks: ((emotion: EmotionState) => void)[] = [];

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
      // 添加AI回應到聊天
      if (data.content) {
        this.addMessage({
          role: 'bot',
          content: data.content
        });
      }
      
      // 更新情緒狀態
      if (data.emotion) {
        this.updateEmotion(data.emotion, data.confidence || 0);
      }
      
      // 處理語音回應
      if (data.hasSpeech && data.audio) {
        this.audioService.playAudio(`data:audio/mp3;base64,${data.audio}`);
      }
      
      this.setProcessing(false);
    });
    
    // 處理錯誤
    this.wsService.registerHandler('error', (data) => {
      this.addMessage({
        role: 'bot',
        content: `發生錯誤: ${data.message}`
      });
      
      this.setProcessing(false);
    });
  }

  // 獲取所有消息
  public getMessages(): ChatMessage[] {
    return [...this.messages];
  }

  // 添加消息
  public addMessage(message: ChatMessage): void {
    this.messages = [...this.messages, message];
    this.notifyMessagesUpdate();
  }

  // 清空消息
  public clearMessages(): void {
    this.messages = [];
    this.notifyMessagesUpdate();
  }

  // 發送文本消息
  public sendMessage(content: string): boolean {
    if (!content.trim()) {
      return false;
    }
    
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
      this.addMessage({
        role: 'bot',
        content: '發送消息失敗，請檢查網絡連接。'
      });
      this.setProcessing(false);
    }
    
    return sent;
  }

  // 獲取處理狀態
  public isCurrentlyProcessing(): boolean {
    return this.isProcessing;
  }

  // 設置處理狀態
  public setProcessing(processing: boolean): void {
    this.isProcessing = processing;
    this.notifyProcessingChange();
  }

  // 獲取當前情緒
  public getCurrentEmotion(): EmotionState {
    return {
      emotion: this.currentEmotion,
      confidence: this.emotionConfidence
    };
  }

  // 更新情緒
  public updateEmotion(emotion: string, confidence: number): void {
    this.currentEmotion = emotion;
    this.emotionConfidence = confidence;
    this.notifyEmotionUpdate();
  }

  // 註冊消息更新事件
  public onMessagesUpdate(callback: (messages: ChatMessage[]) => void): void {
    this.onMessagesUpdateCallbacks.push(callback);
    
    // 立即調用回調，提供當前狀態
    callback([...this.messages]);
  }

  // 移除消息更新事件
  public offMessagesUpdate(callback: (messages: ChatMessage[]) => void): void {
    this.onMessagesUpdateCallbacks = this.onMessagesUpdateCallbacks.filter(cb => cb !== callback);
  }

  // 觸發消息更新事件
  private notifyMessagesUpdate(): void {
    const messagesCopy = [...this.messages];
    this.onMessagesUpdateCallbacks.forEach(callback => callback(messagesCopy));
  }

  // 註冊處理狀態變更事件
  public onProcessingChange(callback: (isProcessing: boolean) => void): void {
    this.onProcessingChangeCallbacks.push(callback);
    
    // 立即調用回調，提供當前狀態
    callback(this.isProcessing);
  }

  // 移除處理狀態變更事件
  public offProcessingChange(callback: (isProcessing: boolean) => void): void {
    this.onProcessingChangeCallbacks = this.onProcessingChangeCallbacks.filter(cb => cb !== callback);
  }

  // 觸發處理狀態變更事件
  private notifyProcessingChange(): void {
    this.onProcessingChangeCallbacks.forEach(callback => callback(this.isProcessing));
  }

  // 註冊情緒更新事件
  public onEmotionUpdate(callback: (emotion: EmotionState) => void): void {
    this.onEmotionUpdateCallbacks.push(callback);
    
    // 立即調用回調，提供當前狀態
    callback({
      emotion: this.currentEmotion,
      confidence: this.emotionConfidence
    });
  }

  // 移除情緒更新事件
  public offEmotionUpdate(callback: (emotion: EmotionState) => void): void {
    this.onEmotionUpdateCallbacks = this.onEmotionUpdateCallbacks.filter(cb => cb !== callback);
  }

  // 觸發情緒更新事件
  private notifyEmotionUpdate(): void {
    this.onEmotionUpdateCallbacks.forEach(callback => callback({
      emotion: this.currentEmotion,
      confidence: this.emotionConfidence
    }));
  }
}

// React Hook - 使用聊天服務
export function useChatService() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [emotion, setEmotion] = useState<EmotionState>({ emotion: 'neutral', confidence: 0 });
  const [userInput, setUserInput] = useState<string>('');
  const chatService = useRef<ChatService>(ChatService.getInstance());

  useEffect(() => {
    // 消息更新處理
    const handleMessagesUpdate = (updatedMessages: ChatMessage[]) => {
      setMessages(updatedMessages);
    };
    
    // 處理狀態變更處理
    const handleProcessingChange = (processing: boolean) => {
      setIsProcessing(processing);
    };
    
    // 情緒更新處理
    const handleEmotionUpdate = (updatedEmotion: EmotionState) => {
      setEmotion(updatedEmotion);
    };
    
    // 註冊事件處理
    chatService.current.onMessagesUpdate(handleMessagesUpdate);
    chatService.current.onProcessingChange(handleProcessingChange);
    chatService.current.onEmotionUpdate(handleEmotionUpdate);
    
    // 清理函數
    return () => {
      chatService.current.offMessagesUpdate(handleMessagesUpdate);
      chatService.current.offProcessingChange(handleProcessingChange);
      chatService.current.offEmotionUpdate(handleEmotionUpdate);
    };
  }, []);

  // 發送消息
  const sendMessage = () => {
    if (userInput.trim()) {
      const success = chatService.current.sendMessage(userInput);
      if (success) {
        setUserInput('');
      }
    }
  };

  // 清空消息
  const clearMessages = () => {
    chatService.current.clearMessages();
  };

  return {
    messages,
    isProcessing,
    emotion,
    userInput,
    setUserInput,
    sendMessage,
    clearMessages
  };
}

export default ChatService; 