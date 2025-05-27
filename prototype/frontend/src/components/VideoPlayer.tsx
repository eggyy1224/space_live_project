import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { useStore } from '../store';

/**
 * VideoPlayer renders a plane with a video texture inside the 3D scene.
 * - Videos are loaded from the public/videos directory.
 * - Maintains a 2:3 aspect ratio by default.
 * - Automatically cycles through the playlist with a 5s delay between items.
 * - If autoplay is blocked, user must click the screen once to start playback.
 * - Basic controls (play, pause, restart, volume) are exposed via on-screen HTML controls.
 * - Playback speed is controlled by BGM intensity: higher volume = slower playback
 *
 * This component is designed to be lightweight. For performance, keep video
 * resolutions modest (720p or lower). Videos are preloaded and reused via a
 * single HTMLVideoElement and THREE.VideoTexture.
 */
interface VideoPlayerProps {
  playlist: string[];
  initialVideoIndex?: number;
  position?: [number, number, number];
  width?: number;
  speedRange?: {
    min: number;
    max: number;
  };
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  playlist,
  initialVideoIndex = 0,
  position = [25, 10, -20],
  width = 20,
  speedRange
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);
  const [index, setIndex] = useState(() => {
    return playlist && playlist.length > 0 ? initialVideoIndex % playlist.length : 0;
  });
  const [autoplayFailed, setAutoplayFailed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 從 store 獲取音量強度
  const bgmIntensity = useStore((state) => state.bgmIntensity);

  const height = useMemo(() => (width * 3) / 2, [width]);

  // 計算播放速度：音量大時播放慢，音量小時播放快
  const calculatePlaybackRate = (intensity: number) => {
    // intensity 通常在 0-1 之間
    // 使用傳入的速度範圍，如果沒有則使用預設值
    const defaultSpeedRange = { min: 0.3, max: 1.5 };
    const currentSpeedRange = speedRange || defaultSpeedRange;
    
    const minSpeed = currentSpeedRange.min;
    const maxSpeed = currentSpeedRange.max;
    
    // 反向映射：intensity 越大，速度越慢
    const normalizedIntensity = Math.min(Math.max(intensity, 0), 1);
    const speed = maxSpeed - (normalizedIntensity * (maxSpeed - minSpeed));
    
    // 加入一些平滑處理，避免速度變化太突兀
    return Math.round(speed * 10) / 10; // 四捨五入到小數點後一位
  };

  // 監聽音量變化並調整播放速度
  useEffect(() => {
    if (videoRef.current && !videoRef.current.paused) {
      const newPlaybackRate = calculatePlaybackRate(bgmIntensity);
      videoRef.current.playbackRate = newPlaybackRate;
    }
  }, [bgmIntensity]);

  const handleMouseEnter = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    hoverTimeoutRef.current = setTimeout(() => {
      setIsHovered(false);
    }, 800);
  };

  useFrame(() => {
    if (texture && videoRef.current && !videoRef.current.paused) {
      texture.needsUpdate = true;
    }
  });

  useEffect(() => {
    if (!playlist || playlist.length === 0) {
      console.log('VideoPlayer: No playlist or empty playlist');
      return;
    }
    
    console.log('VideoPlayer: Loading video', playlist[index], 'from playlist of', playlist.length, 'videos');
    
    const video = document.createElement('video');
    videoRef.current = video;
    video.src = playlist[index];
    video.crossOrigin = 'anonymous';
    video.loop = false;
    video.playsInline = true;
    video.volume = 0;
    video.muted = true;
    
    let localTextureInstance: THREE.VideoTexture | null = null;

    const onLoadedMetadata = () => {
      console.log('VideoPlayer: Video metadata loaded for', video.src);
      const videoTexture = new THREE.VideoTexture(video);
      localTextureInstance = videoTexture;
      videoTexture.minFilter = THREE.LinearFilter;
      videoTexture.magFilter = THREE.LinearFilter;
      videoTexture.generateMipmaps = false;
      videoTexture.colorSpace = THREE.SRGBColorSpace;
      setTexture(videoTexture);
      
      // 設定初始播放速度
      const initialPlaybackRate = calculatePlaybackRate(bgmIntensity);
      video.playbackRate = initialPlaybackRate;
      console.log('VideoPlayer: Set playback rate to', initialPlaybackRate);
      
      video.play().then(() => {
        console.log('VideoPlayer: Video started playing');
      }).catch((error) => {
        console.log('VideoPlayer: Autoplay failed', error);
        setAutoplayFailed(true);
      });
    };

    const onVideoEnded = () => {
      setTimeout(() => {
        setIndex((prevIndex) => (prevIndex + 1) % playlist.length);
      }, 2000);
    };
    
    const onError = (error: Event) => {
      console.error('VideoPlayer: Video load error for', video.src, error);
    };
    
    video.addEventListener('loadedmetadata', onLoadedMetadata);
    video.addEventListener('ended', onVideoEnded);
    video.addEventListener('error', onError);
    video.load();

    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      video.removeEventListener('ended', onVideoEnded);
      video.removeEventListener('error', onError);
      video.pause();
      video.src = '';
      if (videoRef.current === video) {
          videoRef.current = null;
      }
      if (localTextureInstance) {
        localTextureInstance.dispose();
      }
    };
  }, [index, playlist]);

  const handlePlay = () => {
    if (videoRef.current) {
      // 播放時也要設定正確的播放速度
      const currentPlaybackRate = calculatePlaybackRate(bgmIntensity);
      videoRef.current.playbackRate = currentPlaybackRate;
      videoRef.current.play();
      setAutoplayFailed(false);
    }
  };
  
  const handlePause = () => videoRef.current?.pause();
  
  const handleRestart = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      const currentPlaybackRate = calculatePlaybackRate(bgmIntensity);
      videoRef.current.playbackRate = currentPlaybackRate;
      videoRef.current.play();
    }
  };
  
  const handleVolume = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (videoRef.current) {
      videoRef.current.volume = parseFloat(e.target.value);
    }
  };

  if (!texture || !playlist || playlist.length === 0) {
    return null;
  }

  const currentPlaybackRate = calculatePlaybackRate(bgmIntensity);

  return (
    <group position={position}>
      <mesh 
        onClick={handlePlay}
        onPointerEnter={handleMouseEnter}
        onPointerLeave={handleMouseLeave}
      >
        <planeGeometry args={[width, height]} />
        <meshBasicMaterial 
          map={texture}
          toneMapped={false}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh
        position={[0, 0, 0.2]}
        onPointerEnter={handleMouseEnter}
        onPointerLeave={handleMouseLeave}
        visible={false}
      >
        <planeGeometry args={[width, height * 0.6]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      <Html position={[0, 0, 0.1]} center>
        <div 
          style={{ 
            display: 'flex',
            gap: '0.75rem',
            background: 'rgba(0, 0, 0, 0.7)',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            opacity: isHovered ? 1 : 0,
            transition: 'opacity 0.3s ease',
            pointerEvents: isHovered ? 'auto' : 'none',
            backdropFilter: 'blur(10px)',
            alignItems: 'center',
            flexDirection: 'column'
          }}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <button 
              onClick={handlePlay}
              style={{
                padding: '0.4rem 0.8rem',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '0.9rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              ▶️
            </button>
            <button 
              onClick={handlePause}
              style={{
                padding: '0.4rem 0.8rem',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '0.9rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              ⏸️
            </button>
            <button 
              onClick={handleRestart}
              style={{
                padding: '0.4rem 0.8rem',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '4px',
                color: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '0.9rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              🔄
            </button>
            <div style={{ width: '1px', height: '20px', background: 'rgba(255, 255, 255, 0.3)' }} />
            <span style={{ color: 'white', fontSize: '0.9rem' }}>🔊</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              defaultValue="0"
              onChange={handleVolume}
              style={{
                width: '80px',
                cursor: 'pointer',
                height: '4px'
              }}
            />
          </div>
          
          {/* 顯示當前播放速度和音量強度 */}
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            fontSize: '0.8rem', 
            color: 'rgba(255, 255, 255, 0.8)',
            marginTop: '0.5rem',
            flexDirection: 'column',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <span style={{ 
                color: currentPlaybackRate < 0.5 ? '#ff6b6b' : 
                       currentPlaybackRate > 2.0 ? '#4ecdc4' : '#ffd93d',
                fontWeight: 'bold'
              }}>
                速度: {currentPlaybackRate.toFixed(1)}x
              </span>
              <span>音量: {(bgmIntensity * 100).toFixed(0)}%</span>
            </div>
            <div style={{ 
              fontSize: '0.7rem', 
              color: 'rgba(255, 255, 255, 0.6)',
              textAlign: 'center'
            }}>
              {currentPlaybackRate <= 0.5 ? '🐌 慢動作' : 
               currentPlaybackRate <= 1.0 ? '🚶 正常' :
               currentPlaybackRate <= 1.5 ? '🏃 快速' :
               currentPlaybackRate <= 2.0 ? '🚀 高速' : '⚡ 超高速'}
              <br />
              <span style={{ fontSize: '0.6rem', opacity: 0.7 }}>
                範圍: {speedRange?.min || 0.3}x - {speedRange?.max || 1.5}x
              </span>
            </div>
          </div>
          
          {autoplayFailed && (
            <div style={{ color: 'white', fontSize: '0.8rem', marginTop: '0.5rem' }}>
              Click to play
            </div>
          )}
        </div>
      </Html>
    </group>
  );
};

export default VideoPlayer;
