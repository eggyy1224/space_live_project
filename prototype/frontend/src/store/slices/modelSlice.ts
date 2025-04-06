import { StateCreator } from 'zustand';
import * as THREE from 'three';

// ModelSlice 狀態與操作定義
export interface ModelSlice {
  // 狀態
  modelUrl: string;
  modelScale: [number, number, number];
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  morphTargets: Record<string, number>;
  morphTargetDictionary: Record<string, number> | null;
  availableAnimations: string[];
  currentAnimation: string | null;
  modelLoaded: boolean;
  showSpaceBackground: boolean;
  
  // 操作：模型基本資訊
  setModelUrl: (url: string) => void;
  setModelLoaded: (loaded: boolean) => void;
  
  // 操作：模型變換（批次更新）
  setModelTransform: (
    scale?: [number, number, number],
    rotation?: [number, number, number],
    position?: [number, number, number]
  ) => void;
  
  // 操作：模型 Morph Targets（高頻更新）
  setMorphTargets: (targets: Record<string, number>) => void;
  updateMorphTarget: (key: string, value: number) => void;
  setMorphTargetDictionary: (dict: Record<string, number> | null) => void;
  
  // 操作：動畫相關
  setAvailableAnimations: (animations: string[]) => void;
  setCurrentAnimation: (animation: string | null) => void;
  
  // 操作：場景相關
  setShowSpaceBackground: (show: boolean) => void;
}

// 創建 Model Slice
export const createModelSlice: StateCreator<ModelSlice> = (set) => ({
  // 初始狀態
  modelUrl: '/models/headonly.glb',
  modelScale: [1, 1, 1],
  modelRotation: [0, 0, 0],
  modelPosition: [0, -1, 0],
  morphTargets: {},
  morphTargetDictionary: null,
  availableAnimations: [],
  currentAnimation: null,
  modelLoaded: false,
  showSpaceBackground: true,
  
  // 操作實現
  setModelUrl: (url) => set({ 
    modelUrl: url,
    // 重置相關狀態
    morphTargets: {},
    availableAnimations: [],
    currentAnimation: null,
    modelLoaded: false
  }),
  
  setModelLoaded: (loaded) => set({ modelLoaded: loaded }),
  
  // 批次更新模型變換
  setModelTransform: (scale, rotation, position) => set((state) => {
    const newState: Partial<ModelSlice> = {};
    
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
  
  // 整體設置 morphTargets (適用於從後端收到完整更新)
  setMorphTargets: (targets) => set({ morphTargets: targets }),
  
  // 單個更新 morphTarget (適用於 UI 控制)
  updateMorphTarget: (key, value) => set((state) => {
    // 移除日誌
    // console.log(`[ZUSTAND STATE] 更新MorphTarget: ${key} = ${value}`);
    
    // 創建新的狀態對象，確保觸發更新
    const newMorphTargets = {
      ...state.morphTargets,
      [key]: value
    };
    
    // 返回新狀態
    return { morphTargets: newMorphTargets };
  }),
  
  setMorphTargetDictionary: (dict) => set({ morphTargetDictionary: dict }),
  
  setAvailableAnimations: (animations) => set({ availableAnimations: animations }),
  
  setCurrentAnimation: (animation) => set({ currentAnimation: animation }),
  
  setShowSpaceBackground: (show) => set({ showSpaceBackground: show }),
}); 