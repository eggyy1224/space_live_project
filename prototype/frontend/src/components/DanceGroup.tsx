import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Group } from 'three';
import BodyModel from './BodyModel';

interface DanceGroupProps {
  /**
   * Positions of each dancer. If not provided, will auto-generate based on count.
   */
  positions?: [number, number, number][];
  /** Scale applied to each dancer */
  scale?: number;
  /** Number of dancers to create (default: 30) */
  count?: number;
  /** Enable floating animation (default: true) */
  enableFloating?: boolean;
}

// 生成圓形或網格佈局的位置
const generatePositions = (count: number): [number, number, number][] => {
  const positions: [number, number, number][] = [];
  
  if (count <= 10) {
    // 少於等於10個：單排排列
    const spacing = 4;
    const startX = -(count - 1) * spacing / 2;
    for (let i = 0; i < count; i++) {
      positions.push([startX + i * spacing, 0, 0]);
    }
  } else if (count <= 20) {
    // 11-20個：兩排排列
    const spacing = 4;
    const frontRow = Math.ceil(count / 2);
    const backRow = count - frontRow;
    
    // 前排
    const frontStartX = -(frontRow - 1) * spacing / 2;
    for (let i = 0; i < frontRow; i++) {
      positions.push([frontStartX + i * spacing, 0, 2]);
    }
    
    // 後排
    const backStartX = -(backRow - 1) * spacing / 2;
    for (let i = 0; i < backRow; i++) {
      positions.push([backStartX + i * spacing, 0, -2]);
    }
  } else {
    // 超過20個：圓形佈局
    const radius = Math.max(12, count * 0.4); // 根據數量調整半徑
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      // 添加隨機的Y軸偏移，營造3D漂浮感
      const y = (Math.random() - 0.5) * 8;
      positions.push([x, y, z]);
    }
  }
  
  return positions;
};

// 單個漂浮舞者元件
interface FloatingDancerProps {
  position: [number, number, number];
  scale: number;
  index: number;
  enableFloating: boolean;
}

const FloatingDancer: React.FC<FloatingDancerProps> = ({ 
  position, 
  scale, 
  index, 
  enableFloating 
}) => {
  const groupRef = useRef<Group>(null);
  
  // 為每個舞者生成不同的漂浮參數
  const floatingParams = {
    // 不同的漂浮頻率
    yFrequency: 0.5 + (index * 0.1) % 0.8,
    // 不同的旋轉頻率
    rotationFrequency: 0.2 + (index * 0.05) % 0.4,
    // 不同的相位偏移
    yPhase: index * 0.5,
    rotationPhase: index * 0.3,
    // 漂浮幅度
    yAmplitude: 1.5 + (index % 3) * 0.5,
    rotationAmplitude: 0.1 + (index % 4) * 0.05,
  };

  useFrame((state) => {
    if (!groupRef.current || !enableFloating) return;
    
    const time = state.clock.getElapsedTime();
    
    // Y軸漂浮動畫
    const yOffset = Math.sin(time * floatingParams.yFrequency + floatingParams.yPhase) * floatingParams.yAmplitude;
    
    // 輕微的旋轉動畫，模擬失重漂浮
    const rotationY = Math.sin(time * floatingParams.rotationFrequency + floatingParams.rotationPhase) * floatingParams.rotationAmplitude;
    const rotationX = Math.cos(time * floatingParams.rotationFrequency * 0.7 + floatingParams.rotationPhase) * floatingParams.rotationAmplitude * 0.5;
    const rotationZ = Math.sin(time * floatingParams.rotationFrequency * 1.3 + floatingParams.rotationPhase) * floatingParams.rotationAmplitude * 0.3;
    
    // 應用位置和旋轉
    groupRef.current.position.set(
      position[0],
      position[1] + yOffset,
      position[2]
    );
    
    groupRef.current.rotation.set(rotationX, rotationY, rotationZ);
  });

  return (
    <group ref={groupRef} position={position} scale={scale}>
      <BodyModel />
    </group>
  );
};

const DanceGroup: React.FC<DanceGroupProps> = ({ 
  positions, 
  scale = 5, 
  count = 30,
  enableFloating = true 
}) => {
  const finalPositions = positions || generatePositions(count);
  
  return (
    <>
      {finalPositions.map((pos, idx) => (
        <FloatingDancer
          key={idx}
          position={pos}
          scale={scale}
          index={idx}
          enableFloating={enableFloating}
        />
      ))}
    </>
  );
};

export default DanceGroup;

