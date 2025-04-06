import { StateCreator } from 'zustand';

// AppSlice 狀態與操作定義
export interface AppSlice {
  // 狀態
  activeTab: string;
  isDebugMode: boolean;
  isCameraFar: boolean;
  
  // 操作
  setActiveTab: (tab: string) => void;
  toggleDebugMode: () => void;
  setCameraDistance: (isFar: boolean) => void;
}

// 創建 App Slice
export const createAppSlice: StateCreator<AppSlice> = (set) => ({
  // 初始狀態
  activeTab: 'control', // 'control' | 'chat'
  isDebugMode: false,
  isCameraFar: true,
  
  // 操作實現
  setActiveTab: (tab) => set({ activeTab: tab }),
  
  toggleDebugMode: () => set((state) => ({ 
    isDebugMode: !state.isDebugMode 
  })),
  
  setCameraDistance: (isFar) => set({ isCameraFar: isFar }),
}); 