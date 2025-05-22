import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useStore } from '../store';
import * as THREE from 'three';

const MusicBackground: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const bgmIntensity = useStore((s) => s.bgmIntensity);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.z += 0.001 + bgmIntensity * 0.02;
    }
  });

  return (
    <mesh ref={meshRef} position={[0, 0, -10]}>
      <torusKnotGeometry args={[3, 1, 100, 16]} />
      <meshStandardMaterial color={0x222244} emissive={0x222244} emissiveIntensity={0.5 + bgmIntensity} />
    </mesh>
  );
};

export default MusicBackground;
