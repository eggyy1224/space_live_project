import React, { useState } from 'react';
// 移除不需要的store引入，因為我們現在使用props
// import { useStore } from '../store';

// 臨時的音效配置，之後會移動到配置文件中
const temporarySoundEffects = {
  'entrance': {
    name: '登場音',
    description: '人物華麗登場時使用的音效',
    type: 'variety'
  },
  'whoosh': {
    name: 'Whoosh',
    description: '快速移動或場景切換時的嗖聲',
    type: 'variety'
  },
  'applause': {
    name: '掌聲',
    description: '觀眾鼓掌聲，用於角色精彩表現',
    type: 'variety'
  },
  'laser': {
    name: '雷射',
    description: '科幻感的雷射槍射擊音效',
    type: 'sci-fi'
  },
  'transition': {
    name: '轉場',
    description: '切換場景或主題時的提示音',
    type: 'variety'
  }
};

// 添加 props 定義，使組件接受從父元件傳入的可見性與切換函數
interface SoundEffectPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

// 修改為接受 props 的形式
const SoundEffectPanel: React.FC<SoundEffectPanelProps> = ({ isVisible, onClose }) => {
  // 移除對Zustand的依賴
  // const { isSoundEffectPanelVisible, toggleSoundEffectPanel } = useStore(state => ({
  //   isSoundEffectPanelVisible: state.isSoundEffectPanelVisible,
  //   toggleSoundEffectPanel: state.toggleSoundEffectPanel
  // }));

  // 添加JSON指令輸入狀態
  const [jsonInput, setJsonInput] = useState('');
  // 添加音量狀態
  const [volume, setVolume] = useState(80);

  // 臨時的播放音效函數(尚未實現實際功能)
  const playSoundEffect = (soundId: string) => {
    console.log(`播放音效: ${soundId}`);
    // TODO: 這裡將來會調用 useSoundEffects hook 的播放方法
  };

  // 處理JSON指令執行
  const handleExecuteCommand = () => {
    try {
      const commandObj = JSON.parse(jsonInput);
      console.log('解析後的JSON指令:', commandObj);
      
      // 檢查是否符合預期格式
      if (commandObj.effects && Array.isArray(commandObj.effects)) {
        console.log(`準備執行${commandObj.effects.length}個音效指令`);
        // TODO: 這裡將來會調用 useSoundEffects().playSoundEffectFromCommand(commandObj.effects)
      } else {
        alert('指令格式錯誤：未找到effects陣列');
      }
    } catch (error) {
      alert(`JSON解析錯誤: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  };

  // 如果面板不可見，則不渲染
  if (!isVisible) {
    return null;
  }

  return (
    <div 
      className="fixed right-20 bottom-20 w-80 bg-gray-800 bg-opacity-90 rounded-lg shadow-lg p-4 z-[999] text-white"
      // 點擊面板不會關閉(阻止冒泡)
      onClick={e => e.stopPropagation()}
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">音效控制面板</h2>
        <button 
          onClick={onClose}
          className="text-gray-400 hover:text-white"
          aria-label="關閉音效面板"
        >
          ✕
        </button>
      </div>

      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">綜藝音效</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(temporarySoundEffects)
            .filter(([_, effect]) => effect.type === 'variety')
            .map(([id, effect]) => (
              <button
                key={id}
                onClick={() => playSoundEffect(id)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title={effect.description}
              >
                {effect.name}
              </button>
            ))}
        </div>
      </div>

      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">科幻音效</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(temporarySoundEffects)
            .filter(([_, effect]) => effect.type === 'sci-fi')
            .map(([id, effect]) => (
              <button
                key={id}
                onClick={() => playSoundEffect(id)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm transition-colors duration-200"
                title={effect.description}
              >
                {effect.name}
              </button>
            ))}
        </div>
      </div>

      {/* 音量控制部分 */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">控制</h3>
        <div className="flex items-center">
          <span className="mr-2">音量</span>
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={volume}
            className="w-full"
            onChange={(e) => {
              const newVolume = parseInt(e.target.value);
              setVolume(newVolume);
              console.log(`音量設定為: ${newVolume}%`);
              // TODO: 未來會調用 useSoundEffects().setGlobalVolume(newVolume / 100)
            }} 
          />
          <span className="ml-2">{volume}%</span>
        </div>
      </div>

      {/* 添加JSON指令輸入區域 */}
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
          <button
            onClick={handleExecuteCommand}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded"
          >
            執行指令
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          可用於測試後端WebSocket指令。將JSON貼上並點擊執行。
        </p>
      </div>
    </div>
  );
};

// 將 SoundEffectPanel 導入到 App.tsx 或其他布局元件中
export default SoundEffectPanel; 