import React from 'react';
import { useStore } from '../store';
interface RealtimeSchedulePanelProps {
  isVisible: boolean;
  onClose: () => void;
}

/**
 * 即時對話排程控制面板
 * 提供排程設定、狀態顯示和手動控制功能
 */
export function RealtimeSchedulePanel({ isVisible, onClose }: RealtimeSchedulePanelProps) {
  // 如果不可見，不渲染任何內容
  if (!isVisible) return null;
  // 從 store 獲取狀態和操作
  const scheduleEnabled = useStore(state => state.scheduleEnabled);
  const onlineDurationSeconds = useStore(state => state.onlineDurationSeconds);
  const offlineDurationSeconds = useStore(state => state.offlineDurationSeconds);
  const isManualMode = useStore(state => state.isManualMode);
  const currentCountdown = useStore(state => state.currentCountdown);
  const nextAction = useStore(state => state.nextAction);
  const realtimeCurrentlyActive = useStore(state => state.realtimeCurrentlyActive);
  
  // 操作方法
  const setScheduleEnabled = useStore(state => state.setScheduleEnabled);
  const setOnlineDuration = useStore(state => state.setOnlineDuration);
  const setOfflineDuration = useStore(state => state.setOfflineDuration);
  const enableManualMode = useStore(state => state.enableManualMode);
  const disableManualMode = useStore(state => state.disableManualMode);
  const resetSchedule = useStore(state => state.resetSchedule);
  
  // 手動控制方法 - 直接調用 API 而不是透過 hook
  const manualStart = async () => {
    try {
      const response = await fetch('/api/control/realtime-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'start' }),
      });
      if (response.ok) {
        useStore.getState().setRealtimeActive(true);
      }
    } catch (error) {
      console.error('Manual start failed:', error);
    }
  };

  const manualStop = async () => {
    try {
      const response = await fetch('/api/control/realtime-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'stop' }),
      });
      if (response.ok) {
        useStore.getState().setRealtimeActive(false);
      }
    } catch (error) {
      console.error('Manual stop failed:', error);
    }
  };

  // 格式化時間顯示
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 處理持續時間變更
  const handleOnlineDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value) || 0;
    setOnlineDuration(Math.max(10, Math.min(3600, value))); // 限制在 10秒 到 1小時
  };

  const handleOfflineDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value) || 0;
    setOfflineDuration(Math.max(10, Math.min(3600, value))); // 限制在 10秒 到 1小時
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">即時對話排程控制</h3>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className={`w-3 h-3 rounded-full ${scheduleEnabled ? 'bg-green-500' : 'bg-gray-500'}`}></span>
            <span className="text-sm text-gray-300">
              {scheduleEnabled ? '運行中' : '已停止'}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* 當前狀態顯示 */}
      <div className="bg-gray-700 rounded-lg p-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">當前狀態：</span>
            <span className={`ml-2 font-medium ${
              realtimeCurrentlyActive ? 'text-green-400' : 'text-red-400'
            }`}>
              {realtimeCurrentlyActive ? '🟢 進行中' : '🔴 已關閉'}
            </span>
          </div>
          <div>
            <span className="text-gray-400">下次動作：</span>
            <span className="ml-2 font-medium text-yellow-400">
              {nextAction === 'start' ? '開啟' : '關閉'}
            </span>
          </div>
          <div className="col-span-2">
            <span className="text-gray-400">倒數時間：</span>
            <span className="ml-2 font-mono text-xl text-blue-400">
              {formatTime(currentCountdown)}
            </span>
          </div>
        </div>
      </div>

      {/* 排程開關 */}
      <div className="flex items-center justify-between">
        <label className="text-white font-medium">啟用自動排程</label>
        <button
          onClick={() => setScheduleEnabled(!scheduleEnabled)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            scheduleEnabled ? 'bg-green-600' : 'bg-gray-600'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              scheduleEnabled ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      {/* 時間設定 */}
      <div className="space-y-4">
        <h4 className="text-white font-medium">時間設定</h4>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">開啟持續時間（秒）</label>
            <input
              type="number"
              min="10"
              max="3600"
              value={onlineDurationSeconds}
              onChange={handleOnlineDurationChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-xs text-gray-500 mt-1 block">
              ({formatTime(onlineDurationSeconds)})
            </span>
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-2">關閉持續時間（秒）</label>
            <input
              type="number"
              min="10"
              max="3600"
              value={offlineDurationSeconds}
              onChange={handleOfflineDurationChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-xs text-gray-500 mt-1 block">
              ({formatTime(offlineDurationSeconds)})
            </span>
          </div>
        </div>
      </div>

      {/* 手動控制 */}
      <div className="space-y-3">
        <h4 className="text-white font-medium">手動控制</h4>
        
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-400">手動模式（暫停自動排程）</label>
          <button
            onClick={() => isManualMode ? disableManualMode() : enableManualMode()}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              isManualMode ? 'bg-yellow-600' : 'bg-gray-600'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                isManualMode ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={manualStart}
            disabled={realtimeCurrentlyActive}
            className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
              realtimeCurrentlyActive
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            手動開啟
          </button>
          
          <button
            onClick={manualStop}
            disabled={!realtimeCurrentlyActive}
            className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
              !realtimeCurrentlyActive
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700 text-white'
            }`}
          >
            手動關閉
          </button>
        </div>
      </div>

      {/* 重置按鈕 */}
      <div className="border-t border-gray-600 pt-4">
        <button
          onClick={resetSchedule}
          className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors"
        >
          重置排程
        </button>
      </div>
    </div>
  );
}
