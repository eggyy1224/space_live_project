import { useState, useEffect, useCallback, useRef } from 'react';
import { useStore } from '../store';
import { getEmotionBaseWeights } from '../config/emotionMappings';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager';

// 定義情緒關鍵幀的類型
interface EmotionKeyframe {
  tag: string;
  proportion: number; // 0.0 to 1.0
}

// 定義後端傳來的 emotionalTrajectory 數據類型
interface EmotionalTrajectory {
  duration: number;
  keyframes: EmotionKeyframe[];
}

// 更新 Hook 的返回值類型
interface EmotionalSpeakingControl {
  // 返回一個函數，用於在每一幀計算 **最終混合後** 的 Blendshape 目標權重
  calculateFinalWeights: () => Record<string, number>;
}

// 定義說話狀態的 Blendshape 目標值 (可配置)
const SPEAKING_JAW_OPEN = 0.7; // 說話時下巴張開程度
const IDLE_MOUTH_CLOSE = 0.1; // 不說話時嘴巴閉合程度

/**
 * Custom hook to manage emotional trajectory, speaking state, and calculate final blendshape targets.
 */
export const useEmotionalSpeaking = (): EmotionalSpeakingControl => {
  const isSpeaking = useStore((state) => state.isSpeaking);
  const audioStartTime = useStore((state) => state.audioStartTime);
  const lastMessage = useStore((state) => state.lastJsonMessage); // Assume exists, linter warning ignored

  const [currentTrajectory, setCurrentTrajectory] = useState<EmotionalTrajectory | null>(null);

  // Effect to handle incoming trajectories
  useEffect(() => {
    // Add detailed logging here
    logger.debug('[useEmotionalSpeaking] useEffect triggered by lastMessage change. Current lastMessage:', LogCategory.ANIMATION, JSON.stringify(lastMessage));
    
    if (lastMessage?.type === 'emotionalTrajectory') {
      logger.info('[useEmotionalSpeaking] Detected emotionalTrajectory message type.', LogCategory.ANIMATION);
      const payload = lastMessage.payload;
      if (payload && typeof payload.duration === 'number' && Array.isArray(payload.keyframes)) {
          logger.info('[useEmotionalSpeaking] Payload is valid. Processing trajectory...', LogCategory.ANIMATION);
          const trajectoryData = payload as EmotionalTrajectory;
          trajectoryData.keyframes.sort((a, b) => a.proportion - b.proportion);
          setCurrentTrajectory(trajectoryData); // Update local state
          logger.info('[useEmotionalSpeaking] Successfully set currentTrajectory:', LogCategory.ANIMATION, JSON.stringify(trajectoryData, null, 2));
      } else {
          logger.warn(
              '[useEmotionalSpeaking] Received invalid trajectory data format:',
              LogCategory.ANIMATION,
              JSON.stringify(payload)
          );
      }
    } else {
      // Log if it's not the expected type or null
      if (lastMessage) {
        logger.debug(`[useEmotionalSpeaking] lastMessage type is not 'emotionalTrajectory': ${lastMessage?.type}`, LogCategory.ANIMATION);
      } else {
        logger.debug('[useEmotionalSpeaking] lastMessage is null.', LogCategory.ANIMATION);
      }
    }
  }, [lastMessage]); 

  // --- Step 3.2: 計算基礎說話權重 ---
  const calculateSpeakingWeights = useCallback((): Record<string, number> => {
    if (isSpeaking) {
      return {
        jawOpen: SPEAKING_JAW_OPEN, 
        mouthClose: 0 // 說話時嘴巴不強制閉合
      };
    } else {
      return {
        jawOpen: 0, // 不說話時下巴閉合
        mouthClose: IDLE_MOUTH_CLOSE // 嘴唇閉合
      };
    }
  }, [isSpeaking]);
  // --------------------------------

  // --- Step 3.1: 計算當前情緒權重 --- (Code from previous step, slightly renamed)
  const calculateCurrentEmotionWeights = useCallback((): Record<string, number> => {
    if (!currentTrajectory || audioStartTime === null || !isSpeaking) {
        // Log why it's returning neutral
        if (!isSpeaking) logger.debug('[calculateCurrentEmotionWeights] Returning neutral because isSpeaking is false.', LogCategory.ANIMATION);
        else if (!currentTrajectory) logger.debug('[calculateCurrentEmotionWeights] Returning neutral because currentTrajectory is null.', LogCategory.ANIMATION);
        else logger.debug('[calculateCurrentEmotionWeights] Returning neutral because audioStartTime is null.', LogCategory.ANIMATION);
        return getEmotionBaseWeights('neutral');
    }

    const elapsedTime = (performance.now() - audioStartTime) / 1000;
    const duration = currentTrajectory.duration;
    if (duration <= 0) return getEmotionBaseWeights('neutral');

    const progress = Math.max(0, Math.min(elapsedTime / duration, 1.0));
    const keyframes = currentTrajectory.keyframes;

    if (!keyframes || keyframes.length === 0) return getEmotionBaseWeights('neutral');
    if (keyframes.length === 1) return getEmotionBaseWeights(keyframes[0].tag);

    let prevFrame = keyframes[0];
    let nextFrame = keyframes[keyframes.length - 1];

    for (let i = 0; i < keyframes.length; i++) {
        if (keyframes[i].proportion >= progress) {
            nextFrame = keyframes[i];
            prevFrame = i > 0 ? keyframes[i - 1] : nextFrame;
            break;
        }
        if (i === keyframes.length - 1) {
            prevFrame = keyframes[i];
            nextFrame = keyframes[i];
        }
    }

    if (prevFrame === nextFrame || prevFrame.proportion >= nextFrame.proportion) {
        return getEmotionBaseWeights(nextFrame.tag);
    }

    const segmentProportion = nextFrame.proportion - prevFrame.proportion;
    const progressInSegment = progress - prevFrame.proportion;
    const localProgress = segmentProportion > 0.0001 ? Math.max(0, Math.min(progressInSegment / segmentProportion, 1.0)) : 0;

    const weightsPrev = getEmotionBaseWeights(prevFrame.tag);
    const weightsNext = getEmotionBaseWeights(nextFrame.tag);
    const currentEmotionWeights: Record<string, number> = {};
    const allKeys = [...new Set([...Object.keys(weightsPrev), ...Object.keys(weightsNext)])];

    allKeys.forEach(key => {
        const prevValue = weightsPrev[key] ?? 0;
        const nextValue = weightsNext[key] ?? 0;
        currentEmotionWeights[key] = THREE.MathUtils.lerp(prevValue, nextValue, localProgress);
    });

    // Log the calculated weights
    logger.debug('[calculateCurrentEmotionWeights] Calculated weights:', LogCategory.ANIMATION, JSON.stringify(currentEmotionWeights));
    return currentEmotionWeights;
  }, [currentTrajectory, audioStartTime, isSpeaking]);
  // -------------------------------

  // --- Step 3.3: 混合權重 (下一步實現) ---
  const calculateFinalWeights = useCallback((): Record<string, number> => {
    const emotionWeights = calculateCurrentEmotionWeights();
    const speakingWeights = calculateSpeakingWeights();
    
    // TODO: 實現混合策略
    const finalWeights = { ...emotionWeights }; // 初始為情緒權重

    // 示例混合策略：
    // jawOpen: 取說話和情緒中的最大值 (說話優先)
    finalWeights.jawOpen = Math.max(speakingWeights.jawOpen ?? 0, emotionWeights.jawOpen ?? 0);
    // mouthClose: 只在不說話時應用
    finalWeights.mouthClose = speakingWeights.mouthClose; // 直接使用說話狀態的 mouthClose
    
    // 其他權重暫時直接使用情緒權重，未來可添加更複雜混合

    // Log the final weights before returning
    logger.debug('[calculateFinalWeights] Calculated final weights:', LogCategory.ANIMATION, JSON.stringify(finalWeights));
    return finalWeights;

  }, [calculateCurrentEmotionWeights, calculateSpeakingWeights]);
  // -------------------------------

  // 返回最終的計算函數
  return {
    calculateFinalWeights,
  };
}; 