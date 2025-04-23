# 音效系統擴充功能設計

## 概述

根據`docs/Soundeffect_related/音效系統功能與擴充指南.md`的內容，本文檔設計音效系統的擴充功能，包括音效資源管理、音效組合（Combo）、音效分級策略和事件驅動擴展。

## 主要擴充方向

1. **資源管理與快取機制**：實現高效的音效資源加載和快取策略
2. **Combo音效系統**：支持複雜的音效串聯和組合
3. **音效分級與優先級**：根據重要性和使用頻率對音效進行分級
4. **事件驅動擴展**：通過事件機制支持與其他系統的整合
5. **自定義音效處理**：允許通過配置添加自定義音效處理邏輯

## 1. 資源管理與快取機制

### 音效資源管理器設計

```typescript
// src/services/SoundResourceManager.ts
import { IndexedDBStorage } from '../utils/IndexedDBStorage';

// 音效資源類型
export enum ResourceTier {
  TIER_0 = 0, // 關鍵即時資源
  TIER_1 = 1, // 高頻使用資源
  TIER_2 = 2  // 低頻使用資源
}

export interface SoundResource {
  id: string;
  url: string;
  tier: ResourceTier;
  metadata?: {
    name?: string;
    duration?: number;
    size?: number;
    format?: string;
    tags?: string[];
    source?: string;
    license?: string;
  };
  lastUsed?: number;
  usageCount?: number;
}

export class SoundResourceManager {
  private cache: IndexedDBStorage<SoundResource>;
  private memoryCache: Map<string, AudioBuffer> = new Map();
  private audioContext: AudioContext;
  private loadingPromises: Map<string, Promise<AudioBuffer>> = new Map();
  
  constructor() {
    this.cache = new IndexedDBStorage<SoundResource>('sound-resources');
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  
  // 獲取音效資源（優先從內存獲取，其次從IndexedDB，最後從網絡）
  async getResource(id: string): Promise<AudioBuffer> {
    // 檢查內存快取
    if (this.memoryCache.has(id)) {
      // 更新使用統計
      this.updateUsageStats(id);
      return this.memoryCache.get(id)!;
    }
    
    // 檢查是否正在加載
    if (this.loadingPromises.has(id)) {
      return this.loadingPromises.get(id)!;
    }
    
    // 從IndexedDB獲取
    const loadPromise = (async () => {
      try {
        const resourceInfo = await this.cache.get(id);
        
        // 如果有快取記錄
        if (resourceInfo) {
          // 更新使用統計
          this.updateUsageStats(id);
          
          // 從URL加載音頻數據
          const audioBuffer = await this.loadAudioBuffer(resourceInfo.url);
          
          // 加入內存快取
          this.addToMemoryCache(id, audioBuffer, resourceInfo.tier);
          
          return audioBuffer;
        }
        
        // 從網絡加載（假設ID可以映射到API路徑）
        const resource = await this.fetchResourceFromAPI(id);
        const audioBuffer = await this.loadAudioBuffer(resource.url);
        
        // 保存到快取
        await this.cache.set(id, resource);
        
        // 加入內存快取
        this.addToMemoryCache(id, audioBuffer, resource.tier);
        
        return audioBuffer;
      } catch (error) {
        console.error(`Failed to load sound resource: ${id}`, error);
        throw error;
      } finally {
        // 清理加載中的Promise
        this.loadingPromises.delete(id);
      }
    })();
    
    // 記錄加載中的Promise
    this.loadingPromises.set(id, loadPromise);
    
    return loadPromise;
  }
  
  // 批量預加載資源
  async preloadResources(ids: string[]): Promise<void> {
    // 獲取資源信息
    const resources = await Promise.all(
      ids.map(id => this.cache.get(id).catch(() => null)).filter(Boolean)
    );
    
    // 按tier排序，優先加載較低tier的資源
    resources.sort((a, b) => a.tier - b.tier);
    
    // 逐個加載
    for (const resource of resources) {
      if (!this.memoryCache.has(resource.id)) {
        try {
          const audioBuffer = await this.loadAudioBuffer(resource.url);
          this.addToMemoryCache(resource.id, audioBuffer, resource.tier);
        } catch (error) {
          console.warn(`Failed to preload: ${resource.id}`, error);
        }
      }
    }
  }
  
  // 從Freesound API獲取並保存資源
  async saveFreeSound(freesoundId: string, tier: ResourceTier = ResourceTier.TIER_2): Promise<string> {
    // 資源ID格式：freesound_{id}
    const resourceId = `freesound_${freesoundId}`;
    
    // 檢查快取
    const existing = await this.cache.get(resourceId);
    if (existing) {
      return resourceId;
    }
    
    // 從Freesound API獲取資源
    const freesoundData = await this.fetchFreeSoundData(freesoundId);
    
    // 創建資源記錄
    const resource: SoundResource = {
      id: resourceId,
      url: freesoundData.previews['preview-hq-mp3'],
      tier,
      metadata: {
        name: freesoundData.name,
        duration: freesoundData.duration,
        tags: freesoundData.tags,
        license: freesoundData.license,
        source: 'freesound',
      },
      lastUsed: Date.now(),
      usageCount: 0
    };
    
    // 保存到快取
    await this.cache.set(resourceId, resource);
    
    return resourceId;
  }
  
  // 清理快取
  async cleanupCache(maxSize: number = 100 * 1024 * 1024): Promise<void> {
    // 獲取所有資源
    const allResources = await this.cache.getAll();
    
    // 計算當前大小
    let totalSize = allResources.reduce((sum, resource) => 
      sum + (resource.metadata?.size || 0), 0);
    
    // 如果未超出限制，不需要清理
    if (totalSize <= maxSize) return;
    
    // 按重要性排序（tier、使用頻率、最近使用時間）
    const sortedResources = [...allResources].sort((a, b) => {
      // 優先按tier排序
      if (a.tier !== b.tier) return a.tier - b.tier;
      
      // 然後按使用頻率
      if ((a.usageCount || 0) !== (b.usageCount || 0)) 
        return (b.usageCount || 0) - (a.usageCount || 0);
      
      // 最後按最近使用時間
      return (b.lastUsed || 0) - (a.lastUsed || 0);
    });
    
    // 移除最低優先級的資源，直到大小合適
    let i = sortedResources.length - 1;
    while (totalSize > maxSize && i >= 0) {
      const resource = sortedResources[i];
      
      // 不會刪除tier 0的資源
      if (resource.tier > ResourceTier.TIER_0) {
        totalSize -= (resource.metadata?.size || 0);
        await this.cache.delete(resource.id);
        
        // 同時從內存快取中移除
        this.memoryCache.delete(resource.id);
      }
      
      i--;
    }
  }
  
  // 從URL加載音頻緩衝
  private async loadAudioBuffer(url: string): Promise<AudioBuffer> {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    return await this.audioContext.decodeAudioData(arrayBuffer);
  }
  
  // 添加到內存快取
  private addToMemoryCache(id: string, buffer: AudioBuffer, tier: ResourceTier): void {
    // Tier 0和Tier 1的資源保留在內存中
    if (tier <= ResourceTier.TIER_1) {
      this.memoryCache.set(id, buffer);
      
      // 如果內存快取過大，可以進行清理
      if (this.memoryCache.size > 100) { // 假設最多保留100個
        this.cleanupMemoryCache();
      }
    }
  }
  
  // 清理內存快取
  private cleanupMemoryCache(): void {
    // 如果沒有太多資源，就不清理
    if (this.memoryCache.size <= 50) return; // 保留至少50個
    
    // 獲取使用頻率最低的非Tier 0資源
    const resourceEntries = Array.from(this.memoryCache.entries());
    const entriesToRemove = resourceEntries
      .filter(([id]) => {
        const resource = this.cache.get(id);
        return resource.then(r => r?.tier > ResourceTier.TIER_0);
      })
      .sort(([idA], [idB]) => {
        const resourceA = this.cache.get(idA);
        const resourceB = this.cache.get(idB);
        return Promise.all([resourceA, resourceB]).then(([a, b]) => 
          (a?.usageCount || 0) - (b?.usageCount || 0)
        );
      })
      .slice(0, Math.floor(this.memoryCache.size * 0.3)); // 移除30%的資源
    
    // 移除低優先級資源
    for (const [id] of entriesToRemove) {
      this.memoryCache.delete(id);
    }
  }
  
  // 更新使用統計
  private async updateUsageStats(id: string): Promise<void> {
    const resource = await this.cache.get(id);
    if (resource) {
      resource.lastUsed = Date.now();
      resource.usageCount = (resource.usageCount || 0) + 1;
      await this.cache.set(id, resource);
    }
  }
  
  // 從API獲取資源
  private async fetchResourceFromAPI(id: string): Promise<SoundResource> {
    // 實際實現應根據API設計
    const response = await fetch(`/api/sound-resources/${id}`);
    if (!response.ok) throw new Error(`Failed to fetch resource: ${id}`);
    return await response.json();
  }
  
  // 從Freesound API獲取資源
  private async fetchFreeSoundData(id: string): Promise<any> {
    // 實際實現應根據Freesound API設計
    const response = await fetch(`/api/freesound/${id}`);
    if (!response.ok) throw new Error(`Failed to fetch Freesound: ${id}`);
    return await response.json();
  }
}
```

## 2. Combo音效系統

### Combo定義與處理

```typescript
// src/models/ComboDefinition.ts
export interface ComboStep {
  resourceId: string;
  type: string;
  duration: number;
  delay?: number;
  volume?: number;
  rate?: number;
  options?: Record<string, any>;
}

export interface ComboDefinition {
  id: string;
  name: string;
  description?: string;
  steps: ComboStep[];
  totalDuration?: number;
  category?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

// src/services/ComboManager.ts
import { ComboDefinition } from '../models/ComboDefinition';

export class ComboManager {
  private definitions: Map<string, ComboDefinition> = new Map();
  
  constructor() {}
  
  // 加載Combo定義
  async loadDefinitions(): Promise<void> {
    try {
      // 從服務器或本地配置加載定義
      const response = await fetch('/api/combo-definitions');
      const definitions: ComboDefinition[] = await response.json();
      
      // 存儲定義
      definitions.forEach(def => {
        // 計算總持續時間（如果未提供）
        if (!def.totalDuration) {
          def.totalDuration = def.steps.reduce((total, step) => 
            total + (step.duration || 0) + (step.delay || 0), 0);
        }
        
        this.definitions.set(def.id, def);
      });
      
      console.log(`Loaded ${definitions.length} combo definitions`);
    } catch (error) {
      console.error('Failed to load combo definitions', error);
    }
  }
  
  // 獲取Combo定義
  getDefinition(id: string): ComboDefinition | undefined {
    return this.definitions.get(id);
  }
  
  // 獲取所有定義
  getAllDefinitions(): ComboDefinition[] {
    return Array.from(this.definitions.values());
  }
  
  // 按類別獲取定義
  getDefinitionsByCategory(category: string): ComboDefinition[] {
    return Array.from(this.definitions.values())
      .filter(def => def.category === category);
  }
  
  // 按標籤篩選定義
  getDefinitionsByTags(tags: string[]): ComboDefinition[] {
    return Array.from(this.definitions.values())
      .filter(def => def.tags?.some(tag => tags.includes(tag)));
  }
  
  // 創建自定義Combo
  createCustomCombo(definition: Omit<ComboDefinition, 'id'>): string {
    const id = `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const fullDefinition: ComboDefinition = {
      ...definition,
      id
    };
    
    // 計算總持續時間
    fullDefinition.totalDuration = fullDefinition.steps.reduce(
      (total, step) => total + (step.duration || 0) + (step.delay || 0), 0
    );
    
    // 存儲定義
    this.definitions.set(id, fullDefinition);
    
    // 可選：持久化到本地存儲
    this.saveCustomCombos();
    
    return id;
  }
  
  // 保存自定義Combo
  private saveCustomCombos(): void {
    // 提取自定義Combo
    const customCombos = Array.from(this.definitions.values())
      .filter(def => def.id.startsWith('custom_'));
    
    // 保存到本地存儲
    localStorage.setItem('customCombos', JSON.stringify(customCombos));
  }
  
  // 加載自定義Combo
  loadCustomCombos(): void {
    const saved = localStorage.getItem('customCombos');
    if (saved) {
      try {
        const combos: ComboDefinition[] = JSON.parse(saved);
        combos.forEach(combo => {
          this.definitions.set(combo.id, combo);
        });
        console.log(`Loaded ${combos.length} custom combos`);
      } catch (error) {
        console.error('Failed to load custom combos', error);
      }
    }
  }
}
```

## 3. AudioCoordinator擴展

為AudioCoordinator添加音效擴充功能：

```typescript
// src/services/AudioCoordinator.ts (擴展部分)
import { SoundResourceManager, ResourceTier } from './SoundResourceManager';
import { ComboManager } from './ComboManager';

class AudioCoordinator {
  private resourceManager: SoundResourceManager;
  private comboManager: ComboManager;
  
  constructor() {
    // 其他初始化...
    
    this.resourceManager = new SoundResourceManager();
    this.comboManager = new ComboManager();
    
    // 初始化
    this.initialize();
  }
  
  private async initialize(): Promise<void> {
    // 加載Combo定義
    await this.comboManager.loadDefinitions();
    
    // 加載自定義Combo
    this.comboManager.loadCustomCombos();
    
    // 預加載Tier 0資源
    await this.preloadCriticalResources();
  }
  
  // 預加載關鍵資源
  private async preloadCriticalResources(): Promise<void> {
    try {
      // 獲取所有Tier 0資源ID
      const response = await fetch('/api/sound-resources/critical');
      const criticalResources: string[] = await response.json();
      
      // 預加載
      await this.resourceManager.preloadResources(criticalResources);
      console.log(`Preloaded ${criticalResources.length} critical resources`);
    } catch (error) {
      console.error('Failed to preload critical resources', error);
    }
  }
  
  // 播放Combo音效
  async playCombo(comboId: string, options?: PlayRequestOptions): Promise<string> {
    const definition = this.comboManager.getDefinition(comboId);
    if (!definition) {
      throw new Error(`Combo not found: ${comboId}`);
    }
    
    // 創建播放請求
    const request: PlayRequest = {
      track: options?.track || 'sfx',
      type: 'combo',
      source: definition,
      priority: options?.priority || 60,
      options
    };
    
    // 交由通用播放邏輯處理
    return await this.play(request);
  }
  
  // 播放Freesound音效
  async playFreesound(freesoundId: string, options?: PlayRequestOptions): Promise<string> {
    // 先保存到資源管理器
    const resourceId = await this.resourceManager.saveFreeSound(
      freesoundId, 
      options?.tier || ResourceTier.TIER_2
    );
    
    // 創建播放請求
    const request: PlayRequest = {
      track: options?.track || 'sfx',
      type: 'freesound',
      source: resourceId,
      priority: options?.priority || 50,
      options
    };
    
    // 交由通用播放邏輯處理
    return await this.play(request);
  }
  
  // 創建自定義Combo
  createCustomCombo(steps: any[], name: string = 'Custom Combo'): string {
    // 將步驟格式化為ComboStep
    const formattedSteps = steps.map(step => ({
      resourceId: step.resourceId,
      type: step.type || 'sfx',
      duration: step.duration || 1.0,
      delay: step.delay || 0,
      volume: step.volume,
      rate: step.rate,
      options: step.options
    }));
    
    // 創建Combo定義
    return this.comboManager.createCustomCombo({
      name,
      steps: formattedSteps,
      category: 'custom',
      tags: ['custom']
    });
  }
  
  // 獲取可用的Combo列表
  getAvailableCombos(category?: string, tags?: string[]): any[] {
    let combos;
    
    if (category) {
      combos = this.comboManager.getDefinitionsByCategory(category);
    } else if (tags && tags.length > 0) {
      combos = this.comboManager.getDefinitionsByTags(tags);
    } else {
      combos = this.comboManager.getAllDefinitions();
    }
    
    // 格式化輸出
    return combos.map(combo => ({
      id: combo.id,
      name: combo.name,
      description: combo.description,
      duration: combo.totalDuration,
      category: combo.category,
      tags: combo.tags
    }));
  }
  
  // 預加載資源
  async preloadResources(resourceIds: string[]): Promise<void> {
    await this.resourceManager.preloadResources(resourceIds);
  }
  
  // 清理資源快取
  async cleanupResources(): Promise<void> {
    await this.resourceManager.cleanupCache();
  }
}
```

## 4. 事件驅動擴展設計

通過事件系統支持音效系統的動態擴展：

```typescript
// src/services/AudioEventSystem.ts
import mitt from 'mitt';

// 定義事件類型
export type AudioEventTypes = {
  // 音效相關事件
  'sound:started': { id: string, track: string, type: string };
  'sound:ended': { id: string, track: string, type: string };
  'sound:failed': { id: string, track: string, type: string, error: any };
  
  // 音軌相關事件
  'track:volume-changed': { track: string, volume: number };
  'track:ducking': { track: string, isDucking: boolean };
  
  // 資源相關事件
  'resource:loaded': { id: string, tier: number };
  'resource:failed': { id: string, error: any };
  
  // Combo相關事件
  'combo:step-started': { comboId: string, step: number, total: number };
  'combo:completed': { comboId: string };
  
  // 系統事件
  'system:initialized': void;
  'system:error': { code: string, message: string };
  
  // 用戶可擴展的自定義事件
  [key: `custom:${string}`]: any;
};

// 創建事件發射器
export const audioEvents = mitt<AudioEventTypes>();

// src/services/AudioCoordinator.ts (事件整合部分)
import { audioEvents } from './AudioEventSystem';

class AudioCoordinator {
  // 其他代碼...
  
  constructor() {
    // 初始化...
    
    // 系統初始化完成事件
    setTimeout(() => {
      audioEvents.emit('system:initialized', undefined);
    }, 0);
  }
  
  // 使用事件系統進行通知
  private notifyPlaybackStarted(sound: SoundInfo): void {
    audioEvents.emit('sound:started', {
      id: sound.id,
      track: sound.track,
      type: sound.type
    });
  }
  
  private notifyPlaybackEnded(sound: SoundInfo): void {
    audioEvents.emit('sound:ended', {
      id: sound.id,
      track: sound.track,
      type: sound.type
    });
  }
  
  private notifyComboStep(comboId: string, step: number, total: number): void {
    audioEvents.emit('combo:step-started', {
      comboId,
      step,
      total
    });
  }
  
  private notifyComboCompleted(comboId: string): void {
    audioEvents.emit('combo:completed', {
      comboId
    });
  }
  
  // 設置音軌音量時發送事件
  setVolume(track: string, volume: number): void {
    // 實際設置邏輯...
    
    // 發送事件
    audioEvents.emit('track:volume-changed', {
      track,
      volume
    });
  }
  
  // 提供事件訂閱介面
  on<K extends keyof AudioEventTypes>(event: K, handler: (data: AudioEventTypes[K]) => void): void {
    audioEvents.on(event, handler);
  }
  
  off<K extends keyof AudioEventTypes>(event: K, handler: (data: AudioEventTypes[K]) => void): void {
    audioEvents.off(event, handler);
  }
}
```

## 5. 音效插件系統

設計插件系統允許擴展音效功能：

```typescript
// src/plugins/AudioPluginSystem.ts
import { AudioCoordinator } from '../services/AudioCoordinator';
import { audioEvents } from '../services/AudioEventSystem';

// 插件接口
export interface AudioPlugin {
  id: string;
  name: string;
  version: string;
  initialize(coordinator: AudioCoordinator): Promise<void>;
  destroy?(): Promise<void>;
}

// 插件管理器
export class AudioPluginManager {
  private plugins: Map<string, AudioPlugin> = new Map();
  private coordinator: AudioCoordinator;
  
  constructor(coordinator: AudioCoordinator) {
    this.coordinator = coordinator;
  }
  
  // 註冊插件
  async registerPlugin(plugin: AudioPlugin): Promise<void> {
    if (this.plugins.has(plugin.id)) {
      throw new Error(`Plugin already registered: ${plugin.id}`);
    }
    
    try {
      // 初始化插件
      await plugin.initialize(this.coordinator);
      
      // 存儲插件
      this.plugins.set(plugin.id, plugin);
      
      console.log(`Plugin registered: ${plugin.name} (${plugin.version})`);
    } catch (error) {
      console.error(`Failed to initialize plugin: ${plugin.id}`, error);
      throw error;
    }
  }
  
  // 卸載插件
  async unregisterPlugin(pluginId: string): Promise<boolean> {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) return false;
    
    try {
      // 調用插件銷毀方法（如果有）
      if (plugin.destroy) {
        await plugin.destroy();
      }
      
      // 移除插件
      this.plugins.delete(pluginId);
      
      console.log(`Plugin unregistered: ${plugin.name}`);
      return true;
    } catch (error) {
      console.error(`Failed to unregister plugin: ${pluginId}`, error);
      return false;
    }
  }
  
  // 獲取插件
  getPlugin(pluginId: string): AudioPlugin | undefined {
    return this.plugins.get(pluginId);
  }
  
  // 獲取所有插件
  getAllPlugins(): AudioPlugin[] {
    return Array.from(this.plugins.values());
  }
}

// 示例插件：音頻視覺化
export class AudioVisualizerPlugin implements AudioPlugin {
  id = 'audio-visualizer';
  name = 'Audio Visualizer';
  version = '1.0.0';
  
  private analyser: AnalyserNode | null = null;
  private dataArray: Uint8Array | null = null;
  private animationFrameId: number | null = null;
  private canvasContext: CanvasRenderingContext2D | null = null;
  
  async initialize(coordinator: AudioCoordinator): Promise<void> {
    // 獲取音頻上下文
    const audioContext = coordinator.getAudioContext();
    
    // 創建分析器
    this.analyser = audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    
    // 連接到主輸出
    coordinator.connectToMaster(this.analyser);
    
    // 準備數據數組
    const bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(bufferLength);
    
    // 初始化畫布
    this.initializeCanvas();
    
    // 開始動畫
    this.startAnimation();
    
    // 監聽事件
    audioEvents.on('sound:started', this.handleSoundStarted);
    audioEvents.on('sound:ended', this.handleSoundEnded);
  }
  
  async destroy(): Promise<void> {
    // 停止動畫
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    
    // 移除事件監聽
    audioEvents.off('sound:started', this.handleSoundStarted);
    audioEvents.off('sound:ended', this.handleSoundEnded);
    
    // 清理資源
    this.analyser = null;
    this.dataArray = null;
    this.canvasContext = null;
  }
  
  private initializeCanvas(): void {
    const canvas = document.createElement('canvas');
    canvas.width = 300;
    canvas.height = 150;
    canvas.style.position = 'fixed';
    canvas.style.bottom = '20px';
    canvas.style.right = '20px';
    canvas.style.zIndex = '1000';
    canvas.style.background = 'rgba(0, 0, 0, 0.7)';
    canvas.style.borderRadius = '5px';
    canvas.style.display = 'none';
    
    document.body.appendChild(canvas);
    
    this.canvasContext = canvas.getContext('2d');
  }
  
  private startAnimation(): void {
    const draw = () => {
      this.animationFrameId = requestAnimationFrame(draw);
      
      if (!this.analyser || !this.dataArray || !this.canvasContext) return;
      
      // 獲取頻率數據
      this.analyser.getByteFrequencyData(this.dataArray);
      
      // 清空畫布
      const canvas = this.canvasContext.canvas;
      this.canvasContext.clearRect(0, 0, canvas.width, canvas.height);
      
      // 設置樣式
      this.canvasContext.fillStyle = 'rgb(0, 255, 0)';
      
      // 繪製頻譜
      const barWidth = (canvas.width / this.dataArray.length) * 2.5;
      let barHeight;
      let x = 0;
      
      for (let i = 0; i < this.dataArray.length; i++) {
        barHeight = this.dataArray[i] / 2;
        
        this.canvasContext.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
        this.canvasContext.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        
        x += barWidth + 1;
      }
    };
    
    this.animationFrameId = requestAnimationFrame(draw);
  }
  
  private handleSoundStarted = () => {
    // 顯示視覺化
    if (this.canvasContext) {
      this.canvasContext.canvas.style.display = 'block';
    }
  };
  
  private handleSoundEnded = () => {
    // 檢查是否還有其他聲音在播放
    // 如果沒有，隱藏視覺化
    // 這裡簡化處理，實際應該檢查是否還有活躍聲音
    setTimeout(() => {
      if (this.canvasContext) {
        this.canvasContext.canvas.style.display = 'none';
      }
    }, 500);
  };
}
```

## 6. 實施策略與優先順序

實現音效系統擴充功能的建議步驟：

1. **資源管理層**：
   - 首先實現SoundResourceManager，建立高效的資源管理機制
   - 實現IndexedDB快取和內存緩存策略
   - 添加資源分級和預加載功能

2. **音效組合系統**：
   - 設計並實現ComboManager
   - 創建基礎的Combo定義和處理邏輯
   - 實現Combo的播放和控制

3. **基礎功能擴展**：
   - 擴展AudioCoordinator支持新的資源管理和Combo功能
   - 實現新的播放方法（playCombo、playFreesound等）
   - 增強錯誤處理和資源清理

4. **事件系統整合**：
   - 建立AudioEventSystem
   - 在AudioCoordinator中集成事件通知
   - 確保所有關鍵操作都有相應的事件通知

5. **插件系統**：
   - 實現AudioPluginManager和插件接口
   - 開發示例插件（如AudioVisualizerPlugin）
   - 測試插件的註冊、使用和卸載流程

## 結論

這份音效系統擴充功能設計強化了現有系統的以下能力：

1. **高效資源管理**：通過三級分層和智能快取實現高效的音效資源管理
2. **組合式音效**：支持複雜的音效組合和串聯
3. **事件驅動擴展**：通過標準化事件系統支持系統間整合
4. **插件式架構**：允許通過插件機制擴展系統功能

這些擴充功能將使音效系統更加靈活、高效且易於擴展，為未來需求提供堅實基礎。 