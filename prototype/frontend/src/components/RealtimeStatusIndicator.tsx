import React, { useMemo, useCallback } from 'react';
import { useStore } from '../store';

/**
 * 終端機風格的即時對話狀態指示器
 * 顯示在左上角，排程面板收起來時顯示
 */
export function RealtimeStatusIndicator() {
  // 不需要在這裡調用 useRealtimeScheduler，App.tsx 中已經調用了

  const realtimeCurrentlyActive = useStore(state => state.realtimeCurrentlyActive);
  const scheduleEnabled = useStore(state => state.scheduleEnabled);
  const currentCountdown = useStore(state => state.currentCountdown);
  const nextAction = useStore(state => state.nextAction);
  const isManualMode = useStore(state => state.isManualMode);

  // 格式化時間顯示 (MM:SS) - 使用 useCallback 優化
  const formatTime = useCallback((seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }, []);

  // 使用 useMemo 優化，避免每次渲染都重新計算
  const terminal = useMemo(() => {
    const isOnline = realtimeCurrentlyActive;
    const timeLeft = formatTime(currentCountdown);
    
    if (isManualMode) {
      return {
        status: isOnline ? 'ONLINE' : 'OFFLINE',
        message: isOnline ? 'MANUAL MODE ACTIVE' : 'MANUAL MODE INACTIVE',
        color: isOnline ? 'text-yellow-400' : 'text-yellow-600',
        bgColor: 'bg-gray-900',
        borderColor: 'border-yellow-500',
        time: '--:--'
      };
    }

    if (!scheduleEnabled) {
      return {
        status: 'DISABLED',
        message: 'SCHEDULE INACTIVE',
        color: 'text-gray-400',
        bgColor: 'bg-gray-900',
        borderColor: 'border-gray-500',
        time: '--:--'
      };
    }

    return {
      status: isOnline ? 'ONLINE' : 'OFFLINE',
      message: isOnline ? `SHUTDOWN IN ${timeLeft}` : `STARTUP IN ${timeLeft}`,
      color: isOnline ? 'text-green-400' : 'text-red-400',
      bgColor: 'bg-gray-900',
      borderColor: isOnline ? 'border-green-500' : 'border-red-500',
      time: timeLeft
    };
  }, [realtimeCurrentlyActive, currentCountdown, isManualMode, scheduleEnabled]);
  const isOnline = realtimeCurrentlyActive;

  return (
    <div className={`font-mono text-sm select-none ${terminal.bgColor} ${terminal.borderColor} border-2 rounded-md shadow-lg backdrop-blur-sm bg-opacity-95 min-w-[280px]`}>
      {/* Terminal Header */}
      <div className="px-3 py-1 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <span className="text-gray-400 text-xs">realtime-status</span>
        </div>
        <span className="text-gray-500 text-xs">●</span>
      </div>

      {/* Terminal Content */}
      <div className="px-3 py-2 space-y-1">
        {/* Status Line */}
        <div className="flex items-center space-x-2">
          <span className="text-gray-500">$</span>
          <span className="text-gray-300">status</span>
          <span className={`font-bold ${terminal.color}`}>
            {terminal.status}
          </span>
          {(isOnline || (!isManualMode && scheduleEnabled)) && (
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
          )}
        </div>

        {/* Timer Line */}
        {!isManualMode && scheduleEnabled && (
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">$</span>
            <span className="text-gray-300">timer</span>
            <span className={`font-bold tabular-nums ${terminal.color}`}>
              {terminal.time}
            </span>
          </div>
        )}

        {/* Message Line */}
        <div className="flex items-center space-x-2">
          <span className="text-gray-500">&gt;</span>
          <span className={`text-xs ${terminal.color}`}>
            {terminal.message}
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * 簡化版狀態指示器（用於頂部狀態欄）
 */
export function RealtimeStatusBadge() {
  const realtimeCurrentlyActive = useStore(state => state.realtimeCurrentlyActive);
  const scheduleEnabled = useStore(state => state.scheduleEnabled);
  const isManualMode = useStore(state => state.isManualMode);

  const getStatus = () => {
    if (isManualMode) {
      return { 
        color: 'bg-yellow-500', 
        text: '手動', 
        icon: '🟡' 
      };
    }
    
    if (!scheduleEnabled) {
      return { 
        color: 'bg-gray-500', 
        text: '停用', 
        icon: '⚫' 
      };
    }
    
    return realtimeCurrentlyActive 
      ? { color: 'bg-green-500', text: '進行', icon: '🟢' }
      : { color: 'bg-red-500', text: '關閉', icon: '🔴' };
  };

  const status = getStatus();

  return (
    <div className="inline-flex items-center space-x-1">
      <span className="text-sm">{status.icon}</span>
      <span className="text-xs font-medium text-gray-700">{status.text}</span>
    </div>
  );
}
