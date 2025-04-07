import { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';
import WebSocketService from './WebSocketService';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';
import { getPresetExpression } from './api';

// 後端API URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

// 模型數據接口
interface ModelData {
  modelUrl: string;
  modelScale: number;
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  morphTargets: Record<string, number>;
  showSpaceBackground: boolean;
  currentAnimation: string | null;
}

// 模型服務類
class ModelService {
  private static instance: ModelService;
  
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
  public static getInstance(): ModelService {
    if (!ModelService.instance) {
      ModelService.instance = new ModelService();
    }
    return ModelService.instance;
  }

  constructor() {
    // 預加載模型
    this.preloadModel(this.getModelUrl());
    
    // 獲取WebSocket服務實例
    this.wsService = WebSocketService.getInstance();
    
    // 設置WebSocket消息處理器
    this.setupMessageHandlers();

    logger.info('ModelService initialized', LogCategory.MODEL);
  }
  
  // 設置WebSocket消息處理器
  private setupMessageHandlers(): void {
    // 處理唇型同步更新
    this.wsService.registerHandler('lipsync_update', (data) => {
      if (data.morphTargets) {
        this.handleLipsyncUpdate(data);
      }
    });
    
    // 處理表情更新
    this.wsService.registerHandler('morph_update', (data) => {
      if (data.morphTargets) {
        this.handleMorphUpdate(data);
      }
    });
  }
  
  // 處理唇型同步更新
  public handleLipsyncUpdate(data: any): void {
    if (!data || typeof data !== 'object') {
      logger.warn('Received invalid lipsync data', LogCategory.WEBSOCKET);
      return;
    }
    
    // <--- 新增日誌：打印收到的完整 lipsync 數據
    logger.debug({ 
      msg: '[ModelService] Received lipsync update data:', 
      details: data 
    }, LogCategory.WEBSOCKET);
    // --->
    
    // 迭代更新 Zustand store
    Object.entries(data).forEach(([key, value]) => {
      if (typeof value === 'number') {
        useStore.getState().updateMorphTarget(key, value);
      }
    });
    // logger.debug(`Lipsync update applied via Zustand: ${JSON.stringify(data)}`, LogCategory.MODEL);
  }
  
  // 處理表情更新
  public handleMorphUpdate(data: any): void {
    if (!data || typeof data !== 'object') {
      logger.warn('Received invalid morph target data', LogCategory.WEBSOCKET);
      return;
    }
    // 迭代更新 Zustand store
    Object.entries(data).forEach(([key, value]) => {
      if (typeof value === 'number') {
        useStore.getState().updateMorphTarget(key, value);
      }
    });
    // logger.debug(`Morph update applied via Zustand: ${JSON.stringify(data)}`, LogCategory.MODEL);
  }

  // 預加載模型
  public preloadModel(modelUrl: string): void {
    useGLTF.preload(modelUrl);
    
    // 預加載其他可能需要的模型
    const availableModels = [
      '/models/headonly.glb',
      '/models/klee.glb',
      '/models/fullbody.glb'
    ];
    
    availableModels.forEach(url => {
      if (url !== modelUrl) {
        useGLTF.preload(url);
      }
    });
  }

  // 獲取模型是否已加載 (使用 Zustand)
  public isModelLoaded(): boolean {
    return useStore.getState().modelLoaded;
  }

  // 設置模型加載狀態 (使用 Zustand)
  public setModelLoaded(loaded: boolean): void {
    useStore.getState().setModelLoaded(loaded);
  }

  // 設置 MorphTarget 字典 (使用 Zustand)
  public setMorphTargetDictionary(dictionary: Record<string, number> | null): void {
    useStore.getState().setMorphTargetDictionary(dictionary);
    // 同時更新本地的 dictionary 引用，供 updateMorphTargetInfluence 內部檢查
    this.morphTargetDictionary = dictionary || {};
  }

  // 獲取 MorphTarget 字典 (使用 Zustand)
  public getMorphTargetDictionary(): Record<string, number> | null {
    return useStore.getState().morphTargetDictionary;
  }

  // 設置 MorphTarget 影響值 (使用 Zustand)
  public setMorphTargetInfluences(influences: number[] | null): void {
    // 這個方法已經棄用，移除日誌警告
    // logger.warn('setMorphTargetInfluences 方法已棄用', LogCategory.MODEL);
  }

  // 獲取 MorphTarget 影響值 (使用 Zustand)
  public getMorphTargetInfluences(): number[] | null {
    // 這個方法已經棄用，移除日誌警告
    // logger.warn('getMorphTargetInfluences 方法已棄用', LogCategory.MODEL);
    return null;
  }

  // 設置可用動畫列表 (使用 Zustand)
  public setAvailableAnimations(animations: string[]): void {
    useStore.getState().setAvailableAnimations(animations);
    
    // 如果有動畫，嘗試自動選擇一個默認動畫
    if (animations.length > 0 && useStore.getState().currentAnimation === null) {
      // 首選 "Idle" 或 "idle" 動畫
      const idleAnimation = animations.find(anim => 
        anim.toLowerCase() === 'idle'
      );
      
      if (idleAnimation) {
        this.setCurrentAnimation(idleAnimation);
      } else {
        // 如果沒有 idle 動畫，選擇第一個可用的動畫
        this.setCurrentAnimation(animations[0]);
      }
    }
  }

  // 獲取可用動畫列表 (使用 Zustand)
  public getAvailableAnimations(): string[] {
    return useStore.getState().availableAnimations;
  }

  // 設置當前動畫 (使用 Zustand)
  public setCurrentAnimation(animation: string | null): void {
    useStore.getState().setCurrentAnimation(animation);
  }

  // 獲取當前動畫 (使用 Zustand)
  public getCurrentAnimation(): string | null {
    return useStore.getState().currentAnimation;
  }

  // 設置模型縮放 (使用 Zustand)
  public setModelScale(scale: number): void {
    const store = useStore.getState();
    store.setModelTransform([scale, scale, scale]);
  }

  // 獲取模型縮放 (使用 Zustand)
  public getModelScale(): number {
    return useStore.getState().modelScale[0]; // 假設三個軸的縮放比例相同
  }

  // 設置模型旋轉 (使用 Zustand)
  public setModelRotation(rotation: [number, number, number]): void {
    useStore.getState().setModelTransform(undefined, rotation);
  }

  // 獲取模型旋轉 (使用 Zustand)
  public getModelRotation(): [number, number, number] {
    return useStore.getState().modelRotation;
  }

  // 設置模型位置 (使用 Zustand)
  public setModelPosition(position: [number, number, number]): void {
    useStore.getState().setModelTransform(undefined, undefined, position);
  }

  // 獲取模型位置 (使用 Zustand)
  public getModelPosition(): [number, number, number] {
    return useStore.getState().modelPosition;
  }

  // 設置是否顯示太空背景 (使用 Zustand)
  public setShowSpaceBackground(show: boolean): void {
    useStore.getState().setShowSpaceBackground(show);
  }

  // 獲取是否顯示太空背景 (使用 Zustand)
  public getShowSpaceBackground(): boolean {
    return useStore.getState().showSpaceBackground;
  }

  // 獲取 MorphTargets (本地緩存版本)
  // public getMorphTargets(): Record<string, number> {
  //   return this.morphTargets;
  // }

  // 設置 MorphTargets (更新本地緩存與 Zustand)
  // public setMorphTargets(morphTargets: Record<string, number>): void {
  //   // 更新本地緩存
  //   this.morphTargets = { ...morphTargets };
  //   
  //   // 更新 Zustand (注意：這是個高頻操作)
  //   // 使用節流控制更新頻率，避免過多的狀態更新
  //   this._throttledNotify(morphTargets);
  // }
  
  // 節流控制的狀態更新
  // private _throttledNotify(morphTargets: Record<string, number>): void {
  //   const now = Date.now();
  //   
  //   // 使用節流控制，限制更新頻率
  //   if (now - this._lastNotifyTime < 50) { // 節流閾值50毫秒
  //     // 如果過於頻繁，則等待並保存最新狀態
  //     this._pendingMorphTargets = morphTargets;
  //     
  //     // 如果沒有設置定時器，則設置一個
  //     if (this._notifyTimeout === null) {
  //       this._notifyTimeout = window.setTimeout(() => {
  //         // 更新時間戳
  //         this._lastNotifyTime = Date.now();
  //         
  //         // 如果有待處理的數據，則使用它；否則什麼都不做
  //         if (this._pendingMorphTargets) {
  //           useStore.getState().setMorphTargets(this._pendingMorphTargets);
  //           this._pendingMorphTargets = null;
  //         }
  //         
  //         // 清除定時器引用
  //         this._notifyTimeout = null;
  //       }, 50 - (now - this._lastNotifyTime));
  //     }
  //   } else {
  //     // 如果距離上次更新已經過了足夠時間，則立即更新
  //     this._lastNotifyTime = now;
  //     useStore.getState().setMorphTargets(morphTargets);
  //     
  //     // 清除任何待處理的數據和定時器
  //     this._pendingMorphTargets = null;
  //     if (this._notifyTimeout !== null) {
  //       window.clearTimeout(this._notifyTimeout);
  //       this._notifyTimeout = null;
  //     }
  //   }
  // }

  // 更新單個 MorphTarget 的值 (使用 Zustand)
  public updateMorphTargetInfluence(name: string, value: number): void {
    // 使用 this.morphTargetDictionary 進行檢查
    if (this.morphTargetDictionary && this.morphTargetDictionary[name] === undefined) {
       // logger.warn(`Attempted to update unknown morph target: ${name}`, LogCategory.MODEL);
       return; // 如果名稱無效則返回
    }

    // 直接更新 Zustand store 使用正確的方法名
    useStore.getState().updateMorphTarget(name, value);
    // logger.debug(`Manual morph target updated via Zustand: ${name} = ${value}`, LogCategory.MODEL);
  }

  // 重置所有 MorphTargets (使用 Zustand)
  public resetAllMorphTargets(): void {
    // 創建一個所有值都設為0的新對象
    const resetTargets: Record<string, number> = {};
    
    // 獲取完整的 Morph Target 字典 (從 Zustand 讀取)
    const dictionary = useStore.getState().morphTargetDictionary;
    
    // 如果字典存在，則基於字典的鍵進行重置
    if (dictionary) {
      Object.keys(dictionary).forEach(key => {
        resetTargets[key] = 0;
      });
      
      // 直接更新 Zustand
      useStore.getState().setMorphTargets(resetTargets);
      logger.info('All morph targets reset based on dictionary via Zustand.', LogCategory.MODEL);
    } else {
      // 如果字典不存在，可能無法正確重置，記錄警告
      logger.warn('Cannot reset morph targets: Dictionary not found in Zustand.', LogCategory.MODEL);
      // 作為備選，可以嘗試清空現有狀態，但這可能不理想
      // useStore.getState().setMorphTargets({});
    }
  }

  // 旋轉模型 (使用 Zustand)
  public rotateModel(direction: 'left' | 'right'): void {
    const currentRotation = [...this.getModelRotation()];
    const rotationStep = Math.PI / 8; // 約22.5度
    
    if (direction === 'left') {
      currentRotation[1] += rotationStep;
    } else {
      currentRotation[1] -= rotationStep;
    }
    
    this.setModelRotation(currentRotation as [number, number, number]);
  }

  // 縮放模型 (使用 Zustand)
  public scaleModel(factor: number): void {
    const currentScale = this.getModelScale();
    const newScale = currentScale * factor;
    // 限制縮放範圍
    this.setModelScale(Math.max(0.5, Math.min(newScale, 2.0)));
  }

  // 重置模型變換 (使用 Zustand)
  public resetModel(): void {
    // 重置到默認值
    useStore.getState().setModelTransform(
      [1, 1, 1], // 默認縮放
      [0, 0, 0], // 默認旋轉
      [0, -1, 0] // 默認位置
    );
  }

  // 切換背景 (使用 Zustand)
  public toggleBackground(): void {
    const currentState = this.getShowSpaceBackground();
    this.setShowSpaceBackground(!currentState);
  }

  // 選擇動畫 (使用 Zustand)
  public selectAnimation(animation: string): void {
    this.setCurrentAnimation(animation);
  }

  // 應用預設表情
  public async applyPresetExpression(expression: string): Promise<boolean> {
    logger.info(`應用表情預設: ${expression}`, LogCategory.MODEL);
    try {
      const presetData = await getPresetExpression(expression);
      if (presetData && presetData.morphTargets) {
        // 在處理前打印從 API 收到的數據
        console.log('[ModelService] Received preset data:', JSON.stringify(presetData.morphTargets)); 
        
        // 保存情緒信息（如果存在）
        // if (presetData.emotion) {
        //   useStore.getState().setEmotion(presetData.emotion, presetData.confidence || 0);
        // }
        
        // 使用 handleMorphUpdate 處理 morph targets
        this.handleMorphUpdate(presetData.morphTargets);
        return true;
      } else {
        logger.error(`無法獲取或解析預設表情數據: ${expression}`, LogCategory.MODEL);
        return false;
      }
    } catch (error) {
      logger.error(`應用預設表情時出錯 (${expression}):`, LogCategory.MODEL, error);
      return false;
    }
  }

  // 獲取模型數據 (使用 Zustand)
  public getModelData(): ModelData {
    const store = useStore.getState();
    return {
      modelUrl: store.modelUrl,
      modelScale: store.modelScale[0], // 假設三個軸的縮放比例相同
      modelRotation: store.modelRotation,
      modelPosition: store.modelPosition,
      morphTargets: store.morphTargets, // <-- 直接從 store 獲取
      showSpaceBackground: store.showSpaceBackground,
      currentAnimation: store.currentAnimation
    };
  }

  // 獲取模型URL (使用 Zustand)
  public getModelUrl(): string {
    return useStore.getState().modelUrl;
  }

  // 切換模型 (使用 Zustand)
  public switchModel(url: string): void {
    if (url === this.getModelUrl()) {
      return; // 如果URL相同，則不做任何事情
    }

    logger.info(`切換模型: ${url}`, LogCategory.MODEL);
    
    // 預加載新模型
    this.preloadModel(url);
    
    // 重置所有狀態 (包括 morph targets - 現在會正確調用修改後的 reset)
    this.resetAllMorphTargets();
    
    // 更新URL和重置相關狀態
    useStore.getState().setModelUrl(url);
    
    // 重置加載狀態
    this.setModelLoaded(false);
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
        msg: "ModelService initialized: Zustand dictionary and morphs set.", 
        details: initialMorphTargets // 將物件放在 details 欄位
      }, LogCategory.MODEL);
    } else {
      // 如果傳入 null (例如模型加載失敗或無 morphs)
      useStore.getState().setMorphTargetDictionary(null);
      useStore.getState().setMorphTargets({}); // 清空 morphs
      this.morphTargetDictionary = {}; // 清空內部引用
      logger.warn("ModelService initialized with null dictionary: Cleared morph state.", LogCategory.MODEL);
    }
  }
}

// React Hook - 使用模型服務
export function useModelService() {
  // 直接從 Zustand 獲取狀態
  const modelLoaded = useStore((state) => state.modelLoaded);
  const modelUrl = useStore((state) => state.modelUrl);
  const modelScale = useStore((state) => state.modelScale);
  const modelRotation = useStore((state) => state.modelRotation);
  const modelPosition = useStore((state) => state.modelPosition);
  const showSpaceBackground = useStore((state) => state.showSpaceBackground);
  const availableAnimations = useStore((state) => state.availableAnimations);
  const currentAnimation = useStore((state) => state.currentAnimation);
  const morphTargets = useStore((state) => state.morphTargets);
  const morphTargetDictionary = useStore((state) => state.morphTargetDictionary);

  const modelService = useRef<ModelService>(ModelService.getInstance());

  const setMorphTargetData = useCallback((dictionary: Record<string, number> | null, influences: number[] | null) => {
    // 如果 dictionary 存在，調用 ModelService 的 initialize 方法
    // 該方法會處理設置 dictionary 和初始化 morphTargets 狀態
    if (dictionary) {
      // modelService.current.setMorphTargetDictionary(dictionary); // 不再需要單獨調用這個
      modelService.current.initialize(dictionary);
      logger.info('useModelService: Called ModelService.initialize with new dictionary.', LogCategory.MODEL);
    } else {
      // 如果 dictionary 為 null (模型加載失敗或無 morphs)，也需要通知服務進行清理
      // 可以考慮在 ModelService 中添加一個清理方法，或者讓 initialize 處理 null
      // 暫時假設 initialize 可以處理 null 或添加一個明確的清理函數
      // modelService.current.clearMorphData(); // 假設有此方法
      // 或者，如果 initialize 能處理 null:
      // modelService.current.initialize(null);
      // 目前 ModelService.initialize 可能沒有處理 null 的情況，先只處理 dictionary 存在的情況
      logger.warn('useModelService: Received null dictionary, state might not be cleared.', LogCategory.MODEL);
    }
    // influences 已棄用，無需處理
  }, []);

  const rotateModel = useCallback((direction: 'left' | 'right') => {
    modelService.current.rotateModel(direction);
  }, []);

  const scaleModel = useCallback((factor: number) => {
    modelService.current.scaleModel(factor);
  }, []);

  const resetModel = useCallback(() => {
    modelService.current.resetModel();
  }, []);

  const toggleBackground = useCallback(() => {
    modelService.current.toggleBackground();
  }, []);

  const selectAnimation = useCallback((animation: string) => {
    modelService.current.selectAnimation(animation);
  }, []);

  const updateMorphTargetInfluence = useCallback((name: string, value: number) => {
    modelService.current.updateMorphTargetInfluence(name, value);
  }, []);

  const resetAllMorphTargets = useCallback(() => {
    modelService.current.resetAllMorphTargets();
  }, []);

  const applyPresetExpression = useCallback((expression: string) => {
    return modelService.current.applyPresetExpression(expression);
  }, []);

  const switchModel = useCallback((url: string) => {
    modelService.current.switchModel(url);
  }, []);

  // 從返回物件中移除 getManualMorphTargets
  return {
    modelLoaded,
    modelUrl,
    modelScale,
    modelRotation,
    modelPosition,
    showSpaceBackground,
    availableAnimations,
    currentAnimation,
    morphTargets,
    morphTargetDictionary,
    setMorphTargetData,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    selectAnimation,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    switchModel
  };
}

export default ModelService; 