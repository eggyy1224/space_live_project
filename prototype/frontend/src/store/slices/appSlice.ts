import { StateCreator } from 'zustand';

// Toast類型定義
export interface Toast {
  id: string;
  message: string;
  type: 'error' | 'success' | 'info';
  duration?: number;
}

// AppSlice 狀態與操作定義
export interface AppSlice {
  // 狀態
  activeTab: string;
  isDebugMode: boolean;
  isCameraFar: boolean;
  toasts: Toast[];
  isSettingsPanelVisible: boolean;
  isSoundEffectPanelVisible: boolean;
  isLoading: boolean;
  errorMessage: string | null;
  currentAction: string | null;
  userInteracted: boolean;
  micPermission: 'prompt' | 'granted' | 'denied';
  audioDuration: number | null;
  
  // 操作
  setActiveTab: (tab: string) => void;
  toggleDebugMode: () => void;
  setCameraDistance: (isFar: boolean) => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  toggleSettingsPanel: () => void;
  toggleSoundEffectPanel: () => void;
  setLoading: (loading: boolean) => void;
  setError: (message: string | null) => void;
  setCurrentAction: (action: string | null) => void;
  setUserInteracted: () => void;
  setMicPermission: (permission: 'prompt' | 'granted' | 'denied') => void;
  setAudioDuration: (duration: number | null) => void;
}

// 創建 App Slice
export const createAppSlice: StateCreator<AppSlice> = (set) => ({
  // 初始狀態
  activeTab: 'control', // 'control' | 'chat'
  isDebugMode: false,
  isCameraFar: true,
  toasts: [],
  isSettingsPanelVisible: false,
  isSoundEffectPanelVisible: false,
  isLoading: false,
  errorMessage: null,
  currentAction: null,
  userInteracted: false,
  micPermission: 'prompt',
  audioDuration: null,
  
  // 操作實現
  setActiveTab: (tab) => set({ activeTab: tab }),
  
  toggleDebugMode: () => set((state) => ({ 
    isDebugMode: !state.isDebugMode 
  })),
  
  setCameraDistance: (isFar) => set({ isCameraFar: isFar }),
  
  addToast: (toast) => set((state) => ({
    toasts: [...state.toasts, { ...toast, id: `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}` }]
  })),
  
  removeToast: (id) => set((state) => ({
    toasts: state.toasts.filter(toast => toast.id !== id)
  })),
  
  clearToasts: () => set({ toasts: [] }),
  
  toggleSettingsPanel: () => set((state) => ({ isSettingsPanelVisible: !state.isSettingsPanelVisible })),
  
  toggleSoundEffectPanel: () => set((state) => ({ isSoundEffectPanelVisible: !state.isSoundEffectPanelVisible })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (message) => set({ errorMessage: message }),
  
  setCurrentAction: (action) => set({ currentAction: action }),
  
  setUserInteracted: () => set({ userInteracted: true }),
  
  setMicPermission: (permission) => set({ micPermission: permission }),
  
  setAudioDuration: (duration) => set({ audioDuration: duration }),
}); 