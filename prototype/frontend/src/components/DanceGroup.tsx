import React from 'react';
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

const DanceGroup: React.FC<DanceGroupProps> = ({ 
  positions, 
  scale = 5, 
  count = 30,
  forceCircular,
  circleRadius
}) => {
  const finalPositions = positions || generatePositions(count, forceCircular, circleRadius);
  
  return (
    <>
      {finalPositions.map((pos, idx) => (
        <group key={idx} position={pos} scale={scale}>
          <BodyModel />
        </group>
      ))}
    </>
  );
};

export default DanceGroup;

