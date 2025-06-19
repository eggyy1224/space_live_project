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
  
  // 表情同步狀態 (與 HeadSlice 獨立，但可以同步)
  characterMorphTargets: Record<string, number>; // 角色專屬的手動表情
  characterAudioLipsyncTargets: Record<string, number>; // 角色專屬的語音口型
  characterMorphTargetDictionary: Record<string, number> | null;
  
  // 操作方法
  setCharacterModelLoaded: (loaded: boolean) => void;
  setCharacterVisible: (visible: boolean) => void;
  setCharacterPosition: (position: [number, number, number]) => void;
  setCharacterScale: (scale: number) => void;
  setCharacterRotation: (rotation: [number, number, number]) => void;
  setAvailableCharacterAnimations: (animations: string[]) => void;
  setCurrentCharacterAnimation: (animation: string | null) => void;
  setCharacterMorphTargetDictionary: (dictionary: Record<string, number> | null) => void;
  
  // 表情同步操作方法
  setCharacterMorphTargets: (targets: Record<string, number>) => void;
  updateCharacterMorphTarget: (key: string, value: number) => void;
  resetCharacterMorphTargets: () => void;
  setCharacterAudioLipsyncTarget: (key: string, value: number) => void;
  
  resetCharacterTransform: () => void;
}

// 創建 Character Slice
export const createCharacterSlice: StateCreator<CharacterSlice> = (set, get) => ({
  // 初始狀態
  characterModelLoaded: false,
  characterVisible: true,
  characterPosition: [2, 0, 0], // 放在頭部旁邊
  characterScale: 15,
  characterRotation: [0, 0, 0],
  
  // 動畫狀態
  availableCharacterAnimations: CHARACTER_ANIMATIONS,
  currentCharacterAnimation: "Tpose", // 默認姿勢
  
  // 表情同步狀態
  characterMorphTargets: {},
  characterAudioLipsyncTargets: {},
  characterMorphTargetDictionary: null,
  
  // 操作實現
  setCharacterModelLoaded: (loaded: boolean) => set({ characterModelLoaded: loaded }),
  
  setCharacterVisible: (visible: boolean) => set({ characterVisible: visible }),
  
  setCharacterPosition: (position: [number, number, number]) => set({ characterPosition: position }),
  
  setCharacterScale: (scale: number) => set({ characterScale: scale }),
  
  setCharacterRotation: (rotation: [number, number, number]) => set({ characterRotation: rotation }),
  
  setAvailableCharacterAnimations: (animations: string[]) => set({ availableCharacterAnimations: animations }),
  
  setCurrentCharacterAnimation: (animation: string | null) => set({ currentCharacterAnimation: animation }),
  
  setCharacterMorphTargetDictionary: (dictionary: Record<string, number> | null) => set({ characterMorphTargetDictionary: dictionary }),
  
  // 表情同步操作實現
  setCharacterMorphTargets: (targets: Record<string, number>) => set({ characterMorphTargets: targets }),
  
  updateCharacterMorphTarget: (key: string, value: number) => set((state) => ({
    characterMorphTargets: { ...state.characterMorphTargets, [key]: value }
  })),
  
  resetCharacterMorphTargets: () => set({ characterMorphTargets: {} }),
  
  setCharacterAudioLipsyncTarget: (key: string, value: number) => set((state) => ({
    characterAudioLipsyncTargets: { ...state.characterAudioLipsyncTargets, [key]: value }
  })),
  
  resetCharacterTransform: () => set({
    characterPosition: [2, 0, 0],
    characterScale: 15,
    characterRotation: [0, 0, 0]
  })
}); 