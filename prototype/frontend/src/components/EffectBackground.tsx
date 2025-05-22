import React, { useEffect, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { useStore } from '../store';

interface Ripple {
  id: number;
  scale: number;
  opacity: number;
}

const EffectBackground: React.FC = () => {
  const trigger = useStore((s) => s.effectTrigger);
  const [ripples, setRipples] = useState<Ripple[]>([]);

  useEffect(() => {
    if (trigger > 0) {
      setRipples((prev) => [...prev, { id: trigger, scale: 0.1, opacity: 1 }]);
    }
  }, [trigger]);

  useFrame(() => {
    setRipples((prev) =>
      prev
        .map((r) => ({ ...r, scale: r.scale + 0.1, opacity: r.opacity - 0.005 }))
        .filter((r) => r.opacity > 0)
    );
  });

  return (
    <>
      {ripples.map((r) => (
        <mesh key={r.id} scale={r.scale} position={[0, 0, -5]}>
          <ringGeometry args={[0.5, 0.6, 32]} />
          <meshBasicMaterial transparent color={0xFFFF00} opacity={r.opacity} />
        </mesh>
      ))}
    </>
  );
};

export default EffectBackground;
