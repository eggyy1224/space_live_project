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
  playlist: string[];
  initialVideoIndex?: number;
  position?: [number, number, number];
  width?: number;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  playlist,
  initialVideoIndex = 0,
  position = [25, 10, -20],
  width = 20
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);
  const [index, setIndex] = useState(() => {
    return playlist && playlist.length > 0 ? initialVideoIndex % playlist.length : 0;
  });
  const [autoplayFailed, setAutoplayFailed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const height = useMemo(() => (width * 3) / 2, [width]);

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
      return;
    }
    
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
      const videoTexture = new THREE.VideoTexture(video);
      localTextureInstance = videoTexture;
      videoTexture.minFilter = THREE.LinearFilter;
      videoTexture.magFilter = THREE.LinearFilter;
      videoTexture.generateMipmaps = false;
      videoTexture.colorSpace = THREE.SRGBColorSpace;
      setTexture(videoTexture);
      
      video.play().catch(() => {
        setAutoplayFailed(true);
      });
    };

    const onVideoEnded = () => {
      setTimeout(() => {
        setIndex((prevIndex) => (prevIndex + 1) % playlist.length);
      }, 2000);
    };
    
    video.addEventListener('loadedmetadata', onLoadedMetadata);
    video.addEventListener('ended', onVideoEnded);
    video.load();

    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      video.removeEventListener('ended', onVideoEnded);
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

  if (!texture || !playlist || playlist.length === 0) {
    return null;
  }

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
            alignItems: 'center'
          }}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
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
          {autoplayFailed && (
            <div style={{ color: 'white', fontSize: '0.8rem', marginLeft: '1rem' }}>
              Click to play
            </div>
          )}
        </div>
      </Html>
    </group>
  );
};

export default VideoPlayer;
