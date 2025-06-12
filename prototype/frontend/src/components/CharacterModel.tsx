import React, { useEffect, useRef, useMemo } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { Group } from 'three';
import * as THREE from 'three';
import * as SkeletonUtils from 'three/examples/jsm/utils/SkeletonUtils.js';
import { useCharacterService } from '../services/CharacterService';
import { useEmotionalSpeaking } from '../hooks/useEmotionalSpeaking';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';

/**
 * CharacterModel - 角色模型組件
 * 
 * 完全同步設計說明：
 * - Character 和 Head 模型實現雙向完全同步
 * - 手動表情控制：HeadSlice.morphTargets ⟷ CharacterSlice.characterMorphTargets
 * - 語音口型同步：HeadSlice.audioLipsyncTargets ⟷ CharacterSlice.characterAudioLipsyncTargets
 * - CharacterService 提供合併後的狀態，確保兩個模型完全一致
 * - 包括用戶手動控制、語音驅動和情緒軌跡的完全同步
 */
export function CharacterModel() {
  const {
    characterModelUrl,
    characterVisible,
    characterPosition,
    characterScale,
    characterRotation,
    currentCharacterAnimation,
    morphTargets,
    audioLipsyncTargets,
    setCharacterModelLoaded,
    setCharacterMorphTargetDictionary,
  } = useCharacterService();

  // 添加情緒軌跡計算 (與 HeadModel 保持一致)
  const { calculateCurrentTrajectoryWeights } = useEmotionalSpeaking();
  const isSpeaking = useStore((state) => state.isSpeaking);

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

  // 設置變形目標字典 (角色專屬，但不影響共享表情狀態)
  useEffect(() => {
    if (clonedScene) {
      const morphTargetDict: Record<string, number> = {};
      
      clonedScene.traverse((child) => {
        // 檢查標準 Mesh
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh;
          if (mesh.morphTargetDictionary) {
            logger.info(`[CharacterModel] Found Mesh with morph targets: ${child.name}`, LogCategory.MODEL);
            Object.keys(mesh.morphTargetDictionary).forEach((key) => {
              morphTargetDict[key] = mesh.morphTargetDictionary![key];
            });
          }
        }
        
        // 檢查 SkinnedMesh (角色模型的主要表情網格通常是 SkinnedMesh)
        if ((child as THREE.SkinnedMesh).isSkinnedMesh) {
          const skinnedMesh = child as THREE.SkinnedMesh;
          if (skinnedMesh.morphTargetDictionary) {
            logger.info(`[CharacterModel] Found SkinnedMesh with morph targets: ${child.name}`, LogCategory.MODEL);
            Object.keys(skinnedMesh.morphTargetDictionary).forEach((key) => {
              morphTargetDict[key] = skinnedMesh.morphTargetDictionary![key];
            });
          }
        }
      });

      if (Object.keys(morphTargetDict).length > 0) {
        // 僅保存角色專屬的字典，不影響共享的表情狀態
        setCharacterMorphTargetDictionary(morphTargetDict);
        logger.info(`[CharacterModel] Found ${Object.keys(morphTargetDict).length} morph targets in character model`, LogCategory.MODEL);
        logger.info(`[CharacterModel] Character morphTargets will sync with HeadModel via shared state`, LogCategory.MODEL);
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

  // 應用變形目標 (同步表情 + 語音驅動 + 情緒軌跡)
  useEffect(() => {
    if (!clonedScene) return;

    // 使用與 HeadModel 相同的權重計算邏輯
    const trajectoryWeights = calculateCurrentTrajectoryWeights(); // 1. 情緒軌跡權重
    const manualOrPresetTargets = morphTargets; // 2. 手動/預設權重
    const audioLipsyncTargetsFromProps = audioLipsyncTargets; // 3. 語音口型權重

    // 判斷是否有手動/預設激活
    const isManualOrPresetActive = Object.keys(manualOrPresetTargets).length > 0 && 
                                    Object.values(manualOrPresetTargets).some((v: number) => v > 0.01);

    // 確定基礎表情
    const baseEmotion = isManualOrPresetActive ? manualOrPresetTargets : trajectoryWeights;

    // 獲取語音口型 (只有在說話時)
    const audioShapes = isSpeaking ? audioLipsyncTargetsFromProps : {};

    // 合併：以 baseEmotion 為基礎，用 audioShapes 覆蓋
    const finalTargetWeights = {
      ...baseEmotion,
      ...audioShapes
    };
    
    // 調試日誌
    if (Object.keys(finalTargetWeights).length > 0) {
      logger.info(`[CharacterModel] Applying ${Object.keys(finalTargetWeights).length} final target weights (trajectory + manual + audio)`, LogCategory.MODEL);
      if (Object.keys(trajectoryWeights).length > 0) {
        logger.info(`[CharacterModel] Trajectory weights active: ${Object.keys(trajectoryWeights).length}`, LogCategory.MODEL);
      }
    }

    clonedScene.traverse((child) => {
      // 處理標準 Mesh
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
          Object.entries(finalTargetWeights).forEach(([name, value]) => {
            const index = mesh.morphTargetDictionary![name];
            if (index !== undefined && mesh.morphTargetInfluences && typeof value === 'number') {
              mesh.morphTargetInfluences[index] = value;
            }
          });
        }
      }
      
      // 處理 SkinnedMesh (這裡應該是 AvatarHead.007)
      if ((child as THREE.SkinnedMesh).isSkinnedMesh) {
        const skinnedMesh = child as THREE.SkinnedMesh;
        if (skinnedMesh.morphTargetDictionary && skinnedMesh.morphTargetInfluences) {
          logger.info(`[CharacterModel] Applying final weights to SkinnedMesh: ${child.name}`, LogCategory.MODEL);
          Object.entries(finalTargetWeights).forEach(([name, value]) => {
            const index = skinnedMesh.morphTargetDictionary![name];
            if (index !== undefined && skinnedMesh.morphTargetInfluences && typeof value === 'number') {
              skinnedMesh.morphTargetInfluences[index] = value;
            }
          });
        }
      }
    });
  }, [clonedScene, morphTargets, audioLipsyncTargets, calculateCurrentTrajectoryWeights, isSpeaking]);

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