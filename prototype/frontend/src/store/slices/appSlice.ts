import { StateCreator } from "zustand";

// Toast類型定義
export interface Toast {
  id: string;
  message: string;
  type: "error" | "success" | "info";
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
  isCharacterControlPanelVisible: boolean;
  isEnvironmentControlPanelVisible: boolean;
  isRealtimeSchedulePanelVisible: boolean;
  isTextPanelVisible: boolean;
  isSideButtonsVisible: boolean; // 控制右側按鈕的顯示/隱藏
  isLoading: boolean;
  errorMessage: string | null;
  currentAction: string | null;
  userInteracted: boolean;
  micPermission: "prompt" | "granted" | "denied";
  audioDuration: number | null;
  // 背景圖片相關狀態
  currentBackgroundPicture: string | null;
  availableBackgroundPictures: string[];
  backgroundPictureEnabled: boolean;

  // 操作
  setActiveTab: (tab: string) => void;
  toggleDebugMode: () => void;
  setCameraDistance: (isFar: boolean) => void;
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  toggleSettingsPanel: () => void;
  toggleCharacterControlPanel: () => void;
  toggleEnvironmentControlPanel: () => void;
  toggleRealtimeSchedulePanel: () => void;
  toggleTextPanel: () => void;
  toggleSideButtons: () => void; // 切換右側按鈕顯示狀態
  setLoading: (loading: boolean) => void;
  setError: (message: string | null) => void;
  setCurrentAction: (action: string | null) => void;
  setUserInteracted: () => void;
  setMicPermission: (permission: "prompt" | "granted" | "denied") => void;
  setAudioDuration: (duration: number | null) => void;
  // 背景圖片相關操作
  setCurrentBackgroundPicture: (picture: string | null) => void;
  setAvailableBackgroundPictures: (pictures: string[]) => void;
  toggleBackgroundPicture: () => void;
  setBackgroundPictureEnabled: (enabled: boolean) => void;
}

// 創建 App Slice
export const createAppSlice: StateCreator<AppSlice> = (set) => ({
  // 初始狀態
  activeTab: "control", // 'control' | 'chat'
  isDebugMode: false,
  isCameraFar: true,
  toasts: [],
  isSettingsPanelVisible: false,
  isCharacterControlPanelVisible: false,
  isEnvironmentControlPanelVisible: false,
  isRealtimeSchedulePanelVisible: false,
  isTextPanelVisible: false,
  isSideButtonsVisible: true, // 預設顯示右側按鈕
  isLoading: false,
  errorMessage: null,
  currentAction: null,
  userInteracted: false,
  micPermission: "prompt",
  audioDuration: null,
  // 背景圖片初始狀態
  currentBackgroundPicture: null,
  availableBackgroundPictures: [
    "outerspace1.png",
    "outerspace2.png",
    "outerspace3.png",
  ],
  backgroundPictureEnabled: false,

  // 操作實現
  setActiveTab: (tab) => set({ activeTab: tab }),

  toggleDebugMode: () =>
    set((state) => ({
      isDebugMode: !state.isDebugMode,
    })),

  setCameraDistance: (isFar) => set({ isCameraFar: isFar }),

  addToast: (toast) =>
    set((state) => ({
      toasts: [
        ...state.toasts,
        {
          ...toast,
          id: `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        },
      ],
    })),

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    })),

  clearToasts: () => set({ toasts: [] }),

  toggleSettingsPanel: () =>
    set((state) => ({ isSettingsPanelVisible: !state.isSettingsPanelVisible })),

  toggleCharacterControlPanel: () =>
    set((state) => ({
      isCharacterControlPanelVisible: !state.isCharacterControlPanelVisible,
    })),

  toggleEnvironmentControlPanel: () =>
    set((state) => ({
      isEnvironmentControlPanelVisible: !state.isEnvironmentControlPanelVisible,
    })),

  toggleRealtimeSchedulePanel: () =>
    set((state) => ({
      isRealtimeSchedulePanelVisible: !state.isRealtimeSchedulePanelVisible,
    })),

  toggleTextPanel: () =>
    set((state) => ({ isTextPanelVisible: !state.isTextPanelVisible })),

  toggleSideButtons: () =>
    set((state) => ({ isSideButtonsVisible: !state.isSideButtonsVisible })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (message) => set({ errorMessage: message }),

  setCurrentAction: (action) => set({ currentAction: action }),

  setUserInteracted: () => set({ userInteracted: true }),

  setMicPermission: (permission) => set({ micPermission: permission }),

  setAudioDuration: (duration) => set({ audioDuration: duration }),

  // 背景圖片操作實現
  setCurrentBackgroundPicture: (picture) =>
    set({ currentBackgroundPicture: picture }),

  setAvailableBackgroundPictures: (pictures) =>
    set({ availableBackgroundPictures: pictures }),

  toggleBackgroundPicture: () =>
    set((state) => ({
      backgroundPictureEnabled: !state.backgroundPictureEnabled,
    })),

  setBackgroundPictureEnabled: (enabled) =>
    set({ backgroundPictureEnabled: enabled }),
});
