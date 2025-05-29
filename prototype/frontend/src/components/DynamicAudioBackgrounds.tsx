import React from 'react';
import SpeechBackground from './SpeechBackground';
import VideoPlayer from './VideoPlayer';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';
import P5SpaceEffect from './P5SpaceEffect';
import { DANCE_VIDEOS, LIFESTYLE_VIDEOS, SPACE_EFFECT_VIDEOS, createMixedPlaylist } from '../config/resources';

// ==================== 螢幕配置 ====================

interface ScreenConfig {
  id: string;
  position: [number, number, number];
  width: number;
  playlist: string[];
  initialVideoIndex: number;
  speedRange: { min: number; max: number };
}

const screenConfigs: ScreenConfig[] = [
  { 
    id: 'screen1', 
    position: [-50, 25, -60],
    width: 30,
    // 螢幕1：主要播放舞蹈類影片，偶爾穿插生活類 - 慢速範圍
    playlist: createMixedPlaylist([DANCE_VIDEOS, LIFESTYLE_VIDEOS], [7, 3]),
    initialVideoIndex: Math.floor(Math.random() * 10),
    speedRange: { min: 0.2, max: 1.0 } // 慢速：0.2x - 1.0x
  },
  { 
    id: 'screen2', 
    position: [0, 35, -50],
    width: 30,
    // 螢幕2：主要播放生活類影片，偶爾穿插太空特效 - 正常範圍
    playlist: createMixedPlaylist([LIFESTYLE_VIDEOS, SPACE_EFFECT_VIDEOS, DANCE_VIDEOS], [6, 3, 1]),
    initialVideoIndex: Math.floor(Math.random() * 10),
    speedRange: { min: 0.6, max: 1.8 } // 正常：0.6x - 1.8x（與其他有重疊）
  },
  { 
    id: 'screen3', 
    position: [50, 20, -55],
    width: 30,
    // 螢幕3：主要播放太空特效，偶爾穿插其他類型 - 快速範圍
    playlist: createMixedPlaylist([SPACE_EFFECT_VIDEOS, DANCE_VIDEOS, LIFESTYLE_VIDEOS], [6, 2, 2]),
    initialVideoIndex: Math.floor(Math.random() * 10),
    speedRange: { min: 1.2, max: 3.0 } // 快速：1.2x - 3.0x
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
