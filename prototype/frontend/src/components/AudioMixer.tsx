import React from 'react';
import { useStore } from '../store';

const sliderClasses = 'w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer';

const AudioMixer: React.FC = () => {
  const bgmVolume = useStore((state) => state.bgmVolume);
  const effectVolume = useStore((state) => state.effectVolume);
  const ttsVolume = useStore((state) => state.ttsVolume);
  const setBgmVolume = useStore((state) => state.setBgmVolume);
  const setEffectVolume = useStore((state) => state.setEffectVolume);
  const setTtsVolume = useStore((state) => state.setTtsVolume);

  return (
    <div className="space-y-2">
      <div>
        <label className="text-xs text-gray-600 dark:text-gray-300">BGM 音量: {bgmVolume.toFixed(2)}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={bgmVolume}
          onChange={(e) => setBgmVolume(parseFloat(e.target.value))}
          className={sliderClasses}
        />
      </div>
      <div>
        <label className="text-xs text-gray-600 dark:text-gray-300">效果音量: {effectVolume.toFixed(2)}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={effectVolume}
          onChange={(e) => setEffectVolume(parseFloat(e.target.value))}
          className={sliderClasses}
        />
      </div>
      <div>
        <label className="text-xs text-gray-600 dark:text-gray-300">語音音量: {ttsVolume.toFixed(2)}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={ttsVolume}
          onChange={(e) => setTtsVolume(parseFloat(e.target.value))}
          className={sliderClasses}
        />
      </div>
    </div>
  );
};

export default AudioMixer;
