import React, { useEffect, useState, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useStore } from '../store';
import * as THREE from 'three';

interface PhysicalRipple {
  id: number;
  scale: number;
  opacity: number;
  time: number;
  layers: number;
  rotationSpeed: number;
}

const EffectBackground: React.FC = () => {
  const trigger = useStore((s) => s.effectTrigger);
  const [ripples, setRipples] = useState<PhysicalRipple[]>([]);

  useEffect(() => {
    if (trigger > 0) {
      // 創建多層物理波紋
      setRipples((prev) => [...prev, { 
        id: trigger, 
        scale: 0.1, 
        opacity: 1,
        time: 0,
        layers: 3 + Math.floor(Math.random() * 3), // 3-5層波紋
        rotationSpeed: (Math.random() - 0.5) * 0.02 // 隨機旋轉速度
      }]);
    }
  }, [trigger]);

  useFrame((state, delta) => {
    setRipples((prev) =>
      prev
        .map((r) => ({ 
          ...r, 
          scale: r.scale + 0.08, // 稍微減慢擴散速度
          opacity: r.opacity - 0.003, // 減慢透明度衰減
          time: r.time + delta
        }))
        .filter((r) => r.opacity > 0)
    );
  });

  return (
    <>
      {ripples.map((ripple) => (
        <group key={ripple.id}>
          {/* 創建多層波紋效果 */}
          {Array.from({ length: ripple.layers }, (_, layerIndex) => {
            const layerDelay = layerIndex * 0.3;
            const layerScale = Math.max(0, ripple.scale - layerDelay);
            const layerOpacity = ripple.opacity * (1 - layerIndex * 0.2);
            
            if (layerScale <= 0) return null;
            
            return (
              <mesh 
                key={`${ripple.id}-layer-${layerIndex}`}
                scale={layerScale} 
                position={[0, 0, -5 - layerIndex * 0.1]}
                rotation={[0, 0, ripple.time * ripple.rotationSpeed + layerIndex * Math.PI / 4]}
              >
                <ringGeometry args={[0.4 + layerIndex * 0.1, 0.7 + layerIndex * 0.1, 64]} />
                <meshStandardMaterial 
                  transparent 
                  color={new THREE.Color().setHSL(0.05 + layerIndex * 0.04, 1.0, 0.55 + layerOpacity * 0.2)} // 吸積盤熾熱色調 (橘黃到黃)
                  emissive={new THREE.Color().setHSL(0.05 + layerIndex * 0.04, 1.0, 0.5 + layerOpacity * 0.15)}
                  emissiveIntensity={layerOpacity * 3} // 增強發光
                  opacity={Math.max(0, layerOpacity * 0.85)} // 調整透明度以看到層次
                  side={THREE.DoubleSide}
                  roughness={0.6} // 表面更粗糙
                  metalness={0.05} // 金屬感降低
                />
              </mesh>
            );
          })}
          
          {/* 中心爆發效果 -> 改為黑洞核心 */}
          <mesh 
            scale={ripple.scale * 0.3} 
            position={[0, 0, -4.8]} // 稍微靠前一點，確保在吸積盤內
          >
            <sphereGeometry args={[0.3, 32, 32]} /> {/* 可以稍微調整核心大小 */}
            <meshStandardMaterial 
              transparent={false} // 不透明
              color={0x000000} // 純黑色
              emissive={0x000000} // 無發光
              emissiveIntensity={0}
              opacity={1} // 完全不透明
              roughness={0.2} // 黑洞本身可以有點質感
              metalness={0}
            />
          </mesh>
        </group>
      ))}
    </>
  );
};

export default EffectBackground;
