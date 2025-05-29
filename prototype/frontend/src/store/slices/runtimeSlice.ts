import { StateCreator } from 'zustand';

export interface RuntimeSlice {
  bgm: string | null;
  bgmPlaying: boolean;
  bgmTime: number;
  sfxActive: boolean;
  videoId: string | null;
  videoVisible: boolean;
  lightingPreset: string | null;
  cameraPreset: string | null;
  fps: number;
  cpu: number;
  setRuntime: (partial: Partial<RuntimeSlice>) => void;
}

export const createRuntimeSlice: StateCreator<RuntimeSlice> = (set) => ({
  bgm: null,
  bgmPlaying: false,
  bgmTime: 0,
  sfxActive: false,
  videoId: null,
  videoVisible: false,
  lightingPreset: null,
  cameraPreset: null,
  fps: 0,
  cpu: 0,
  setRuntime: (partial) => set(partial),
});
