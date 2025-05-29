import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { CameraManager, CameraPreset } from './CameraManager';

/**
 * React hook that creates a CameraManager instance bound to the given camera.
 * The manager's update method is called automatically each frame.
 */
export function useCameraManager(
  camera: THREE.PerspectiveCamera,
  presets: CameraPreset[] = [],
  initial?: string,
): CameraManager {
  const managerRef = useRef<CameraManager | null>(null);
  if (!managerRef.current) {
    managerRef.current = new CameraManager(camera, presets);
    if (initial) {
      managerRef.current.transitionTo(initial, 0);
    }
  }
  useFrame((_, delta) => {
    managerRef.current!.update(delta);
  });
  return managerRef.current;
}
