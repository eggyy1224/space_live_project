import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import VideoPlayer from '../VideoPlayer';

test('render video player without crashing', () => {
  render(
    <Canvas>
      <VideoPlayer playlist={["/videos/space_live.mp4"]} />
    </Canvas>
  );
});
