import { StateCreator } from 'zustand';

// MediaSlice 狀態與操作定義
export interface MediaSlice {
  // 狀態
  isSpeaking: boolean;          // 標記當前是否有語音正在播放或錄製中 (用於驅動基礎說話嘴型)
  audioStartTime: number | null; // 記錄當前播放語音的開始時間戳 (performance.now()), 用於計算 elapsedTime
  isRecording: boolean;         // 標記是否正在錄音 (從 AudioService 移過來統一管理)

  // 操作
  setSpeaking: (speaking: boolean) => void;
  setAudioStartTime: (time: number | null) => void;
  setRecording: (recording: boolean) => void;
}

// 創建 Media Slice
export const createMediaSlice: StateCreator<MediaSlice> = (set) => ({
  // 初始狀態
  isSpeaking: false,
  audioStartTime: null,
  isRecording: false,

  // 操作實現
  setSpeaking: (speaking) => set({ isSpeaking: speaking }),
  setAudioStartTime: (time) => set({ audioStartTime: time }),
  setRecording: (recording) => set({ isRecording: recording }),
}); 