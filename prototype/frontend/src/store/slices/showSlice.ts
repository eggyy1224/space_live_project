import { StateCreator } from 'zustand';

export type ShowState = 'idle' | 'buildUp' | 'drop' | 'coolDown';

export interface ShowSlice {
  showState: ShowState;
  emitterCount: number;
  ringRadius: number;
  setShowState: (s: ShowState) => void;
  setEmitterCount: (n: number) => void;
  setRingRadius: (r: number) => void;
}

export const createShowSlice: StateCreator<ShowSlice> = (set) => ({
  showState: 'idle',
  emitterCount: 12,
  ringRadius: 1.2,
  setShowState: (s) => set({ showState: s }),
  setEmitterCount: (n) => set({ emitterCount: n }),
  setRingRadius: (r) => set({ ringRadius: r }),
});
