import React, { useRef, useState, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import { useStore } from '../store';
import * as THREE from 'three';

// Renders a plane that reacts to audio volume and displays the latest
// speech text from the chat stream as a large floating caption.
const SpeechBackground: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const { viewport } = useThree();
  const audioAverageVolume = useStore((state) => state.audioAverageVolume);
  const speechText = useStore((state) => state.speechText);

  // Local state with small debounce to avoid flicker when rapid
  // updates arrive from the WebSocket/chat service.
  const [displayText, setDisplayText] = useState('');

  // Update displayed text when store changes
  useEffect(() => {
    const t = setTimeout(() => setDisplayText(speechText), 100);
    return () => clearTimeout(t);
  }, [speechText]);

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
    <group position={[0, 0, -15]}>
      <mesh ref={meshRef}>
        <planeGeometry args={[viewport.width * 1.5, viewport.height * 1.5]} />
        <meshStandardMaterial
          ref={materialRef}
          color={0x050510}
          emissive={0x111133}
          emissiveIntensity={0.1}
          metalness={0}
          roughness={1}
        />
      </mesh>
      {displayText && (
        <Text
          position={[0, 0, 0.1]}
          fontSize={viewport.width / 10}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {displayText}
        </Text>
      )}
    </group>
  );
};

export default SpeechBackground;
