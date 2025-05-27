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
    let videoAdded = false;
    
    for (let j = 0; j < categories.length; j++) {
      currentWeight += weights[j];
      if (randomValue <= currentWeight && shuffledCategories[j].length > 0) {
        const video = shuffledCategories[j].shift();
        if (video) {
          mixed.push(video);
          videoAdded = true;
          // 如果該類別用完了，重新打亂並補充
          if (shuffledCategories[j].length === 0) {
            shuffledCategories[j] = shuffleArray(categories[j]);
          }
        }
        break;
      }
    }
    
    // 如果沒有成功加入影片，從第一個有影片的類別中取一個
    if (!videoAdded) {
      for (let j = 0; j < shuffledCategories.length; j++) {
        if (shuffledCategories[j].length > 0) {
          const video = shuffledCategories[j].shift();
          if (video) {
            mixed.push(video);
            if (shuffledCategories[j].length === 0) {
              shuffledCategories[j] = shuffleArray(categories[j]);
            }
            break;
          }
        }
      }
    }
  }
  
  // 確保至少有一些影片
  if (mixed.length === 0) {
    // 如果混合失敗，直接使用第一個類別的所有影片
    mixed.push(...shuffleArray(categories[0]));
  }
  
  console.log('Generated playlist:', mixed.slice(0, 5)); // 只顯示前5個
  return mixed;
};

// Define configurations for multiple screens with different logic
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
