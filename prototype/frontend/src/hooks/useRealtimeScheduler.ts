import { useEffect, useRef } from 'react';
import { useStore } from '../store';
import { useRealtimeVoice } from '../services/RealtimeVoiceService';

/**
 * 即時對話排程器 Hook
 * 負責管理自動計時器，並在時間到時呼叫後端 API
 */
export function useRealtimeScheduler() {
  const timerRef = useRef<number | null>(null);
  const lastUpdateRef = useRef<number>(Date.now());
  
  // 從 store 獲取排程狀態
  const scheduleEnabled = useStore(state => state.scheduleEnabled);
  const isManualMode = useStore(state => state.isManualMode);
  const currentCountdown = useStore(state => state.currentCountdown);
  const nextAction = useStore(state => state.nextAction);
  const realtimeCurrentlyActive = useStore(state => state.realtimeCurrentlyActive);
  
  // 從 store 獲取更新方法
  const _updateCountdown = useStore(state => state._updateCountdown);
  const setRealtimeActive = useStore(state => state.setRealtimeActive);
  
  // 實時語音控制
  const { 
    start: startRealtimeVoice, 
    stop: stopRealtimeVoice,
    streaming: realtimeStreaming 
  } = useRealtimeVoice();

  // 執行實際的動作（呼叫後端 API）
  const executeRealtimeAction = async (action: 'start' | 'stop') => {
    console.log(`[RealtimeScheduler] Executing ${action} action`);
    
    try {
      // 呼叫後端 API 控制即時語音
      const response = await fetch('/api/control/realtime-voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }

      const result = await response.json();
      console.log(`[RealtimeScheduler] API response:`, result);
      
      // 更新本地狀態
      setRealtimeActive(action === 'start');
      
    } catch (error) {
      console.error(`[RealtimeScheduler] Failed to ${action} realtime voice:`, error);
      
      // 如果 API 失敗，嘗試直接呼叫本地方法作為備用
      if (action === 'start') {
        startRealtimeVoice();
        setRealtimeActive(true);
      } else {
        stopRealtimeVoice();
        setRealtimeActive(false);
      }
    }
  };

  // 主計時器邏輯
  useEffect(() => {
    // 先清除現有計時器，避免重複
    if (timerRef.current) {
      console.log('[RealtimeScheduler] Clearing existing timer');
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // 如果排程被停用或處於手動模式，不啟動計時器
    if (!scheduleEnabled || isManualMode) {
      console.log('[RealtimeScheduler] Timer disabled - scheduleEnabled:', scheduleEnabled, 'isManualMode:', isManualMode);
      return;
    }

    // 啟動計時器 - 簡化版本，直接每秒更新
    console.log('[RealtimeScheduler] Starting timer, scheduleEnabled:', scheduleEnabled);
    timerRef.current = setInterval(() => {
      _updateCountdown();
      lastUpdateRef.current = Date.now();
    }, 1000);

    // 清理函數
    return () => {
      console.log('[RealtimeScheduler] Cleanup: clearing timer');
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [scheduleEnabled, isManualMode]); // 移除 _updateCountdown 依賴，避免重複觸發

  // 監聽倒數完成，執行對應動作
  useEffect(() => {
    if (scheduleEnabled && !isManualMode && currentCountdown === 0) {
      executeRealtimeAction(nextAction);
    }
  }, [currentCountdown, nextAction, scheduleEnabled, isManualMode]);

  // 同步本地語音狀態與排程狀態
  useEffect(() => {
    // 當本地語音狀態與排程狀態不一致時，更新排程狀態
    if (realtimeStreaming !== realtimeCurrentlyActive) {
      console.log(`[RealtimeScheduler] Syncing state: streaming=${realtimeStreaming}, scheduled=${realtimeCurrentlyActive}`);
      setRealtimeActive(realtimeStreaming);
    }
  }, [realtimeStreaming, realtimeCurrentlyActive, setRealtimeActive]);

  // 提供手動控制方法
  const manualStart = async () => {
    await executeRealtimeAction('start');
  };

  const manualStop = async () => {
    await executeRealtimeAction('stop');
  };

  // 返回狀態和控制方法
  return {
    // 狀態
    scheduleEnabled,
    isManualMode,
    currentCountdown,
    nextAction,
    realtimeCurrentlyActive,
    
    // 手動控制
    manualStart,
    manualStop,
    
    // 計時器狀態
    isRunning: !!timerRef.current,
  };
}
