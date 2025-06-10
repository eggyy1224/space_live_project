import React, { useRef, useState, useEffect, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import { useStore } from '../store';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager';

// 可調整的參數配置
const CONFIG = {
  // 生成位置
  SPAWN_POSITION: new THREE.Vector3(0, 0, 0),
  
  // 打字機效果參數
  TYPING_SPEED: 0.08, // 每個字符出現的間隔時間（秒）
  
  // 漂浮動畫參數
  FLOAT_SPEED: 2.5, // 基礎漂浮速度
  FLOAT_RANDOMNESS: 8.0, // 隨機性強度 - 增加以展開更廣
  UPWARD_FORCE: 3.0, // 向上漂浮力度 - 增加垂直展開
  DOWNWARD_FORCE: 1.5, // 向下漂浮力度
  SPREAD_FORCE: 5.0, // 水平展開力度
  VERTICAL_SPREAD: 6.0, // 垂直展開力度
  
  // 淡出持續時間（秒）
  FADE_DURATION: 15.0,
  
  // 生長動畫持續時間（秒）
  GROWTH_DURATION: 1.5,
  
  // 字符大小變化範圍
  MIN_FONT_SIZE: 0.8,
  MAX_FONT_SIZE: 5.0,
  
  // 音量反應參數
  VOLUME_SCALE_MULTIPLIER: 2.0, // 音量對大小的影響
  VOLUME_SPEED_MULTIPLIER: 3.0, // 音量對速度的影響
  VOLUME_COLOR_INTENSITY: 0.8, // 音量對顏色的影響
  
  // 彩虹色彩參數
  RAINBOW_SPEED: 0.5, // 色彩變化速度
  RAINBOW_INTENSITY: 0.95, // 色彩飽和度
  
  // 文字參數
  BASE_FONT_SIZE: 3.0,
  CHARACTER_SPACING: 2.5, // 增加初始間距
  
  // 性能參數
  MAX_CHARACTERS: 400, // 最大同時顯示字符數
};

// 單個字符的數據結構
interface FloatingCharacter {
  id: string;
  char: string;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  scale: number;
  opacity: number;
  age: number; // 存在時間
  hueOffset: number; // 彩虹色相偏移
  initialPosition: THREE.Vector3;
  targetSize: number; // 目標字體大小
  rotationSpeed: THREE.Vector3; // 旋轉速度
  spawnTime: number; // 生成時間
  volumeReaction: number; // 音量反應係數
  pulsePhase: number; // 脈動相位
}

// 字符池管理器
class CharacterPool {
  private pool: FloatingCharacter[] = [];
  private activeCharacters: Map<string, FloatingCharacter> = new Map();
  private nextId = 0;

  // 獲取或創建字符
  getCharacter(char: string, position: THREE.Vector3, spawnTime: number): FloatingCharacter {
    let character = this.pool.pop();
    
    if (!character) {
      character = {
        id: `char_${this.nextId++}`,
        char: '',
        position: new THREE.Vector3(),
        velocity: new THREE.Vector3(),
        scale: 0,
        opacity: 1,
        age: 0,
        hueOffset: Math.random(),
        initialPosition: new THREE.Vector3(),
        targetSize: 1,
        rotationSpeed: new THREE.Vector3(),
        spawnTime: 0,
        volumeReaction: 0.5 + Math.random() * 0.5,
        pulsePhase: Math.random() * Math.PI * 2,
      };
    }

    // 重置字符屬性
    character.char = char;
    character.position.copy(position);
    character.initialPosition.copy(position);
    character.spawnTime = spawnTime;
    
    // 隨機生成飛行方向和速度 - 更強的水平和垂直展開
    const angle = Math.random() * Math.PI * 2;
    const elevation = (Math.random() - 0.5) * Math.PI * 0.6; // 增加垂直範圍
    const speed = CONFIG.FLOAT_RANDOMNESS * (0.5 + Math.random() * 1.5);
    
    // 增加水平展開力度
    const horizontalForce = CONFIG.SPREAD_FORCE * (0.5 + Math.random());
    
    // 增加垂直展開力度 - 有些字符向上飛，有些向下飛
    const verticalDirection = Math.random() > 0.5 ? 1 : -1;
    const verticalForce = CONFIG.VERTICAL_SPREAD * (0.5 + Math.random()) * verticalDirection;
    
    character.velocity.set(
      Math.cos(angle) * Math.cos(elevation) * speed * horizontalForce,
      (CONFIG.UPWARD_FORCE + Math.sin(elevation) * speed) * Math.abs(verticalForce) * 0.5 + 
        (verticalDirection > 0 ? CONFIG.UPWARD_FORCE : -CONFIG.DOWNWARD_FORCE),
      Math.sin(angle) * Math.cos(elevation) * speed * horizontalForce
    );
    
    character.scale = 0;
    character.opacity = 1;
    character.age = 0;
    character.hueOffset = Math.random();
    character.volumeReaction = 0.5 + Math.random() * 0.5;
    character.pulsePhase = Math.random() * Math.PI * 2;
    
    // 隨機目標大小
    character.targetSize = CONFIG.MIN_FONT_SIZE + 
      Math.random() * (CONFIG.MAX_FONT_SIZE - CONFIG.MIN_FONT_SIZE);
    
    // 隨機旋轉速度
    character.rotationSpeed.set(
      (Math.random() - 0.5) * 3,
      (Math.random() - 0.5) * 3,
      (Math.random() - 0.5) * 3
    );

    this.activeCharacters.set(character.id, character);
    return character;
  }

  // 回收字符
  recycleCharacter(character: FloatingCharacter) {
    this.activeCharacters.delete(character.id);
    this.pool.push(character);
  }

  // 獲取所有活躍字符
  getActiveCharacters(): FloatingCharacter[] {
    return Array.from(this.activeCharacters.values());
  }

  // 清理所有字符
  clear() {
    this.activeCharacters.clear();
  }
}

const SpeechBackground: React.FC = () => {
  const { viewport } = useThree();
  const audioAverageVolume = useStore((state) => state.audioAverageVolume);
  const speechText = useStore((state) => state.speechText);
  const lastJsonMessage = useStore((state) => state.lastJsonMessage);
  const isSpeaking = useStore((state) => state.isSpeaking);

  // 字符池和狀態管理
  const characterPool = useMemo(() => new CharacterPool(), []);
  const [characters, setCharacters] = useState<FloatingCharacter[]>([]);
  const [lastProcessedText, setLastProcessedText] = useState('');
  
  // 打字機效果狀態
  const [currentText, setCurrentText] = useState('');
  const [typingIndex, setTypingIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [speechDuration, setSpeechDuration] = useState<number | null>(null);
  
  // 時間追蹤
  const timeRef = useRef(0);
  const typingStartTime = useRef(0);
  
  // 音量歷史記錄（用於平滑處理）
  const volumeHistory = useRef<number[]>([]);
  const smoothedVolume = useRef(0);

  // 當新的語音文字到達時，開始打字機效果
  useEffect(() => {
    if (speechText && speechText !== lastProcessedText) {
      logger.info(`更新 3D 文字動畫: "${speechText}"`, LogCategory.CHAT);
      
      // 檢查是否是新的對話開始（文字長度變短或完全不同）
      if (speechText.length < lastProcessedText.length || 
          !speechText.startsWith(lastProcessedText.slice(0, Math.min(speechText.length, lastProcessedText.length)))) {
        // 新對話開始，清理所有舊字符
        characterPool.clear();
        setCharacters([]);
        setCurrentText(speechText);
        setTypingIndex(0);
        setIsTyping(true);
        typingStartTime.current = timeRef.current;
      } else {
        // 增量更新：只處理新增的字符
        const newCharCount = speechText.length - lastProcessedText.length;
        if (newCharCount > 0) {
          setCurrentText(speechText);
          // 立即顯示新字符
          for (let i = lastProcessedText.length; i < speechText.length; i++) {
            const char = speechText[i];
            if (char && char.trim()) {
              const xOffset = (i - speechText.length / 2) * CONFIG.CHARACTER_SPACING;
              const yOffset = Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 10;
              const zOffset = Math.cos(i * 0.2) * 5;
              
              const spawnPos = new THREE.Vector3(
                CONFIG.SPAWN_POSITION.x + xOffset,
                CONFIG.SPAWN_POSITION.y + yOffset,
                CONFIG.SPAWN_POSITION.z + zOffset
              );
              
              characterPool.getCharacter(char, spawnPos, timeRef.current);
            }
          }
          setCharacters([...characterPool.getActiveCharacters()]);
          setTypingIndex(speechText.length);
        }
      }
      
      setLastProcessedText(speechText);
      
      // 從最近的消息中獲取語音持續時間
      if (lastJsonMessage && 
          lastJsonMessage.type === 'chat-message' && 
          lastJsonMessage.message && 
          lastJsonMessage.message.role === 'bot') {
        
        if (lastJsonMessage.speechDuration) {
          setSpeechDuration(lastJsonMessage.speechDuration);
          logger.info(`設置語音持續時間: ${lastJsonMessage.speechDuration}秒`, LogCategory.CHAT);
        } else if (lastJsonMessage.message.speechDuration) {
          setSpeechDuration(lastJsonMessage.message.speechDuration);
          logger.info(`設置語音持續時間(從消息): ${lastJsonMessage.message.speechDuration}秒`, LogCategory.CHAT);
        } else {
          const estimatedDuration = Math.max(3, speechText.length * 0.15);
          setSpeechDuration(estimatedDuration);
          logger.info(`估算語音持續時間: ${estimatedDuration}秒`, LogCategory.CHAT);
        }
      } else {
        setSpeechDuration(Math.max(3, speechText.length * 0.15));
      }
    }
  }, [speechText, lastJsonMessage, lastProcessedText]);

  // 打字機效果：根據語音持續時間或固定速度生成字符
  useEffect(() => {
    if (isTyping && currentText && speechDuration !== null) {
      let intervalId: NodeJS.Timeout;
      
      // 獲取音頻播放狀態
      const audioStartTime = useStore.getState().audioStartTime;
      const audioDuration = useStore.getState().audioDuration;
      const isSpeaking = useStore.getState().isSpeaking;
      
      if (isSpeaking && audioStartTime && audioDuration) {
        // 根據音頻進度同步打字
        const checkAudioProgress = () => {
          const currentTime = performance.now();
          const elapsedAudioTime = (currentTime - audioStartTime) / 1000;
          const totalAudioDuration = audioDuration;
          
          const progress = Math.min(1, elapsedAudioTime / totalAudioDuration);
          const expectedIndex = Math.floor(progress * currentText.length);
          
          if (expectedIndex > typingIndex && expectedIndex < currentText.length) {
            // 可能一次生成多個字符
            for (let i = typingIndex + 1; i <= expectedIndex; i++) {
              const char = currentText[i];
              if (char && char.trim()) {
                // 計算初始位置 - 增加展開範圍
                const xOffset = (i - currentText.length / 2) * CONFIG.CHARACTER_SPACING;
                const yOffset = Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 10; // 增加Y軸變化
                const zOffset = Math.cos(i * 0.2) * 5; // 增加Z軸變化
                
                const spawnPos = new THREE.Vector3(
                  CONFIG.SPAWN_POSITION.x + xOffset,
                  CONFIG.SPAWN_POSITION.y + yOffset,
                  CONFIG.SPAWN_POSITION.z + zOffset
                );
                
                characterPool.getCharacter(char, spawnPos, timeRef.current);
              }
            }
            setTypingIndex(expectedIndex);
            setCharacters([...characterPool.getActiveCharacters()]);
          }
          
          if (expectedIndex >= currentText.length - 1) {
            setIsTyping(false);
          }
        };
        
        intervalId = setInterval(checkAudioProgress, 30); // 更頻繁的檢查
      } else {
        // 使用固定速度打字
        const typingSpeed = speechDuration / currentText.length;
        
        intervalId = setInterval(() => {
          setTypingIndex(prev => {
            if (prev < currentText.length) {
              const char = currentText[prev];
              if (char.trim()) {
                // 計算初始位置 - 增加展開範圍
                const xOffset = (prev - currentText.length / 2) * CONFIG.CHARACTER_SPACING;
                const yOffset = Math.sin(prev * 0.3) * 5 + (Math.random() - 0.5) * 10; // 增加Y軸變化
                const zOffset = Math.cos(prev * 0.2) * 5; // 增加Z軸變化
                
                const spawnPos = new THREE.Vector3(
                  CONFIG.SPAWN_POSITION.x + xOffset,
                  CONFIG.SPAWN_POSITION.y + yOffset,
                  CONFIG.SPAWN_POSITION.z + zOffset
                );
                
                characterPool.getCharacter(char, spawnPos, timeRef.current);
                setCharacters([...characterPool.getActiveCharacters()]);
              }
              return prev + 1;
            } else {
              setIsTyping(false);
              return prev;
            }
          });
        }, typingSpeed * 1000);
      }
      
      return () => {
        if (intervalId) clearInterval(intervalId);
      };
    }
  }, [isTyping, currentText, speechDuration, typingIndex, characterPool]);

  // 主動畫循環
  useFrame((state, delta) => {
    timeRef.current += delta;
    
    // 平滑音量處理
    volumeHistory.current.push(audioAverageVolume);
    if (volumeHistory.current.length > 10) {
      volumeHistory.current.shift();
    }
    smoothedVolume.current = volumeHistory.current.reduce((a, b) => a + b, 0) / volumeHistory.current.length;
    
    const activeChars = characterPool.getActiveCharacters();
    let needsUpdate = false;

    activeChars.forEach((character) => {
      character.age += delta;
      
      // 1. 生長動畫（從 0 縮放到目標大小）
      if (character.age < CONFIG.GROWTH_DURATION) {
        const growthProgress = character.age / CONFIG.GROWTH_DURATION;
        // 使用 easeOutElastic 緩動函數創建彈性效果
        const easeOutElastic = (t: number) => {
          const c4 = (2 * Math.PI) / 3;
          return t === 0 ? 0 : t === 1 ? 1 : 
            Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
        };
        character.scale = easeOutElastic(Math.min(1, growthProgress)) * character.targetSize;
      } else {
        // 根據音量動態調整大小
        const volumeScale = 1 + smoothedVolume.current * CONFIG.VOLUME_SCALE_MULTIPLIER * character.volumeReaction;
        const pulseFactor = 1 + Math.sin(timeRef.current * 3 + character.pulsePhase) * 0.1 * smoothedVolume.current;
        character.scale = character.targetSize * volumeScale * pulseFactor;
      }

      // 2. 漂浮動畫 - 根據音量調整速度
      const speedMultiplier = 1 + smoothedVolume.current * CONFIG.VOLUME_SPEED_MULTIPLIER;
      character.velocity.multiplyScalar(0.93); // 阻力
      
      // 音量爆發時的額外推力
      if (audioAverageVolume > 0.3 && isSpeaking) {
        const burstForce = audioAverageVolume * 2;
        character.velocity.x += (Math.random() - 0.5) * burstForce;
        character.velocity.y += (Math.random() - 0.5) * burstForce * 2; // 增加垂直爆發力
        character.velocity.z += (Math.random() - 0.5) * burstForce;
      }
      
      character.position.add(
        character.velocity.clone().multiplyScalar(delta * CONFIG.FLOAT_SPEED * speedMultiplier)
      );

      // 添加隨機擾動和旋轉
      const time = timeRef.current + character.hueOffset * 10;
      const wobbleIntensity = 1 + smoothedVolume.current * 2;
      character.position.x += Math.sin(time * 0.3) * 0.03 * wobbleIntensity;
      character.position.y += Math.cos(time * 0.4) * 0.02 * wobbleIntensity;
      character.position.z += Math.sin(time * 0.5) * 0.03 * wobbleIntensity;

      // 3. 淡出動畫
      const fadeStartTime = CONFIG.FADE_DURATION - 4.0; // 提前開始淡出
      if (character.age > fadeStartTime) {
        const fadeProgress = (character.age - fadeStartTime) / 4.0;
        character.opacity = Math.max(0, 1 - fadeProgress);
      }

      // 4. 清理完全透明的字符
      if (character.opacity <= 0 || character.age > CONFIG.FADE_DURATION) {
        characterPool.recycleCharacter(character);
        needsUpdate = true;
      }
    });

    // 更新字符列表
    if (needsUpdate) {
      setCharacters([...characterPool.getActiveCharacters()]);
    }
  });

  // 計算彩虹色彩 - 根據音量增強效果
  const getRainbowColor = (character: FloatingCharacter): THREE.Color => {
    const time = timeRef.current * CONFIG.RAINBOW_SPEED;
    const volumeBoost = smoothedVolume.current * CONFIG.VOLUME_COLOR_INTENSITY;
    
    // 音量高時加快色彩變化
    const hue = (time * (1 + volumeBoost * 2) + character.hueOffset) % 1;
    const saturation = Math.min(1, CONFIG.RAINBOW_INTENSITY + volumeBoost * 0.5);
    const lightness = 0.5 + smoothedVolume.current * 0.5; // 根據音量調整亮度
    
    return new THREE.Color().setHSL(hue, saturation, lightness);
  };

  return (
    <group>
      {/* 渲染所有漂浮字符 */}
      {characters.map((character) => {
        const color = getRainbowColor(character);
        const rotationSpeed = 1 + smoothedVolume.current * 3; // 音量影響旋轉速度
        
        return (
          <Text
            key={character.id}
            position={character.position}
            fontSize={CONFIG.BASE_FONT_SIZE * character.scale}
            color={color}
            anchorX="center"
            anchorY="middle"
            material-transparent={true}
            material-opacity={character.opacity}
            outlineWidth={0.05 * character.scale * (1 + smoothedVolume.current)}
            outlineColor={color.clone().multiplyScalar(0.3)}
            rotation={[
              character.rotationSpeed.x * character.age * 0.5 * rotationSpeed,
              character.rotationSpeed.y * character.age * 0.5 * rotationSpeed,
              character.rotationSpeed.z * character.age * 0.5 * rotationSpeed
            ]}
          >
            {character.char}
          </Text>
        );
      })}

      {/* 音量反應的環境光效 */}
      <pointLight
        position={[0, 0, 20]}
        intensity={1 + smoothedVolume.current * 5}
        color={new THREE.Color().setHSL((timeRef.current * 0.15) % 1, 0.9, 0.7)}
        distance={100 + smoothedVolume.current * 50}
      />
      
      {/* 額外的動態光源 - 跟隨音量脈動 */}
      <pointLight
        position={[
          Math.sin(timeRef.current * 0.5) * 30 * (1 + smoothedVolume.current), 
          Math.cos(timeRef.current * 0.3) * 20 * (1 + smoothedVolume.current), 
          10 + smoothedVolume.current * 20
        ]}
        intensity={0.5 + smoothedVolume.current * 3}
        color={new THREE.Color().setHSL((timeRef.current * 0.2 + 0.5) % 1, 0.8, 0.6)}
        distance={80}
      />
      
      {/* 音量爆發時的閃光效果 */}
      {audioAverageVolume > 0.5 && (
        <pointLight
          position={[0, 0, 30]}
          intensity={audioAverageVolume * 10}
          color={new THREE.Color(1, 1, 1)}
          distance={150}
        />
      )}
    </group>
  );
};

export default SpeechBackground;

