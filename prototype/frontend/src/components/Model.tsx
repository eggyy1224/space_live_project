import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type
import ModelService from '../services/ModelService'; // <--- 引入 ModelService
import { useStore } from '../store'; // 修正導入路徑
import { useEmotionalSpeaking } from '../hooks/useEmotionalSpeaking'; // <-- 導入新的 Hook

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
  const { scene, animations } = useGLTF(url);
  const { actions, mixer } = useAnimations(animations, group);
  const modelService = ModelService.getInstance();
  
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
    const animationNames = Object.keys(actions);
    modelService.setAvailableAnimations(animationNames);
    logger.info({ msg: 'Model: Extracted and sent available animations', details: animationNames }, LogCategory.MODEL);
    logger.debug({ msg: 'Model: Available actions', details: animationNames }, LogCategory.MODEL);
  }, [actions, modelService]);

  useEffect(() => {
    const availableActionKeys = Object.keys(actions);
    logger.debug({ msg: 'Model: Setting animation based on current state', details: { currentAnimation, availableActionKeys } }, LogCategory.MODEL);
    Object.values(actions).forEach(action => {
      if (action && action.isRunning()) {
        action.stop();
      }
    });
    let animationToPlay: THREE.AnimationAction | null = null;
    let animationName: string | null = null;
    if (currentAnimation && actions[currentAnimation]) {
      animationToPlay = actions[currentAnimation];
      animationName = currentAnimation;
      logger.info(`Model: Playing selected animation: ${animationName}`, LogCategory.MODEL);
    } else {
      if (actions.Idle) {
        animationToPlay = actions.Idle;
        animationName = 'Idle';
        logger.info('Model: Playing default animation: Idle', LogCategory.MODEL);
      } else if (availableActionKeys.length > 0) {
        animationName = availableActionKeys[0];
        animationToPlay = actions[animationName];
        logger.info(`Model: Playing first available animation as default: ${animationName}`, LogCategory.MODEL);
      } else {
        logger.warn('Model: No animation selected and no default/available animation found.', LogCategory.MODEL);
      }
    }
    if (animationToPlay) {
      animationToPlay.reset().fadeIn(0.5).play();
    }
    return () => {
      if (animationToPlay && animationToPlay.isRunning()) {
        logger.debug(`Model: Fading out animation: ${animationName || 'unknown'}`, LogCategory.MODEL);
        animationToPlay.fadeOut(0.5);
      }
    };
  }, [currentAnimation, actions, mixer]);

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
    }

    if (foundMeshWithMorphs) {
      setModelLoaded(true);
      logger.info('Model: Set modelLoaded state to true in Zustand.', LogCategory.MODEL);
    } else {
      setLocalMorphTargetDictionary({});
      setModelLoaded(false);
      logger.warn('Model: No mesh with morph targets found.', LogCategory.MODEL, `URL: ${url}`);
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

  return (
    <group ref={group} position={position} rotation={rotation}>
      <primitive object={scene} scale={scale} key={url} />
    </group>
  );
}; 