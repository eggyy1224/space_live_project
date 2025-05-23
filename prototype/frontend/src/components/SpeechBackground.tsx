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
      // 使用 requestAnimationFrame 實現更平滑的打字效果和更頻繁的同步檢查
      let animationFrameId: number | null = null;
      let lastTimestamp: number | null = null;
      
      const animate = (timestamp: number) => {
        // 首次呼叫時初始化時間戳
        if (lastTimestamp === null) {
          lastTimestamp = timestamp;
          animationFrameId = requestAnimationFrame(animate);
          return;
        }
        
        // 獲取音頻的實際播放狀態
        const audioStartTime = useStore.getState().audioStartTime;
        const audioDuration = useStore.getState().audioDuration;
        const isSpeaking = useStore.getState().isSpeaking;
        
        // 如果有音頻正在播放，使用音頻進度同步文本顯示
        if (isSpeaking && audioStartTime && audioDuration) {
          const elapsedAudioTime = timestamp - audioStartTime;
          const totalAudioDuration = audioDuration * 1000;
          
          // 添加初始延遲
          const initialDelay = 100;
          const adjustedElapsedTime = Math.max(0, elapsedAudioTime - initialDelay);
          
          // 計算期望顯示的字符索引
          const expectedCharIndex = Math.min(
            fullText.length,
            Math.floor((adjustedElapsedTime / totalAudioDuration) * fullText.length)
          );
          
          // 只在需要更新時才更新，避免不必要的狀態變更
          if (expectedCharIndex > typingIndex) {
            setTypingIndex(expectedCharIndex);
            setDisplayText(fullText.substring(0, expectedCharIndex));
            logger.debug(`大屏幕同步更新: ${expectedCharIndex}/${fullText.length} 字符`, LogCategory.CHAT);
          }
          
          // 檢查是否全部顯示完畢
          if (expectedCharIndex >= fullText.length) {
            // 維持顯示直到音頻結束
            const remainingAudioTime = Math.max(0, totalAudioDuration - elapsedAudioTime);
            if (remainingAudioTime <= 0) {
              setTypingComplete(true);
            }
          }
        } 
        // 沒有音頻播放，使用預設的打字速度
        else {
          const deltaTime = timestamp - lastTimestamp;
          lastTimestamp = timestamp;
          
          // 計算整個打字過程應該花費的總時間
          const totalTypingDuration = speechDuration * 1000;
          const elapsedTime = timestamp - typingStartTime;
          const progress = elapsedTime / totalTypingDuration;
          
          // 計算當前應該顯示的字符索引
          const expectedCharIndex = Math.min(
            fullText.length,
            Math.floor(fullText.length * progress)
          );
          
          // 更新顯示的文本
          if (expectedCharIndex > typingIndex) {
            setTypingIndex(expectedCharIndex);
            setDisplayText(fullText.substring(0, expectedCharIndex));
          }
          
          // 檢查是否全部顯示完畢
          if (expectedCharIndex >= fullText.length) {
            // 維持顯示一段時間
            const displayCompleteDelay = 1000;
            setTimeout(() => {
              setTypingComplete(true);
            }, displayCompleteDelay);
            return; // 結束動畫
          }
        }
        
        // 繼續動畫
        if (!typingComplete) {
          animationFrameId = requestAnimationFrame(animate);
        }
      };
      
      // 啟動動畫
      animationFrameId = requestAnimationFrame(animate);
      
      // 清理函數
      return () => {
        if (animationFrameId !== null) {
          cancelAnimationFrame(animationFrameId);
        }
      };
    }
  }, [fullText, typingComplete, typingStartTime, speechDuration]);

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
    <group position={[0, 0, -30]}>
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

