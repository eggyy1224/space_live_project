import React from 'react';
import SpeechBackground from './SpeechBackground';
import VideoPlayer from './VideoPlayer';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';
import P5SpaceEffect from './P5SpaceEffect';
import { ALL_VIDEOS } from '../config/resources';

// ==================== 螢幕配置 ====================

interface ScreenConfig {
  id: string;
  position: [number, number, number];
  width: number;
  playlist: readonly string[];
  initialVideoIndex: number;
  speedRange: { min: number; max: number };
}

const screenConfigs: ScreenConfig[] = [
  { 
    id: 'screen1', 
    position: [-55, 30, -75],
    width: 50,
    playlist: ALL_VIDEOS,
    initialVideoIndex: Math.floor(Math.random() * ALL_VIDEOS.length),
    speedRange: { min: 0.2, max: 1.0 }
  },
  { 
    id: 'screen2', 
    position: [0, 30, -75],
    width: 50,
    playlist: ALL_VIDEOS,
    initialVideoIndex: Math.floor(Math.random() * ALL_VIDEOS.length),
    speedRange: { min: 0.6, max: 1.8 }
  },
  { 
    id: 'screen3', 
    position: [55, 30, -75],
    width: 50,
    playlist: ALL_VIDEOS,
    initialVideoIndex: Math.floor(Math.random() * ALL_VIDEOS.length),
    speedRange: { min: 1.2, max: 3.0 }
  },
];

const DynamicAudioBackgrounds: React.FC = () => (
  <>
    <SpeechBackground />
    {/* Render multiple video players based on configs */}
    {screenConfigs.map(config => (
      <VideoPlayer
        key={config.id}
        screenId={config.id}
        playlist={config.playlist}
        initialVideoIndex={config.initialVideoIndex}
        position={config.position}
        width={config.width}
        speedRange={config.speedRange}
      />
    ))}
    <MusicBackground />
    <EffectBackground />
    <P5SpaceEffect />
  </>
);

export default DynamicAudioBackgrounds;
