import React from 'react';
import BodyModel from './BodyModel';

interface DanceGroupProps {
  /**
   * Positions of each dancer. If not provided, will auto-generate based on count.
   */
  positions?: [number, number, number][];
  /** Scale applied to each dancer */
  scale?: number;
  /** Number of dancers to create. If positions are provided, this is ignored. */
  count?: number;
}

export type FormationType = 'circle' | 'grid' | 'line' | 'wall';

interface GeneratePositionsOptions {
  radius?: number;
  spacing?: number;
}

// 生成佈局的位置
export const generatePositions = (
  count: number, 
  formationType: FormationType,
  options: GeneratePositionsOptions = {}
): [number, number, number][] => {
  const positions: [number, number, number][] = [];
  const { radius = 50, spacing = 8 } = options;

  switch (formationType) {
    case 'circle': {
      const angleStep = (2 * Math.PI) / count;
      for (let i = 0; i < count; i++) {
        const angle = i * angleStep;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        positions.push([x, 0, z]);
      }
      break;
    }

    case 'line': {
      const startX = -((count - 1) * spacing) / 2;
      for (let i = 0; i < count; i++) {
        positions.push([startX + i * spacing, 0, 0]);
      }
      break;
    }

    case 'grid': {
      const cols = Math.ceil(Math.sqrt(count));
      const rows = Math.ceil(count / cols);
      
      let currentIndex = 0;
      for (let row = 0; row < rows && currentIndex < count; row++) {
        const currentRowCols = Math.min(cols, count - currentIndex);
        const startX = -((currentRowCols - 1) * spacing) / 2;
        
        for (let col = 0; col < currentRowCols; col++) {
          const x = startX + col * spacing;
          const z = (row - (rows - 1) / 2) * spacing;
          positions.push([x, 0, z]);
          currentIndex++;
        }
      }
      break;
    }

    case 'wall': {
      const cols = Math.ceil(Math.sqrt(count));
      const rows = Math.ceil(count / cols);
      
      let currentIndex = 0;
      for (let row = 0; row < rows && currentIndex < count; row++) {
        const currentRowCols = Math.min(cols, count - currentIndex);
        const startX = -((currentRowCols - 1) * spacing) / 2;
        
        for (let col = 0; col < currentRowCols; col++) {
          const x = startX + col * spacing;
          const y = (row - (rows - 1) / 2) * spacing;
          positions.push([x, y, 0]);
          currentIndex++;
        }
      }
      break;
    }

    default:
      // 默認返回空陣列或拋出錯誤
      break;
  }
  
  return positions;
};


const DanceGroup: React.FC<DanceGroupProps> = ({ 
  positions, 
  scale = 5,
}) => {
  // 如果沒有提供 positions，就不渲染任何東西
  if (!positions) {
    return null;
  }
  
  return (
    <>
      {positions.map((pos, idx) => (
        <group key={idx} position={pos} scale={scale}>
          <BodyModel />
        </group>
      ))}
    </>
  );
};

export default DanceGroup;

