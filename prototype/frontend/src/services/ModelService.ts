import { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';
import WebSocketService from './WebSocketService';
import logger, { LogCategory } from '../utils/LogManager';

// 後端API URL
const API_BASE_URL = 'http://localhost:8000';

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
  private morphTargetDictionary: Record<string, number> | null = null;
  private morphTargetInfluences: number[] | null = null;
  private availableAnimations: string[] = [];
  private currentAnimation: string | null = null;
  private modelScale: number = 1;
  private modelRotation: [number, number, number] = [0, 0, 0];
  private modelPosition: [number, number, number] = [0, -1, 0];
  private showSpaceBackground: boolean = true;
  private modelLoaded: boolean = false;
  private morphTargets: Record<string, number> = {};
  private onModelLoadedCallbacks: (() => void)[] = [];
  private onMorphTargetsUpdateCallbacks: ((morphTargets: Record<string, number>) => void)[] = [];
  private onStateUpdateCallbacks: (() => void)[] = [];
  private wsService: WebSocketService;
  
  // 新增：保存最近的情緒表情
  private _lastEmotionMorphs: Record<string, number> = {};
  private _currentEmotion: string = 'neutral';
  
  // 限制更新頻率的變數
  private _lastNotifyTime: number = 0;
  private _pendingMorphTargets: Record<string, number> | null = null;
  private _notifyTimeout: number | null = null;

  // 新增：專門儲存手動設置的 Morph Target 目標值
  private _manualMorphTargets: Record<string, number> = {};

  private modelUrl: string = '/models/headonly.glb';

  // 回調函數列表
  private onModelChangeCallbacks: ((url: string) => void)[] = [];
  private onTransformChangeCallbacks: (() => void)[] = [];
  private onAnimationChangeCallbacks: ((animation: string | null) => void)[] = [];
  private onManualMorphTargetsUpdateCallbacks: ((targets: Record<string, number>) => void)[] = [];
  private onDictionaryUpdateCallbacks: ((dict: Record<string, number> | null) => void)[] = [];
  private onLoadStatusChangeCallbacks: ((isLoaded: boolean) => void)[] = [];
  private onBackgroundToggleCallbacks: ((show: boolean) => void)[] = [];
  private onAvailableAnimationsUpdateCallbacks: ((animations: string[]) => void)[] = [];

  // 單例模式
  public static getInstance(): ModelService {
    if (!ModelService.instance) {
      ModelService.instance = new ModelService();
    }
    return ModelService.instance;
  }

  constructor() {
    // 預加載模型
    this.preloadModel(this.modelUrl);
    
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
        this._currentEmotion = data.emotion;
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
        this._currentEmotion = data.emotion;
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
      '/models/mixamowomanwithface.glb',
      '/models/armature001_model.glb'
    ];
    
    // 預加載所有模型
    availableModels.forEach(url => {
      if (url !== modelUrl) {
        useGLTF.preload(url);
      }
    });
    
    // 模擬模型加載完成
    setTimeout(() => {
      this.modelLoaded = true;
      this.notifyModelLoaded();
    }, 1000);
  }

  // 獲取模型是否已加載
  public isModelLoaded(): boolean {
    return this.modelLoaded;
  }

  // 設置模型加載狀態
  public setModelLoaded(loaded: boolean): void {
    this.modelLoaded = loaded;
    
    if (loaded) {
      this.notifyModelLoaded();
    }
  }

  // 設置Morph Target字典
  public setMorphTargetDictionary(dictionary: Record<string, number> | null): void {
    this.morphTargetDictionary = dictionary;
  }

  // 獲取Morph Target字典
  public getMorphTargetDictionary(): Record<string, number> | null {
    return this.morphTargetDictionary;
  }

  // 設置Morph Target影響值
  public setMorphTargetInfluences(influences: number[] | null): void {
    this.morphTargetInfluences = influences;
  }

  // 獲取Morph Target影響值
  public getMorphTargetInfluences(): number[] | null {
    return this.morphTargetInfluences;
  }

  // 設置可用動畫列表
  public setAvailableAnimations(animations: string[]): void {
    const hasChanged = 
      animations.length !== this.availableAnimations.length || 
      !animations.every((val, index) => val === this.availableAnimations[index]);
      
    if (hasChanged) {
      // 將詳細資訊放入第一個參數對象，省略第三個 type 參數
      logger.info({ msg: 'Available animations updated', details: animations }, LogCategory.MODEL); 
      this.availableAnimations = [...animations];
      this.notifyAvailableAnimationsUpdate();
    }
  }

  // 獲取可用動畫列表
  public getAvailableAnimations(): string[] {
    return [...this.availableAnimations];
  }

  // 設置當前動畫
  public setCurrentAnimation(animation: string | null): void {
    this.currentAnimation = animation;
  }

  // 獲取當前動畫
  public getCurrentAnimation(): string | null {
    return this.currentAnimation;
  }

  // 設置模型縮放
  public setModelScale(scale: number): void {
    this.modelScale = scale > 0.1 ? scale : 0.1;
  }

  // 獲取模型縮放
  public getModelScale(): number {
    return this.modelScale;
  }

  // 設置模型旋轉
  public setModelRotation(rotation: [number, number, number]): void {
    this.modelRotation = rotation;
  }

  // 獲取模型旋轉
  public getModelRotation(): [number, number, number] {
    return this.modelRotation;
  }

  // 設置模型位置
  public setModelPosition(position: [number, number, number]): void {
    this.modelPosition = position;
  }

  // 獲取模型位置
  public getModelPosition(): [number, number, number] {
    return this.modelPosition;
  }

  // 設置空間背景顯示
  public setShowSpaceBackground(show: boolean): void {
    this.showSpaceBackground = show;
  }

  // 獲取空間背景顯示
  public getShowSpaceBackground(): boolean {
    return this.showSpaceBackground;
  }

  // 獲取當前Morph Target設置
  public getMorphTargets(): Record<string, number> {
    return this.morphTargets;
  }

  // 設置Morph Target值
  public setMorphTargets(morphTargets: Record<string, number>): void {
    // 效能優化：如果新值與舊值相同，則不進行更新
    let hasChanged = false;
    const currentKeys = Object.keys(this.morphTargets);
    const newKeys = Object.keys(morphTargets);
    
    // 檢查兩個對象是否有不同的鍵
    if (currentKeys.length !== newKeys.length) {
      hasChanged = true;
    } else {
      // 檢查值是否有變化
      for (const key of newKeys) {
        // 使用閾值比較，微小差異不觸發更新
        if (!this.morphTargets.hasOwnProperty(key) || 
            Math.abs(this.morphTargets[key] - morphTargets[key]) > 0.01) {
          hasChanged = true;
          break;
        }
      }
    }
    
    // 如果沒有變化，則不更新
    if (!hasChanged) {
      return;
    }
    
    // 更新值
    this.morphTargets = morphTargets;
    
    // 限制事件觸發頻率，避免過多更新
    this._throttledNotify(morphTargets);
  }

  // 限制通知更新的頻率
  private _throttledNotify(morphTargets: Record<string, number>): void {
    const now = Date.now();
    const timeSinceLastNotify = now - this._lastNotifyTime;
    
    // 如果距離上次通知時間很短，則緩存此次更新
    if (timeSinceLastNotify < 100) { // 限制為最多每100毫秒更新一次
      // 保存最新的值，以便之後使用
      this._pendingMorphTargets = morphTargets;
      
      // 如果沒有排定的更新，則安排一個
      if (this._notifyTimeout === null) {
        this._notifyTimeout = window.setTimeout(() => {
          if (this._pendingMorphTargets) {
            this.notifyMorphTargetsUpdate(this._pendingMorphTargets);
            this._lastNotifyTime = Date.now();
          }
          this._pendingMorphTargets = null;
          this._notifyTimeout = null;
        }, 100 - timeSinceLastNotify);
      }
    } else {
      // 如果距離上次通知時間較長，則立即通知
      this.notifyMorphTargetsUpdate(morphTargets);
      this._lastNotifyTime = now;
      
      // 清除任何待處理的更新
      if (this._notifyTimeout !== null) {
        window.clearTimeout(this._notifyTimeout);
        this._notifyTimeout = null;
        this._pendingMorphTargets = null;
      }
    }
  }

  // 更新特定Morph Target的影響值 (由 UI 調用)
  public updateMorphTargetInfluence(name: string, value: number): void {
    this._manualMorphTargets[name] = value;
    logger.debug(`手動更新 Morph Target: ${name} = ${value}`, LogCategory.MORPH);
    this.notifyStateChange(); 
  }

  // 新增：獲取所有手動設置的目標值 (供 useFrame 和 UI 使用)
  public getManualMorphTargets(): Record<string, number> {
    return { ...this._manualMorphTargets }; 
  }

  // 重置所有Morph Target
  public resetAllMorphTargets(): void {
    logger.info('重置所有 Morph Targets', LogCategory.MODEL);
    this._manualMorphTargets = {};
    const previousMorphTargets = this.morphTargets;
    this.morphTargets = {}; 
    if (this.morphTargetInfluences) {
      this.morphTargetInfluences = this.morphTargetInfluences.map(() => 0);
    }
    if (Object.keys(previousMorphTargets).length > 0) {
       this.notifyMorphTargetsUpdate({});
    }
    this.notifyStateChange(); 
  }

  // 旋轉模型
  public rotateModel(direction: 'left' | 'right'): void {
    const step = direction === 'left' ? 0.1 : -0.1;
    this.modelRotation = [
      this.modelRotation[0],
      this.modelRotation[1] + step,
      this.modelRotation[2]
    ];
  }

  // 縮放模型
  public scaleModel(factor: number): void {
    const newScale = this.modelScale + factor;
    this.modelScale = newScale > 0.1 ? newScale : 0.1;
  }

  // 重置模型
  public resetModel(): void {
    this.modelScale = 1;
    this.modelRotation = [0, 0, 0];
    this.modelPosition = [0, -1, 0];
    this.currentAnimation = null;
    this.resetAllMorphTargets();
  }

  // 切換背景
  public toggleBackground(): void {
    this.showSpaceBackground = !this.showSpaceBackground;
  }

  // 選擇動畫
  public selectAnimation(animation: string): void {
    this.currentAnimation = animation;
  }

  // 應用預設表情
  public async applyPresetExpression(expression: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/preset-expressions/${expression}`);
      if (!response.ok) {
        throw new Error(`API錯誤: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.morphTargets) {
        logger.info(`應用預設表情: ${expression}`, LogCategory.MODEL);
        this._manualMorphTargets = { ...data.morphTargets };
        this.notifyStateChange(); 
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('應用預設表情錯誤:', error);
      return false;
    }
  }

  // 獲取模型數據
  public getModelData(): ModelData {
    return {
      modelUrl: this.modelUrl,
      modelScale: this.modelScale,
      modelRotation: this.modelRotation,
      modelPosition: this.modelPosition,
      morphTargets: this.morphTargets,
      showSpaceBackground: this.showSpaceBackground,
      currentAnimation: this.currentAnimation,
    };
  }

  // 註冊模型加載完成事件
  public onModelLoaded(callback: () => void): void {
    this.onModelLoadedCallbacks.push(callback);
    
    // 如果模型已經加載完成，立即調用回調
    if (this.modelLoaded) {
      callback();
    }
  }

  // 移除模型加載完成事件
  public offModelLoaded(callback: () => void): void {
    this.onModelLoadedCallbacks = this.onModelLoadedCallbacks.filter(cb => cb !== callback);
  }

  // 觸發模型加載完成事件
  private notifyModelLoaded(): void {
    this.modelLoaded = true;
    this.onModelLoadedCallbacks.forEach(cb => cb());
    this.notifyStateChange(); // 通知狀態變更
    logger.info(`模型 ${this.modelUrl} 已觸發加載完成通知`, LogCategory.MODEL);
  }

  // 註冊Morph Targets更新事件
  public onMorphTargetsUpdate(callback: (morphTargets: Record<string, number>) => void): void {
    this.onMorphTargetsUpdateCallbacks.push(callback);
  }

  // 移除Morph Targets更新事件
  public offMorphTargetsUpdate(callback: (morphTargets: Record<string, number>) => void): void {
    this.onMorphTargetsUpdateCallbacks = this.onMorphTargetsUpdateCallbacks.filter(cb => cb !== callback);
  }

  // 觸發Morph Targets更新事件
  private notifyMorphTargetsUpdate(morphTargets: Record<string, number>): void {
    this.onMorphTargetsUpdateCallbacks.forEach(cb => cb(morphTargets));
  }

  // 獲取模型URL
  public getModelUrl(): string {
    return this.modelUrl;
  }

  // 設置模型URL (改為 switchModel)
  public switchModel(url: string): void {
    if (url === this.modelUrl) {
      logger.info(`Model URL is already ${url}, skipping switch.`, LogCategory.MODEL);
      return; // 如果 URL 相同，不執行任何操作
    }

    logger.info(`Switching model to: ${url}`, LogCategory.MODEL);
    this.modelUrl = url;

    // 重置與模型相關的狀態
    this.modelLoaded = false;
    this.availableAnimations = [];
    this.currentAnimation = null; // 可以考慮設置一個預設動畫，如果有的話
    this.morphTargetDictionary = null;
    this.morphTargetInfluences = null;
    this.morphTargets = {};
    this._manualMorphTargets = {};
    this._lastEmotionMorphs = {};
    this._currentEmotion = 'neutral';

    // 預加載新模型
    this.preloadModel(url);

    // 觸發狀態更新，通知 UI 模型正在更換且狀態已重置
    this.notifyStateChange(); 
    this.notifyAvailableAnimationsUpdate(); // 通知動畫列表已清空
    this.notifyModelLoaded(); // 通知模型加載狀態改變 (变为 false)
  }

  // 通知其他狀態變更 (模型變換、動畫、字典、影響值等)
  private notifyStateChange(): void {
    logger.debug('觸發通用狀態更新通知', LogCategory.MODEL);
    this.onStateUpdateCallbacks.forEach(cb => cb());
  }

  // 重新加入 register/unregister 方法以修正 Linter 錯誤
  public registerStateUpdateCallback(callback: () => void): void {
    this.onStateUpdateCallbacks.push(callback);
  }

  public unregisterStateUpdateCallback(callback: () => void): void {
    this.onStateUpdateCallbacks = this.onStateUpdateCallbacks.filter(cb => cb !== callback);
  }

  // Available Animations Update Callbacks
  public onAvailableAnimationsUpdate(callback: (animations: string[]) => void): void {
    this.onAvailableAnimationsUpdateCallbacks.push(callback);
    callback([...this.availableAnimations]); // Immediately provide current state
  }

  public offAvailableAnimationsUpdate(callback: (animations: string[]) => void): void {
    this.onAvailableAnimationsUpdateCallbacks = this.onAvailableAnimationsUpdateCallbacks.filter(cb => cb !== callback);
  }

  private notifyAvailableAnimationsUpdate(): void {
    const animationsCopy = [...this.availableAnimations];
    this.onAvailableAnimationsUpdateCallbacks.forEach(callback => callback(animationsCopy));
  }
}

// React Hook - 使用模型服務
export function useModelService() {
  const [modelLoaded, setModelLoaded] = useState<boolean>(false);
  const [modelScale, setModelScale] = useState<number>(1);
  const [modelRotation, setModelRotation] = useState<[number, number, number]>([0, 0, 0]);
  const [modelPosition, setModelPosition] = useState<[number, number, number]>([0, -1, 0]);
  const [showSpaceBackground, setShowSpaceBackground] = useState<boolean>(true);
  const [currentAnimation, setCurrentAnimation] = useState<string | null>(null);
  const [availableAnimations, setAvailableAnimations] = useState<string[]>([]);
  const [morphTargetDictionary, setMorphTargetDictionary] = useState<Record<string, number> | null>(null);
  const [morphTargetInfluences, setMorphTargetInfluences] = useState<number[] | null>(null);
  const [morphTargets, setMorphTargets] = useState<Record<string, number>>({});
  const [manualMorphTargets, setManualMorphTargets] = useState<Record<string, number>>({});
  const [modelUrl, setModelUrl] = useState<string>('/models/headonly.glb');
  const modelService = useRef<ModelService>(ModelService.getInstance());

  useEffect(() => {
    // 獲取初始狀態
    setModelLoaded(modelService.current.isModelLoaded());
    setModelScale(modelService.current.getModelScale());
    setModelRotation(modelService.current.getModelRotation());
    setModelPosition(modelService.current.getModelPosition());
    setShowSpaceBackground(modelService.current.getShowSpaceBackground());
    setCurrentAnimation(modelService.current.getCurrentAnimation());
    setAvailableAnimations(modelService.current.getAvailableAnimations());
    setMorphTargetDictionary(modelService.current.getMorphTargetDictionary());
    setMorphTargetInfluences(modelService.current.getMorphTargetInfluences());
    setMorphTargets(modelService.current.getMorphTargets());
    setManualMorphTargets(modelService.current.getManualMorphTargets());
    setModelUrl(modelService.current.getModelUrl());

    // 註冊模型加載事件
    const handleModelLoaded = () => {
      setModelLoaded(true);
    };
    
    // 註冊Morph Targets更新事件 (只關心來自 WS 的動態更新)
    const handleMorphTargetsUpdate = (updatedMorphTargets: Record<string, number>) => {
      setMorphTargets(updatedMorphTargets);
    };

    // 註冊可用動畫列表更新事件
    const handleAvailableAnimationsUpdate = (updatedAnimations: string[]) => {
      setAvailableAnimations(updatedAnimations);
    };
    
    const handleStateUpdate = () => {
      setModelUrl(modelService.current.getModelUrl());
      setModelScale(modelService.current.getModelScale());
      setModelRotation([...modelService.current.getModelRotation()]);
      setModelPosition([...modelService.current.getModelPosition()]);
      setShowSpaceBackground(modelService.current.getShowSpaceBackground());
      setCurrentAnimation(modelService.current.getCurrentAnimation());
      
      const dict = modelService.current.getMorphTargetDictionary();
      setMorphTargetDictionary(dict ? { ...dict } : null);
      const inf = modelService.current.getMorphTargetInfluences();
      setMorphTargetInfluences(inf ? [...inf] : null);
      setModelLoaded(modelService.current.isModelLoaded());
      setManualMorphTargets(modelService.current.getManualMorphTargets());
    };
    
    modelService.current.onModelLoaded(handleModelLoaded);
    modelService.current.onMorphTargetsUpdate(handleMorphTargetsUpdate);
    modelService.current.onAvailableAnimationsUpdate(handleAvailableAnimationsUpdate);
    modelService.current.registerStateUpdateCallback(handleStateUpdate);

    return () => {
      modelService.current.offModelLoaded(handleModelLoaded);
      modelService.current.offMorphTargetsUpdate(handleMorphTargetsUpdate);
      modelService.current.offAvailableAnimationsUpdate(handleAvailableAnimationsUpdate);
      modelService.current.unregisterStateUpdateCallback(handleStateUpdate);
    };
  }, []);

  const updateModelData = (data: Partial<ModelData>) => {
    if (data.modelScale !== undefined) {
      modelService.current.setModelScale(data.modelScale);
      setModelScale(data.modelScale);
    }
    
    if (data.modelRotation !== undefined) {
      modelService.current.setModelRotation(data.modelRotation);
      setModelRotation(data.modelRotation);
    }
    
    if (data.modelPosition !== undefined) {
      modelService.current.setModelPosition(data.modelPosition);
      setModelPosition(data.modelPosition);
    }
    
    if (data.showSpaceBackground !== undefined) {
      modelService.current.setShowSpaceBackground(data.showSpaceBackground);
      setShowSpaceBackground(data.showSpaceBackground);
    }
    
    if (data.currentAnimation !== undefined) {
      modelService.current.setCurrentAnimation(data.currentAnimation);
      setCurrentAnimation(data.currentAnimation);
    }
    
    if (data.modelUrl !== undefined) {
      modelService.current.switchModel(data.modelUrl);
      setModelUrl(data.modelUrl);
    }
  };

  const setAnimations = (animations: string[]) => {
    modelService.current.setAvailableAnimations(animations);
    setAvailableAnimations(animations);
  };

  const setMorphTargetData = useCallback((dictionary: Record<string, number> | null, influences: number[] | null) => {
    if (dictionary !== null) {
      modelService.current.setMorphTargetDictionary(dictionary);
    }
    
    if (influences !== null) {
      modelService.current.setMorphTargetInfluences(influences);
    }
  }, []);

  const rotateModel = useCallback((direction: 'left' | 'right') => {
    modelService.current.rotateModel(direction);
    setModelRotation(modelService.current.getModelRotation());
  }, []);

  const scaleModel = useCallback((factor: number) => {
    modelService.current.scaleModel(factor);
    setModelScale(modelService.current.getModelScale());
  }, []);

  const resetModel = useCallback(() => {
    modelService.current.resetModel();
    setModelScale(modelService.current.getModelScale());
    setModelRotation(modelService.current.getModelRotation());
    setModelPosition(modelService.current.getModelPosition());
    setCurrentAnimation(modelService.current.getCurrentAnimation());
    setMorphTargets(modelService.current.getMorphTargets());
    setManualMorphTargets(modelService.current.getManualMorphTargets());
  }, []);

  const toggleBackground = useCallback(() => {
    modelService.current.toggleBackground();
    setShowSpaceBackground(modelService.current.getShowSpaceBackground());
  }, []);

  const selectAnimation = useCallback((animationName: string) => {
    modelService.current.selectAnimation(animationName);
    setCurrentAnimation(modelService.current.getCurrentAnimation());
  }, []);

  const resetAllMorphTargets = useCallback(() => {
    modelService.current.resetAllMorphTargets();
  }, []);

  const applyPresetExpression = useCallback(async (expression: string) => {
    return await modelService.current.applyPresetExpression(expression);
  }, []);

  const switchModel = useCallback((url: string) => {
    modelService.current.switchModel(url);
  }, []);

  const updateMorphTargetInfluence = useCallback((name: string, value: number) => {
    modelService.current.updateMorphTargetInfluence(name, value);
  }, []);

  return {
    modelLoaded,
    modelScale,
    modelRotation,
    modelPosition,
    showSpaceBackground,
    currentAnimation,
    availableAnimations,
    morphTargetDictionary,
    morphTargetInfluences,
    morphTargets,
    manualMorphTargets,
    modelUrl,
    updateModelData,
    setAnimations,
    setMorphTargetData,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    selectAnimation,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    switchModel,
    getManualMorphTargets: modelService.current.getManualMorphTargets.bind(modelService.current),
  };
}

export default ModelService; 