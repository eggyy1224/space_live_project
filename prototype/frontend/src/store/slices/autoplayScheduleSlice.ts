import { StateCreator } from 'zustand';

export interface AutoplayScheduleSlice {
  autoplayEnabled: boolean;
  nextTrigger: number | null;
  intervalSeconds: number | null;
  setAutoplayEnabled: (enabled: boolean) => void;
  setNextTrigger: (ts: number | null) => void;
  setIntervalSeconds: (secs: number | null) => void;
  resetAutoplay: () => void;
}

export const createAutoplayScheduleSlice: StateCreator<AutoplayScheduleSlice> = (set) => ({
  autoplayEnabled: false,
  nextTrigger: null,
  intervalSeconds: null,
  setAutoplayEnabled: (enabled) => set({ autoplayEnabled: enabled }),
  setNextTrigger: (ts) => set({ nextTrigger: ts }),
  setIntervalSeconds: (secs) => set({ intervalSeconds: secs }),
  resetAutoplay: () => set({ autoplayEnabled: false, nextTrigger: null, intervalSeconds: null }),
});
