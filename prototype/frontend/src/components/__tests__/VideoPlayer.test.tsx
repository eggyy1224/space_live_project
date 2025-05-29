import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import VideoPlayer from '../VideoPlayer';
import { DANCE_VIDEOS } from '../../config/resources';

test('renders VideoPlayer in Canvas', () => {
  render(
    <Canvas>
      <VideoPlayer screenId="test" playlist={DANCE_VIDEOS.slice(0, 1)} />
    </Canvas>
  );
});
