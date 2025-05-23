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

