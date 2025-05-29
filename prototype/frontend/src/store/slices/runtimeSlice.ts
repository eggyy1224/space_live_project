import { StateCreator } from 'zustand';

export interface RuntimeSlice {
  bgm: string | null;
  bgmPlaying: boolean;
  bgmTime: number;
  sfxActive: boolean;
  selectedEffect: string | null;
  videoId: string | null;
  videoVisible: boolean;
  lightingPreset: string | null;
  cameraPreset: string | null;
  randomMode: boolean;
  fps: number;
  cpu: number;
  setRuntime: (partial: Partial<RuntimeSlice>) => void;
}

export const createRuntimeSlice: StateCreator<RuntimeSlice> = (set) => ({
  bgm: null,
  bgmPlaying: false,
  bgmTime: 0,
  sfxActive: false,
  selectedEffect: null,
  videoId: null,
  videoVisible: false,
  lightingPreset: null,
  cameraPreset: null,
  randomMode: true,
  fps: 0,
  cpu: 0,
  setRuntime: (partial) => set(partial),
});
