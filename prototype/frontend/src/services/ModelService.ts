import { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';
import WebSocketService from './WebSocketService';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

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
  private morphTargets: Record<string, number> = {};

  // 不再需要舊的回調列表，全部使用 Zustand 狀態更新
  private wsService: WebSocketService;
  
  // 新增：保存最近的情緒表情
  private _lastEmotionMorphs: Record<string, number> = {};
  
  // 限制更新頻率的變數
  private _lastNotifyTime: number = 0;
  private _pendingMorphTargets: Record<string, number> | null = null;
  private _notifyTimeout: number | null = null;

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
  private handleLipsyncUpdate(data: any): void {
    if (data.morphTargets) {
      logger.debug('處理唇型同步更新', LogCategory.MORPH, 'lipsync_update');
      const faceKeys = [
        // 嘴部相關
        "jawOpen", "mouthOpen", "mouthFunnel", "mouthPucker", 
        "mouthLowerDownLeft", "mouthLowerDownRight", "mouthLeft", "mouthRight",
        "mouthStretchLeft", "mouthStretchRight", "mouthSmileLeft", "mouthSmileRight",
        "mouthFrownLeft", "mouthFrownRight",
        // 眉毛和眼睛相關
        "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
        "eyeWideLeft", "eyeWideRight", "eyeSquintLeft", "eyeSquintRight",
        "eyeBlinkLeft", "eyeBlinkRight",
        // 臉頰相關
        "cheekPuff", "cheekSquintLeft", "cheekSquintRight"
      ];
      
      // 嘴型相關的關鍵字，用於區分嘴部和非嘴部表情
      const mouthKeys = [
        "jawOpen", "mouthOpen", "mouthFunnel", "mouthPucker", 
        "mouthLowerDownLeft", "mouthLowerDownRight", "mouthLeft", "mouthRight",
        "mouthStretchLeft", "mouthStretchRight", "mouthClose", "jawLeft", "jawRight"
      ];
      
      // 創建新物件，保留所有原有值
      const newMorphTargets = { ...this.morphTargets };
      
      // 更新表情值 - 融合情緒表情和唇型
      Object.entries(data.morphTargets).forEach(([key, value]) => {
        if (faceKeys.includes(key)) {
          // 嘴部動作優先使用lipsync數據
          if (mouthKeys.includes(key)) {
            // 為嘴巴相關的目標值設置一個最小閾值，避免完全閉合
            if (key === "jawOpen" || key === "mouthOpen") {
              newMorphTargets[key] = Math.max(value as number, 0.05);
            } else {
              newMorphTargets[key] = value as number;
            }
          } 
          // 表情相關的臉部動作（例如笑或皺眉）需要融合lipsync和情緒表情
          else if (key.includes("mouthSmile") || key.includes("mouthFrown")) {
            const lipsyncValue = value as number;
            const emotionValue = this._lastEmotionMorphs[key] || 0;
            // 選擇較強的表情效果，確保表情明顯
            newMorphTargets[key] = Math.max(lipsyncValue, emotionValue * 0.8);
          }
          // 眼睛和眉毛動作：如果lipsync提供了強烈的表情，使用它；否則優先使用情緒表情
          else if (key.startsWith("eye") || key.startsWith("brow") || key.startsWith("cheek")) {
            const lipsyncValue = value as number;
            const emotionValue = this._lastEmotionMorphs[key] || 0;
            
            // 眨眼動作需要特殊處理，確保其可以正常進行
            if (key.startsWith("eyeBlink")) {
              newMorphTargets[key] = lipsyncValue > 0.3 ? lipsyncValue : emotionValue;
            } else {
              // 其他眼睛和眉毛動作，選擇較強的值或融合兩者
              // 如果lipsync數據中的值很小，使用情緒表情的值
              newMorphTargets[key] = lipsyncValue > 0.2 ? lipsyncValue : emotionValue;
            }
          } else {
            // 其他臉部表情，直接使用lipsync值
            newMorphTargets[key] = value as number;
          }
        }
      });
      
      // 確保將所有情緒表情中存在但lipsync中不存在的值也添加到結果中
      // 這確保了即使lipsync數據不包括某些表情，情緒表情仍然會顯示
      Object.entries(this._lastEmotionMorphs).forEach(([key, value]) => {
        if (!data.morphTargets[key] && !mouthKeys.includes(key) && value > 0.1) {
          newMorphTargets[key] = value;
        }
      });
      
      // 保存情緒信息（如果有）
      if (data.emotion) {
        // 使用 Zustand 更新情緒
        useStore.getState().setEmotion(data.emotion, data.confidence || 0);
      }
      
      // 更新morphTargets
      this.setMorphTargets(newMorphTargets);
    }
  }
  
  // 處理表情更新
  private handleMorphUpdate(data: any): void {
    if (data.morphTargets) {
      // 日誌記錄表情更新 (使用debug級別避免過多輸出)
      logger.debug('處理表情更新', LogCategory.MORPH, 'morph_update');
      
      // 口型相關的關鍵字列表
      const mouthKeys = [
        "jawOpen", "mouthOpen", "mouthFunnel", "mouthPucker", 
        "mouthLowerDownLeft", "mouthLowerDownRight", "mouthLeft", "mouthRight",
        "mouthStretchLeft", "mouthStretchRight", "mouthSmileLeft", "mouthSmileRight",
        "mouthFrownLeft", "mouthFrownRight", "mouthDimpleLeft", "mouthDimpleRight",
        "mouthUpperUpLeft", "mouthUpperUpRight", "mouthShrugLower", "mouthShrugUpper",
        "mouthRollLower", "mouthRollUpper", "mouthClose", "jawLeft", "jawRight",
        "eyeBlinkLeft", "eyeBlinkRight"
      ];
      
      // 保存當前的情緒表情，供handleLipsyncUpdate使用
      this._lastEmotionMorphs = {...data.morphTargets};
      
      // 如果提供了情緒信息，保存它
      if (data.emotion) {
        // 使用 Zustand 更新情緒
        useStore.getState().setEmotion(data.emotion, data.confidence || 0);
      }
      
      // 創建新物件，保留所有原有值
      const newMorphTargets = { ...this.morphTargets };
      
      // 如果正在播放語音，只更新非嘴部相關的值，否則更新所有值
      Object.entries(data.morphTargets).forEach(([key, value]) => {
        // 判斷是否正在播放語音
        const isPlayingAudio = document.querySelector('audio')?.paused === false;
        
        if (isPlayingAudio) {
          // 如果正在播放語音，只更新非嘴部相關的值
          if (!mouthKeys.some(mouthKey => key.includes(mouthKey))) {
            newMorphTargets[key] = value as number;
          }
        } else {
          // 如果不在播放語音，更新所有值
          newMorphTargets[key] = value as number;
        }
      });
      
      // 更新morphTargets
      this.setMorphTargets(newMorphTargets);
    }
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
  }

  // 獲取 MorphTarget 字典 (使用 Zustand)
  public getMorphTargetDictionary(): Record<string, number> | null {
    return useStore.getState().morphTargetDictionary;
  }

  // 設置 MorphTarget 影響值 (使用 Zustand)
  public setMorphTargetInfluences(influences: number[] | null): void {
    // 這個方法已經棄用，保留只為兼容舊代碼
    logger.warn('setMorphTargetInfluences 方法已棄用', LogCategory.MODEL);
  }

  // 獲取 MorphTarget 影響值 (使用 Zustand)
  public getMorphTargetInfluences(): number[] | null {
    // 這個方法已經棄用，保留只為兼容舊代碼
    logger.warn('getMorphTargetInfluences 方法已棄用', LogCategory.MODEL);
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
  public getMorphTargets(): Record<string, number> {
    return this.morphTargets;
  }

  // 設置 MorphTargets (更新本地緩存與 Zustand)
  public setMorphTargets(morphTargets: Record<string, number>): void {
    // 更新本地緩存
    this.morphTargets = { ...morphTargets };
    
    // 更新 Zustand (注意：這是個高頻操作)
    // 使用節流控制更新頻率，避免過多的狀態更新
    this._throttledNotify(morphTargets);
  }
  
  // 節流控制的狀態更新
  private _throttledNotify(morphTargets: Record<string, number>): void {
    const now = Date.now();
    
    // 使用節流控制，限制更新頻率
    if (now - this._lastNotifyTime < 50) { // 節流閾值50毫秒
      // 如果過於頻繁，則等待並保存最新狀態
      this._pendingMorphTargets = morphTargets;
      
      // 如果沒有設置定時器，則設置一個
      if (this._notifyTimeout === null) {
        this._notifyTimeout = window.setTimeout(() => {
          // 更新時間戳
          this._lastNotifyTime = Date.now();
          
          // 如果有待處理的數據，則使用它；否則什麼都不做
          if (this._pendingMorphTargets) {
            useStore.getState().setMorphTargets(this._pendingMorphTargets);
            this._pendingMorphTargets = null;
          }
          
          // 清除定時器引用
          this._notifyTimeout = null;
        }, 50 - (now - this._lastNotifyTime));
      }
    } else {
      // 如果距離上次更新已經過了足夠時間，則立即更新
      this._lastNotifyTime = now;
      useStore.getState().setMorphTargets(morphTargets);
      
      // 清除任何待處理的數據和定時器
      this._pendingMorphTargets = null;
      if (this._notifyTimeout !== null) {
        window.clearTimeout(this._notifyTimeout);
        this._notifyTimeout = null;
      }
    }
  }

  // 更新單個 MorphTarget 的值 (使用 Zustand)
  public updateMorphTargetInfluence(name: string, value: number): void {
    useStore.getState().updateMorphTarget(name, value);
    // 同時更新本地緩存
    this.morphTargets[name] = value;
  }

  // 獲取手動設置的 MorphTargets (使用 Zustand)
  public getManualMorphTargets(): Record<string, number> {
    return useStore.getState().morphTargets;
  }

  // 重置所有 MorphTargets (使用 Zustand)
  public resetAllMorphTargets(): void {
    // 創建一個所有值都設為0的新對象
    const resetTargets: Record<string, number> = {};
    
    // 獲取所有當前存在的Morph Target名稱
    Object.keys(this.morphTargets).forEach(key => {
      resetTargets[key] = 0;
    });
    
    // 更新Morph Targets
    this.setMorphTargets(resetTargets);
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

  // 應用預設表情 (使用 Zustand)
  public async applyPresetExpression(expression: string): Promise<boolean> {
    try {
      // 獲取表情預設值
      const response = await fetch(`${API_BASE_URL}/api/expressions/preset-expressions/${expression}`);
      
      if (!response.ok) {
        logger.error(`獲取表情預設 ${expression} 失敗: ${response.statusText}`, LogCategory.MODEL);
        return false;
      }
      
      const data = await response.json();
      
      if (data.morphTargets) {
        logger.info(`應用表情預設: ${expression}`, LogCategory.MODEL);
        
        // 獲取當前表情
        const currentMorphs = this.getMorphTargets();
        
        // 創建新表情對象
        const newMorphs = { ...currentMorphs };
        
        // 更新表情值
        Object.entries(data.morphTargets).forEach(([key, value]) => {
          newMorphs[key] = value as number;
        });
        
        // 更新Morph Targets
        this.setMorphTargets(newMorphs);
        return true;
      }
    } catch (error) {
      logger.error(`應用表情預設時出錯: ${expression}`, LogCategory.MODEL, error);
    }
    
    return false;
  }

  // 獲取模型數據 (使用 Zustand)
  public getModelData(): ModelData {
    const store = useStore.getState();
    return {
      modelUrl: store.modelUrl,
      modelScale: store.modelScale[0], // 假設三個軸的縮放比例相同
      modelRotation: store.modelRotation,
      modelPosition: store.modelPosition,
      morphTargets: this.morphTargets, // 使用本地緩存的版本
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
    
    // 重置所有狀態
    this.resetAllMorphTargets();
    
    // 更新URL和重置相關狀態
    useStore.getState().setModelUrl(url);
    
    // 重置加載狀態
    this.setModelLoaded(false);
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

  const modelService = useRef<ModelService>(ModelService.getInstance());

  // 提供方法給組件使用
  const getManualMorphTargets = useCallback(() => {
    return modelService.current.getManualMorphTargets();
  }, []);

  const setMorphTargetData = useCallback((dictionary: Record<string, number> | null, influences: number[] | null) => {
    if (dictionary) {
      modelService.current.setMorphTargetDictionary(dictionary);
    }
    
    // influences 已棄用，但保留方法簽名以向後兼容
    if (influences) {
      logger.warn('setMorphTargetInfluences 已棄用', LogCategory.MODEL);
    }
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

  // 返回所有狀態和方法
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
    getManualMorphTargets,
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