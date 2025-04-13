import { StateCreator } from 'zustand';
import { v4 as uuidv4 } from 'uuid';

// 聊天消息類型定義
export interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
  isTyping?: boolean; // 是否顯示打字機效果
  fullContent?: string; // 完整內容 (用於打字機效果)
  timestamp?: string; // 可選：消息時間戳
  audioUrl?: string; // 可選：音頻URL (如果有)
  bodyAnimationSequence?: any[]; // 可選：身體動畫序列
  speechDuration?: number; // 可選：語音持續時間（秒）
  isMurmur?: boolean; // 可選：標記是否為自言自語
}

// 情緒狀態類型定義
export interface EmotionState {
  emotion: string;
  confidence: number;
}

// ChatSlice 狀態與操作定義
export interface ChatSlice {
  // 狀態
  messages: ChatMessage[];
  isProcessing: boolean;
  currentEmotion: EmotionState;
  isChatWindowVisible: boolean;

  // 操作
  addMessage: (message: Omit<ChatMessage, 'id'>) => void;
  setMessages: (messages: ChatMessage[]) => void;
  clearMessages: () => void;
  setProcessing: (processing: boolean) => void;
  setEmotion: (emotion: string, confidence: number) => void;
  toggleChatWindow: () => void;
}

// 創建 Chat Slice
export const createChatSlice: StateCreator<ChatSlice> = (set) => ({
  // 初始狀態
  messages: [],
  isProcessing: false,
  currentEmotion: { emotion: 'neutral', confidence: 0 },
  isChatWindowVisible: false,

  // 操作實現
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, { ...message, id: uuidv4() }]
  })),
  
  setMessages: (messages) => set({ messages }),
  
  clearMessages: () => set({ messages: [] }),
  
  setProcessing: (processing) => set({ isProcessing: processing }),
  
  setEmotion: (emotion, confidence) => set({
    currentEmotion: { emotion, confidence }
  }),
  
  toggleChatWindow: () => set((state) => ({ isChatWindowVisible: !state.isChatWindowVisible })),
}); 