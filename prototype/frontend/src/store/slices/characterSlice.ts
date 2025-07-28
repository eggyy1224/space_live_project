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
  
  // 動畫混合相關 (新增)
  animationMixMode: boolean; // 是否在混合模式
  currentAnimationMix: Array<{
    name: string;
    weight: number;
    loop: boolean;
    speed: number;
  }>; // 當前混合的動畫配置
  animationMixBlendMode: 'normal' | 'additive' | 'override';
  
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
  
  // 動畫混合操作方法 (新增)
  setAnimationMixMode: (enabled: boolean) => void;
  setCurrentAnimationMix: (animations: Array<{
    name: string;
    weight: number;
    loop: boolean;
    speed: number;
  }>) => void;
  setAnimationMixBlendMode: (mode: 'normal' | 'additive' | 'override') => void;
  updateAnimationMixWeight: (animationName: string, weight: number) => void;
  clearAnimationMix: () => void;
  
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
  characterPosition: [0, 0, 0], // 主要角色移動到原點位置
  characterScale: 0.1,
  characterRotation: [0, Math.PI, 0],
  
  // 動畫狀態
  availableCharacterAnimations: CHARACTER_ANIMATIONS,
  currentCharacterAnimation: "Tpose", // 默認姿勢
  
  // 動畫混合相關 (新增)
  animationMixMode: false,
  currentAnimationMix: [],
  animationMixBlendMode: 'normal',
  
  // 表情同步狀態
  characterMorphTargets: {},
  characterAudioLipsyncTargets: {},
  characterMorphTargetDictionary: null,
  
  // 操作實現
  setCharacterModelLoaded: (loaded: boolean) => set({ characterModelLoaded: loaded }),
  
  setCharacterVisible: (visible: boolean) => set({ characterVisible: visible }),
  
  setCharacterPosition: (position: [number, number, number]) => set({ characterPosition: position }),
  
  setCharacterScale: (scale: number) => set({ characterScale: Math.max(0, Math.min(1, scale)) }),
  
  setCharacterRotation: (rotation: [number, number, number]) => set({ characterRotation: rotation }),
  
  setAvailableCharacterAnimations: (animations: string[]) => set({ availableCharacterAnimations: animations }),
  
  setCurrentCharacterAnimation: (animation: string | null) => set({ currentCharacterAnimation: animation }),
  
  setCharacterMorphTargetDictionary: (dictionary: Record<string, number> | null) => set({ characterMorphTargetDictionary: dictionary }),
  
  // 動畫混合操作方法 (新增)
  setAnimationMixMode: (enabled: boolean) => set({ animationMixMode: enabled }),
  
  setCurrentAnimationMix: (animations: Array<{
    name: string;
    weight: number;
    loop: boolean;
    speed: number;
  }>) => set({ currentAnimationMix: animations }),
  
  setAnimationMixBlendMode: (mode: 'normal' | 'additive' | 'override') => set({ animationMixBlendMode: mode }),
  
  updateAnimationMixWeight: (animationName: string, weight: number) => set((state) => ({
    currentAnimationMix: state.currentAnimationMix.map((animation) =>
      animation.name === animationName ? { ...animation, weight } : animation
    )
  })),
  
  clearAnimationMix: () => set({ currentAnimationMix: [] }),
  
  // 表情同步操作方法
  setCharacterMorphTargets: (targets: Record<string, number>) => set({ characterMorphTargets: targets }),
  
  updateCharacterMorphTarget: (key: string, value: number) => set((state) => ({
    characterMorphTargets: { ...state.characterMorphTargets, [key]: value }
  })),
  
  resetCharacterMorphTargets: () => set({ characterMorphTargets: {} }),
  
  setCharacterAudioLipsyncTarget: (key: string, value: number) => set((state) => ({
    characterAudioLipsyncTargets: { ...state.characterAudioLipsyncTargets, [key]: value }
  })),
  
  resetCharacterTransform: () => set({
    characterPosition: [0, 0, 0],
    characterScale: 15,
    characterRotation: [0, 0, 0]
  })
}); 