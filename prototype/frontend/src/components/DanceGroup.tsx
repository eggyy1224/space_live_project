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
      positions.push([x, 0, z]);
    }
  }
  
  return positions;
};

const DanceGroup: React.FC<DanceGroupProps> = ({ 
  positions, 
  scale = 5, 
  count = 30 
}) => {
  const finalPositions = positions || generatePositions(count);
  
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

