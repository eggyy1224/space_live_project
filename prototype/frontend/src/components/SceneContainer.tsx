import React, { Suspense, useRef, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { HeadModel } from './HeadModel';
import DanceGroup from './DanceGroup';
import DynamicAudioBackgrounds from './DynamicAudioBackgrounds';
import { useStore } from '../store';
import * as THREE from 'three';
import { useCameraManager, CameraPreset } from '../camera';

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
      <SceneContent
        headModelUrl={headModelUrl}
        isHeadModelLoaded={isHeadModelLoaded}
        showSpaceBackground={showSpaceBackground}
        modelScale={modelScale}
      />
    </Canvas>
  );
};

// 將場景內容提取到一個新組件中，以便在 Canvas 內部使用 useThree
const SceneContent: React.FC<SceneContainerProps> = ({
  headModelUrl,
  isHeadModelLoaded,
  showSpaceBackground,
  modelScale,
}) => {
  const { camera } = useThree();
  
  const cameraPresets: CameraPreset[] = [
    { name: 'overview', position: [0, 20, 100], target: [0, 0, 0], fov: 50 },
    { name: 'head_close_up', position: [0, -3, 8], target: [0, -5, 0], fov: 40 }, // Y target 調整為 -5
    { name: 'dance_circle_view', position: [0, 50, 80], target: [0, -25, 0], fov: 60 },
    { name: 'side_view', position: [-80, 10, 0], target: [0, -10, 0], fov: 55 },
    { name: 'low_angle_head', position: [0, -7, 7], target: [0, -5, 0], fov: 45 }, // Y target 調整為 -5, position 微調
    // 新增鏡位
    { name: 'center_orbit_high_1', position: [15, 10, 15], target: [0, 0, 0], fov: 50 },
    { name: 'center_orbit_high_2', position: [-15, 10, 15], target: [0, 0, 0], fov: 50 },
    { name: 'center_orbit_low_1', position: [10, -2, 10], target: [0, 0, 0], fov: 45 },
    { name: 'center_orbit_low_2', position: [-10, -2, -10], target: [0, 0, 0], fov: 45 },
    { name: 'top_down_center', position: [0, 25, 0.1], target: [0, 0, 0], fov: 50 }, // 0.1 Z to avoid gimbal lock issues with lookAt if exactly on axis
    { name: 'dramatic_angle_1', position: [20, -5, -20], target: [0, -2, 0], fov: 60 },
    { name: 'dramatic_angle_2', position: [-20, 5, 20], target: [0, 0, 0], fov: 60 },
    { name: 'behind_head_looking_out', position: [0, -3, -5], target: [0, -3, 20], fov: 50 }, // 假設頭部在 [0,-5,0]
    { name: 'fly_by_left', position: [-50, 0, 10], target: [50, 0, 0], fov: 70 },
    { name: 'fly_by_right', position: [50, 0, 10], target: [-50, 0, 0], fov: 70 },
    { name: 'frontal_dynamic_low', position: [0, -10, 30], target: [0, 0, 0], fov: 50},
    { name: 'frontal_dynamic_high', position: [0, 15, 25], target: [0, 0, 0], fov: 45},
    { name: 'orbit_head_1', position: [10, -5, 3], target: [0, -5, 0], fov: 40},
    { name: 'orbit_head_2', position: [-10, -5, 3], target: [0, -5, 0], fov: 40},
    { name: 'full_shot_dancers', position: [0, 10, 120], target: [0, -20, 0], fov: 55},
  ];

  const cameraManager = useCameraManager(camera as THREE.PerspectiveCamera, cameraPresets, 'overview');
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const switchView = () => {
      const presetNames = cameraPresets.map(p => p.name);
      const randomPresetName = presetNames[Math.floor(Math.random() * presetNames.length)];
      cameraManager.transitionTo(randomPresetName, 2.5); // 2.5 秒轉場

      // 隨機設定下一次切換的時間 (5 到 10 秒)
      const randomInterval = Math.random() * 5000 + 5000;
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(switchView, randomInterval);
    };

    // 初始延遲後開始第一次切換
    const initialDelay = setTimeout(switchView, 5000); // 5秒後第一次切換

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      clearTimeout(initialDelay);
    };
  }, [cameraManager, cameraPresets]);


  return (
    <>
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
        target={[0, 0.8, 0]} // OrbitControls 的 target 可能需要根據當前 cameraManager 的 target 動態調整，或者由 cameraManager 完全接管
        mouseButtons={{
          LEFT: THREE.MOUSE.PAN,
          MIDDLE: THREE.MOUSE.DOLLY,
          RIGHT: THREE.MOUSE.ROTATE,
        }}
      />
    </>
  );
};

export default SceneContainer; 