import { StateCreator } from 'zustand';

export interface RuntimeSlice {
  bgm: string | null;
  bgmPlaying: boolean;
  bgmTime: number;
  sfxActive: boolean;
  selectedEffect: string | null;
  lightingPreset: string | null;
  cameraPreset: string | null;
  randomMode: boolean;
  fps: number;
  cpu: number;
  videoPlaying: boolean;
  videoVolume: number;
  videoCurrentTime: number;
  videoDuration: number;
  videoPlaybackRate: number;
  videoScreens: {
    id: string;
    currentVideo: string;
    visible: boolean;
  }[];
  setVideoScreen: (
    id: string,
    partial: Partial<{ id: string; currentVideo: string; visible: boolean }>
  ) => void;
  setRuntime: (partial: Partial<RuntimeSlice>) => void;
}

export const createRuntimeSlice: StateCreator<RuntimeSlice> = (set) => ({
  bgm: null,
  bgmPlaying: false,
  bgmTime: 0,
  sfxActive: false,
  selectedEffect: null,
  lightingPreset: null,
  cameraPreset: null,
  randomMode: true,
  fps: 0,
  cpu: 0,
  videoPlaying: false,
  videoVolume: 1,
  videoCurrentTime: 0,
  videoDuration: 0,
  videoPlaybackRate: 1,
  videoScreens: [
    { id: 'screen1', currentVideo: '', visible: false },
    { id: 'screen2', currentVideo: '', visible: false },
    { id: 'screen3', currentVideo: '', visible: false },
  ],
  setVideoScreen: (id, partial) =>
    set((state) => ({
      videoScreens: state.videoScreens.map((s) =>
        s.id === id ? { ...s, ...partial } : s
      ),
    })),
  setRuntime: (partial) => set(partial),
});
