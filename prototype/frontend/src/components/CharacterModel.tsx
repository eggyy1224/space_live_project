import React, { useEffect, useRef, useMemo } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { Group } from 'three';
import * as THREE from 'three';
import * as SkeletonUtils from 'three/examples/jsm/utils/SkeletonUtils.js';
import { useCharacterService } from '../services/CharacterService';
import logger, { LogCategory } from '../utils/LogManager';

export function CharacterModel() {
  const {
    characterModelUrl,
    characterVisible,
    characterPosition,
    characterScale,
    characterRotation,
    currentCharacterAnimation,
    morphTargets,
    setCharacterModelLoaded,
    setCharacterMorphTargetDictionary,
  } = useCharacterService();

  const group = useRef<Group>(null);

  // 預加載模型
  useEffect(() => {
    logger.info(`[CharacterModel] Mounting with URL: ${characterModelUrl}`, LogCategory.MODEL);
    try {
      useGLTF.preload(characterModelUrl);
    } catch (error) {
      logger.error(`[CharacterModel] Failed to preload: ${error instanceof Error ? error.message : String(error)}`, LogCategory.MODEL);
    }
    return () => {
      logger.info(`[CharacterModel] Unmounting. Model: ${characterModelUrl}`, LogCategory.MODEL);
    };
  }, [characterModelUrl]);

  // 加載模型
  const { scene, animations } = useGLTF(characterModelUrl);

  // 克隆場景以允許多個實例
  const clonedScene = useMemo(() => {
    if (!scene) return null;
    const cloned = SkeletonUtils.clone(scene);

    // 設置角色材質（可以根據需要調整）
    const characterMaterial = new THREE.MeshPhysicalMaterial({
      color: '#F0F0F0',
      metalness: 0.1,
      roughness: 0.8,
      clearcoat: 0.1,
      clearcoatRoughness: 0.4
    });

    cloned.traverse((obj: THREE.Object3D) => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        mesh.material = characterMaterial;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
      }
    });

    return cloned;
  }, [scene]);

  // 初始化動畫混合器
  const { mixer, actions } = useAnimations(animations, group);

  // 設置變形目標字典
  useEffect(() => {
    if (clonedScene) {
      const morphTargetDict: Record<string, number> = {};
      
      clonedScene.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh;
          if (mesh.morphTargetDictionary) {
            Object.keys(mesh.morphTargetDictionary).forEach((key) => {
              morphTargetDict[key] = mesh.morphTargetDictionary![key];
            });
          }
        }
      });

      if (Object.keys(morphTargetDict).length > 0) {
        setCharacterMorphTargetDictionary(morphTargetDict);
        logger.info(`[CharacterModel] Found ${Object.keys(morphTargetDict).length} morph targets`, LogCategory.MODEL);
      }

      // 標記模型已加載
      setCharacterModelLoaded(true);
    }
  }, [clonedScene, setCharacterMorphTargetDictionary, setCharacterModelLoaded]);

  // 控制動畫播放
  useEffect(() => {
    if (!mixer || !actions || !currentCharacterAnimation) return;

    // 停止所有當前動畫
    Object.values(actions).forEach((action) => {
      if (action) {
        action.fadeOut(0.3);
      }
    });

    // 播放指定動畫
    const action = actions[currentCharacterAnimation];
    if (action) {
      action.reset().fadeIn(0.3).play();
      logger.info(`[CharacterModel] Playing animation: ${currentCharacterAnimation}`, LogCategory.ANIMATION);
    } else {
      logger.warn(`[CharacterModel] Animation not found: ${currentCharacterAnimation}`, LogCategory.ANIMATION);
    }

    return () => {
      // 清理函數
    };
  }, [mixer, actions, currentCharacterAnimation]);

  // 應用變形目標
  useEffect(() => {
    if (!clonedScene) return;

    clonedScene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
          Object.entries(morphTargets).forEach(([name, value]) => {
            const index = mesh.morphTargetDictionary![name];
            if (index !== undefined && mesh.morphTargetInfluences) {
              mesh.morphTargetInfluences[index] = value;
            }
          });
        }
      }
    });
  }, [clonedScene, morphTargets]);

  // 如果不可見，不渲染
  if (!characterVisible || !clonedScene) {
    return null;
  }

  return (
    <group
      ref={group}
      position={characterPosition}
      scale={[characterScale, characterScale, characterScale]}
      rotation={characterRotation}
    >
      <primitive object={clonedScene} />
    </group>
  );
}

// 預加載模型（可選）
useGLTF.preload('/models/character0611.glb');

// 導出組件
export default CharacterModel; 