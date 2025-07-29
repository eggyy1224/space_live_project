import React, { Suspense } from 'react';
import { HeadModel } from '../HeadModel'; // 直接使用 Model 組件
import { Canvas } from '@react-three/fiber';
import { Html, OrbitControls, Stars, Environment } from '@react-three/drei';
import * as THREE from 'three';

interface SceneContainerProps {
  headModelUrl: string;
  modelScale: number;
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  showSpaceBackground: boolean;
  morphTargetDictionary: Record<string, number> | null;
}

const SceneContainer: React.FC<SceneContainerProps> = React.memo(({
  headModelUrl,
  modelScale,
  modelRotation,
  modelPosition,
  showSpaceBackground,
  morphTargetDictionary,
}) => {
  return (
    <Canvas 
      className="scene-canvas" 
      camera={{ position: [0, 0, 2], fov: 50 }}
      gl={{ 
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.0,
        outputColorSpace: THREE.SRGBColorSpace
      }}
    >
      <Suspense fallback={<Html center>加載模型中...</Html>}>
        {/* 環境光照 - 自然照明設定 */}
        <Environment preset="studio" background={false} />
        <ambientLight intensity={1.5} />
        <directionalLight position={[50, 50, 50]} intensity={2} castShadow />
        <directionalLight position={[-50, 50, 50]} intensity={1.5} />
        <directionalLight position={[0, 100, 0]} intensity={1.8} />
        <pointLight position={[30, 30, 30]} intensity={15} decay={2} />
        <pointLight position={[-30, 30, 30]} intensity={15} decay={2} />
        
        {/* 聚光燈專門打在臉上 - 自然照明 */}
        <spotLight
          position={[0, 20, 40]}
          angle={0.8}
          penumbra={0.6}
          intensity={12}
          distance={200}
          castShadow
          target-position={[0, -10, 0]}
          color="#ffffff"
        />
        <spotLight
          position={[30, 10, 30]}
          angle={0.7}
          penumbra={0.5}
          intensity={10}
          distance={150}
          target-position={[0, -10, 0]}
          color="#fff5f0"
        />
        {/* 額外的大範圍補光 */}
        <spotLight
          position={[-30, 20, 35]}
          angle={0.9}
          penumbra={0.7}
          intensity={8}
          distance={150}
          target-position={[0, -10, 0]}
          color="#fffefc"
        />
        {/* HeadModel 暫時隱藏 */}
        {false && (
          <HeadModel
            headModelUrl={headModelUrl}
            scale={modelScale}
            rotation={modelRotation}
            position={modelPosition}
          />
        )}
        <OrbitControls
          makeDefault
          mouseButtons={{
            LEFT: THREE.MOUSE.PAN,
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.ROTATE,
          }}
        />
        {showSpaceBackground && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />}
      </Suspense>
    </Canvas>
  );
});

export default SceneContainer; 