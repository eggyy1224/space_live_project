import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../store';

const hudStyle = 'fixed top-2 right-2 bg-black/70 text-white text-xs p-2 rounded shadow z-50';

const DirectorMonitorHUD: React.FC = () => {
  const bgm = useStore((s) => s.bgm);
  const bgmTime = useStore((s) => s.bgmTime);
  const sfxActive = useStore((s) => s.sfxActive);
  const videoId = useStore((s) => s.videoId);
  const videoVisible = useStore((s) => s.videoVisible);
  const lightingPreset = useStore((s) => s.lightingPreset);
  const cameraPreset = useStore((s) => s.cameraPreset);
  const fps = useStore((s) => s.fps);
  const cpu = useStore((s) => s.cpu);
  const gpu = useStore((s) => s.gpu);

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
      <div>gpu: {gpu}</div>
    </motion.div>
  );
};

export default DirectorMonitorHUD;
