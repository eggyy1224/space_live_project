import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useSoundEffects } from '../hooks';
import useFreesoundAPI from '../hooks/useFreesoundAPI';
import { FreesoundSearchResult } from '../services/FreesoundService';
import { soundEffectCategories, soundEffectInfo } from '../config/soundEffectsConfig';
import logger, { LogCategory } from '../utils/LogManager';

// 添加 props 定義，使組件接受從父元件傳入的可見性與切換函數
interface SoundEffectPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

// 定義多種合成音效範例
const synthExamples = {
  // 基本範例
  basic: {
    effects: [
      {
        type: "beep",
        options: { 
          frequency: 880,
          duration: 0.2,
          volume: 0.8
        },
        startTime: 0
      },
      {
        type: "laser",
        options: {
          volume: 0.7
        },
        startTime: 500
      },
      {
        type: "powerUp",
        options: {
          duration: 1,
          volume: 0.6
        },
        startTime: 1000
      }
    ]
  },
  
  // 綜藝感鼓聲系列
  variety: {
    effects: [
      {
        type: "beep",
        options: { 
          frequency: 440,
          duration: 0.1,
          volume: 0.6,
          wavetype: "triangle"
        },
        startTime: 0
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.15,
          volume: 0.7,
          filter: {
            type: "lowpass",
            frequency: 500
          }
        },
        startTime: 100
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.2,
          volume: 0.9,
          filter: {
            type: "lowpass",
            frequency: 300
          }
        },
        startTime: 300
      },
      {
        type: "beep",
        options: { 
          frequency: 880,
          duration: 0.05,
          volume: 0.8
        },
        startTime: 800
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.3,
          volume: 1.0,
          filter: {
            type: "lowpass",
            frequency: 200
          }
        },
        startTime: 1200
      },
      {
        type: "powerUp",
        options: {
          duration: 1.5,
          volume: 0.7
        },
        startTime: 2000
      }
    ]
  },
  
  // 科幻系列
  scifi: {
    effects: [
      {
        type: "sweep",
        options: {
          startFreq: 2000,
          endFreq: 500,
          duration: 0.3,
          volume: 0.6,
          wavetype: "sawtooth"
        },
        startTime: 0
      },
      {
        type: "laser",
        options: {
          volume: 0.7
        },
        startTime: 500
      },
      {
        type: "beep",
        options: {
          frequency: 1200,
          duration: 0.05,
          volume: 0.5,
          wavetype: "sine"
        },
        startTime: 1000
      },
      {
        type: "beep",
        options: {
          frequency: 1500,
          duration: 0.05,
          volume: 0.5,
          wavetype: "sine"
        },
        startTime: 1100
      },
      {
        type: "beep",
        options: {
          frequency: 1800,
          duration: 0.05,
          volume: 0.5,
          wavetype: "sine"
        },
        startTime: 1200
      },
      {
        type: "explosion",
        options: {
          duration: 1,
          volume: 0.8
        },
        startTime: 1500
      }
    ]
  },
  
  // 鼓聲節奏
  drums: {
    effects: [
      // 主要鼓聲
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.1,
          volume: 0.8,
          filter: {
            type: "lowpass",
            frequency: 300
          }
        },
        startTime: 0
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.05,
          volume: 0.6,
          filter: {
            type: "highpass",
            frequency: 3000
          }
        },
        startTime: 250
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.1,
          volume: 0.8,
          filter: {
            type: "lowpass",
            frequency: 300
          }
        },
        startTime: 500
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.05,
          volume: 0.6,
          filter: {
            type: "highpass",
            frequency: 3000
          }
        },
        startTime: 750
      },
      // 重複模式
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.1,
          volume: 0.8,
          filter: {
            type: "lowpass",
            frequency: 300
          }
        },
        startTime: 1000
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.05,
          volume: 0.6,
          filter: {
            type: "highpass",
            frequency: 3000
          }
        },
        startTime: 1250
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.1,
          volume: 0.8,
          filter: {
            type: "lowpass",
            frequency: 300
          }
        },
        startTime: 1500
      },
      {
        type: "noise",
        options: {
          noiseType: "white",
          duration: 0.3,
          volume: 1.0,
          filter: {
            type: "lowpass",
            frequency: 200
          }
        },
        startTime: 1750
      }
    ]
  }
};

// 修改為接受 props 的形式
const SoundEffectPanel: React.FC<SoundEffectPanelProps> = ({ isVisible, onClose }) => {
  // 添加JSON指令輸入狀態
  const [jsonInput, setJsonInput] = useState('');
  // 添加合成音效指令輸入狀態
  const [synthJsonInput, setSynthJsonInput] = useState('');
  // 添加當前標籤狀態
  const [activeTab, setActiveTab] = useState('samples');
  // 添加Freesound搜索關鍵詞狀態
  const [searchQuery, setSearchQuery] = useState('');
  // 添加當前播放音效ID
  const [playingPreviewId, setPlayingPreviewId] = useState<number | null>(null);
  // 添加音效預覽音頻元素
  const audioPreviewRef = useRef<HTMLAudioElement | null>(null);
  
  // 標籤引用
  const samplesTabRef = useRef<HTMLInputElement>(null);
  const synthTabRef = useRef<HTMLInputElement>(null);
  const freesoundTabRef = useRef<HTMLInputElement>(null);
  
  // 使用音效hook
  const {
    isReady,
    isLoading,
    globalVolume,
    loadedSounds,
    unlockAudioContext,
    initAndLoadSounds,
    playSingleSoundEffect,
    playSynthSound,
    playSynthSequence,
    playSoundEffectFromCommand,
    setGlobalVolume,
    stopAllSounds
  } = useSoundEffects();

  // 使用Freesound API hook
  const {
    isLoading: isSearchLoading,
    error: searchError,
    searchResults,
    totalResults,
    currentPage,
    hasNextPage,
    search,
    loadMore,
    cachedSounds,
    cacheSound,
    getPreviewUrl
  } = useFreesoundAPI();

  // 使用useMemo優化，避免不必要的重渲染
  const categorizedTags = useMemo(() => {
    const tags: Record<string, string[]> = {
      '綜藝': ['applause', 'laugh', 'crowd', 'comedy', 'funny', 'drum', 'fail', 'success'],
      '科幻': ['laser', 'space', 'futuristic', 'robot', 'sci-fi', 'technology', 'machine'],
      '環境': ['nature', 'water', 'wind', 'rain', 'city', 'ambient', 'forest', 'birds'],
      '音樂': ['music', 'piano', 'guitar', 'drum', 'bass', 'electronic', 'orchestra', 'beat'],
      '動物': ['animal', 'dog', 'cat', 'bird', 'roar', 'howl', 'bark', 'meow'],
      '人聲': ['voice', 'speech', 'shout', 'scream', 'whisper', 'talk', 'human'],
      '物體': ['door', 'explosion', 'crash', 'impact', 'glass', 'metal', 'wooden', 'plastic']
    };
    return tags;
  }, []);

  // 首次載入時解鎖音頻上下文並初始化
  useEffect(() => {
    if (isVisible && !isReady && !isLoading) {
      // 嘗試解鎖音頻上下文
      unlockAudioContext().then(success => {
        if (success) {
          logger.info('[SoundEffectPanel] AudioContext unlocked successfully', LogCategory.AUDIO);
        } else {
          logger.warn('[SoundEffectPanel] Failed to unlock AudioContext', LogCategory.AUDIO);
        }
      });
    }
  }, [isVisible, isReady, isLoading, unlockAudioContext]);

  // 處理標籤切換
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    // 不用直接操作 DOM，使用 React 狀態來控制顯示
  };

  // 播放音效並顯示日誌
  const handlePlaySoundEffect = (soundId: string) => {
    logger.info(`[SoundEffectPanel] Playing sound effect: ${soundId}`, LogCategory.AUDIO);
    
    if (!isReady) {
      logger.warn(`[SoundEffectPanel] Cannot play sound ${soundId}: Service not ready`, LogCategory.AUDIO);
      
      // 嘗試初始化
      unlockAudioContext().then(success => {
        if (success) {
          logger.info('[SoundEffectPanel] AudioContext unlocked on demand', LogCategory.AUDIO);
        }
      });
      
      return;
    }
    
    // 播放音效
    playSingleSoundEffect(soundId);
  };

  // 播放合成音效
  const handlePlaySynthSound = (type: string, options = {}) => {
    logger.info(`[SoundEffectPanel] Playing synth sound: ${type}`, LogCategory.AUDIO);
    
    // 解鎖音頻上下文（如果尚未完成）
    unlockAudioContext().then(success => {
      if (success) {
        // 播放合成音效
        playSynthSound(type, options);
      } else {
        logger.warn('[SoundEffectPanel] Cannot play synth sound: AudioContext not unlocked', LogCategory.AUDIO);
      }
    });
  };

  // 處理JSON指令執行
  const handleExecuteCommand = () => {
    try {
      // 解析JSON
      const commandObj = JSON.parse(jsonInput);
      logger.info('[SoundEffectPanel] Parsed JSON command:', LogCategory.AUDIO, commandObj);
      
      // 檢查是否符合預期格式
      if (commandObj.effects && Array.isArray(commandObj.effects)) {
        logger.info(`[SoundEffectPanel] Executing command with ${commandObj.effects.length} effects`, LogCategory.AUDIO);
        
        // 解鎖音頻上下文（如果尚未完成）
        unlockAudioContext().then(success => {
          if (success && isReady) {
            // 執行音效序列
            const result = playSoundEffectFromCommand(commandObj.effects);
            
            if (!result) {
              logger.warn('[SoundEffectPanel] Failed to execute sound effect command', LogCategory.AUDIO);
            }
          } else {
            logger.warn('[SoundEffectPanel] Cannot execute command: AudioContext not unlocked or service not ready', LogCategory.AUDIO);
          }
        });
      } else {
        logger.warn('[SoundEffectPanel] Invalid command format: missing or invalid effects array', LogCategory.AUDIO);
        alert('指令格式錯誤：未找到effects陣列');
      }
    } catch (error) {
      logger.error('[SoundEffectPanel] JSON parsing error:', LogCategory.AUDIO, error);
      alert(`JSON解析錯誤: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  };

  // 處理合成音效JSON指令執行
  const handleExecuteSynthCommand = () => {
    try {
      // 解析JSON
      const commandObj = JSON.parse(synthJsonInput);
      logger.info('[SoundEffectPanel] Parsed synth JSON command:', LogCategory.AUDIO, commandObj);
      
      // 檢查是否符合預期格式（支持兩種格式：直接effects數組或包含在payload中）
      const effects = commandObj.effects || (commandObj.payload && commandObj.payload.effects);
      
      if (effects && Array.isArray(effects)) {
        logger.info(`[SoundEffectPanel] Executing synth command with ${effects.length} effects`, LogCategory.AUDIO);
        
        // 解鎖音頻上下文（如果尚未完成）
        unlockAudioContext().then(success => {
          if (success) {
            // 執行合成音效序列
            const result = playSynthSequence(effects);
            
            if (!result) {
              logger.warn('[SoundEffectPanel] Failed to execute synth command', LogCategory.AUDIO);
            }
          } else {
            logger.warn('[SoundEffectPanel] Cannot execute synth command: AudioContext not unlocked', LogCategory.AUDIO);
          }
        });
      } else {
        logger.warn('[SoundEffectPanel] Invalid synth command format: missing or invalid effects array', LogCategory.AUDIO);
        alert('指令格式錯誤：未找到effects陣列');
      }
    } catch (error) {
      logger.error('[SoundEffectPanel] JSON parsing error:', LogCategory.AUDIO, error);
      alert(`JSON解析錯誤: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  };

  // 處理音量變更
  const handleVolumeChange = (value: number) => {
    // 將0-100轉換為0-1
    const normalizedVolume = value / 100;
    setGlobalVolume(normalizedVolume);
  };

  // 執行搜索
  const handleSearch = () => {
    if (searchQuery.trim()) {
      search({ query: searchQuery, page: 1 });
    }
  };

  // 按標籤搜索
  const handleTagSearch = (tag: string) => {
    setSearchQuery(tag);
    search({ query: `tag:${tag}`, page: 1 });
  };

  // 播放音效預覽
  const handlePlayPreview = (sound: FreesoundSearchResult) => {
    if (audioPreviewRef.current) {
      // 停止當前播放
      audioPreviewRef.current.pause();
      
      // 獲取預覽URL
      const previewUrl = getPreviewUrl(sound);
      
      // 設置新音源
      audioPreviewRef.current.src = previewUrl;
      audioPreviewRef.current.volume = globalVolume;
      
      // 播放
      audioPreviewRef.current.play()
        .then(() => {
          setPlayingPreviewId(sound.id);
          logger.info(`[SoundEffectPanel] 預覽播放: ${sound.name}`, LogCategory.AUDIO);
        })
        .catch(error => {
          logger.error(`[SoundEffectPanel] 預覽播放失敗: ${error.message}`, LogCategory.AUDIO);
        });
    }
  };

  // 停止預覽
  const handleStopPreview = () => {
    if (audioPreviewRef.current) {
      audioPreviewRef.current.pause();
      setPlayingPreviewId(null);
    }
  };

  // 收藏音效
  const handleSaveSound = async (sound: FreesoundSearchResult) => {
    try {
      await cacheSound(sound);
      logger.info(`[SoundEffectPanel] 音效已收藏: ${sound.name}`, LogCategory.AUDIO);
    } catch (error) {
      logger.error(`[SoundEffectPanel] 收藏音效失敗`, LogCategory.AUDIO, error);
    }
  };

  // 如果面板不可見，則不渲染
  if (!isVisible) {
    return null;
  }

  // 獲取當前音量（轉換為百分比）
  const volumePercent = Math.round(globalVolume * 100);

  return (
    <div 
      className="fixed right-20 bottom-20 w-80 bg-gray-800 bg-opacity-90 rounded-lg shadow-lg p-4 z-[999] text-white"
      // 點擊面板不會關閉(阻止冒泡)
      onClick={e => e.stopPropagation()}
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">音效控制面板</h2>
        <div className="flex items-center">
          {/* 顯示載入狀態 */}
          <span className={`w-3 h-3 rounded-full mr-2 ${isReady ? 'bg-green-500' : isLoading ? 'bg-yellow-500' : 'bg-red-500'}`} 
                title={isReady ? '已準備就緒' : isLoading ? '正在載入中' : '未準備就緒'}>
          </span>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
            aria-label="關閉音效面板"
          >
            ✕
          </button>
        </div>
      </div>

      {/* 標籤頁切換 */}
      <div className="mb-4">
        <ul className="flex border-b border-gray-700">
          <li className="mr-2">
            <button 
              onClick={() => handleTabChange('samples')}
              className={`inline-block px-4 py-2 border-b-2 ${activeTab === 'samples' ? 'border-blue-500 text-blue-500' : 'border-transparent hover:text-gray-300'}`}
            >
              預設音效
            </button>
          </li>
          <li className="mr-2">
            <button 
              onClick={() => handleTabChange('synth')}
              className={`inline-block px-4 py-2 border-b-2 ${activeTab === 'synth' ? 'border-blue-500 text-blue-500' : 'border-transparent hover:text-gray-300'}`}
            >
              合成音效
            </button>
          </li>
          <li className="mr-2">
            <button 
              onClick={() => handleTabChange('freesound')}
              className={`inline-block px-4 py-2 border-b-2 ${activeTab === 'freesound' ? 'border-blue-500 text-blue-500' : 'border-transparent hover:text-gray-300'}`}
            >
              Freesound
            </button>
          </li>
        </ul>
      </div>

      {/* 標籤內容區域 */}
      <div className="tabs-content overflow-y-auto" style={{ maxHeight: '400px' }}>
        {/* 預設音效標籤 */}
        <div className={activeTab === 'samples' ? 'block' : 'hidden'}>
          {/* 綜藝音效 */}
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">綜藝音效</h3>
            <div className="grid grid-cols-2 gap-2">
              {soundEffectCategories.variety.map(id => (
                <button
                  key={id}
                  onClick={() => handlePlaySoundEffect(id)}
                  className={`${isReady ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-600 cursor-not-allowed'} text-white px-3 py-2 rounded-md text-sm transition-colors duration-200`}
                  title={soundEffectInfo[id]?.description || id}
                  disabled={!isReady}
                >
                  {soundEffectInfo[id]?.name || id}
                </button>
              ))}
            </div>
          </div>

          {/* 科幻音效 */}
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">科幻音效</h3>
            <div className="grid grid-cols-2 gap-2">
              {soundEffectCategories['sci-fi'].map(id => (
                <button
                  key={id}
                  onClick={() => handlePlaySoundEffect(id)}
                  className={`${isReady ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-600 cursor-not-allowed'} text-white px-3 py-2 rounded-md text-sm transition-colors duration-200`}
                  title={soundEffectInfo[id]?.description || id}
                  disabled={!isReady}
                >
                  {soundEffectInfo[id]?.name || id}
                </button>
              ))}
            </div>
          </div>

          {/* 環境音效 */}
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">環境音效</h3>
            <div className="grid grid-cols-2 gap-2">
              {soundEffectCategories.environment.map(id => (
                <button
                  key={id}
                  onClick={() => handlePlaySoundEffect(id)}
                  className={`${isReady ? 'bg-teal-600 hover:bg-teal-700' : 'bg-gray-600 cursor-not-allowed'} text-white px-3 py-2 rounded-md text-sm transition-colors duration-200`}
                  title={soundEffectInfo[id]?.description || id}
                  disabled={!isReady}
                >
                  {soundEffectInfo[id]?.name || id}
                </button>
              ))}
            </div>
          </div>

          {/* JSON指令測試區域 */}
          <div className="mt-4 border-t border-gray-700 pt-4">
            <h3 className="text-lg font-semibold mb-2">API測試</h3>
            <div className="space-y-2">
              <textarea 
                className="w-full h-32 px-2 py-1 text-sm bg-gray-700 text-white rounded"
                placeholder={`輸入JSON指令，例如：
{
  "effects": [
    {
      "name": "entrance",
      "type": "variety",
      "params": { "volume": 0.8 },
      "startTime": 0
    },
    {
      "name": "applause",
      "params": { "volume": 1.0 },
      "startTime": 1000
    }
  ]
}`}
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleExecuteCommand}
                  className={`flex-1 ${isReady ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 cursor-not-allowed'} text-white py-2 rounded`}
                  disabled={!isReady}
                >
                  執行指令
                </button>
                <button
                  onClick={() => setJsonInput(JSON.stringify({
                    effects: [
                      {
                        name: "entrance",
                        type: "variety",
                        params: { volume: 0.8 },
                        startTime: 0
                      },
                      {
                        name: "applause",
                        params: { volume: 1.0 },
                        startTime: 1000
                      }
                    ]
                  }, null, 2))}
                  className="px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded"
                  title="載入預設範例"
                >
                  範例
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              可用於測試後端WebSocket指令。將JSON貼上並點擊執行。
            </p>
          </div>
        </div>

        {/* 合成音效標籤 */}
        <div className={activeTab === 'synth' ? 'block' : 'hidden'}>
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Tone.js 合成器音效</h3>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => handlePlaySynthSound('beep', { frequency: 880, duration: 0.2 })}
                className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="簡單的高音嗶聲"
              >
                嗶聲 (高音)
              </button>
              <button
                onClick={() => handlePlaySynthSound('beep', { frequency: 440, duration: 0.3 })}
                className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="簡單的中音嗶聲"
              >
                嗶聲 (中音)
              </button>
              <button
                onClick={() => handlePlaySynthSound('sweep', { startFreq: 220, endFreq: 880, duration: 0.5 })}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="上升頻率掃描"
              >
                頻率掃描 (上升)
              </button>
              <button
                onClick={() => handlePlaySynthSound('sweep', { startFreq: 880, endFreq: 220, duration: 0.5 })}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="下降頻率掃描"
              >
                頻率掃描 (下降)
              </button>
              <button
                onClick={() => handlePlaySynthSound('noise', { noiseType: 'white', duration: 0.3 })}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="白噪音"
              >
                白噪音
              </button>
              <button
                onClick={() => handlePlaySynthSound('noise', { noiseType: 'pink', duration: 0.3 })}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="粉紅噪音"
              >
                粉紅噪音
              </button>
              <button
                onClick={() => handlePlaySynthSound('laser')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="雷射槍音效"
              >
                雷射音效
              </button>
              <button
                onClick={() => handlePlaySynthSound('explosion')}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title="爆炸音效"
              >
                爆炸音效
              </button>
              <button
                onClick={() => handlePlaySynthSound('powerUp', { duration: 1 })}
                className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200 col-span-2"
                title="能量充能音效"
              >
                能量充能
              </button>
            </div>
          </div>

          {/* 合成音效JSON指令測試區域 */}
          <div className="mt-4 border-t border-gray-700 pt-4">
            <h3 className="text-lg font-semibold mb-2">合成音效測試</h3>
            <div className="space-y-2">
              <textarea 
                className="w-full h-32 px-2 py-1 text-sm bg-gray-700 text-white rounded"
                placeholder={`輸入合成音效序列，例如：
{
  "effects": [
    {
      "type": "beep",
      "options": { 
        "frequency": 880,
        "duration": 0.2,
        "volume": 0.8
      },
      "startTime": 0
    },
    {
      "type": "laser",
      "options": {
        "volume": 0.7
      },
      "startTime": 500
    }
  ]
}`}
                value={synthJsonInput}
                onChange={(e) => setSynthJsonInput(e.target.value)}
              />
              <div className="flex space-x-2 mb-2">
                <button
                  onClick={handleExecuteSynthCommand}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded"
                >
                  執行合成序列
                </button>
              </div>
              
              {/* 範例選擇區 */}
              <div className="grid grid-cols-2 gap-2 mb-2">
                <button
                  onClick={() => setSynthJsonInput(JSON.stringify(synthExamples.basic, null, 2))}
                  className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
                  title="基本音效組合"
                >
                  基本範例
                </button>
                <button
                  onClick={() => setSynthJsonInput(JSON.stringify(synthExamples.variety, null, 2))}
                  className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded"
                  title="帶有綜藝節目風格的音效序列"
                >
                  綜藝鼓聲
                </button>
                <button
                  onClick={() => setSynthJsonInput(JSON.stringify(synthExamples.scifi, null, 2))}
                  className="px-3 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded"
                  title="科幻風格音效"
                >
                  科幻系列
                </button>
                <button
                  onClick={() => setSynthJsonInput(JSON.stringify(synthExamples.drums, null, 2))}
                  className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
                  title="鼓聲節奏模式"
                >
                  鼓聲節奏
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              測試直接通過Tone.js生成的合成音效和音效序列。點擊範例後再點擊"執行合成序列"。
            </p>
          </div>
        </div>

        {/* Freesound庫標籤 */}
        <div className={activeTab === 'freesound' ? 'block' : 'hidden'}>
          {/* 搜索區域 */}
          <div className="mb-4">
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索音效..."
                className="flex-1 px-2 py-1 bg-gray-700 rounded text-white text-sm"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
                disabled={isSearchLoading}
              >
                {isSearchLoading ? '搜索中...' : '搜索'}
              </button>
            </div>
            
            {/* 熱門標籤 */}
            <div className="mb-2">
              <p className="text-xs text-gray-400 mb-1">熱門標籤:</p>
              <div className="flex flex-wrap gap-1">
                {Object.entries(categorizedTags).flatMap(([category, tags]) => (
                  tags.slice(0, 3).map(tag => (
                    <button
                      key={tag}
                      onClick={() => handleTagSearch(tag)}
                      className="px-2 py-0.5 text-xs bg-gray-700 hover:bg-gray-600 rounded-full text-gray-200"
                    >
                      {tag}
                    </button>
                  ))
                ))}
              </div>
            </div>
            
            {/* 分類標籤 */}
            <div className="mb-2">
              <details className="text-xs">
                <summary className="text-gray-400 cursor-pointer">所有分類</summary>
                <div className="mt-1 pl-2">
                  {Object.entries(categorizedTags).map(([category, tags]) => (
                    <div key={category} className="mb-2">
                      <p className="text-gray-400 mb-1">{category}:</p>
                      <div className="flex flex-wrap gap-1">
                        {tags.map(tag => (
                          <button
                            key={tag}
                            onClick={() => handleTagSearch(tag)}
                            className="px-2 py-0.5 text-xs bg-gray-700 hover:bg-gray-600 rounded-full text-gray-200"
                          >
                            {tag}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          </div>
          
          {/* 搜索結果 */}
          <div className="mb-4">
            {searchError && (
              <p className="text-red-400 text-sm">{searchError}</p>
            )}
            
            {searchResults.length > 0 ? (
              <>
                <p className="text-xs text-gray-400 mb-2">找到 {totalResults} 個結果:</p>
                
                <div className="space-y-2">
                  {searchResults.map(sound => (
                    <div 
                      key={sound.id} 
                      className="p-2 bg-gray-700 rounded hover:bg-gray-600 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="text-sm font-semibold truncate" title={sound.name}>
                          {sound.name}
                        </h4>
                        <span className="text-xs text-gray-400">
                          {sound.duration.toFixed(1)}s
                        </span>
                      </div>
                      
                      {/* 波形圖 */}
                      {sound.images?.waveform_m && (
                        <div className="mb-1">
                          <img 
                            src={sound.images.waveform_m} 
                            alt="波形圖" 
                            className="w-full h-12 object-cover rounded"
                          />
                        </div>
                      )}
                      
                      <div className="flex flex-wrap gap-1 mb-1">
                        {sound.tags.slice(0, 3).map(tag => (
                          <span key={tag} className="px-1.5 py-0.5 bg-gray-800 rounded-full text-gray-300 text-xs">
                            {tag}
                          </span>
                        ))}
                        {sound.tags.length > 3 && (
                          <span className="px-1.5 py-0.5 bg-gray-800 rounded-full text-gray-400 text-xs">
                            +{sound.tags.length - 3}
                          </span>
                        )}
                      </div>
                      
                      <div className="flex text-xs text-gray-400 justify-between">
                        <span title="上傳者">{sound.username}</span>
                        <span title="許可證">{sound.license}</span>
                      </div>
                      
                      {/* 操作按鈕 */}
                      <div className="flex justify-between mt-2">
                        <button
                          onClick={() => playingPreviewId === sound.id 
                            ? handleStopPreview() 
                            : handlePlayPreview(sound)
                          }
                          className={`px-2 py-1 text-xs rounded ${
                            playingPreviewId === sound.id 
                              ? 'bg-red-600 hover:bg-red-700' 
                              : 'bg-green-600 hover:bg-green-700'
                          } text-white`}
                        >
                          {playingPreviewId === sound.id ? '停止' : '預覽'}
                        </button>
                        
                        <button
                          onClick={() => handleSaveSound(sound)}
                          className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
                          title="收藏音效"
                        >
                          收藏
                        </button>
                        
                        <a
                          href={sound.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-1 text-xs bg-gray-600 hover:bg-gray-500 rounded text-white"
                          title="查看詳情"
                        >
                          詳情
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* 加載更多按鈕 */}
                {hasNextPage && (
                  <button
                    onClick={loadMore}
                    disabled={isSearchLoading}
                    className="w-full mt-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200"
                  >
                    {isSearchLoading ? '加載中...' : '加載更多'}
                  </button>
                )}
              </>
            ) : searchQuery ? (
              <p className="text-sm text-gray-400">未找到結果</p>
            ) : (
              <p className="text-sm text-gray-400">輸入關鍵詞開始搜索</p>
            )}
          </div>
          
          {/* 收藏的音效 */}
          {cachedSounds.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-700">
              <h3 className="text-lg font-semibold mb-2">我的收藏</h3>
              
              <div className="space-y-2">
                {cachedSounds.map(sound => (
                  <div 
                    key={sound.id} 
                    className="p-2 bg-gray-700 rounded"
                  >
                    <div className="flex justify-between">
                      <h4 className="text-sm truncate" title={sound.name}>
                        {sound.name}
                      </h4>
                      
                      <button
                        onClick={() => sound.previews && handlePlayPreview(sound as FreesoundSearchResult)}
                        className="px-2 text-xs bg-green-600 hover:bg-green-700 rounded text-white"
                      >
                        播放
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* 音頻預覽元素 */}
          <audio ref={audioPreviewRef} className="hidden" />
        </div>
      </div>

      {/* 控制區域 */}
      <div className="mb-4 mt-4 pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold mb-2">控制</h3>
        
        {/* 音量控制 */}
        <div className="flex items-center mb-2">
          <span className="mr-2">音量</span>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={volumePercent}
            className="w-full"
            onChange={(e) => handleVolumeChange(parseInt(e.target.value))}
          />
          <span className="ml-2">{volumePercent}%</span>
        </div>
        
        {/* 停止所有音效 */}
        <button
          onClick={stopAllSounds}
          className="w-full bg-red-600 hover:bg-red-700 text-white py-1.5 rounded mt-2"
        >
          停止所有音效
        </button>
      </div>
      
      {/* 載入狀態 */}
      <div className="mt-4 text-xs text-gray-400">
        狀態: {isReady ? '準備就緒' : isLoading ? '載入中...' : '未初始化'} | 
        已載入預設音效: {loadedSounds.length}
      </div>

      {/* 測試用的隱藏標籤，添加freesound標籤 */}
      <input ref={samplesTabRef} type="radio" id="tab-samples" name="tabs" className="hidden" defaultChecked />
      <input ref={synthTabRef} type="radio" id="tab-synth" name="tabs" className="hidden" />
      <input ref={freesoundTabRef} type="radio" id="tab-freesound" name="tabs" className="hidden" />
    </div>
  );
};

export default SoundEffectPanel;