import React from 'react';
import { useStore } from '../store';

/**
 * 即時對話狀態指示器
 * 在主界面顯示當前狀態和倒數時間
 */
export function RealtimeStatusIndicator() {
  const realtimeCurrentlyActive = useStore(state => state.realtimeCurrentlyActive);
  const scheduleEnabled = useStore(state => state.scheduleEnabled);
  const currentCountdown = useStore(state => state.currentCountdown);
  const nextAction = useStore(state => state.nextAction);
  const isManualMode = useStore(state => state.isManualMode);

  // 格式化時間顯示
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 獲取狀態描述
  const getStatusText = () => {
    if (isManualMode) {
      return realtimeCurrentlyActive ? '手動模式 - 進行中' : '手動模式 - 已關閉';
    }
    
    if (!scheduleEnabled) {
      return realtimeCurrentlyActive ? '排程已停用 - 進行中' : '排程已停用 - 已關閉';
    }
    
    if (realtimeCurrentlyActive) {
      return `進行中 - ${formatTime(currentCountdown)}後關閉`;
    } else {
      return `已關閉 - ${formatTime(currentCountdown)}後開啟`;
    }
  };

  // 獲取指示器顏色
  const getIndicatorColor = () => {
    if (isManualMode) {
      return realtimeCurrentlyActive ? 'bg-yellow-500' : 'bg-yellow-600';
    }
    
    if (!scheduleEnabled) {
      return 'bg-gray-500';
    }
    
    return realtimeCurrentlyActive ? 'bg-green-500' : 'bg-red-500';
  };

  // 獲取背景顏色
  const getBackgroundColor = () => {
    if (isManualMode) {
      return 'bg-yellow-50 border-yellow-200';
    }
    
    if (!scheduleEnabled) {
      return 'bg-gray-50 border-gray-200';
    }
    
    return realtimeCurrentlyActive 
      ? 'bg-green-50 border-green-200' 
      : 'bg-red-50 border-red-200';
  };

  // 獲取文字顏色
  const getTextColor = () => {
    if (isManualMode) {
      return 'text-yellow-800';
    }
    
    if (!scheduleEnabled) {
      return 'text-gray-800';
    }
    
    return realtimeCurrentlyActive ? 'text-green-800' : 'text-red-800';
  };

  return (
    <div className={`inline-flex items-center px-4 py-2 rounded-lg border ${getBackgroundColor()}`}>
      {/* 狀態指示燈 */}
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${getIndicatorColor()}`}></div>
        <span className={`font-medium ${getTextColor()}`}>即時對話</span>
      </div>
      
      {/* 分隔線 */}
      <div className="mx-3 h-4 w-px bg-gray-300"></div>
      
      {/* 狀態文字 */}
      <span className={`text-sm ${getTextColor()}`}>
        {getStatusText()}
      </span>
      
      {/* 排程狀態標籤 */}
      {isManualMode && (
        <span className="ml-2 px-2 py-1 text-xs font-medium bg-yellow-200 text-yellow-800 rounded">
          手動
        </span>
      )}
      
      {!scheduleEnabled && !isManualMode && (
        <span className="ml-2 px-2 py-1 text-xs font-medium bg-gray-200 text-gray-800 rounded">
          停用
        </span>
      )}
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
