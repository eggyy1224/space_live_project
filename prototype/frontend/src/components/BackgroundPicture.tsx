import React, { useEffect, useMemo, useState } from 'react';
import { useThree } from '@react-three/fiber';
import { useLoader } from '@react-three/fiber';
import { useStore } from '../store';
import WebSocketService from '../services/WebSocketService';
import * as THREE from 'three';

const BackgroundPicture: React.FC = () => {
  const { scene } = useThree();
  
  // 從 zustand 獲取背景圖片狀態
  const backgroundPictureEnabled = useStore((state) => state.backgroundPictureEnabled);
  const currentBackgroundPicture = useStore((state) => state.currentBackgroundPicture);
  const setCurrentBackgroundPicture = useStore((state) => state.setCurrentBackgroundPicture);
  const setBackgroundPictureEnabled = useStore((state) => state.setBackgroundPictureEnabled);
  const setAvailableBackgroundPictures = useStore((state) => state.setAvailableBackgroundPictures);
  const availableBackgroundPictures = useStore((state) => state.availableBackgroundPictures);
  
  // 使用狀態來管理紋理載入
  const [texture, setTexture] = useState<THREE.Texture | null>(null);
  
  // 構建圖片路徑
  const imagePath = useMemo(() => {
    if (backgroundPictureEnabled && currentBackgroundPicture) {
      return `/background_pictures/${currentBackgroundPicture}`;
    }
    return null; // 當沒有背景圖片時返回 null
  }, [backgroundPictureEnabled, currentBackgroundPicture]);

  // 載入紋理
  useEffect(() => {
    if (!imagePath) {
      setTexture(null);
      return;
    }

    let retryCount = 0;
    const maxRetries = 3;
    
    const loadTexture = () => {
      const loader = new THREE.TextureLoader();
      
      // 檢查路徑並添加隨機參數避免快取問題
      const urlWithCacheBuster = `${imagePath}?t=${Date.now()}&retry=${retryCount}`;
      
      console.log(`Attempting to load background texture: ${urlWithCacheBuster}`);
      
      // 先用 fetch 檢查文件是否存在
      fetch(imagePath, { method: 'HEAD' })
        .then(response => {
          if (!response.ok) {
            throw new Error(`File not found: ${response.status} ${response.statusText}`);
          }
          
          // 文件存在，載入紋理
          loader.load(
            urlWithCacheBuster,
            (loadedTexture) => {
              console.log('✅ Background texture loaded successfully:', imagePath);
              setTexture(loadedTexture);
            },
            (progress) => {
              // console.log('Loading progress:', progress);
            },
            (loadError) => {
              console.error(`❌ Three.js failed to load texture (attempt ${retryCount + 1}):`, imagePath, loadError);
              handleRetry();
            }
          );
        })
        .catch(fetchError => {
          console.error(`❌ File does not exist (attempt ${retryCount + 1}):`, imagePath, fetchError);
          handleRetry();
        });
    };
    
    const handleRetry = () => {
      if (retryCount < maxRetries) {
        retryCount++;
        console.log(`🔄 Retrying in 1 second... (attempt ${retryCount + 1}/${maxRetries + 1})`);
        setTimeout(loadTexture, 1000);
      } else {
        console.error('🚫 Max retries reached, giving up loading texture:', imagePath);
        setTexture(null);
      }
    };
    
    loadTexture();
  }, [imagePath]);

  // WebSocket 監聽背景圖片生成
  useEffect(() => {
    const service = WebSocketService.getInstance();

    const handleBackgroundImageGenerated = (data: any) => {
      if (data.type === 'background-image-generated' && data.filename) {
        console.log('收到新的背景圖片:', data.filename);
        
        // 更新可用的背景圖片列表
        const newBackgroundPictures = [...availableBackgroundPictures];
        if (!newBackgroundPictures.includes(data.filename)) {
          newBackgroundPictures.push(data.filename);
          setAvailableBackgroundPictures(newBackgroundPictures);
        }
        
        // 延遲一點時間確保文件完全寫入，然後設定背景
        setTimeout(() => {
          setBackgroundPictureEnabled(true);
          setCurrentBackgroundPicture(data.filename);
          console.log('背景圖片已更新:', data.filename, '描述:', data.caption);
        }, 500); // 延遲 500ms
      }
    };

    const handleBackgroundImageChanged = (data: any) => {
      if (data.type === 'background-image-changed') {
        console.log('收到背景圖片變更指令:', data);
        
        // 設定背景圖片啟用狀態
        setBackgroundPictureEnabled(data.enabled);
        
        // 設定當前背景圖片
        setCurrentBackgroundPicture(data.filename);
        
        console.log('背景圖片狀態已更新:', data.enabled ? '啟用' : '停用', '檔案:', data.filename);
      }
    };

    service.registerHandler('background-image-generated', handleBackgroundImageGenerated);
    service.registerHandler('background-image-changed', handleBackgroundImageChanged);
    
    return () => {
      service.removeHandler('background-image-generated', handleBackgroundImageGenerated);
      service.removeHandler('background-image-changed', handleBackgroundImageChanged);
    };
  }, [availableBackgroundPictures, setAvailableBackgroundPictures, setBackgroundPictureEnabled, setCurrentBackgroundPicture]);

  // 設定場景背景
  useEffect(() => {
    if (backgroundPictureEnabled && currentBackgroundPicture && texture) {
      // 將材質設定為場景背景
      console.log('🎨 Setting scene background:', currentBackgroundPicture);
      scene.background = texture;
    } else {
      // 移除背景，回到原本的顏色
      console.log('🚫 Removing scene background');
      scene.background = null;
    }

    // 清理函數
    return () => {
      if (!backgroundPictureEnabled) {
        scene.background = null;
      }
    };
  }, [scene, backgroundPictureEnabled, currentBackgroundPicture, texture]);

  // 組件卸載時清理
  useEffect(() => {
    return () => {
      if (texture) {
        texture.dispose();
      }
      scene.background = null;
    };
  }, []);

  // 這個組件不需要渲染任何 3D 物件，只是設定場景背景
  return null;
};

export default BackgroundPicture; 