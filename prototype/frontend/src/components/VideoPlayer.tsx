import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
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
  position = [35, 50, -70],
  width = 20
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const textureRef = useRef<THREE.VideoTexture>();
  const [index, setIndex] = useState(0);
  const [autoplayFailed, setAutoplayFailed] = useState(false);
  const { gl } = useThree();

  const height = useMemo(() => (width * 3) / 2, [width]);

  // load current video
  useEffect(() => {
    const video = videoRef.current ?? document.createElement('video');
    videoRef.current = video;
    video.src = playlist[index];
    video.crossOrigin = 'anonymous';
    video.loop = false;
    video.preload = 'auto';
    video.playsInline = true;
    video.load();

    const texture = textureRef.current ?? new THREE.VideoTexture(video);
    textureRef.current = texture;
    texture.needsUpdate = true;
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    texture.generateMipmaps = false;

    const attempt = video
      .play()
      .catch(() => {
        setAutoplayFailed(true);
      });

    return () => {
      video.pause();
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
    videoRef.current?.play();
    setAutoplayFailed(false);
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

  return (
    <group position={position}>
      <mesh onClick={handlePlay}>
        <planeGeometry args={[width, height]} />
        <meshBasicMaterial toneMapped={false}>
          {textureRef.current && <primitive attach="map" object={textureRef.current} />}
        </meshBasicMaterial>
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
