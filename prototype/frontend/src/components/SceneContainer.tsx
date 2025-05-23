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
          // 左側隊伍：20個人，整齊排列
          const leftArmyPosition: [number, number, number] = [-25, 0, -10];
          return (
            <group position={leftArmyPosition}>
              <DanceGroup count={20} scale={4} enableFloating={false} />
            </group>
          );
        })()}
        {(() => {
          // 右側隊伍：20個人，整齊排列
          const rightArmyPosition: [number, number, number] = [25, 0, -10];
          return (
            <group position={rightArmyPosition}>
              <DanceGroup count={20} scale={4} enableFloating={false} />
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