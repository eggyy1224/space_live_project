import React, { useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useStore } from '../store';
import * as THREE from 'three';

export const AudioReactiveBackground: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const { viewport } = useThree();

  // 從 Zustand store 讀取平均音量
  const audioAverageVolume = useStore((state) => state.audioAverageVolume);

  useFrame(() => {
    if (materialRef.current) {
      // 基本的發光顏色
      const baseEmissiveColor = new THREE.Color(0x111133); // 深藍紫色
      materialRef.current.emissive.set(baseEmissiveColor);

      // 將音量映射到發光強度
      // audioAverageVolume 通常在 0-1 範圍內，rms 可能需要放大
      // 可以根據實際效果調整 sensitivity
      const sensitivity = 10.0; // <-- 增加靈敏度
      let rawIntensity = audioAverageVolume * sensitivity;

      // 使用冪運算來拉大動態範圍，使漸層更明顯
      let mappedIntensity = Math.pow(rawIntensity, 1.5); // <-- 非線性映射

      // 平滑化處理，避免閃爍過於劇烈
      const currentIntensity = materialRef.current.emissiveIntensity;
      const lerpFactor = 0.15; // <-- 稍微增加 lerpFactor 使反應略快
      mappedIntensity = THREE.MathUtils.lerp(currentIntensity, mappedIntensity, lerpFactor);
      
      // 確保至少有一點基礎發光，或者根據需要調整最小值
      materialRef.current.emissiveIntensity = Math.max(0.05, mappedIntensity); // <-- 降低最小發光，或設為 mappedIntensity
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -5]} receiveShadow={false} castShadow={false}>
      <planeGeometry args={[viewport.width * 1.5, viewport.height * 1.5]} /> {/* 稍微放大以確保覆蓋 */}
      <meshStandardMaterial 
        ref={materialRef} 
        color={0x050510} // 非常暗的背景色
        emissive={0x111133} // 初始發光顏色
        emissiveIntensity={0.1} // 初始發光強度
        metalness={0}
        roughness={1}
      />
    </mesh>
  );
};

// 如果需要 default export:
// export default AudioReactiveBackground; 