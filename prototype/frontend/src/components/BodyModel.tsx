import React, { useEffect, useRef, useMemo } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { Group } from 'three';
import * as THREE from 'three';
import { useBodyService } from '../services/BodyService';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';
import { EXTERNAL_ANIMATION_PATHS } from '../config/modelConfig';
import { getFriendlyAnimationName } from '../utils/animationUtils';

// --- 輔助 Hook 加載多個 GLTF 動畫 ---
const useExternalAnimations = (paths: string[]) => {
  // 1. 為每個路徑調用 useGLTF 並獲取結果
  const results = paths.map(path => useGLTF(path)); 
  
  // 2. 提取每個結果中的 animations 數組
  const animationClipsPerFile = useMemo(() => 
    results.map(result => result.animations),
    [results] // 依賴原始加載結果
  );

  // 3. 合併所有 animations (供 useAnimations 初始化 mixer)
  const combinedAnimations = useMemo(() => 
    animationClipsPerFile.flat(), // 使用 flat() 替代 reduce
    [animationClipsPerFile]
  );

  // 返回合併結果和按文件分的結果
  return { combinedAnimations, animationClipsPerFile }; 
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

  // --- 生成友好名稱列表 ---
  const friendlyAnimationNames = useMemo(() => 
    EXTERNAL_ANIMATION_PATHS.map(getFriendlyAnimationName),
    [] // 只計算一次，因為 EXTERNAL_ANIMATION_PATHS 是常量
  );
  // ----------------------

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

  // 2. 加載所有外部動畫 (獲取合併結果和原始結果)
  const { combinedAnimations: externalAnimations, animationClipsPerFile } = 
    useExternalAnimations(EXTERNAL_ANIMATION_PATHS);
  logger.info(`[BodyModel] Loaded ${externalAnimations.length} external animations from ${EXTERNAL_ANIMATION_PATHS.length} files.`, LogCategory.ANIMATION);
  
  // 3. 使用合併後的外部動畫獲取 mixer
  const { mixer } = useAnimations(externalAnimations, group); 

  // --- 創建友好名稱到精確 Action 的映射 --- 
  const friendlyToActionMap = useMemo(() => {
    const map = new Map<string, THREE.AnimationAction>();
    // --- 檢查 mixer 和 group.current 是否就緒 ---
    if (!mixer || !group.current) {
        logger.warn('[BodyModel] Mixer or group ref not ready for mapping.', LogCategory.ANIMATION);
        return map; // 返回空 map
    }
    // ------------------------------------------
    const currentGroup = group.current; // 確保在 useMemo 內部引用的是當前值
    
    if (friendlyAnimationNames.length === animationClipsPerFile.length) {
      friendlyAnimationNames.forEach((friendlyName, index) => {
        const clips = animationClipsPerFile[index];
        if (clips && clips.length > 0) {
            const clip = clips[0]; 
            // --- 使用 currentGroup (已知非 null) ---
            const action = mixer.clipAction(clip, currentGroup); 
            // -------------------------------------
            if (action) {
                if (map.has(friendlyName)) {
                   logger.warn(`[BodyModel] Duplicate friendly animation name encountered: ${friendlyName}. Overwriting map entry.`, LogCategory.ANIMATION);
                }
                map.set(friendlyName, action);
            } else {
                 logger.error(`[BodyModel] mixer.clipAction returned null for clip: ${clip?.name} (friendly name: ${friendlyName})`, LogCategory.ANIMATION);
            }
        } else {
             logger.warn(`[BodyModel] No animation clips found in file corresponding to friendly name: ${friendlyName}`, LogCategory.ANIMATION);
        }
      });
      // 日誌記錄映射關係 (友好名稱 -> action 的內部 clip 名稱)
      const mapLog: Record<string, string> = {};
      map.forEach((action, friendlyName) => {
        mapLog[friendlyName] = action?.getClip().name || 'undefined';
      });
      logger.info(`[BodyModel] Created precise friendlyName-to-Action map: ${JSON.stringify(mapLog)}`, LogCategory.ANIMATION);

    } else {
      logger.error(`[BodyModel] Mismatch between friendly names (${friendlyAnimationNames.length}) and animation files (${animationClipsPerFile.length}). Cannot create accurate map.`, LogCategory.ANIMATION);
    }
    return map;
  // --- 添加 group.current 到依賴 --- 
  }, [friendlyAnimationNames, animationClipsPerFile, mixer, group.current]); 
  // --------------------------------

  // 初始加載處理
  useEffect(() => {
    logger.info(`[BodyModel] Load Success & Effect running. Model: ${bodyModelUrl}, Setting available FRIENDLY animations: ${friendlyAnimationNames.join(', ') || 'None'}`, LogCategory.MODEL);
    setAvailableAnimations(friendlyAnimationNames); 
    setBodyModelLoaded(true);     
    
    return () => {
      logger.info(`[BodyModel] Effect cleanup for ${bodyModelUrl}. Resetting loaded state and animations.`, LogCategory.MODEL);
      setBodyModelLoaded(false);
      setAvailableAnimations([]);
    };
  // 依賴項：僅在模型 URL 或場景對象變化時重新運行
  // 移除可能不穩定的 externalAnimations 和 names 引用
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bodyModelUrl, scene, setAvailableAnimations, setBodyModelLoaded, friendlyAnimationNames]); 

  // --- 動畫切換邏輯 (使用精確 Action 映射表) ---
  useEffect(() => {
    // 使用 actions 判斷是否就緒不再可靠，直接檢查 map
    // if (!actions || Object.keys(actions).length === 0) {
    //   return; 
    // }
    if (!friendlyToActionMap || friendlyToActionMap.size === 0) {
        logger.warn('[BodyModel] Animation effect: Precise Action map is not ready.', LogCategory.ANIMATION);
        return;
    }

    // 1. 獲取目標 Action
    let targetAction: THREE.AnimationAction | undefined | null = null;
    if (currentAnimation) { 
        targetAction = friendlyToActionMap.get(currentAnimation);
        if (!targetAction) {
            logger.error(`[BodyModel] Animation effect: Cannot find Action in precise map for friendly name: ${currentAnimation}`, LogCategory.ANIMATION);
        }
    } else {
        logger.debug('[BodyModel] Animation effect: currentAnimation is null/empty, stopping.', LogCategory.ANIMATION);
    }

    // 2. 獲取正在播放的 action (仍然需要遍歷 map 中的 actions)
    let previousAnimation: THREE.AnimationAction | null = null;
    for (const action of friendlyToActionMap.values()) {
        if (action?.isRunning()) {
            previousAnimation = action;
            break;
        }
    }
    // const previousAnimation = Object.values(actions).find(action => action?.isRunning()); // 不再可靠

    // 3. 執行淡入淡出
    if (previousAnimation && previousAnimation !== targetAction) {
        logger.debug(`[BodyModel] Fading out: ${previousAnimation.getClip().name}`, LogCategory.ANIMATION);
        previousAnimation.fadeOut(0.5);
    }

    if (targetAction) {
        logger.debug(`[BodyModel] Fading in Precise Action for friendly name: ${currentAnimation} (Clip: ${targetAction.getClip().name})`, LogCategory.ANIMATION);
        targetAction
          .reset()
          .setEffectiveTimeScale(1)
          .setEffectiveWeight(1)
          .fadeIn(0.5)
          .play();
    } else if (previousAnimation && !currentAnimation) {
        logger.debug(`[BodyModel] Stopping previous animation: ${previousAnimation.getClip().name}`, LogCategory.ANIMATION);
    } else if (!targetAction && currentAnimation) {
         logger.warn(`[BodyModel] Could not play animation: targetAction not found in precise map for friendly name ${currentAnimation}`, LogCategory.ANIMATION);
    }

  // 依賴項包含 currentAnimation (友好名稱) 和 精確的 map
  }, [currentAnimation, friendlyToActionMap]); 
  // ----------------------------------

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