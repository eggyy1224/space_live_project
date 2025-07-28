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
    id: 'cyber-capsule',
    name: '賽博太空艙',
    url: '/scenes/賽博太空艙.glb',
    description: '未來感賽博太空艙',
    defaultScale: [200, 200, 200],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 185, 0] // Y 軸 180 度
  },
  {
    id: 'spaceship-control',
    name: '飛船控制間',
    url: '/scenes/飛船控制間.glb',
    description: '飛船駕駛艙場景',
    defaultScale: [200, 200, 200],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  },
  {
    id: 'star-ruins',
    name: '星際廢墟',
    url: '/scenes/星際廢墟.glb',
    description: '星際廢墟場景',
    defaultScale: [200, 200, 200],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  },
  {
    id: 'star-bedroom',
    name: '星際臥室',
    url: '/scenes/星際臥室.glb',
    description: '星際臥室場景',
    defaultScale: [200, 200, 200],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  },
  {
    id: 'space-capsule-2',
    name: '太空艙2',
    url: '/scenes/太空艙2.glb',
    description: '第二版太空艙',
    defaultScale: [200, 200, 200],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  },
  {
    id: 'space-capsule',
    name: '太空艙',
    url: '/scenes/太空艙.glb',
    description: '經典太空艙',
    defaultScale: [200, 200, 200],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  },
  {
    id: 'space-dancefloor',
    name: '太空舞池',
    url: '/scenes/太空舞池.glb',
    description: '太空舞池場景',
    defaultScale: [200, 200, 200],
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