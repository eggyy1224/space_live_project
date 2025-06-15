import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, useProgress, Environment, Stats } from '@react-three/drei';
import * as THREE from 'three';
import { HeadModel } from './HeadModel';

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
  morphTargets: Record<string, number>; // Dynamic targets from WS
  showSpaceBackground: boolean;
  morphTargetDictionary: Record<string, number> | null; 
  getManualMorphTargets: () => Record<string, number>;
  setMorphTargetData: (dictionary: Record<string, number> | null, influences: number[] | null) => void;
}

const ModelViewer: React.FC<ModelViewerProps> = React.memo(({
  modelUrl,
  modelScale,
  modelRotation,
  modelPosition,
  currentAnimation,
  morphTargets, // Dynamic targets
  showSpaceBackground,
  morphTargetDictionary, // Pass initial dict
  getManualMorphTargets, // Pass the function
  setMorphTargetData // Pass the new function
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
      
      <Canvas 
        camera={{ position: [0, 1, 5], fov: 50 }}
        gl={{ 
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.0,
          outputColorSpace: THREE.SRGBColorSpace
        }}
      >
        {showSpaceBackground ? (
          <SpaceBackground />
        ) : (
          <color attach="background" args={['#121212']} />
        )}
        
        {/* 環境光照 - 自然照明設定 */}
        <Environment preset="studio" background={false} />
        <ambientLight intensity={1.2} />
        <directionalLight position={[100, 100, 50]} intensity={1.8} castShadow />
        <directionalLight position={[-100, -100, -50]} intensity={1.2} />
        <directionalLight position={[0, 100, 0]} intensity={1.5} />
        <pointLight position={[50, 50, 50]} intensity={12} decay={2} />
        <pointLight position={[-50, 50, 50]} intensity={12} decay={2} />
        
        {/* 聚光燈專門打在臉上 - 自然照明 */}
        <spotLight
          position={[0, 40, 60]}
          angle={0.8}
          penumbra={0.6}
          intensity={12}
          distance={200}
          castShadow
          target-position={[0, 0, 0]}
          color="#ffffff"
        />
        <spotLight
          position={[40, 20, 40]}
          angle={0.7}
          penumbra={0.5}
          intensity={10}
          distance={150}
          target-position={[0, 0, 0]}
          color="#fff5f0"
        />
        {/* 額外的大範圍補光 */}
        <spotLight
          position={[-40, 30, 50]}
          angle={0.9}
          penumbra={0.7}
          intensity={8}
          distance={150}
          target-position={[0, 0, 0]}
          color="#fffefc"
        />
        
        <Suspense fallback={null}>
          <HeadModel 
            headModelUrl={modelUrl} 
            scale={modelScale}
            rotation={modelRotation}
            position={modelPosition}
          />
        </Suspense>
        <OrbitControls
          makeDefault
          mouseButtons={{
            LEFT: THREE.MOUSE.PAN,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.ROTATE,
          }}
        />
        <Stats />
      </Canvas>
    </div>
  );
});

export default ModelViewer; 