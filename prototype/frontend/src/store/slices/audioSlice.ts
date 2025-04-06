import { StateCreator } from 'zustand';

// AudioSlice 狀態與操作定義
export interface AudioSlice {
  // 狀態
  isRecording: boolean;
  isPlaying: boolean;
  currentAudioSource: string | null;
  
  // 操作
  setRecording: (recording: boolean) => void;
  setPlaying: (playing: boolean) => void;
  setAudioSource: (source: string | null) => void;
  
  // 便捷操作 (組合狀態更新)
  startPlaying: (source: string) => void;
  stopPlaying: () => void;
}

// 創建 Audio Slice
export const createAudioSlice: StateCreator<AudioSlice> = (set) => ({
  // 初始狀態
  isRecording: false,
  isPlaying: false,
  currentAudioSource: null,
  
  // 操作實現
  setRecording: (recording) => set({ isRecording: recording }),
  
  setPlaying: (playing) => set({ isPlaying: playing }),
  
  setAudioSource: (source) => set({ currentAudioSource: source }),
  
  // 便捷操作
  startPlaying: (source) => set({ 
    isPlaying: true,
    currentAudioSource: source 
  }),
  
  stopPlaying: () => set({ 
    isPlaying: false,
    currentAudioSource: null
  }),
}); 