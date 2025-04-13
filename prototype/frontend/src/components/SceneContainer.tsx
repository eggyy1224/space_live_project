import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { HeadModel } from './HeadModel';
import BodyModel from './BodyModel';

interface SceneContainerProps {
  headModelUrl: string;
  isHeadModelLoaded: boolean;
  showSpaceBackground: boolean;
  modelScale: [number, number, number];
}

const SceneContainer: React.FC<SceneContainerProps> = ({ 
  headModelUrl, 
  isHeadModelLoaded, 
  showSpaceBackground,
  modelScale,
}) => {
  // console.log('[SceneContainer] Rendering...');
  return (
    <Canvas 
      shadows 
      camera={{ position: [0, 0.5, 3], fov: 50 }}
      style={{ background: showSpaceBackground ? '#000010' : '#111a21' }}
    >
      {showSpaceBackground && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />}
      <ambientLight intensity={0.5} />
      <directionalLight 
        position={[10, 10, 5]} 
        intensity={1.5} 
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024} 
      />
      <Suspense fallback={null}>
        {(() => {
          // 只使用基礎縮放值和位置
          const baseScale = 10;
          const basePosition: [number, number, number] = [-22, -5, 0];
          
          return (
            <group position={basePosition} scale={baseScale}>
              <HeadModel 
                headModelUrl={headModelUrl}
                scale={modelScale}
              />
            </group>
          );
        })()}
        {(() => {
          return (
            <group scale={5}> 
              <BodyModel />
            </group>
          );
        })()}
      </Suspense>
      <OrbitControls 
        enablePan={true} 
        enableZoom={true} 
        enableRotate={true} 
        target={[0, 0.8, 0]}
      />
    </Canvas>
  );
};

export default SceneContainer; 