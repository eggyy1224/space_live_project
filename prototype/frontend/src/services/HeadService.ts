import { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';
import WebSocketService from './WebSocketService';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';
import { getEmotionBaseWeights } from '../config/emotionMappings';
import { HEAD_MODEL_URL } from '../config/modelConfig';
import { createHeadSlice } from '../store/slices/headSlice';

// 後端API URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

// Head 模型數據接口 (移除動畫相關)
interface HeadData {
  headModelUrl: string;
  modelScale: number;
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  morphTargets: Record<string, number>;
  showSpaceBackground: boolean;
  // currentAnimation: string | null; // 移除
}

// 頭部模型服務類 (原 ModelService)
class HeadService {
  private static instance: HeadService; // <-- 重命名
  
  // 這個暫時保留在本地，因為是高頻更新，會進行優化處理
  // private morphTargets: Record<string, number> = {};

  // 不再需要舊的回調列表，全部使用 Zustand 狀態更新
  private wsService: WebSocketService;
  
  // 新增：保存最近的情緒表情
  private _lastEmotionMorphs: Record<string, number> = {};
  
  // 限制更新頻率的變數
  // private _lastNotifyTime: number = 0;
  // private _pendingMorphTargets: Record<string, number> | null = null;
  // private _notifyTimeout: number | null = null;

  // 確保 morphTargetDictionary 被正確定義為類的屬性
  private morphTargetDictionary: { [key: string]: number } = {};

  // 單例模式
  public static getInstance(): HeadService { // <-- 重命名
    if (!HeadService.instance) {
      HeadService.instance = new HeadService();
    }
    return HeadService.instance;
  }

  constructor() {
    // 預加載頭部模型
    this.preloadModel(this.getHeadModelUrl()); // <-- 使用新方法名
    
    // 獲取WebSocket服務實例
    this.wsService = WebSocketService.getInstance();
    
    // 設置WebSocket消息處理器
    this.setupMessageHandlers();

    logger.info('HeadService initialized', LogCategory.MODEL);
  }
  
  // 設置WebSocket消息處理器
  private setupMessageHandlers(): void {
    // --- 移除 morph_update 處理器 --- 
    // // 處理表情更新
    // this.wsService.registerHandler('morph_update', (data) => {
    //   if (data.morphTargets) {
    //     this.handleMorphUpdate(data);
    //   }
    // });
    // --- 移除結束 ---
  }
  
  // --- 移除 handleMorphUpdate 函數 --- 
  // // 處理表情更新 (morph_update)
  // public handleMorphUpdate(data: any): void {
  //   if (!data || typeof data !== 'object') {
  //     logger.warn('Received invalid morph target data', LogCategory.WEBSOCKET);
  //     return;
  //   }
  //   // 迭代更新 Zustand store
  //   Object.entries(data).forEach(([key, value]) => {
  //     if (typeof value === 'number') {
  //       useStore.getState().updateMorphTarget(key, value);
  //     }
  //   });
  //   // logger.debug(`Morph update applied via Zustand: ${JSON.stringify(data)}`, LogCategory.MODEL);
  // }
  // --- 移除結束 ---

  // 預加載模型 (只預加載頭部)
  public preloadModel(modelUrl: string): void {
    // 只預加載傳入的 URL (頭部)
    useGLTF.preload(modelUrl);
    logger.info(`HeadService: Preloading head model: ${modelUrl}`, LogCategory.MODEL);
    // 移除其他模型的預加載
  }

  // 獲取模型是否已加載 (讀取 headModelLoaded)
  public isHeadModelLoaded(): boolean {
    return useStore.getState().headModelLoaded;
  }

  // 設置模型加載狀態 (設置 headModelLoaded)
  public setHeadModelLoaded(loaded: boolean): void {
    useStore.getState().setHeadModelLoaded(loaded);
  }

  // 設置 MorphTarget 字典 (保持不變)
  public setMorphTargetDictionary(dictionary: Record<string, number> | null): void {
    useStore.getState().setMorphTargetDictionary(dictionary);
    this.morphTargetDictionary = dictionary || {};
  }

  // 獲取 MorphTarget 字典 (保持不變)
  public getMorphTargetDictionary(): Record<string, number> | null {
    return useStore.getState().morphTargetDictionary;
  }

  // 設置 MorphTarget 影響值 (已棄用，保持不變)
  public setMorphTargetInfluences(influences: number[] | null): void {}

  // 獲取 MorphTarget 影響值 (已棄用，保持不變)
  public getMorphTargetInfluences(): number[] | null { return null; }

  // --- 移除動畫相關方法 ---
  // public setAvailableAnimations(animations: string[]): void {}
  // public getAvailableAnimations(): string[] { return []; }
  // public setCurrentAnimation(animation: string | null): void {}
  // public getCurrentAnimation(): string | null { return null; }
  // public selectAnimation(animation: string): void {}
  // --- 移除結束 ---

  // 設置模型縮放 (保持不變，操作通用狀態)
  public setModelScale(scale: number): void {
    const store = useStore.getState();
    store.setUniformScale(scale); // 使用新的setUniformScale方法
  }

  // 獲取模型縮放 (保持不變)
  public getModelScale(): number {
    return useStore.getState().modelScale[0];
  }

  // 設置模型旋轉 (保持不變)
  public setModelRotation(rotation: [number, number, number]): void {
    useStore.getState().setModelTransform(undefined, rotation);
  }

  // 獲取模型旋轉 (保持不變)
  public getModelRotation(): [number, number, number] {
    return useStore.getState().modelRotation;
  }

  // 設置模型位置 (保持不變)
  public setModelPosition(position: [number, number, number]): void {
    useStore.getState().setModelTransform(undefined, undefined, position);
  }

  // 獲取模型位置 (保持不變)
  public getModelPosition(): [number, number, number] {
    return useStore.getState().modelPosition;
  }

  // 設置是否顯示太空背景 (保持不變)
  public setShowSpaceBackground(show: boolean): void {
    useStore.getState().setShowSpaceBackground(show);
  }

  // 獲取是否顯示太空背景 (保持不變)
  public getShowSpaceBackground(): boolean {
    return useStore.getState().showSpaceBackground;
  }

  // 更新 MorphTarget 影響值 (保持不變)
  public updateMorphTargetInfluence(name: string, value: number): void {
    if (this.morphTargetDictionary && this.morphTargetDictionary.hasOwnProperty(name)) {
      useStore.getState().updateMorphTarget(name, value);
    } else {
      logger.warn(`[HeadService] Attempted to update unknown morph target: ${name}`, LogCategory.MODEL);
    }
  }

  // 重置所有 Morph Targets (保持不變)
  public resetAllMorphTargets(): void {
    const currentDict = this.getMorphTargetDictionary();
    if (currentDict) {
      const resetTargets: Record<string, number> = {};
      Object.keys(currentDict).forEach(key => {
        resetTargets[key] = 0;
      });
      useStore.getState().setMorphTargets(resetTargets);
      logger.info('HeadService: Reset all morph targets to 0.', LogCategory.MODEL);
    } else {
      logger.warn('HeadService: Cannot reset morph targets, dictionary not available.', LogCategory.MODEL);
    }
    // 清空最近的情緒狀態
    this._lastEmotionMorphs = {};
    // 清空 Zustand 中的 lastJsonMessage (如果它觸發表情)
    useStore.getState().setLastJsonMessage(null);
  }

  // 旋轉模型 (保持不變)
  public rotateModel(direction: 'left' | 'right'): void {
    const currentRotation = this.getModelRotation();
    const delta = direction === 'left' ? Math.PI / 8 : -Math.PI / 8;
    this.setModelRotation([currentRotation[0], currentRotation[1] + delta, currentRotation[2]]);
  }

  // 縮放模型 (保持不變)
  public scaleModel(factor: number): void {
    const currentScale = this.getModelScale();
    this.setModelScale(Math.max(0.1, currentScale * factor)); // Limit min scale
  }

  // 重置模型變換 (保持不變)
  public resetModel(): void {
    // 獲取 slice 的初始狀態定義
    // 雖然 set/get/api 在這裡可能沒用到，但類型要求傳入
    const initialStateDefinition = createHeadSlice(
        useStore.setState as any, // Use type assertion if needed
        useStore.getState as any,
        useStore as any 
    );
    
    // 直接從初始狀態定義中讀取值
    useStore.getState().setModelTransform(
      initialStateDefinition.modelScale,
      initialStateDefinition.modelRotation,
      initialStateDefinition.modelPosition
    );
    logger.info('HeadService: Reset model transform to initial state.', LogCategory.MODEL);
  }

  // 切換背景 (保持不變)
  public toggleBackground(): void {
    this.setShowSpaceBackground(!this.getShowSpaceBackground());
  }

  // 應用預設表情 (保持不變，操作 Morph Targets)
  public async applyPresetExpression(expression: string): Promise<boolean> {
    logger.info(`應用表情預設 (前端): ${expression}`, LogCategory.MODEL);
    try {
      const weights = getEmotionBaseWeights(expression.toLowerCase()); 
      
      if (Object.keys(weights).length > 0) { 
        console.log(`[HeadService] Applying preset from frontend mapping: ${expression}`, JSON.stringify(weights)); 
        
        // 直接設置 Zustand 的 morphTargets 狀態
        useStore.getState().setMorphTargets(weights);
        // --- 新增：清除情緒軌跡狀態 --- 
        useStore.getState().setLastJsonMessage(null); 
        logger.debug(`Applied preset '${expression}' and cleared lastJsonMessage.`, LogCategory.MODEL);
        // --- 新增結束 ---
        this._lastEmotionMorphs = weights; // 保存預設表情狀態
        return true;
      } else {
        logger.error(`無法從前端映射獲取預設表情數據: ${expression}`, LogCategory.MODEL);
        return false;
      }
    } catch (error) {
      logger.error(`應用預設表情時出錯 (${expression}):`, LogCategory.MODEL, error);
      return false;
    }
  }

  // 獲取 Head 模型數據 (移除動畫)
  public getHeadData(): HeadData {
    return {
      headModelUrl: this.getHeadModelUrl(),
      modelScale: this.getModelScale(),
      modelRotation: this.getModelRotation(),
      modelPosition: this.getModelPosition(),
      morphTargets: useStore.getState().morphTargets, // 直接從 store 讀取
      showSpaceBackground: this.getShowSpaceBackground(),
      // currentAnimation: this.getCurrentAnimation(), // 移除
    };
  }

  // 獲取頭部模型 URL
  public getHeadModelUrl(): string { // <-- 重命名
    return HEAD_MODEL_URL; // 使用導入的常數
  }

  // 切換模型 (現在只切換頭部)
  public switchHeadModel(url: string): void { // <-- 重命名
    if (url === this.getHeadModelUrl()) {
      return;
    }
    logger.info(`Switching head model: ${url}`, LogCategory.MODEL);
    this.preloadModel(url);
    this.resetAllMorphTargets();
    useStore.getState().setHeadModelUrl(url); // <-- 使用 setHeadModelUrl
    this.setHeadModelLoaded(false); // <-- 使用 setHeadModelLoaded
  }

  public initialize(morphTargetDictionary: { [key: string]: number } | null): void {
    if (morphTargetDictionary) {
      // 1. 更新 Zustand Store 中的字典
      // 直接調用 Store 的 action，或者通過 Service 內部方法（如果有的話）
      // 這裡我們假設 Store 有 setMorphTargetDictionary action
      useStore.getState().setMorphTargetDictionary(morphTargetDictionary);
      // 同步更新 Service 內部持有的字典引用 (如果其他地方還需要)
      this.morphTargetDictionary = morphTargetDictionary;

      // 2. 計算初始的 Morph Targets 狀態（所有值為 0）
      const initialMorphTargets: Record<string, number> = {};
      Object.keys(morphTargetDictionary).forEach(key => {
        initialMorphTargets[key] = 0;
      });

      // 3. 更新 Zustand Store 中的 Morph Targets 狀態
      // 這裡我們假設 Store 有 setMorphTargets action
      useStore.getState().setMorphTargets(initialMorphTargets);

      // logger.info("ModelService initialized: Zustand dictionary and morphs set.", LogCategory.MODEL, initialMorphTargets);
      // 使用正確的日誌格式
      logger.info({
        msg: "HeadService initialized: Zustand dictionary and morphs set.", 
        details: initialMorphTargets // 將物件放在 details 欄位
      }, LogCategory.MODEL);
    } else {
      // 如果傳入 null (例如模型加載失敗或無 morphs)
      useStore.getState().setMorphTargetDictionary(null);
      useStore.getState().setMorphTargets({}); // 清空 morphs
      this.morphTargetDictionary = {}; // 清空內部引用
      logger.warn("HeadService initialized with null dictionary: Cleared morph state.", LogCategory.MODEL);
    }
  }
}

// React Hook - 使用頭部服務 (原 useModelService) - 修正轉義字符
export function useHeadService() { // <-- 保留這個定義
  // 直接從 Zustand 獲取頭部相關狀態
  const headModelLoaded = useStore((state) => state.headModelLoaded);
  const headModelUrl = useStore((state) => state.headModelUrl);
  const modelScale = useStore((state) => state.modelScale);
  const modelRotation = useStore((state) => state.modelRotation);
  const modelPosition = useStore((state) => state.modelPosition);
  const showSpaceBackground = useStore((state) => state.showSpaceBackground);
  const morphTargets = useStore((state) => state.morphTargets);
  const morphTargetDictionary = useStore((state) => state.morphTargetDictionary);

  const headService = useRef<HeadService>(HeadService.getInstance());

  const setMorphTargetData = useCallback((dictionary: Record<string, number> | null, influences: number[] | null) => {
    if (dictionary) {
      headService.current.initialize(dictionary);
      logger.info('useHeadService: Called HeadService.initialize with new dictionary.', LogCategory.MODEL);
    } else {
       logger.warn('useHeadService: Received null dictionary, state might not be cleared correctly yet.', LogCategory.MODEL);
       headService.current.initialize(null);
    }
  }, []);

  const rotateModel = useCallback((direction: 'left' | 'right') => {
    headService.current.rotateModel(direction);
  }, []);

  const scaleModel = useCallback((factor: number) => {
    headService.current.scaleModel(factor);
  }, []);

  const resetModel = useCallback(() => {
    headService.current.resetModel();
  }, []);

  const toggleBackground = useCallback(() => {
    headService.current.toggleBackground();
  }, []);

  const updateMorphTargetInfluence = useCallback((name: string, value: number) => {
    headService.current.updateMorphTargetInfluence(name, value);
  }, []);

  const resetAllMorphTargets = useCallback(() => {
    headService.current.resetAllMorphTargets();
  }, []);

  const applyPresetExpression = useCallback((expression: string) => {
    return headService.current.applyPresetExpression(expression);
  }, []);

  const switchHeadModel = useCallback((url: string) => {
    headService.current.switchHeadModel(url);
  }, []);

  // 返回 Hook 的公共 API
  return {
    headModelLoaded,
    headModelUrl,
    modelScale,
    modelRotation,
    modelPosition,
    showSpaceBackground,
    morphTargets,
    morphTargetDictionary,
    setMorphTargetData,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    switchHeadModel
  };
}

export default HeadService; // <-- 導出 HeadService 