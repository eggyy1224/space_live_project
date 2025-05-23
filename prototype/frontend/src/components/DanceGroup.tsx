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
  /** Force circular layout */
  forceCircular?: boolean;
  /** Radius for circular layout */
  circleRadius?: number;
}

// 生成圓形或網格佈局的位置
const generatePositions = (count: number, forceCircular?: boolean, circleRadius?: number): [number, number, number][] => {
  const positions: [number, number, number][] = [];
  
  // 如果強制圓形佈局或人數超過80個，使用圓形陣列
  if (forceCircular || count > 80) {
    const radius = circleRadius || Math.max(30, count * 0.8); // 動態調整半徑
    const angleStep = (2 * Math.PI) / count;
    
    for (let i = 0; i < count; i++) {
      const angle = i * angleStep;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      positions.push([x, 0, z]);
    }
    return positions;
  }
  
  if (count <= 10) {
    // 少於等於10個：單排排列
    const spacing = 6; // 增加間距
    const startX = -(count - 1) * spacing / 2;
    for (let i = 0; i < count; i++) {
      positions.push([startX + i * spacing, 0, 0]);
    }
  } else {
    // 11個以上：整齊的軍隊陣形
    let cols, rows;
    
    if (count <= 20) {
      // 20個以下：5列為主
      cols = 5;
      rows = Math.ceil(count / cols);
    } else if (count <= 50) {
      // 21-50個：10列為主，更寬的陣形
      cols = 10;
      rows = Math.ceil(count / cols);
    } else {
      // 50個以上：15列為主
      cols = 15;
      rows = Math.ceil(count / cols);
    }
    
    const spacingX = 8; // 列間距
    const spacingZ = 8; // 行間距
    
    let currentIndex = 0;
    for (let row = 0; row < rows && currentIndex < count; row++) {
      const currentRowCount = Math.min(cols, count - currentIndex);
      const startX = -(currentRowCount - 1) * spacingX / 2;
      
      for (let col = 0; col < currentRowCount; col++) {
        const x = startX + col * spacingX;
        const z = row * spacingZ;
        positions.push([x, 0, z]);
        currentIndex++;
      }
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
  enableFloating = true,
  forceCircular,
  circleRadius
}) => {
  const finalPositions = positions || generatePositions(count, forceCircular, circleRadius);
  
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

