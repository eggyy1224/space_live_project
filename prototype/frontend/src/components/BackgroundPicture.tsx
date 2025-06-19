import React, { useEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import { useTexture } from '@react-three/drei';
import { useStore } from '../store';
import * as THREE from 'three';

const BackgroundPicture: React.FC = () => {
  const { scene } = useThree();
  
  // 從 zustand 獲取背景圖片狀態
  const backgroundPictureEnabled = useStore((state) => state.backgroundPictureEnabled);
  const currentBackgroundPicture = useStore((state) => state.currentBackgroundPicture);
  
  // 構建圖片路徑（總是返回一個有效路徑，避免條件性使用 hook）
  const imagePath = useMemo(() => {
    if (backgroundPictureEnabled && currentBackgroundPicture) {
      return `/background_pictures/${currentBackgroundPicture}`;
    }
    // 返回一個預設圖片路徑，避免 hook 條件性調用
    return '/background_pictures/outerspace1.png';
  }, [backgroundPictureEnabled, currentBackgroundPicture]);

  // 總是載入材質（避免條件性使用 hook）
  const texture = useTexture(imagePath);

  // 設定場景背景
  useEffect(() => {
    if (backgroundPictureEnabled && currentBackgroundPicture && texture) {
      // 將材質設定為場景背景
      scene.background = texture;
    } else {
      // 移除背景，回到原本的顏色
      scene.background = null;
    }

    // 清理函數
    return () => {
      if (!backgroundPictureEnabled) {
        scene.background = null;
      }
    };
  }, [scene, backgroundPictureEnabled, currentBackgroundPicture, texture]);

  // 這個組件不需要渲染任何 3D 物件，只是設定場景背景
  return null;
};

export default BackgroundPicture; 