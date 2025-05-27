import React from 'react';
import SpeechBackground from './SpeechBackground';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';
import P5SpaceEffect from './P5SpaceEffect';
import VideoPlayer from './VideoPlayer';

// 將影片分類，讓不同螢幕播放不同類型的內容
const DANCE_VIDEOS = [
  '/videos/太空熱舞3.mp4',
  '/videos/太空熱舞2.mp4',
  '/videos/太空熱舞.mp4',
  '/videos/太空辣妹跳舞.mp4',
  '/videos/太空走秀.mp4',
  '/videos/太空走秀2.mp4'
];

const LIFESTYLE_VIDEOS = [
  '/videos/太空瑜伽3.mp4',
  '/videos/太空瑜伽2.mp4',
  '/videos/太空瑜伽.mp4',
  '/videos/太空直播中.mp4',
  '/videos/太空泡水.mp4',
  '/videos/太空化妝.mp4',
  '/videos/太空打卡.mp4',
  '/videos/太空打卡2.mp4',
  '/videos/daily_life_1.mp4'
];

const SPACE_EFFECT_VIDEOS = [
  '/videos/火箭發射.mp4',
  '/videos/星際小可愛.mp4',
  '/videos/星際小籠包.mp4',
  '/videos/星際聽音樂.mp4',
  '/videos/黑洞.mp4',
  '/videos/模擬星雲圖.mp4',
  '/videos/太空巨乳.mp4',
  '/videos/太空史萊姆.mp4',
  '/videos/space_live_video_1.mp4',
  '/videos/space_live.mp4'
];

// 隨機打亂陣列的函數
const shuffleArray = (array: string[]) => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

// 混合不同類型影片的函數
const createMixedPlaylist = (categories: string[][], weights: number[]) => {
  const mixed: string[] = [];
  const shuffledCategories = categories.map(cat => shuffleArray(cat));
  
  // 根據權重比例混合影片
  const totalWeight = weights.reduce((sum, w) => sum + w, 0);
  const targetLength = Math.max(...shuffledCategories.map(cat => cat.length)) * 2;
  
  for (let i = 0; i < targetLength; i++) {
    const randomValue = Math.random() * totalWeight;
    let currentWeight = 0;
    
    for (let j = 0; j < categories.length; j++) {
      currentWeight += weights[j];
      if (randomValue <= currentWeight && shuffledCategories[j].length > 0) {
        const video = shuffledCategories[j].shift();
        if (video) {
          mixed.push(video);
          // 如果該類別用完了，重新打亂並補充
          if (shuffledCategories[j].length === 0) {
            shuffledCategories[j] = shuffleArray(categories[j]);
          }
        }
        break;
      }
    }
  }
  
  return mixed;
};

// Define configurations for multiple screens with different logic
interface ScreenConfig {
  id: string;
  position: [number, number, number];
  width: number;
  playlist: string[];
  initialVideoIndex: number;
}

const screenConfigs: ScreenConfig[] = [
  { 
    id: 'screen1', 
    position: [-50, 25, -60],
    width: 30,
    // 螢幕1：主要播放舞蹈類影片，偶爾穿插生活類
    playlist: createMixedPlaylist([DANCE_VIDEOS, LIFESTYLE_VIDEOS], [7, 3]),
    initialVideoIndex: Math.floor(Math.random() * 10)
  },
  { 
    id: 'screen2', 
    position: [0, 35, -50],
    width: 30,
    // 螢幕2：主要播放生活類影片，偶爾穿插太空特效
    playlist: createMixedPlaylist([LIFESTYLE_VIDEOS, SPACE_EFFECT_VIDEOS, DANCE_VIDEOS], [6, 3, 1]),
    initialVideoIndex: Math.floor(Math.random() * 10)
  },
  { 
    id: 'screen3', 
    position: [50, 20, -55],
    width: 30,
    // 螢幕3：主要播放太空特效，偶爾穿插其他類型
    playlist: createMixedPlaylist([SPACE_EFFECT_VIDEOS, DANCE_VIDEOS, LIFESTYLE_VIDEOS], [6, 2, 2]),
    initialVideoIndex: Math.floor(Math.random() * 10)
  },
];

const DynamicAudioBackgrounds: React.FC = () => (
  <>
    <SpeechBackground />
    {/* Render multiple video players based on configs */}
    {screenConfigs.map(config => (
      <VideoPlayer 
        key={config.id}
        playlist={config.playlist}
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
