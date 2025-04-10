import { StateCreator } from 'zustand';
// import { StoreApi, UseBoundStore } from 'zustand'; // 移除多餘導入
// --- 引入模型設定 ---
import { BODY_MODEL_URL } from '../../config/modelConfig';
// --- 引入結束 ---

// 定義動畫關鍵幀類型
export interface AnimationKeyframe {
  name: string;           // 必需，動畫友好名稱
  proportion: number;     // 必需，範圍 0.0 到 1.0，表示此動畫開始播放的時間點相對於總語音時長的比例
  transitionDuration?: number; // 可選，與上一個動畫混合的過渡時間，默認 0.5 秒
  loop?: boolean;         // 可選，是否循環播放此動畫直到下一個 keyframe 開始，默認 false
  weight?: number;        // 可選，動畫混合權重，範圍 0-1，默認 1
}

// BodySlice 狀態與操作定義
export interface BodySlice {
  bodyModelUrl: string;
  bodyModelLoaded: boolean;
  availableAnimations: string[];
  currentAnimation: string | null;
  suggestedAnimationName: string | null;
  animationSequence: AnimationKeyframe[]; // 新增：動畫序列
  isPlayingSequence: boolean;            // 新增：當前是否在播放序列
  currentSequenceIndex: number;          // 新增：當前播放的序列索引
  setBodyModelUrl: (url: string) => void;
  setBodyModelLoaded: (loaded: boolean) => void;
  setAvailableAnimations: (animations: string[]) => void;
  setCurrentAnimation: (animation: string | null) => void;
  setSuggestedAnimationName: (name: string | null) => void;
  setAnimationSequence: (sequence: AnimationKeyframe[]) => void; // 新增：設置動畫序列
  startSequencePlayback: () => void;                            // 新增：開始播放序列
  stopSequencePlayback: () => void;                             // 新增：停止播放序列
  playNextInSequence: (index?: number) => void;                 // 新增：播放序列中的下一個動畫
}

// 創建 Body Slice (簡化類型)
export const createBodySlice: StateCreator<BodySlice> = (set, get) => ({
  // 初始狀態
  bodyModelUrl: BODY_MODEL_URL,
  bodyModelLoaded: false,
  availableAnimations: [],
  currentAnimation: null,
  suggestedAnimationName: null,
  animationSequence: [],           // 新增：初始化為空數組
  isPlayingSequence: false,        // 新增：初始化為 false
  currentSequenceIndex: -1,        // 新增：初始化為 -1 (表示未開始)

  // 操作實現
  setBodyModelUrl: (url: string) => set({
    bodyModelUrl: url,
    availableAnimations: [],
    currentAnimation: null,
    bodyModelLoaded: false,
    suggestedAnimationName: null,
    animationSequence: [],         // 新增：重置動畫序列
    isPlayingSequence: false,      // 新增：重置播放狀態
    currentSequenceIndex: -1,      // 新增：重置序列索引
  }),

  setBodyModelLoaded: (loaded: boolean) => set({ bodyModelLoaded: loaded }),

  setAvailableAnimations: (animations: string[]) => set((state: BodySlice) => ({ // <-- 為 state 添加類型
    availableAnimations: animations,
    currentAnimation: state.currentAnimation === null && animations.includes('Idle') ? 'Idle' : (state.currentAnimation === null && animations.length > 0 ? animations[0] : state.currentAnimation)
  })),

  setCurrentAnimation: (animation: string | null) => set({ currentAnimation: animation }),

  setSuggestedAnimationName: (name: string | null) => set({ suggestedAnimationName: name }),
  
  // 新增：設置動畫序列
  setAnimationSequence: (sequence: AnimationKeyframe[]) => set({
    animationSequence: sequence,
    currentSequenceIndex: -1, // 重置序列索引
    isPlayingSequence: false  // 重置播放狀態
  }),

  // 新增：開始播放序列
  startSequencePlayback: () => set((state) => {
    if (state.animationSequence.length === 0) {
      return state; // 如果序列為空，不做任何改變
    }
    
    return {
      isPlayingSequence: true,
      currentSequenceIndex: 0, // 從第一個動畫開始
      currentAnimation: state.animationSequence[0].name // 設置當前動畫為序列中的第一個
    };
  }),

  // 新增：停止播放序列
  stopSequencePlayback: () => set((state) => {
    // 如果當前有可用的 Idle 動畫，切換回 Idle
    const idleAnimation = state.availableAnimations.includes('Idle') ? 'Idle' : null;
    
    return {
      isPlayingSequence: false,
      currentSequenceIndex: -1,
      currentAnimation: idleAnimation // 切換回 Idle 或 null
    };
  }),

  // 新增：播放序列中的下一個動畫
  playNextInSequence: (index?: number) => set((state) => {
    // 如果沒有提供索引，使用當前索引 + 1
    const nextIndex = index !== undefined ? index : state.currentSequenceIndex + 1;
    
    // 檢查下一個索引是否有效
    if (nextIndex >= state.animationSequence.length) {
      // 序列播放完畢，停止播放
      return {
        isPlayingSequence: false,
        currentSequenceIndex: -1,
        currentAnimation: state.availableAnimations.includes('Idle') ? 'Idle' : state.currentAnimation
      };
    }
    
    // 播放下一個動畫
    return {
      currentSequenceIndex: nextIndex,
      currentAnimation: state.animationSequence[nextIndex].name
    };
  })
}); 