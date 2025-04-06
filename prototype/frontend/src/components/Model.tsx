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
  morphTargets?: Record<string, number>;
  currentAnimation?: string;
  setAvailableAnimations: (anims: string[]) => void;
  setMorphTargetDictionary: (dict: Record<string, number>) => void;
  setMorphTargetInfluences: (influences: number[]) => void;
}

const FALLBACK_ANIMATION_THRESHOLD = 0.5; // Seconds
const FALLBACK_MORPH_KEYS = ['jawOpen', 'mouthFunnel', 'mouthPucker', 'mouthSmile']; // Adjust based on model

export const Model: React.FC<ModelProps> = ({
  url,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  morphTargets = {},
  currentAnimation,
  setAvailableAnimations,
  setMorphTargetDictionary,
  setMorphTargetInfluences
}) => {
  const group = useRef<THREE.Group>(null);
  const meshRef = useRef<MeshWithMorphs | null>(null);
  const { scene, animations } = useGLTF(url);
  const { actions, mixer } = useAnimations(animations, group);
  const [localMorphTargetDictionary, setLocalMorphTargetDictionary] = useState<Record<string, number>>({});
  
  // Refs for fallback animation logic
  const lastMorphUpdateTimestampRef = useRef<number>(0);
  const prevMorphTargetsRef = useRef<Record<string, number>>(morphTargets);

  // Update available animations list and set default animation
  useEffect(() => {
    const animationNames = Object.keys(actions);
    setAvailableAnimations(animationNames);
  // Add actions to dependency array as it changes when model reloads
  }, [actions, setAvailableAnimations]);

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

  // Extract mesh with morph targets and update parent state
  useEffect(() => {
    if (scene) {
      let foundMeshWithMorphs = false;
      let newMorphDict: Record<string, number> | null = null;
      let newMorphInfluences: number[] | null = null;

      // Traverse the loaded scene (which is a Group) to find the mesh
      scene.traverse((object) => {
        // Check if it's a Mesh and has morph targets
        if (!foundMeshWithMorphs && object instanceof THREE.Mesh && object.morphTargetInfluences && object.morphTargetDictionary) {
          const meshWithMorphs = object as MeshWithMorphs;
          if (meshWithMorphs.morphTargetDictionary && meshWithMorphs.morphTargetInfluences) {
            foundMeshWithMorphs = true;
            meshRef.current = meshWithMorphs; // Store ref to the mesh
            newMorphDict = { ...meshWithMorphs.morphTargetDictionary };
            newMorphInfluences = [...meshWithMorphs.morphTargetInfluences];
            setLocalMorphTargetDictionary(newMorphDict); // Update local dictionary
          }
        }
      });

      if (foundMeshWithMorphs && newMorphDict && newMorphInfluences) {
        // Lift the state up to the parent component
        setMorphTargetDictionary(newMorphDict);
        setMorphTargetInfluences(newMorphInfluences);
        // Reset timestamp and previous morphs ref on model change
        lastMorphUpdateTimestampRef.current = performance.now() / 1000;
        prevMorphTargetsRef.current = {}; 
      } else {
        // Reset if no mesh with morphs found
        meshRef.current = null;
        setMorphTargetDictionary({});
        setMorphTargetInfluences([]);
        setLocalMorphTargetDictionary({});
      }
    }
  }, [scene, url, setMorphTargetDictionary, setMorphTargetInfluences]); // Dependencies

  // useFrame for morph target updates (API/Service OR Fallback)
  useFrame((state, delta) => {
    // Guard clauses
    if (!meshRef.current || !meshRef.current.morphTargetInfluences || Object.keys(localMorphTargetDictionary).length === 0) {
      return; 
    }

    const meshWithMorphs = meshRef.current;
    const influences = meshWithMorphs.morphTargetInfluences;
    const dictionary = localMorphTargetDictionary;
    const currentTime = state.clock.elapsedTime;

    // Check if morphTargets prop has updated
    if (morphTargets !== prevMorphTargetsRef.current) {
      lastMorphUpdateTimestampRef.current = currentTime;
      prevMorphTargetsRef.current = morphTargets;
    }

    const timeSinceLastUpdate = currentTime - lastMorphUpdateTimestampRef.current;

    // Decide whether to use fallback or standard update
    if (timeSinceLastUpdate > FALLBACK_ANIMATION_THRESHOLD) {
      // --- Fallback Mouth Animation Logic ---
      FALLBACK_MORPH_KEYS.forEach((key, index) => {
        const morphIndex = dictionary[key];
        if (morphIndex !== undefined && morphIndex < influences.length) {
          const speedFactor = 0.5 + index * 0.2;
          const amplitudeFactor = 0.1 + Math.random() * 0.15;
          const phaseFactor = index * Math.PI / 3;
          const targetValue = Math.max(0, Math.sin(currentTime * speedFactor * Math.PI * 2 + phaseFactor) * amplitudeFactor);
          const currentValue = influences[morphIndex];
          const lerpFactor = Math.min(delta * 5, 1);
          influences[morphIndex] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
        }
      });
      // Smoothly zero out other mouth morphs not controlled by fallback
      Object.keys(dictionary).forEach(key => {
        if (key.toLowerCase().includes('mouth') && !FALLBACK_MORPH_KEYS.includes(key)) {
           const morphIndex = dictionary[key];
           if (morphIndex !== undefined && morphIndex < influences.length) {
              const currentValue = influences[morphIndex];
              if (currentValue > 0.01) {
                  const lerpFactor = Math.min(delta * 10, 1);
                  influences[morphIndex] = THREE.MathUtils.lerp(currentValue, 0, lerpFactor);
              }
           }
        }
      });

    } else {
      // --- Standard Morph Targets Update Logic (from props) ---
      Object.entries(morphTargets).forEach(([name, value]) => {
        const index = dictionary[name];
        if (index !== undefined && index < influences.length) {
          const currentValue = influences[index];
          const targetValue = value as number;
          if (Math.abs(currentValue - targetValue) > 0.01) {
            const lerpFactor = Math.min(delta * 15, 1); 
            influences[index] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
          } else if (currentValue !== targetValue) {
            influences[index] = targetValue;
          }
        }
      });
      // Smoothly zero out fallback morphs if not present in new morphTargets prop
      FALLBACK_MORPH_KEYS.forEach(key => {
         const morphIndex = dictionary[key];
         if (morphIndex !== undefined && morphIndex < influences.length && !(key in morphTargets)) {
             const currentValue = influences[morphIndex];
             if (currentValue > 0.01) {
                 const lerpFactor = Math.min(delta * 10, 1);
                 influences[morphIndex] = THREE.MathUtils.lerp(currentValue, 0, lerpFactor);
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