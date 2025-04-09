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
  // 返回一個函數，用於在每一幀計算基於軌跡的情緒權重
  calculateCurrentTrajectoryWeights: () => Record<string, number>; 
}

// 定義說話狀態的 Blendshape 目標值 (可配置)
// const SPEAKING_JAW_OPEN = 0.7; // 說話時下巴張開程度 (原值)
// const SPEAKING_JAW_OPEN = 0.85; // <-- 增大基礎張嘴幅度
// const IDLE_MOUTH_CLOSE = 0.1; // 不說話時嘴巴閉合程度

/**
 * Custom hook to manage emotional trajectory and calculate current emotion weights based on time.
 */
export const useEmotionalSpeaking = (): EmotionalSpeakingControl => {
  // const isSpeaking = useStore((state) => state.isSpeaking);
  const audioStartTime = useStore((state) => state.audioStartTime);
  const lastMessage = useStore((state) => state.lastJsonMessage);

  const [currentTrajectory, setCurrentTrajectory] = useState<EmotionalTrajectory | null>(null);
  const [localReferenceTime, setLocalReferenceTime] = useState<number | null>(null);
  const [trajectoryActive, setTrajectoryActive] = useState<boolean>(false);
  const trajectoryCompleted = useRef<boolean>(false);

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
          // --- 新增：重置本地參考時間和標記 ---
          setLocalReferenceTime(null); // 會在下面的 useEffect 中設定
          setTrajectoryActive(true);
          trajectoryCompleted.current = false;
          // --- 新增結束 ---
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

  // --- 新增：監聽 audioStartTime 變化，設置本地參考時間 ---
  useEffect(() => {
    if (audioStartTime !== null && trajectoryActive && localReferenceTime === null) {
      // 音頻開始播放且軌跡處於活躍狀態，設置本地參考時間
      setLocalReferenceTime(audioStartTime);
      logger.info(`[useEmotionalSpeaking] Setting localReferenceTime to ${audioStartTime}`, LogCategory.ANIMATION);
    }
  }, [audioStartTime, trajectoryActive, localReferenceTime]);
  // --- 新增結束 ---

  // --- 計算當前情緒權重函數 (邏輯不變) ---
  const calculateCurrentEmotionWeights = useCallback((): Record<string, number> => {
    if (!currentTrajectory || (!trajectoryActive && !trajectoryCompleted.current)) {
        return getEmotionBaseWeights('neutral');
    }
    let referenceTime = localReferenceTime !== null 
        ? localReferenceTime 
        : (audioStartTime !== null ? audioStartTime : null);
    if (referenceTime === null && trajectoryActive) {
        referenceTime = performance.now();
        setLocalReferenceTime(referenceTime);
        logger.info(`[calculateCurrentEmotionWeights] No reference time, setting new one: ${referenceTime}`, LogCategory.ANIMATION);
    }
    if (referenceTime === null) {
        logger.debug('[calculateCurrentEmotionWeights] No reference time available, returning neutral.', LogCategory.ANIMATION);
        return getEmotionBaseWeights('neutral');
    }
    const elapsedTime = (performance.now() - referenceTime) / 1000;
    const duration = currentTrajectory.duration;
    if (elapsedTime >= duration) {
        if (trajectoryActive) {
            setTrajectoryActive(false);
            trajectoryCompleted.current = true;
            logger.info('[calculateCurrentEmotionWeights] Trajectory completed, maintaining final emotion.', LogCategory.ANIMATION);
        }
        const keyframes = currentTrajectory.keyframes;
        if (keyframes && keyframes.length > 0) {
            const lastKeyframe = keyframes[keyframes.length - 1];
            return getEmotionBaseWeights(lastKeyframe.tag);
        }
        return getEmotionBaseWeights('neutral');
    }
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
    logger.debug(`[calculateCurrentEmotionWeights] Progress: ${progress.toFixed(2)}, elapsed: ${elapsedTime.toFixed(2)}s, duration: ${duration.toFixed(2)}s`, LogCategory.ANIMATION);
    return currentEmotionWeights;
  }, [currentTrajectory, audioStartTime, localReferenceTime, trajectoryActive]);
  // --- 函數結束 ---

  // --- 重命名並簡化導出函數 --- 
  const calculateCurrentTrajectoryWeights = useCallback((): Record<string, number> => {
    // 直接返回純粹的情緒權重
    const emotionWeights = calculateCurrentEmotionWeights();
    // logger.debug('[calculateCurrentTrajectoryWeights] Returning pure emotion weights:', LogCategory.ANIMATION, emotionWeights);
    return emotionWeights;
  }, [calculateCurrentEmotionWeights]);
  // --- 簡化結束 ---

  // 返回更新後的接口
  return {
    calculateCurrentTrajectoryWeights, // 使用新名稱
  };
}; 