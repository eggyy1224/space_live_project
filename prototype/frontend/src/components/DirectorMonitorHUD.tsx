import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../store';
import { 
  BGM_FILES, 
  ALL_VIDEOS,
  LIGHTING_PRESETS, 
  CAMERA_PRESETS,
  CAMERA_PRESET_DISPLAY_NAMES,
  EFFECT_FILES 
} from '../config/resources';

const hudStyle = 'fixed top-2 right-2 bg-black/70 text-white text-xs p-2 rounded shadow z-50';

const DirectorMonitorHUD: React.FC = () => {
  const bgm = useStore((s) => s.bgm);
  const bgmPlaying = useStore((s) => s.bgmPlaying);
  const bgmTime = useStore((s) => s.bgmTime);
  const sfxActive = useStore((s) => s.sfxActive);
  const lightingPreset = useStore((s) => s.lightingPreset);
  const cameraPreset = useStore((s) => s.cameraPreset);
  const randomMode = useStore((s) => s.randomMode);
  const bgmVolume = useStore((s) => s.bgmVolume);
  const effectVolume = useStore((s) => s.effectVolume);
  const setBgmVolume = useStore((s) => s.setBgmVolume);
  const setEffectVolume = useStore((s) => s.setEffectVolume);
  const setRuntime = useStore((s) => s.setRuntime);
  const triggerEffect = useStore((s) => s.triggerEffect);
  const fps = useStore((s) => s.fps);
  const cpu = useStore((s) => s.cpu);
  const videoScreens = useStore((s) => s.videoScreens);
  const setVideoScreen = useStore((s) => s.setVideoScreen);

  const [expanded, setExpanded] = useState(true);
  const [selectedEffect, setSelectedEffect] = useState<string>(EFFECT_FILES[0]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'd') setExpanded((v) => !v);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const handlePlayEffect = () => {
    console.log('Manual effect play requested:', selectedEffect);
    
    // 先清除之前的音效狀態，確保重新觸發
    setRuntime({ 
      selectedEffect: null,
      sfxActive: false 
    });
    
    // 使用 setTimeout 確保狀態更新後再設定新的音效
    setTimeout(() => {
      setRuntime({ 
        selectedEffect: selectedEffect,
        sfxActive: true 
      });
      triggerEffect();
      console.log('Manual effect triggered:', selectedEffect);
    }, 10);
  };

  const toggleRandomMode = () => {
    const newRandomMode = !randomMode;
    
    if (!newRandomMode) {
      // 關閉隨機模式時，重置 BGM 播放狀態，讓用戶能重新控制
      setRuntime({ 
        randomMode: newRandomMode,
        bgmPlaying: false  // 重置播放狀態，讓播放按鈕可以點擊
      });
    } else {
      // 開啟隨機模式時，只設定模式狀態
      setRuntime({ randomMode: newRandomMode });
    }
  };

  if (import.meta.env.VITE_DIRECTOR !== 'true') return null;

  return (
    <motion.div
      className={hudStyle}
      animate={{ width: expanded ? 280 : 120 }}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-bold">隨機模式</span>
        <button 
          onClick={toggleRandomMode}
          className={`px-2 py-1 text-xs rounded ${
            randomMode 
              ? 'bg-green-600 hover:bg-green-500 text-white' 
              : 'bg-gray-600 hover:bg-gray-500 text-white'
          }`}
        >
          {randomMode ? '開啟' : '關閉'}
        </button>
      </div>
      <div>bgm: {bgm ?? '-'}</div>
      <div>time: {bgmTime.toFixed(1)}</div>
      <div>sfx: {sfxActive ? 'on' : 'off'}</div>
      <div>screens: {videoScreens.filter(s => s.visible).length}/{videoScreens.length} active</div>
      <div>light: {lightingPreset ?? '-'}</div>
      <div>camera: {cameraPreset ?? '-'}</div>
      <div>fps: {fps}</div>
      <div>cpu: {cpu.toFixed(2)}</div>
      {expanded && (
        <div className="mt-2 space-y-2">
          {!randomMode ? (
            <>
              <div className="border-t border-white/30 pt-2">
                <div className="font-bold mb-1">BGM</div>
                <div className="flex items-center space-x-1 mb-1">
                  <button 
                    onClick={() => setRuntime({ bgmPlaying: true })} 
                    disabled={bgmPlaying} 
                    className="px-1 bg-gray-600 hover:bg-gray-500 disabled:opacity-50 rounded text-xs"
                  >
                    ▶
                  </button>
                  <button 
                    onClick={() => setRuntime({ bgmPlaying: false })} 
                    disabled={!bgmPlaying} 
                    className="px-1 bg-gray-600 hover:bg-gray-500 disabled:opacity-50 rounded text-xs"
                  >
                    ⏸
                  </button>
                  <select 
                    value={bgm ?? ''} 
                    onChange={(e) => setRuntime({ bgm: e.target.value, bgmPlaying: true })} 
                    className="bg-gray-800 text-white text-xs rounded flex-1"
                  >
                    <option value="" disabled>選擇音樂</option>
                    {BGM_FILES.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div className="text-xs text-gray-300 mb-1">音量: {Math.round(bgmVolume * 100)}%</div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={bgmVolume * 100} 
                  onChange={(e) => setBgmVolume(Number(e.target.value) / 100)} 
                  className="w-full h-1" 
                />
              </div>
              
              <div className="border-t border-white/30 pt-2">
                <div className="font-bold mb-1">音效 (SFX)</div>
                <div className="flex items-center space-x-1 mb-1">
                  <button 
                    onClick={handlePlayEffect}
                    className="px-2 py-1 bg-yellow-600 hover:bg-yellow-500 rounded text-xs"
                  >
                    播放
                  </button>
                  <select 
                    value={selectedEffect} 
                    onChange={(e) => setSelectedEffect(e.target.value)} 
                    className="bg-gray-800 text-white text-xs rounded flex-1"
                  >
                    {EFFECT_FILES.map((effect) => (
                      <option key={effect} value={effect}>
                        {effect.replace('.mp3', '')}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="text-xs text-gray-300 mb-1">音量: {Math.round(effectVolume * 100)}%</div>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={effectVolume * 100} 
                  onChange={(e) => setEffectVolume(Number(e.target.value) / 100)} 
                  className="w-full h-1" 
                />
              </div>
              
              <div className="border-t border-white/30 pt-2">
                <div className="font-bold mb-1">視訊牆</div>
                {videoScreens.map((screen) => (
                  <div
                    key={screen.id}
                    className="mb-2 last:mb-0 border-b last:border-b-0 border-white/20 pb-1"
                  >
                    <div className="font-bold mb-1 text-purple-300">{screen.id}</div>
                    <select
                      value={screen.currentVideo}
                      onChange={(e) =>
                        setVideoScreen(screen.id, { currentVideo: e.target.value })
                      }
                      className="bg-gray-800 text-white text-xs rounded w-full mb-1"
                    >
                      <option value="" disabled>
                        選擇影片
                      </option>
                      {ALL_VIDEOS.map((v) => (
                        <option key={v} value={v}>
                          {v.split('/').pop()?.replace('.mp4', '')}
                        </option>
                      ))}
                    </select>
                    <label className="flex items-center space-x-1">
                      <input
                        type="checkbox"
                        checked={screen.visible}
                        onChange={(e) =>
                          setVideoScreen(screen.id, { visible: e.target.checked })
                        }
                      />
                      <span>顯示</span>
                    </label>
                    <div className="mt-1 text-[10px] text-gray-400">
                      {screen.visible ? screen.currentVideo.split('/').pop() : 'hidden'}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="border-t border-white/30 pt-2">
                <div className="font-bold mb-1">燈光</div>
                <select 
                  value={lightingPreset ?? ''} 
                  onChange={(e) => setRuntime({ lightingPreset: e.target.value })} 
                  className="bg-gray-800 text-white text-xs rounded w-full"
                >
                  <option value="" disabled>選擇燈光</option>
                  {LIGHTING_PRESETS.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              
              <div className="border-t border-white/30 pt-2">
                <div className="font-bold mb-1">相機</div>
                <select 
                  value={cameraPreset ?? ''} 
                  onChange={(e) => setRuntime({ cameraPreset: e.target.value })} 
                  className="bg-gray-800 text-white text-xs rounded w-full"
                >
                  <option value="" disabled>選擇鏡位</option>
                  {CAMERA_PRESETS.map((preset) => (
                    <option key={preset.name} value={preset.name}>
                      {CAMERA_PRESET_DISPLAY_NAMES[preset.name] || preset.name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          ) : (
            <div className="border-t border-white/30 pt-2">
              <div className="text-center text-yellow-300 text-xs">
                🎲 隨機模式啟用中<br/>
                系統自動控制BGM、音效和鏡位<br/>
                關閉隨機模式即可手動控制
              </div>
              <div className="mt-2 space-y-1">
                <div className="text-xs text-gray-300">音量控制仍可使用：</div>
                <div>
                  <div className="text-xs text-gray-300 mb-1">BGM 音量: {Math.round(bgmVolume * 100)}%</div>
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value={bgmVolume * 100} 
                    onChange={(e) => setBgmVolume(Number(e.target.value) / 100)} 
                    className="w-full h-1" 
                  />
                </div>
                <div>
                  <div className="text-xs text-gray-300 mb-1">音效音量: {Math.round(effectVolume * 100)}%</div>
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value={effectVolume * 100} 
                    onChange={(e) => setEffectVolume(Number(e.target.value) / 100)} 
                    className="w-full h-1" 
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default DirectorMonitorHUD;
