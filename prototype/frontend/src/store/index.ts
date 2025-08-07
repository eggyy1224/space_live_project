import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
// import { immer } from 'zustand/middleware/immer'; // 移除 immer

import { WebSocketSlice, createWebSocketSlice } from './slices/webSocketSlice';
import { ChatSlice, createChatSlice } from './slices/chatSlice';
import { HeadSlice, createHeadSlice } from './slices/headSlice';
import { AppSlice, createAppSlice } from './slices/appSlice';
import { MediaSlice, createMediaSlice } from './slices/mediaSlice';
import { BodySlice, createBodySlice } from './slices/bodySlice';
import { CharacterSlice, createCharacterSlice } from './slices/characterSlice';
import { AudioSettingsSlice, createAudioSettingsSlice } from './slices/audioSettingsSlice';
import { BackgroundAudioSlice, createBackgroundAudioSlice } from './slices/backgroundAudioSlice';
import { SpeechTextSlice, createSpeechTextSlice } from './slices/speechTextSlice';
import { RuntimeSlice, createRuntimeSlice } from './slices/runtimeSlice';
import { RoomSlice, createRoomSlice } from './slices/roomSlice';
import { createDanceSlice, DanceSlice } from './slices/danceSlice';
import { RealtimeScheduleSlice, createRealtimeScheduleSlice } from './slices/realtimeScheduleSlice';
// import { EmotionSlice, createEmotionSlice } from './slices/emotionSlice';
// import { AudioSlice, createAudioSlice } from './slices/audioSlice';

// 定義完整的 Zustand State
export type AppState =
  WebSocketSlice &
  ChatSlice &
  HeadSlice &
  AppSlice &
  MediaSlice &
  BodySlice &
  CharacterSlice &
  AudioSettingsSlice &
  BackgroundAudioSlice &
  SpeechTextSlice &
  RuntimeSlice &
  RoomSlice &
  DanceSlice &
  RealtimeScheduleSlice;

// 創建 Zustand Store
export const useStore = create<AppState>()(
  devtools(
    (...a) => ({
      ...createWebSocketSlice(...a),
      ...createChatSlice(...a),
      ...createHeadSlice(...a),
      ...createAppSlice(...a),
      ...createMediaSlice(...a),
      ...createBodySlice(...a),
      ...createCharacterSlice(...a),
      ...createAudioSettingsSlice(...a),
      ...createBackgroundAudioSlice(...a),
      ...createSpeechTextSlice(...a),
      ...createRuntimeSlice(...a),
      ...createRoomSlice(...a),
      ...createDanceSlice(...a),
      ...createRealtimeScheduleSlice(...a),
    }),
    { name: 'AppStore' } // Optional: Name for Redux DevTools
  )
);
