import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type
import ModelService from '../services/ModelService'; // <--- 引入 ModelService
import { useStore } from '../store'; // 修正導入路徑
import { useEmotionalSpeaking } from '../hooks/useEmotionalSpeaking'; // <-- 導入新的 Hook

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

  const { calculateFinalWeights } = useEmotionalSpeaking();
  const manualOrPresetTargets = useStore((state) => state.morphTargets); // <-- Read manual/preset targets from Zustand

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
    
    const autoTargetWeights = calculateFinalWeights(); // Automatic weights
    
    // Determine final target weights based on priority
    let finalTargetWeights: Record<string, number>;
    const hasManualTargets = manualOrPresetTargets && Object.keys(manualOrPresetTargets).length > 0;

    if (Object.keys(autoTargetWeights).length > 0 || hasManualTargets) { // 只在有權重時打印
        console.log('[Model useFrame] Weights Check:', {
            manualTargets: JSON.stringify(manualOrPresetTargets),
            hasManual: hasManualTargets,
            autoTargets: JSON.stringify(autoTargetWeights),
        });
    }

    if (hasManualTargets) {
      // Priority to manual/preset targets if they exist
      finalTargetWeights = manualOrPresetTargets;
      // Optional refinement: Maybe still allow automatic jawOpen/mouthClose for speaking?
      // Example: if (autoTargetWeights.jawOpen !== undefined) finalTargetWeights.jawOpen = Math.max(autoTargetWeights.jawOpen, manualOrPresetTargets.jawOpen ?? 0);
      // Example: if (autoTargetWeights.mouthClose !== undefined) finalTargetWeights.mouthClose = autoTargetWeights.mouthClose; 
    } else {
      // Otherwise, use automatic weights
      finalTargetWeights = autoTargetWeights;
    }
    
    // Apply the final weights with lerp (existing logic)
    Object.keys(dictionary).forEach(name => {
      const index = dictionary[name];
      if (index !== undefined && index < influences.length) {
        // Use finalTargetWeights determined above
        const targetValue = finalTargetWeights[name] ?? 0; 
        
        const currentValue = influences[index];
        
        // Existing lerp logic
        if (Math.abs(currentValue - targetValue) > 0.01) { 
          const lerpFactor = Math.min(delta * 15, 1); // Adjust lerp speed as needed
          influences[index] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
        } else if (currentValue !== targetValue) {
          influences[index] = targetValue;
        } 
      }
    });
  });

  return (
    <group ref={group} position={position} rotation={rotation}>
      <primitive object={scene} scale={scale} key={url} />
    </group>
  );
}; 