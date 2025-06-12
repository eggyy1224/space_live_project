import { useCallback, useEffect } from 'react';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';
import { CHARACTER_MODEL_URL } from '../store/slices/characterSlice';

/**
 * CharacterService Hook - 管理角色模型狀態和操作
 */
export const useCharacterService = () => {
  // 從 Store 獲取狀態
  const characterModelLoaded = useStore((state) => state.characterModelLoaded);
  const characterVisible = useStore((state) => state.characterVisible);
  const characterPosition = useStore((state) => state.characterPosition);
  const characterScale = useStore((state) => state.characterScale);
  const characterRotation = useStore((state) => state.characterRotation);
  const availableCharacterAnimations = useStore((state) => state.availableCharacterAnimations);
  const currentCharacterAnimation = useStore((state) => state.currentCharacterAnimation);
  const morphTargets = useStore((state) => state.morphTargets);
  const morphTargetDictionary = useStore((state) => state.morphTargetDictionary);

  // 從 Store 獲取操作方法
  const setCharacterModelLoaded = useStore((state) => state.setCharacterModelLoaded);
  const setCharacterVisible = useStore((state) => state.setCharacterVisible);
  const setCharacterPosition = useStore((state) => state.setCharacterPosition);
  const setCharacterScale = useStore((state) => state.setCharacterScale);
  const setCharacterRotation = useStore((state) => state.setCharacterRotation);
  const setAvailableCharacterAnimations = useStore((state) => state.setAvailableCharacterAnimations);
  const setCurrentCharacterAnimation = useStore((state) => state.setCurrentCharacterAnimation);
  const setCharacterMorphTargets = useStore((state) => state.setCharacterMorphTargets);
  const setCharacterMorphTargetDictionary = useStore((state) => state.setCharacterMorphTargetDictionary);
  const updateCharacterMorphTarget = useStore((state) => state.updateCharacterMorphTarget);
  const resetCharacterMorphTargets = useStore((state) => state.resetCharacterMorphTargets);
  const resetCharacterTransform = useStore((state) => state.resetCharacterTransform);

  // 包裝操作方法
  const toggleCharacterVisibility = useCallback(() => {
    const newVisibility = !characterVisible;
    setCharacterVisible(newVisibility);
    logger.info(`[CharacterService] Character visibility toggled: ${newVisibility}`, LogCategory.MODEL);
  }, [characterVisible, setCharacterVisible]);

  const selectCharacterAnimation = useCallback((animationName: string) => {
    if (availableCharacterAnimations.includes(animationName)) {
      setCurrentCharacterAnimation(animationName);
      logger.info(`[CharacterService] Animation changed to: ${animationName}`, LogCategory.ANIMATION);
    } else {
      logger.warn(`[CharacterService] Animation not found: ${animationName}`, LogCategory.ANIMATION);
    }
  }, [availableCharacterAnimations, setCurrentCharacterAnimation]);

  const adjustCharacterScale = useCallback((scaleFactor: number) => {
    const newScale = Math.max(0.1, Math.min(3, characterScale * scaleFactor));
    setCharacterScale(newScale);
    logger.info(`[CharacterService] Character scale adjusted to: ${newScale}`, LogCategory.MODEL);
  }, [characterScale, setCharacterScale]);

  const moveCharacter = useCallback((direction: 'left' | 'right' | 'forward' | 'backward' | 'up' | 'down', distance: number = 0.5) => {
    const [x, y, z] = characterPosition;
    let newPosition: [number, number, number];

    switch (direction) {
      case 'left':
        newPosition = [x - distance, y, z];
        break;
      case 'right':
        newPosition = [x + distance, y, z];
        break;
      case 'forward':
        newPosition = [x, y, z - distance];
        break;
      case 'backward':
        newPosition = [x, y, z + distance];
        break;
      case 'up':
        newPosition = [x, y + distance, z];
        break;
      case 'down':
        newPosition = [x, y - distance, z];
        break;
      default:
        newPosition = [x, y, z];
    }

    setCharacterPosition(newPosition);
    logger.info(`[CharacterService] Character moved ${direction} to: [${newPosition.join(', ')}]`, LogCategory.MODEL);
  }, [characterPosition, setCharacterPosition]);

  const rotateCharacter = useCallback((axis: 'x' | 'y' | 'z', angle: number) => {
    const [x, y, z] = characterRotation;
    let newRotation: [number, number, number];

    switch (axis) {
      case 'x':
        newRotation = [x + angle, y, z];
        break;
      case 'y':
        newRotation = [x, y + angle, z];
        break;
      case 'z':
        newRotation = [x, y, z + angle];
        break;
      default:
        newRotation = [x, y, z];
    }

    setCharacterRotation(newRotation);
    logger.info(`[CharacterService] Character rotated around ${axis}-axis by ${angle} to: [${newRotation.join(', ')}]`, LogCategory.MODEL);
  }, [characterRotation, setCharacterRotation]);

  const applyCharacterExpression = useCallback((expression: Record<string, number>) => {
    Object.entries(expression).forEach(([name, value]) => {
      updateCharacterMorphTarget(name, value);
    });
    logger.info(`[CharacterService] Applied expression with ${Object.keys(expression).length} morph targets`, LogCategory.MODEL);
  }, [updateCharacterMorphTarget]);

  // 初始化時預加載模型
  useEffect(() => {
    logger.info('[CharacterService] Initializing character service', LogCategory.SERVICE);
  }, []);

  return {
    // 狀態
    characterModelUrl: CHARACTER_MODEL_URL,
    characterModelLoaded,
    characterVisible,
    characterPosition,
    characterScale,
    characterRotation,
    availableCharacterAnimations,
    currentCharacterAnimation,
    morphTargets,
    morphTargetDictionary,

    // 操作方法
    setCharacterModelLoaded,
    toggleCharacterVisibility,
    setCharacterPosition,
    setCharacterScale,
    setCharacterRotation,
    selectCharacterAnimation,
    adjustCharacterScale,
    moveCharacter,
    rotateCharacter,
    updateCharacterMorphTarget,
    applyCharacterExpression,
    resetCharacterMorphTargets,
    resetCharacterTransform,
    setCharacterMorphTargetDictionary,
    setCharacterMorphTargets,
  };
}; 