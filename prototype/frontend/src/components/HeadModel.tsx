import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, Center } from '@react-three/drei';
import * as THREE from 'three';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { Mesh } from 'three'; // Import Mesh type
import { useStore } from '../store'; // 導入 Zustand store
import { useEmotionalSpeaking } from '../hooks/useEmotionalSpeaking'; // <-- 導入新的 Hook
// --- 移除模型設定導入 ---
// import { EXTERNAL_ANIMATION_PATHS } from '../config/modelConfig';
// --- 移除結束 ---

// --- 移除外部動畫路徑定義 ---
// const EXTERNAL_ANIMATION_PATHS = [
//   '/animations/BaseballHit_animation.glb',
//   '/animations/BodyBlock_animation.glb'
// ];
// --- 移除結束 ---

// --- 新增：定義口型相關的 Morph Target Keys ---
const MOUTH_MORPH_TARGET_KEYS = new Set([
  'jawForward', 'jawLeft', 'jawOpen', 'jawRight',
  'mouthClose', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft',
  'mouthFrownRight', 'mouthFunnel', 'mouthLeft', 'mouthLowerDownLeft',
  'mouthLowerDownRight', 'mouthPressLeft', 'mouthPressRight', 'mouthPucker',
  'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower',
  'mouthShrugUpper', 'mouthSmileLeft', 'mouthSmileRight', 'mouthStretchLeft',
  'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight'
]);
// --- 新增結束 ---

// 擴展的網格類型，包含morphTargets屬性
interface MeshWithMorphs extends THREE.Mesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

// 更新 Props 接口
interface HeadModelProps { // <-- 重命名
  headModelUrl: string; // <-- 重命名
  scale?: number | [number, number, number]; // 保留變換 props
  position?: [number, number, number];
  rotation?: [number, number, number];
  // currentAnimation?: string; // 移除
}

// 更新組件名稱
export const HeadModel: React.FC<HeadModelProps> = ({
  headModelUrl, // <-- 使用新 prop 名
  scale = 1,
  position = [0, 0, 0], // 這是傳入的初始位置
  rotation = [0, 0, 0],
  // currentAnimation, // 移除
}) => {
  const group = useRef<THREE.Group>(null);
  const meshRef = useRef<MeshWithMorphs | null>(null);
  // const headService = HeadService.getInstance(); // <-- 不再需要實例

  // 儲存初始位置的 Ref
  const initialPosition = useRef(new THREE.Vector3(...position));
  useEffect(() => {
    initialPosition.current.set(...position);
  }, [position]);

  // 儲存初始旋轉的 Ref
  const initialRotation = useRef(new THREE.Euler(...rotation));
  useEffect(() => {
    initialRotation.current.set(...rotation);
  }, [rotation]);

  // 新增瞬移相關 Refs
  const teleportTimer = useRef(0);
  const nextTeleportTime = useRef(0);

  // 新增量子徘徊效果的 Refs
  const quantumPhaseRef = useRef(0);
  const chaosAttractorRef = useRef({ x: 0, y: 0, z: 0 });
  const timeWarpFactorsRef = useRef({ slow: 1, fast: 1 });
  const realityLayersRef = useRef(Array.from({length: 3}, () => ({ phase: Math.random() * Math.PI * 2, intensity: 0 })));

  // 初始化瞬移時間
  useEffect(() => {
    const teleportIntervalMin = 0.08; // 瞬移間隔下限 (秒) - 更快
    const teleportIntervalMax = 1.5;  // 瞬移間隔上限 (秒) - 更慢
    nextTeleportTime.current = Math.random() * (teleportIntervalMax - teleportIntervalMin) + teleportIntervalMin;
  }, [position]);

  // --- 移除外部動畫預加載 ---
  // useEffect(() => {
  //   EXTERNAL_ANIMATION_PATHS.forEach(path => useGLTF.preload(path));
  // }, []);
  // --- 移除結束 ---

  // --- 只加載主模型 (頭部) ---
  const { scene /*, animations: embeddedAnimations */ } = useGLTF(headModelUrl); // <-- 使用 headModelUrl, 移除 animations
  // --- 移除外部動畫加載 ---
  // const externalAnimationsData = EXTERNAL_ANIMATION_PATHS.map(path => useGLTF(path));
  // --- 移除結束 ---

  // --- 移除動畫合併邏輯 ---
  // const combinedAnimations = useRef<THREE.AnimationClip[]>([]);
  // useEffect(() => {
      // ... 合併邏輯 ...
  // }, [embeddedAnimations, externalAnimationsData, headService]);
  // --- 移除結束 ---

  // --- 移除 useAnimations ---
  // const { actions, mixer } = useAnimations(combinedAnimations.current, group);
  // --- 移除結束 ---

  // --- 從 Zustand Store 獲取 setHeadModelLoaded ---
  const setHeadModelLoaded = useStore((state) => state.setHeadModelLoaded); // <-- 使用重命名後的 action
  // --- 結束 ---

  const [localMorphTargetDictionary, setLocalMorphTargetDictionary] = useState<Record<string, number>>({});

  const { calculateCurrentTrajectoryWeights } = useEmotionalSpeaking();

  // --- 讀取 Zustand 狀態並使用 Ref 傳遞 ---
  const manualOrPresetTargetsFromStore = useStore((state) => state.morphTargets);
  const manualOrPresetTargetsRef = useRef(manualOrPresetTargetsFromStore);
  // -- 新增：讀取語音口型狀態 -- 
  const audioLipsyncTargetsFromStore = useStore((state) => state.audioLipsyncTargets);
  const audioLipsyncTargetsRef = useRef(audioLipsyncTargetsFromStore);
  // -- 新增結束 -- 
  const isSpeakingFromStore = useStore((state) => state.isSpeaking);
  const isSpeakingRef = useRef(isSpeakingFromStore);
  // -- 新增：讀取背景音樂強度 --
  const bgmIntensityFromStore = useStore((state) => state.bgmIntensity);
  const bgmIntensityRef = useRef(bgmIntensityFromStore);
  // -- 新增：讀取語音音量強度 --
  const audioAverageVolumeFromStore = useStore((state) => state.audioAverageVolume);
  const audioAverageVolumeRef = useRef(audioAverageVolumeFromStore);
  // -- 新增結束 --

  useEffect(() => {
    manualOrPresetTargetsRef.current = manualOrPresetTargetsFromStore;
  }, [manualOrPresetTargetsFromStore]);
  // -- 新增：更新語音口型 Ref -- 
  useEffect(() => {
    audioLipsyncTargetsRef.current = audioLipsyncTargetsFromStore;
  }, [audioLipsyncTargetsFromStore]);
  // -- 新增結束 -- 
  useEffect(() => {
    isSpeakingRef.current = isSpeakingFromStore;
  }, [isSpeakingFromStore]);
  // -- 新增：更新背景音樂強度 Ref --
  useEffect(() => {
    bgmIntensityRef.current = bgmIntensityFromStore;
  }, [bgmIntensityFromStore]);
  // -- 新增：更新語音音量強度 Ref --
  useEffect(() => {
    audioAverageVolumeRef.current = audioAverageVolumeFromStore;
  }, [audioAverageVolumeFromStore]);
  // -- 新增結束 --

  // --- 移除舊的設置可用動畫的 useEffect ---
  // useEffect(() => {
      // ... 設置可用動畫 ...
  // }, [actions, headService]);
  // --- 移除結束 ---

  // --- 移除簡化的動畫播放邏輯 ---
  // useEffect(() => {
      // ... 播放動畫邏輯 ...
  // }, [currentAnimation, actions]);
  // --- 移除結束 ---

  // --- 更新設置加載狀態和提取 Morph 字典的 useEffect ---
  useEffect(() => {
    let foundMeshWithMorphs = false;
    meshRef.current = null;
    let finalDict: Record<string, number> | null = null;

    if (scene) {
      scene.traverse((object) => {
        if (!foundMeshWithMorphs && object instanceof THREE.Mesh && object.morphTargetInfluences && object.morphTargetDictionary) {
          const meshWithMorphs = object as MeshWithMorphs;
          if (!meshWithMorphs.morphTargetInfluences) return;
          meshRef.current = meshWithMorphs;
          foundMeshWithMorphs = true;
          finalDict = meshWithMorphs.morphTargetDictionary || null;
          setLocalMorphTargetDictionary(finalDict || {});
          logger.info('HeadModel: Found mesh with morph targets.', LogCategory.MODEL, JSON.stringify(finalDict));
          meshWithMorphs.morphTargetInfluences.fill(0);
          logger.info('HeadModel: Initialized morphTargetInfluences to 0.', LogCategory.MODEL);
        }
      });

      // 只要 scene 存在，就設置 headModelLoaded 為 true
      setHeadModelLoaded(true); // <-- 使用重命名後的 action
      logger.info('HeadModel: Scene loaded, setting headModelLoaded state to true in Zustand.', LogCategory.MODEL);

      if (!foundMeshWithMorphs) {
        setLocalMorphTargetDictionary({});
        logger.warn('HeadModel: No mesh with morph targets found, but scene loaded.', LogCategory.MODEL, `URL: ${headModelUrl}`);
      }

    } else {
      setLocalMorphTargetDictionary({});
      setHeadModelLoaded(false); // <-- 使用重命名後的 action
      logger.error('HeadModel: Scene failed to load.', LogCategory.MODEL, `URL: ${headModelUrl}`);
    }
    // 依賴項更新為 headModelUrl
  }, [headModelUrl, scene, setHeadModelLoaded]);
  // --- 更新結束 ---

  // --- 更新 useFrame，使用新的權重合併邏輯 ---
  useFrame((state, delta) => {
    const time = state.clock.elapsedTime; 

    if (group.current) {
      // === 量子徘徊系統 ===
      
      // 1. 重新設計動態映射 - 語音為主，背景音樂為輔
      const musicIntensity = bgmIntensityRef.current;
      const voiceVolume = audioAverageVolumeRef.current;
      const isSpeaking = isSpeakingRef.current;
      
      // 語音強度處理 - 主要驅動因素（80%權重）
      const voiceIntensity = isSpeaking ? Math.min(voiceVolume * 8, 1.0) : 0; // 放大語音敏感度
      
      // 使用平滑的tanh函數創造中間值過渡，避免極端跳躍
      const voiceBaseline = 0.15; // 基礎活動度，確保最小運動
      const voiceSmoothCurve = Math.tanh(voiceIntensity * 3) * 1.8; // 使用tanh創造平滑S曲線
      const voiceDynamicRange = voiceBaseline + voiceSmoothCurve * (1.0 - voiceBaseline); // 0.15-1.95範圍
      
      // 背景音樂強度處理 - 次要影響因素（20%權重）
      const musicBaseline = 0.05; // 音樂基礎活動度
      const musicSmoothCurve = Math.tanh(musicIntensity * 2.5) * 0.6; // 平滑音樂曲線
      const musicDynamicRange = musicBaseline + musicSmoothCurve * (1.0 - musicBaseline); // 0.05-0.65範圍
      
      // 合併動態範圍 - 語音主導，確保平滑過渡
      const rawCombinedRange = voiceDynamicRange * 0.8 + musicDynamicRange * 0.2;
      const finalDynamicRange = Math.max(rawCombinedRange, 0.1); // 確保最小活動度 0.1
      
      // 2. 時間扭曲因子 - 使用更溫和的變化
      quantumPhaseRef.current += delta * finalDynamicRange;
      
      // 溫和的慢速因子：0.5-1.0範圍
      const timeWarpSlow = 0.5 + Math.sin(quantumPhaseRef.current * 0.1) * 0.25 + 0.25;
      
      // 溫和的快速因子：1.0-2.0範圍  
      const timeWarpFast = 1.0 + Math.cos(quantumPhaseRef.current * 0.3) * 0.5 + 0.5;
      
      timeWarpFactorsRef.current = { slow: timeWarpSlow, fast: timeWarpFast };
      
      // 3. 混沌吸引子 (簡化的Lorenz系統)
      const chaos = chaosAttractorRef.current;
      const sigma = 10, rho = 28, beta = 8/3;
      const dt = delta * (0.01 + finalDynamicRange * 0.02);
      
      chaos.x += sigma * (chaos.y - chaos.x) * dt;
      chaos.y += (chaos.x * (rho - chaos.z) - chaos.y) * dt;
      chaos.z += (chaos.x * chaos.y - beta * chaos.z) * dt;
      
      // 將混沌值歸一化到合理範圍
      const chaosNormalized = {
        x: Math.tanh(chaos.x * 0.05) * 0.02,
        y: Math.tanh(chaos.y * 0.05) * 0.02,
        z: Math.tanh(chaos.z * 0.05) * 0.01
      };

      // 始終執行繞原點的徘徊動畫
      // 使用正弦波創造自然的飄浮效果
      const baseWaveSpeedX = 0.3; // X軸徘徊基礎速度
      const baseWaveSpeedY = 0.5; // Y軸徘徊基礎速度
      const baseWaveSpeedZ = 0.2; // Z軸徘徊基礎速度
      
      // 4. 多重現實疊加
      const realities = realityLayersRef.current;
      let realityOffsetX = 0, realityOffsetY = 0, realityOffsetZ = 0;
      
      realities.forEach((reality, i) => {
        reality.phase += delta * (0.1 + i * 0.05) * timeWarpFactorsRef.current.fast;
        reality.intensity = Math.sin(reality.phase) * Math.cos(reality.phase * 1.7) * finalDynamicRange;
        
        const layerWeight = 1 / (i + 1); // 越高層影響越小
        realityOffsetX += Math.sin(reality.phase * (i + 1)) * reality.intensity * layerWeight * 0.01;
        realityOffsetY += Math.cos(reality.phase * (i + 1.3)) * reality.intensity * layerWeight * 0.008;
        realityOffsetZ += Math.sin(reality.phase * (i + 0.7)) * reality.intensity * layerWeight * 0.005;
      });
      
      // 5. 量子不確定性 - 微觀隨機擾動
      const quantumUncertainty = {
        x: (Math.random() - 0.5) * 0.001 * Math.sqrt(finalDynamicRange),
        y: (Math.random() - 0.5) * 0.001 * Math.sqrt(finalDynamicRange),
        z: (Math.random() - 0.5) * 0.0005 * Math.sqrt(finalDynamicRange)
      };

      // 添加隨機速度變化 - 現在受時間扭曲影響
      const warpedTime = time * timeWarpFactorsRef.current.slow + time * timeWarpFactorsRef.current.fast * 0.1;
      const randomSpeedVariationX = 0.8 + Math.sin(warpedTime * 0.1) * 0.4 + Math.cos(warpedTime * 0.07) * 0.3;
      const randomSpeedVariationY = 0.8 + Math.sin(warpedTime * 0.13 + Math.PI/3) * 0.5 + Math.cos(warpedTime * 0.09) * 0.2;
      const randomSpeedVariationZ = 0.8 + Math.sin(warpedTime * 0.08 + Math.PI/6) * 0.3 + Math.cos(warpedTime * 0.12) * 0.4;
      
      const baseDriftRangeX = 0.04; // X軸徘徊基礎範圍
      const baseDriftRangeY = 0.025; // Y軸徘徊基礎範圍
      const baseDriftRangeZ = 0.06; // Z軸徘徊基礎範圍

      // 如果在說話，增加一些隨機變化和額外的運動強度
      const speakingMultiplier = isSpeaking ? 1.4 : 1.0; // 增加說話時的運動倍數
      const randomFactor = isSpeaking ? (0.7 + Math.random() * 0.6) : 1.0; // 增加隨機變化範圍

      // 音樂強度影響 - 現在使用非線性映射
      const musicSpeedBoost = 1.0 + finalDynamicRange; // 使用新的動態範圍
      const musicRandomBoost = voiceIntensity > 0.3 ? (0.9 + Math.random() * 0.2) : 1.0;

      // 計算實際的運動參數
      const waveSpeedX = baseWaveSpeedX * randomSpeedVariationX * speakingMultiplier * randomFactor * musicSpeedBoost * musicRandomBoost;
      const waveSpeedY = baseWaveSpeedY * randomSpeedVariationY * speakingMultiplier * randomFactor * musicSpeedBoost * musicRandomBoost;
      const waveSpeedZ = baseWaveSpeedZ * randomSpeedVariationZ * speakingMultiplier * musicSpeedBoost;
      
      // 音樂強度也影響運動範圍 - 使用非線性映射
      const musicRangeBoost = 1.0 + finalDynamicRange * 0.8;
      const driftRangeX = baseDriftRangeX * speakingMultiplier * musicRangeBoost;
      const driftRangeY = baseDriftRangeY * speakingMultiplier * musicRangeBoost;
      const driftRangeZ = baseDriftRangeZ * speakingMultiplier * musicRangeBoost;

      // 計算徘徊偏移 - 融入所有效果
      const driftX = Math.sin(warpedTime * waveSpeedX) * driftRangeX + chaosNormalized.x + realityOffsetX + quantumUncertainty.x;
      const driftY = Math.sin(warpedTime * waveSpeedY + Math.PI/3) * driftRangeY + chaosNormalized.y + realityOffsetY + quantumUncertainty.y;
      const driftZ = Math.sin(warpedTime * waveSpeedZ + Math.PI/6) * driftRangeZ + driftRangeZ * 0.6 + chaosNormalized.z + realityOffsetZ + quantumUncertainty.z;

      // 旋轉變化受量子效應影響
      const rotationIntensity = (isSpeaking ? 1.8 : 1.0) * (1.0 + finalDynamicRange * 0.6); // 增加說話時的旋轉強度
      const musicRotationSpeedBoost = 1.0 + finalDynamicRange * 1.2;
      const rotationVariationY = Math.sin(warpedTime * 0.3 * randomFactor * musicRotationSpeedBoost) * 0.05 * rotationIntensity + realityOffsetY * 2;
      const rotationVariationX = Math.sin(warpedTime * 0.4 * randomFactor * musicRotationSpeedBoost + Math.PI/4) * 0.03 * rotationIntensity + realityOffsetX * 2;

      // 說話時可能添加一些瞬間的位置跳躍
      let extraOffsetX = 0, extraOffsetY = 0, extraOffsetZ = 0;
      if (isSpeaking) {
        // 語音驅動的瞬移效果 - 根據語音強度調整
        teleportTimer.current += delta;
        const voiceBasedInterval = Math.max(0.05, 0.3 - voiceIntensity * 0.25); // 語音越強，間隔越短
        
        if (teleportTimer.current >= nextTeleportTime.current) {
          // 瞬移強度根據語音音量調整
          const voiceOffsetMultiplier = 0.5 + voiceIntensity * 1.5; // 0.5-2.0倍
          extraOffsetX = (Math.random() - 0.5) * 0.025 * voiceOffsetMultiplier;
          extraOffsetY = (Math.random() - 0.5) * 0.025 * voiceOffsetMultiplier;
          extraOffsetZ = (Math.random() - 0.5) * 0.015 * voiceOffsetMultiplier;
          
          teleportTimer.current = 0;
          nextTeleportTime.current = voiceBasedInterval + Math.random() * voiceBasedInterval;
        }
      }

      // 量子現實撕裂效果 - 語音高潮時的極端視覺
      if (voiceIntensity > 0.85) {
        // 6. 現實撕裂 - 不受控的受控
        const riftIntensity = Math.pow((voiceIntensity - 0.85) / 0.15, 1.5); // 0-1範圍的撕裂強度，更溫和的曲線
        
        // 空間扭曲 - 不同維度的時間流速
        const dimensionX = Math.sin(warpedTime * 5 + chaos.x * 0.1) * riftIntensity * 0.08;
        const dimensionY = Math.cos(warpedTime * 7 + chaos.y * 0.1) * riftIntensity * 0.06;
        const dimensionZ = Math.sin(warpedTime * 3 + chaos.z * 0.1) * riftIntensity * 0.04;
        
        // 量子跳躍 - 瞬間位置變化
        if (Math.random() < riftIntensity * 0.1) {
          const jumpDistance = riftIntensity * 0.1;
          extraOffsetX += (Math.random() - 0.5) * jumpDistance;
          extraOffsetY += (Math.random() - 0.5) * jumpDistance;
          extraOffsetZ += (Math.random() - 0.5) * jumpDistance * 0.5;
        }
        
        // 時空螺旋 - 極端的軌道運動
        const spiralRadius = riftIntensity * 0.15;
        const spiralSpeed = warpedTime * (10 + riftIntensity * 20);
        const spiralX = Math.cos(spiralSpeed) * spiralRadius * Math.sin(spiralSpeed * 0.3);
        const spiralY = Math.sin(spiralSpeed * 1.1) * spiralRadius * Math.cos(spiralSpeed * 0.2);
        const spiralZ = Math.sin(spiralSpeed * 0.7) * spiralRadius * 0.3 * Math.sin(spiralSpeed * 0.1);
        
        extraOffsetX += dimensionX + spiralX;
        extraOffsetY += dimensionY + spiralY;
        extraOffsetZ += dimensionZ + spiralZ;
        
        // 現實分層 - 同時存在多個位置的疊加
        realityLayersRef.current.forEach((reality, i) => {
          if (riftIntensity > 0.5) {
            const layerPhase = reality.phase + warpedTime * (i + 1) * 2;
            const layerIntensity = riftIntensity * reality.intensity * 0.1;
            
            extraOffsetX += Math.sin(layerPhase) * layerIntensity;
            extraOffsetY += Math.cos(layerPhase * 1.3) * layerIntensity * 0.8;
            extraOffsetZ += Math.sin(layerPhase * 0.7) * layerIntensity * 0.5;
          }
        });
      } else if (musicIntensity > 0.8 && !isSpeaking) {
        // 僅在不說話且音樂很強時，提供輕微的背景音樂驅動效果
        const musicRiftIntensity = Math.pow((musicIntensity - 0.8) / 0.2, 1.5) * 0.3; // 降低強度
        
        // 輕微的音樂驅動軌道運動
        const musicOrbitRadius = musicRiftIntensity * 0.02;
        const musicOrbitSpeed = warpedTime * (3.0 + musicIntensity * 2.0);
        extraOffsetX += Math.cos(musicOrbitSpeed) * musicOrbitRadius;
        extraOffsetY += Math.sin(musicOrbitSpeed * 1.2) * musicOrbitRadius * 0.7;
        extraOffsetZ += Math.sin(musicOrbitSpeed * 0.8) * musicOrbitRadius * 0.4;
      }

      // 設置最終位置（基於初始位置加上所有偏移）
      group.current.position.set(
        initialPosition.current.x + driftX + extraOffsetX,
        initialPosition.current.y + driftY + extraOffsetY,
        initialPosition.current.z + driftZ + extraOffsetZ
      );

      // 設置旋轉變化（基於初始旋轉加上變化）
      group.current.rotation.set(
        initialRotation.current.x + rotationVariationX,
        initialRotation.current.y + rotationVariationY,
        initialRotation.current.z
      );
    }

    if (!meshRef.current?.morphTargetInfluences || !localMorphTargetDictionary || Object.keys(localMorphTargetDictionary).length === 0) {
      return; 
    }
    
    const influences = meshRef.current.morphTargetInfluences;
    const dictionary = localMorphTargetDictionary;
    
    // --- 新的權重計算邏輯 --- 
    const trajectoryWeights = calculateCurrentTrajectoryWeights(); // 1. 情緒軌跡權重 (直接計算)
    const manualOrPresetTargets = manualOrPresetTargetsRef.current; // 2. 手動/預設權重 (來自 store)
    const audioLipsyncTargets = audioLipsyncTargetsRef.current; // 3. 語音口型權重 (來自 store)
    const isSpeaking = isSpeakingRef.current; // 4. 說話狀態

    // 5. 判斷是否有手動/預設激活
    //    (簡單檢查 manualOrPresetTargets 是否有非零值，或更複雜的邏輯)
    //    這裡使用一個簡化判斷：如果 manualOrPresetTargets 不是空對象就認為激活
    const isManualOrPresetActive = Object.keys(manualOrPresetTargets).length > 0 && 
                                    Object.values(manualOrPresetTargets).some(v => v > 0.01);

    // 6. 確定基礎表情
    const baseEmotion = isManualOrPresetActive ? manualOrPresetTargets : trajectoryWeights;

    // 7. 獲取語音口型 (只有在說話時)
    const audioShapes = isSpeaking ? audioLipsyncTargets : {};

    // 8. 合併：以 baseEmotion 為基礎，用 audioShapes 覆蓋
    const finalTargetWeights = {
      ...baseEmotion,
      ...audioShapes // 如果 audioShapes 中有鍵，會覆蓋 baseEmotion 中的同名鍵
    };

    // logger.debug("[useFrame] Final Weights:", LogCategory.MODEL, finalTargetWeights);
    // --- 權重計算結束 ---
    
    // --- Apply final weights with Lerp (保持不變) --- 
    Object.keys(dictionary).forEach(name => {
      const index = dictionary[name];
      if (index !== undefined && index < influences.length) {
        const targetValue = finalTargetWeights[name] ?? 0;
        const currentValue = influences[index];
        if (Math.abs(currentValue - targetValue) > 0.01) { 
          const lerpFactor = Math.min(delta * 25, 1); 
          influences[index] = THREE.MathUtils.lerp(currentValue, targetValue, lerpFactor);
        } else if (currentValue !== targetValue) {
          influences[index] = targetValue;
        } 
      }
    });
    // --- Apply End ---
  });
  // --- 更新結束 ---

  // 更新返回的 JSX
  return (
    <group ref={group} position={position} rotation={rotation}>
      {/* 使用drei的Center組件包裹scene，讓模型以視覺中心點進行縮放 */}
      <Center scale={scale} position={[0, 0, 0]}>
        <primitive 
          object={scene} 
          key={headModelUrl} 
        />
      </Center>
    </group>
  );
};

// 導出 HeadModel
// export default HeadModel; // <-- 如果有 default export 