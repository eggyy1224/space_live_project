import React, { useState, useEffect } from 'react';
import { useSoundEffects } from '../hooks';
import useFreesoundAPI from '../hooks/useFreesoundAPI';
import { soundEffectCategories, soundEffectInfo } from '../config/soundEffectsConfig';
import logger, { LogCategory } from '../utils/LogManager';
import { useStore } from '../store';

// 引入拆分後的組件
import FreesoundPanel from './soundEffects/FreesoundPanel';
import SynthPanel from './soundEffects/SynthPanel';
import SongLibraryPanel from './soundEffects/SongLibraryPanel';

// 添加 props 定義，使組件接受從父元件傳入的可見性與切換函數
interface SoundEffectPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

// 定義分類名稱映射
const categoryNames: Record<string, string> = {
  'variety': '綜藝音效',
  'sci-fi': '科幻音效',
  'environment': '環境音效'
};

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

// 更新：歌曲數據結構，包含動畫線索
interface Song {
  id: string;
  name: string;
  url: string;
  animationCues?: AnimationCue[];
}

// 範例歌曲數據 (更新 URL 並添加動畫線索)
const sampleSongs: Song[] = [
  {
    id: 'song1', 
    name: '範例歌曲 1 (快樂)', 
    url: '/audio/songs/song1.mp3',
    animationCues: [
      { time: 0.5, type: 'emotion', value: 'happy' },
      { time: 1.0, type: 'action', value: 'wave_hand' },
      { time: 2.0, type: 'viseme', value: 'A' },
      { time: 3.5, type: 'emotion', value: 'excited' },
      { time: 5.0, type: 'action', value: 'idle' },
    ]
  },
  {
    id: 'song2',
    name: '範例歌曲 2 (平靜)',
    url: '/audio/songs/song2.mp3',
    animationCues: [
      { time: 0.0, type: 'emotion', value: 'calm' },
      { time: 2.0, type: 'action', value: 'subtle_nod' },
      { time: 4.0, type: 'viseme', value: 'O' },
      { time: 6.0, type: 'emotion', value: 'neutral' },
    ]
  },
  {
    id: 'song3',
    name: '範例歌曲 3 (無動畫)',
    url: '/audio/songs/song3.mp3'
  },
  {
    id: 'moonlight', 
    name: '皎潔的滿月下', 
    url: '/audio/songs/皎潔的滿月下.mp3',
    animationCues: [
      { time: 0.0, type: 'emotion', value: 'neutral' },
      { time: 0.1, type: 'action', value: 'Idle' },
      { time: 2.0, type: 'action', value: 'LookAround' },
      { time: 5.0, type: 'emotion', value: 'happy' },
      { time: 8.0, type: 'action', value: 'PointingGesture' },
      { time: 15.0, type: 'emotion', value: 'excited' },
      { time: 15.1, type: 'action', value: 'Cheering' },
      { time: 25.0, type: 'action', value: 'ReachingOut' },
      { time: 35.0, type: 'action', value: 'LookAround' },
      { time: 45.0, type: 'action', value: 'FemaleDynamicPose' },
      { time: 55.0, type: 'emotion', value: 'neutral' },
      { time: 55.1, type: 'action', value: 'FemaleStandingPose' },
      { time: 65.0, type: 'emotion', value: 'happy' },
      { time: 65.1, type: 'action', value: 'Cheering' },
      { time: 75.0, type: 'action', value: 'PointingGesture' },
      { time: 85.0, type: 'action', value: 'Idle' },
      { time: 88.0, type: 'emotion', value: 'neutral' },
    ]
  },
];

const SoundEffectPanel: React.FC<SoundEffectPanelProps> = ({ isVisible, onClose }) => {
  // 使用音效掛鉤
  const soundEffects = useSoundEffects();
  
  // 當前選擇的標籤
  const [activeTab, setActiveTab] = useState<string>('soundEffects');
  const [volume, setVolume] = useState(100);

  // useEffect 讓面板在打開時停止所有聲音
  useEffect(() => {
    if (isVisible) {
      soundEffects.stopAllSounds();
    }
  }, [isVisible, soundEffects]);

  // 處理標籤切換
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
  };

  // 處理音量變更
  const handleVolumeChange = (value: number) => {
    setVolume(value);
    soundEffects.setGlobalVolume(value / 100);
  };

  // 如果面板不可見，不渲染任何內容
  if (!isVisible) {
    return null;
  }

  return (
    <div 
      className="fixed right-8 top-16 w-96 bg-gray-800 shadow-lg rounded-lg z-30 text-white overflow-auto"
      style={{ maxHeight: 'calc(100vh - 120px)' }}
      onClick={(e) => e.stopPropagation()}
    >
      {/* 標題列 */}
      <div className="flex justify-between items-center px-4 py-3 bg-gray-900 border-b border-gray-700 sticky top-0">
        <h2 className="text-xl font-bold">音效面板</h2>
        <button 
          onClick={onClose}
          className="text-gray-400 hover:text-white focus:outline-none"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      
      {/* 主內容區 */}
      <div className="p-4">
        {/* 標籤選擇區域 */}
        <div className="flex border-b border-gray-700 mb-4 overflow-x-auto">
          <button 
            className={`px-4 py-2 whitespace-nowrap ${activeTab === 'soundEffects' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
            onClick={() => handleTabChange('soundEffects')}
          >
            預設音效
          </button>
          <button 
            className={`px-4 py-2 whitespace-nowrap ${activeTab === 'freesound' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
            onClick={() => handleTabChange('freesound')}
          >
            Freesound搜尋
          </button>
          <button 
            className={`px-4 py-2 whitespace-nowrap ${activeTab === 'synth' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
            onClick={() => handleTabChange('synth')}
          >
            合成音效
          </button>
          <button 
            className={`px-4 py-2 whitespace-nowrap ${activeTab === 'songs' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
            onClick={() => handleTabChange('songs')}
          >
            歌曲
          </button>
        </div>
        
        {/* 音量調節 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-1">音量: {volume}%</label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={volume} 
            onChange={(e) => handleVolumeChange(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-md appearance-none cursor-pointer"
          />
        </div>
        
        {/* 各標籤內容 */}
        {activeTab === 'soundEffects' && (
          <div>
            <h3 className="text-lg font-semibold mb-2">預設音效</h3>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(soundEffectCategories).map(([category, sounds]) => (
                <div key={category} className="mb-4">
                  <h4 className="text-md font-medium mb-1 text-gray-300">{categoryNames[category] || category}</h4>
                  <div className="grid grid-cols-2 gap-1">
                    {sounds.map(soundId => {
                      const sound = soundEffectInfo[soundId];
                      return (
                        <button
                          key={soundId}
                          onClick={() => soundEffects.playSingleSoundEffect(soundId)}
                          className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-xs text-left transition-colors duration-200"
                          title={sound.description}
                        >
                          {sound.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'freesound' && (
          <FreesoundPanel soundEffects={soundEffects} />
        )}
        
        {activeTab === 'synth' && (
          <SynthPanel soundEffects={soundEffects} />
        )}
        
        {activeTab === 'songs' && (
          <SongLibraryPanel globalVolume={volume} />
        )}
      </div>
    </div>
  );
};

export default SoundEffectPanel;