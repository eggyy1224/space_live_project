import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger

// 擴展的網格類型，包含morphTargets屬性
interface MeshWithMorphs extends THREE.Mesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

interface ModelProps {
  url: string;
  scale: number;
  rotation: [number, number, number];
  position: [number, number, number];
  currentAnimation: string | null;
  setAvailableAnimations: (anims: string[]) => void;
  morphTargetDictionary: Record<string, number> | null;
  setMorphTargetDictionary: (dict: Record<string, number>) => void;
  morphTargetInfluences: number[] | null;
  setMorphTargetInfluences: (influences: number[]) => void;
  morphTargets: Record<string, number>;
}

export const Model: React.FC<ModelProps> = ({
  url,
  scale,
  rotation,
  position,
  currentAnimation,
  setAvailableAnimations,
  morphTargetDictionary,
  setMorphTargetDictionary,
  morphTargetInfluences,
  setMorphTargetInfluences,
  morphTargets
}) => {
  const group = useRef<THREE.Group>(null!);
  // Keep track of the previous URL to manage cleanup
  const previousUrlRef = useRef<string>(url);
  // Ref to hold the current scene's group for cleanup, correctly typed as Group
  const sceneRef = useRef<THREE.Group>();

  // Load the model, Drei handles caching based on URL
  // useGLTF returns a scene group
  const { scene, animations } = useGLTF(url);
  const { actions, mixer } = useAnimations(animations, group);
  const meshRef = useRef<THREE.Mesh | null>(null);

  // Store the current scene group in a ref for access in the cleanup function
  useEffect(() => {
    sceneRef.current = scene;
  }, [scene]);

  // Effect for cleaning up resources when the URL changes or component unmounts
  useEffect(() => {
    const currentUrl = url; // Capture url at the time of effect setup

    // Return the cleanup function
    return () => {
      const sceneToClean = sceneRef.current;
      const urlBeingCleaned = currentUrl;

      // Only cleanup if the URL actually changed
      if (sceneToClean && url !== urlBeingCleaned) { 
        logger.info(`Cleaning up resources for model: ${urlBeingCleaned}`, LogCategory.MODEL);
        sceneToClean.traverse((object) => {
          // Check if it's a Mesh
          if (object instanceof THREE.Mesh) {
            // Dispose Geometry
            if (object.geometry) {
              object.geometry.dispose();
              logger.debug(`Disposed geometry for mesh: ${object.name || 'unnamed'} in ${urlBeingCleaned}`, LogCategory.MODEL);
            }
            // Dispose Material(s)
            if (object.material) {
              if (Array.isArray(object.material)) {
                // Iterate through materials array and dispose each
                object.material.forEach((material: THREE.Material) => { // Explicitly type material
                  disposeMaterial(material, urlBeingCleaned); // Ensure 2 arguments are passed
                });
              } else {
                // Dispose single material
                disposeMaterial(object.material as THREE.Material, urlBeingCleaned); // Ensure 2 arguments are passed
              }
            }
          }
        });
         logger.info(`Finished cleanup for model: ${urlBeingCleaned}`, LogCategory.MODEL);
      }
    };
  }, [url]);

  // Helper function to dispose materials and their textures
  const disposeMaterial = (material: THREE.Material, modelUrl: string) => {
    logger.debug(`Disposing material: ${material.name || 'unnamed'} from ${modelUrl}`, LogCategory.MODEL);
    material.dispose();
    // Dispose textures
    for (const key of Object.keys(material)) {
      const value = (material as any)[key];
      if (value && typeof value === 'object' && 'isTexture' in value) {
         logger.debug(`Disposing texture: ${key} from ${modelUrl}`, LogCategory.MODEL);
        (value as THREE.Texture).dispose();
      }
    }
  };

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

  // Get the mesh containing Morph Targets
  useEffect(() => {
    if (scene) {
      let foundMeshWithMorphs = false;
      let newMorphDict: Record<string, number> | null = null;
      let newMorphInfluences: number[] | null = null;

      scene.traverse((object) => {
        if (!foundMeshWithMorphs && object instanceof THREE.Mesh) {
          const meshWithMorphs = object as MeshWithMorphs;

          if (meshWithMorphs.morphTargetDictionary && meshWithMorphs.morphTargetInfluences) {
            foundMeshWithMorphs = true;
            meshRef.current = meshWithMorphs;
            newMorphDict = { ...meshWithMorphs.morphTargetDictionary };
            newMorphInfluences = [...meshWithMorphs.morphTargetInfluences];
          }
        }
      });

      if (foundMeshWithMorphs && newMorphDict && newMorphInfluences) {
        setMorphTargetDictionary(newMorphDict);
        setMorphTargetInfluences(newMorphInfluences);
      } else {
        // Reset morph target data if the new model doesn't have them
        meshRef.current = null;
        setMorphTargetDictionary({});
        setMorphTargetInfluences([]);
      }
    }
  // Ensure url triggers reset
  }, [scene, url, setMorphTargetDictionary, setMorphTargetInfluences]); 

  // Update dynamic Morph Targets from API/Service using lerp for smoothing
  useFrame((_, delta) => {
    if (meshRef.current && morphTargetDictionary && Object.keys(morphTargets).length > 0) {
      const meshWithMorphs = meshRef.current as MeshWithMorphs;

      if (meshWithMorphs.morphTargetInfluences) {
        // let influencesChanged = false; // Not needed if not updating state
        Object.entries(morphTargets).forEach(([name, value]) => {
          const index = morphTargetDictionary[name];
          if (index !== undefined && index < meshWithMorphs.morphTargetInfluences!.length) {
            const currentValue = meshWithMorphs.morphTargetInfluences![index];
            const targetValue = value as number;
            if (Math.abs(currentValue - targetValue) > 0.01) {
              const lerpFactor = Math.min(delta * 15, 1); // Adjust 15 for speed
              meshWithMorphs.morphTargetInfluences![index] = THREE.MathUtils.lerp(
                currentValue,
                targetValue,
                lerpFactor
              );
              // influencesChanged = true;
            } else if (currentValue !== targetValue) {
                meshWithMorphs.morphTargetInfluences![index] = targetValue;
                // influencesChanged = true;
            }
          }
        });
      }
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
      {/* Set key={url} to force re-creation of primitive when url changes */}
      <primitive object={scene} scale={scale} key={url} />
    </group>
  );
}; 