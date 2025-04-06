import React, { useRef, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, useProgress } from '@react-three/drei';
import * as THREE from 'three';
import { Model } from './Model';

// 加載進度組件
function LoadingIndicator() {
  const { progress } = useProgress();
  return (
    <div style={{
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      color: 'white',
      padding: '10px 20px',
      borderRadius: '5px',
      zIndex: 1000
    }}>
      加載中... {progress.toFixed(0)}%
    </div>
  );
}

// 太空背景組件
function SpaceBackground() {
  return (
    <>
      <color attach="background" args={['#000']} />
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      <fog attach="fog" args={['#000', 20, 40]} />
    </>
  );
}

interface ModelViewerProps {
  modelUrl: string;
  modelScale: number;
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  currentAnimation: string | null;
  morphTargets: Record<string, number>;
  showSpaceBackground: boolean;
  setAvailableAnimations: (animations: string[]) => void;
  setMorphTargetDictionary: (dict: Record<string, number>) => void;
  setMorphTargetInfluences: (influences: number[]) => void;
  morphTargetDictionary: Record<string, number> | null;
  morphTargetInfluences: number[] | null;
}

const ModelViewer: React.FC<ModelViewerProps> = ({
  modelUrl,
  modelScale,
  modelRotation,
  modelPosition,
  currentAnimation,
  morphTargets,
  showSpaceBackground,
  setAvailableAnimations,
  setMorphTargetDictionary,
  setMorphTargetInfluences,
  morphTargetDictionary,
  morphTargetInfluences
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const lastModelUrl = useRef(modelUrl);
  
  // 監測模型URL變化
  useEffect(() => {
    if (lastModelUrl.current !== modelUrl) {
      setIsLoading(true);
      lastModelUrl.current = modelUrl;
      
      // 模型加載需要一些時間，這裡模擬等待
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [modelUrl]);

  return (
    <div className="canvas-container">
      {isLoading && <LoadingIndicator />}
      
      <Canvas camera={{ position: [0, 1, 5], fov: 50 }}>
        {showSpaceBackground ? (
          <SpaceBackground />
        ) : (
          <color attach="background" args={['#121212']} />
        )}
        
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <directionalLight position={[-10, -10, -5]} intensity={0.5} />
        
        <Model 
          url={modelUrl} 
          scale={modelScale}
          rotation={modelRotation}
          position={modelPosition}
          currentAnimation={currentAnimation}
          setAvailableAnimations={setAvailableAnimations}
          morphTargetDictionary={morphTargetDictionary}
          setMorphTargetDictionary={setMorphTargetDictionary}
          morphTargetInfluences={morphTargetInfluences}
          setMorphTargetInfluences={setMorphTargetInfluences}
          morphTargets={morphTargets}
        />
        <OrbitControls />
      </Canvas>
    </div>
  );
};

// 使用 React.memo 包裹導出的組件
export default React.memo(ModelViewer); 