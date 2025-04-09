import React, { useEffect, useRef, useMemo } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { AnimationClip, Group } from 'three';
import { useBodyService } from '../services/BodyService';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';
import { EXTERNAL_ANIMATION_PATHS } from '../config/modelConfig';

// --- 輔助 Hook 加載多個 GLTF 動畫 ---
const useExternalAnimations = (paths: string[]) => {
  const results = paths.map(path => useGLTF(path)); // 為每個路徑調用 useGLTF
  // 將所有加載結果中的 animations 數組合併
  const combinedAnimations = useMemo(() => 
    results.reduce((acc, result) => acc.concat(result.animations), [] as AnimationClip[]),
    [results] // 當 results 數組本身變化時重新計算
  );
  return combinedAnimations;
};
// ----------------------------------

export function BodyModel() {
  const { 
    bodyModelUrl, 
    currentAnimation, 
    setBodyModelLoaded, 
    setAvailableAnimations 
  } = useBodyService();
  const group = useRef<Group>(null);

  useEffect(() => {
    logger.info(`[BodyModel] Mounting with URL: ${bodyModelUrl}`, LogCategory.MODEL);
    // 添加預加載日誌，因為組件可能因 Suspense 多次嘗試掛載
    try {
      const initialBodyUrl = useStore.getState().bodyModelUrl;
      if (initialBodyUrl === bodyModelUrl) { // 只在 URL 匹配時預加載
        logger.info(`[BodyModel] Attempting preload (inside component): ${initialBodyUrl}`, LogCategory.MODEL);
        useGLTF.preload(initialBodyUrl);
      } else {
        logger.warn(`[BodyModel] Preload skipped: URL mismatch (${bodyModelUrl} vs ${initialBodyUrl})`, LogCategory.MODEL);
      }
    } catch (error) {
      logger.error(`[BodyModel] Failed to preload (inside component): ${error instanceof Error ? error.message : String(error)}`, LogCategory.MODEL);
    }
    return () => {
      logger.info(`[BodyModel] Unmounting/Remounting. Model: ${bodyModelUrl}`, LogCategory.MODEL);
    };
  }, [bodyModelUrl]);

  // 1. 加載身體模型場景 (忽略其動畫)
  const { scene } = useGLTF(bodyModelUrl);
  logger.info(`[BodyModel] Body scene loaded from ${bodyModelUrl}`, LogCategory.MODEL);

  // 2. 加載所有外部動畫
  const externalAnimations = useExternalAnimations(EXTERNAL_ANIMATION_PATHS);
  logger.info(`[BodyModel] Loaded ${externalAnimations.length} external animations from ${EXTERNAL_ANIMATION_PATHS.length} files.`, LogCategory.ANIMATION);
  
  // 3. 使用合併後的外部動畫
  const { actions, names } = useAnimations(externalAnimations, group);

  // 初始加載處理
  useEffect(() => {
    // 這個 effect 應該在 scene 和 animations 成功加載後運行一次
    // 使用當前渲染週期計算出的 names
    logger.info(`[BodyModel] Load Success & Effect running. Model: ${bodyModelUrl}, Setting available animations: ${names.join(', ') || 'None'}`, LogCategory.MODEL);
    setAvailableAnimations(names); // Set state using the current 'names'
    setBodyModelLoaded(true);     // Set state
    
    // 清理函數
    return () => {
      logger.info(`[BodyModel] Effect cleanup for ${bodyModelUrl}. Resetting loaded state and animations.`, LogCategory.MODEL);
      setBodyModelLoaded(false);
      setAvailableAnimations([]);
    };
  // 依賴項：僅在模型 URL 或場景對象變化時重新運行
  // 移除可能不穩定的 externalAnimations 和 names 引用
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bodyModelUrl, scene, setAvailableAnimations, setBodyModelLoaded]); 

  // 動畫切換邏輯 (保持不變)
  useEffect(() => {
    if (!actions || Object.keys(actions).length === 0) {
      return; 
    }
    
    const currentAction = currentAnimation ? actions[currentAnimation] : null;
    const previousAnimation = Object.values(actions).find(action => action?.isRunning());

    if (previousAnimation && previousAnimation !== currentAction) {
      previousAnimation.fadeOut(0.5);
    }

    if (currentAction) {
        currentAction
          .reset()
          .setEffectiveTimeScale(1)
          .setEffectiveWeight(1)
          .fadeIn(0.5)
          .play();
        logger.debug(`[BodyModel] Playing external animation: ${currentAnimation}`, LogCategory.ANIMATION);
    } else if (previousAnimation) {
        previousAnimation.fadeOut(0.5);
        logger.debug('[BodyModel] Fading out last external animation', LogCategory.ANIMATION);
    }

  }, [currentAnimation, actions]);

  // scene 應該總是存在，因為 useGLTF 會 suspend 直到加載完成或錯誤
  // 如果 useGLTF 拋出錯誤，會被 Suspense fallback 捕獲，不會執行到這裡
  logger.info(`[BodyModel] Rendering primitive for ${bodyModelUrl}...`, LogCategory.MODEL);
  return <primitive ref={group} object={scene} dispose={null} />;
}

// --- 預加載邏輯更新 ---
try {
  const initialBodyUrl = useStore.getState().bodyModelUrl;
  if (initialBodyUrl) {
    logger.info(`[BodyModel] Preloading body: ${initialBodyUrl}`, LogCategory.MODEL);
    useGLTF.preload(initialBodyUrl);
  } else {
    logger.warn('[BodyModel] Preload skipped (body): initial bodyModelUrl is empty.', LogCategory.MODEL);
  }
  // 預加載所有外部動畫
  EXTERNAL_ANIMATION_PATHS.forEach(path => {
    logger.info(`[BodyModel] Preloading animation: ${path}`, LogCategory.ANIMATION);
    useGLTF.preload(path);
  });
} catch (error) {
  logger.error(`[BodyModel] Failed to preload: ${error instanceof Error ? error.message : String(error)}`, LogCategory.MODEL);
}
// ----------------------

export default BodyModel; 