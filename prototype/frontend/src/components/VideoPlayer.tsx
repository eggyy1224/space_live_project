import React, { useEffect, useRef, useState } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

interface VideoPlayerProps {
  playlist: string[];
  position?: [number, number, number];
  rotation?: [number, number, number];
  scale?: [number, number, number];
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  playlist,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = [1, 1, 1]
}) => {
  const { viewport } = useThree();
  const [index, setIndex] = useState(0);
  const videoRef = useRef<HTMLVideoElement>();
  const textureRef = useRef<THREE.VideoTexture>();
  const materialRef = useRef<THREE.MeshBasicMaterial>(null);

  useEffect(() => {
    const video = document.createElement('video');
    video.crossOrigin = 'anonymous';
    video.loop = false;
    video.playsInline = true;
    videoRef.current = video;

    return () => {
      video.pause();
      textureRef.current?.dispose();
    };
  }, []);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const src = playlist[index];
    video.src = src;
    video.load();
    const handleEnded = () => {
      setTimeout(() => {
        setIndex((i) => (i + 1) % playlist.length);
      }, 5000);
    };
    video.addEventListener('ended', handleEnded);
    video.play();

    textureRef.current = new THREE.VideoTexture(video);
    textureRef.current.needsUpdate = true;
    textureRef.current.minFilter = THREE.LinearFilter;
    textureRef.current.magFilter = THREE.LinearFilter;
    textureRef.current.format = THREE.RGBFormat;

    if (materialRef.current) {
      materialRef.current.map = textureRef.current;
      materialRef.current.needsUpdate = true;
    }

    return () => {
      video.pause();
      video.removeEventListener('ended', handleEnded);
      textureRef.current?.dispose();
      textureRef.current = undefined;
    };
  }, [index, playlist]);

  useFrame(() => {
    if (textureRef.current) textureRef.current.needsUpdate = true;
  });

  const play = () => videoRef.current?.play();
  const pause = () => videoRef.current?.pause();
  const restart = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
    }
  };
  const setVolume = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (videoRef.current) {
      videoRef.current.volume = parseFloat(e.target.value);
    }
  };

  const width = viewport.width * 0.4;
  const height = viewport.height * 0.25;

  return (
    <group position={position} rotation={rotation} scale={scale}>
      <mesh>
        <planeGeometry args={[width, height]} />
        <meshBasicMaterial ref={materialRef} toneMapped={false} />
      </mesh>
      <Html position={[0, -height * 0.7, 0]} center>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={play}>Play</button>
          <button onClick={pause}>Pause</button>
          <button onClick={restart}>Restart</button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            defaultValue="1"
            onChange={setVolume}
          />
        </div>
      </Html>
    </group>
  );
};

export default VideoPlayer;
