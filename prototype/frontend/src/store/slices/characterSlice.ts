import { StateCreator } from 'zustand';

// Character 模型數據 (基於 character0611.glb_analysis.json)
export const CHARACTER_MODEL_URL = '/models/character0611.glb';
export const CHARACTER_ANIMATIONS = [
  "運動2", "漂浮", "運動1", "Tpose", "不穩", "划手機", 
  "漂浮2", "臥躺", "舞步1", "舞步2", "舞步3", "飛1", "飛2"
];

// CharacterSlice 狀態與操作定義
export interface CharacterSlice {
  // 模型相關
  characterModelLoaded: boolean;
  characterVisible: boolean;
  characterPosition: [number, number, number];
  characterScale: number;
  characterRotation: [number, number, number];
  
  // 動畫相關
  availableCharacterAnimations: string[];
  currentCharacterAnimation: string | null;
  
  // 變形目標相關
  morphTargets: Record<string, number>;
  morphTargetDictionary: Record<string, number> | null;
  
  // 操作方法
  setCharacterModelLoaded: (loaded: boolean) => void;
  setCharacterVisible: (visible: boolean) => void;
  setCharacterPosition: (position: [number, number, number]) => void;
  setCharacterScale: (scale: number) => void;
  setCharacterRotation: (rotation: [number, number, number]) => void;
  setAvailableCharacterAnimations: (animations: string[]) => void;
  setCurrentCharacterAnimation: (animation: string | null) => void;
  setCharacterMorphTargets: (targets: Record<string, number>) => void;
  setCharacterMorphTargetDictionary: (dictionary: Record<string, number> | null) => void;
  updateCharacterMorphTarget: (name: string, value: number) => void;
  resetCharacterMorphTargets: () => void;
  resetCharacterTransform: () => void;
}

// 創建 Character Slice
export const createCharacterSlice: StateCreator<CharacterSlice> = (set, get) => ({
  // 初始狀態
  characterModelLoaded: false,
  characterVisible: true,
  characterPosition: [2, 0, 0], // 放在頭部旁邊
  characterScale: 1,
  characterRotation: [0, 0, 0],
  
  // 動畫狀態
  availableCharacterAnimations: CHARACTER_ANIMATIONS,
  currentCharacterAnimation: "Tpose", // 默認姿勢
  
  // 變形目標狀態
  morphTargets: {},
  morphTargetDictionary: null,
  
  // 操作實現
  setCharacterModelLoaded: (loaded: boolean) => set({ characterModelLoaded: loaded }),
  
  setCharacterVisible: (visible: boolean) => set({ characterVisible: visible }),
  
  setCharacterPosition: (position: [number, number, number]) => set({ characterPosition: position }),
  
  setCharacterScale: (scale: number) => set({ characterScale: scale }),
  
  setCharacterRotation: (rotation: [number, number, number]) => set({ characterRotation: rotation }),
  
  setAvailableCharacterAnimations: (animations: string[]) => set({ availableCharacterAnimations: animations }),
  
  setCurrentCharacterAnimation: (animation: string | null) => set({ currentCharacterAnimation: animation }),
  
  setCharacterMorphTargets: (targets: Record<string, number>) => set({ morphTargets: targets }),
  
  setCharacterMorphTargetDictionary: (dictionary: Record<string, number> | null) => set({ morphTargetDictionary: dictionary }),
  
  updateCharacterMorphTarget: (name: string, value: number) => set((state) => ({
    morphTargets: {
      ...state.morphTargets,
      [name]: value
    }
  })),
  
  resetCharacterMorphTargets: () => set({ morphTargets: {} }),
  
  resetCharacterTransform: () => set({
    characterPosition: [2, 0, 0],
    characterScale: 1,
    characterRotation: [0, 0, 0]
  })
}); 