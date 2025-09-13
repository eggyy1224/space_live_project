import { StateCreator } from 'zustand';

export interface AudioSettingsSlice {
  bgmVolume: number;
  effectVolume: number;
  ttsVolume: number;
  setBgmVolume: (volume: number) => void;
  setEffectVolume: (volume: number) => void;
  setTtsVolume: (volume: number) => void;
}

export const createAudioSettingsSlice: StateCreator<AudioSettingsSlice> = (set) => ({
  bgmVolume: 0.7,
  effectVolume: 0.4,
  ttsVolume: 1.0,
  setBgmVolume: (volume) => set({ bgmVolume: Math.max(0, Math.min(1, volume)) }),
  setEffectVolume: (volume) => set({ effectVolume: Math.max(0, Math.min(1, volume)) }),
  // 允許語音音量提升至 2.0（結合 Realtime 播放器的壓縮器保護）
  setTtsVolume: (volume) => set({ ttsVolume: Math.max(0, Math.min(2, volume)) }),
});
