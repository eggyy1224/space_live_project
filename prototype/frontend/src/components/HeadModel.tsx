import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, Center } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type
import { useStore } from '../store'; // 導入 Zustand store
import { useEmotionalSpeaking } from '../hooks/useEmotionalSpeaking'; // <-- 導入新的 Hook
// --- 移除模型設定導入 ---
// import { EXTERNAL_ANIMATION_PATHS } from '../config/modelConfig';
// --- 移除結束 ---

// --- 移除外部動畫路徑定義 ---
// const EXTERNAL_ANIMATION_PATHS = [
//   '/animations/BaseballHit_animation.glb',
//   '/animations/BodyBlock_animation.glb'
// ];
// --- 移除結束 ---

// --- 新增：定義口型相關的 Morph Target Keys ---
const MOUTH_MORPH_TARGET_KEYS = new Set([
  'jawForward', 'jawLeft', 'jawOpen', 'jawRight',
  'mouthClose', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft',
  'mouthFrownRight', 'mouthFunnel', 'mouthLeft', 'mouthLowerDownLeft',
  'mouthLowerDownRight', 'mouthPressLeft', 'mouthPressRight', 'mouthPucker',
  'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower',
  'mouthShrugUpper', 'mouthSmileLeft', 'mouthSmileRight', 'mouthStretchLeft',
  'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight'
]);
// --- 新增結束 ---

// 擴展的網格類型，包含morphTargets屬性
interface MeshWithMorphs extends THREE.Mesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

// 更新 Props 接口
interface HeadModelProps { // <-- 重命名
  headModelUrl: string; // <-- 重命名
  scale?: number | [number, number, number]; // 保留變換 props
  position?: [number, number, number];
  rotation?: [number, number, number];
  // currentAnimation?: string; // 移除
}

// 更新組件名稱
export const HeadModel: React.FC<HeadModelProps> = ({
  headModelUrl, // <-- 使用新 prop 名
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  // currentAnimation, // 移除
}) => {
  const group = useRef<THREE.Group>(null);
  const meshRef = useRef<MeshWithMorphs | null>(null);
  // const headService = HeadService.getInstance(); // <-- 不再需要實例

  // --- 移除外部動畫預加載 ---
  // useEffect(() => {
  //   EXTERNAL_ANIMATION_PATHS.forEach(path => useGLTF.preload(path));
  // }, []);
  // --- 移除結束 ---

  // --- 只加載主模型 (頭部) ---
  const { scene /*, animations: embeddedAnimations */ } = useGLTF(headModelUrl); // <-- 使用 headModelUrl, 移除 animations
  // --- 移除外部動畫加載 ---
  // const externalAnimationsData = EXTERNAL_ANIMATION_PATHS.map(path => useGLTF(path));
  // --- 移除結束 ---

  // --- 移除動畫合併邏輯 ---
  // const combinedAnimations = useRef<THREE.AnimationClip[]>([]);
  // useEffect(() => {
      // ... 合併邏輯 ...
  // }, [embeddedAnimations, externalAnimationsData, headService]);
  // --- 移除結束 ---

  // --- 移除 useAnimations ---
  // const { actions, mixer } = useAnimations(combinedAnimations.current, group);
  // --- 移除結束 ---

  // --- 從 Zustand Store 獲取 setHeadModelLoaded ---
  const setHeadModelLoaded = useStore((state) => state.setHeadModelLoaded); // <-- 使用重命名後的 action
  // --- 結束 ---

  const [localMorphTargetDictionary, setLocalMorphTargetDictionary] = useState<Record<string, number>>({});

  const { calculateCurrentTrajectoryWeights } = useEmotionalSpeaking();

  // --- 讀取 Zustand 狀態並使用 Ref 傳遞 ---
  const manualOrPresetTargetsFromStore = useStore((state) => state.morphTargets);
  const manualOrPresetTargetsRef = useRef(manualOrPresetTargetsFromStore);
  // -- 新增：讀取語音口型狀態 -- 
  const audioLipsyncTargetsFromStore = useStore((state) => state.audioLipsyncTargets);
  const audioLipsyncTargetsRef = useRef(audioLipsyncTargetsFromStore);
  // -- 新增結束 -- 
  const isSpeakingFromStore = useStore((state) => state.isSpeaking);
  const isSpeakingRef = useRef(isSpeakingFromStore);

  useEffect(() => {
    manualOrPresetTargetsRef.current = manualOrPresetTargetsFromStore;
  }, [manualOrPresetTargetsFromStore]);
  // -- 新增：更新語音口型 Ref -- 
  useEffect(() => {
    audioLipsyncTargetsRef.current = audioLipsyncTargetsFromStore;
  }, [audioLipsyncTargetsFromStore]);
  // -- 新增結束 -- 
  useEffect(() => {
    isSpeakingRef.current = isSpeakingFromStore;
  }, [isSpeakingFromStore]);
  // --- Ref 傳遞結束 ---

  // --- 移除舊的設置可用動畫的 useEffect ---
  // useEffect(() => {
      // ... 設置可用動畫 ...
  // }, [actions, headService]);
  // --- 移除結束 ---

  // --- 移除簡化的動畫播放邏輯 ---
  // useEffect(() => {
      // ... 播放動畫邏輯 ...
  // }, [currentAnimation, actions]);
  // --- 移除結束 ---

  // --- 更新設置加載狀態和提取 Morph 字典的 useEffect ---
  useEffect(() => {
    let foundMeshWithMorphs = false;
    meshRef.current = null;
    let finalDict: Record<string, number> | null = null;

    if (scene) {
      scene.traverse((object) => {
        if (!foundMeshWithMorphs && object instanceof THREE.Mesh && object.morphTargetInfluences && object.morphTargetDictionary) {
          const meshWithMorphs = object as MeshWithMorphs;
          if (!meshWithMorphs.morphTargetInfluences) return;
          meshRef.current = meshWithMorphs;
          foundMeshWithMorphs = true;
          finalDict = meshWithMorphs.morphTargetDictionary || null;
          setLocalMorphTargetDictionary(finalDict || {});
          logger.info('HeadModel: Found mesh with morph targets.', LogCategory.MODEL, JSON.stringify(finalDict));
          meshWithMorphs.morphTargetInfluences.fill(0);
          logger.info('HeadModel: Initialized morphTargetInfluences to 0.', LogCategory.MODEL);
        }
      });

      // 只要 scene 存在，就設置 headModelLoaded 為 true
      setHeadModelLoaded(true); // <-- 使用重命名後的 action
      logger.info('HeadModel: Scene loaded, setting headModelLoaded state to true in Zustand.', LogCategory.MODEL);

      if (!foundMeshWithMorphs) {
        setLocalMorphTargetDictionary({});
        logger.warn('HeadModel: No mesh with morph targets found, but scene loaded.', LogCategory.MODEL, `URL: ${headModelUrl}`);
      }

    } else {
      setLocalMorphTargetDictionary({});
      setHeadModelLoaded(false); // <-- 使用重命名後的 action
      logger.error('HeadModel: Scene failed to load.', LogCategory.MODEL, `URL: ${headModelUrl}`);
    }
    // 依賴項更新為 headModelUrl
  }, [headModelUrl, scene, setHeadModelLoaded]);
  // --- 更新結束 ---

  // --- 更新 useFrame，使用新的權重合併邏輯 ---
  useFrame((state, delta) => {
    if (!meshRef.current?.morphTargetInfluences || !localMorphTargetDictionary || Object.keys(localMorphTargetDictionary).length === 0) {
      return; 
    }
    
    const influences = meshRef.current.morphTargetInfluences;
    const dictionary = localMorphTargetDictionary;
    
    // --- 新的權重計算邏輯 --- 
    const trajectoryWeights = calculateCurrentTrajectoryWeights(); // 1. 情緒軌跡權重 (直接計算)
    const manualOrPresetTargets = manualOrPresetTargetsRef.current; // 2. 手動/預設權重 (來自 store)
    const audioLipsyncTargets = audioLipsyncTargetsRef.current; // 3. 語音口型權重 (來自 store)
    const isSpeaking = isSpeakingRef.current; // 4. 說話狀態

    // 5. 判斷是否有手動/預設激活
    //    (簡單檢查 manualOrPresetTargets 是否有非零值，或更複雜的邏輯)
    //    這裡使用一個簡化判斷：如果 manualOrPresetTargets 不是空對象就認為激活
    const isManualOrPresetActive = Object.keys(manualOrPresetTargets).length > 0 && 
                                    Object.values(manualOrPresetTargets).some(v => v > 0.01);

    // 6. 確定基礎表情
    const baseEmotion = isManualOrPresetActive ? manualOrPresetTargets : trajectoryWeights;

    // 7. 獲取語音口型 (只有在說話時)
    const audioShapes = isSpeaking ? audioLipsyncTargets : {};

    // 8. 合併：以 baseEmotion 為基礎，用 audioShapes 覆蓋
    const finalTargetWeights = {
      ...baseEmotion,
      ...audioShapes // 如果 audioShapes 中有鍵，會覆蓋 baseEmotion 中的同名鍵
    };

    // logger.debug("[useFrame] Final Weights:", LogCategory.MODEL, finalTargetWeights);
    // --- 權重計算結束 ---
    
    // --- Apply final weights with Lerp (保持不變) --- 
    Object.keys(dictionary).forEach(name => {
      const index = dictionary[name];
      if (index !== undefined && index < influences.length) {
        const targetValue = finalTargetWeights[name] ?? 0;
        const currentValue = influences[index];
        if (Math.abs(currentValue - targetValue) > 0.01) { 
          const lerpFactor = Math.min(delta * 25, 1); 
          influences[index] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
        } else if (currentValue !== targetValue) {
          influences[index] = targetValue;
        } 
      }
    });
    // --- Apply End ---
  });
  // --- 更新結束 ---

  // 更新返回的 JSX
  return (
    <group ref={group} position={position} rotation={rotation}>
      {/* 使用drei的Center組件包裹scene，讓模型以視覺中心點進行縮放 */}
      <Center scale={scale} position={[0, 0, 0]}>
        <primitive 
          object={scene} 
          key={headModelUrl} 
        />
      </Center>
    </group>
  );
};

// 導出 HeadModel
// export default HeadModel; // <-- 如果有 default export 