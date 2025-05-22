import React, { useRef, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { useStore } from '../store';
import * as THREE from 'three';

const NUM_PARTICLES = 7000;

const P5SpaceEffect: React.FC = () => {
  const pointsRef = useRef<THREE.Points>(null);
  const materialRef = useRef<THREE.PointsMaterial>(null);
  const bgmIntensity = useStore((s) => s.bgmIntensity);
  const { viewport } = useThree();

  const particles = useMemo(() => {
    const p = new Float32Array(NUM_PARTICLES * 3);
    const velocities = new Float32Array(NUM_PARTICLES * 3);
    const colors = new Float32Array(NUM_PARTICLES * 3);
    const initialSizes = new Float32Array(NUM_PARTICLES);

    for (let i = 0; i < NUM_PARTICLES; i++) {
      const i3 = i * 3;
      p[i3] = (Math.random() - 0.5) * viewport.width * 2.5;
      p[i3 + 1] = (Math.random() - 0.5) * viewport.height * 2.5;
      p[i3 + 2] = (Math.random() - 0.5) * 25;

      velocities[i3] = (Math.random() - 0.5) * 0.03;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.03;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.015;
      
      const baseColor = new THREE.Color(0x66ccff);
      baseColor.toArray(colors, i3);
      initialSizes[i] = Math.random() * 0.1 + 0.05;
    }
    return { positions: p, velocities, colors, initialSizes };
  }, [viewport.width, viewport.height]);

  const particleGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(particles.positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(particles.colors, 3));
    return geometry;
  }, [particles]);
  
  const timeRef = useRef(0);

  useFrame((state, delta) => {
    timeRef.current += delta;
    if (pointsRef.current && materialRef.current) {
      const positions = pointsRef.current.geometry.attributes.position as THREE.BufferAttribute;
      const colorsAttribute = pointsRef.current.geometry.attributes.color as THREE.BufferAttribute;

      const intensityFactor = 0.8 + bgmIntensity * 8;
      materialRef.current.size = (0.05 + bgmIntensity * 0.2) * (1 + Math.sin(timeRef.current * 2 + bgmIntensity * 5) * 0.3);
      
      const accentColor = new THREE.Color(0xff33aa);
      const baseColor = new THREE.Color(0x66ccff);

      for (let i = 0; i < NUM_PARTICLES; i++) {
        const i3 = i * 3;
        
        const speedMultiplier = intensityFactor * (1 + particles.initialSizes[i]);
        particles.positions[i3] += particles.velocities[i3] * speedMultiplier * delta * 80;
        particles.positions[i3 + 1] += particles.velocities[i3 + 1] * speedMultiplier * delta * 80;
        particles.positions[i3 + 2] += particles.velocities[i3 + 2] * speedMultiplier * delta * 40;

        const padding = 2;
        if (particles.positions[i3] > viewport.width + padding) particles.positions[i3] = -viewport.width - padding;
        if (particles.positions[i3] < -viewport.width - padding) particles.positions[i3] = viewport.width + padding;
        if (particles.positions[i3 + 1] > viewport.height + padding) particles.positions[i3 + 1] = -viewport.height - padding;
        if (particles.positions[i3 + 1] < -viewport.height - padding) particles.positions[i3 + 1] = viewport.height + padding;
        if (particles.positions[i3 + 2] > 12) particles.positions[i3 + 2] = -12;
        if (particles.positions[i3 + 2] < -12) particles.positions[i3 + 2] = 12;

        positions.setXYZ(i, particles.positions[i3], particles.positions[i3+1], particles.positions[i3+2]);
        
        const currentColor = new THREE.Color();
        currentColor.copy(baseColor).lerp(accentColor, Math.min(1, bgmIntensity * 2.5));
        
        const zFactor = (particles.positions[i3 + 2] / 12 + 1) / 2;
        const timeBrightnessFactor = (Math.sin(timeRef.current * 1.5 + i * 0.15) + 1) / 2 * 0.6 + 0.4;
        currentColor.multiplyScalar(zFactor * timeBrightnessFactor * (1 + bgmIntensity * 0.5));
        
        colorsAttribute.setXYZ(i, currentColor.r, currentColor.g, currentColor.b);
      }
      positions.needsUpdate = true;
      colorsAttribute.needsUpdate = true;
      pointsRef.current.rotation.z += bgmIntensity * 0.0025;
      pointsRef.current.rotation.x += bgmIntensity * 0.0005;
    }
  });

  return (
    <points ref={pointsRef} geometry={particleGeometry}>
      <pointsMaterial 
        ref={materialRef} 
        size={0.1}
        vertexColors 
        transparent
        opacity={0.6 + bgmIntensity * 0.4}
        sizeAttenuation
      />
    </points>
  );
};

export default P5SpaceEffect; 