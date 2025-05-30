import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
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
  screenId: string;
  playlist: readonly string[];
  initialVideoIndex?: number;
  position?: [number, number, number];
  width?: number;
  speedRange?: {
    min: number;
    max: number;
  };
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  screenId,
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

  // 從 store 獲取音量強度
  const bgmIntensity = useStore((state) => state.bgmIntensity);
  const screenState = useStore((s) =>
    s.videoScreens.find((v) => v.id === screenId)
  );
  const setVideoScreen = useStore((s) => s.setVideoScreen);
  const videoPlaying = useStore((s) => s.videoPlaying);
  const videoVolume = useStore((s) => s.videoVolume);
  const videoCurrentTime = useStore((s) => s.videoCurrentTime);
  const videoPlaybackRateStore = useStore((s) => s.videoPlaybackRate);
  const setRuntime = useStore((s) => s.setRuntime);

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

  useEffect(() => {
    if (!videoRef.current) return;
    if (videoPlaying) {
      videoRef.current.play().catch(() => {});
    } else {
      videoRef.current.pause();
    }
  }, [videoPlaying]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.volume = videoVolume;
    }
  }, [videoVolume]);

  useEffect(() => {
    if (videoRef.current && Math.abs(videoRef.current.currentTime - videoCurrentTime) > 0.3) {
      videoRef.current.currentTime = videoCurrentTime;
    }
  }, [videoCurrentTime]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = videoPlaybackRateStore;
    }
  }, [videoPlaybackRateStore]);


  useFrame(() => {
    if (texture && videoRef.current && !videoRef.current.paused) {
      texture.needsUpdate = true;
    }
  });

  // Follow runtime state
  useEffect(() => {
    if (!screenState?.visible && videoRef.current) {
      videoRef.current.pause();
    }
    if (screenState?.currentVideo) {
      const idx = playlist.indexOf(screenState.currentVideo);
      if (idx >= 0) setIndex(idx);
    }
  }, [screenState?.visible, screenState?.currentVideo]);

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
      setRuntime({ videoDuration: video.duration, videoCurrentTime: 0 });
      
      // 設定初始播放速度
      const initialPlaybackRate = calculatePlaybackRate(bgmIntensity);
      video.playbackRate = initialPlaybackRate;
      console.log('VideoPlayer: Set playback rate to', initialPlaybackRate);

      setVideoScreen(screenId, {
        currentVideo: playlist[index],
        visible: true,
      });
      
      video.play().then(() => {
        console.log('VideoPlayer: Video started playing');
        setRuntime({ videoPlaying: true });
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

    const onTimeUpdate = () => {
      setRuntime({ videoCurrentTime: video.currentTime });
    };
    
    const onError = (error: Event) => {
      console.error('VideoPlayer: Video load error for', video.src, error);
    };
    
    video.addEventListener('loadedmetadata', onLoadedMetadata);
    video.addEventListener('ended', onVideoEnded);
    video.addEventListener('error', onError);
    video.addEventListener('timeupdate', onTimeUpdate);
    video.load();

    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      video.removeEventListener('ended', onVideoEnded);
      video.removeEventListener('error', onError);
      video.removeEventListener('timeupdate', onTimeUpdate);
      video.pause();
      video.src = '';
      if (videoRef.current === video) {
          videoRef.current = null;
      }
      if (localTextureInstance) {
        localTextureInstance.dispose();
      }
      setVideoScreen(screenId, { visible: false, currentVideo: '' });
    };
  }, [index, playlist]);

  const handlePlay = () => {
    if (videoRef.current) {
      // 播放時也要設定正確的播放速度
      const currentPlaybackRate = calculatePlaybackRate(bgmIntensity);
      videoRef.current.playbackRate = currentPlaybackRate;
      videoRef.current.play();
      setRuntime({ videoPlaying: true });
      setAutoplayFailed(false);
    }
  };
  

  if (!texture || !playlist || playlist.length === 0) {
    return null;
  }

  const currentPlaybackRate = calculatePlaybackRate(bgmIntensity);

  return (
    <group position={position} visible={screenState?.visible}>
      <mesh onClick={handlePlay}>
        <planeGeometry args={[width, height]} />
        <meshBasicMaterial 
          map={texture}
          toneMapped={false}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh position={[0, 0, 0.2]} visible={false}>
        <planeGeometry args={[width, height * 0.6]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
    </group>
  );
};

export default VideoPlayer;
