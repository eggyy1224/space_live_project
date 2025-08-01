import { useCallback, useEffect } from 'react';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';

/**
 * CharacterService - 角色服務 Hook
 * 
 * 完全同步設計說明：
 * - Character 和 Head 模型實現雙向完全同步
 * - 手動表情控制：HeadSlice.morphTargets ⟷ CharacterSlice.characterMorphTargets
 * - 語音口型同步：HeadSlice.audioLipsyncTargets ⟷ CharacterSlice.characterAudioLipsyncTargets
 * - 確保兩個模型在任何情況下都保持一致的表情狀態
 * - 包括用戶手動控制、語音驅動和情緒軌跡
 */
export const useCharacterService = () => {
  // 從 CharacterSlice 獲取角色專屬狀態
  const characterModelLoaded = useStore((state) => state.characterModelLoaded);
  const characterVisible = useStore((state) => state.characterVisible);
  const characterPosition = useStore((state) => state.characterPosition);
  const characterScale = useStore((state) => state.characterScale);
  const characterRotation = useStore((state) => state.characterRotation);
  const availableCharacterAnimations = useStore((state) => state.availableCharacterAnimations);
  const currentCharacterAnimation = useStore((state) => state.currentCharacterAnimation);
  
  // 動畫混合相關狀態 (新增)
  const animationMixMode = useStore((state) => state.animationMixMode);
  const currentAnimationMix = useStore((state) => state.currentAnimationMix);
  const animationMixBlendMode = useStore((state) => state.animationMixBlendMode);
  
  // 角色專屬的表情狀態
  const characterMorphTargets = useStore((state) => state.characterMorphTargets);
  const characterAudioLipsyncTargets = useStore((state) => state.characterAudioLipsyncTargets);
  const characterMorphTargetDictionary = useStore((state) => state.characterMorphTargetDictionary);
  
  // 從 HeadSlice 獲取共享狀態 (用於同步)
  const headMorphTargets = useStore((state) => state.morphTargets);
  const headAudioLipsyncTargets = useStore((state) => state.audioLipsyncTargets);
  const headMorphTargetDictionary = useStore((state) => state.morphTargetDictionary);

  // 從 CharacterSlice 獲取角色專屬操作方法
  const setCharacterModelLoaded = useStore((state) => state.setCharacterModelLoaded);
  const setCharacterVisible = useStore((state) => state.setCharacterVisible);
  const setCharacterPosition = useStore((state) => state.setCharacterPosition);
  const setCharacterScale = useStore((state) => state.setCharacterScale);
  const setCharacterRotation = useStore((state) => state.setCharacterRotation);
  const setAvailableCharacterAnimations = useStore((state) => state.setAvailableCharacterAnimations);
  const setCurrentCharacterAnimation = useStore((state) => state.setCurrentCharacterAnimation);
  const setCharacterMorphTargetDictionary = useStore((state) => state.setCharacterMorphTargetDictionary);
  const setCharacterMorphTargets = useStore((state) => state.setCharacterMorphTargets);
  const updateCharacterMorphTarget = useStore((state) => state.updateCharacterMorphTarget);
  const resetCharacterMorphTargets = useStore((state) => state.resetCharacterMorphTargets);
  const setCharacterAudioLipsyncTarget = useStore((state) => state.setCharacterAudioLipsyncTarget);
  const resetCharacterTransform = useStore((state) => state.resetCharacterTransform);
  
  // 動畫混合相關操作方法 (新增)
  const setAnimationMixMode = useStore((state) => state.setAnimationMixMode);
  const setCurrentAnimationMix = useStore((state) => state.setCurrentAnimationMix);
  const setAnimationMixBlendMode = useStore((state) => state.setAnimationMixBlendMode);
  const updateAnimationMixWeight = useStore((state) => state.updateAnimationMixWeight);
  const clearAnimationMix = useStore((state) => state.clearAnimationMix);
  
  // 從 HeadSlice 獲取操作方法 (用於反向同步)
  const updateHeadMorphTarget = useStore((state) => state.updateMorphTarget);
  const setHeadMorphTargets = useStore((state) => state.setMorphTargets);

  // 包裝操作方法
  const moveCharacter = useCallback((position: [number, number, number]) => {
    setCharacterPosition(position);
    logger.info(`[CharacterService] Moved character to: [${position.join(', ')}]`, LogCategory.MODEL);
  }, [setCharacterPosition]);

  const rotateCharacter = useCallback((rotation: [number, number, number]) => {
    setCharacterRotation(rotation);
    logger.info(`[CharacterService] Rotated character to: [${rotation.join(', ')}]`, LogCategory.MODEL);
  }, [setCharacterRotation]);

  // 表情控制方法 - 實現雙向同步
  const applyCharacterExpression = useCallback((expression: Record<string, number>) => {
    // 同時更新兩個模型的表情
    Object.entries(expression).forEach(([name, value]) => {
      updateCharacterMorphTarget(name, value);
      updateHeadMorphTarget(name, value); // 同步到 Head
    });
    logger.info(`[CharacterService] Applied synchronized expression with ${Object.keys(expression).length} morph targets`, LogCategory.MODEL);
  }, [updateCharacterMorphTarget, updateHeadMorphTarget]);

  // 動畫混合便利方法 (新增)
  const playAnimationMix = useCallback((animations: Array<{
    name: string;
    weight: number;
    loop?: boolean;
    speed?: number;
  }>, blendMode: 'normal' | 'additive' | 'override' = 'normal') => {
    const formattedAnimations = animations.map(anim => ({
      name: anim.name,
      weight: anim.weight,
      loop: anim.loop !== undefined ? anim.loop : true,
      speed: anim.speed !== undefined ? anim.speed : 1.0
    }));
    
    setAnimationMixMode(true);
    setCurrentAnimationMix(formattedAnimations);
    setAnimationMixBlendMode(blendMode);
    
    logger.info(`[CharacterService] Playing animation mix with ${animations.length} animations (${blendMode} mode)`, LogCategory.MODEL);
  }, [setAnimationMixMode, setCurrentAnimationMix, setAnimationMixBlendMode]);

  const stopAnimationMix = useCallback(() => {
    setAnimationMixMode(false);
    clearAnimationMix();
    logger.info(`[CharacterService] Stopped animation mix`, LogCategory.MODEL);
  }, [setAnimationMixMode, clearAnimationMix]);

  const adjustAnimationWeight = useCallback((animationName: string, weight: number) => {
    if (weight < 0 || weight > 1) {
      logger.warn(`[CharacterService] Invalid weight ${weight} for animation ${animationName}, must be 0-1`, LogCategory.MODEL);
      return;
    }
    updateAnimationMixWeight(animationName, weight);
    logger.info(`[CharacterService] Adjusted ${animationName} weight to ${weight}`, LogCategory.MODEL);
  }, [updateAnimationMixWeight]);

  // 同步 HeadSlice 的手動表情到 Character
  useEffect(() => {
    if (Object.keys(headMorphTargets).length > 0) {
      const hasChanges = Object.keys(headMorphTargets).some(
        key => characterMorphTargets[key] !== headMorphTargets[key]
      );
      
      if (hasChanges) {
        setCharacterMorphTargets(headMorphTargets);
        logger.info(`[CharacterService] Synced ${Object.keys(headMorphTargets).length} morph targets from Head to Character`, LogCategory.MODEL);
      }
    } else if (Object.keys(characterMorphTargets).length > 0) {
      // Head 清空時也清空 Character
      resetCharacterMorphTargets();
      logger.info(`[CharacterService] Reset character morph targets to sync with Head`, LogCategory.MODEL);
    }
  }, [headMorphTargets, characterMorphTargets, setCharacterMorphTargets, resetCharacterMorphTargets]);

  // 同步 HeadSlice 的語音口型到 Character
  useEffect(() => {
    if (Object.keys(headAudioLipsyncTargets).length > 0) {
      const hasChanges = Object.keys(headAudioLipsyncTargets).some(
        key => characterAudioLipsyncTargets[key] !== headAudioLipsyncTargets[key]
      );
      
      if (hasChanges) {
        Object.entries(headAudioLipsyncTargets).forEach(([key, value]) => {
          setCharacterAudioLipsyncTarget(key, value);
        });
        logger.info(`[CharacterService] Synced ${Object.keys(headAudioLipsyncTargets).length} audio lipsync targets from Head to Character`, LogCategory.MODEL);
      }
    }
  }, [headAudioLipsyncTargets, characterAudioLipsyncTargets, setCharacterAudioLipsyncTarget]);

  // 初始化時的日誌
  useEffect(() => {
    logger.info('[CharacterService] Initializing character service with complete synchronization', LogCategory.GENERAL);
  }, []);

  // 直接複製分析 json 的 animationNames 陣列
  const CHARACTER0801_ANIMATIONS = [
    "空體Action", "運動2", "漂浮", "運動1", "Tpose", "不穩", "划手機", "漂浮2", "臥躺", "舞步1", "舞步2", "舞步3", "飛1", "飛2", "瑜珈動作1", "瑜珈動作2", "瑜珈動作3", "瑜珈動作4", "漂浮.001", "瑜珈動作5", "瑜珈動作6", "瑜珈動作7", "瑜珈動作8", "瑜珈動作9", "瑜珈動作10", "瑜珈動作11", "瑜珈動作12", "瑜珈動作13", "瑜珈動作14", "瑜珈動作15", "瑜珈動作16", "瑜珈動作17", "瑜珈動作18", "瑜珈動作19", "瑜珈動作20"
  ];

  // 返回值 - 提供兩套狀態以支持完全同步
  return {
    // 基本模型狀態
    characterModelUrl: '/models/character0801.glb',
    characterModelLoaded,
    characterVisible,
    characterPosition,
    characterScale,
    characterRotation,
    
    // 動畫狀態
    availableCharacterAnimations: CHARACTER0801_ANIMATIONS,
    currentCharacterAnimation,
    
    // 動畫混合相關狀態 (新增)
    animationMixMode,
    currentAnimationMix,
    animationMixBlendMode,
    
    // 表情狀態 - 使用合併後的狀態 (確保同步)
    morphTargets: { ...characterMorphTargets, ...headMorphTargets }, // 合併手動表情
    audioLipsyncTargets: { ...characterAudioLipsyncTargets, ...headAudioLipsyncTargets }, // 合併語音口型
    morphTargetDictionary: characterMorphTargetDictionary || headMorphTargetDictionary,

    // 操作方法
    setCharacterModelLoaded,
    setCharacterVisible,
    moveCharacter,
    rotateCharacter,
    updateCharacterMorphTarget: (targetOrKey: string | Record<string, number>, value?: number) => {
      if (typeof targetOrKey === 'string' && typeof value === 'number') {
        // 單個 morph target 更新
        applyCharacterExpression({ [targetOrKey]: value });
      } else if (typeof targetOrKey === 'object') {
        // 批量 morph targets 更新
        applyCharacterExpression(targetOrKey);
      }
    },
    applyCharacterExpression,
    resetCharacterMorphTargets: () => {
      resetCharacterMorphTargets();
      setHeadMorphTargets({}); // 同時重置 Head
      logger.info(`[CharacterService] Reset morph targets for both models`, LogCategory.MODEL);
    },
    resetCharacterTransform,
    setCharacterMorphTargetDictionary,
    setCharacterMorphTargets: (targets: Record<string, number>) => {
      setCharacterMorphTargets(targets);
      setHeadMorphTargets(targets); // 同步到 Head
      logger.info(`[CharacterService] Set morph targets for both models`, LogCategory.MODEL);
    },
    setAnimationMixMode,
    setCurrentAnimationMix,
    setAnimationMixBlendMode,
    updateAnimationMixWeight,
    clearAnimationMix,
    playAnimationMix,
    stopAnimationMix,
    adjustAnimationWeight,
  };
}; 