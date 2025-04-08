import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useStore } from '../store'; // Import Zustand store
import { getPresetsList } from '../services/api'; // Import API function
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import Draggable from 'react-draggable'; // Import Draggable

// --- 子組件: Morph Target 控制條 (Tailwind 樣式) ---
interface MorphTargetBarProps {
  name: string;
  value: number; 
  onChange: (name: string, value: number) => void;
}

const MorphTargetBar: React.FC<MorphTargetBarProps> = React.memo(({ name, value, onChange }) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(name, parseFloat(event.target.value));
  };

  return (
    <div className="flex items-center space-x-2">
      <label htmlFor={`morph-${name}`} className="text-xs text-gray-700 dark:text-gray-300 w-20 truncate" title={name}>{name}</label>
      <input 
        id={`morph-${name}`}
        type="range" 
        min="0" 
        max="1" 
        step="0.01" 
        value={value}
        onChange={handleChange} 
        className="flex-grow h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full appearance-none cursor-pointer accent-blue-500 dark:accent-blue-400"
      />
      <span className="text-xs text-gray-600 dark:text-gray-400 w-8 text-right">{value.toFixed(2)}</span>
    </div>
  );
});
// --- 子組件結束 ---


// --- SettingsPanel Props 定義 ---
interface SettingsPanelProps {
  isVisible: boolean;
  onClose: () => void;
  // Model Control Props (migrated from ControlPanel)
  isModelLoaded: boolean;
  modelScale: number;
  currentAnimation: string | null;
  availableAnimations: string[];
  morphTargetDictionary: Record<string, number> | null;
  selectedMorphTarget: string | null; // This state is now managed in App.tsx
  setSelectedMorphTarget: (name: string | null) => void; // This state is now managed in App.tsx
  updateMorphTargetInfluence: (name: string, value: number) => void;
  resetAllMorphTargets: () => void;
  rotateModel: (direction: 'left' | 'right') => void;
  scaleModel: (factor: number) => void;
  resetModel: () => void;
  toggleBackground: () => void;
  selectAnimation: (animationName: string) => void;
  applyPresetExpression: (expression: string) => Promise<boolean>;
  showSpaceBackground: boolean;
  // Emotion State Props (optional display)
  currentEmotion: string;
  emotionConfidence: number;
  // Debug Control Props (moved from AppUI)
  debugMode: boolean;
  showModelAnalyzer: boolean;
  modelUrl: string; 
  toggleDebugMode: () => void;
  toggleModelAnalyzer: () => void;
  handleModelSwitch: () => void;
}
// --- Props 定義結束 ---


// --- 主 SettingsPanel 組件 --- 
const SettingsPanel: React.FC<SettingsPanelProps> = ({
  isVisible,
  onClose,
  // Model Control Props
  isModelLoaded,
  modelScale,
  currentAnimation,
  availableAnimations,
  morphTargetDictionary,
  // selectedMorphTarget, // No longer needed directly here, managed by App.tsx
  // setSelectedMorphTarget, // No longer needed directly here, managed by App.tsx
  updateMorphTargetInfluence,
  resetAllMorphTargets,
  rotateModel,
  scaleModel,
  resetModel,
  toggleBackground,
  selectAnimation,
  applyPresetExpression,
  showSpaceBackground,
  // Emotion State Props
  currentEmotion,
  emotionConfidence,
  // Debug Control Props
  debugMode,
  showModelAnalyzer,
  modelUrl,
  toggleDebugMode,
  toggleModelAnalyzer,
  handleModelSwitch,
}) => {
  const nodeRef = useRef<HTMLDivElement>(null); // Ref for Draggable
  const morphTargetsFromStore = useStore((state) => state.morphTargets);
  const setLastJsonMessage = useStore((state) => state.setLastJsonMessage); // 取得設置 WebSocket 訊息的函數
  const isSpeaking = useStore((state) => state.isSpeaking); // 取得當前說話狀態
  const setSpeaking = useStore((state) => state.setSpeaking); // 取得設置說話狀態的函數
  const setAudioStartTime = useStore((state) => state.setAudioStartTime); // 取得設置音頻開始時間的函數

  // State for presets
  const [presets, setPresets] = useState<string[]>([]);
  const [loadingPresets, setLoadingPresets] = useState<boolean>(false);

  // Fetch presets on mount
  useEffect(() => {
    if (!isVisible) return; // Only fetch when visible?
    const fetchPresets = async () => {
      setLoadingPresets(true);
      try {
        const response = await getPresetsList();
        if (response && response.presets) {
          setPresets(response.presets);
          logger.info(`[SettingsPanel] Fetched ${response.presets.length} presets`, LogCategory.MODEL);
        }
      } catch (error) {
        logger.error('[SettingsPanel] Failed to fetch presets', LogCategory.MODEL, error);
        setPresets(['happy', 'sad', 'angry', 'surprised', 'reset']); // Fallback
      } finally {
        setLoadingPresets(false);
      }
    };
    fetchPresets();
  }, [isVisible]); // Re-fetch if panel becomes visible again?

  const handlePresetApply = useCallback(async (preset: string) => {
    logger.info(`[SettingsPanel] Applying preset: ${preset}`, LogCategory.MODEL);
    await applyPresetExpression(preset);
  }, [applyPresetExpression]);

  const translatePreset = useCallback((preset: string): string => {
    const translations: Record<string, string> = {
      'happy': '快樂',
      'sad': '悲傷',
      'angry': '生氣',
      'surprised': '驚訝',
      'reset': '重置',
    };
    return translations[preset] || preset;
  }, []);

  const handleMorphTargetChange = useCallback((name: string, value: number) => {
    // logger.info(`[SettingsPanel] Setting MorphTarget: ${name} = ${value}`, LogCategory.MODEL);
    updateMorphTargetInfluence(name, value);
  }, [updateMorphTargetInfluence]);

  const sortedMorphTargetKeys = Object.keys(morphTargetDictionary || {}).sort();

  // 模擬情緒軌跡數據
  const mockEmotionalTrajectories = {
    // 開心 -> 驚訝 -> 開心 (持續15秒)
    happyToSurprisedToHappy: {
      type: 'emotionalTrajectory',
      payload: {
        duration: 15.0, // 15秒長
        keyframes: [
          { tag: 'happy', proportion: 0.0 }, // 開始：開心
          { tag: 'surprised', proportion: 0.5 }, // 中間：驚訝
          { tag: 'happy', proportion: 1.0 }, // 結束：開心
        ]
      }
    },
    
    // 悲傷 -> 生氣 -> 中性 (持續10秒)
    sadToAngryToNeutral: {
      type: 'emotionalTrajectory',
      payload: {
        duration: 10.0, // 10秒長
        keyframes: [
          { tag: 'sad', proportion: 0.0 }, // 開始：悲傷
          { tag: 'angry', proportion: 0.4 }, // 40%處：生氣
          { tag: 'neutral', proportion: 1.0 }, // 結束：中性
        ]
      }
    },
    
    // 中性 -> 快速輪流所有情緒 (持續20秒)
    emotionTour: {
      type: 'emotionalTrajectory',
      payload: {
        duration: 20.0, // 20秒長
        keyframes: [
          { tag: 'neutral', proportion: 0.0 }, // 開始：中性
          { tag: 'happy', proportion: 0.2 }, // 20%處：開心
          { tag: 'sad', proportion: 0.4 }, // 40%處：悲傷
          { tag: 'angry', proportion: 0.6 }, // 60%處：生氣
          { tag: 'surprised', proportion: 0.8 }, // 80%處：驚訝
          { tag: 'neutral', proportion: 1.0 }, // 結束：中性
        ]
      }
    }
  };
  
  // 發送模擬情緒軌跡數據
  const sendMockTrajectory = useCallback((trajectoryKey: keyof typeof mockEmotionalTrajectories) => {
    const trajectory = mockEmotionalTrajectories[trajectoryKey];
    logger.info(`[SettingsPanel] 發送模擬情緒軌跡: ${trajectoryKey}`, LogCategory.ANIMATION);
    
    // 設置 lastJsonMessage，模擬接收 WebSocket 訊息
    setLastJsonMessage(trajectory);
    
    // 移除自動設置說話狀態的邏輯，讓用戶必須明確使用上面的「開始說話」按鈕
    /* 
    if (!isSpeaking) {
      logger.info('[SettingsPanel] 模擬開始說話狀態', LogCategory.ANIMATION);
      setSpeaking(true);
      setAudioStartTime(performance.now()); // 設置時間戳
    }
    */
    
    // 如果尚未開始說話，提醒用戶先點擊「開始說話」按鈕
    if (!isSpeaking) {
      logger.warn('[SettingsPanel] 發送了情緒軌跡，但說話狀態為 false，可能看不到完整效果', LogCategory.ANIMATION);
    }
  }, [setLastJsonMessage, isSpeaking]);
  
  // 切換說話狀態
  const toggleSpeaking = useCallback(() => {
    if (isSpeaking) {
      // 如果正在說話，停止
      logger.info('[SettingsPanel] 模擬停止說話', LogCategory.ANIMATION);
      setSpeaking(false);
      setAudioStartTime(null);
    } else {
      // 如果沒在說話，開始
      logger.info('[SettingsPanel] 模擬開始說話', LogCategory.ANIMATION);
      setSpeaking(true);
      setAudioStartTime(performance.now());
    }
  }, [isSpeaking, setSpeaking, setAudioStartTime]);

  if (!isVisible) {
    return null;
  }

  // Helper function for button classes
  const buttonClasses = (active = false, disabled = false) => 
    `px-2 py-1 text-xs rounded ${active ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-500'} ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`;

  const controlButtonClasses = (disabled = false) =>
    `px-2 py-1 text-xs rounded bg-indigo-500 text-white hover:bg-indigo-600 ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`;

  return (
    <Draggable nodeRef={nodeRef as React.RefObject<HTMLElement>} handle=".panel-header" bounds="parent"> 
      <div 
        ref={nodeRef} // Attach ref for Draggable
        className={`fixed bottom-5 right-5 z-40 w-96 max-w-[calc(100vw-2.5rem)] max-h-[70vh] bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden 
                    transition-opacity duration-300 ease-in-out ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        // Size is fixed by Tailwind classes (w-96, max-h-[70vh])
      >
        {/* Panel Header - Add panel-header class for handle */}
        <div className="panel-header flex justify-between items-center p-3 bg-gray-100 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 flex-shrink-0 cursor-move">
          <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200">模型設定</h2>
          <button 
            onClick={onClose} 
            className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none rounded-full hover:bg-gray-200 dark:hover:bg-gray-600"
            aria-label="關閉設定面板"
          >
            {/* Close icon */}
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Panel Content - Scrollable area */}
        <div className="flex-grow p-4 overflow-y-auto space-y-6 text-sm">
          
          {/* --- Model Transform Controls --- */}  
          <div className="space-y-2">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">模型變換</h3>
            <div className="grid grid-cols-3 gap-2">
              <button onClick={() => rotateModel('left')} disabled={!isModelLoaded} className={controlButtonClasses(!isModelLoaded)}>左旋</button>
              <button onClick={() => rotateModel('right')} disabled={!isModelLoaded} className={controlButtonClasses(!isModelLoaded)}>右旋</button>
              <button onClick={() => scaleModel(0.1)} disabled={!isModelLoaded} className={controlButtonClasses(!isModelLoaded)}>放大</button>
              <button onClick={() => scaleModel(-0.1)} disabled={!isModelLoaded} className={controlButtonClasses(!isModelLoaded)}>縮小</button>
              <button onClick={resetModel} disabled={!isModelLoaded} className={controlButtonClasses(!isModelLoaded)}>重置</button>
              <button onClick={toggleBackground} className={controlButtonClasses()}>{showSpaceBackground ? '隱藏背景' : '顯示背景'}</button>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              縮放: {modelScale.toFixed(2)} | 狀態: {isModelLoaded ? '已載入' : '載入中...'}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
               當前情緒: {currentEmotion} ({(emotionConfidence * 100).toFixed(1)}%)
             </div>
          </div>

          {/* --- Animation Controls --- */}  
          {availableAnimations && availableAnimations.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">動畫控制</h3>
              <div className="flex flex-wrap gap-1.5">
                {availableAnimations.map((anim) => (
                  <button
                    key={anim}
                    onClick={() => selectAnimation(anim)}
                    className={buttonClasses(currentAnimation === anim, !isModelLoaded)}
                    disabled={!isModelLoaded}
                  >
                    {anim}
                  </button>
                ))}
                <button 
                  onClick={() => selectAnimation('')} 
                  disabled={!currentAnimation || !isModelLoaded} 
                  className={buttonClasses(false, !currentAnimation || !isModelLoaded)}
                >
                  停止
                </button>
              </div>
            </div>
          )}

          {/* --- Preset Expressions --- */}  
          <div className="space-y-2">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">預設表情</h3>
            {loadingPresets ? (
              <p className="text-xs text-gray-500 dark:text-gray-400">載入預設表情中...</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {presets.map((preset) => (
                  <button
                    key={preset}
                    onClick={() => handlePresetApply(preset)}
                    className={buttonClasses(false, !isModelLoaded)}
                    disabled={!isModelLoaded}
                  >
                    {translatePreset(preset)}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* --- Morph Target Controls --- */}  
          {morphTargetDictionary && sortedMorphTargetKeys.length > 0 && (
            <div className="space-y-3">
               <div className="flex justify-between items-center">
                 <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">表情細調 (Morph Targets)</h3>
                 <button 
                   onClick={resetAllMorphTargets} 
                   disabled={!isModelLoaded}
                   className={buttonClasses(false, !isModelLoaded)}
                 >
                   全部重置
                 </button>
               </div>
              <div className="space-y-1 max-h-48 overflow-y-auto pr-2"> {/* Limit height and enable scroll */} 
                {sortedMorphTargetKeys.map((key) => (
                  <MorphTargetBar
                    key={key}
                    name={key}
                    value={morphTargetsFromStore[key] || 0} // Use live value from store
                    onChange={handleMorphTargetChange}
                  />
                ))}
              </div>
            </div>
          )}

          {/* --- Debug Controls (Moved from AppUI) --- */} 
          <div className="space-y-2 pt-4 border-t border-gray-200 dark:border-gray-600">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">除錯工具</h3>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={toggleDebugMode}
                className={`px-3 py-1.5 rounded text-xs text-white shadow-md transition-colors duration-200 ${debugMode ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'}`}
              >
                {debugMode ? '關閉調試' : '開啟調試'}
              </button>
              <button
                onClick={toggleModelAnalyzer}
                className={`px-3 py-1.5 rounded text-xs text-white shadow-md transition-colors duration-200 ${showModelAnalyzer ? 'bg-red-500 hover:bg-red-600' : 'bg-purple-500 hover:bg-purple-600'}`}
              >
                {showModelAnalyzer ? '關閉分析' : '模型分析'}
              </button>
              <button
                onClick={handleModelSwitch}
                className="px-3 py-1.5 rounded text-xs text-white bg-orange-500 hover:bg-orange-600 shadow-md transition-colors duration-200 truncate col-span-2" // Span 2 columns
                title={`切換模型: ${modelUrl.split('/').pop()?.replace('.glb', '')}`}
              >
                切換模型: {modelUrl.split('/').pop()?.replace('.glb', '')}
              </button>
            </div>
          </div>

          {/* --- 測試工具區塊 (只在Debug模式顯示) --- */}
          <div className="space-y-2 border-t border-gray-200 dark:border-gray-700 pt-4">
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase flex items-center">
              <span>情緒化說話測試</span>
              <span className="ml-2 px-1.5 py-0.5 text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">測試工具</span>
            </h3>
            
            {/* 手動控制說話狀態 */}
            <div className="mb-2">
               <button 
                 onClick={() => {
                   if (!isSpeaking) {
                     logger.info('[SettingsPanel] 手動觸發開始說話狀態', LogCategory.ANIMATION);
                     setSpeaking(true);
                     setAudioStartTime(performance.now());
                   }
                 }}
                 disabled={isSpeaking} // 如果正在說話，則禁用此按鈕
                 className={`px-3 py-1.5 rounded text-white w-full ${isSpeaking ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'}`}
               >
                 {isSpeaking ? '正在說話中...' : '手動開始說話 (設置 isSpeaking=true)'}
               </button>
               {/* 可以保留或移除手動停止按鈕，取決於您的測試需求 */} 
               {isSpeaking && (
                 <button 
                   onClick={() => {
                     setSpeaking(false);
                     setAudioStartTime(null);
                     logger.info('[SettingsPanel] 手動停止說話', LogCategory.ANIMATION);
                   }}
                   className="w-full px-2 py-1.5 mt-2 bg-red-500 hover:bg-red-600 text-white rounded text-xs"
                 >
                   手動停止說話
                 </button>
               )}
            </div>
            
            {/* 同時播放與情緒變化測試 */}
            <div className="space-y-2">
              <p className="text-xs text-gray-500 dark:text-gray-400">以下按鈕會同時模擬「說話狀態」和「情緒變化」，並在指定時間後自動停止:</p>
              <div className="grid grid-cols-1 gap-2">
                <button 
                  onClick={() => {
                    // 設置說話狀態
                    setSpeaking(true);
                    setAudioStartTime(performance.now());
                    // 發送情緒軌跡
                    sendMockTrajectory('happyToSurprisedToHappy');
                    // 15秒後自動停止說話
                    setTimeout(() => {
                      setSpeaking(false);
                      setAudioStartTime(null);
                      logger.info('[SettingsPanel] 自動停止說話 (15秒完畢)', LogCategory.ANIMATION);
                    }, 15000);
                  }}
                  disabled={!isModelLoaded || isSpeaking}
                  className="px-2 py-2 bg-gradient-to-r from-blue-400 to-cyan-500 text-white rounded hover:from-blue-500 hover:to-cyan-600 disabled:opacity-50 text-xs"
                >
                  1. 模擬講話 15 秒 (開心→驚訝→開心)
                </button>
                <button 
                  onClick={() => {
                    // 設置說話狀態
                    setSpeaking(true);
                    setAudioStartTime(performance.now());
                    // 發送情緒軌跡
                    sendMockTrajectory('sadToAngryToNeutral');
                    // 10秒後自動停止說話
                    setTimeout(() => {
                      setSpeaking(false);
                      setAudioStartTime(null);
                      logger.info('[SettingsPanel] 自動停止說話 (10秒完畢)', LogCategory.ANIMATION);
                    }, 10000);
                  }}
                  disabled={!isModelLoaded || isSpeaking}
                  className="px-2 py-2 bg-gradient-to-r from-purple-400 to-pink-500 text-white rounded hover:from-purple-500 hover:to-pink-600 disabled:opacity-50 text-xs"
                >
                  2. 模擬講話 10 秒 (悲傷→生氣→中性)
                </button>
                <button 
                  onClick={() => {
                    // 設置說話狀態
                    setSpeaking(true);
                    setAudioStartTime(performance.now());
                    // 發送情緒軌跡
                    sendMockTrajectory('emotionTour');
                    // 20秒後自動停止說話
                    setTimeout(() => {
                      setSpeaking(false);
                      setAudioStartTime(null);
                      logger.info('[SettingsPanel] 自動停止說話 (20秒完畢)', LogCategory.ANIMATION);
                    }, 20000);
                  }}
                  disabled={!isModelLoaded || isSpeaking}
                  className="px-2 py-2 bg-gradient-to-r from-amber-400 to-orange-500 text-white rounded hover:from-amber-500 hover:to-orange-600 disabled:opacity-50 text-xs"
                >
                  3. 模擬講話 20 秒 (情緒巡迴)
                </button>
              </div>
              <p className="text-xs text-gray-400 italic mt-2">
                每個按鈕按一下就會：1) 設置說話狀態 2) 發送情緒軌跡 3) 計時結束後自動停止
              </p>
            </div>
          </div>
          {/* --- 測試工具區塊結束 --- */}
        </div>
      </div>
    </Draggable>
  );
};

export default SettingsPanel; 