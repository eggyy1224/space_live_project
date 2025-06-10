# 音頻驅動的3D背景系統

本文檔描述了專案中實現的音頻驅動3D背景系統。該系統提供多種對音頻輸入做出反應的視覺效果，增強用戶體驗。

## 系統組件概述

系統主要由以下組件構成：

| 組件名稱 | 文件路徑 | 功能描述 | 觸發方式 |
|---------|--------|---------|--------|
| SpeechBackground | prototype/frontend/src/components/SpeechBackground.tsx | 對用戶語音輸入做出反應的背景牆 | audioAverageVolume |
| MusicBackground | prototype/frontend/src/components/MusicBackground.tsx | 對背景音樂做出反應的太空音樂播放器 | bgmIntensity |
| EffectBackground | prototype/frontend/src/components/EffectBackground.tsx | 對特定事件觸發的粒子效果 | effectTrigger |
| P5SpaceEffect | prototype/frontend/src/components/P5SpaceEffect.tsx | P5.js風格的粒子系統 | bgmIntensity |
| DynamicAudioBackgrounds | prototype/frontend/src/components/DynamicAudioBackgrounds.tsx | 整合所有背景效果的容器組件 | - |

## 組件詳細說明

### SpeechBackground

一個對語音音量做出反應的背景牆。當用戶說話時，背景牆會根據音量變化發光強度。

- **位置**：z=-15（為避免與前景元素衝突）
- **觸發參數**：audioAverageVolume
- **反應方式**：音量越大，發光強度越高
- **字幕來源**：即時語音模組傳回的轉錄文字會即時更新於此背景牆，使用 3D 打字機特效顯示。

### MusicBackground

一個對背景音樂強度做出反應的太空音樂播放器，具有環繞粒子效果。

- **主要特點**：
  - 漂浮的3D播放器模型
  - 環繞播放器的粒子系統
  - 多種幾何形狀的粒子（球體、立方體、環形等）
  - 基於音樂強度的顏色和運動變化
  - 支持"瘋狂模式"，提供更隨機和誇張的視覺效果

- **觸發參數**：bgmIntensity
- **反應方式**：音樂強度影響粒子運動速度、大小、顏色和發光強度

### EffectBackground

對特定事件（如用戶操作或系統回應）做出反應的特效系統。

- **特點**：
  - 擴散的環形波紋
  - 長時間持續的粒子效果
  - 高對比度的顏色

- **觸發參數**：effectTrigger
- **反應方式**：每次觸發時創建新的擴散環

### P5SpaceEffect

P5.js風格的粒子系統，創建太空中漂浮的粒子效果。

- **特點**：
  - 大量三維空間中的粒子
  - 對音樂強度做出反應
  - 漸變的顏色效果
  - 平滑的粒子運動

- **觸發參數**：bgmIntensity
- **反應方式**：音樂強度影響粒子速度、大小和顏色

## 整合與使用

所有背景效果通過 `DynamicAudioBackgrounds` 組件整合在一起，並在主場景中使用。這種模塊化設計允許：

1. 輕鬆啟用/禁用特定背景效果
2. 獨立控制每種效果的參數
3. 根據不同場景需求組合不同效果

## 狀態管理

背景系統使用全局狀態來接收音頻輸入：

- **audioAverageVolume**：麥克風輸入的平均音量
- **bgmIntensity**：背景音樂的強度
- **effectTrigger**：特效觸發計數器

## 自定義與擴展

系統設計具有高度可擴展性：

1. 可以通過調整現有組件的參數自定義視覺效果
2. 可以添加新的背景效果組件
3. 可以實現新的音頻分析參數以驅動更豐富的視覺效果

## 瘋狂模式

特殊的"瘋狂模式"提供更加誇張和隨機的視覺效果：

- 更快速和不規則的粒子運動
- 隨機的顏色變化
- 爆發式的粒子行為
- 不可預測的形狀變化

瘋狂模式通過組件接收的 `crazyModeRef` 參數控制，可在特定時刻啟用以增強視覺體驗。 