import { StateCreator } from 'zustand';

// AudioSlice 狀態與操作定義
export interface AudioSlice {
  // 狀態
  isRecording: boolean;
  isPlaying: boolean;
  isSpeaking: boolean;          // 新增：當前是否正在說話（播放音頻）
  isProcessing: boolean;
  currentAudioSource: string | null;
  micPermission: string; // 'granted' | 'denied' | 'prompt' 使用 string 類型
  audioStartTime: number | null; // 新增：音頻開始播放的時間（用於動畫序列同步）
  audioDuration: number | null;  // 新增：當前播放的音頻時長（用於動畫序列同步）
  
  // 操作
  setRecording: (recording: boolean) => void;
  setPlaying: (playing: boolean) => void;
  setSpeaking: (speaking: boolean) => void; // 新增：設置說話狀態
  setProcessing: (processing: boolean) => void;
  setAudioSource: (source: string | null) => void;
  setMicPermission: (permission: string) => void;
  setAudioStartTime: (time: number | null) => void; // 新增：設置音頻開始時間
  setAudioDuration: (duration: number | null) => void; // 新增：設置音頻時長
  
  // 便捷操作 (組合狀態更新)
  startPlaying: (source: string) => void;
  stopPlaying: () => void;
}

// 創建 Audio Slice
export const createAudioSlice: StateCreator<AudioSlice> = (set) => ({
  // 初始狀態
  isRecording: false,
  isPlaying: false,
  isSpeaking: false,           // 新增：初始為 false
  isProcessing: false,
  currentAudioSource: null,
  micPermission: 'prompt',
  audioStartTime: null,        // 新增：初始為 null
  audioDuration: null,         // 新增：初始為 null
  
  // 操作實現
  setRecording: (recording) => set({ isRecording: recording }),
  
  setPlaying: (playing) => set({ isPlaying: playing }),
  
  setSpeaking: (speaking) => set({ isSpeaking: speaking }), // 新增：實現 setSpeaking
  
  setProcessing: (processing) => set({ isProcessing: processing }),
  
  setAudioSource: (source) => set({ currentAudioSource: source }),
  
  setMicPermission: (permission) => set({ micPermission: permission }),
  
  setAudioStartTime: (time) => set({ audioStartTime: time }), // 新增：實現 setAudioStartTime
  
  setAudioDuration: (duration) => set({ audioDuration: duration }), // 新增：實現 setAudioDuration
  
  // 便捷操作
  startPlaying: (source) => set({ 
    isPlaying: true,
    isSpeaking: true,  // 新增：同時設置 isSpeaking
    currentAudioSource: source,
    audioStartTime: performance.now() // 新增：記錄開始時間
  }),
  
  stopPlaying: () => set({ 
    isPlaying: false,
    isSpeaking: false,  // 新增：同時設置 isSpeaking
    currentAudioSource: null,
    audioStartTime: null // 新增：重置開始時間
  }),
}); 