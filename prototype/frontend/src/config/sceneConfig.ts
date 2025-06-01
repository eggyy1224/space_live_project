/**
 * 場景配置文件
 * 管理所有可用的 3D 場景
 */

export interface SceneConfig {
  id: string;
  name: string;
  url: string;
  description?: string;
  thumbnail?: string;
  defaultScale?: [number, number, number];
  defaultPosition?: [number, number, number];
  defaultRotation?: [number, number, number];
}

export const AVAILABLE_SCENES: SceneConfig[] = [
  {
    id: 'room-a',
    name: '6面房間A',
    url: '/scenes/6面房間A.glb',
    description: '原始6面房間場景',
    defaultScale: [2, 2, 2],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  },
  {
    id: 'room-b',
    name: '6面房間',
    url: '/scenes/6面房間.glb',
    description: '新版6面房間場景',
    defaultScale: [2, 2, 2],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  }
];

// 預設場景
export const DEFAULT_SCENE = AVAILABLE_SCENES[0];

// 根據 ID 獲取場景配置
export const getSceneById = (id: string): SceneConfig | undefined => {
  return AVAILABLE_SCENES.find(scene => scene.id === id);
};

// 獲取場景名稱列表
export const getSceneNames = (): string[] => {
  return AVAILABLE_SCENES.map(scene => scene.name);
};

// 獲取場景 ID 列表
export const getSceneIds = (): string[] => {
  return AVAILABLE_SCENES.map(scene => scene.id);
}; 