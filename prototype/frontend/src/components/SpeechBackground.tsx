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

  // 用於打字機效果的狀態
  const [displayText, setDisplayText] = useState('');
  const [typingIndex, setTypingIndex] = useState(0);
  const [fullText, setFullText] = useState('');
  const [typingComplete, setTypingComplete] = useState(true);
  
  // 用於彩色 VJ 效果
  const [textColor, setTextColor] = useState<THREE.Color>(new THREE.Color(0xffffff));
  const colorTimeRef = useRef(0);

  // 當新的語音文字到達時，重置打字機效果
  useEffect(() => {
    if (speechText !== fullText) {
      setFullText(speechText);
      setTypingIndex(0);
      setTypingComplete(false);
    }
  }, [speechText]);

  // 打字機效果：每隔一段時間增加一個字符
  useEffect(() => {
    if (!typingComplete && fullText) {
      const typingSpeed = 150; // 打字速度 (毫秒/字符)，調整為更慢的速度
      
      if (typingIndex < fullText.length) {
        const timer = setTimeout(() => {
          setDisplayText(fullText.substring(0, typingIndex + 1));
          setTypingIndex(prev => prev + 1);
        }, typingSpeed);
        
        return () => clearTimeout(timer);
      } else {
        setTypingComplete(true);
      }
    }
  }, [typingIndex, fullText, typingComplete]);

  useFrame((state, delta) => {
    // 背景發光效果
    if (materialRef.current) {
      const baseColor = new THREE.Color(0x111133);
      materialRef.current.emissive.set(baseColor);
      const sensitivity = 10.0;
      let intensity = Math.pow(audioAverageVolume * sensitivity, 1.5);
      const current = materialRef.current.emissiveIntensity;
      intensity = THREE.MathUtils.lerp(current, intensity, 0.15);
      materialRef.current.emissiveIntensity = Math.max(0.05, intensity);
    }
    
    // 彩色 VJ 效果：基於音量和時間更新文字顏色
    colorTimeRef.current += delta;
    
    // 顏色脈動，基於時間和音量
    const hue = (colorTimeRef.current * 0.1) % 1;
    const saturation = 0.7 + audioAverageVolume * 0.5;
    const lightness = 0.5 + audioAverageVolume * 0.2;
    
    // 使用 HSL 設置顏色
    const newColor = new THREE.Color().setHSL(hue, saturation, lightness);
    setTextColor(newColor);
  });

  // 定義背景「大螢幕」區域
  const screenWidth = viewport.width * 0.8;
  const screenHeight = viewport.height * 0.6;

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
      
      {/* 可視化「大螢幕」區域 */}
      <mesh position={[0, 0, 0.05]}>
        <planeGeometry args={[screenWidth, screenHeight]} />
        <meshBasicMaterial color={0x000022} transparent opacity={0.2} />
      </mesh>
      
      {displayText && (
        <Text
          position={[0, 0, 0.1]}
          fontSize={viewport.width / 20}
          color={textColor}
          anchorX="center"
          anchorY="middle"
          maxWidth={screenWidth * 0.9}
          textAlign="center"
          outlineWidth={audioAverageVolume > 0.1 ? 0.01 : 0} // 音量大時添加輪廓
          outlineColor={new THREE.Color().setHSL((colorTimeRef.current * 0.2) % 1, 1, 0.7)} // 動態輪廓顏色
        >
          {displayText}
        </Text>
      )}
    </group>
  );
};

export default SpeechBackground;
