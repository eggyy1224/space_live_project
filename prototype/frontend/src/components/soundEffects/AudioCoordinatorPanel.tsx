import React, { useState, useEffect, useRef } from 'react';
import { useAudioCoordinator } from '../../services/AudioCoordinator';
import { 
  AudioEvent, 
  AudioTimeline, 
  AudioTimelineEvent, 
  AudioCoordinatorEventType,
  IAudioCoordinator
} from '../../services/AudioCoordinator';
import AudioCoordinator from '../../services/AudioCoordinator';
import logger, { LogCategory } from '../../utils/LogManager';

// 時間軸項目顯示元件
const TimelineItem: React.FC<{
  event: AudioTimelineEvent;
  duration: number;
  onRemove: () => void;
}> = ({ event, duration, onRemove }) => {
  const startPercent = (event.startTime / duration) * 100;
  const widthPercent = ((event.duration || 2) / duration) * 100;
  
  const getColorByType = (kind: string) => {
    switch (kind) {
      case 'voice': return 'bg-blue-500';
      case 'song': return 'bg-green-500';
      case 'sfx': return 'bg-yellow-500';
      case 'synth': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };
  
  return (
    <div 
      className={`absolute h-8 rounded-md flex items-center justify-between px-2 text-xs text-white ${getColorByType(event.kind)}`}
      style={{ 
        left: `${startPercent}%`, 
        width: `${widthPercent}%`,
        minWidth: '60px'
      }}
    >
      <span className="truncate">{event.id}</span>
      <button 
        onClick={onRemove}
        className="ml-1 hover:text-red-300"
      >
        ✕
      </button>
    </div>
  );
};

// 音效素材列表元件
const SoundLibrary: React.FC<{
  onSelectSound: (sound: { id: string, url: string, kind: string }) => void;
}> = ({ onSelectSound }) => {
  // 這是簡單的示範數據，實際應用中可能從API獲取或從其他地方傳入
  const sampleSounds = [
    { id: 'bgm_happy', name: '愉快背景音樂', url: '/audio/bgm/happy.mp3', kind: 'song' },
    { id: 'bgm_peaceful', name: '平靜背景音樂', url: '/audio/bgm/peaceful.mp3', kind: 'song' },
    { id: 'sfx_applause', name: '掌聲', url: '/audio/sfx/applause.mp3', kind: 'sfx' },
    { id: 'sfx_bell', name: '鈴聲', url: '/audio/sfx/bell.mp3', kind: 'sfx' },
    { id: 'voice_hello', name: '問候語音', url: '/audio/voice/hello.mp3', kind: 'voice' },
    { id: 'voice_bye', name: '道別語音', url: '/audio/voice/bye.mp3', kind: 'voice' },
  ];
  
  return (
    <div className="bg-gray-800 p-3 rounded-md">
      <h3 className="text-sm font-medium mb-2 text-gray-200">素材庫</h3>
      <div className="grid grid-cols-2 gap-2">
        {sampleSounds.map(sound => (
          <div 
            key={sound.id}
            className="bg-gray-700 p-2 rounded-md cursor-pointer hover:bg-gray-600 transition-colors"
            onClick={() => onSelectSound(sound)}
          >
            <div className="text-xs font-medium truncate">{sound.name}</div>
            <div className="text-xs text-gray-400">{sound.kind}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

// 主要協調器面板元件
const AudioCoordinatorPanel: React.FC = () => {
  // 使用 Zustand store 獲取方法
  const audioCoordinatorStore = useAudioCoordinator();
  
  // 獲取 AudioCoordinator 類實例，用於時間軸相關功能
  const coordinator = useRef<IAudioCoordinator | null>(null);
  
  // 初始化 AudioCoordinator 實例
  useEffect(() => {
    try {
      // @ts-ignore - 我們知道 getInstance 存在但 TypeScript 可能無法識別
      coordinator.current = AudioCoordinator.getInstance();
    } catch (err) {
      logger.error('[AudioCoordinatorPanel] 無法初始化 AudioCoordinator', LogCategory.AUDIO, err);
      // 建立備用模擬實現
      coordinator.current = {
        playNow: () => {},
        stop: () => {},
        scheduleFromJson: () => {},
        stopTimeline: () => {},
        setGlobalVolume: () => {},
        addEventListener: () => () => {},
        removeEventListener: () => {},
      };
    }
  }, []);
  
  const [timelineEvents, setTimelineEvents] = useState<AudioTimelineEvent[]>([]);
  const [totalDuration, setTotalDuration] = useState(30); // 預設時間軸總長度為30秒
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedEventIndex, setSelectedEventIndex] = useState<number | null>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const playbackIntervalRef = useRef<number | null>(null);
  
  // 處理添加事件到時間軸
  const handleAddToTimeline = (sound: { id: string, url: string, kind: string }) => {
    // 如果點擊了時間軸上的位置，就將新事件放在該位置
    const newEvent: AudioTimelineEvent = {
      id: `${sound.kind}_${sound.id}_${Date.now()}`,
      kind: sound.kind as any, // 類型轉換
      url: sound.url,
      track: sound.kind === 'voice' ? 'voice' : 'sfx',
      startTime: selectedEventIndex !== null 
        ? timelineEvents[selectedEventIndex].startTime 
        : Math.min(currentTime, totalDuration - 5),
      duration: 3, // 預設持續時間
    };
    
    setTimelineEvents([...timelineEvents, newEvent]);
    logger.debug(`[AudioCoordinatorPanel] Added ${sound.kind} to timeline at ${newEvent.startTime}s`, LogCategory.AUDIO);
  };
  
  // 處理從時間軸移除事件
  const handleRemoveFromTimeline = (index: number) => {
    const updatedEvents = [...timelineEvents];
    updatedEvents.splice(index, 1);
    setTimelineEvents(updatedEvents);
    
    if (selectedEventIndex === index) {
      setSelectedEventIndex(null);
    } else if (selectedEventIndex !== null && selectedEventIndex > index) {
      setSelectedEventIndex(selectedEventIndex - 1);
    }
  };
  
  // 處理清空時間軸
  const handleClearTimeline = () => {
    setTimelineEvents([]);
    setSelectedEventIndex(null);
    logger.debug('[AudioCoordinatorPanel] Timeline cleared', LogCategory.AUDIO);
  };
  
  // 處理播放時間軸
  const handlePlayTimeline = () => {
    if (timelineEvents.length === 0 || !coordinator.current) {
      logger.debug('[AudioCoordinatorPanel] Cannot play empty timeline', LogCategory.AUDIO);
      return;
    }
    
    // 構建時間軸對象
    const timeline: AudioTimeline = {
      timeline: [...timelineEvents].sort((a, b) => a.startTime - b.startTime)
    };
    
    // 使用 AudioCoordinator 播放時間軸
    coordinator.current.scheduleFromJson(timeline);
    setIsPlaying(true);
    setCurrentTime(0);
    
    // 啟動播放進度更新
    if (playbackIntervalRef.current) {
      clearInterval(playbackIntervalRef.current);
    }
    
    const startTime = Date.now();
    playbackIntervalRef.current = window.setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      setCurrentTime(elapsed);
      
      // 檢查是否播放完成
      const lastEvent = timelineEvents[timelineEvents.length - 1];
      const endTime = lastEvent.startTime + (lastEvent.duration || 0);
      
      if (elapsed >= endTime) {
        handleStopTimeline();
      }
    }, 100);
    
    logger.debug('[AudioCoordinatorPanel] Started playing timeline', LogCategory.AUDIO);
  };
  
  // 處理停止時間軸播放
  const handleStopTimeline = () => {
    if (playbackIntervalRef.current) {
      clearInterval(playbackIntervalRef.current);
      playbackIntervalRef.current = null;
    }
    
    if (coordinator.current) {
      coordinator.current.stopTimeline();
    }
    
    setIsPlaying(false);
    setCurrentTime(0);
    logger.debug('[AudioCoordinatorPanel] Stopped playing timeline', LogCategory.AUDIO);
  };
  
  // 處理時間軸點擊，設置當前時間和選中的事件
  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current || isPlaying) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const clickPosition = e.clientX - rect.left;
    const clickPercent = clickPosition / rect.width;
    const clickTime = clickPercent * totalDuration;
    
    setCurrentTime(clickTime);
    
    // 尋找點擊位置是否有事件
    const clickedEventIndex = timelineEvents.findIndex(event => {
      const eventStart = event.startTime;
      const eventEnd = eventStart + (event.duration || 0);
      return clickTime >= eventStart && clickTime <= eventEnd;
    });
    
    setSelectedEventIndex(clickedEventIndex >= 0 ? clickedEventIndex : null);
  };
  
  // 處理修改選中事件的屬性
  const handleEditEvent = (property: keyof AudioTimelineEvent, value: any) => {
    if (selectedEventIndex === null) return;
    
    const updatedEvents = [...timelineEvents];
    updatedEvents[selectedEventIndex] = {
      ...updatedEvents[selectedEventIndex],
      [property]: value
    };
    
    setTimelineEvents(updatedEvents);
  };
  
  // 清理播放計時器
  useEffect(() => {
    return () => {
      if (playbackIntervalRef.current) {
        clearInterval(playbackIntervalRef.current);
      }
      
      if (coordinator.current) {
        coordinator.current.stopTimeline();
      }
    };
  }, []);
  
  // 註冊事件監聽器
  useEffect(() => {
    if (!coordinator.current) return;
    
    const handleTimelineEnd = () => {
      handleStopTimeline();
    };

    const removeTimelineEndListener = coordinator.current.addEventListener('timeline_end', handleTimelineEnd);
    
    return () => {
      removeTimelineEndListener();
    };
  }, [coordinator.current]);
  
  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">音頻協調控制中心</h2>
      
      {/* 控制按鈕 */}
      <div className="flex mb-4 space-x-2">
        <button
          onClick={isPlaying ? handleStopTimeline : handlePlayTimeline}
          className={`px-4 py-2 rounded-md ${
            isPlaying ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
          } transition-colors`}
          disabled={timelineEvents.length === 0}
        >
          {isPlaying ? '停止' : '播放'}
        </button>
        <button
          onClick={handleClearTimeline}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md transition-colors"
          disabled={timelineEvents.length === 0 || isPlaying}
        >
          清空時間軸
        </button>
        <div className="ml-auto">
          <label className="text-sm mr-2">總時長:</label>
          <input
            type="number"
            value={totalDuration}
            onChange={e => setTotalDuration(Math.max(5, parseInt(e.target.value) || 5))}
            className="w-16 px-2 py-1 bg-gray-800 border border-gray-700 rounded-md text-sm"
            min="5"
            max="300"
            disabled={isPlaying || timelineEvents.length > 0}
          />
          <span className="ml-1 text-sm">秒</span>
        </div>
      </div>
      
      {/* 時間軸 */}
      <div className="mb-4">
        <div className="text-sm mb-1 flex justify-between">
          <span>時間軸</span>
          <span>當前: {currentTime.toFixed(1)}s / {totalDuration}s</span>
        </div>
        <div 
          ref={timelineRef}
          className="h-20 bg-gray-800 border border-gray-700 rounded-md relative"
          onClick={handleTimelineClick}
        >
          {/* 時間標記 */}
          {Array.from({ length: Math.floor(totalDuration / 5) + 1 }).map((_, i) => (
            <div 
              key={i} 
              className="absolute bottom-0 border-l border-gray-600 h-full" 
              style={{ left: `${(i * 5 / totalDuration) * 100}%` }}
            >
              <span className="absolute bottom-0 text-xs text-gray-400 -ml-2">
                {i * 5}s
              </span>
            </div>
          ))}
          
          {/* 播放線 */}
          {isPlaying && (
            <div 
              className="absolute top-0 h-full w-px bg-red-500 z-10"
              style={{ left: `${(currentTime / totalDuration) * 100}%` }}
            />
          )}
          
          {/* 時間軸事件 */}
          {timelineEvents.map((event, index) => (
            <TimelineItem 
              key={event.id}
              event={event}
              duration={totalDuration}
              onRemove={() => handleRemoveFromTimeline(index)}
            />
          ))}
        </div>
      </div>
      
      {/* 事件編輯區域 */}
      {selectedEventIndex !== null && (
        <div className="mb-4 p-3 border border-gray-700 rounded-md bg-gray-800">
          <h3 className="text-sm font-medium mb-2">編輯事件</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs block mb-1">開始時間 (秒)</label>
              <input
                type="number"
                value={timelineEvents[selectedEventIndex].startTime}
                onChange={e => handleEditEvent('startTime', parseFloat(e.target.value) || 0)}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded-md text-sm"
                min="0"
                max={totalDuration - (timelineEvents[selectedEventIndex].duration || 0)}
                step="0.1"
                disabled={isPlaying}
              />
            </div>
            <div>
              <label className="text-xs block mb-1">持續時間 (秒)</label>
              <input
                type="number"
                value={timelineEvents[selectedEventIndex].duration || 0}
                onChange={e => handleEditEvent('duration', parseFloat(e.target.value) || 0)}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded-md text-sm"
                min="0.1"
                max={totalDuration - timelineEvents[selectedEventIndex].startTime}
                step="0.1"
                disabled={isPlaying}
              />
            </div>
            <div>
              <label className="text-xs block mb-1">音量 (0-1)</label>
              <input
                type="number"
                value={timelineEvents[selectedEventIndex].volume || 1}
                onChange={e => handleEditEvent('volume', parseFloat(e.target.value) || 0)}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded-md text-sm"
                min="0"
                max="1"
                step="0.1"
                disabled={isPlaying}
              />
            </div>
            <div>
              <label className="text-xs block mb-1">循環播放</label>
              <input
                type="checkbox"
                checked={timelineEvents[selectedEventIndex].loop || false}
                onChange={e => handleEditEvent('loop', e.target.checked)}
                className="h-6 w-6"
                disabled={isPlaying}
              />
            </div>
          </div>
        </div>
      )}
      
      {/* 素材庫 */}
      <SoundLibrary onSelectSound={handleAddToTimeline} />
    </div>
  );
};

export default AudioCoordinatorPanel; 