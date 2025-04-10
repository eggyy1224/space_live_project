import { StateCreator } from 'zustand';
// import { StoreApi, UseBoundStore } from 'zustand'; // 移除多餘導入
// --- 引入模型設定 ---
import { BODY_MODEL_URL } from '../../config/modelConfig';
// --- 引入結束 ---
// --- 引入動畫類型 ---
import { AnimationKeyframe, PlaybackState } from '../../types/animation';
// --- 引入結束 ---

// BodySlice 狀態與操作定義
export interface BodySlice {
  bodyModelUrl: string;
  bodyModelLoaded: boolean;
  availableAnimations: string[];
  currentAnimation: string | null;
  suggestedAnimationName: string | null;
  animationSequence: AnimationKeyframe[]; // 動畫序列
  isPlayingSequence: boolean;            // 當前是否在播放序列
  currentSequenceIndex: number;          // 當前播放的序列索引
  playbackState: PlaybackState;          // 新增：播放狀態
  loopCount: number;                     // 新增：當前動畫已循環次數
  maxLoopCount: number | null;           // 新增：當前動畫最大循環次數 (null 表示無限)
  setBodyModelUrl: (url: string) => void;
  setBodyModelLoaded: (loaded: boolean) => void;
  setAvailableAnimations: (animations: string[]) => void;
  setCurrentAnimation: (animation: string | null) => void;
  setSuggestedAnimationName: (name: string | null) => void;
  setAnimationSequence: (sequence: AnimationKeyframe[]) => void;
  startSequencePlayback: () => void;
  stopSequencePlayback: () => void;
  pauseSequencePlayback: () => void;     // 新增：暫停序列播放
  resumeSequencePlayback: () => void;    // 新增：恢復序列播放
  playNextInSequence: (index?: number) => void;
  incrementLoopCount: () => void;        // 新增：增加循環計數
  resetLoopCount: (maxCount?: number | null) => void; // 新增：重置循環計數
  hasReachedMaxLoops: () => boolean;     // 新增：檢查是否達到最大循環次數
}

// 創建 Body Slice
export const createBodySlice: StateCreator<BodySlice> = (set, get) => ({
  // 初始狀態
  bodyModelUrl: BODY_MODEL_URL,
  bodyModelLoaded: false,
  availableAnimations: [],
  currentAnimation: null,
  suggestedAnimationName: null,
  animationSequence: [],
  isPlayingSequence: false,
  currentSequenceIndex: -1,
  playbackState: PlaybackState.STOPPED,   // 新增：初始為停止狀態
  loopCount: 0,                           // 新增：循環計數初始為 0
  maxLoopCount: null,                     // 新增：默認為無限循環

  // 操作實現
  setBodyModelUrl: (url: string) => set({
    bodyModelUrl: url,
    availableAnimations: [],
    currentAnimation: null,
    bodyModelLoaded: false,
    suggestedAnimationName: null,
    animationSequence: [],
    isPlayingSequence: false,
    currentSequenceIndex: -1,
    playbackState: PlaybackState.STOPPED, // 重置播放狀態
    loopCount: 0,                         // 重置循環計數
    maxLoopCount: null,                   // 重置最大循環次數
  }),

  setBodyModelLoaded: (loaded: boolean) => set({ bodyModelLoaded: loaded }),

  setAvailableAnimations: (animations: string[]) => set((state: BodySlice) => ({
    availableAnimations: animations,
    currentAnimation: state.currentAnimation === null && animations.includes('Idle') ? 'Idle' : (state.currentAnimation === null && animations.length > 0 ? animations[0] : state.currentAnimation)
  })),

  setCurrentAnimation: (animation: string | null) => set((state) => ({
    currentAnimation: animation,
    // 如果是手動切換動畫，停止序列播放
    isPlayingSequence: animation === null ? false : state.isPlayingSequence,
    // 重置循環計數
    loopCount: 0,
    // 如果當前在序列中，獲取對應的最大循環次數
    maxLoopCount: state.isPlayingSequence && state.currentSequenceIndex >= 0 && state.currentSequenceIndex < state.animationSequence.length 
      ? (state.animationSequence[state.currentSequenceIndex].loopCount || null)
      : null
  })),

  setSuggestedAnimationName: (name: string | null) => set({ suggestedAnimationName: name }),
  
  // 設置動畫序列
  setAnimationSequence: (sequence: AnimationKeyframe[]) => set({
    animationSequence: sequence,
    currentSequenceIndex: -1,
    isPlayingSequence: false,
    playbackState: PlaybackState.STOPPED,
    loopCount: 0,
    maxLoopCount: null
  }),

  // 開始播放序列
  startSequencePlayback: () => set((state) => {
    if (state.animationSequence.length === 0) {
      return state; // 如果序列為空，不做任何改變
    }
    
    // 獲取第一個動畫的最大循環次數
    const maxLoops = state.animationSequence[0].loopCount || null;
    
    return {
      isPlayingSequence: true,
      currentSequenceIndex: 0,
      currentAnimation: state.animationSequence[0].name,
      playbackState: PlaybackState.PLAYING,
      loopCount: 0,         // 重置循環計數
      maxLoopCount: maxLoops // 設置最大循環次數
    };
  }),

  // 停止播放序列
  stopSequencePlayback: () => set((state) => {
    // 如果當前有可用的 Idle 動畫，切換回 Idle
    const idleAnimation = state.availableAnimations.includes('Idle') ? 'Idle' : null;
    
    return {
      isPlayingSequence: false,
      currentSequenceIndex: -1,
      currentAnimation: idleAnimation,
      playbackState: PlaybackState.STOPPED,
      loopCount: 0,
      maxLoopCount: null
    };
  }),
  
  // 新增：暫停序列播放
  pauseSequencePlayback: () => set((state) => {
    if (!state.isPlayingSequence || state.playbackState !== PlaybackState.PLAYING) {
      return state; // 如果沒有播放序列或已經暫停，不做任何改變
    }
    
    return {
      playbackState: PlaybackState.PAUSED
    };
  }),
  
  // 新增：恢復序列播放
  resumeSequencePlayback: () => set((state) => {
    if (!state.isPlayingSequence || state.playbackState !== PlaybackState.PAUSED) {
      return state; // 如果沒有播放序列或沒有暫停，不做任何改變
    }
    
    return {
      playbackState: PlaybackState.PLAYING
    };
  }),

  // 播放序列中的下一個動畫
  playNextInSequence: (index?: number) => set((state) => {
    // 如果沒有提供索引，使用當前索引 + 1
    const nextIndex = index !== undefined ? index : state.currentSequenceIndex + 1;
    
    // 檢查下一個索引是否有效
    if (nextIndex >= state.animationSequence.length) {
      // 序列播放完畢，停止播放
      return {
        isPlayingSequence: false,
        currentSequenceIndex: -1,
        currentAnimation: state.availableAnimations.includes('Idle') ? 'Idle' : state.currentAnimation,
        playbackState: PlaybackState.STOPPED,
        loopCount: 0,
        maxLoopCount: null
      };
    }
    
    // 獲取下一個動畫的最大循環次數
    const maxLoops = state.animationSequence[nextIndex].loopCount || null;
    
    // 播放下一個動畫
    return {
      currentSequenceIndex: nextIndex,
      currentAnimation: state.animationSequence[nextIndex].name,
      loopCount: 0,         // 重置循環計數
      maxLoopCount: maxLoops // 設置最大循環次數
    };
  }),
  
  // 新增：增加循環計數
  incrementLoopCount: () => set((state) => ({
    loopCount: state.loopCount + 1
  })),
  
  // 新增：重置循環計數
  resetLoopCount: (maxCount?: number | null) => set({
    loopCount: 0,
    maxLoopCount: maxCount !== undefined ? maxCount : null
  }),
  
  // 新增：檢查是否達到最大循環次數
  hasReachedMaxLoops: () => {
    const state = get();
    return state.maxLoopCount !== null && state.loopCount >= state.maxLoopCount;
  }
}); 