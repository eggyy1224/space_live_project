import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import * as THREE from 'three';
import HeadRigTechLight, { lasersEnabledForState } from '../HeadRigTechLight';

// Basic render test
test('renders tech light rig', () => {
  const parent = new THREE.Group();
  render(
    <Canvas>
      <HeadRigTechLight parentRef={{ current: parent }} />
    </Canvas>
  );
});

test('lasers enabled on drop state', () => {
  expect(lasersEnabledForState('drop')).toBe(true);
});
