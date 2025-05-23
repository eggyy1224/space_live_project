import React from 'react';
import BodyModel from './BodyModel';

interface DanceGroupProps {
  /**
   * Positions of each dancer. Defaults to three spaced positions.
   */
  positions?: [number, number, number][];
  /** Scale applied to each dancer */
  scale?: number;
}

const defaultPositions: [number, number, number][] = [
  [-3, 0, 0],
  [0, 0, 0],
  [3, 0, 0]
];

const DanceGroup: React.FC<DanceGroupProps> = ({ positions = defaultPositions, scale = 5 }) => (
  <>
    {positions.map((pos, idx) => (
      <group key={idx} position={pos} scale={scale}>
        <BodyModel />
      </group>
    ))}
  </>
);

export default DanceGroup;

