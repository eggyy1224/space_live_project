import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';

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
  const { scene, animations } = useGLTF(url);
  const { actions, mixer } = useAnimations(animations, group);
  const meshRef = useRef<THREE.Mesh | null>(null);
  
  // 更新可用動畫列表並設定預設動畫
  useEffect(() => {
    const animationNames = Object.keys(actions);
    setAvailableAnimations(animationNames);
  }, [actions, setAvailableAnimations]);
  
  // 根據選擇播放動畫
  useEffect(() => {
    // 先停止所有動畫
    Object.values(actions).forEach(action => {
      if (action && typeof action.stop === 'function') {
        action.stop();
      }
    });
    
    // 播放選定的動畫
    if (currentAnimation && actions[currentAnimation] && typeof actions[currentAnimation].play === 'function') {
      actions[currentAnimation].play();
    }
    
    return () => {
      if (mixer) mixer.stopAllAction();
    };
  }, [currentAnimation, actions, mixer]);

  // 獲取包含Morph Targets的網格
  useEffect(() => {
    if (scene) {
      let foundMeshWithMorphs = false;
      
      scene.traverse((object) => {
        // 檢查所有類型的網格，不僅僅是SkinnedMesh
        if (object instanceof THREE.Mesh) {
          const meshWithMorphs = object as MeshWithMorphs;
          
          if (meshWithMorphs.morphTargetDictionary && meshWithMorphs.morphTargetInfluences) {
            foundMeshWithMorphs = true;
            meshRef.current = meshWithMorphs;
            setMorphTargetDictionary(meshWithMorphs.morphTargetDictionary);
            setMorphTargetInfluences([...meshWithMorphs.morphTargetInfluences]);
          }
        }
      });
      
      if (!foundMeshWithMorphs) {
        // 靜默失敗，不輸出警告
      }
    }
  }, [scene, setMorphTargetDictionary, setMorphTargetInfluences, url]);

  // 更新手動設置的Morph Target數值
  useEffect(() => {
    if (meshRef.current && morphTargetInfluences) {
      const meshWithMorphs = meshRef.current as MeshWithMorphs;
      
      if (meshWithMorphs.morphTargetInfluences) {
        for (let i = 0; i < morphTargetInfluences.length; i++) {
          if (i < meshWithMorphs.morphTargetInfluences.length) {
            meshWithMorphs.morphTargetInfluences[i] = morphTargetInfluences[i];
          }
        }
      }
    }
  }, [morphTargetInfluences]);

  // 更新從API獲取的動態Morph Target
  useEffect(() => {
    if (meshRef.current && morphTargetDictionary && Object.keys(morphTargets).length > 0) {
      const meshWithMorphs = meshRef.current as MeshWithMorphs;
      
      // 先保存當前的影響值
      const currentInfluences = [...(morphTargetInfluences || [])];
      
      // 應用來自API的動態值
      Object.entries(morphTargets).forEach(([name, value]) => {
        const index = morphTargetDictionary[name];
        if (index !== undefined && meshWithMorphs.morphTargetInfluences) {
          // 平滑過渡到新值，避免突然的變化
          const currentValue = meshWithMorphs.morphTargetInfluences[index];
          const targetValue = value as number;
          
          // 使用較小的過渡步驟，使變化更加平滑
          const transitionStep = Math.abs(targetValue - currentValue) > 0.05 ? 
                               (targetValue - currentValue) * 0.5 : 
                               (targetValue - currentValue);
          
          meshWithMorphs.morphTargetInfluences[index] = currentValue + transitionStep;
          
          // 更新保存的影響值
          if (currentInfluences[index] !== undefined) {
            currentInfluences[index] = currentValue + transitionStep;
          }
        }
      });
      
      // 更新狀態，這樣UI會反映新值
      setMorphTargetInfluences(currentInfluences);
    }
  }, [morphTargets, morphTargetDictionary, setMorphTargetInfluences, morphTargetInfluences]);

  // 旋轉模型
  useFrame(() => {
    if (group.current) {
      group.current.rotation.y = rotation[1];
    }
  });

  return (
    <group ref={group} position={position}>
      <primitive object={scene} scale={scale} />
    </group>
  );
}; 