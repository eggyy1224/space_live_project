import React, { useState, useEffect, useRef } from 'react';
import { useAudioCoordinator } from '../../services/AudioCoordinator';
import { 
  AudioTimeline, 
  AudioCoordinatorEventType,
  IAudioCoordinator
} from '../../services/AudioCoordinator';
import AudioCoordinator from '../../services/AudioCoordinator';
import logger, { LogCategory } from '../../utils/LogManager';

// JSON 輸入區域元件
const JsonInputArea: React.FC<{
  onSubmit: (json: AudioTimeline) => void;
}> = ({ onSubmit }) => {
  const [jsonValue, setJsonValue] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  
  // 範例JSON
  const exampleJson = JSON.stringify({
    timeline: [
      {
        id: "voice_hello_1",
        kind: "voice",
        url: "/audio/voice/hello.mp3",
        track: "voice",
        startTime: 0,
        duration: 2
      },
      {
        id: "sfx_bell_1",
        kind: "sfx",
        url: "/audio/sfx/bell.mp3",
        track: "sfx",
        startTime: 3,
        duration: 1
      }
    ]
  }, null, 2);
  
  const handleLoadExample = () => {
    setJsonValue(exampleJson);
    setError(null);
  };
  
  const handleSubmit = () => {
    try {
      const parsed = JSON.parse(jsonValue);
      
      // 簡單驗證
      if (!parsed.timeline || !Array.isArray(parsed.timeline)) {
        throw new Error('JSON 必須包含 timeline 陣列');
      }
      
      // 檢查每個事件是否有必要的字段
      parsed.timeline.forEach((event: any, index: number) => {
        if (!event.id || !event.kind || !event.url || !event.track || 
            event.startTime === undefined) {
          throw new Error(`時間軸事件 #${index + 1} 缺少必要字段`);
        }
      });
      
      setError(null);
      onSubmit(parsed);
      logger.debug('[JsonInputArea] 提交有效的 JSON 時間軸', LogCategory.AUDIO);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '無效的 JSON 格式';
      setError(errorMsg);
      logger.error('[JsonInputArea] JSON 解析錯誤', LogCategory.AUDIO, err);
    }
  };
  
  return (
    <div className="mb-4 p-3 border border-gray-700 rounded-md bg-gray-800">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-sm font-medium">JSON 輸入</h3>
        <button 
          onClick={handleLoadExample}
          className="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded-md"
        >
          載入範例
        </button>
      </div>
      
      <textarea 
        value={jsonValue}
        onChange={(e) => setJsonValue(e.target.value)}
        className="w-full h-48 bg-gray-900 text-gray-200 p-2 rounded-md font-mono text-xs"
        placeholder="在此輸入時間軸 JSON..."
      />
      
      {error && (
        <div className="mt-2 text-xs text-red-400 bg-red-900 bg-opacity-30 p-2 rounded-md">
          錯誤: {error}
        </div>
      )}
      
      <button 
        onClick={handleSubmit}
        className="mt-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-md w-full"
      >
        播放 JSON
      </button>
    </div>
  );
};

// 主要協調器面板元件
const AudioCoordinatorPanel: React.FC = () => {
  // 獲取 AudioCoordinator 類實例
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
  
  // 處理從JSON播放
  const handlePlayFromJson = (jsonTimeline: AudioTimeline) => {
    if (!coordinator.current) return;
    
    // 停止當前播放
    if (coordinator.current) {
      coordinator.current.stopTimeline();
    }
    
    // 使用協調器播放JSON時間軸
    coordinator.current.scheduleFromJson(jsonTimeline);
    logger.debug('[AudioCoordinatorPanel] Started playing from JSON', LogCategory.AUDIO);
  };
  
  // 清理資源
  useEffect(() => {
    return () => {
      if (coordinator.current) {
        coordinator.current.stopTimeline();
      }
    };
  }, []);
  
  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">音頻協調控制中心</h2>
      
      {/* JSON 輸入區域 */}
      <JsonInputArea onSubmit={handlePlayFromJson} />
    </div>
  );
};

export default AudioCoordinatorPanel; 