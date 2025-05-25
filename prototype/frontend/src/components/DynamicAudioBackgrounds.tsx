import React from 'react';
import SpeechBackground from './SpeechBackground';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';
import P5SpaceEffect from './P5SpaceEffect';
import VideoPlayer from './VideoPlayer';

// Define the full playlist here
const FULL_PLAYLIST = [
  '/videos/space_live.mp4',
  '/videos/Drive_in_stormy.mp4',
  '/videos/BirdmanTalk.mp4',
  '/videos/Birds.mp4',
  '/videos/Club_Scene.mp4',
  '/videos/fireworks.mp4',
  '/videos/grass_man.mp4',
  '/videos/Horse.mp4'
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
    position: [-40, 25, -60], 
    width: 30, 
    initialVideoIndex: getRandomVideoIndex() 
  },
  { 
    id: 'screen2', 
    position: [0, 35, -50],
    width: 40, 
    initialVideoIndex: getRandomVideoIndex() 
  },
  { 
    id: 'screen3', 
    position: [40, 20, -55],
    width: 25, 
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
