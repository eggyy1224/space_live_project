import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type
import ModelService from '../services/ModelService'; // <--- 引入 ModelService
import { useStore } from '../store'; // 修正導入路徑
import { useEmotionalSpeaking } from '../hooks/useEmotionalSpeaking'; // <-- 導入新的 Hook
// --- 引入模型設定 ---
import { EXTERNAL_ANIMATION_PATHS } from '../config/modelConfig';
// --- 引入結束 ---

// --- 定義外部動畫路徑 (移至 modelConfig.ts) ---
// const EXTERNAL_ANIMATION_PATHS = [
//   \'/animations/BaseballHit_animation.glb\',
//   \'/animations/BodyBlock_animation.glb\'
// ];
// --- 定義結束 ---

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

interface ModelProps {
  url: string;
  scale?: number | [number, number, number];
  position?: [number, number, number];
  rotation?: [number, number, number];
  currentAnimation?: string; // Keep optional
}

export const Model: React.FC<ModelProps> = ({
  url,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  currentAnimation,
}) => {
  const group = useRef<THREE.Group>(null);
  const meshRef = useRef<MeshWithMorphs | null>(null);
  const modelService = ModelService.getInstance();
  
  // --- 預加載外部動畫 ---
  useEffect(() => {
    EXTERNAL_ANIMATION_PATHS.forEach(path => useGLTF.preload(path));
  }, []);
  // --- 預加載結束 ---

  // --- 加載主模型和外部動畫 ---
  const { scene, animations: embeddedAnimations } = useGLTF(url);
  // 加載所有外部動畫
  const externalAnimationsData = EXTERNAL_ANIMATION_PATHS.map(path => useGLTF(path));

  // 提取並合併所有動畫
  const combinedAnimations = useRef<THREE.AnimationClip[]>([]);
  useEffect(() => {
    let allClips = [...embeddedAnimations];
    externalAnimationsData.forEach((data, index) => {
      if (data && data.animations) {
        // 可以選擇性地為外部動畫名稱添加前綴以避免衝突
        const prefix = EXTERNAL_ANIMATION_PATHS[index].split('/').pop()?.replace('_animation.glb', '') || `ext_${index}`;
        const processedClips = data.animations.map(clip => {
            const newClip = clip.clone(); // 克隆以避免修改原始緩存
            newClip.name = `${prefix}|${clip.name}`; // 添加前綴到名稱
            return newClip;
        });
        allClips = allClips.concat(processedClips);
        logger.debug(`[Model] Loaded external animations from ${EXTERNAL_ANIMATION_PATHS[index]} with prefix ${prefix}`, LogCategory.ANIMATION);
      }
    });
    combinedAnimations.current = allClips;
    // Note: useAnimations 會在下一次渲染時使用更新後的 combinedAnimations.current
    // 但為了確保 ModelService 獲取最新的列表，我們在此處直接觸發更新
    const animationNames = allClips.map(clip => clip.name);
    modelService.setAvailableAnimations(animationNames);
    logger.info({ msg: 'Model: Combined and sent available animations', details: animationNames }, LogCategory.MODEL);

  }, [embeddedAnimations, externalAnimationsData, modelService]); // 依賴項確保在數據加載後執行

  // 使用合併後的動畫列表初始化 useAnimations
  const { actions, mixer } = useAnimations(combinedAnimations.current, group);
  // --- 加載和合併結束 ---

  const setModelLoaded = useStore((state) => state.setModelLoaded);
  
  const [localMorphTargetDictionary, setLocalMorphTargetDictionary] = useState<Record<string, number>>({});

  const { calculateCurrentTrajectoryWeights } = useEmotionalSpeaking();

  // --- 讀取 Zustand 狀態並使用 Ref 傳遞 --- 
  const manualOrPresetTargetsFromStore = useStore((state) => state.morphTargets);
  const manualOrPresetTargetsRef = useRef(manualOrPresetTargetsFromStore);
  // Add isSpeaking state with ref
  const isSpeakingFromStore = useStore((state) => state.isSpeaking);
  const isSpeakingRef = useRef(isSpeakingFromStore);

  useEffect(() => {
    manualOrPresetTargetsRef.current = manualOrPresetTargetsFromStore;
  }, [manualOrPresetTargetsFromStore]);
  // Update isSpeaking ref
  useEffect(() => {
    isSpeakingRef.current = isSpeakingFromStore;
  }, [isSpeakingFromStore]);
  // --- Ref 傳遞結束 ---

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
          logger.info('Model: Found mesh with morph targets.', LogCategory.MODEL, JSON.stringify(finalDict));
          meshWithMorphs.morphTargetInfluences.fill(0);
          logger.info('Model: Initialized morphTargetInfluences to 0.', LogCategory.MODEL);
        }
      });
      
      // --- 修改點：只要 scene 存在，就設置 modelLoaded 為 true --- 
      setModelLoaded(true);
      logger.info('Model: Scene loaded, setting modelLoaded state to true in Zustand.', LogCategory.MODEL);
      // --- 修改結束 ---
      
      // 如果沒有找到 morphs，還是要記錄一下
      if (!foundMeshWithMorphs) {
        setLocalMorphTargetDictionary({}); // 清空本地字典
        logger.warn('Model: No mesh with morph targets found, but scene loaded.', LogCategory.MODEL, `URL: ${url}`);
      }
      
    } else {
      // 如果 scene 不存在 (加載失敗)
      setLocalMorphTargetDictionary({});
      setModelLoaded(false);
      logger.error('Model: Scene failed to load.', LogCategory.MODEL, `URL: ${url}`);
    }
  }, [url, scene, setModelLoaded]);

  useFrame((state, delta) => {
    if (mixer) {
      mixer.update(delta);
    }

    if (!meshRef.current?.morphTargetInfluences || !localMorphTargetDictionary || Object.keys(localMorphTargetDictionary).length === 0) {
      return; 
    }
    
    const influences = meshRef.current.morphTargetInfluences;
    const dictionary = localMorphTargetDictionary;
    
    // --- Weights Calculation (Corrected Logic) --- 
    const trajectoryWeights = calculateCurrentTrajectoryWeights(); // 1. Trajectory emotion weights
    const storeTargets = manualOrPresetTargetsRef.current; // 2. Contains presets OR audio mouth shapes
    const isSpeaking = isSpeakingRef.current; // 3. Speaking state

    // 4. Determine Base Emotion (Preset or Trajectory)
    //    Check if storeTargets contains keys *other than* known audio-driven keys
    const isPresetActive = Object.keys(storeTargets).some(key => key !== 'jawOpen'); // Simple check assuming only jawOpen is audio-driven
    const baseEmotion = isPresetActive ? storeTargets : trajectoryWeights;

    // 5. Determine Audio Mouth Shapes (only if speaking)
    const audioMouthShapes: Record<string, number> = {};
    if (isSpeaking) {
        // Explicitly check for known audio-driven keys provided by AudioService
        if (storeTargets.hasOwnProperty('jawOpen')) {
            audioMouthShapes['jawOpen'] = storeTargets['jawOpen'];
        }
        // If more audio-driven keys are added later (e.g., mouthFunnel from frequency), add checks here
    }

    // 6. Merge: Start with base emotion, then overlay audio mouth shapes
    //    Spread ensures non-mouth keys from baseEmotion are kept.
    //    Audio keys (like jawOpen) will be overridden if present in audioMouthShapes.
    const finalTargetWeights = {
        ...baseEmotion,
        ...audioMouthShapes
    };

    // logger.debug("[useFrame] Calculated final weights.", LogCategory.MODEL, finalTargetWeights);
    // --- Weights Calculation End ---
    
    // --- Apply final weights with Lerp --- 
    Object.keys(dictionary).forEach(name => {
      const index = dictionary[name];
      if (index !== undefined && index < influences.length) {
        const targetValue = finalTargetWeights[name] ?? 0; // Use the correctly calculated final weight
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

  // --- Simplified Animation Logic for Debugging ---
  useEffect(() => {
    // 重要：確保在 actions 更新後再執行此 effect
    if (Object.keys(actions).length === 0 && combinedAnimations.current.length > 0) {
        // 如果 actions 尚未根據 combinedAnimations 更新，則稍後再試
        logger.debug('[Model Debug] Actions not yet populated, waiting...', LogCategory.ANIMATION);
        return; 
    }

    const action = currentAnimation ? actions[currentAnimation] : null;
    const animationNameToLog = currentAnimation || 'None';

    if (action) {
      logger.debug(`[Model Debug] Attempting to play: ${animationNameToLog}`, LogCategory.ANIMATION);
      // Stop everything else first (less smooth, but for testing)
      Object.values(actions).forEach(a => {
          if (a && a !== action && a.isRunning()) {
              a.stop();
              logger.debug(`[Model Debug] Stopped other running action`, LogCategory.ANIMATION); // Log which action gets stopped
          }
      });
      // Reset, fade in, and play the target action
      action.reset().fadeIn(0.3).play();
      logger.info(`[Model Debug] Played: ${animationNameToLog}`, LogCategory.ANIMATION);
    } else {
      // Stop all if no animation selected (currentAnimation is null or invalid)
      logger.debug(`[Model Debug] No target animation, stopping all.`, LogCategory.ANIMATION);
      let stoppedAny = false;
      Object.values(actions).forEach(a => {
          if (a && a.isRunning()) {
              a.stop();
              stoppedAny = true;
          }
      });
      if (stoppedAny) {
          logger.info(`[Model Debug] Stopped all running animations.`, LogCategory.ANIMATION);
      }
    }
    // Note: No dependency on previousAnimation ref in this simplified version
  }, [currentAnimation, actions]); // 保持依賴 actions
  // --- End Simplified Logic ---

  return (
    <group ref={group} position={position} rotation={rotation}>
      <primitive object={scene} scale={scale} key={url} />
    </group>
  );
}; 