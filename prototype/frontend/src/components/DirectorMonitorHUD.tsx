import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../store';

const hudStyle = 'fixed top-2 right-2 bg-black/70 text-white text-xs p-2 rounded shadow z-50';
const songs = [
  'spacelive_theme.mp3',
  'spacelive_theme2.mp3',
  'heavy_metal_bgm_01.mp3',
  'heavy_metal_bgm_02.mp3',
  'space_live_country_theme1.mp3'
];
const videos = [
  '/videos/太空直播中.mp4',
  '/videos/太空熱舞.mp4',
  '/videos/星際小可愛.mp4'
];
const lightingPresets = ['idle', 'dramatic', 'calm'];
const cameraPresets = ['wide', 'closeUp', 'sideView'];

const DirectorMonitorHUD: React.FC = () => {
  const bgm = useStore((s) => s.bgm);
  const bgmPlaying = useStore((s) => s.bgmPlaying);
  const bgmTime = useStore((s) => s.bgmTime);
  const sfxActive = useStore((s) => s.sfxActive);
  const videoId = useStore((s) => s.videoId);
  const videoVisible = useStore((s) => s.videoVisible);
  const lightingPreset = useStore((s) => s.lightingPreset);
  const cameraPreset = useStore((s) => s.cameraPreset);
  const bgmVolume = useStore((s) => s.bgmVolume);
  const setBgmVolume = useStore((s) => s.setBgmVolume);
  const setRuntime = useStore((s) => s.setRuntime);
  const fps = useStore((s) => s.fps);
  const cpu = useStore((s) => s.cpu);

  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'd') setExpanded((v) => !v);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  if (import.meta.env.VITE_DIRECTOR !== 'true') return null;

  return (
    <motion.div
      className={hudStyle}
      animate={{ width: expanded ? 240 : 120 }}
    >
      <div>bgm: {bgm ?? '-'}</div>
      <div>time: {bgmTime.toFixed(1)}</div>
      <div>sfx: {sfxActive ? 'on' : 'off'}</div>
      <div>video: {videoVisible ? videoId : 'hidden'}</div>
      <div>light: {lightingPreset ?? '-'}</div>
      <div>camera: {cameraPreset ?? '-'}</div>
      <div>fps: {fps}</div>
      <div>cpu: {cpu.toFixed(2)}</div>
      {expanded && (
        <div className="mt-2 space-y-2">
          <div className="border-t border-white/30 pt-2">
            <div className="font-bold mb-1">BGM</div>
            <div className="flex items-center space-x-1 mb-1">
              <button onClick={() => setRuntime({ bgmPlaying: true })} disabled={bgmPlaying} className="px-1 bg-gray-600 rounded">▶</button>
              <button onClick={() => setRuntime({ bgmPlaying: false })} disabled={!bgmPlaying} className="px-1 bg-gray-600 rounded">⏸</button>
              <select value={bgm ?? ''} onChange={(e) => setRuntime({ bgm: e.target.value, bgmPlaying: true })} className="bg-gray-800 text-white text-xs rounded">
                <option value="" disabled>Select song</option>
                {songs.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <input type="range" min="0" max="100" value={bgmVolume * 100} onChange={(e) => setBgmVolume(Number(e.target.value) / 100)} className="w-full" />
          </div>
          <div className="border-t border-white/30 pt-2">
            <div className="font-bold mb-1">Video</div>
            <select value={videoId ?? ''} onChange={(e) => setRuntime({ videoId: e.target.value })} className="bg-gray-800 text-white text-xs rounded w-full mb-1">
              <option value="" disabled>Select video</option>
              {videos.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
            <label className="flex items-center space-x-1">
              <input type="checkbox" checked={videoVisible} onChange={(e) => setRuntime({ videoVisible: e.target.checked })} />
              <span>Visible</span>
            </label>
          </div>
          <div className="border-t border-white/30 pt-2">
            <div className="font-bold mb-1">Lighting</div>
            <select value={lightingPreset ?? ''} onChange={(e) => setRuntime({ lightingPreset: e.target.value })} className="bg-gray-800 text-white text-xs rounded w-full">
              <option value="" disabled>Select preset</option>
              {lightingPresets.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div className="border-t border-white/30 pt-2">
            <div className="font-bold mb-1">Camera</div>
            <select value={cameraPreset ?? ''} onChange={(e) => setRuntime({ cameraPreset: e.target.value })} className="bg-gray-800 text-white text-xs rounded w-full">
              <option value="" disabled>Select preset</option>
              {cameraPresets.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default DirectorMonitorHUD;
