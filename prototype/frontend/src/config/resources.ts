// 統一資源配置檔案 - 單一真相來源
// 所有媒體資源的路徑和配置都在這裡定義

import { CameraPreset } from '../camera';

// ==================== 音頻資源 ====================

export const AUDIO_PATHS = {
  BGM: '/audio/BGM/',
  EFFECTS: '/audio/effects/',
  GENERATED_SOUNDS: '/audio/generated_sounds/',
} as const;

// BGM 音樂檔案清單
export const BGM_FILES = [
  'spacelive_theme.mp3',
  'spacelive_theme2.mp3',
  'heavy_metal_bgm_01.mp3',
  'heavy_metal_bgm_02.mp3',
  'heavy_metal_bgm_03.mp3',
  'space_live_country_theme1.mp3',
  'space_live_country_theme2.mp3',
  'hihi.mp3',
  'hihi (1).mp3',
  'hihi (2).mp3',
  'hihi (3).mp3',
  '太空媽祖.mp3',
  '星際狂舞.mp3',
] as const;

// 音效檔案清單
export const EFFECT_FILES = [
  // 環境音效
  'winds_blowing.mp3',
  'spaceship_ambience_01.mp3',
  'spaceship_ambience_02.mp3',
  'spaceship_ambience_03.mp3',
  'spaceship_ambience_04.mp3',
  
  // 節奏音效
  'Energetic_fast_pace.mp3',
  'Ambient_keyboard_cli_2.mp3',
  
  // 綜藝節目音效
  'taiwan_variety_sfx_01.mp3',
  'taiwan_variety_sfx_02.mp3',
  'taiwan_variety_sfx_03.mp3',
  'taiwan_variety_sfx_04.mp3',
  
  // 測試音效
  '測試音效1.mp3',
  '測試音效2.mp3',
  '測試音效3.mp3',
  '測試音效4.mp3',
  '測試音效5.mp3',
  
  // 通訊音效
  '通訊聲1.mp3',
  '通訊聲2.mp3',
  '通訊聲3.mp3',
  '通訊聲4.mp3',
  
  // 警告音效
  '警告音1.mp3',
  '警告音2.mp3',
  '警告音3.mp3',
  
  // 故障音效
  '故障音1.mp3',
  '故障音2.mp3',
  '故障音3.mp3',
  '故障音4.mp3',
  
  // 戰鬥音效
  '電子砲1.mp3',
  '電子砲2.mp3',
  '電子砲3.mp3',
  
  // 特殊效果音效
  '聖光音效1.mp3',
  '聖光音效2.mp3',
  '聖光音效3.mp3',
  '物件漂浮音效1.mp3',
  '物件漂浮音效2.mp3',
  '物件漂浮音效3.mp3',
  
  // 文化音效
  '媽祖遶境1.mp3',
  '媽祖遶境2.mp3',
  '媽祖遶境3.mp3',
] as const;

// 音效分類常數
export const AMBIENT_EFFECTS = [
  'winds_blowing.mp3',
  'spaceship_ambience_01.mp3',
  'spaceship_ambience_02.mp3',
  'spaceship_ambience_03.mp3',
  'spaceship_ambience_04.mp3',
] as const;

export const COMMUNICATION_EFFECTS = [
  '通訊聲1.mp3',
  '通訊聲2.mp3',
  '通訊聲3.mp3',
  '通訊聲4.mp3',
] as const;

export const WARNING_EFFECTS = [
  '警告音1.mp3',
  '警告音2.mp3',
  '警告音3.mp3',
] as const;

export const MALFUNCTION_EFFECTS = [
  '故障音1.mp3',
  '故障音2.mp3',
  '故障音3.mp3',
  '故障音4.mp3',
] as const;

export const COMBAT_EFFECTS = [
  '電子砲1.mp3',
  '電子砲2.mp3',
  '電子砲3.mp3',
] as const;

export const SPECIAL_EFFECTS = [
  '聖光音效1.mp3',
  '聖光音效2.mp3',
  '聖光音效3.mp3',
  '物件漂浮音效1.mp3',
  '物件漂浮音效2.mp3',
  '物件漂浮音效3.mp3',
] as const;

export const CULTURAL_EFFECTS = [
  '媽祖遶境1.mp3',
  '媽祖遶境2.mp3',
  '媽祖遶境3.mp3',
] as const;

// ==================== 影片資源 ====================

export const VIDEO_PATH = '/videos/';

// 舞蹈類影片
export const DANCE_VIDEOS = [
  '/videos/太空熱舞3.mp4',
  '/videos/太空熱舞2.mp4',
  '/videos/太空熱舞.mp4',
  '/videos/太空辣妹跳舞.mp4',
  '/videos/太空走秀.mp4',
  '/videos/太空走秀2.mp4',
] as const;

// 生活類影片
export const LIFESTYLE_VIDEOS = [
  '/videos/太空瑜伽3.mp4',
  '/videos/太空瑜伽2.mp4',
  '/videos/太空瑜伽.mp4',
  '/videos/太空直播中.mp4',
  '/videos/太空直播中3.mp4',
  '/videos/太空泡水.mp4',
  '/videos/太空化妝.mp4',
  '/videos/太空打卡.mp4',
  '/videos/太空打卡2.mp4',
  '/videos/太空摘帽帽.mp4',
  '/videos/太空吃東西.mp4',
  '/videos/daily_life_1.mp4',
] as const;

// 娛樂類影片
export const ENTERTAINMENT_VIDEOS = [
  '/videos/太空鋪克牌.mp4',
  '/videos/太空鋪克牌2.mp4',
  '/videos/太空戀愛秀.mp4',
  '/videos/太空帶貨中.mp4',
  '/videos/小綠人動畫.mp4',
  '/videos/小綠人動畫2.mp4',
  '/videos/小綠人動畫3.mp4',
] as const;

// VR/科技類影片
export const VR_TECH_VIDEOS = [
  '/videos/太空VR.mp4',
  '/videos/太空VR2.mp4',
] as const;

// 太空特效類影片
export const SPACE_EFFECT_VIDEOS = [
  '/videos/火箭發射.mp4',
  '/videos/星際小可愛.mp4',
  '/videos/星際小籠包.mp4',
  '/videos/星際聽音樂.mp4',
  '/videos/黑洞.mp4',
  '/videos/模擬星雲圖.mp4',
  '/videos/太空巨乳.mp4',
  '/videos/太空史萊姆.mp4',
  '/videos/space_live_video_1.mp4',
  '/videos/space_live.mp4',
] as const;

// 所有影片的聯合清單
export const ALL_VIDEOS = [
  ...DANCE_VIDEOS,
  ...LIFESTYLE_VIDEOS,
  ...ENTERTAINMENT_VIDEOS,
  ...VR_TECH_VIDEOS,
  ...SPACE_EFFECT_VIDEOS,
] as const;

// Director Panel 快速選擇的影片清單 (常用的幾個)
export const DIRECTOR_VIDEOS = [
  '/videos/太空直播中.mp4',
  '/videos/太空直播中3.mp4',
  '/videos/太空熱舞.mp4',
  '/videos/星際小可愛.mp4',
  '/videos/太空瑜伽.mp4',
  '/videos/火箭發射.mp4',
  '/videos/太空化妝.mp4',
  '/videos/太空戀愛秀.mp4',
  '/videos/太空VR.mp4',
] as const;

// ==================== 預設配置 ====================

// 燈光預設
export const LIGHTING_PRESETS = [
  'idle',
  'dramatic',
  'calm',
] as const;

// 簡化的相機預設 (給 Director Panel 用)
export const CAMERA_PRESET_NAMES = [
  'wide',
  'closeUp',
  'sideView',
] as const;

// 完整的相機預設配置 (給場景控制用)
export const CAMERA_PRESETS: CameraPreset[] = [
  { name: 'overview', position: [0, 20, 100], target: [0, 0, 0], fov: 50 },
  { name: 'head_close_up', position: [0, -3, 8], target: [0, -5, 0], fov: 40 },
  { name: 'dance_circle_view', position: [0, 50, 80], target: [0, -25, 0], fov: 60 },
  { name: 'side_view', position: [-80, 10, 0], target: [0, -10, 0], fov: 55 },
  { name: 'low_angle_head', position: [0, -7, 7], target: [0, -5, 0], fov: 45 },
  { name: 'center_orbit_high_1', position: [15, 10, 15], target: [0, 0, 0], fov: 50 },
  { name: 'center_orbit_high_2', position: [-15, 10, 15], target: [0, 0, 0], fov: 50 },
  { name: 'center_orbit_low_1', position: [10, -2, 10], target: [0, 0, 0], fov: 45 },
  { name: 'center_orbit_low_2', position: [-10, -2, -10], target: [0, 0, 0], fov: 45 },
  { name: 'top_down_center', position: [0, 25, 0.1], target: [0, 0, 0], fov: 50 },
  { name: 'dramatic_angle_1', position: [20, -5, -20], target: [0, -2, 0], fov: 60 },
  { name: 'dramatic_angle_2', position: [-20, 5, 20], target: [0, 0, 0], fov: 60 },
  { name: 'behind_head_looking_out', position: [0, -3, -5], target: [0, -3, 20], fov: 50 },
  { name: 'fly_by_left', position: [-50, 0, 10], target: [50, 0, 0], fov: 70 },
  { name: 'fly_by_right', position: [50, 0, 10], target: [-50, 0, 0], fov: 70 },
  { name: 'frontal_dynamic_low', position: [0, -10, 30], target: [0, 0, 0], fov: 50 },
  { name: 'frontal_dynamic_high', position: [0, 15, 25], target: [0, 0, 0], fov: 45 },
  { name: 'orbit_head_1', position: [10, -5, 3], target: [0, -5, 0], fov: 40 },
  { name: 'orbit_head_2', position: [-10, -5, 3], target: [0, -5, 0], fov: 40 },
  { name: 'full_shot_dancers', position: [0, 10, 120], target: [0, -20, 0], fov: 55 },
];

// Director Panel 相機預設名稱映射 (簡化名稱 -> 完整預設名稱)
export const CAMERA_PRESET_MAPPING = {
  wide: 'overview',
  closeUp: 'head_close_up',
  sideView: 'side_view',
} as const;

// 相機預設的友善顯示名稱
export const CAMERA_PRESET_DISPLAY_NAMES: Record<string, string> = {
  'overview': '總覽',
  'head_close_up': '頭部特寫',
  'dance_circle_view': '舞蹈圓圈視角',
  'side_view': '側面視角',
  'low_angle_head': '低角度頭部',
  'center_orbit_high_1': '中心軌道高位1',
  'center_orbit_high_2': '中心軌道高位2',
  'center_orbit_low_1': '中心軌道低位1',
  'center_orbit_low_2': '中心軌道低位2',
  'top_down_center': '俯視中心',
  'dramatic_angle_1': '戲劇角度1',
  'dramatic_angle_2': '戲劇角度2',
  'behind_head_looking_out': '頭後向外看',
  'fly_by_left': '左側飛越',
  'fly_by_right': '右側飛越',
  'frontal_dynamic_low': '正面動態低位',
  'frontal_dynamic_high': '正面動態高位',
  'orbit_head_1': '環繞頭部1',
  'orbit_head_2': '環繞頭部2',
  'full_shot_dancers': '舞者全景',
};

// ==================== 輔助函數 ====================

/**
 * 根據分類和權重創建混合播放清單
 */
export function createMixedPlaylist(categories: readonly (readonly string[])[], weights: number[]): string[] {
  if (categories.length !== weights.length) {
    throw new Error('Categories and weights arrays must have the same length');
  }

  const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
  const mixed: string[] = [];

  // 計算每個分類應該有多少個影片
  categories.forEach((category, index) => {
    const ratio = weights[index] / totalWeight;
    const count = Math.round(category.length * ratio);
    
    // 隨機選擇該分類的影片
    const shuffled = [...category].sort(() => Math.random() - 0.5);
    mixed.push(...shuffled.slice(0, count));
  });

  // 最終打亂整個清單
  return mixed.sort(() => Math.random() - 0.5);
}

/**
 * 取得完整的音頻檔案路徑
 */
export function getBgmPath(filename: string): string {
  if (filename.startsWith('http://') || filename.startsWith('https://')) {
    return filename;
  }
  if (filename.startsWith('/')) {
    return filename;
  }
  return `${AUDIO_PATHS.BGM}${filename}`;
}

export function getEffectPath(filename: string): string {
  if (filename.startsWith('http://') || filename.startsWith('https://')) {
    return filename;
  }
  if (filename.startsWith('/')) {
    return filename;
  }
  // 檢查是否為生成的音效（包含 "generated_" 前綴）
  if (filename.includes('generated_')) {
    return `${AUDIO_PATHS.GENERATED_SOUNDS}${filename}`;
  }
  return `${AUDIO_PATHS.EFFECTS}${filename}`;
}

export function getGeneratedSoundPath(filename: string): string {
  if (filename.startsWith('http://') || filename.startsWith('https://')) {
    return filename;
  }
  if (filename.startsWith('/')) {
    return filename;
  }
  return `${AUDIO_PATHS.GENERATED_SOUNDS}${filename}`;
}

/**
 * 驗證檔案是否存在於清單中
 */
export function isBgmFileValid(filename: string): boolean {
  return BGM_FILES.includes(filename as any);
}

export function isEffectFileValid(filename: string): boolean {
  return EFFECT_FILES.includes(filename as any);
}

export function isVideoFileValid(filepath: string): boolean {
  return ALL_VIDEOS.includes(filepath as any);
}

// ==================== 類型定義 ====================

export type BgmFile = typeof BGM_FILES[number];
export type EffectFile = typeof EFFECT_FILES[number];
export type VideoFile = typeof ALL_VIDEOS[number];
export type DanceVideo = typeof DANCE_VIDEOS[number];
export type LifestyleVideo = typeof LIFESTYLE_VIDEOS[number];
export type EntertainmentVideo = typeof ENTERTAINMENT_VIDEOS[number];
export type VrTechVideo = typeof VR_TECH_VIDEOS[number];
export type SpaceEffectVideo = typeof SPACE_EFFECT_VIDEOS[number];
export type DirectorVideo = typeof DIRECTOR_VIDEOS[number];
export type AmbientEffect = typeof AMBIENT_EFFECTS[number];
export type CommunicationEffect = typeof COMMUNICATION_EFFECTS[number];
export type WarningEffect = typeof WARNING_EFFECTS[number];
export type MalfunctionEffect = typeof MALFUNCTION_EFFECTS[number];
export type CombatEffect = typeof COMBAT_EFFECTS[number];
export type SpecialEffect = typeof SPECIAL_EFFECTS[number];
export type CulturalEffect = typeof CULTURAL_EFFECTS[number];
export type LightingPreset = typeof LIGHTING_PRESETS[number];
export type CameraPresetName = typeof CAMERA_PRESET_NAMES[number]; 