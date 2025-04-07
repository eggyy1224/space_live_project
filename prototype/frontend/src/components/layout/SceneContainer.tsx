import React, { Suspense } from 'react';
import { Model } from '../Model'; // 直接使用 Model 組件
import { Canvas } from '@react-three/fiber';
import { Html, OrbitControls, Stars } from '@react-three/drei';

interface SceneContainerProps {
  modelUrl: string;
  modelScale: number;
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  currentAnimation: string | null;
  showSpaceBackground: boolean;
  morphTargetDictionary: Record<string, number> | null;
  setMorphTargetData: (dictionary: Record<string, number> | null, influences: number[] | null) => void;
}

const SceneContainer: React.FC<SceneContainerProps> = React.memo(({
  modelUrl,
  modelScale,
  modelRotation,
  modelPosition,
  currentAnimation,
  showSpaceBackground,
  morphTargetDictionary,
  setMorphTargetData,
}) => {
  return (
    <Canvas className="scene-canvas" camera={{ position: [0, 0, 2], fov: 50 }}>
      <Suspense fallback={<Html center>加載模型中...</Html>}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <Model
          url={modelUrl}
          scale={modelScale}
          rotation={modelRotation}
          position={modelPosition}
          currentAnimation={currentAnimation ?? undefined}
          morphTargetDictionary={morphTargetDictionary}
          setMorphTargetData={setMorphTargetData}
        />
        <OrbitControls />
        {showSpaceBackground && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />}
      </Suspense>
    </Canvas>
  );
});

export default SceneContainer; 