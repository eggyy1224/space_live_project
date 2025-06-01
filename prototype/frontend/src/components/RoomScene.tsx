import React, { useRef, useEffect } from 'react';
import { useGLTF } from '@react-three/drei';
import { Group } from 'three';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager';
import { AVAILABLE_SCENES } from '../config/sceneConfig';

interface RoomSceneProps {
  roomModelUrl: string;
  position?: [number, number, number];
  rotation?: [number, number, number];
  scale?: [number, number, number];
}

export const RoomScene: React.FC<RoomSceneProps> = ({
  roomModelUrl,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = [1, 1, 1]
}) => {
  const group = useRef<Group>(null);
  
  // 載入房間場景模型
  const { scene } = useGLTF(roomModelUrl);
  
  useEffect(() => {
    logger.info(`[RoomScene] Loading room scene: ${roomModelUrl}`, LogCategory.MODEL);
    
    if (scene) {
      // 設置房間場景的材質和陰影
      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          // 啟用陰影接收和投射
          object.castShadow = true;
          object.receiveShadow = true;
          
          // 如果材質存在，調整其屬性
          if (object.material) {
            const material = Array.isArray(object.material) ? object.material : [object.material];
            material.forEach((mat: any) => {
              if (mat.isMeshStandardMaterial || mat.isMeshPhysicalMaterial) {
                // 確保材質能夠正確反射光線
                mat.needsUpdate = true;
              }
            });
          }
        }
      });
      
      logger.info('[RoomScene] Room scene loaded and configured successfully', LogCategory.MODEL);
    }
  }, [scene, roomModelUrl]);
  
  if (!scene) {
    logger.warn('[RoomScene] Scene not loaded yet', LogCategory.MODEL);
    return null;
  }
  
  return (
    <group ref={group} position={position} rotation={rotation} scale={scale}>
      <primitive object={scene} dispose={null} />
    </group>
  );
};

// 預加載所有房間場景
AVAILABLE_SCENES.forEach((scene) => {
  try {
    logger.info(`[RoomScene] Preloading scene: ${scene.name} (${scene.url})`, LogCategory.MODEL);
    useGLTF.preload(scene.url);
  } catch (error) {
    logger.error(`[RoomScene] Failed to preload scene ${scene.name}: ${error instanceof Error ? error.message : String(error)}`, LogCategory.MODEL);
  }
});

export default RoomScene; 