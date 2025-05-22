import { render } from '@testing-library/react';
import DynamicAudioBackgrounds from '../DynamicAudioBackgrounds';
import { Canvas } from '@react-three/fiber';

test('render dynamic audio backgrounds without crashing', () => {
  render(
    <Canvas>
      <DynamicAudioBackgrounds />
    </Canvas>
  );
});
