import { CameraManager } from '../../camera/CameraManager';
import * as THREE from 'three';

test('camera manager transitions between presets', () => {
  const camera = new THREE.PerspectiveCamera();
  const mgr = new CameraManager(camera, [
    { name: 'a', position: [0, 0, 5], target: [0, 0, 0], fov: 50 },
    { name: 'b', position: [0, 1, 5], target: [0, 1, 0], fov: 40 },
  ]);
  mgr.transitionTo('b', 1);
  mgr.update(0.5);
  expect(camera.position.y).toBeCloseTo(0.5, 1);
  mgr.update(0.5);
  expect(camera.position.y).toBeCloseTo(1, 1);
});
