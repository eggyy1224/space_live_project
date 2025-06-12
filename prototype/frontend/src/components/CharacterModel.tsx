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

    // 處理材質和陰影
    cloned.traverse((obj: THREE.Object3D) => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        
        // 增強角色的光照效果（參考 HeadModel 的處理）
        if (mesh.material) {
          const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
          materials.forEach((mat: any) => {
            if (mat.isMeshStandardMaterial || mat.isMeshPhysicalMaterial) {
              // 增加材質的亮度 - 添加更強的自發光
              mat.emissive = new THREE.Color(0x222222); // 增強自發光顏色
              mat.emissiveIntensity = 0.8; // 大幅增加自發光強度
              // 調整材質屬性讓它更容易被照亮
              mat.roughness = Math.min(mat.roughness * 0.5, 1); // 更光滑
              mat.metalness = Math.max(mat.metalness * 0.3, 0); // 更少金屬感
              
              // 如果原始材質是白色或沒有顏色，給它一個默認顏色
              if (mat.color && (mat.color.r > 0.9 && mat.color.g > 0.9 && mat.color.b > 0.9)) {
                mat.color.setHex(0xcccccc); // 淺灰色代替純白色
              }
              mat.needsUpdate = true;
            }
            if (mat.isMeshLambertMaterial || mat.isMeshPhongMaterial) {
              // 對於舊式材質，大幅增加亮度
              if (mat.color) {
                mat.color.multiplyScalar(2.5); // 增加亮度倍數
              }
              mat.needsUpdate = true;
            }
          });
        } else {
          // 如果沒有材質，創建一個帶強自發光的材質
          mesh.material = new THREE.MeshStandardMaterial({
            color: 0xffffff, // 更亮的基礎顏色
            roughness: 0.3,  // 更光滑
            metalness: 0.1,  // 更少金屬感
            emissive: new THREE.Color(0x333333), // 更強的自發光
            emissiveIntensity: 1.0 // 最大自發光強度
          });
        }
        
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