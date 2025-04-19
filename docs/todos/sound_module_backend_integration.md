# 聲音模組後端整合計劃

此文件記錄如何在後端整合三種聲音模組（預設音效、合成音效和Freesound API）以及預錄歌曲的計劃。

## 1. 統一音頻管理系統

- [ ] **設計統一的音頻管理介面**
  - 設計一個抽象的音頻源接口（AudioSourceInterface）
  - 實現針對不同音頻來源的適配器：
    - 預設音效適配器（PresetSoundAdapter）
    - 合成音效適配器（SynthSoundAdapter）
    - Freesound API適配器（FreesoundAdapter）
    - 預錄歌曲適配器（PrerecordedSongAdapter）
  - 實現音頻管理器（AudioManager）統一管理各種音頻源

- [ ] **音頻元數據標準化**
  - 定義統一的音頻元數據格式
  - 為每種音頻類型實現元數據轉換方法
  - 實現標準化的音頻查詢與過濾機制

- [ ] **音頻播放指令標準化**
  - 定義統一的WebSocket指令格式
  - 支持單一音效和組合音效的播放
  - 設計可組合的音頻播放序列

## 2. 預錄歌曲整合與同步

- [ ] **預錄歌曲管理系統**
  - 設計歌曲庫結構和元數據格式
  - 實現歌曲分類、標籤和搜索功能
  - 建立歌曲與情緒標籤的映射

- [ ] **唇形同步（Lipsync）整合**
  - 分析預錄歌曲生成唇形同步數據
  - 實現歌曲音頻與角色嘴型同步播放
  - 研究現有Lipsync系統並擴展支持預錄內容

- [ ] **表情動作同步機制**
  - 為預錄歌曲添加表情動作標記
  - 實現歌曲情緒與角色表情同步
  - 開發基於音頻特徵的自動表情生成系統

- [ ] **多模態同步框架**
  - 設計統一的時間軸同步系統
  - 實現音頻、唇形、表情和動作的精確同步
  - 支持帶有標記的MIDI/JSON格式的表情動作腳本

## 3. WebSocket通信協議擴展

- [ ] **擴展現有WebSocket協議**
  - 修改`AudioManager`支持所有類型的音頻
  - 擴展WebSocket消息格式支持新的音頻指令
  - 定義音頻源類型區分標識

- [ ] **音頻播放指令設計**
  - 設計基本音效播放指令
  - 設計合成音效參數化指令
  - 設計Freesound音效引用指令
  - 設計歌曲播放與控制指令

- [ ] **播放控制指令**
  - 實現暫停/繼續功能
  - 實現停止功能
  - 實現音量調整
  - 實現播放進度控制

- [ ] **回應指令設計**
  - 實現播放狀態回應
  - 實現錯誤處理與回應
  - 實現準備就緒通知機制

## 4. 後端服務架構

- [ ] **聲音模組服務**
  - 實現`SoundModuleService`作為統一聲音管理服務
  - 整合現有的`SoundEffectService`
  - 設計音效選擇與推薦算法

- [ ] **Freesound API代理服務**
  - 實現API金鑰管理與安全訪問
  - 實現請求緩存與速率限制
  - 設計異步下載與預處理機制

- [ ] **預錄歌曲服務**
  - 實現歌曲庫管理
  - 設計流媒體播放機制
  - 實現歌曲分段與動態加載

- [ ] **合成音效服務增強**
  - 擴展現有的合成音效功能
  - 實現更複雜的聲音合成模式
  - 開發情境化音效序列生成

## 5. LLM整合與智能選擇

- [ ] **擴展LLM知識庫**
  - 向LLM提供可用音效的完整列表
  - 提供音效分類與標籤信息
  - 建立音效與情感/場景的關聯

- [ ] **基於上下文的音效推薦**
  - 實現基於對話內容的音效推薦
  - 開發基於角色情緒的音效選擇邏輯
  - 實現基於場景的音效序列生成

- [ ] **歌曲選擇邏輯**
  - 基於對話上下文選擇合適的歌曲
  - 實現基於情緒的歌曲推薦
  - 開發用戶偏好學習系統

- [ ] **混合音效策略**
  - 實現背景音樂與音效的組合
  - 開發多層次音效疊加機制
  - 設計音效轉換與混合算法

## 6. 緩存與性能優化

- [ ] **統一緩存系統**
  - 設計本地與雲端雙級緩存架構
  - 實現基於使用頻率的緩存策略
  - 實現預加載與異步加載機制

- [ ] **音頻處理優化**
  - 實現音頻格式轉換與壓縮
  - 開發音頻流分段處理
  - 優化大型音頻文件的處理

- [ ] **WebSocket性能優化**
  - 實現消息批處理機制
  - 優化音頻數據傳輸
  - 實現連接狀態管理與恢復

- [ ] **分佈式部署支持**
  - 設計支持分佈式部署的音頻服務
  - 實現跨服務的音頻資源共享
  - 開發負載均衡策略

## 7. API與集成點

- [ ] **統一的REST API**
  - 實現音效庫查詢API
  - 實現歌曲庫查詢API
  - 開發音效推薦API

- [ ] **WebSocket事件API**
  - 實現音效播放事件
  - 實現歌曲播放事件
  - 開發播放狀態變更事件

- [ ] **前端集成點**
  - 擴展前端`SoundEffectService`支持所有音頻類型
  - 更新`WebSocketService`處理所有音頻指令
  - 擴展UI組件支持新的音頻功能

- [ ] **LLM集成點**
  - 實現LLM音效選擇接口
  - 開發音效參數生成接口
  - 設計歌曲選擇與同步接口

## 8. 測試與部署

- [ ] **單元測試**
  - 為音頻服務編寫單元測試
  - 測試WebSocket音頻指令
  - 測試音頻同步機制

- [ ] **集成測試**
  - 測試前後端音頻交互
  - 測試LLM與音頻系統集成
  - 測試多用戶並發播放

- [ ] **性能測試**
  - 測試大量音效並發播放
  - 測試長時間歌曲播放
  - 測試網絡延遲下的同步效果

- [ ] **部署與監控**
  - 設計音頻服務部署架構
  - 實現音頻服務監控
  - 開發問題診斷工具

## 9. 詳細實現計劃

### 9.1 WebSocket協議擴展

```json
{
  "type": "audio",
  "source": "preset|synth|freesound|song",
  "payload": {
    // 針對不同source類型的特定參數
    "id": "sound_id或歌曲id",
    "startTime": 0,
    "duration": null,  // 可選，限制播放時長
    "volume": 1.0,
    "loop": false,
    // 唇形同步相關參數（僅歌曲需要）
    "lipsync": {
      "data": "base64編碼的唇形數據或URL",
      "format": "json|binary"
    },
    // 表情動作相關參數
    "expression": {
      "data": "base64編碼的表情數據或URL",
      "format": "json|binary"
    }
  }
}
```

### 9.2 音頻源類型定義

```typescript
interface AudioSource {
  type: 'preset' | 'synth' | 'freesound' | 'song';
  id: string;
  metadata: {
    name: string;
    duration: number;
    tags: string[];
    // 其他元數據...
  };
  getPlayableUrl(): Promise<string>;
  getWaveformData?(): Promise<ArrayBuffer>;
  getLipsyncData?(): Promise<any>;
  getExpressionData?(): Promise<any>;
}
```

### 9.3 唇形同步數據格式

```json
{
  "version": "1.0",
  "frameRate": 30,
  "frames": [
    {
      "time": 0,
      "phoneme": "sil",
      "value": 0.0
    },
    {
      "time": 0.033,
      "phoneme": "AA",
      "value": 0.7
    },
    // 更多唇形幀...
  ]
}
```

### 9.4 表情動作腳本格式

```json
{
  "version": "1.0",
  "frameRate": 30,
  "expressions": [
    {
      "time": 0,
      "name": "neutral",
      "value": 1.0
    },
    {
      "time": 1.5,
      "name": "happy",
      "value": 0.8
    },
    // 更多表情...
  ],
  "motions": [
    {
      "time": 0.5,
      "name": "nod",
      "params": {
        "strength": 0.7,
        "speed": 1.0
      }
    },
    // 更多動作...
  ]
}
```

## 10. 時間規劃

- **第一階段 (2週)**: 設計與實現基礎架構
  - 統一音頻管理介面
  - WebSocket協議擴展
  - 基本後端服務結構

- **第二階段 (2週)**: 實現預錄歌曲與同步功能
  - 唇形同步系統
  - 表情動作同步系統
  - 歌曲管理服務

- **第三階段 (2週)**: LLM整合與智能選擇
  - 擴展LLM知識庫
  - 音效推薦系統
  - 混合音效策略

- **第四階段 (1週)**: 性能優化與測試
  - 緩存系統
  - 性能優化
  - 測試與部署 

## 11. 角色語音與音效協調系統

- [ ] **聲音優先級管理**
  - 建立音頻類型優先級階層（角色語音 > 重要音效 > 背景音樂）
  - 實現可配置的優先級規則系統
  - 開發動態優先級調整機制（基於上下文和重要性）

- [ ] **音量平衡與自動混音**
  - 實現實時音量動態調整（例如，語音播放時自動降低背景音量）
  - 開發頻率敏感的混音系統（不同頻率範圍的聲音相互協調）
  - 設計環境感知混音（基於場景調整混音策略）

- [ ] **聲音時序協調**
  - 實現關鍵音效與語音的精確時序安排
  - 開發聲音佇列管理系統，避免同時播放過多音效
  - 設計智能音效延遲/提前策略

- [ ] **衝突檢測與解決**
  - 開發音頻衝突預測算法
  - 實現自動衝突解決策略（暫停、淡出、延遲、跳過）
  - 添加人工可干預的衝突處理機制

- [ ] **聲音空間化與定位**
  - 實現3D音頻定位，將不同音效分配到不同空間位置
  - 開發基於重要性的聲音空間分配
  - 設計動態聲音空間調整機制

### 11.1 角色語音優先級模型

```typescript
interface AudioPriorityRule {
  sourceType: AudioSourceType;          // 音頻來源類型
  baseLevel: number;                    // 基礎優先級(1-100)
  contextMultipliers: {                 // 上下文相關的優先級調整
    duringDialogue: number;             // 對話期間的優先級倍數
    duringImportantScene: number;       // 重要場景期間的優先級倍數
    duringBackgroundActivity: number;   // 背景活動期間的優先級倍數
  };
  volumeAdjustment: {                   // 與其他聲音共存時的音量調整
    whenHigherPriorityPlaying: number;  // 當更高優先級聲音播放時的音量調整倍數
    whenSamePriorityPlaying: number;    // 當同優先級聲音播放時的音量調整倍數
    whenLowerPriorityPlaying: number;   // 當較低優先級聲音播放時的音量調整倍數
  };
  interruptBehavior: 'stop' | 'fade' | 'pause' | 'continue'; // 被中斷時的行為
}

// 默認優先級設置
const defaultPriorityRules: Record<AudioSourceType, AudioPriorityRule> = {
  'character-voice': {
    sourceType: 'character-voice',
    baseLevel: 90,
    contextMultipliers: { duringDialogue: 1.1, duringImportantScene: 1.2, duringBackgroundActivity: 1.0 },
    volumeAdjustment: { whenHigherPriorityPlaying: 0.7, whenSamePriorityPlaying: 0.8, whenLowerPriorityPlaying: 1.0 },
    interruptBehavior: 'continue'
  },
  'sound-effect': {
    sourceType: 'sound-effect',
    baseLevel: 70,
    contextMultipliers: { duringDialogue: 0.8, duringImportantScene: 1.0, duringBackgroundActivity: 1.0 },
    volumeAdjustment: { whenHigherPriorityPlaying: 0.5, whenSamePriorityPlaying: 0.7, whenLowerPriorityPlaying: 1.0 },
    interruptBehavior: 'continue'
  },
  'background-music': {
    sourceType: 'background-music',
    baseLevel: 40,
    contextMultipliers: { duringDialogue: 0.6, duringImportantScene: 0.7, duringBackgroundActivity: 1.0 },
    volumeAdjustment: { whenHigherPriorityPlaying: 0.4, whenSamePriorityPlaying: 0.6, whenLowerPriorityPlaying: 1.0 },
    interruptBehavior: 'fade'
  },
  'song': {
    sourceType: 'song',
    baseLevel: 85,
    contextMultipliers: { duringDialogue: 0.9, duringImportantScene: 1.0, duringBackgroundActivity: 1.0 },
    volumeAdjustment: { whenHigherPriorityPlaying: 0.6, whenSamePriorityPlaying: 0.8, whenLowerPriorityPlaying: 1.0 },
    interruptBehavior: 'pause'
  }
};
```

### 11.2 音頻混合策略

```typescript
interface AudioMixingStrategy {
  name: string;
  description: string;
  applyMixing: (activeSources: ActiveAudioSource[]) => AudioMixingAdjustments;
}

interface ActiveAudioSource {
  id: string;
  type: AudioSourceType;
  priority: number;
  volume: number;
  startedAt: number;
  duration?: number;
  position?: { x: number, y: number, z: number };
}

interface AudioMixingAdjustments {
  volumeAdjustments: Record<string, number>;  // 音源ID到音量調整的映射
  pauseIds: string[];                         // 應該暫停的音源ID
  stopIds: string[];                          // 應該停止的音源ID
  spatialAdjustments?: Record<string, { x: number, y: number, z: number }>;  // 空間定位調整
}

// 策略示例 - 語音優先混合策略
const voiceFirstMixingStrategy: AudioMixingStrategy = {
  name: 'voice-first',
  description: '優先保證語音清晰度的混合策略',
  applyMixing: (activeSources) => {
    // 實現混合邏輯...
    const adjustments: AudioMixingAdjustments = {
      volumeAdjustments: {},
      pauseIds: [],
      stopIds: []
    };
    
    // 找出所有角色語音音源
    const voiceSources = activeSources.filter(s => s.type === 'character-voice');
    
    if (voiceSources.length > 0) {
      // 有語音播放時，降低其他音源的音量
      activeSources.forEach(source => {
        if (source.type !== 'character-voice') {
          // 根據音源類型應用不同的音量調整係數
          const adjustmentFactor = source.type === 'background-music' ? 0.3 : 0.6;
          adjustments.volumeAdjustments[source.id] = adjustmentFactor;
        }
      });
    }
    
    return adjustments;
  }
};
```

### 11.3 角色語音與音效的時序協調

在處理角色語音和各種音效的協調時，一個關鍵挑戰是確保它們在時間上的精確安排。這不僅僅是關於音量和優先級，還關乎於何時播放什麼音效以達到最佳效果。

```typescript
interface AudioScheduleEntry {
  id: string;
  sourceType: AudioSourceType;
  scheduledTime: number;      // 相對於時間軸的播放時間點(毫秒)
  duration?: number;          // 預期持續時間
  priority: number;           // 計算得到的最終優先級
  params: any;                // 播放參數
}

class AudioScheduler {
  // 排程音頻播放，處理衝突
  scheduleAudio(entries: AudioScheduleEntry[]): ResolvedSchedule {
    // 1. 按時間和優先級排序
    const sortedEntries = [...entries].sort((a, b) => {
      // 首先按時間排序
      if (a.scheduledTime !== b.scheduledTime) {
        return a.scheduledTime - b.scheduledTime;
      }
      // 時間相同按優先級排序
      return b.priority - a.priority;
    });
    
    // 2. 時序衝突檢測與解決
    const resolvedEntries: ResolvedAudioEntry[] = [];
    let currentlyPlaying: ResolvedAudioEntry[] = [];
    
    for (const entry of sortedEntries) {
      // 檢查此條目是否與當前播放的任何音頻衝突
      const conflicts = this.detectConflicts(entry, currentlyPlaying);
      
      if (conflicts.length === 0) {
        // 無衝突，正常添加
        const resolvedEntry = { ...entry, adjustments: {} };
        resolvedEntries.push(resolvedEntry);
        currentlyPlaying.push(resolvedEntry);
      } else {
        // 有衝突，應用解決策略
        const { adjustedEntry, adjustments } = this.resolveConflicts(entry, conflicts);
        
        if (adjustedEntry) {
          resolvedEntries.push(adjustedEntry);
          currentlyPlaying.push(adjustedEntry);
        }
        
        // 應用對當前播放音頻的調整
        this.applyAdjustments(currentlyPlaying, adjustments);
      }
      
      // 更新當前播放列表，移除已經結束的音頻
      const currentTime = entry.scheduledTime;
      currentlyPlaying = currentlyPlaying.filter(playing => {
        return !playing.duration || 
          playing.scheduledTime + playing.duration > currentTime;
      });
    }
    
    return { entries: resolvedEntries };
  }
  
  // 衝突檢測
  private detectConflicts(entry: AudioScheduleEntry, playing: ResolvedAudioEntry[]): ResolvedAudioEntry[] {
    // 檢測邏輯...
    return [];
  }
  
  // 衝突解決
  private resolveConflicts(entry: AudioScheduleEntry, conflicts: ResolvedAudioEntry[]): 
    { adjustedEntry: ResolvedAudioEntry | null, adjustments: AudioAdjustments } {
    // 解決邏輯...
    return { adjustedEntry: null, adjustments: { volumeChanges: {} } };
  }
  
  // 應用調整
  private applyAdjustments(entries: ResolvedAudioEntry[], adjustments: AudioAdjustments): void {
    // 應用邏輯...
  }
}
```

這些擴展將確保角色語音與其他音頻源能夠和諧協作，不會相互干擾，從而提供最佳的用戶體驗。特別是在直播或交互式場景中，角色的語音回覆需要清晰傳達，同時背景音樂和音效也能適當地增強氛圍。 