import React, { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { useStore } from '../store';
import * as THREE from 'three';

// Global origin for particle effects
const SCENE_CENTER = new THREE.Vector3(0, 0, 0);

// 物理波紋組件 - 替代黃色粒子特效
interface PhysicalRippleProps {
  parentPosition: THREE.Vector3;
  bgmIntensity: number;
  crazyModeRef?: React.MutableRefObject<boolean>;
}

const PhysicalRipple: React.FC<PhysicalRippleProps> = ({ parentPosition, bgmIntensity, crazyModeRef }) => {
  const rippleGroupRef = useRef<THREE.Group>(null);
  const timeRef = useRef(0);
  const rippleRefs = useRef<THREE.Mesh[]>([]);
  const [rippleCount] = useState(5); // 5層波紋
  
  // 初始化波紋環
  const ripples = useMemo(() => {
    const rings: { radius: number; opacity: number; speed: number }[] = [];
    for (let i = 0; i < rippleCount; i++) {
      rings.push({
        radius: 1 + i * 2,
        opacity: 1 - (i * 0.15),
        speed: 0.8 + i * 0.2
      });
    }
    return rings;
  }, [rippleCount]);

  useFrame((state, delta) => {
    timeRef.current += delta;
    const isCrazyMode = crazyModeRef?.current || false;
    
    if (rippleGroupRef.current) {
      // 跟隨父物件位置
      rippleGroupRef.current.position.copy(parentPosition);
      
      // 波紋擴散動畫
      rippleRefs.current.forEach((ripple, index) => {
        if (ripple) {
          const baseRadius = ripples[index].radius;
          const waveIntensity = 1 + bgmIntensity * (isCrazyMode ? 8 : 4);
          
          // 波紋擴散效果
          const expansionFactor = 1 + Math.sin(timeRef.current * ripples[index].speed) * waveIntensity;
          const currentRadius = baseRadius * expansionFactor;
          
          ripple.scale.set(currentRadius, currentRadius, 1);
          
          // 透明度脈動
          const baseOpacity = ripples[index].opacity;
          const opacityPulse = Math.abs(Math.sin(timeRef.current * ripples[index].speed * 1.5));
          const finalOpacity = baseOpacity * (0.3 + opacityPulse * 0.7) * (0.5 + bgmIntensity * 2);
          
          if (ripple.material instanceof THREE.MeshStandardMaterial) {
            ripple.material.opacity = Math.min(1, finalOpacity);
            
            // 波紋顏色 - 藍白色調
            const baseColor = new THREE.Color(0x4488ff);
            const activeColor = new THREE.Color(0xffffff);
            const waveColor = baseColor.clone().lerp(activeColor, bgmIntensity * 2);
            
            if (isCrazyMode) {
              // 瘋狂模式下彩虹色
              const h = (timeRef.current * 0.5 + index * 0.2) % 1;
              waveColor.setHSL(h, 0.8, 0.6);
            }
            
            ripple.material.color.copy(waveColor);
            ripple.material.emissive.copy(waveColor);
            ripple.material.emissiveIntensity = bgmIntensity * (isCrazyMode ? 3 : 1.5);
          }
          
          // 旋轉效果
          ripple.rotation.z += delta * (0.2 + bgmIntensity * (isCrazyMode ? 2 : 0.5));
        }
      });
    }
  });

  return (
    <group ref={rippleGroupRef}>
      {ripples.map((_, index) => (
        <mesh
          key={`ripple-${index}`}
          ref={(el) => {
            if (el) rippleRefs.current[index] = el;
          }}
          rotation={[Math.PI / 2, 0, 0]} // 水平放置
        >
          <ringGeometry args={[0.8, 1.2, 32]} />
          <meshStandardMaterial
            color={0x4488ff}
            emissive={0x4488ff}
            emissiveIntensity={0.5}
            transparent
            opacity={0.7}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}
    </group>
  );
};

// 環繞粒子組件
interface OrbitingParticleProps {
  radius: number;
  speed: number;
  phase: number;
  parentPosition: THREE.Vector3;
  bgmIntensity: number;
  particleType?: 'sphere' | 'box' | 'torus' | 'cone'; // 增加更多形狀
  baseColor?: THREE.Color;
  crazyModeRef?: React.MutableRefObject<boolean>; // 接受瘋狂模式引用
}

const OrbitingParticle: React.FC<OrbitingParticleProps> = ({ 
  radius, 
  speed, 
  phase, 
  parentPosition, 
  bgmIntensity,
  particleType = 'sphere',
  baseColor = new THREE.Color(0x88aaff), // 改為淡藍色
  crazyModeRef
}) => {
  const particleRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(phase);
  
  // 隨機爆發參數
  const burstTimeRef = useRef(Math.random() * 10);
  const burstActiveRef = useRef(false);
  
  useFrame((state, delta) => {
    timeRef.current += delta * speed * (1 + bgmIntensity * 0.5);
    burstTimeRef.current += delta;
    
    // 偵測是否處於瘋狂模式
    const isCrazyMode = crazyModeRef?.current || false;
    
    // 隨機爆發效果
    if (bgmIntensity > 0.6 && Math.random() < 0.002 * (isCrazyMode ? 5 : 1)) {
      burstActiveRef.current = true;
      setTimeout(() => { burstActiveRef.current = false }, 300 + Math.random() * 300);
    }
    
    if (particleRef.current) {
      // 正常軌道運動，但在瘋狂模式或爆發時增加變異
      let r = radius * (1 + bgmIntensity * 0.2);
      
      // 爆發或瘋狂模式下的半徑變化
      if (burstActiveRef.current) {
        r *= 2 + Math.random() * 3;
      } else if (isCrazyMode) {
        r *= 1 + Math.sin(timeRef.current * 3) * 0.5;
      }
      
      // 計算基本軌道位置
      let x = Math.cos(timeRef.current) * r;
      let y = Math.sin(timeRef.current) * r;
      let z = Math.sin(timeRef.current * 1.5) * r * 0.4;
      
      // 瘋狂模式下增加混沌行為
      if (isCrazyMode) {
        x += Math.sin(timeRef.current * 5) * r * 0.2;
        y += Math.cos(timeRef.current * 6) * r * 0.2;
        z += Math.sin(timeRef.current * 4) * r * 0.3;
      }
      
      // 爆發效果
      if (burstActiveRef.current) {
        const explosionDir = new THREE.Vector3(
          Math.random() - 0.5,
          Math.random() - 0.5,
          Math.random() - 0.5
        ).normalize();
        
        x += explosionDir.x * 5 * bgmIntensity;
        y += explosionDir.y * 5 * bgmIntensity;
        z += explosionDir.z * 5 * bgmIntensity;
      }
      
      particleRef.current.position.x = parentPosition.x + x;
      particleRef.current.position.y = parentPosition.y + y;
      particleRef.current.position.z = parentPosition.z + z;
      
      // 粒子旋轉
      particleRef.current.rotation.x += 0.01 * (isCrazyMode ? 5 : 1);
      particleRef.current.rotation.y += 0.015 * (isCrazyMode ? 5 : 1);
      particleRef.current.rotation.z += 0.005 * (isCrazyMode ? 5 : 1);
      
      // 大小脈動 - 更加劇烈
      let pulseScale = 1 + Math.sin(timeRef.current * (particleType === 'box' ? 3 : 5)) * bgmIntensity * 0.6;
      
      if (burstActiveRef.current) {
        pulseScale = 0.1 + Math.random() * 3 * bgmIntensity;
      } else if (isCrazyMode) {
        pulseScale *= 1 + Math.sin(timeRef.current * 10) * 0.5;
      }
      
      particleRef.current.scale.set(pulseScale, pulseScale, pulseScale);

      if (particleRef.current.material instanceof THREE.MeshStandardMaterial) {
        // 增強發光和顏色變化
        let emissiveIntensity = 1 + bgmIntensity * 3;
        
        if (burstActiveRef.current) {
          emissiveIntensity = 5 + Math.random() * 5;
        } else if (isCrazyMode) {
          emissiveIntensity = 2 + Math.sin(timeRef.current * 20) * 4 * bgmIntensity;
        }
        
        particleRef.current.material.emissiveIntensity = emissiveIntensity;
        
        // 顏色變化
        const activeColor = baseColor.clone().multiplyScalar(1.5);
        
        if (isCrazyMode) {
          // 瘋狂模式下顏色快速變化
          const h = (timeRef.current * 0.1) % 1;
          const s = 0.8;
          const l = 0.6;
          activeColor.setHSL(h, s, l);
        }
        
        particleRef.current.material.emissive.copy(baseColor).lerp(activeColor, bgmIntensity * (isCrazyMode ? 2 : 1));
      }
    }
  });
  
  return (
    <mesh ref={particleRef}>
      {particleType === 'sphere' && <sphereGeometry args={[0.2, 12, 12]} />}
      {particleType === 'box' && <boxGeometry args={[0.3, 0.3, 0.3]} />}
      {particleType === 'torus' && <torusGeometry args={[0.2, 0.1, 8, 12]} />}
      {particleType === 'cone' && <coneGeometry args={[0.2, 0.4, 8]} />}
      <meshStandardMaterial 
        color={baseColor}
        emissive={baseColor}
        emissiveIntensity={1}
        roughness={0.5}
        metalness={0.2}
      />
    </mesh>
  );
};

// 漂浮的數位方塊組件
interface FloatingCubeProps {
  bgmIntensity: number;
  initialPosition: THREE.Vector3;
  index: number;
  crazyModeRef?: React.MutableRefObject<boolean>; // 接受瘋狂模式引用
}

const FloatingCube: React.FC<FloatingCubeProps> = ({ bgmIntensity, initialPosition, index, crazyModeRef }) => {
  const cubeRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(Math.random() * Math.PI * 2);
  const [cubeGeometry, setCubeGeometry] = useState<'box' | 'sphere' | 'tetrahedron'>('box');
  
  // 瘋狂行為計時器
  const crazyCubeTimerRef = useRef(0);
  const crazyCubeActiveRef = useRef(false);

  useFrame((state, delta) => {
    timeRef.current += delta * (0.3 + bgmIntensity * 0.5);
    crazyCubeTimerRef.current += delta;
    
    // 檢查是否處於瘋狂模式
    const isCrazyMode = crazyModeRef?.current || false;
    
    // 隨機個體瘋狂
    if (bgmIntensity > 0.5 && Math.random() < 0.003 * (isCrazyMode ? 5 : 1)) {
      crazyCubeActiveRef.current = true;
      setTimeout(() => { crazyCubeActiveRef.current = false }, 1000 + Math.random() * 2000);
      
      // 隨機改變形狀
      const shapes: ('box' | 'sphere' | 'tetrahedron')[] = ['box', 'sphere', 'tetrahedron'];
      setCubeGeometry(shapes[Math.floor(Math.random() * shapes.length)]);
    }
    
    if (cubeRef.current) {
      // 基本位置變化
      let yOffset = Math.sin(timeRef.current + index * 0.5) * (2 + bgmIntensity * 3);
      let xOffset = Math.cos(timeRef.current * 0.7 + index * 0.3) * (1 + bgmIntensity);
      
      // 瘋狂模式或個體瘋狂時的增強
      if (isCrazyMode || crazyCubeActiveRef.current) {
        yOffset *= 1.5 + Math.sin(timeRef.current * 10) * 0.5;
        xOffset *= 1.5 + Math.cos(timeRef.current * 8) * 0.5;
        
        // 添加隨機位置跳躍
        if (Math.random() < 0.05) {
          yOffset += (Math.random() - 0.5) * 10;
          xOffset += (Math.random() - 0.5) * 10;
        }
      }
      
      cubeRef.current.position.y = initialPosition.y + yOffset;
      cubeRef.current.position.x = initialPosition.x + xOffset;
      
      // Z 軸波動
      cubeRef.current.position.z = initialPosition.z + 
        (isCrazyMode || crazyCubeActiveRef.current ? 
          Math.sin(timeRef.current * 5) * 3 : 
          Math.sin(timeRef.current) * 0.5
        );
      
      // 旋轉行為
      const rotSpeed = {
        x: (0.005 + bgmIntensity * 0.01) * (index % 2 === 0 ? 1 : -1),
        y: (0.003 + bgmIntensity * 0.008) * (index % 3 === 0 ? 1 : -1),
        z: (0.002 + bgmIntensity * 0.005) * (index % 4 === 0 ? 1 : -1)
      };
      
      // 瘋狂旋轉
      if (isCrazyMode || crazyCubeActiveRef.current) {
        rotSpeed.x *= 5 + Math.sin(timeRef.current * 5) * 2;
        rotSpeed.y *= 5 + Math.cos(timeRef.current * 4) * 2;
        rotSpeed.z *= 5 + Math.sin(timeRef.current * 6) * 2;
      }
      
      cubeRef.current.rotation.x += rotSpeed.x;
      cubeRef.current.rotation.y += rotSpeed.y;
      cubeRef.current.rotation.z += rotSpeed.z;
      
      // 縮放行為
      let baseScale = 0.3 + bgmIntensity * 0.5;
      let scaleVariation = Math.sin(timeRef.current * 2 + index) * 0.1 * bgmIntensity;
      
      if (isCrazyMode || crazyCubeActiveRef.current) {
        baseScale *= 1 + Math.sin(timeRef.current * 10) * 0.5;
        scaleVariation *= 3;
        
        // 不均勻的縮放
        cubeRef.current.scale.set(
          baseScale + scaleVariation * Math.sin(timeRef.current * 5),
          baseScale + scaleVariation * Math.cos(timeRef.current * 6),
          baseScale + scaleVariation * Math.sin(timeRef.current * 7)
        );
      } else {
        cubeRef.current.scale.set(baseScale + scaleVariation, baseScale + scaleVariation, baseScale + scaleVariation);
      }

      if (cubeRef.current.material instanceof THREE.MeshStandardMaterial) {
        // 顏色和發光變化
        const baseC = new THREE.Color(0x3333ff);
        const activeC = new THREE.Color(0x88aaff);
        
        if (isCrazyMode || crazyCubeActiveRef.current) {
          // 瘋狂模式下彩虹色變化
          const h = (timeRef.current * 0.2 + index * 0.1) % 1;
          activeC.setHSL(h, 1, 0.5);
          
          cubeRef.current.material.color.copy(baseC).lerp(activeC, 0.5 + Math.sin(timeRef.current * 20) * 0.5);
          cubeRef.current.material.emissive.copy(baseC).lerp(activeC, 0.5 + Math.sin(timeRef.current * 15) * 0.5);
          cubeRef.current.material.emissiveIntensity = 2 + Math.sin(timeRef.current * 30) * 2;
        } else {
          cubeRef.current.material.color.copy(baseC).lerp(activeC, bgmIntensity);
          cubeRef.current.material.emissive.copy(baseC).lerp(activeC, bgmIntensity);
          cubeRef.current.material.emissiveIntensity = bgmIntensity * 2;
        }
        
        // 瘋狂模式下隨機切換 wireframe
        if ((isCrazyMode || crazyCubeActiveRef.current) && Math.random() < 0.01) {
          cubeRef.current.material.wireframe = !cubeRef.current.material.wireframe;
        }
      }
    }
  });

  return (
    <mesh ref={cubeRef} position={initialPosition}>
      {cubeGeometry === 'box' && <boxGeometry args={[1, 1, 1]} />}
      {cubeGeometry === 'sphere' && <sphereGeometry args={[0.7, 16, 16]} />}
      {cubeGeometry === 'tetrahedron' && <tetrahedronGeometry args={[0.8, 0]} />}
      <meshStandardMaterial 
        color={0x3333ff} 
        emissive={0x3333ff} 
        emissiveIntensity={0} 
        metalness={0.6} 
        roughness={0.3} 
      />
    </mesh>
  );
};

// 核心物體的幾何形狀類型
type GeometryType = 'torusKnot' | 'octahedron' | 'tetrahedron' | 'icosahedron';

// 語音喇叭組件 - 專門用於角色語音
interface VoiceSpeakerProps {
  bgmIntensity: number;
  musicSpeakerPosition: THREE.Vector3;
  outerRadius: number;
  innerRadius: number;
}

const VoiceSpeaker: React.FC<VoiceSpeakerProps> = ({ bgmIntensity, musicSpeakerPosition, outerRadius, innerRadius }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const timeRef = useRef(0);
  const audioAverageVolume = useStore((s) => s.audioAverageVolume); // 語音音量
  const speechIntensity = Math.min(audioAverageVolume * 8, 1.0); // 將音量轉換為語音強度
  
  // 語音喇叭的移動參數
  const voiceDriftParams = useMemo(() => ({
    speedX: (Math.random() - 0.5) * 0.015,
    speedZ: (Math.random() - 0.5) * 0.015,
    rotationSpeedBase: {
      x: (Math.random() - 0.5) * 0.002,
      y: (Math.random() - 0.5) * 0.003,
      z: (Math.random() - 0.5) * 0.001
    },
    basePosition: { x: 0, y: -23, z: 0 }
  }), []);
  
  const positionRef = useRef({ 
    x: voiceDriftParams.basePosition.x + (Math.random() - 0.5) * 40, 
    y: voiceDriftParams.basePosition.y, 
    z: voiceDriftParams.basePosition.z + (Math.random() - 0.5) * 40 
  });

  // 形狀變化狀態
  const [geometryType, setGeometryType] = useState<'cylinder' | 'cone' | 'dodecahedron' | 'octahedron'>('cylinder');
  const morphTimerRef = useRef(0);
  const lastMorphTimeRef = useRef(0);

  useFrame((state, delta) => {
    timeRef.current += delta;
    morphTimerRef.current += delta;
    
    // 根據語音強度隨機改變形狀
    if ((speechIntensity > 0.3 && Math.random() < 0.008) || 
        (morphTimerRef.current - lastMorphTimeRef.current > 6 + Math.random() * 4)) {
      const shapes: ('cylinder' | 'cone' | 'dodecahedron' | 'octahedron')[] = ['cylinder', 'cone', 'dodecahedron', 'octahedron'];
      const newShape = shapes[Math.floor(Math.random() * shapes.length)];
      setGeometryType(newShape);
      lastMorphTimeRef.current = morphTimerRef.current;
    }
    
    if (meshRef.current) {
      // 語音喇叭在圈圈內的移動邏輯
      const combinedIntensity = Math.max(speechIntensity, bgmIntensity * 0.3);
      
      positionRef.current.x += voiceDriftParams.speedX * (1 + combinedIntensity * 0.8);
      positionRef.current.z += voiceDriftParams.speedZ * (1 + combinedIntensity * 0.6);
      
      // 環形邊界檢測：確保在外圓內但不進入內圓禁區
      const currentDistance = Math.sqrt(positionRef.current.x ** 2 + positionRef.current.z ** 2);
      
      // 檢查是否超出外圓邊界
      if (currentDistance > outerRadius) {
        const normalizeX = positionRef.current.x / currentDistance;
        const normalizeZ = positionRef.current.z / currentDistance;
        
        voiceDriftParams.speedX = -voiceDriftParams.speedX * 1.2;
        voiceDriftParams.speedZ = -voiceDriftParams.speedZ * 1.2;
        
        positionRef.current.x = normalizeX * outerRadius * 0.9;
        positionRef.current.z = normalizeZ * outerRadius * 0.9;
      }
      
      // 檢查是否進入內圓禁區（頭部區域）
      if (currentDistance < innerRadius) {
        const normalizeX = positionRef.current.x / currentDistance;
        const normalizeZ = positionRef.current.z / currentDistance;
        
        // 強力推出禁區
        voiceDriftParams.speedX = normalizeX * 0.025;
        voiceDriftParams.speedZ = normalizeZ * 0.025;
        
        positionRef.current.x = normalizeX * innerRadius * 1.15;
        positionRef.current.z = normalizeZ * innerRadius * 1.15;
      }

      // 與音樂喇叭的互動 - 相互吸引和排斥
      const distanceToMusic = musicSpeakerPosition.distanceTo(new THREE.Vector3(positionRef.current.x, positionRef.current.y, positionRef.current.z));
      const interactionForce = 0.001;
      
      if (distanceToMusic < 15) {
        // 太近時排斥
        const repelDirection = new THREE.Vector3(positionRef.current.x, 0, positionRef.current.z)
          .sub(new THREE.Vector3(musicSpeakerPosition.x, 0, musicSpeakerPosition.z))
          .normalize();
        positionRef.current.x += repelDirection.x * interactionForce * 20;
        positionRef.current.z += repelDirection.z * interactionForce * 20;
      } else if (distanceToMusic > 35) {
        // 太遠時吸引
        const attractDirection = new THREE.Vector3(musicSpeakerPosition.x, 0, musicSpeakerPosition.z)
          .sub(new THREE.Vector3(positionRef.current.x, 0, positionRef.current.z))
          .normalize();
        positionRef.current.x += attractDirection.x * interactionForce * 10;
        positionRef.current.z += attractDirection.z * interactionForce * 10;
      }

      // 語音響應的跳動效果
      const voiceJumpFactor = (0.8 + speechIntensity * 3.0);
      const musicInfluence = bgmIntensity * 0.5;
      
      let voiceJumpX = Math.sin(timeRef.current * 2.2) * voiceJumpFactor;
      let voiceJumpZ = Math.cos(timeRef.current * 1.8) * voiceJumpFactor;
      let voiceJumpY = Math.sin(timeRef.current * 4.0) * (2 + speechIntensity * 4 + musicInfluence * 2);
      
      // 添加高頻語音脈動
      voiceJumpX += Math.sin(timeRef.current * 6.5) * speechIntensity * 2;
      voiceJumpZ += Math.cos(timeRef.current * 5.8) * speechIntensity * 2;
      voiceJumpY += Math.sin(timeRef.current * 8.0) * speechIntensity * 3;
      
      meshRef.current.position.set(
        positionRef.current.x + voiceJumpX,
        positionRef.current.y + voiceJumpY,
        positionRef.current.z + voiceJumpZ
      );
      
      // 語音響應的旋轉
      const rotationMultiplier = 1 + speechIntensity * 3 + musicInfluence;
      meshRef.current.rotation.x += (voiceDriftParams.rotationSpeedBase.x + speechIntensity * 0.04) * rotationMultiplier;
      meshRef.current.rotation.y += (voiceDriftParams.rotationSpeedBase.y + speechIntensity * 0.06) * rotationMultiplier;
      meshRef.current.rotation.z += (voiceDriftParams.rotationSpeedBase.z + speechIntensity * 0.03) * rotationMultiplier;
      
      // 語音響應的縮放
      let baseScale = 1.2;
      const scaleFactor = baseScale * (1 + speechIntensity * 1.5 + musicInfluence * 0.8);
      
      const voicePulse = 1 + Math.sin(timeRef.current * 5.0) * speechIntensity * 0.6;
      const musicPulse = 1 + Math.cos(timeRef.current * 3.5) * musicInfluence * 0.4;
      
      meshRef.current.scale.set(scaleFactor * voicePulse * musicPulse, scaleFactor * voicePulse * musicPulse, scaleFactor * voicePulse * musicPulse);
    }
    
    // 語音喇叭的材質動畫 - 帥氣的藍綠色系
    if (materialRef.current) {
      const baseColor = new THREE.Color(0x001133); // 深藍
      const activeColor = new THREE.Color(0x00ffaa); // 亮青綠
      const speechColor = new THREE.Color(0x0088ff); // 藍色
      
      // 根據語音和音樂強度混合顏色
      const mixedColor = baseColor.clone()
        .lerp(speechColor, speechIntensity * 2)
        .lerp(activeColor, bgmIntensity * 1.5);
      
      materialRef.current.color.copy(mixedColor);
      materialRef.current.emissive.copy(mixedColor);
      materialRef.current.emissiveIntensity = 0.5 + speechIntensity * 8 + bgmIntensity * 3;
      
      // 動態材質屬性
      materialRef.current.metalness = 0.8 + Math.sin(timeRef.current * 6) * 0.2;
      materialRef.current.roughness = 0.2 + Math.cos(timeRef.current * 4) * 0.3;
      
      // 語音活躍時的wireframe效果
      materialRef.current.wireframe = speechIntensity > 0.5;
    }
  });

  return (
    <mesh ref={meshRef}>
      {geometryType === 'cylinder' && <cylinderGeometry args={[0.8, 1.2, 2.5, 12]} />}
      {geometryType === 'cone' && <coneGeometry args={[1.0, 2.8, 8]} />}
      {geometryType === 'dodecahedron' && <dodecahedronGeometry args={[1.3, 0]} />}
      {geometryType === 'octahedron' && <octahedronGeometry args={[1.6, 1]} />}
      
      <meshStandardMaterial 
        ref={materialRef} 
        color={0x001133} 
        emissive={0x001133} 
        emissiveIntensity={0.5}
        metalness={0.8}
        roughness={0.2}
      />
    </mesh>
  );
};

const MusicBackground: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const bgmIntensity = useStore((s) => s.bgmIntensity);
  
  // 隨機變形計時器
  const morphTimerRef = useRef(0);
  const lastMorphTimeRef = useRef(0);
  
  // 控制隨機形狀變化
  const [geometryType, setGeometryType] = useState<GeometryType>('torusKnot');
  
  // 儲存當前位置的參考
  const currentPosition = useMemo(() => new THREE.Vector3(), []);
  const timeRef = useRef(0);
  
  // 瘋狂模式標誌
  const [crazyMode, setCrazyMode] = useState(false);
  const crazyCooldownRef = useRef(0);

  // 主物件漂流參數 - 修改為在舞者圈圈內跳動
  const driftParams = useMemo(() => ({
    speedX: (Math.random() - 0.5) * 0.02, // 初始化 X 方向速度
    speedY: 0,
    speedZ: (Math.random() - 0.5) * 0.02, // 初始化 Z 方向速度
    rotationSpeedBase: {
      x: (Math.random() - 0.5) * 0.001,
      y: (Math.random() - 0.5) * 0.001,
      z: (Math.random() - 0.5) * 0.001
    },
    positionOffset: { x: SCENE_CENTER.x, y: -23, z: SCENE_CENTER.z }, // 移動到舞者圈圈高度
    outerRadius: 60, // 舞者圈圈的半徑（外圓）
    innerRadius: 15  // 頭部禁區半徑（內圓）
  }), []);
  
  const positionRef = useRef({ x: driftParams.positionOffset.x, y: driftParams.positionOffset.y, z: driftParams.positionOffset.z });

  // 新增：漂浮方塊的初始位置
  const floatingCubesPositions = useMemo(() => {
    const positions: THREE.Vector3[] = [];
    for (let i = 0; i < 8; i++) {
      positions.push(
        new THREE.Vector3(
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 6 - 2,
          driftParams.positionOffset.z - 5 - Math.random() * 5
        )
      );
    }
    return positions;
  }, [driftParams.positionOffset.z]);

  // 新增：隨機生成粒子類型和顏色（移除黃色球體，改用物理波紋）
  const particleConfigs = useMemo(() => {
    const configs: {type: 'sphere' | 'box' | 'torus' | 'cone', color: THREE.Color}[] = [];
    
    // 為方塊粒子生成配置
    for (let i = 0; i < 6; i++) {
      configs.push({
        type: 'box',
        color: new THREE.Color(0x0088ff) // 藍色
      });
    }
    
    // 為環狀粒子生成配置
    for (let i = 0; i < 5; i++) {
      configs.push({
        type: 'torus',
        color: new THREE.Color(0xff55ff) // 粉色
      });
    }
    
    // 為錐體粒子生成配置
    for (let i = 0; i < 4; i++) {
      configs.push({
        type: 'cone',
        color: new THREE.Color(0x00ff88) // 綠色
      });
    }
    
    return configs;
  }, []);
  
  // 新增：巨型隨機出現的瘋狂物體
  const [showCrazyObject, setShowCrazyObject] = useState(false);
  const crazyObjectRef = useRef<THREE.Mesh>(null);
  const crazyObjectType = useRef<'dodecahedron' | 'octahedron' | 'torusKnot'>('dodecahedron');
  const crazyObjectTimeRef = useRef(0);

  useFrame((state, delta) => {
    timeRef.current += delta;
    morphTimerRef.current += delta;
    
    // 處理瘋狂模式冷卻時間
    if (crazyCooldownRef.current > 0) {
      crazyCooldownRef.current -= delta;
    }
    
    // 音樂強度超過閾值時，隨機觸發瘋狂模式
    if (bgmIntensity > 0.7 && !crazyMode && crazyCooldownRef.current <= 0 && Math.random() < 0.01) {
      setCrazyMode(true);
      setTimeout(() => {
        setCrazyMode(false);
        crazyCooldownRef.current = 5; // 5秒冷卻時間
      }, 2000 + Math.random() * 3000); // 瘋狂模式持續2-5秒
    }
    
    // 根據音樂強度或時間，隨機改變幾何形狀
    if ((bgmIntensity > 0.6 && Math.random() < 0.005) || 
        (morphTimerRef.current - lastMorphTimeRef.current > 8 + Math.random() * 5)) {
      const shapes: GeometryType[] = ['torusKnot', 'octahedron', 'tetrahedron', 'icosahedron'];
      const newShape = shapes[Math.floor(Math.random() * shapes.length)];
      setGeometryType(newShape);
      lastMorphTimeRef.current = morphTimerRef.current;
    }
    
    if (meshRef.current) {
      // 瘋狂模式下的行為
      const crazyFactor = crazyMode ? 5 : 1;
      
      // 在舞者圈圈內跳動的新邏輯
      positionRef.current.x += driftParams.speedX * (1 + bgmIntensity * 0.5 * crazyFactor);
      positionRef.current.z += driftParams.speedZ * (1 + bgmIntensity * 0.3 * crazyFactor);
      
      // 環形邊界檢測：確保在舞者圈圈內但不接近頭部
      const currentDistance = Math.sqrt(positionRef.current.x ** 2 + positionRef.current.z ** 2);
      
      // 檢查是否超出外圓邊界（舞者圈圈）
      if (currentDistance > driftParams.outerRadius) {
        const normalizeX = positionRef.current.x / currentDistance;
        const normalizeZ = positionRef.current.z / currentDistance;
        
        // 反射速度
        driftParams.speedX = -driftParams.speedX * (1 + (crazyMode ? 0.3 : 0));
        driftParams.speedZ = -driftParams.speedZ * (1 + (crazyMode ? 0.3 : 0));
        
        // 將位置拉回外圓邊界內
        positionRef.current.x = normalizeX * driftParams.outerRadius * 0.95;
        positionRef.current.z = normalizeZ * driftParams.outerRadius * 0.95;
        
        if (crazyMode) {
          driftParams.speedX += (Math.random() - 0.5) * 0.02;
          driftParams.speedZ += (Math.random() - 0.5) * 0.02;
        }
      }
      
      // 檢查是否進入內圓禁區（頭部區域）
      if (currentDistance < driftParams.innerRadius) {
        const normalizeX = positionRef.current.x / currentDistance;
        const normalizeZ = positionRef.current.z / currentDistance;
        
        // 強力反彈出禁區
        driftParams.speedX = normalizeX * 0.03 * (1 + (crazyMode ? 0.5 : 0));
        driftParams.speedZ = normalizeZ * 0.03 * (1 + (crazyMode ? 0.5 : 0));
        
        // 將位置推出內圓禁區
        positionRef.current.x = normalizeX * driftParams.innerRadius * 1.1;
        positionRef.current.z = normalizeZ * driftParams.innerRadius * 1.1;
      }

      // 音樂響應的跳動效果 - 增強脈動
      const jumpFactor = (1.0 + bgmIntensity * 4.0) * (crazyMode ? 5.0 : 1);
      let musicJumpX = Math.sin(timeRef.current * 1.8) * jumpFactor;
      let musicJumpZ = Math.cos(timeRef.current * 1.5) * jumpFactor;
      let musicJumpY = Math.sin(timeRef.current * 3.0) * (3 + bgmIntensity * 6);
      
      // 添加多層次的脈動效果
      musicJumpX += Math.sin(timeRef.current * 4.5) * jumpFactor * 0.6;
      musicJumpZ += Math.cos(timeRef.current * 3.8) * jumpFactor * 0.6;
      musicJumpY += Math.cos(timeRef.current * 5.5) * (1 + bgmIntensity * 4);
      
      // 瘋狂模式下添加額外的高頻跳動
      if (crazyMode) {
        musicJumpX += Math.sin(timeRef.current * 12) * jumpFactor * 0.5;
        musicJumpZ += Math.cos(timeRef.current * 10) * jumpFactor * 0.5;
        musicJumpY += Math.sin(timeRef.current * 15) * bgmIntensity * 3.0;
      }
      
      meshRef.current.position.set(
        positionRef.current.x + musicJumpX,
        positionRef.current.y + musicJumpY,
        positionRef.current.z + musicJumpZ
      );
      
      currentPosition.copy(meshRef.current.position);
      
      // 瘋狂旋轉 - 增強脈動
      const rotationMultiplier = crazyMode ? 5 + Math.sin(timeRef.current * 15) * 3 : 1 + bgmIntensity * 2;
      const rotationPulse = 1 + Math.sin(timeRef.current * 8) * bgmIntensity * 2;
      
      meshRef.current.rotation.x += (driftParams.rotationSpeedBase.x + bgmIntensity * 0.03) * rotationMultiplier * rotationPulse;
      meshRef.current.rotation.y += (driftParams.rotationSpeedBase.y + bgmIntensity * 0.04) * rotationMultiplier * rotationPulse;
      meshRef.current.rotation.z += (driftParams.rotationSpeedBase.z + bgmIntensity * 0.05) * rotationMultiplier * rotationPulse;
      
      // 更瘋狂的縮放 - 增強脈動
      let baseScale = 1.8;
      if (crazyMode) {
        baseScale *= 1 + Math.sin(timeRef.current * 12) * 0.5;
      }
      
      const scaleFactor = baseScale * (1 + bgmIntensity * (crazyMode ? 2.5 : 1.2));
      meshRef.current.scale.set(scaleFactor, scaleFactor, scaleFactor);
      
      // 增強的脈動效果 - 多層次縮放
      const primaryPulse = 1 + Math.sin(timeRef.current * 4.0) * bgmIntensity * 0.8;
      const secondaryPulse = 1 + Math.cos(timeRef.current * 6.5) * bgmIntensity * 0.4;
      
      if (crazyMode) {
        const pulseX = 1 + Math.sin(timeRef.current * 5.5) * bgmIntensity * 1.0;
        const pulseY = 1 + Math.cos(timeRef.current * 7.2) * bgmIntensity * 1.2;
        const pulseZ = 1 + Math.sin(timeRef.current * 4.8) * bgmIntensity * 0.8;
        meshRef.current.scale.x *= pulseX * primaryPulse;
        meshRef.current.scale.y *= pulseY * primaryPulse;
        meshRef.current.scale.z *= pulseZ * primaryPulse;
      } else {
        meshRef.current.scale.multiplyScalar(primaryPulse * secondaryPulse);
      }
    }
    
    // 材質動畫
    if (materialRef.current) {
      const baseColor = new THREE.Color(crazyMode ? 0x330033 : 0x1a1a33);
      const activeColor = new THREE.Color(crazyMode ? 0xff33ff : 0xaa88ff);
      
      materialRef.current.color.copy(baseColor).lerp(
        activeColor, 
        Math.min(1, bgmIntensity * (crazyMode ? 3.0 : 2.0))
      );
      
      materialRef.current.emissive.copy(baseColor).lerp(
        activeColor,
        Math.min(1, bgmIntensity * (crazyMode ? 3.0 : 2.0))
      );
      
      materialRef.current.emissiveIntensity = 0.3 + bgmIntensity * (crazyMode ? 10 : 7);
      
      // 瘋狂模式下迅速切換金屬感和粗糙度
      if (crazyMode) {
        materialRef.current.metalness = 0.2 + Math.abs(Math.sin(timeRef.current * 10)) * 0.8;
        materialRef.current.roughness = Math.abs(Math.cos(timeRef.current * 8)) * 0.9;
      } else {
        materialRef.current.metalness = THREE.MathUtils.clamp(0.2 + bgmIntensity * 0.8, 0.2, 0.9);
        materialRef.current.roughness = THREE.MathUtils.clamp(0.8 - bgmIntensity * 0.6, 0.1, 0.8);
      }
      
      // Wireframe 效果更動態
      materialRef.current.wireframe = bgmIntensity > 0.4 || crazyMode;
      materialRef.current.wireframeLinewidth = 1 + bgmIntensity * (crazyMode ? 4 : 2);
    }

    // 巨型瘋狂物體的邏輯
    crazyObjectTimeRef.current += delta;
    
    // 只在瘋狂模式下才有機會觸發巨型物體
    if (crazyMode && !showCrazyObject && Math.random() < 0.002) {
      setShowCrazyObject(true);
      
      // 隨機選擇一種形狀
      const shapes: ('dodecahedron' | 'octahedron' | 'torusKnot')[] = ['dodecahedron', 'octahedron', 'torusKnot'];
      crazyObjectType.current = shapes[Math.floor(Math.random() * shapes.length)];
      
      // 2-4秒後消失
      setTimeout(() => {
        setShowCrazyObject(false);
      }, 2000 + Math.random() * 2000);
    }
    
    // 巨型物體的動畫
    if (crazyObjectRef.current && showCrazyObject) {
      // 巨型物體圍繞中心瘋狂旋轉
      crazyObjectRef.current.position.x = Math.sin(crazyObjectTimeRef.current * 2) * 10;
      crazyObjectRef.current.position.y = Math.cos(crazyObjectTimeRef.current * 3) * 8;
      crazyObjectRef.current.position.z = -15 + Math.sin(crazyObjectTimeRef.current * 5) * 5;
      
      // 瘋狂旋轉
      crazyObjectRef.current.rotation.x += 0.05 + bgmIntensity * 0.1;
      crazyObjectRef.current.rotation.y += 0.04 + bgmIntensity * 0.08;
      crazyObjectRef.current.rotation.z += 0.03 + bgmIntensity * 0.06;
      
      // 脈動縮放
      const pulseScale = 3 + Math.sin(crazyObjectTimeRef.current * 10) * 1.5 * bgmIntensity;
      crazyObjectRef.current.scale.set(pulseScale, pulseScale, pulseScale);
    }
  });

  return (
    <group>
      {/* 主要的"音樂播放器"物體 - 現在會根據狀態切換形狀 */}
      <mesh ref={meshRef} position={[driftParams.positionOffset.x, driftParams.positionOffset.y, driftParams.positionOffset.z]}>
        {geometryType === 'torusKnot' && <torusKnotGeometry args={[1.2, 0.4, 128, 20]} />}
        {geometryType === 'octahedron' && <octahedronGeometry args={[1.5, 2]} />}
        {geometryType === 'tetrahedron' && <tetrahedronGeometry args={[1.8, 1]} />}
        {geometryType === 'icosahedron' && <icosahedronGeometry args={[1.5, 1]} />}
        
        <meshStandardMaterial 
          ref={materialRef} 
          color={0x1a1a33} 
          emissive={0x1a1a33} 
          emissiveIntensity={0.3}
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>
      
      {/* 語音喇叭 - 專門用於角色語音 */}
      <VoiceSpeaker 
        bgmIntensity={bgmIntensity}
        musicSpeakerPosition={currentPosition}
        outerRadius={driftParams.outerRadius}
        innerRadius={driftParams.innerRadius}
      />
      
      {/* 物理波紋效果 - 替代黃色粒子 */}
      <PhysicalRipple
        parentPosition={currentPosition}
        bgmIntensity={bgmIntensity}
        crazyModeRef={crazyMode ? {current: true} : undefined}
      />
      
      {/* 多種類型的環繞粒子 */}
      {particleConfigs.map((config, i) => (
        <OrbitingParticle 
          key={`particle-${config.type}-${i}`}
          radius={2.5 + i * 0.3} 
          speed={0.3 + Math.random() * 0.3} 
          phase={i * Math.PI / (particleConfigs.length / 2)}
          parentPosition={currentPosition}
          bgmIntensity={bgmIntensity}
          particleType={config.type}
          baseColor={config.color}
          crazyModeRef={crazyMode ? {current: true} : undefined}
        />
      ))}

      {/* 漂浮的數位方塊 */}
      {floatingCubesPositions.map((pos, i) => (
        <FloatingCube 
          key={`floating-cube-${i}`}
          initialPosition={pos}
          bgmIntensity={bgmIntensity}
          index={i}
          crazyModeRef={crazyMode ? {current: true} : undefined}
        />
      ))}
      
      {/* 瘋狂模式下隨機出現的巨型物體 */}
      {showCrazyObject && (
        <mesh ref={crazyObjectRef} position={[0, 0, -15]}>
          {crazyObjectType.current === 'dodecahedron' && <dodecahedronGeometry args={[3, 0]} />}
          {crazyObjectType.current === 'octahedron' && <octahedronGeometry args={[4, 0]} />}
          {crazyObjectType.current === 'torusKnot' && <torusKnotGeometry args={[2, 0.8, 64, 8, 2, 3]} />}
          <meshStandardMaterial 
            color={0xff00ff} 
            emissive={0xff00ff}
            emissiveIntensity={2}
            wireframe={true}
          />
        </mesh>
      )}
      
      {/* 瘋狂模式下的額外閃爍物件 */}
      {crazyMode && [...Array(20)].map((_, i) => (
        <mesh 
          key={`crazy-flash-${i}`}
          position={[
            (Math.random() - 0.5) * 15,
            (Math.random() - 0.5) * 15,
            -10 - Math.random() * 20
          ]}
          rotation={[Math.random() * Math.PI * 2, Math.random() * Math.PI * 2, Math.random() * Math.PI * 2]}
          scale={0.2 + Math.random() * 0.3}
        >
          {Math.random() > 0.5 ? 
            <sphereGeometry args={[1, 8, 8]} /> : 
            <boxGeometry args={[1, 1, 1]} />
          }
          <meshStandardMaterial 
            color={new THREE.Color().setHSL(Math.random(), 1, 0.5)} 
            emissive={new THREE.Color().setHSL(Math.random(), 1, 0.5)}
            emissiveIntensity={2}
            transparent
            opacity={0.7}
          />
        </mesh>
      ))}
    </group>
  );
};

export default MusicBackground;

