import React, { useRef, useState, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import { useStore } from '../store';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager';

// Renders a plane that reacts to audio volume and displays the latest
// speech text from the chat stream as a large floating caption.
const SpeechBackground: React.FC = () => {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const { viewport } = useThree();
  const audioAverageVolume = useStore((state) => state.audioAverageVolume);
  const speechText = useStore((state) => state.speechText);
  const lastJsonMessage = useStore((state) => state.lastJsonMessage);

  // 用於打字機效果的狀態
  const [displayText, setDisplayText] = useState('');
  const [typingIndex, setTypingIndex] = useState(0);
  const [fullText, setFullText] = useState('');
  const [typingComplete, setTypingComplete] = useState(true);
  const [speechDuration, setSpeechDuration] = useState<number | null>(null);
  const [typingStartTime, setTypingStartTime] = useState<number | null>(null);
  
  // 用於彩色 VJ 效果
  const [textColor, setTextColor] = useState<THREE.Color>(new THREE.Color(0xffffff));
  const colorTimeRef = useRef(0);

  // 當新的語音文字到達時，重置打字機效果
  useEffect(() => {
    if (speechText !== fullText) {
      setFullText(speechText);
      setTypingIndex(0);
      setTypingComplete(false);
      setTypingStartTime(performance.now());
      
      // 從最近的消息中獲取語音持續時間
      if (lastJsonMessage && 
          lastJsonMessage.type === 'chat-message' && 
          lastJsonMessage.message && 
          lastJsonMessage.message.role === 'bot') {
        
        // 首先檢查消息中直接提供的 speechDuration
        if (lastJsonMessage.speechDuration) {
          setSpeechDuration(lastJsonMessage.speechDuration);
          logger.info(`大屏幕設置語音持續時間: ${lastJsonMessage.speechDuration}秒`, LogCategory.CHAT);
        } 
        // 然後檢查消息對象中的 speechDuration
        else if (lastJsonMessage.message.speechDuration) {
          setSpeechDuration(lastJsonMessage.message.speechDuration);
          logger.info(`大屏幕設置語音持續時間(從消息): ${lastJsonMessage.message.speechDuration}秒`, LogCategory.CHAT);
        } 
        // 如果都沒有，使用基於文本長度的估算
        else {
          const estimatedDuration = Math.max(1, speechText.length * 0.08 + 0.5);
          setSpeechDuration(estimatedDuration);
          logger.info(`大屏幕估算語音持續時間: ${estimatedDuration}秒`, LogCategory.CHAT);
        }
      } else {
        // 默認值
        setSpeechDuration(speechText.length * 0.08 + 0.5);
      }
    }
  }, [speechText, lastJsonMessage]);

  // 改進的打字機效果：根據語音持續時間動態調整打字速度
  useEffect(() => {
    if (!typingComplete && fullText && typingStartTime !== null && speechDuration !== null) {
      // 初始延遲，讓音頻有時間開始播放
      const initialDelay = 100; 
      
      // 如果是首個字符，等待初始延遲
      if (typingIndex === 0) {
        const timer = setTimeout(() => {
          setDisplayText(fullText.substring(0, typingIndex + 1));
          setTypingIndex(prev => prev + 1);
        }, initialDelay);
        
        return () => clearTimeout(timer);
      }
      
      // 計算整個打字過程應該花費的總時間 (毫秒)
      const totalTypingDuration = speechDuration * 1000;
      
      // 計算每個字符應該顯示的時間間隔
      // 根據字符總數和已經過去的時間來動態調整
      if (typingIndex < fullText.length) {
        const elapsedTime = performance.now() - typingStartTime;
        const remainingTime = Math.max(0, totalTypingDuration - elapsedTime);
        const remainingChars = fullText.length - typingIndex;
        
        // 如果還有字符需要顯示，計算下一個字符的顯示間隔
        if (remainingChars > 0) {
          const intervalPerChar = Math.max(10, remainingTime / remainingChars);
          
          const timer = setTimeout(() => {
            setDisplayText(fullText.substring(0, typingIndex + 1));
            setTypingIndex(prev => prev + 1);
          }, intervalPerChar);
          
          return () => clearTimeout(timer);
        } else {
          setTypingComplete(true);
        }
      } else {
        setTypingComplete(true);
      }
    }
  }, [typingIndex, fullText, typingComplete, typingStartTime, speechDuration]);

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
          {!typingComplete && (
            <meshBasicMaterial attach="material" color={textColor}>
              <Text
                position={[displayText.length * 0.5, 0, 0]}
                fontSize={viewport.width / 20}
                color={textColor}
              >
                |
              </Text>
            </meshBasicMaterial>
          )}
        </Text>
      )}
    </group>
  );
};

export default SpeechBackground;
