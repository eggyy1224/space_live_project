import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AnimationCue } from '../../types/AudioTimeline';
import { AudioPlayerService } from '../../services/audioPlayer';
import { useStore } from '../../store';
import HeadService from '../../services/HeadService';
import logger, { LogCategory } from '../../utils/LogManager';

// 更新：歌曲數據結構，包含動畫線索
interface Song {
  id: string;
  name: string;
  url: string;
  animationCues?: AnimationCue[];
}

// 範例歌曲數據
const sampleSongs: Song[] = [
  {
    id: 'song1', 
    name: '範例歌曲 1 (快樂)', 
    url: '/audio/songs/song1.mp3',
    animationCues: [
      { time: 0.5, type: 'emotion', value: 'happy' },
      { time: 1.0, type: 'action', value: 'wave_hand' },
      { time: 2.0, type: 'viseme', value: 'A' },
      { time: 3.5, type: 'emotion', value: 'excited' },
      { time: 5.0, type: 'action', value: 'idle' },
    ]
  },
  {
    id: 'song2',
    name: '範例歌曲 2 (平靜)',
    url: '/audio/songs/song2.mp3',
    animationCues: [
      { time: 0.0, type: 'emotion', value: 'calm' },
      { time: 2.0, type: 'action', value: 'subtle_nod' },
      { time: 4.0, type: 'viseme', value: 'O' },
      { time: 6.0, type: 'emotion', value: 'neutral' },
    ]
  },
  {
    id: 'song3',
    name: '範例歌曲 3 (無動畫)',
    url: '/audio/songs/song3.mp3'
  },
  {
    id: 'moonlight', 
    name: '皎潔的滿月下', 
    url: '/audio/songs/皎潔的滿月下.mp3',
    animationCues: [
      { time: 0.0, type: 'emotion', value: 'neutral' },
      { time: 0.1, type: 'action', value: 'Idle' },
      { time: 2.0, type: 'action', value: 'LookAround' },
      { time: 5.0, type: 'emotion', value: 'happy' },
      { time: 8.0, type: 'action', value: 'PointingGesture' },
      { time: 15.0, type: 'emotion', value: 'excited' },
      { time: 15.1, type: 'action', value: 'Cheering' },
      { time: 25.0, type: 'action', value: 'ReachingOut' },
      { time: 35.0, type: 'action', value: 'LookAround' },
      { time: 45.0, type: 'action', value: 'FemaleDynamicPose' },
      { time: 55.0, type: 'emotion', value: 'neutral' },
      { time: 55.1, type: 'action', value: 'FemaleStandingPose' },
      { time: 65.0, type: 'emotion', value: 'happy' },
      { time: 65.1, type: 'action', value: 'Cheering' },
      { time: 75.0, type: 'action', value: 'PointingGesture' },
      { time: 85.0, type: 'action', value: 'Idle' },
      { time: 88.0, type: 'emotion', value: 'neutral' },
    ]
  },
];

interface SongLibraryPanelProps {
  globalVolume: number;
}

const SongLibraryPanel: React.FC<SongLibraryPanelProps> = ({ globalVolume }) => {
  const [playingSongId, setPlayingSongId] = useState<string | null>(null);
  const audioPlayerService = useRef(new AudioPlayerService()).current;
  const animationFrameRef = useRef<number | null>(null);
  const headService = useRef(HeadService.getInstance()).current;

  // --- Animation Control Logic ---
  const startAnimationLoop = useCallback(
    (song: Song, onEndCallback?: () => void) => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      // Check if the service instance and cues exist
      if (!audioPlayerService || !song.animationCues) return;

      const cues = [...song.animationCues].sort((a, b) => a.time - b.time);
      let cueIndex = 0;

      const loop = (currentTime: number) => {
        // Check if the service instance exists
        if (!audioPlayerService) { 
          console.log("Animation loop stopped: Player service not available");
          return;
        }
        // Get elapsed time using the service method
        const elapsedTime = audioPlayerService.getCurrentTime(); 

        // Process cues up to the current elapsed time
        while (cueIndex < cues.length && cues[cueIndex].time <= elapsedTime) {
          const cue = cues[cueIndex];
          console.log(`Processing cue: time=${cue.time}, type=${cue.type}, value=${cue.value}`);
          switch (cue.type) {
            case 'emotion':
              if (cue.value && typeof cue.value === 'string') {
                headService.applyPresetExpression(cue.value as string);
              }
              break;
            case 'action': // Handle action cues
              if (cue.value && typeof cue.value === 'string') {
                console.log(`Setting animation to: ${cue.value}`);
                useStore.getState().setCurrentAnimation(cue.value as string);
              }
              break;
            // Add other cue types here if needed
          }
          cueIndex++;
        }

        // Check if song has ended using the service method for duration
        const duration = audioPlayerService.getDuration();
        if (duration > 0 && elapsedTime >= duration - 0.1) { // Add a small buffer for end detection
            console.log("Song ended, stopping animation loop.");
            headService.applyPresetExpression('neutral'); // Reset emotion at the end
            useStore.getState().setCurrentAnimation('Idle'); // Reset animation to Idle
            if (onEndCallback) {
                onEndCallback();
            }
            animationFrameRef.current = null;
        // Check if the player is playing using the service method
        } else if (audioPlayerService.isAudioPlaying()) { 
          animationFrameRef.current = requestAnimationFrame(loop);
        } else {
          console.log("Animation loop stopped: Player is not playing");
          animationFrameRef.current = null;
        }
      };

      animationFrameRef.current = requestAnimationFrame(loop);
    },
    [audioPlayerService, headService] 
  );

  const stopAnimationLoop = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    // Reset animation states when loop stops
    useStore.getState().setAudioLipsyncTarget('jawOpen', 0);
    if (!useStore.getState().isSpeaking) {
       useStore.getState().setCurrentAnimation('Idle'); 
    }
    logger.debug('[SongLibraryPanel] Stopped animation loop.', LogCategory.ANIMATION);
  };
  // --- End Animation Control Logic ---

  useEffect(() => {
    // 監聽 AudioPlayerService 的播放結束事件
    const handleSongEnd = () => {
      logger.debug('[SongLibraryPanel] Song ended event received from AudioPlayerService.', LogCategory.AUDIO);
      setPlayingSongId(null);
      useStore.getState().setSpeaking(false);
      stopAnimationLoop();
    };
    audioPlayerService.addEventListener('end', handleSongEnd);

    // 清理函數
    return () => {
      audioPlayerService.removeEventListener('end', handleSongEnd);
      if (audioPlayerService.isAudioPlaying()) {
         audioPlayerService.stop();
      }
      useStore.getState().setSpeaking(false);
      stopAnimationLoop();
    };
  }, [audioPlayerService]);

  // 處理歌曲播放/停止
  const handlePlaySong = async (song: Song) => {
    if (playingSongId === song.id) {
      // 停止
      logger.info(`[SongLibraryPanel] 手動停止歌曲: ${song.name}`, LogCategory.AUDIO);
      audioPlayerService.stop();
      setPlayingSongId(null);
      useStore.getState().setSpeaking(false);
      stopAnimationLoop();
    } else {
      // 播放新歌曲
      try {
        logger.info(`[SongLibraryPanel] 開始播放歌曲: ${song.name}`, LogCategory.AUDIO);
        useStore.getState().setSpeaking(true);
        const success = await audioPlayerService.playAudio(song.url);
        if (success) {
          setPlayingSongId(song.id);
          if (song.animationCues && song.animationCues.length > 0) {
            startAnimationLoop(song);
          } else {
            stopAnimationLoop();
            logger.debug(`[SongLibraryPanel] Song ${song.name} has no animation cues. Relying on default lipsync if active.`, LogCategory.ANIMATION);
          }
        } else {
          logger.error(`[SongLibraryPanel] AudioPlayerService failed to play ${song.name}`, LogCategory.AUDIO);
          setPlayingSongId(null);
          useStore.getState().setSpeaking(false);
          stopAnimationLoop();
        }
      } catch (error) {
        logger.error(`[SongLibraryPanel] 播放歌曲失敗: ${song.name}`, LogCategory.AUDIO, error);
        setPlayingSongId(null);
        useStore.getState().setSpeaking(false);
        stopAnimationLoop();
      }
    }
  };
  
  // 停止所有歌曲播放
  const handleStopAllSongs = () => {
    logger.info(`[SongLibraryPanel] 停止所有歌曲播放`, LogCategory.AUDIO);
    audioPlayerService.stop();
    setPlayingSongId(null);
    useStore.getState().setSpeaking(false);
    stopAnimationLoop();
  };

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">歌曲列表</h3>
        {sampleSongs.length > 0 ? (
          <div className="space-y-2">
            {sampleSongs.map(song => (
              <div key={song.id} className="flex items-center justify-between p-2 bg-gray-700 rounded">
                <span className="text-sm truncate mr-2" title={song.name}>{song.name}</span>
                <button
                  onClick={() => handlePlaySong(song)}
                  className={`px-3 py-1 text-xs rounded transition-colors duration-200 ${
                    playingSongId === song.id
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-green-600 hover:bg-green-700'
                  } text-white`}
                >
                  {playingSongId === song.id ? '停止' : '播放'}
                </button>
              </div>
            ))}
            {/* 添加一個全局停止按鈕 */} 
            {playingSongId && (
               <button
                 onClick={handleStopAllSongs}
                 className="w-full mt-2 py-1 bg-red-700 hover:bg-red-800 rounded text-sm text-gray-200 transition-colors duration-200"
               >
                 停止播放
               </button>
            )}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">沒有可播放的歌曲。</p>
        )}
      </div>
    </div>
  );
};

export default SongLibraryPanel; 