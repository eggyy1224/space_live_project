import { StateCreator } from 'zustand';

export interface RoomSlice {
  // 房間場景狀態
  showRoomScene: boolean;
  roomSceneUrl: string;
  roomPosition: [number, number, number];
  roomRotation: [number, number, number];
  roomScale: [number, number, number];
  
  // UI 狀態
  isRoomControlPanelVisible: boolean;
  
  // 房間場景操作
  toggleRoomScene: () => void;
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
  roomSceneUrl: '/scenes/6面房間A.glb',
  roomPosition: [0, 0, 0],
  roomRotation: [0, 0, 0],
  roomScale: [2, 2, 2],
  
  // UI 狀態
  isRoomControlPanelVisible: false,
  
  // 操作
  toggleRoomScene: () => {
    const currentState = get();
    set({ showRoomScene: !currentState.showRoomScene });
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
  
  resetRoomTransform: () => set({
    roomPosition: [0, 0, 0],
    roomRotation: [0, 0, 0],
    roomScale: [2, 2, 2]
  }),
  
  // UI 操作
  toggleRoomControlPanel: () => {
    const currentState = get();
    set({ isRoomControlPanelVisible: !currentState.isRoomControlPanelVisible });
  }
}); 