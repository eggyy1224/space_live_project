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
          // 增加語音持續時間以確保文字顯示完成前語音不會結束
          // 增加20%的時間來確保文字顯示不會太快結束
          setSpeechDuration(lastJsonMessage.speechDuration * 1.2);
          logger.info(`大屏幕設置語音持續時間: ${lastJsonMessage.speechDuration * 1.2}秒 (原始: ${lastJsonMessage.speechDuration}秒)`, LogCategory.CHAT);
        } 
        // 然後檢查消息對象中的 speechDuration
        else if (lastJsonMessage.message.speechDuration) {
          // 同樣增加語音持續時間
          setSpeechDuration(lastJsonMessage.message.speechDuration * 1.2);
          logger.info(`大屏幕設置語音持續時間(從消息): ${lastJsonMessage.message.speechDuration * 1.2}秒 (原始: ${lastJsonMessage.message.speechDuration}秒)`, LogCategory.CHAT);
        } 
        // 如果都沒有，使用基於文本長度的估算
        else {
          // 更保守的估算，以確保文字顯示速度更慢
          const estimatedDuration = Math.max(2, speechText.length * 0.15);
          setSpeechDuration(estimatedDuration);
          logger.info(`大屏幕估算語音持續時間: ${estimatedDuration}秒`, LogCategory.CHAT);
        }
      } else {
        // 默認值 - 增加每個字符的時間以放慢顯示速度
        setSpeechDuration(Math.max(2, speechText.length * 0.15));
      }
    }
  }, [speechText, lastJsonMessage]);

  // 改進的打字機效果：根據語音持續時間動態調整打字速度
  useEffect(() => {
    if (!typingComplete && fullText && typingStartTime !== null && speechDuration !== null) {
      // 獲取音頻的實際播放狀態
      const audioStartTime = useStore.getState().audioStartTime;
      const audioDuration = useStore.getState().audioDuration;
      const isSpeaking = useStore.getState().isSpeaking;
      
      // 如果有實際音頻播放數據，使用它來精確同步
      if (isSpeaking && audioStartTime && audioDuration) {
        const now = performance.now();
        const elapsedAudioTime = now - audioStartTime; // 音頻已播放時間
        const totalAudioDuration = audioDuration * 1000; // 音頻總持續時間（毫秒）
        
        // 根據音頻播放進度計算應該顯示的文字位置
        const expectedProgress = Math.min(1, elapsedAudioTime / totalAudioDuration);
        const expectedCharIndex = Math.floor(fullText.length * expectedProgress);
        
        // 顯示進度落後于音頻，需要快速趕上
        if (expectedCharIndex > typingIndex) {
          logger.debug(`大屏幕文字顯示落後: 期望位置 ${expectedCharIndex}, 當前位置 ${typingIndex}`, LogCategory.CHAT);
          // 快速更新到當前應該顯示的位置
          setDisplayText(fullText.substring(0, expectedCharIndex));
          setTypingIndex(expectedCharIndex);
          
          // 設置下一個字符的顯示時間
          const charsRemaining = fullText.length - expectedCharIndex;
          if (charsRemaining > 0) {
            const timeRemaining = totalAudioDuration - elapsedAudioTime;
            const intervalPerChar = Math.max(30, timeRemaining / charsRemaining);
            
            const timer = setTimeout(() => {
              setTypingIndex(prev => prev + 1);
              setDisplayText(fullText.substring(0, expectedCharIndex + 1));
            }, intervalPerChar);
            
            return () => clearTimeout(timer);
          }
        } 
        // 顯示進度超前于音頻，需要等待
        else if (expectedCharIndex < typingIndex) {
          logger.debug(`大屏幕文字顯示超前: 期望位置 ${expectedCharIndex}, 當前位置 ${typingIndex}`, LogCategory.CHAT);
          // 計算下一個字符應該何時顯示
          const nextCharTime = totalAudioDuration * ((typingIndex + 1) / fullText.length);
          const timeUntilNextChar = Math.max(50, nextCharTime - elapsedAudioTime);
          
          const timer = setTimeout(() => {
            setTypingIndex(prev => prev + 1);
            setDisplayText(fullText.substring(0, typingIndex + 1));
          }, timeUntilNextChar);
          
          return () => clearTimeout(timer);
        }
        // 進度匹配，正常顯示下一個字符
        else if (typingIndex < fullText.length) {
          const charsRemaining = fullText.length - typingIndex;
          const timeRemaining = totalAudioDuration - elapsedAudioTime;
          const intervalPerChar = Math.max(30, timeRemaining / charsRemaining);
          
          const timer = setTimeout(() => {
            setTypingIndex(prev => prev + 1);
            setDisplayText(fullText.substring(0, typingIndex + 1));
          }, intervalPerChar);
          
          return () => clearTimeout(timer);
        } else {
          // 所有字符已顯示完成，但保持打字狀態直到音頻結束
          if (elapsedAudioTime < totalAudioDuration) {
            const timer = setTimeout(() => {
              // 保持打字狀態直到音頻結束
            }, totalAudioDuration - elapsedAudioTime);
            
            return () => clearTimeout(timer);
          } else {
            setTypingComplete(true);
          }
        }
      }
      // 沒有實際音頻數據，使用預估的時間
      else {
        // 初始延遲，讓音頻有時間開始播放
        const initialDelay = 300; 
        
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
        
        if (typingIndex < fullText.length) {
          const elapsedTime = performance.now() - typingStartTime;
          const slowdownFactor = 1.5;
          const remainingTime = Math.max(500, (totalTypingDuration - elapsedTime) * slowdownFactor);
          const remainingChars = fullText.length - typingIndex;
          
          if (remainingChars > 0) {
            const intervalPerChar = Math.max(30, remainingTime / remainingChars);
            
            const timer = setTimeout(() => {
              setDisplayText(fullText.substring(0, typingIndex + 1));
              setTypingIndex(prev => prev + 1);
            }, intervalPerChar);
            
            return () => clearTimeout(timer);
          } else {
            const displayCompleteDelay = 1000;
            const timer = setTimeout(() => {
              setTypingComplete(true);
            }, displayCompleteDelay);
            
            return () => clearTimeout(timer);
          }
        }
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
