import { StateCreator } from 'zustand';

export interface RuntimeSlice {
  bgm: string | null;
  bgmTime: number;
  sfxActive: boolean;
  videoId: string | null;
  videoVisible: boolean;
  lightingPreset: string | null;
  cameraPreset: string | null;
  fps: number;
  cpu: number;
  gpu: number;
  setRuntime: (partial: Partial<RuntimeSlice>) => void;
}

export const createRuntimeSlice: StateCreator<RuntimeSlice> = (set) => ({
  bgm: null,
  bgmTime: 0,
  sfxActive: false,
  videoId: null,
  videoVisible: false,
  lightingPreset: null,
  cameraPreset: null,
  fps: 0,
  cpu: 0,
  gpu: 0,
  setRuntime: (partial) => set(partial),
});
