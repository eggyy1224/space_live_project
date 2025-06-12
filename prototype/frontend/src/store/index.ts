import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

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
// import { EmotionSlice, createEmotionSlice } from './slices/emotionSlice';
// import { AudioSlice, createAudioSlice } from './slices/audioSlice';

// 合併所有 slice 類型為最終 Store 類型
export type Store =
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
  RoomSlice;

// 創建 Zustand Store
export const useStore = create<Store>()(
  devtools(
    (set, get, api) => ({
      ...createWebSocketSlice(set, get, api),
      ...createChatSlice(set, get, api),
      ...createHeadSlice(set, get, api),
      ...createAppSlice(set, get, api),
      ...createMediaSlice(set, get, api),
      ...createBodySlice(set, get, api),
      ...createCharacterSlice(set, get, api),
      ...createAudioSettingsSlice(set, get, api),
      ...createBackgroundAudioSlice(set, get, api),
      ...createSpeechTextSlice(set, get, api),
      ...createRuntimeSlice(set, get, api),
      ...createRoomSlice(set, get, api),
    }),
    { name: 'AppStore' } // Optional: Name for Redux DevTools
  )
);
