import { StateCreator } from 'zustand';
// import { StoreApi, UseBoundStore } from 'zustand'; // 移除多餘導入
// --- 引入模型設定 ---
import { BODY_MODEL_URL } from '../../config/modelConfig';
// --- 引入結束 ---

// BodySlice 狀態與操作定義
export interface BodySlice {
  bodyModelUrl: string;
  bodyModelLoaded: boolean;
  availableAnimations: string[];
  currentAnimation: string | null;
  suggestedAnimationName: string | null;
  setBodyModelUrl: (url: string) => void;
  setBodyModelLoaded: (loaded: boolean) => void;
  setAvailableAnimations: (animations: string[]) => void;
  setCurrentAnimation: (animation: string | null) => void;
  setSuggestedAnimationName: (name: string | null) => void;
}

// 創建 Body Slice (簡化類型)
export const createBodySlice: StateCreator<BodySlice> = (set) => ({
  // 初始狀態
  bodyModelUrl: BODY_MODEL_URL,
  bodyModelLoaded: false,
  availableAnimations: [],
  currentAnimation: null,
  suggestedAnimationName: null,

  // 操作實現
  setBodyModelUrl: (url: string) => set({
    bodyModelUrl: url,
    availableAnimations: [],
    currentAnimation: null,
    bodyModelLoaded: false,
    suggestedAnimationName: null,
  }),

  setBodyModelLoaded: (loaded: boolean) => set({ bodyModelLoaded: loaded }),

  setAvailableAnimations: (animations: string[]) => set((state: BodySlice) => ({ // <-- 為 state 添加類型
    availableAnimations: animations,
    currentAnimation: state.currentAnimation === null && animations.includes('Idle') ? 'Idle' : (state.currentAnimation === null && animations.length > 0 ? animations[0] : state.currentAnimation)
  })),

  setCurrentAnimation: (animation: string | null) => set({ currentAnimation: animation }),

  setSuggestedAnimationName: (name: string | null) => set({ suggestedAnimationName: name }),
}); 