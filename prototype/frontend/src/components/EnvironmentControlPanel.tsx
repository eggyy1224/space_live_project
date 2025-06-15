import React from 'react';
import { useStore } from '../store';
import { ENVIRONMENT_PRESETS, type EnvironmentPreset } from '../store/slices/roomSlice';

interface EnvironmentControlPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

export const EnvironmentControlPanel: React.FC<EnvironmentControlPanelProps> = ({
  isVisible,
  onClose,
}) => {
  // 從 store 獲取狀態和操作方法
  const environmentPreset = useStore((state) => state.environmentPreset);
  const environmentIntensity = useStore((state) => state.environmentIntensity);
  const environmentBackground = useStore((state) => state.environmentBackground);
  
  const setEnvironmentPreset = useStore((state) => state.setEnvironmentPreset);
  const setEnvironmentIntensity = useStore((state) => state.setEnvironmentIntensity);
  const setEnvironmentBackground = useStore((state) => state.setEnvironmentBackground);
  const resetEnvironmentSettings = useStore((state) => state.resetEnvironmentSettings);

  if (!isVisible) return null;

  // preset 顯示名稱映射
  const presetDisplayNames: Record<EnvironmentPreset, string> = {
    studio: '🎬 工作室',
    sunset: '🌅 夕陽',
    dawn: '🌄 黎明',
    night: '🌃 夜晚',
    warehouse: '🏭 倉庫',
    forest: '🌲 森林',
    apartment: '🏠 公寓',
    city: '🏙️ 城市',
    park: '🌳 公園',
    lobby: '🏛️ 大廳'
  };

  return (
    <div className="fixed top-4 right-4 w-80 bg-black bg-opacity-80 text-white p-4 rounded-lg shadow-lg z-50 max-h-[90vh] overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold flex items-center gap-2">
          ✨ 環境光照控制
        </h2>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-300 text-xl font-bold"
          aria-label="關閉環境光照控制面板"
        >
          ✕
        </button>
      </div>

      {/* 當前設定顯示 */}
      <div className="mb-4 p-3 bg-gray-800 rounded-lg">
        <div className="text-sm space-y-1">
          <div>當前環境: <span className="text-blue-300">{presetDisplayNames[environmentPreset]}</span></div>
          <div>光照強度: <span className="text-green-300">{environmentIntensity.toFixed(1)}</span></div>
          <div>背景顯示: <span className={environmentBackground ? 'text-green-300' : 'text-gray-400'}>
            {environmentBackground ? '✅ 開啟' : '❌ 關閉'}
          </span></div>
        </div>
      </div>

      {/* 環境預設選擇 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-3 flex items-center gap-2">
          🎨 環境預設
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {ENVIRONMENT_PRESETS.map((preset) => (
            <button
              key={preset}
              onClick={() => setEnvironmentPreset(preset)}
              className={`px-3 py-2 rounded text-sm transition-all duration-200 ${
                environmentPreset === preset
                  ? 'bg-blue-600 text-white shadow-lg scale-105'
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
              }`}
            >
              {presetDisplayNames[preset]}
            </button>
          ))}
        </div>
      </div>

      {/* 光照強度控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-3 flex items-center gap-2">
          💡 光照強度
        </h3>
        <div className="space-y-3">
          <input
            type="range"
            min="0.1"
            max="3.0"
            step="0.1"
            value={environmentIntensity}
            onChange={(e) => setEnvironmentIntensity(parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>0.1 (暗)</span>
            <span className="text-green-300 font-bold">{environmentIntensity.toFixed(1)}</span>
            <span>3.0 (亮)</span>
          </div>
          
          {/* 快速設定按鈕 */}
          <div className="flex gap-2">
            {[0.5, 1.0, 1.5, 2.0, 2.5].map((value) => (
              <button
                key={value}
                onClick={() => setEnvironmentIntensity(value)}
                className={`px-2 py-1 rounded text-xs transition-colors ${
                  Math.abs(environmentIntensity - value) < 0.1
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                {value}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 背景顯示控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-3 flex items-center gap-2">
          🖼️ 背景設定
        </h3>
        <label className="flex items-center gap-3 cursor-pointer p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors">
          <input
            type="checkbox"
            checked={environmentBackground}
            onChange={(e) => setEnvironmentBackground(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-600 border-gray-500 rounded focus:ring-blue-500"
          />
          <span className="text-sm">
            顯示環境作為場景背景
          </span>
        </label>
        <p className="text-xs text-gray-400 mt-2">
          開啟後環境圖案會顯示為背景，關閉則僅提供光照效果
        </p>
      </div>

      {/* 操作按鈕 */}
      <div className="flex gap-2 pt-3 border-t border-gray-700">
        <button
          onClick={resetEnvironmentSettings}
          className="flex-1 px-3 py-2 bg-gray-600 hover:bg-gray-500 rounded text-sm transition-colors"
        >
          🔄 重置設定
        </button>
        <button
          onClick={onClose}
          className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm transition-colors"
        >
          ✅ 完成
        </button>
      </div>
    </div>
  );
};

export default EnvironmentControlPanel; 