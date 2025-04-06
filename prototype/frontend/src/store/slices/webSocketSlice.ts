import { StateCreator } from 'zustand';

// WebSocketSlice 狀態與操作定義
export interface WebSocketSlice {
  // 狀態
  isConnected: boolean;

  // 操作
  setConnected: (status: boolean) => void;
}

// 創建 WebSocket Slice
export const createWebSocketSlice: StateCreator<WebSocketSlice> = (set) => ({
  // 初始狀態
  isConnected: false,

  // 操作實現
  setConnected: (status: boolean) => set({ isConnected: status }),
}); 