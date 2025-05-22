import { StateCreator } from 'zustand';

export interface BackgroundAudioSlice {
  bgmIntensity: number;
  effectTrigger: number;
  setBgmIntensity: (value: number) => void;
  triggerEffect: () => void;
}

export const createBackgroundAudioSlice: StateCreator<BackgroundAudioSlice> = (
  set
) => ({
  bgmIntensity: 0,
  effectTrigger: 0,
  setBgmIntensity: (value) => set({ bgmIntensity: value }),
  triggerEffect: () => set((state) => ({ effectTrigger: state.effectTrigger + 1 })),
});
