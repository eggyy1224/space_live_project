import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import VideoPlayer from '../VideoPlayer';

test('renders VideoPlayer in Canvas', () => {
  render(
    <Canvas>
      <VideoPlayer />
    </Canvas>
  );
});
