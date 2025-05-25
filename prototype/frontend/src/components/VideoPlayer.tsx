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
  '/videos/Drive_in_stormy.mp4',
  '/videos/BirdmanTalk.mp4',
  '/videos/Birds.mp4',
  '/videos/Club_Scene.mp4',
  '/videos/fireworks.mp4',
  '/videos/grass_man.mp4',
  '/videos/Horse.mp4'
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
  const [isHovered, setIsHovered] = useState(false);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const height = useMemo(() => (width * 3) / 2, [width]);

  // Handle hover with delay
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
    }, 1500); // 800ms delay before hiding
  };

  // Update texture every frame when video is playing
  useFrame(() => {
    if (texture && videoRef.current && !videoRef.current.paused) {
      texture.needsUpdate = true;
    }
  });

  // load current video
  useEffect(() => {
    // Clean up previous texture
    if (texture) {
      texture.dispose();
      setTexture(null);
    }

    const video = document.createElement('video');
    videoRef.current = video;
    video.src = playlist[index];
    video.crossOrigin = 'anonymous';
    video.loop = false;
    video.playsInline = true;
    
    // Create texture when video metadata is loaded
    video.addEventListener('loadedmetadata', () => {
      const videoTexture = new THREE.VideoTexture(video);
      videoTexture.minFilter = THREE.LinearFilter;
      videoTexture.magFilter = THREE.LinearFilter;
      videoTexture.generateMipmaps = false;
      videoTexture.colorSpace = THREE.SRGBColorSpace;
      setTexture(videoTexture);
      
      // Set initial volume
      video.volume = 0.6;
      
      // Try to play
      video.play().catch(() => {
        setAutoplayFailed(true);
      });
    });

    // Handle video end
    const handleEnded = () => {
      setTimeout(() => {
        setIndex((prevIndex) => (prevIndex + 1) % playlist.length);
      }, 5000);
    };
    
    video.addEventListener('ended', handleEnded);
    video.load();

    return () => {
      video.removeEventListener('ended', handleEnded);
      video.pause();
      video.src = '';
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

  // Only render mesh when texture is ready
  if (!texture) {
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
      {/* Invisible interaction area for controls */}
      <mesh
        position={[0, 0, 0.2]}
        onPointerEnter={handleMouseEnter}
        onPointerLeave={handleMouseLeave}
        visible={false}
      >
        <planeGeometry args={[width, height * 0.6]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>
      {/* HTML controls overlay - positioned on the video */}
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
            defaultValue="0.6"
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
