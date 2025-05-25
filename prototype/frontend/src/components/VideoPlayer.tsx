import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

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
  /** playlist of video file names relative to /public/videos */
  playlist?: string[];
  /** position of the video plane in the scene */
  position?: [number, number, number];
  /** width of the plane; height is derived from 2:3 aspect ratio */
  width?: number;
}

const DEFAULT_PLAYLIST = [
  '/videos/space_live.mp4',
  '/videos/Drive_in_stormy.mp4'
];

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  playlist = DEFAULT_PLAYLIST,
  position = [25, 10, -20],
  width = 20
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);
  const [index, setIndex] = useState(0);
  const [autoplayFailed, setAutoplayFailed] = useState(false);

  const height = useMemo(() => (width * 3) / 2, [width]);

  // Update texture every frame when video is playing
  useFrame(() => {
    if (texture && videoRef.current && !videoRef.current.paused) {
      texture.needsUpdate = true;
    }
  });

  // load current video
  useEffect(() => {
    const video = document.createElement('video');
    videoRef.current = video;
    video.src = playlist[index];
    video.crossOrigin = 'anonymous';
    video.loop = false;
    video.muted = true; // Start muted to allow autoplay
    video.playsInline = true;
    
    // Create texture when video metadata is loaded
    video.addEventListener('loadedmetadata', () => {
      const videoTexture = new THREE.VideoTexture(video);
      videoTexture.minFilter = THREE.LinearFilter;
      videoTexture.magFilter = THREE.LinearFilter;
      videoTexture.generateMipmaps = false;
      videoTexture.colorSpace = THREE.SRGBColorSpace;
      setTexture(videoTexture);
      
      // Try to play
      video.play().catch(() => {
        setAutoplayFailed(true);
        video.muted = false; // Unmute if autoplay fails
      });
    });

    video.load();

    return () => {
      video.pause();
      video.src = '';
      if (texture) {
        texture.dispose();
      }
    };
  }, [index, playlist]);

  // handle video end -> next video after delay
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const handleEnded = () => {
      setTimeout(() => {
        setIndex((i) => (i + 1) % playlist.length);
      }, 5000);
    };
    video.addEventListener('ended', handleEnded);
    return () => video.removeEventListener('ended', handleEnded);
  }, [playlist.length]);

  const handlePlay = () => {
    if (videoRef.current) {
      videoRef.current.muted = false;
      videoRef.current.play();
      setAutoplayFailed(false);
    }
  };
  
  const handlePause = () => videoRef.current?.pause();
  
  const handleRestart = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
    }
  };
  
  const handleVolume = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (videoRef.current) {
      videoRef.current.volume = parseFloat(e.target.value);
    }
  };

  // Only render mesh when texture is ready
  if (!texture) {
    return null;
  }

  return (
    <group position={position}>
      <mesh onClick={handlePlay}>
        <planeGeometry args={[width, height]} />
        <meshBasicMaterial 
          map={texture}
          toneMapped={false}
          side={THREE.DoubleSide}
        />
      </mesh>
      {/* HTML controls overlay */}
      <Html position={[0, -height / 2 - 2, 0]} center>
        <div style={{ display: 'flex', gap: '0.5rem', background: '#0008', padding: '0.5rem', borderRadius: '4px' }}>
          <button onClick={handlePlay}>Play</button>
          <button onClick={handlePause}>Pause</button>
          <button onClick={handleRestart}>Restart</button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            defaultValue="1"
            onChange={handleVolume}
          />
        </div>
        {autoplayFailed && <div>Click video to start</div>}
      </Html>
    </group>
  );
};

export default VideoPlayer;
