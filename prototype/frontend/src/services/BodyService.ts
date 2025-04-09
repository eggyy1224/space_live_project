import { useState, useEffect, useRef, useCallback } from 'react';
import { useGLTF } from '@react-three/drei';
import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';
import { BODY_MODEL_URL } from '../config/modelConfig';

// 身體模型服務類
class BodyService {
  private static instance: BodyService;

  // 單例模式
  public static getInstance(): BodyService {
    if (!BodyService.instance) {
      BodyService.instance = new BodyService();
    }
    return BodyService.instance;
  }

  constructor() {
    // 預加載身體模型
    this.preloadModel(this.getBodyModelUrl());
    logger.info('BodyService initialized', LogCategory.MODEL);
  }

  // 預加載模型
  public preloadModel(modelUrl: string): void {
    useGLTF.preload(modelUrl);
    logger.info(`BodyService: Preloading body model: ${modelUrl}`, LogCategory.MODEL);
  }

  // 獲取身體模型 URL
  public getBodyModelUrl(): string {
    return BODY_MODEL_URL;
  }

  // 設置身體模型加載狀態
  public setBodyModelLoaded(loaded: boolean): void {
    useStore.getState().setBodyModelLoaded(loaded);
  }

  // 設置可用動畫列表
  public setAvailableAnimations(animations: string[]): void {
    useStore.getState().setAvailableAnimations(animations);
  }

  // 選擇當前動畫
  public selectAnimation(animation: string | null): void {
    useStore.getState().setCurrentAnimation(animation);
  }

  // 切換身體模型 (如果需要)
  public switchBodyModel(url: string): void {
    if (url === this.getBodyModelUrl()) {
      return;
    }
    logger.info(`Switching body model: ${url}`, LogCategory.MODEL);
    this.preloadModel(url);
    useStore.getState().setBodyModelUrl(url); // 會自動重置動畫和加載狀態
  }
}

// React Hook - 使用身體服務
export function useBodyService() {
  // 從 Zustand 獲取狀態
  const bodyModelUrl = useStore((state) => state.bodyModelUrl);
  const bodyModelLoaded = useStore((state) => state.bodyModelLoaded);
  const availableAnimations = useStore((state) => state.availableAnimations);
  const currentAnimation = useStore((state) => state.currentAnimation);

  const bodyService = useRef<BodyService>(BodyService.getInstance());

  // 封裝 Actions
  const selectAnimation = useCallback((animation: string | null) => {
    bodyService.current.selectAnimation(animation);
  }, []);

  const setAvailableAnimations = useCallback((animations: string[]) => {
    bodyService.current.setAvailableAnimations(animations);
  }, []);
  
  const setBodyModelLoaded = useCallback((loaded: boolean) => {
      bodyService.current.setBodyModelLoaded(loaded);
  }, []);

  const switchBodyModel = useCallback((url: string) => {
      bodyService.current.switchBodyModel(url);
  }, []);

  return {
    bodyModelUrl,
    bodyModelLoaded,
    availableAnimations,
    currentAnimation,
    selectAnimation,
    setAvailableAnimations, // 暴露給 BodyModel 組件使用
    setBodyModelLoaded, // 暴露給 BodyModel 組件使用
    switchBodyModel // 如果需要切換身體模型
  };
}

export default BodyService; 