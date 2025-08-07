import { StateCreator } from 'zustand';

// 排程狀態與操作定義
export interface RealtimeScheduleSlice {
  // === 排程配置 ===
  scheduleEnabled: boolean;           // 是否啟用自動排程
  onlineDurationSeconds: number;      // 開啟持續時間（秒）
  offlineDurationSeconds: number;     // 關閉持續時間（秒）
  
  // === 計時器狀態 ===
  currentCountdown: number;           // 當前倒數計時（秒）
  nextAction: 'start' | 'stop';       // 下次要執行的動作
  isManualMode: boolean;              // 是否為手動模式（暫停自動排程）
  lastActionTime: number | null;      // 上次執行動作的時間戳
  
  // === 即時狀態 ===
  realtimeCurrentlyActive: boolean;   // 即時對話當前是否開啟
  
  // === 基本操作 ===
  setScheduleEnabled: (enabled: boolean) => void;
  setOnlineDuration: (seconds: number) => void;
  setOfflineDuration: (seconds: number) => void;
  setRealtimeActive: (active: boolean) => void;
  
  // === 計時器控制 ===
  startSchedule: () => void;
  pauseSchedule: () => void;
  resumeSchedule: () => void;
  resetSchedule: () => void;
  
  // === 手動控制 ===
  enableManualMode: () => void;
  disableManualMode: () => void;
  
  // === 內部更新（由計時器呼叫）===
  _updateCountdown: () => void;
  _executeNextAction: () => void;
  _resetToNextCycle: () => void;
}

// 預設配置
const DEFAULT_ONLINE_DURATION = 300;   // 5分鐘
const DEFAULT_OFFLINE_DURATION = 600;  // 10分鐘

// 創建 RealtimeSchedule Slice
export const createRealtimeScheduleSlice: StateCreator<RealtimeScheduleSlice> = (set, get) => ({
  // === 初始狀態 ===
  scheduleEnabled: false,
  onlineDurationSeconds: DEFAULT_ONLINE_DURATION,
  offlineDurationSeconds: DEFAULT_OFFLINE_DURATION,
  
  currentCountdown: DEFAULT_OFFLINE_DURATION,
  nextAction: 'start',
  isManualMode: false,
  lastActionTime: null,
  
  realtimeCurrentlyActive: false,
  
  // === 基本操作實現 ===
  setScheduleEnabled: (enabled) => {
    set({ scheduleEnabled: enabled });
    if (enabled) {
      get().startSchedule();
    }
  },
  
  setOnlineDuration: (seconds) => {
    set({ onlineDurationSeconds: Math.max(10, seconds) }); // 最少10秒
    // 如果當前是等待開啟狀態，更新倒數時間
    const state = get();
    if (!state.realtimeCurrentlyActive && state.nextAction === 'start') {
      set({ currentCountdown: seconds });
    }
  },
  
  setOfflineDuration: (seconds) => {
    set({ offlineDurationSeconds: Math.max(10, seconds) }); // 最少10秒
    // 如果當前是等待關閉狀態，更新倒數時間
    const state = get();
    if (state.realtimeCurrentlyActive && state.nextAction === 'stop') {
      set({ currentCountdown: seconds });
    }
  },
  
  setRealtimeActive: (active) => {
    set({ realtimeCurrentlyActive: active });
    // 根據新狀態設定下次動作和倒數時間
    const state = get();
    if (active) {
      // 剛開啟，下次要關閉
      set({ 
        nextAction: 'stop',
        currentCountdown: state.onlineDurationSeconds,
        lastActionTime: Date.now()
      });
    } else {
      // 剛關閉，下次要開啟
      set({ 
        nextAction: 'start',
        currentCountdown: state.offlineDurationSeconds,
        lastActionTime: Date.now()
      });
    }
  },
  
  // === 計時器控制實現 ===
  startSchedule: () => {
    const state = get();
    
    // 根據當前狀態設定初始倒數
    if (state.realtimeCurrentlyActive) {
      set({ 
        scheduleEnabled: true,
        isManualMode: false,
        nextAction: 'stop',
        currentCountdown: state.onlineDurationSeconds,
        lastActionTime: Date.now()
      });
    } else {
      set({ 
        scheduleEnabled: true,
        isManualMode: false,
        nextAction: 'start',
        currentCountdown: state.offlineDurationSeconds,
        lastActionTime: Date.now()
      });
    }
    
    console.log('[RealtimeSchedule] Started schedule with countdown:', get().currentCountdown);
  },
  
  pauseSchedule: () => {
    set({ scheduleEnabled: false });
  },
  
  resumeSchedule: () => {
    set({ scheduleEnabled: true, isManualMode: false });
  },
  
  resetSchedule: () => {
    const state = get();
    set({
      currentCountdown: state.realtimeCurrentlyActive ? 
        state.onlineDurationSeconds : 
        state.offlineDurationSeconds,
      nextAction: state.realtimeCurrentlyActive ? 'stop' : 'start',
      lastActionTime: Date.now(),
      isManualMode: false
    });
  },
  
  // === 手動控制實現 ===
  enableManualMode: () => {
    set({ isManualMode: true, scheduleEnabled: false });
  },
  
  disableManualMode: () => {
    set({ isManualMode: false });
    get().resetSchedule();
  },
  
  // === 內部更新方法（由計時器呼叫）===
  _updateCountdown: () => {
    const state = get();
    
    if (!state.scheduleEnabled || state.isManualMode) {
      return;
    }
    
    const newCountdown = Math.max(0, state.currentCountdown - 1);
    set({ currentCountdown: newCountdown });
    
    // 倒數完成，執行動作
    if (newCountdown === 0) {
      console.log('[RealtimeSchedule] Countdown reached 0, executing next action:', state.nextAction);
      get()._executeNextAction();
    }
  },
  
  _executeNextAction: async () => {
    const state = get();
    const action = state.nextAction;
    console.log(`[RealtimeSchedule] Executing action: ${action}`);
    
    try {
      // 呼叫後端 API
      const response = await fetch('/api/control/realtime-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
      });
      
      const result = await response.json();
      console.log(`[RealtimeSchedule] API response for ${action}:`, result);
      
      if (result.success) {
        // API 成功，更新狀態並進入下個週期
        get()._resetToNextCycle();
      } else {
        console.error(`[RealtimeSchedule] Backend API failed to ${action} realtime voice:`, result.detail || result.message);
      }
    } catch (error) {
      console.error(`[RealtimeSchedule] Failed to call backend API for ${action} realtime voice:`, error);
    }
  },
  
  _resetToNextCycle: () => {
    const state = get();
    const newActive = state.nextAction === 'start';
    
    set({
      realtimeCurrentlyActive: newActive,
      nextAction: newActive ? 'stop' : 'start',
      currentCountdown: newActive ? 
        state.onlineDurationSeconds : 
        state.offlineDurationSeconds,
      lastActionTime: Date.now()
    });
  }
});
