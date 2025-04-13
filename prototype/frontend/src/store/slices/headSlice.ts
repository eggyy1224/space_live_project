import { StateCreator } from 'zustand';
import * as THREE from 'three';
// --- 引入模型設定 ---
import { HEAD_MODEL_URL } from '../../config/modelConfig'; // 使用頭部模型 URL
// --- 引入結束 ---

// HeadSlice 狀態與操作定義 (原 ModelSlice)
export interface HeadSlice {
  // 狀態
  headModelUrl: string; // 重命名
  modelScale: [number, number, number]; // 保留通用變換狀態
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  morphTargets: Record<string, number>; // 用戶手動/預設的目標
  audioLipsyncTargets: Record<string, number>; // <-- 新增：語音驅動的口型目標
  morphTargetDictionary: Record<string, number> | null;
  // availableAnimations: string[]; // 移除動畫狀態
  // currentAnimation: string | null;
  headModelLoaded: boolean; // 重命名
  showSpaceBackground: boolean; // 保留場景狀態
  
  // 操作：模型基本資訊
  setHeadModelUrl: (url: string) => void; // 重命名
  setHeadModelLoaded: (loaded: boolean) => void; // 重命名
  
  // 操作：模型變換（批次更新）
  setModelTransform: (
    scale?: [number, number, number],
    rotation?: [number, number, number],
    position?: [number, number, number]
  ) => void;
  
  // 新增：設置統一縮放 (方便UI滑動條使用)
  setUniformScale: (scale: number) => void;
  
  // 操作：模型 Morph Targets（手動/預設）
  setMorphTargets: (targets: Record<string, number>) => void;
  updateMorphTarget: (key: string, value: number) => void;
  setMorphTargetDictionary: (dict: Record<string, number> | null) => void;
  
  // 操作：語音口型 Morph Targets
  setAudioLipsyncTarget: (key: string, value: number) => void; // <-- 新增 Action
  
  // 操作：動畫相關 (移除)
  // setAvailableAnimations: (animations: string[]) => void;
  // setCurrentAnimation: (animation: string | null) => void;
  
  // 操作：場景相關
  setShowSpaceBackground: (show: boolean) => void;
}

// 創建 Head Slice (原 createModelSlice)
export const createHeadSlice: StateCreator<HeadSlice> = (set) => ({
  // 初始狀態
  headModelUrl: HEAD_MODEL_URL, // 使用導入的常數
  modelScale: [1, 1, 1],
  modelRotation: [0, 0, 0],
  modelPosition: [0, -1, 0], // 這個位置可能需要針對頭部調整
  morphTargets: {},
  audioLipsyncTargets: {}, // <-- 初始化新狀態
  morphTargetDictionary: null,
  // availableAnimations: [], // 移除
  // currentAnimation: null, // 移除
  headModelLoaded: false, // 重命名
  showSpaceBackground: true,
  
  // 操作實現
  setHeadModelUrl: (url) => set({ // 重命名 Action
    headModelUrl: url,
    // 重置相關狀態 (只重置頭部相關)
    morphTargets: {},
    audioLipsyncTargets: {}, // <-- 重置時也清空
    // availableAnimations: [], // 移除
    // currentAnimation: null, // 移除
    headModelLoaded: false // 重命名
  }),
  
  setHeadModelLoaded: (loaded) => set({ headModelLoaded: loaded }), // 重命名 Action
  
  // 批次更新模型變換
  setModelTransform: (scale, rotation, position) => set((state) => {
    const newState: Partial<HeadSlice> = {}; // 使用 HeadSlice
    
    if (scale) {
      newState.modelScale = scale;
    }
    
    if (rotation) {
      newState.modelRotation = rotation;
    }
    
    if (position) {
      newState.modelPosition = position;
    }
    
    return newState;
  }),
  
  // 新增：設置統一縮放 (所有軸使用相同縮放值)
  setUniformScale: (scale) => set((state) => ({
    modelScale: [scale, scale, scale]
  })),
  
  // 整體設置 morphTargets
  setMorphTargets: (targets) => set({ morphTargets: targets }),
  
  // 單個更新 morphTarget
  updateMorphTarget: (key, value) => set((state) => ({
    morphTargets: { ...state.morphTargets, [key]: value }
  })),
  
  setMorphTargetDictionary: (dict) => set({ morphTargetDictionary: dict }),
  
  // --- 新增 Lipsync Action 實現 ---
  setAudioLipsyncTarget: (key, value) => set((state) => ({
      // 只更新 audioLipsyncTargets 狀態
      audioLipsyncTargets: { ...state.audioLipsyncTargets, [key]: value }
  })),
  // --- 新增結束 ---
  
  // 移除動畫相關 Actions
  // setAvailableAnimations: (animations) => set({ availableAnimations: animations }),
  // setCurrentAnimation: (animation) => set({ currentAnimation: animation }),
  
  setShowSpaceBackground: (show) => set({ showSpaceBackground: show }),
}); 