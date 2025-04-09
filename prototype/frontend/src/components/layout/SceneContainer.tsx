import React, { Suspense } from 'react';
import { HeadModel } from '../HeadModel'; // 直接使用 Model 組件
import { Canvas } from '@react-three/fiber';
import { Html, OrbitControls, Stars } from '@react-three/drei';

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
    <Canvas className="scene-canvas" camera={{ position: [0, 0, 2], fov: 50 }}>
      <Suspense fallback={<Html center>加載模型中...</Html>}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <HeadModel
          headModelUrl={headModelUrl}
          scale={modelScale}
          rotation={modelRotation}
          position={modelPosition}
        />
        <OrbitControls />
        {showSpaceBackground && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />}
      </Suspense>
    </Canvas>
  );
});

export default SceneContainer; 