import { StateCreator } from 'zustand';

// 定義可用的陣型
export const formations = [
  'circle', 
  'grid', 
  'line'
] as const;

export type Formation = typeof formations[number];

export interface DanceSlice {
  /**
   * 當前舞團陣型
   */
  currentFormation: Formation;
  /**
   * 舞者數量
   */
  dancerCount: number;
  /**
   * 舞團整體位置
   */
  danceGroupPosition: [number, number, number];
  /**
   * 舞團舞者縮放
   */
  danceGroupScale: number;
  /**
   * 設置當前舞團陣型
   * @param formation - 陣型名稱
   */
  setFormation: (formation: Formation) => void;
  /**
   * 設置舞者數量
   * @param count - 數量
   */
  setDancerCount: (count: number) => void;
  /**
   * 設置舞團位置
   * @param axis - 'x' | 'y' | 'z'
   * @param value - 數值
   */
  setDanceGroupPosition: (axis: 'x' | 'y' | 'z', value: number) => void;
  /**
   * 設置舞團縮放
   * @param scale - 縮放值
   */
  setDanceGroupScale: (scale: number) => void;
}

export const createDanceSlice: StateCreator<DanceSlice> = (set) => ({
  currentFormation: 'circle', // 預設為圓形
  dancerCount: 100, // 預設為 100 人
  danceGroupPosition: [0, -25, 0], // 預設位置
  danceGroupScale: 8, // 預設大小
  setFormation: (formation) => set({ currentFormation: formation }),
  setDancerCount: (count) => set({ dancerCount: count }),
  setDanceGroupPosition: (axis, value) =>
    set((state) => {
      const newPosition = [...state.danceGroupPosition] as [number, number, number];
      if (axis === 'x') newPosition[0] = value;
      else if (axis === 'y') newPosition[1] = value;
      else if (axis === 'z') newPosition[2] = value;
      return { danceGroupPosition: newPosition };
    }),
  setDanceGroupScale: (scale) => set({ danceGroupScale: scale }),
}); 