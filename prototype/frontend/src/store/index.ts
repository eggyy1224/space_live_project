import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import { WebSocketSlice, createWebSocketSlice } from './slices/webSocketSlice';
import { ChatSlice, createChatSlice } from './slices/chatSlice';
import { ModelSlice, createModelSlice } from './slices/modelSlice';
import { AppSlice, createAppSlice } from './slices/appSlice';
import { MediaSlice, createMediaSlice } from './slices/mediaSlice';

// 合併所有 slice 類型為最終 Store 類型
export type Store = WebSocketSlice & ChatSlice & ModelSlice & AppSlice & MediaSlice;

// 創建 Zustand Store
export const useStore = create<Store>()(
  devtools(
    (set, get, api) => ({
      ...createWebSocketSlice(set, get, api),
      ...createChatSlice(set, get, api),
      ...createModelSlice(set, get, api),
      ...createAppSlice(set, get, api),
      ...createMediaSlice(set, get, api),
    }),
    { name: 'AppStore' } // Optional: Name for Redux DevTools
  )
); 