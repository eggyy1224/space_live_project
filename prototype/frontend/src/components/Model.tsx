import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type
import ModelService from '../services/ModelService'; // <--- 引入 ModelService
import { useStore } from '../store'; // 修正導入路徑

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
  morphTargetDictionary: Record<string, number> | null;
  setMorphTargetData: (dictionary: Record<string, number> | null, influences: number[] | null) => void;
}

const FALLBACK_ANIMATION_THRESHOLD = 0.5; // Seconds
const FALLBACK_MORPH_KEYS = ['jawOpen', 'mouthFunnel', 'mouthPucker', 'mouthSmile']; // Adjust based on model

export const Model: React.FC<ModelProps> = ({
  url,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  currentAnimation,
  morphTargetDictionary: initialMorphTargetDictionary,
  setMorphTargetData,
}) => {
  const group = useRef<THREE.Group>(null);
  const meshRef = useRef<MeshWithMorphs | null>(null);
  const { scene, animations } = useGLTF(url);
  const { actions, mixer } = useAnimations(animations, group);
  const modelService = ModelService.getInstance();
  
  const currentMorphTargetState = useStore((state) => state.morphTargets);
  const setModelLoaded = useStore((state) => state.setModelLoaded);
  
  // Local state for dictionary, initialized from props or mesh
  const [localMorphTargetDictionary, setLocalMorphTargetDictionary] = useState<Record<string, number>>({});
  
  // Refs for fallback animation logic
  const lastMorphUpdateTimestampRef = useRef<number>(0);
  const prevMorphTargetsRef = useRef<Record<string, number>>({});

  // Update available animations list in the service
  useEffect(() => {
    const animationNames = Object.keys(actions);
    // 直接調用服務方法
    modelService.setAvailableAnimations(animationNames);
    logger.info({ msg: 'Model: Extracted and sent available animations', details: animationNames }, LogCategory.MODEL);
    // Log available animations when model changes
    logger.debug({ msg: 'Model: Available actions', details: animationNames }, LogCategory.MODEL);
  }, [actions, modelService]);

  // Play animation based on selection
  useEffect(() => {
    // Log available actions for debugging when this effect runs
    const availableActionKeys = Object.keys(actions);
    logger.debug({ msg: 'Model: Setting animation based on current state', details: { currentAnimation, availableActionKeys } }, LogCategory.MODEL);

    // Stop all previous animations
    Object.values(actions).forEach(action => {
      if (action && action.isRunning()) {
        action.stop();
      }
    });

    let animationToPlay: THREE.AnimationAction | null = null;
    let animationName: string | null = null;

    // Determine which animation to play
    if (currentAnimation && actions[currentAnimation]) {
       animationToPlay = actions[currentAnimation];
       animationName = currentAnimation;
       logger.info(`Model: Playing selected animation: ${animationName}`, LogCategory.MODEL);
    } else {
        // Try to play Idle as default
        if (actions.Idle) {
            animationToPlay = actions.Idle;
            animationName = 'Idle';
            logger.info('Model: Playing default animation: Idle', LogCategory.MODEL);
        } 
        // If Idle doesn't exist, try playing the first available animation
        else if (availableActionKeys.length > 0) {
           animationName = availableActionKeys[0];
           animationToPlay = actions[animationName];
           logger.info(`Model: Playing first available animation as default: ${animationName}`, LogCategory.MODEL);
        } else {
            logger.warn('Model: No animation selected and no default/available animation found.', LogCategory.MODEL);
        }
    }

    // Play the determined animation with fading
    if (animationToPlay) {
        animationToPlay.reset().fadeIn(0.5).play();
    }

    // Cleanup function to fade out the currently playing animation
    return () => {
       if (animationToPlay && animationToPlay.isRunning()) {
           logger.debug(`Model: Fading out animation: ${animationName || 'unknown'}`, LogCategory.MODEL);
           animationToPlay.fadeOut(0.5);
       }
    };
  // Add actions and mixer to dependencies
  }, [currentAnimation, actions, mixer]);

  // Extract mesh, initialize dictionary and influences, AND set back to service
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

          // Determine dictionary to use
          const dictFromMesh = meshWithMorphs.morphTargetDictionary;
          finalDict = initialMorphTargetDictionary && Object.keys(initialMorphTargetDictionary).length > 0
            ? initialMorphTargetDictionary
            : dictFromMesh || null;
          setLocalMorphTargetDictionary(finalDict || {}); // Update local state for useFrame
          logger.info('Model: Found mesh, dictionary determined.', LogCategory.MODEL, JSON.stringify(finalDict));

          // 不再從這裡初始化或重置 influences，讓 useFrame 從 Zustand 控制
          logger.info('Model: Influences will be controlled by Zustand via useFrame.', LogCategory.MODEL);
        }
      });
    }

    // Call setMorphTargetData and setModelLoaded
    if (foundMeshWithMorphs && finalDict) {
      setMorphTargetData(finalDict, null);
      setModelLoaded(true);
      logger.info('Model: Set modelLoaded state to true in Zustand.', LogCategory.MODEL);
    } else {
      setLocalMorphTargetDictionary({});
      setMorphTargetData(null, null);
      setModelLoaded(false);
      logger.warn('Model: No mesh with morph targets found. Sent null back.', LogCategory.MODEL, `URL: ${url}`);
    }

    // 重置 fallback 計時器和狀態 (這部分可以保留)
    lastMorphUpdateTimestampRef.current = performance.now() / 1000;
    prevMorphTargetsRef.current = {};

  }, [url, scene, setModelLoaded, setMorphTargetData]);

  // useFrame for morph target updates
  useFrame((state, delta) => {
    // 嚴格檢查 mesh 和 influences
    if (!meshRef.current?.morphTargetInfluences || !localMorphTargetDictionary) {
      return; 
    }
    
    const influences = meshRef.current.morphTargetInfluences;
    const dictionary = localMorphTargetDictionary;
    
    // 應用 Zustand 中的 morphTargets 狀態到模型的 influences
    Object.keys(dictionary).forEach(name => {
      const index = dictionary[name];
      if (index !== undefined && index < influences.length) {
        const targetValue = currentMorphTargetState[name] ?? 0;
        
        // --- DEBUG: 直接設置 influence，繞過 lerp --- 
        if (influences[index] !== targetValue) {
          // console.log(`[DEBUG] Setting influence ${name} (${index}) from ${influences[index].toFixed(3)} to ${targetValue}`); // 可選：添加日誌
          influences[index] = targetValue;
        }
        // --- END DEBUG ---

        /* // 原來的 Lerp 邏輯
        const currentValue = influences[index];
        if (Math.abs(currentValue - targetValue) > 0.01) {
          const lerpFactor = Math.min(delta * 15, 1);
          influences[index] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
        } else if (currentValue !== targetValue) {
          influences[index] = targetValue;
        } 
        */
      }
    });
    
    // Fallback 嘴型動畫 (可以保留，但確保它只在沒有任何其他嘴部活動時觸發)
    // 注意：這部分可能需要根據 Zustand 狀態來判斷是否觸發，
    // 例如，檢查 currentMorphTargetState 中是否有嘴部相關的值正在變化。
    // 為了簡化，暫時保留原邏輯，但理想情況下應與 Zustand 狀態同步。
    const timeSinceLastUpdate = state.clock.elapsedTime - lastMorphUpdateTimestampRef.current;
    if (timeSinceLastUpdate > FALLBACK_ANIMATION_THRESHOLD && 
        !Object.keys(currentMorphTargetState).some(key => key.toLowerCase().includes('mouth') || key.toLowerCase().includes('jaw'))) {
      // Fallback嘴型動畫邏輯...
      FALLBACK_MORPH_KEYS.forEach((key, index) => {
        const morphIndex = dictionary[key];
        if (morphIndex !== undefined && morphIndex < influences.length) {
          const speedFactor = 0.5 + index * 0.2;
          const amplitudeFactor = 0.1 + Math.random() * 0.15;
          const phaseFactor = index * Math.PI / 3;
          const targetValue = Math.max(0, Math.sin(state.clock.elapsedTime * speedFactor * Math.PI * 2 + phaseFactor) * amplitudeFactor);
          const currentValue = influences[morphIndex];
          influences[morphIndex] = THREE.MathUtils.lerp(currentValue, targetValue, Math.min(delta * 5, 1));
        }
      });
    }
  });

  // Rotate model based on prop and update mixer
  useFrame((state, delta) => {
    if (group.current) {
      if (group.current.rotation.y !== rotation[1]) {
        group.current.rotation.y = rotation[1];
      }
    }
    if (mixer) {
       mixer.update(delta);
    }
  });

  return (
    <group ref={group} position={position} >
      {/* Use the loaded scene directly, apply scale and key */}
      <primitive object={scene} scale={scale} key={url} />
    </group>
  );
}; 