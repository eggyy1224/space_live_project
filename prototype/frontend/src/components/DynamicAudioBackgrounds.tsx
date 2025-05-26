import React from 'react';
import SpeechBackground from './SpeechBackground';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';
import P5SpaceEffect from './P5SpaceEffect';
import VideoPlayer from './VideoPlayer';

// Define the full playlist here
const FULL_PLAYLIST = [
  '/videos/太空打卡.mp4',
  '/videos/太空打卡2.mp4',
  '/videos/太空走秀.mp4',
  '/videos/太空走秀2.mp4',
  '/videos/火箭發射.mp4',
  '/videos/模擬星雲圖.mp4',
  '/videos/daily_life_1.mp4',
  '/videos/space_live_video_1.mp4',
  '/videos/space_live.mp4'
];

// Define configurations for multiple screens
interface ScreenConfig {
  id: string;
  position: [number, number, number];
  width: number;
  initialVideoIndex: number;
}

// Generate random initial video indices
const getRandomVideoIndex = () => Math.floor(Math.random() * FULL_PLAYLIST.length);

const screenConfigs: ScreenConfig[] = [
  { 
    id: 'screen1', 
    position: [-50, 25, -60],
    width: 30,
    initialVideoIndex: getRandomVideoIndex() 
  },
  { 
    id: 'screen2', 
    position: [0, 35, -50],
    width: 30,
    initialVideoIndex: getRandomVideoIndex() 
  },
  { 
    id: 'screen3', 
    position: [50, 20, -55],
    width: 30,
    initialVideoIndex: getRandomVideoIndex() 
  },
];

const DynamicAudioBackgrounds: React.FC = () => (
  <>
    <SpeechBackground />
    {/* Render multiple video players based on configs */}
    {screenConfigs.map(config => (
      <VideoPlayer 
        key={config.id}
        playlist={FULL_PLAYLIST}
        initialVideoIndex={config.initialVideoIndex}
        position={config.position}
        width={config.width}
      />
    ))}
    <MusicBackground />
    <EffectBackground />
    <P5SpaceEffect />
  </>
);

export default DynamicAudioBackgrounds;
