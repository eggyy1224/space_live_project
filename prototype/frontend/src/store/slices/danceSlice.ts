import { StateCreator } from 'zustand';

// 定義可用的陣型
export const formations = [
  'circle', 
  'grid-small', 
  'grid-medium', 
  'grid-large', 
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
   * 設置當前舞團陣型
   * @param formation - 陣型名稱
   */
  setFormation: (formation: Formation) => void;
  /**
   * 設置舞者數量
   * @param count - 數量
   */
  setDancerCount: (count: number) => void;
}

export const createDanceSlice: StateCreator<DanceSlice> = (set) => ({
  currentFormation: 'circle', // 預設為圓形
  dancerCount: 100, // 預設為 100 人
  setFormation: (formation) => set({ currentFormation: formation }),
  setDancerCount: (count) => set({ dancerCount: count }),
}); 