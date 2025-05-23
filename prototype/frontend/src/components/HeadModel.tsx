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
      // 始終執行繞原點的徘徊動畫
      // 使用正弦波創造自然的飄浮效果
      const baseWaveSpeedX = 0.3; // X軸徘徊基礎速度
      const baseWaveSpeedY = 0.5; // Y軸徘徊基礎速度
      const baseWaveSpeedZ = 0.2; // Z軸徘徊基礎速度
      
      // 添加隨機速度變化
      const randomSpeedVariationX = 0.8 + Math.sin(time * 0.1) * 0.4 + Math.cos(time * 0.07) * 0.3; // 0.1-1.5倍變化
      const randomSpeedVariationY = 0.8 + Math.sin(time * 0.13 + Math.PI/3) * 0.5 + Math.cos(time * 0.09) * 0.2; // 0.1-1.5倍變化
      const randomSpeedVariationZ = 0.8 + Math.sin(time * 0.08 + Math.PI/6) * 0.3 + Math.cos(time * 0.12) * 0.4; // 0.1-1.5倍變化
      
      const baseDriftRangeX = 0.04; // X軸徘徊基礎範圍
      const baseDriftRangeY = 0.025; // Y軸徘徊基礎範圍
      const baseDriftRangeZ = 0.06; // Z軸徘徊基礎範圍

      // 如果在說話，增加一些隨機變化和額外的運動強度
      const speakingMultiplier = isSpeakingRef.current ? 1.3 : 1.0; // 說話時運動倍數也稍微降低
      const randomFactor = isSpeakingRef.current ? (0.8 + Math.random() * 0.4) : 1.0; // 說話時加入隨機因子

      // 添加音樂強度影響
      const musicIntensity = bgmIntensityRef.current;
      const musicSpeedBoost = 1.0 + musicIntensity * 1.5; // 音樂強度可以增加最多1.5倍的速度
      const musicRandomBoost = musicIntensity > 0.3 ? (0.9 + Math.random() * 0.2) : 1.0; // 強音樂時增加隨機性

      // 計算實際的運動參數（結合基礎速度、隨機變化、說話狀態和音樂強度）
      const waveSpeedX = baseWaveSpeedX * randomSpeedVariationX * speakingMultiplier * randomFactor * musicSpeedBoost * musicRandomBoost;
      const waveSpeedY = baseWaveSpeedY * randomSpeedVariationY * speakingMultiplier * randomFactor * musicSpeedBoost * musicRandomBoost;
      const waveSpeedZ = baseWaveSpeedZ * randomSpeedVariationZ * speakingMultiplier * musicSpeedBoost;
      
      // 音樂強度也影響運動範圍
      const musicRangeBoost = 1.0 + musicIntensity * 0.8; // 音樂強度可以增加最多80%的運動範圍
      const driftRangeX = baseDriftRangeX * speakingMultiplier * musicRangeBoost;
      const driftRangeY = baseDriftRangeY * speakingMultiplier * musicRangeBoost;
      const driftRangeZ = baseDriftRangeZ * speakingMultiplier * musicRangeBoost;

      // 計算徘徊偏移
      const driftX = Math.sin(time * waveSpeedX) * driftRangeX;
      const driftY = Math.sin(time * waveSpeedY + Math.PI/3) * driftRangeY; // 加上相位差
      const driftZ = Math.sin(time * waveSpeedZ + Math.PI/6) * driftRangeZ + driftRangeZ * 0.6; // 讓它偏向前面

      // 旋轉變化受音樂強度影響
      const rotationIntensity = (isSpeakingRef.current ? 1.8 : 1.0) * (1.0 + musicIntensity * 0.6);
      const musicRotationSpeedBoost = 1.0 + musicIntensity * 1.2; // 音樂影響旋轉速度
      const rotationVariationY = Math.sin(time * 0.3 * randomFactor * musicRotationSpeedBoost) * 0.05 * rotationIntensity; // 輕微左右搖擺
      const rotationVariationX = Math.sin(time * 0.4 * randomFactor * musicRotationSpeedBoost + Math.PI/4) * 0.03 * rotationIntensity; // 輕微上下點頭

      // 說話時可能添加一些瞬間的位置跳躍
      let extraOffsetX = 0, extraOffsetY = 0, extraOffsetZ = 0;
      if (isSpeakingRef.current) {
        // 每隔一段時間添加小幅度的隨機偏移
        teleportTimer.current += delta;
        if (teleportTimer.current >= nextTeleportTime.current) {
          extraOffsetX = (Math.random() - 0.5) * 0.02;
          extraOffsetY = (Math.random() - 0.5) * 0.02;
          extraOffsetZ = (Math.random() - 0.5) * 0.01;
          
          teleportTimer.current = 0;
          nextTeleportTime.current = Math.random() * 0.5 + 0.1; // 0.1-0.6秒隨機間隔
        }
      }

      // 音樂高潮時的特殊效果
      if (musicIntensity > 0.7) {
        // 強音樂時增加軌道式運動
        const orbitRadius = musicIntensity * 0.03;
        const orbitSpeed = time * (2.0 + musicIntensity * 3.0);
        extraOffsetX += Math.cos(orbitSpeed) * orbitRadius;
        extraOffsetY += Math.sin(orbitSpeed * 1.3) * orbitRadius * 0.6;
        extraOffsetZ += Math.sin(orbitSpeed * 0.7) * orbitRadius * 0.4;
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