import React, { useState, useEffect } from 'react';
import { useSoundEffects } from '../hooks';

// 引入拆分後的組件
import FreesoundPanel from './soundEffects/FreesoundPanel';
import SynthPanel from './soundEffects/SynthPanel';
import SongLibraryPanel from './soundEffects/SongLibraryPanel';

// 面板 props 定義
interface SoundEffectPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

const SoundEffectPanel: React.FC<SoundEffectPanelProps> = ({ isVisible, onClose }) => {
  // 使用音效掛鉤
  const soundEffects = useSoundEffects();
  
  // 當前選擇的標籤
  const [activeTab, setActiveTab] = useState<string>('freesound');
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