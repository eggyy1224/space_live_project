import { StateCreator } from "zustand";
import { directorBus } from "../../director/bus";
import { DirectorState } from "../../../../shared/director/types";

export interface VideoScreen {
  id: string;
  currentVideo: string;
  visible: boolean;
  playing: boolean;
  volume: number;
  currentTime: number;
  duration: number;
  playbackRate: number;
}

export interface RuntimeSlice {
  bgm: string | null;
  bgmPlaying: boolean;
  bgmTime: number;
  sfxActive: boolean;
  selectedEffect: string | null;
  lightingPreset: string | null;
  cameraPreset: string | null;
  cameraAngles: [number, number, number] | null;
  cameraTransitionDuration: number;
  randomMode: boolean;
  fps: number;
  cpu: number;
  videoPlaying: boolean;
  videoVolume: number;
  videoCurrentTime: number;
  videoDuration: number;
  videoPlaybackRate: number;
  videoScreens: VideoScreen[];
  setVideoScreen: (
    id: string,
    partial: Partial<VideoScreen>,
    options?: { silent?: boolean },
  ) => void;
  setRuntime: (
    partial: Partial<RuntimeSlice>,
    options?: { silent?: boolean },
  ) => void;
}

export const createRuntimeSlice: StateCreator<RuntimeSlice> = (set) => ({
  bgm: null,
  bgmPlaying: false,
  bgmTime: 0,
  sfxActive: false,
  selectedEffect: null,
  lightingPreset: null,
  // 預設鏡位：對齊 baseline 使用 head_close_up
  cameraPreset: 'head_close_up',
  cameraAngles: null,
  // 對齊 baseline 過渡時間 1.2 秒
  cameraTransitionDuration: 1.2,
  randomMode: false,
  fps: 0,
  cpu: 0,
  videoPlaying: false,
  videoVolume: 1,
  videoCurrentTime: 0,
  videoDuration: 0,
  videoPlaybackRate: 1,
  videoScreens: [
    {
      id: "screen1",
      currentVideo: "",
      visible: false,
      playing: false,
      volume: 1,
      currentTime: 0,
      duration: 0,
      playbackRate: 1,
    },
    {
      id: "screen2",
      currentVideo: "",
      visible: false,
      playing: false,
      volume: 1,
      currentTime: 0,
      duration: 0,
      playbackRate: 1,
    },
    {
      id: "screen3",
      currentVideo: "",
      visible: false,
      playing: false,
      volume: 1,
      currentTime: 0,
      duration: 0,
      playbackRate: 1,
    },
  ],
  setVideoScreen: (id, partial, options?: { silent?: boolean }) =>
    set((state) => {
      const screens = state.videoScreens.map((s) =>
        s.id === id ? { ...s, ...partial } : s,
      );
      if (!options?.silent) {
        directorBus.emit("stateUpdate", { videoScreens: screens });
      }
      return { videoScreens: screens };
    }),
  setRuntime: (partial, options?: { silent?: boolean }) => {
    if (!options?.silent) {
      directorBus.emit("stateUpdate", partial as Partial<DirectorState>);
    }
    set(partial);
  },
});
