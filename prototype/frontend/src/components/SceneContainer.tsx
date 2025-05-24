import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { HeadModel } from './HeadModel';
import DanceGroup from './DanceGroup';
import DynamicAudioBackgrounds from './DynamicAudioBackgrounds';
import { useStore } from '../store';
import * as THREE from 'three';

interface SceneContainerProps {
  headModelUrl: string;
  isHeadModelLoaded: boolean;
  showSpaceBackground: boolean;
  modelScale: [number, number, number];
}

// 新增全局燈光組件，使其隨著音樂變化
const DynamicLights = () => {
  const ambientLightRef = useRef<THREE.AmbientLight>(null);
  const directionalLightRef = useRef<THREE.DirectionalLight>(null);
  const bgmIntensity = useStore((s) => s.bgmIntensity);
  
  useFrame(() => {
    if (ambientLightRef.current) {
      // 讓環境光隨音樂強度變化（增加幅度）
      ambientLightRef.current.intensity = 0.3 + bgmIntensity * 5;
    }
    if (directionalLightRef.current) {
      // 讓方向光隨音樂強度變化（增加幅度）
      directionalLightRef.current.intensity = 1.2 + bgmIntensity * 8;
      
      // 讓燈光的顏色也隨著音樂強度變化（增加色彩變化的幅度）
      const baseColor = new THREE.Color(0xffffff);
      const accentColor = new THREE.Color(0xff44ff); // 更鮮豔的粉紫色
      directionalLightRef.current.color.copy(baseColor).lerp(accentColor, Math.min(1, bgmIntensity * 1.5));
    }
  });

  return (
    <>
      <ambientLight ref={ambientLightRef} intensity={0.5} />
      <directionalLight 
        ref={directionalLightRef}
        position={[10, 10, 5]} 
        intensity={1.5} 
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024} 
      />
    </>
  );
};

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
      {showSpaceBackground && (
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      )}
      <DynamicAudioBackgrounds />
      <DynamicLights />
      <Suspense fallback={null}>
        {(() => {
          // 調整頭部位置：移到圓圈中央
          const baseScale = 10;
          const basePosition: [number, number, number] = [0, -5, 0]; // 中央位置
          
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
          // 圓形軍隊陣列：100個人圍成圓圈
          const armyPosition: [number, number, number] = [0, -25, 0]; // 再往下移動更多
          return (
            <group position={armyPosition}>
              <DanceGroup 
                count={100} 
                scale={8} 
                enableFloating={false} 
                forceCircular={true}
                circleRadius={60}
              />
            </group>
          );
        })()}
      </Suspense>
      <OrbitControls
        makeDefault
        enablePan
        enableZoom
        enableRotate
        target={[0, 0.8, 0]}
        mouseButtons={{
          LEFT: THREE.MOUSE.PAN,
          MIDDLE: THREE.MOUSE.DOLLY,
          RIGHT: THREE.MOUSE.ROTATE,
        }}
      />
    </Canvas>
  );
};

export default SceneContainer; 