import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type

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
  morphTargets?: Record<string, number>; // Dynamic targets from WS
  currentAnimation?: string; // Keep optional
  morphTargetDictionary: Record<string, number> | null;
  morphTargetInfluences: number[] | null;
  getManualMorphTargets: () => Record<string, number>;
  setMorphTargetData: (dictionary: Record<string, number> | null, influences: number[] | null) => void;
}

const FALLBACK_ANIMATION_THRESHOLD = 0.5; // Seconds
const FALLBACK_MORPH_KEYS = ['jawOpen', 'mouthFunnel', 'mouthPucker', 'mouthSmile']; // Adjust based on model

export const Model: React.FC<ModelProps> = ({
  url,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  morphTargets = {}, // Dynamic targets
  currentAnimation,
  morphTargetDictionary: initialMorphTargetDictionary, // Rename prop
  morphTargetInfluences: initialMorphTargetInfluences, // Rename prop
  getManualMorphTargets,
  setMorphTargetData
}) => {
  const group = useRef<THREE.Group>(null);
  const meshRef = useRef<MeshWithMorphs | null>(null);
  const { scene, animations } = useGLTF(url);
  const { actions, mixer } = useAnimations(animations, group);
  
  // Local state for dictionary, initialized from props or mesh
  const [localMorphTargetDictionary, setLocalMorphTargetDictionary] = useState<Record<string, number>>({});
  // Local state for available animations
  const [availableAnimations, setAvailableAnimations] = useState<string[]>([]);
  
  // Refs for fallback animation logic
  const lastMorphUpdateTimestampRef = useRef<number>(0);
  const prevMorphTargetsRef = useRef<Record<string, number>>(morphTargets);

  // Update available animations list locally
  useEffect(() => {
    const animationNames = Object.keys(actions);
    setAvailableAnimations(animationNames);
  }, [actions]);

  // Play animation based on selection
  useEffect(() => {
    // Stop all previous animations
    Object.values(actions).forEach(action => {
      if (action && action.isRunning()) { // Check if running before stopping
        action.stop();
      }
    });

    // Play the selected animation with fading
    if (currentAnimation && actions[currentAnimation]) {
       // Fade in the new animation
       actions[currentAnimation].reset().fadeIn(0.5).play();
    } else {
        // Optional: Play a default idle animation if no currentAnimation
        if (actions.Idle) {
            actions.Idle.reset().fadeIn(0.5).play();
        }
    }

    // Cleanup function to fade out the current animation when it changes or component unmounts
    return () => {
       if (currentAnimation && actions[currentAnimation]) {
           // Fade out the current animation
           actions[currentAnimation].fadeOut(0.5);
       } else if (actions.Idle && actions.Idle.isRunning()) {
           // Fade out idle if it was playing
           actions.Idle.fadeOut(0.5);
       }
    };
  // Add actions and mixer to dependencies
  }, [currentAnimation, actions, mixer]);

  // Extract mesh, initialize dictionary and influences, AND set back to service
  useEffect(() => {
    let foundMeshWithMorphs = false;
    meshRef.current = null;
    let finalDict: Record<string, number> | null = null;
    let finalInfluences: number[] | null = null;

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

          // Determine influences to use and set on mesh
          const meshInfluences = meshWithMorphs.morphTargetInfluences;
          if (initialMorphTargetInfluences && initialMorphTargetInfluences.length === meshInfluences.length) {
            finalInfluences = [...initialMorphTargetInfluences];
            meshWithMorphs.morphTargetInfluences = finalInfluences;
            logger.info('Model: Initialized influences from props.', LogCategory.MODEL);
          } else {
            finalInfluences = [...meshInfluences]; // Use mesh defaults
            logger.info('Model: Initialized influences from mesh defaults.', LogCategory.MODEL);
          }
        }
      });
    }

    // Call setMorphTargetData to update the service AFTER traversing the scene
    if (foundMeshWithMorphs) {
      setMorphTargetData(finalDict, finalInfluences);
      logger.info('Model: Sent dictionary and influences back to service.', LogCategory.MODEL);
    } else {
      setLocalMorphTargetDictionary({}); // Clear local state if no mesh found
      setMorphTargetData(null, null); // Inform service that no data is available
      logger.warn('Model: No mesh with morph targets found. Sent null back.', LogCategory.MODEL, `URL: ${url}`);
    }

    lastMorphUpdateTimestampRef.current = performance.now() / 1000;
    prevMorphTargetsRef.current = {};

  }, [url, scene, initialMorphTargetDictionary, initialMorphTargetInfluences, setMorphTargetData]); // Add setMorphTargetData to dependencies

  // useFrame for morph target updates
  useFrame((state, delta) => {
    // 嚴格檢查 mesh 和 influences
    if (!meshRef.current?.morphTargetInfluences || Object.keys(localMorphTargetDictionary).length === 0) {
      return; 
    }
    // 將 influences 賦值給常量
    const influences = meshRef.current.morphTargetInfluences;
    // 如果 influences 仍然可能是 null/undefined (理論上不應該，但為了 TS)，再次檢查
    if (!influences) return;
    
    const mesh = meshRef.current;
    const dictionary = localMorphTargetDictionary;
    const currentTime = state.clock.elapsedTime;
    const manualTargets = getManualMorphTargets(); 

    if (morphTargets !== prevMorphTargetsRef.current) {
      lastMorphUpdateTimestampRef.current = currentTime;
      prevMorphTargetsRef.current = morphTargets;
    }
    const timeSinceLastUpdate = currentTime - lastMorphUpdateTimestampRef.current;

    if (timeSinceLastUpdate > FALLBACK_ANIMATION_THRESHOLD && Object.keys(manualTargets).length === 0) {
      // --- Fallback Mouth Animation Logic ---
      FALLBACK_MORPH_KEYS.forEach((key, index) => {
        const morphIndex = dictionary[key];
        // 現在使用確認非空的 influences 常量
        if (morphIndex !== undefined && morphIndex < influences.length) {
          const speedFactor = 0.5 + index * 0.2;
          const amplitudeFactor = 0.1 + Math.random() * 0.15;
          const phaseFactor = index * Math.PI / 3;
          const targetValue = Math.max(0, Math.sin(currentTime * speedFactor * Math.PI * 2 + phaseFactor) * amplitudeFactor);
          const currentValue = influences[morphIndex]; // Use const
          const lerpFactor = Math.min(delta * 5, 1);
          influences[morphIndex] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
        }
      });
      Object.keys(dictionary).forEach(key => {
        if (key.toLowerCase().includes('mouth') && !FALLBACK_MORPH_KEYS.includes(key) && manualTargets[key] === undefined) {
           const morphIndex = dictionary[key];
           if (morphIndex !== undefined && morphIndex < influences.length) { // Use const
              const currentValue = influences[morphIndex]; // Use const
              if (currentValue > 0.01) {
                  const lerpFactor = Math.min(delta * 10, 1);
                  influences[morphIndex] = THREE.MathUtils.lerp(currentValue, 0, lerpFactor);
              }
           }
        }
      });
    } else {
      // --- Standard Morph Targets Update Logic (Manual or Dynamic) ---
      Object.keys(dictionary).forEach(name => {
        const index = dictionary[name];
        if (index !== undefined && index < influences.length) { // Use const
          const manualValue = manualTargets[name];
          const dynamicValue = morphTargets[name];

          let targetValue: number = 0;
          if (manualValue !== undefined) {
            targetValue = manualValue;
          } else if (dynamicValue !== undefined) {
            targetValue = dynamicValue;
          }
          
          const currentValue = influences[index]; // Use const

          if (Math.abs(currentValue - targetValue) > 0.01) {
            const lerpFactor = Math.min(delta * 15, 1);
            influences[index] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
          } else if (currentValue !== targetValue) {
            influences[index] = targetValue;
          }
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