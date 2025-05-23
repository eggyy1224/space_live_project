import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import DanceGroup from '../DanceGroup';

test('render dance group without crashing', () => {
  render(
    <Canvas>
      <DanceGroup />
    </Canvas>
  );
});

test('render dance group with custom count', () => {
  render(
    <Canvas>
      <DanceGroup count={5} />
    </Canvas>
  );
});

test('render dance group with custom positions', () => {
  const customPositions: [number, number, number][] = [
    [0, 0, 0],
    [2, 0, 0]
  ];
  
  render(
    <Canvas>
      <DanceGroup positions={customPositions} />
    </Canvas>
  );
});

