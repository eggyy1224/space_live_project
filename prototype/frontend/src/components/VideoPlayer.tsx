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

  const screenState = useStore((s) =>
    s.videoScreens.find((v) => v.id === screenId)
  );
  const setVideoScreen = useStore((s) => s.setVideoScreen);

  const height = useMemo(() => (width * 3) / 2, [width]);

  // 監聽螢幕播放狀態變化
  useEffect(() => {
    if (!videoRef.current || !screenState) return;
    
    if (screenState.playing) {
      videoRef.current.play().catch((error) => {
        console.log('VideoPlayer: Play failed', error);
        setVideoScreen(screenId, { playing: false });
      });
    } else {
      videoRef.current.pause();
    }
  }, [screenState?.playing, screenId, setVideoScreen]);

  // 監聽螢幕音量變化
  useEffect(() => {
    if (videoRef.current && screenState) {
      videoRef.current.volume = screenState.volume;
      console.log(`VideoPlayer ${screenId}: Volume set to ${screenState.volume}`);
    }
  }, [screenState?.volume, screenId]);

  // 監聽螢幕時間跳轉
  useEffect(() => {
    if (videoRef.current && screenState && Math.abs(videoRef.current.currentTime - screenState.currentTime) > 1.0) {
      videoRef.current.currentTime = screenState.currentTime;
      console.log(`VideoPlayer ${screenId}: Time jumped to ${screenState.currentTime}`);
    }
  }, [screenState?.currentTime, screenId]);

  // 監聽螢幕播放速度變化
  useEffect(() => {
    if (videoRef.current && screenState) {
      videoRef.current.playbackRate = screenState.playbackRate;
      console.log(`VideoPlayer ${screenId}: Playback rate set to ${screenState.playbackRate}`);
    }
  }, [screenState?.playbackRate, screenId]);

  useFrame(() => {
    if (texture && videoRef.current && !videoRef.current.paused) {
      texture.needsUpdate = true;
    }
  });

  // Follow runtime state
  useEffect(() => {
    if (!screenState?.visible && videoRef.current) {
      videoRef.current.pause();
      setVideoScreen(screenId, { playing: false });
    }
    if (screenState?.currentVideo) {
      const idx = playlist.indexOf(screenState.currentVideo);
      if (idx >= 0) setIndex(idx);
    }
  }, [screenState?.visible, screenState?.currentVideo, screenId, setVideoScreen]);

  useEffect(() => {
    if (!playlist || playlist.length === 0) {
      console.log('VideoPlayer: No playlist or empty playlist');
      return;
    }

    // Reset overlay state whenever a new video loads
    setAutoplayFailed(false);
    
    console.log(`VideoPlayer ${screenId}: Loading video`, playlist[index]);
    
    const video = document.createElement('video');
    videoRef.current = video;
    video.src = playlist[index];
    video.crossOrigin = 'anonymous';
    video.loop = false;
    video.playsInline = true;
    video.volume = screenState?.volume || 1;
    video.muted = false;
    
    let localTextureInstance: THREE.VideoTexture | null = null;

    const onLoadedMetadata = () => {
      console.log(`VideoPlayer ${screenId}: Video metadata loaded for`, video.src);
      const videoTexture = new THREE.VideoTexture(video);
      localTextureInstance = videoTexture;
      videoTexture.minFilter = THREE.LinearFilter;
      videoTexture.magFilter = THREE.LinearFilter;
      videoTexture.generateMipmaps = false;
      videoTexture.colorSpace = THREE.SRGBColorSpace;
      setTexture(videoTexture);
      
      // 更新螢幕的 duration 和重置 currentTime（不要強制把 hidden 螢幕設回 visible）
      setVideoScreen(screenId, { 
        duration: video.duration, 
        currentTime: 0,
        currentVideo: playlist[index],
        ...(screenState?.visible === false ? { visible: false } : { visible: true })
      });
      
      // 設定播放參數
      video.playbackRate = screenState?.playbackRate || 1;
      video.volume = screenState?.volume || 1;
      
      console.log(`VideoPlayer ${screenId}: Initial settings - rate: ${video.playbackRate}, volume: ${video.volume}`);
      
      // 嘗試自動播放
      video.play().then(() => {
        console.log(`VideoPlayer ${screenId}: Video started playing`);
        setVideoScreen(screenId, { playing: true });
        setAutoplayFailed(false);
      }).catch((error) => {
        console.log(`VideoPlayer ${screenId}: Autoplay failed`, error);
        setAutoplayFailed(true);
        setVideoScreen(screenId, { playing: false });
      });
    };

    const onVideoEnded = () => {
      console.log(`VideoPlayer ${screenId}: Video ended`);
      setVideoScreen(screenId, { playing: false });
      setTimeout(() => {
        setIndex((prevIndex) => (prevIndex + 1) % playlist.length);
      }, 2000);
    };

    const onTimeUpdate = () => {
      // 更新螢幕的 currentTime
      setVideoScreen(screenId, { currentTime: video.currentTime });
    };

    const onPlay = () => {
      console.log(`VideoPlayer ${screenId}: Video play event`);
      setVideoScreen(screenId, { playing: true });
      setAutoplayFailed(false);
    };

    const onPause = () => {
      console.log(`VideoPlayer ${screenId}: Video pause event`);
      setVideoScreen(screenId, { playing: false });
    };
    
    const onError = (error: Event) => {
      console.error(`VideoPlayer ${screenId}: Video load error for`, video.src, error);
    };
    
    video.addEventListener('loadedmetadata', onLoadedMetadata);
    video.addEventListener('ended', onVideoEnded);
    video.addEventListener('error', onError);
    video.addEventListener('timeupdate', onTimeUpdate);
    video.addEventListener('play', onPlay);
    video.addEventListener('pause', onPause);
    video.load();

    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      video.removeEventListener('ended', onVideoEnded);
      video.removeEventListener('error', onError);
      video.removeEventListener('timeupdate', onTimeUpdate);
      video.removeEventListener('play', onPlay);
      video.removeEventListener('pause', onPause);
      video.pause();
      video.src = '';
      if (videoRef.current === video) {
          videoRef.current = null;
      }
      if (localTextureInstance) {
        localTextureInstance.dispose();
      }
      setVideoScreen(screenId, { visible: false, currentVideo: '', playing: false });
    };
  }, [index, playlist, screenId, setVideoScreen, screenState?.playbackRate, screenState?.volume]);

  const handlePlay = () => {
    if (videoRef.current) {
      videoRef.current.play().then(() => {
        setVideoScreen(screenId, { playing: true });
        setAutoplayFailed(false);
      }).catch((error) => {
        console.log(`VideoPlayer ${screenId}: Manual play failed`, error);
      });
    }
  };
  

  if (!texture || !playlist || playlist.length === 0) {
    return null;
  }

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
      {autoplayFailed && (
        <mesh position={[0, 0, 0.1]}>
          <planeGeometry args={[width * 0.3, height * 0.1]} />
          <meshBasicMaterial color="red" transparent opacity={0.8} />
        </mesh>
      )}
    </group>
  );
};

export default VideoPlayer;
