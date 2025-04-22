import React, { useState } from 'react';
import { useSoundEffects } from '../../hooks';
import logger, { LogCategory } from '../../utils/LogManager';

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

interface SynthPanelProps {
  soundEffects: ReturnType<typeof useSoundEffects>;
}

const SynthPanel: React.FC<SynthPanelProps> = ({ soundEffects }) => {
  // 添加合成音效指令輸入狀態
  const [synthJsonInput, setSynthJsonInput] = useState('');
  
  const {
    unlockAudioContext,
    playSynthSound,
    playSynthSequence
  } = soundEffects;

  // 播放合成音效
  const handlePlaySynthSound = (type: string, options = {}) => {
    logger.info(`[SynthPanel] Playing synth sound: ${type}`, LogCategory.AUDIO);
    
    // 解鎖音頻上下文（如果尚未完成）
    unlockAudioContext().then(success => {
      if (success) {
        // 播放合成音效
        playSynthSound(type, options);
      } else {
        logger.warn('[SynthPanel] Cannot play synth sound: AudioContext not unlocked', LogCategory.AUDIO);
      }
    });
  };

  // 處理合成音效JSON指令執行
  const handleExecuteSynthCommand = () => {
    try {
      // 解析JSON
      const commandObj = JSON.parse(synthJsonInput);
      logger.info('[SynthPanel] Parsed synth JSON command:', LogCategory.AUDIO, commandObj);
      
      // 檢查是否符合預期格式（支持兩種格式：直接effects數組或包含在payload中）
      const effects = commandObj.effects || (commandObj.payload && commandObj.payload.effects);
      
      if (effects && Array.isArray(effects)) {
        logger.info(`[SynthPanel] Executing synth command with ${effects.length} effects`, LogCategory.AUDIO);
        
        // 解鎖音頻上下文（如果尚未完成）
        unlockAudioContext().then(success => {
          if (success) {
            // 執行合成音效序列
            const result = playSynthSequence(effects);
            
            if (!result) {
              logger.warn('[SynthPanel] Failed to execute synth command', LogCategory.AUDIO);
            }
          } else {
            logger.warn('[SynthPanel] Cannot execute synth command: AudioContext not unlocked', LogCategory.AUDIO);
          }
        });
      } else {
        logger.warn('[SynthPanel] Invalid synth command format: missing or invalid effects array', LogCategory.AUDIO);
        alert('指令格式錯誤：未找到effects陣列');
      }
    } catch (error) {
      logger.error('[SynthPanel] JSON parsing error:', LogCategory.AUDIO, error);
      alert(`JSON解析錯誤: ${error instanceof Error ? error.message : '未知錯誤'}`);
    }
  };

  return (
    <div>
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
  );
};

export default SynthPanel; 