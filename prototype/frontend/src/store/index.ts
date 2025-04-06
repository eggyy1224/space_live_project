import { create } from 'zustand';

import { WebSocketSlice, createWebSocketSlice } from './slices/webSocketSlice';
import { ChatSlice, createChatSlice } from './slices/chatSlice';
import { ModelSlice, createModelSlice } from './slices/modelSlice';
import { AudioSlice, createAudioSlice } from './slices/audioSlice';
import { AppSlice, createAppSlice } from './slices/appSlice';

// 合併所有 slice 類型為最終 Store 類型
export type Store = WebSocketSlice & ChatSlice & ModelSlice & AudioSlice & AppSlice;

// 創建 Zustand Store
export const useStore = create<Store>((...a) => ({
  ...createWebSocketSlice(...a),
  ...createChatSlice(...a),
  ...createModelSlice(...a),
  ...createAudioSlice(...a),
  ...createAppSlice(...a),
})); 