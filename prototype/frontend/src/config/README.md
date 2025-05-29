# 統一資源配置使用指南

本文檔說明如何使用統一的資源配置檔案 `resources.ts`。

## 概述

`resources.ts` 是專案的單一真相來源，包含所有媒體資源的路徑和配置。所有組件都應該從這個檔案導入資源清單，而不是自己定義。

## 資源類型

### 🎵 音頻資源

```typescript
import { BGM_FILES, EFFECT_FILES, getBgmPath, getEffectPath } from '../config/resources';

// 使用 BGM 檔案清單
const bgmFile = BGM_FILES[0]; // 'spacelive_theme.mp3'

// 取得完整路徑
const fullPath = getBgmPath(bgmFile); // '/audio/BGM/spacelive_theme.mp3'
```

### 🎬 影片資源

```typescript
import { 
  DANCE_VIDEOS, 
  LIFESTYLE_VIDEOS, 
  SPACE_EFFECT_VIDEOS, 
  ALL_VIDEOS,
  DIRECTOR_VIDEOS,
  createMixedPlaylist 
} from '../config/resources';

// 使用分類影片清單
const danceVideos = DANCE_VIDEOS;

// 創建混合播放清單
const mixedPlaylist = createMixedPlaylist(
  [DANCE_VIDEOS, LIFESTYLE_VIDEOS], 
  [7, 3] // 7:3 的比例
);
```

### 📹 相機預設

```typescript
import { 
  CAMERA_PRESETS, 
  CAMERA_PRESET_NAMES, 
  CAMERA_PRESET_MAPPING 
} from '../config/resources';

// 使用完整的相機預設
const cameraManager = useCameraManager(camera, CAMERA_PRESETS, 'overview');

// 使用簡化的預設名稱 (給 UI 用)
const presetOptions = CAMERA_PRESET_NAMES; // ['wide', 'closeUp', 'sideView']
```

### 💡 燈光預設

```typescript
import { LIGHTING_PRESETS } from '../config/resources';

// 使用燈光預設清單
const lightingOptions = LIGHTING_PRESETS; // ['idle', 'dramatic', 'calm']
```

## 類型安全

配置檔案提供完整的 TypeScript 類型支援：

```typescript
import type { BgmFile, EffectFile, VideoFile, LightingPreset, CameraPresetName } from '../config/resources';

// 這些類型確保只能使用有效的資源名稱
const bgm: BgmFile = 'spacelive_theme.mp3'; // ✅ 正確
const bgm: BgmFile = 'invalid_file.mp3';    // ❌ TypeScript 錯誤
```

## 驗證函數

```typescript
import { isBgmFileValid, isEffectFileValid, isVideoFileValid } from '../config/resources';

// 驗證檔案是否存在於清單中
if (isBgmFileValid('spacelive_theme.mp3')) {
  // 檔案有效，可以播放
}
```

## 更新資源

當需要新增或修改資源時：

1. **只修改 `resources.ts`** - 不要在其他檔案中重複定義
2. **更新相關的分類** - 確保新影片被加入正確的分類
3. **測試所有引用的組件** - 確保變更不會破壞現有功能

## 已更新的組件

以下組件已經更新為使用統一配置：

- ✅ `DirectorMonitorHUD.tsx` - 使用統一的資源清單和新增音效控制
- ✅ `BackgroundSoundSystem.tsx` - 使用統一的音頻資源
- ✅ `DynamicAudioBackgrounds.tsx` - 使用統一的影片資源和混合函數
- ✅ `SceneContainer.tsx` - 使用統一的相機預設

## 範例：新增新的音樂檔案

1. 將檔案放入 `public/audio/BGM/` 目錄
2. 在 `resources.ts` 中更新 `BGM_FILES` 陣列：

```typescript
export const BGM_FILES = [
  'spacelive_theme.mp3',
  // ... 其他檔案
  'new_music.mp3', // 新增的檔案
] as const;
```

3. 所有使用 `BGM_FILES` 的組件會自動包含新檔案，無需修改其他程式碼！ 