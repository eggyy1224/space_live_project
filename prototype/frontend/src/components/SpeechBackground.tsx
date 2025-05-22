import React, { useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useStore } from '../store';
import * as THREE from 'three';

const SpeechBackground: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const { viewport } = useThree();
  const audioAverageVolume = useStore((state) => state.audioAverageVolume);

  useFrame(() => {
    if (materialRef.current) {
      const baseColor = new THREE.Color(0x111133);
      materialRef.current.emissive.set(baseColor);
      const sensitivity = 10.0;
      let intensity = Math.pow(audioAverageVolume * sensitivity, 1.5);
      const current = materialRef.current.emissiveIntensity;
      intensity = THREE.MathUtils.lerp(current, intensity, 0.15);
      materialRef.current.emissiveIntensity = Math.max(0.05, intensity);
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -5]}>
      <planeGeometry args={[viewport.width * 1.5, viewport.height * 1.5]} />
      <meshStandardMaterial ref={materialRef} color={0x050510} emissive={0x111133} emissiveIntensity={0.1} metalness={0} roughness={1} />
    </mesh>
  );
};

export default SpeechBackground;
