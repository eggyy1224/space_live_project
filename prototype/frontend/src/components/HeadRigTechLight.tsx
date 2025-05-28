import React, { useRef, useEffect, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { a, useSpring } from '@react-spring/three';
import * as THREE from 'three';
import { useStore } from '../store';
import { ShowState } from '../store/slices/showSlice';
import { createLaserMaterial } from '../utils/laserShader';
import { createArmGeometry } from '../utils/armGeometry';
import { EffectComposer, Bloom } from '@react-three/postprocessing';

export const lasersEnabledForState = (state: ShowState) => state === 'drop';

interface HeadRigTechLightProps {
  parentRef: React.RefObject<THREE.Group>;
}

const HeadRigTechLight: React.FC<HeadRigTechLightProps> = ({ parentRef }) => {
  const groupRef = useRef<THREE.Group>(null);
  const showState = useStore((s) => s.showState);
  const emitterCount = useStore((s) => s.emitterCount);
  const ringRadius = useStore((s) => s.ringRadius);

  useEffect(() => {
    const parent = parentRef.current;
    const child = groupRef.current;
    if (parent && child) {
      parent.add(child);
      return () => {
        parent.remove(child);
      };
    }
  }, [parentRef]);

  const armGeom = useMemo(() => createArmGeometry(), []);
  const laserGeom = useMemo(() => new THREE.CylinderGeometry(0.005, 0.005, 2), []);
  const armMat = useMemo(() => new THREE.MeshStandardMaterial({ color: 0x2266ff }), []);
  const laserMat = useMemo(() => createLaserMaterial(0x44ffff), []);

  useEffect(() => () => {
    armGeom.dispose();
    laserGeom.dispose();
    armMat.dispose();
    laserMat.dispose();
  }, [armGeom, laserGeom, armMat, laserMat]);

  const { armAngle, color, opacity } = useSpring({
    armAngle:
      showState === 'idle'
        ? 0
        : showState === 'buildUp'
        ? Math.PI / 6
        : showState === 'drop'
        ? Math.PI / 2
        : Math.PI / 4,
    color: showState === 'coolDown' ? '#00ffff' : '#2266ff',
    opacity: showState === 'coolDown' ? 0 : 1,
  });

  const rotationSpeed =
    showState === 'buildUp'
      ? (15 * Math.PI) / 180
      : showState === 'drop'
      ? (30 * Math.PI) / 180
      : 0;

  useFrame((state, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += rotationSpeed * delta;
    if (lasersEnabledForState(showState)) {
      const t = state.clock.elapsedTime;
      laserMat.uniforms.intensity.value = 0.5 + 0.5 * (Math.sin(t * 8 * Math.PI) > 0 ? 1 : 0);
    }
  });

  const angleStep = (2 * Math.PI) / emitterCount;

  return (
    <>
      <group ref={groupRef} position={[0, 0.5, 0]}>
        {Array.from({ length: emitterCount }).map((_, i) => (
          <group key={i} rotation={[0, i * angleStep, 0]}>
            <a.mesh
              geometry={armGeom}
              material={armMat}
              rotation-z={armAngle}
              position={[0, 0, ringRadius]}
              material-color={color}
              material-opacity={opacity}
            />
            {lasersEnabledForState(showState) && (
              <mesh
                geometry={laserGeom}
                material={laserMat}
                position={[0, 1.1, ringRadius + 0.1]}
                rotation={[Math.PI / 2, 0, 0]}
              />
            )}
          </group>
        ))}
      </group>
      {lasersEnabledForState(showState) && (
        <EffectComposer>
          <Bloom intensity={1.2} />
        </EffectComposer>
      )}
    </>
  );
};

export default HeadRigTechLight;
