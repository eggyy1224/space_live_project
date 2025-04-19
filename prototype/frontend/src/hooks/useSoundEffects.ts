import { useEffect, useState, useCallback } from 'react';
import SoundEffectService from '../services/SoundEffectService';
import soundEffects from '../config/soundEffectsConfig';
import logger, { LogCategory } from '../utils/LogManager';

/**
 * 音效Hook，用於在組件中使用音效服務
 */
export const useSoundEffects = () => {
  // 音效服務狀態
  const [isReady, setIsReady] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [globalVolume, setGlobalVolume] = useState<number>(0.8); // 默認音量80%
  const [loadedSounds, setLoadedSounds] = useState<string[]>([]);
  
  // 獲取服務單例
  const soundService = SoundEffectService.getInstance();
  
  /**
   * 初始化並加載音效資源
   */
  const initAndLoadSounds = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // 加載音效資源
      const success = await soundService.loadSoundEffects(soundEffects);
      
      if (success) {
        logger.info('[useSoundEffects] Sound effects loaded successfully', LogCategory.AUDIO);
        setIsReady(true);
        setLoadedSounds(soundService.getLoadedSounds());
      } else {
        logger.warn('[useSoundEffects] Failed to load some sound effects', LogCategory.AUDIO);
      }
    } catch (error) {
      logger.error('[useSoundEffects] Error initializing sound effects:', LogCategory.AUDIO, error);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  /**
   * 解鎖AudioContext（需要在用戶互動後調用）
   */
  const unlockAudioContext = useCallback(async (): Promise<boolean> => {
    try {
      const result = await soundService.unlockAudioContext();
      if (result) {
        // 如果解鎖成功且音效尚未載入，則加載音效
        if (!isReady && !isLoading) {
          initAndLoadSounds();
        }
      }
      return result;
    } catch (error) {
      logger.error('[useSoundEffects] Error unlocking audio context:', LogCategory.AUDIO, error);
      return false;
    }
  }, [isReady, isLoading, initAndLoadSounds]);
  
  /**
   * 播放單個音效
   */
  const playSingleSoundEffect = useCallback((name: string, volume?: number): boolean => {
    try {
      return soundService.playSingleSoundEffect(name, volume);
    } catch (error) {
      logger.error(`[useSoundEffects] Error playing sound ${name}:`, LogCategory.AUDIO, error);
      return false;
    }
  }, []);
  
  /**
   * 播放合成音效
   */
  const playSynthSound = useCallback((type: string, options: any = {}): boolean => {
    try {
      return soundService.playSynthSound(type, options);
    } catch (error) {
      logger.error(`[useSoundEffects] Error playing synth sound ${type}:`, LogCategory.AUDIO, error);
      return false;
    }
  }, []);
  
  /**
   * 播放合成音效序列
   */
  const playSynthSequence = useCallback((effects: Array<{
    type: string;
    options?: any;
    startTime?: number;
  }>): boolean => {
    try {
      return soundService.playSynthSequence(effects);
    } catch (error) {
      logger.error('[useSoundEffects] Error processing synth sequence:', LogCategory.AUDIO, error);
      return false;
    }
  }, []);
  
  /**
   * 處理音效序列指令
   */
  const playSoundEffectFromCommand = useCallback((effects: Array<{
    name: string;
    type?: string;
    params?: { volume?: number };
    startTime?: number;
  }>): boolean => {
    try {
      return soundService.playSoundEffectFromCommand(effects);
    } catch (error) {
      logger.error('[useSoundEffects] Error processing sound effect command:', LogCategory.AUDIO, error);
      return false;
    }
  }, []);
  
  /**
   * 設置全局音量
   */
  const setGlobalVolumeLevel = useCallback((volume: number) => {
    try {
      // 確保音量在0-1範圍內
      const safeVolume = Math.max(0, Math.min(1, volume));
      
      // 更新內部狀態
      setGlobalVolume(safeVolume);
      
      // 設置服務音量
      soundService.setGlobalVolume(safeVolume);
      
      logger.info(`[useSoundEffects] Global volume set to ${safeVolume.toFixed(2)}`, LogCategory.AUDIO);
    } catch (error) {
      logger.error('[useSoundEffects] Error setting global volume:', LogCategory.AUDIO, error);
    }
  }, []);
  
  /**
   * 停止所有音效播放
   */
  const stopAllSounds = useCallback(() => {
    try {
      soundService.stopAllSounds();
    } catch (error) {
      logger.error('[useSoundEffects] Error stopping sounds:', LogCategory.AUDIO, error);
    }
  }, []);
  
  /**
   * 停止特定音效播放
   */
  const stopSound = useCallback((name: string): boolean => {
    try {
      return soundService.stopSound(name);
    } catch (error) {
      logger.error(`[useSoundEffects] Error stopping sound ${name}:`, LogCategory.AUDIO, error);
      return false;
    }
  }, []);
  
  // 在首次渲染時獲取服務狀態
  useEffect(() => {
    const status = soundService.getStatus();
    setIsReady(status.isReady);
    setIsLoading(status.isLoading);
    
    // 如果服務已準備好，獲取已加載的音效
    if (status.isReady) {
      setLoadedSounds(soundService.getLoadedSounds());
    }
  }, []);
  
  // 在組件卸載時停止所有音效
  useEffect(() => {
    return () => {
      // 只在組件卸載時執行
      stopAllSounds();
    };
  }, [stopAllSounds]);
  
  // 返回Hook接口
  return {
    isReady,
    isLoading,
    globalVolume,
    loadedSounds,
    unlockAudioContext,
    initAndLoadSounds,
    playSingleSoundEffect,
    playSynthSound,
    playSynthSequence,
    playSoundEffectFromCommand,
    setGlobalVolume: setGlobalVolumeLevel,
    stopAllSounds,
    stopSound
  };
};

export default useSoundEffects; 