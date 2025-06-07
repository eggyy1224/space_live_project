import { StateCreator } from 'zustand';
import { DEFAULT_SCENE, getSceneById, type SceneConfig } from '../../config/sceneConfig';

export interface RoomSlice {
  // 房間場景狀態
  showRoomScene: boolean;
  currentSceneId: string;
  roomSceneUrl: string;
  roomPosition: [number, number, number];
  roomRotation: [number, number, number];
  roomScale: [number, number, number];
  
  // UI 狀態
  isRoomControlPanelVisible: boolean;
  
  // 房間場景操作
  toggleRoomScene: () => void;
  setShowRoomScene: (show: boolean) => void;
  switchScene: (sceneId: string) => void;
  setRoomSceneUrl: (url: string) => void;
  setRoomPosition: (position: [number, number, number]) => void;
  setRoomRotation: (rotation: [number, number, number]) => void;
  setRoomScale: (scale: [number, number, number]) => void;
  resetRoomTransform: () => void;
  
  // UI 操作
  toggleRoomControlPanel: () => void;
}

export const createRoomSlice = (set: any, get: any, api: any) => ({
  // 初始狀態
  showRoomScene: true,
  currentSceneId: DEFAULT_SCENE.id,
  roomSceneUrl: DEFAULT_SCENE.url,
  roomPosition: DEFAULT_SCENE.defaultPosition || [0, 0, 0],
  roomRotation: DEFAULT_SCENE.defaultRotation || [0, 0, 0],
  roomScale: DEFAULT_SCENE.defaultScale || [2, 2, 2],
  
  // UI 狀態
  isRoomControlPanelVisible: false,
  
  // 操作
  toggleRoomScene: () => {
    const currentState = get();
    set({ showRoomScene: !currentState.showRoomScene });
  },
  
  setShowRoomScene: (show: boolean) => {
    set({ showRoomScene: show });
  },
  
  switchScene: (sceneId: string) => {
    const scene = getSceneById(sceneId);
    if (scene) {
      set({
        currentSceneId: sceneId,
        roomSceneUrl: scene.url,
        roomPosition: scene.defaultPosition || [0, 0, 0],
        roomRotation: scene.defaultRotation || [0, 0, 0],
        roomScale: scene.defaultScale || [2, 2, 2]
      });
    }
  },
  
  setRoomSceneUrl: (url: string) => set({ 
    roomSceneUrl: url 
  }),
  
  setRoomPosition: (position: [number, number, number]) => set({ 
    roomPosition: position 
  }),
  
  setRoomRotation: (rotation: [number, number, number]) => set({ 
    roomRotation: rotation 
  }),
  
  setRoomScale: (scale: [number, number, number]) => set({ 
    roomScale: scale 
  }),
  
  resetRoomTransform: () => {
    const currentState = get();
    const scene = getSceneById(currentState.currentSceneId);
    if (scene) {
      set({
        roomPosition: scene.defaultPosition || [0, 0, 0],
        roomRotation: scene.defaultRotation || [0, 0, 0],
        roomScale: scene.defaultScale || [2, 2, 2]
      });
    }
  },
  
  // UI 操作
  toggleRoomControlPanel: () => {
    const currentState = get();
    set({ isRoomControlPanelVisible: !currentState.isRoomControlPanelVisible });
  }
}); 