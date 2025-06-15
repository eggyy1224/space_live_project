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

// 擴展的網格類型，包含morphTargets屬性 - 支持 Mesh 和 SkinnedMesh
interface MeshWithMorphs extends THREE.Mesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

interface SkinnedMeshWithMorphs extends THREE.SkinnedMesh {
  morphTargetDictionary?: {[key: string]: number};
  morphTargetInfluences?: number[];
}

// 聯合類型，支持兩種網格類型
type MorphTargetMesh = MeshWithMorphs | SkinnedMeshWithMorphs;

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
  const meshRef = useRef<MorphTargetMesh | null>(null);
  // 新增：支持多個 mesh 的引用數組
  const meshRefs = useRef<MorphTargetMesh[]>([]);
  
  // === 量子機率雲系統 - 三頭效果 ===
  const quantumGroup1 = useRef<THREE.Group>(null); // 中心頭部
  const quantumGroup2 = useRef<THREE.Group>(null); // 左側機率位置
  const quantumGroup3 = useRef<THREE.Group>(null); // 右側機率位置
  
  // 量子機率雲參數
  const quantumCloudRef = useRef({
    positions: [
      { x: 0, y: 0, z: 0, probability: 1.0 },     // 中心位置 - 總是存在
      { x: -0.3, y: 0.1, z: -0.1, probability: 0 }, // 左側位置
      { x: 0.3, y: -0.1, z: 0.1, probability: 0 }   // 右側位置
    ],
         targetProbabilities: [1.0, 0, 0], // 目標機率
     transitionSpeed: 12.0, // 提高轉換速度讓反應更快
    coherencePhase: 0,
    entanglementFactor: 0
  });
  
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

  // === 量子頭透明度控制 ===
  useEffect(() => {
    const updateQuantumOpacity = () => {
      const quantumCloud = quantumCloudRef.current;
      
             // 更新量子頭2的透明度 - 更高的透明度和對比
       if (quantumGroup2.current) {
         const probability = quantumCloud.positions[1].probability;
         const opacity = Math.max(0.05, probability); // 降低最小透明度
         quantumGroup2.current.traverse((child) => {
           if (child instanceof THREE.Mesh || child instanceof THREE.SkinnedMesh) {
             if (child.material) {
               const materials = Array.isArray(child.material) ? child.material : [child.material];
               materials.forEach((mat: any) => {
                 if (mat) {
                   mat.transparent = true;
                   // 更高的透明度：說話時接近不透明
                   mat.opacity = opacity * 0.85; // 從 0.6 提升到 0.85
                   mat.needsUpdate = true;
                 }
               });
             }
           }
         });
       }
       
       // 更新量子頭3的透明度 - 更高的透明度和對比
       if (quantumGroup3.current) {
         const probability = quantumCloud.positions[2].probability;
         const opacity = Math.max(0.05, probability); // 降低最小透明度
         quantumGroup3.current.traverse((child) => {
           if (child instanceof THREE.Mesh || child instanceof THREE.SkinnedMesh) {
             if (child.material) {
               const materials = Array.isArray(child.material) ? child.material : [child.material];
               materials.forEach((mat: any) => {
                 if (mat) {
                   mat.transparent = true;
                   // 更高的透明度：說話時接近不透明
                   mat.opacity = opacity * 0.85; // 從 0.6 提升到 0.85
                   mat.needsUpdate = true;
                 }
               });
             }
           }
         });
       }
    };

    // 定期更新透明度
    const interval = setInterval(updateQuantumOpacity, 50); // 20fps 更新
    return () => clearInterval(interval);
  }, [scene]);

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
    meshRef.current = null;
    meshRefs.current = [];
    let combinedDict: Record<string, number> = {};

    if (scene) {
      const foundMeshes: MorphTargetMesh[] = [];
      
      scene.traverse((object) => {
        // 調整材質屬性以獲得自然的外觀
        if (object instanceof THREE.Mesh || object instanceof THREE.SkinnedMesh) {
          if (object.material) {
            const material = Array.isArray(object.material) ? object.material : [object.material];
            material.forEach((mat: any) => {
              if (mat.isMeshStandardMaterial || mat.isMeshPhysicalMaterial) {
                // 降低亮度，使用更自然的材質設定
                mat.emissive = new THREE.Color(0x000000); // 移除自發光
                mat.emissiveIntensity = 0.0; // 關閉自發光強度
                // 保留原始材質屬性的自然外觀
                // mat.roughness 和 mat.metalness 保持原始值
                mat.needsUpdate = true;
              }
              if (mat.isMeshLambertMaterial || mat.isMeshPhongMaterial) {
                // 對於舊式材質，使用適度的亮度調整
                if (mat.color) {
                  mat.color.multiplyScalar(1.0); // 保持原始亮度
                }
                mat.needsUpdate = true;
              }
            });
          }
        }
        
        // 檢查標準 Mesh
        if (object instanceof THREE.Mesh && object.morphTargetInfluences && object.morphTargetDictionary) {
          const meshWithMorphs = object as MeshWithMorphs;
          if (meshWithMorphs.morphTargetInfluences && meshWithMorphs.morphTargetDictionary) {
            foundMeshes.push(meshWithMorphs);
            // 合併 morph target 字典
            Object.assign(combinedDict, meshWithMorphs.morphTargetDictionary);
            // 初始化 morph target influences
            meshWithMorphs.morphTargetInfluences.fill(0);
            logger.info(`HeadModel: Found Mesh with morph targets: ${object.name}`, LogCategory.MODEL, JSON.stringify(meshWithMorphs.morphTargetDictionary));
          }
        }
        
        // 檢查 SkinnedMesh
        if (object instanceof THREE.SkinnedMesh && object.morphTargetInfluences && object.morphTargetDictionary) {
          const skinnedMeshWithMorphs = object as SkinnedMeshWithMorphs;
          if (skinnedMeshWithMorphs.morphTargetInfluences && skinnedMeshWithMorphs.morphTargetDictionary) {
            foundMeshes.push(skinnedMeshWithMorphs);
            // 合併 morph target 字典
            Object.assign(combinedDict, skinnedMeshWithMorphs.morphTargetDictionary);
            // 初始化 morph target influences
            skinnedMeshWithMorphs.morphTargetInfluences.fill(0);
            logger.info(`HeadModel: Found SkinnedMesh with morph targets: ${object.name}`, LogCategory.MODEL, JSON.stringify(skinnedMeshWithMorphs.morphTargetDictionary));
          }
        }
      });

      // 設置引用
      meshRefs.current = foundMeshes;
      if (foundMeshes.length > 0) {
        meshRef.current = foundMeshes[0]; // 保持向後兼容性
        setLocalMorphTargetDictionary(combinedDict);
        logger.info(`HeadModel: Found ${foundMeshes.length} meshes with morph targets. Combined dictionary:`, LogCategory.MODEL, JSON.stringify(combinedDict));
      } else {
        setLocalMorphTargetDictionary({});
        logger.warn('HeadModel: No mesh with morph targets found, but scene loaded.', LogCategory.MODEL, `URL: ${headModelUrl}`);
      }

      // 只要 scene 存在，就設置 headModelLoaded 為 true
      setHeadModelLoaded(true);
      logger.info('HeadModel: Scene loaded, setting headModelLoaded state to true in Zustand.', LogCategory.MODEL);

    } else {
      setLocalMorphTargetDictionary({});
      setHeadModelLoaded(false);
      logger.error('HeadModel: Scene failed to load.', LogCategory.MODEL, `URL: ${headModelUrl}`);
    }
    // 依賴項更新為 headModelUrl
  }, [headModelUrl, scene, setHeadModelLoaded]);
  // --- 更新結束 ---

  // --- 更新 useFrame，使用新的權重合併邏輯 ---
  useFrame((state, delta) => {
    const time = state.clock.elapsedTime; 

    if (group.current) {
      // === 量子機率雲系統 ===
      const musicIntensity = bgmIntensityRef.current;
      const voiceVolume = audioAverageVolumeRef.current;
      const isSpeaking = isSpeakingRef.current;
      
      // 量子機率雲控制 - 說話時激活三頭效果
      const quantumCloud = quantumCloudRef.current;
      
      if (isSpeaking && voiceVolume > 0.02) {
        // 說話時：激活量子疊加態 - 三個位置同時存在
        const speechIntensity = Math.min(voiceVolume * 12, 1.0); // 提高敏感度
        
                 // 根據語音強度決定機率分布 - 更敏感的門檻
         if (speechIntensity > 0.4) {
           // 強烈說話：三頭完全顯現 (降低門檻從 0.7 到 0.4)
           quantumCloud.targetProbabilities = [1.0, 0.9, 0.9];
           quantumCloud.entanglementFactor = speechIntensity;
         } else if (speechIntensity > 0.15) {
           // 中等說話：明顯的三頭效果 (降低門檻從 0.3 到 0.15)
           quantumCloud.targetProbabilities = [1.0, 0.6, 0.6];
           quantumCloud.entanglementFactor = speechIntensity * 0.7;
         } else {
           // 輕微說話：輕微的量子分裂 (門檻 0.02-0.15)
           quantumCloud.targetProbabilities = [1.0, 0.3, 0.3];
           quantumCloud.entanglementFactor = speechIntensity * 0.5;
         }
        
        // 量子相位同步 - 讓三個頭的動作有關聯性
        quantumCloud.coherencePhase += delta * (5 + speechIntensity * 10);
        
             } else {
         // 不說話時：回到單一狀態（量子坍縮）
         quantumCloud.targetProbabilities = [1.0, 0, 0];
         quantumCloud.entanglementFactor *= 0.98; // 更慢的消失速度，避免閃爍
         quantumCloud.coherencePhase += delta * 2;
       }
      
      // 平滑過渡機率值
      quantumCloud.positions.forEach((pos, i) => {
        const target = quantumCloud.targetProbabilities[i];
        const current = pos.probability;
        const lerpSpeed = quantumCloud.transitionSpeed * delta;
        pos.probability = THREE.MathUtils.lerp(current, target, lerpSpeed);
      });
      
      // === 原有的量子徘徊系統（現在應用到每個機率位置）===
      
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
      
      // 將混沌值歸一化到合理範圍 (移除，在下面重新定義)

      // === 新的「中心清晰，四周殘像」系統 ===
      
      // 1. 微妙的中心徘徊 - 大幅縮小範圍，保持在中心
      const centerWaveSpeedX = 0.8; // 提高頻率但縮小範圍
      const centerWaveSpeedY = 1.2; 
      const centerWaveSpeedZ = 0.6;
      
      // 極小的中心徘徊範圍 - 讓主體保持在中心
      const centerDriftRangeX = 0.008; // 從 0.04 縮小到 0.008
      const centerDriftRangeY = 0.006; // 從 0.025 縮小到 0.006
      const centerDriftRangeZ = 0.012; // 從 0.06 縮小到 0.012
      
      // 2. 視覺殘像效果 - 通過快速微振動創造殘像感
      const warpedTime = time * timeWarpFactorsRef.current.slow + time * timeWarpFactorsRef.current.fast * 0.1;
      
      // 高頻微振動 - 創造視覺殘像
      const afterimageFreqX = 15 + finalDynamicRange * 25; // 高頻振動
      const afterimageFreqY = 18 + finalDynamicRange * 30;
      const afterimageFreqZ = 12 + finalDynamicRange * 20;
      
      // 微振動幅度 - 很小但足以創造視覺效果
      const afterimageAmpX = 0.003 + finalDynamicRange * 0.007; // 微小振動
      const afterimageAmpY = 0.002 + finalDynamicRange * 0.005;
      const afterimageAmpZ = 0.001 + finalDynamicRange * 0.003;
      
      // 3. 多層殘像疊加 - 不同頻率的微振動
      let afterimageOffsetX = 0, afterimageOffsetY = 0, afterimageOffsetZ = 0;
      
      // 第一層：基礎殘像
      afterimageOffsetX += Math.sin(warpedTime * afterimageFreqX) * afterimageAmpX;
      afterimageOffsetY += Math.sin(warpedTime * afterimageFreqY + Math.PI/4) * afterimageAmpY;
      afterimageOffsetZ += Math.sin(warpedTime * afterimageFreqZ + Math.PI/6) * afterimageAmpZ;
      
      // 第二層：高頻殘像
      afterimageOffsetX += Math.sin(warpedTime * afterimageFreqX * 2.3) * afterimageAmpX * 0.6;
      afterimageOffsetY += Math.sin(warpedTime * afterimageFreqY * 1.7 + Math.PI/3) * afterimageAmpY * 0.6;
      afterimageOffsetZ += Math.sin(warpedTime * afterimageFreqZ * 2.1 + Math.PI/2) * afterimageAmpZ * 0.6;
      
      // 第三層：超高頻殘像（說話時更明顯）
      if (isSpeaking) {
        const speechAfterimageBoost = 1.0 + voiceIntensity * 2.0;
        afterimageOffsetX += Math.sin(warpedTime * afterimageFreqX * 4.1) * afterimageAmpX * 0.4 * speechAfterimageBoost;
        afterimageOffsetY += Math.sin(warpedTime * afterimageFreqY * 3.7 + Math.PI/5) * afterimageAmpY * 0.4 * speechAfterimageBoost;
        afterimageOffsetZ += Math.sin(warpedTime * afterimageFreqZ * 3.9 + Math.PI/7) * afterimageAmpZ * 0.4 * speechAfterimageBoost;
      }
      
      // 4. 量子不確定性 - 更微妙的隨機擾動
      const quantumUncertainty = {
        x: (Math.random() - 0.5) * 0.0005 * Math.sqrt(finalDynamicRange), // 縮小一半
        y: (Math.random() - 0.5) * 0.0005 * Math.sqrt(finalDynamicRange),
        z: (Math.random() - 0.5) * 0.0003 * Math.sqrt(finalDynamicRange)
      };
      
      // 5. 混沌效果 - 保持但縮小範圍
      const chaosNormalized = {
        x: Math.tanh(chaosAttractorRef.current.x * 0.05) * 0.005, // 從 0.02 縮小到 0.005
        y: Math.tanh(chaosAttractorRef.current.y * 0.05) * 0.005, // 從 0.02 縮小到 0.005
        z: Math.tanh(chaosAttractorRef.current.z * 0.05) * 0.003  // 從 0.01 縮小到 0.003
      };
      
      // 6. 說話時的動態增強
      const speakingMultiplier = isSpeaking ? 1.2 : 1.0; // 降低說話時的倍數
      const musicRangeBoost = 1.0 + finalDynamicRange * 0.3; // 降低音樂影響
      
      // 最終的中心徘徊範圍
      const finalDriftRangeX = centerDriftRangeX * speakingMultiplier * musicRangeBoost;
      const finalDriftRangeY = centerDriftRangeY * speakingMultiplier * musicRangeBoost;
      const finalDriftRangeZ = centerDriftRangeZ * speakingMultiplier * musicRangeBoost;
      
      // 計算最終的中心徘徊偏移
      const centerDriftX = Math.sin(warpedTime * centerWaveSpeedX) * finalDriftRangeX;
      const centerDriftY = Math.sin(warpedTime * centerWaveSpeedY + Math.PI/3) * finalDriftRangeY;
      const centerDriftZ = Math.sin(warpedTime * centerWaveSpeedZ + Math.PI/6) * finalDriftRangeZ;
      
      // 合併所有效果 - 主要是殘像效果
      const driftX = centerDriftX + afterimageOffsetX + chaosNormalized.x + quantumUncertainty.x;
      const driftY = centerDriftY + afterimageOffsetY + chaosNormalized.y + quantumUncertainty.y;
      const driftZ = centerDriftZ + afterimageOffsetZ + chaosNormalized.z + quantumUncertainty.z;

      // 旋轉變化 - 配合殘像效果的微妙旋轉
      const rotationIntensity = (isSpeaking ? 1.3 : 1.0) * (1.0 + finalDynamicRange * 0.4); // 降低旋轉強度
      const musicRotationSpeedBoost = 1.0 + finalDynamicRange * 0.6; // 降低音樂影響
      
      // 微妙的旋轉變化 - 配合中心徘徊
      const rotationVariationY = Math.sin(warpedTime * 0.4 * musicRotationSpeedBoost) * 0.02 * rotationIntensity; // 縮小旋轉範圍
      const rotationVariationX = Math.sin(warpedTime * 0.5 * musicRotationSpeedBoost + Math.PI/4) * 0.015 * rotationIntensity; // 縮小旋轉範圍
      
      // 添加殘像旋轉效果
      const afterimageRotationY = Math.sin(warpedTime * afterimageFreqY * 0.1) * 0.005 * finalDynamicRange;
      const afterimageRotationX = Math.sin(warpedTime * afterimageFreqX * 0.1 + Math.PI/3) * 0.003 * finalDynamicRange;

      // 說話時的微瞬移效果 - 配合殘像系統
      let extraOffsetX = 0, extraOffsetY = 0, extraOffsetZ = 0;
      if (isSpeaking) {
        // 語音驅動的微瞬移效果 - 縮小範圍但增加頻率
        teleportTimer.current += delta;
        const voiceBasedInterval = Math.max(0.03, 0.15 - voiceIntensity * 0.1); // 更頻繁但更微妙

        if (teleportTimer.current >= nextTeleportTime.current) {
          // 微瞬移強度 - 大幅縮小但保持效果
          const voiceOffsetMultiplier = 0.3 + voiceIntensity * 0.7; // 0.3-1.0倍
          extraOffsetX = (Math.random() - 0.5) * 0.008 * voiceOffsetMultiplier; // 從 0.025 縮小到 0.008
          extraOffsetY = (Math.random() - 0.5) * 0.006 * voiceOffsetMultiplier; // 從 0.025 縮小到 0.006
          extraOffsetZ = (Math.random() - 0.5) * 0.004 * voiceOffsetMultiplier; // 從 0.015 縮小到 0.004

          teleportTimer.current = 0;
          nextTeleportTime.current = voiceBasedInterval + Math.random() * voiceBasedInterval * 0.5;
        }
      }

      // 極端語音時的增強殘像效果 - 保持在中心但增強視覺效果
      if (voiceIntensity > 0.85) {
        // 超強殘像效果 - 不移動位置，只增強視覺震動
        const extremeIntensity = Math.pow((voiceIntensity - 0.85) / 0.15, 1.5);
        
        // 增強殘像振動頻率和幅度
        const extremeAfterimageX = Math.sin(warpedTime * afterimageFreqX * 6) * afterimageAmpX * 3 * extremeIntensity;
        const extremeAfterimageY = Math.sin(warpedTime * afterimageFreqY * 7) * afterimageAmpY * 3 * extremeIntensity;
        const extremeAfterimageZ = Math.sin(warpedTime * afterimageFreqZ * 5) * afterimageAmpZ * 2 * extremeIntensity;
        
        // 添加到額外偏移，但範圍很小
        extraOffsetX += extremeAfterimageX;
        extraOffsetY += extremeAfterimageY;
        extraOffsetZ += extremeAfterimageZ;
        
      } else if (musicIntensity > 0.8 && !isSpeaking) {
        // 音樂驅動的微妙殘像增強
        const musicAfterimageIntensity = Math.pow((musicIntensity - 0.8) / 0.2, 1.5) * 0.5;
        
        // 輕微的音樂殘像效果
        const musicAfterimageX = Math.sin(warpedTime * afterimageFreqX * 0.5) * afterimageAmpX * musicAfterimageIntensity;
        const musicAfterimageY = Math.sin(warpedTime * afterimageFreqY * 0.6) * afterimageAmpY * musicAfterimageIntensity;
        const musicAfterimageZ = Math.sin(warpedTime * afterimageFreqZ * 0.4) * afterimageAmpZ * musicAfterimageIntensity;
        
        extraOffsetX += musicAfterimageX;
        extraOffsetY += musicAfterimageY;
        extraOffsetZ += musicAfterimageZ;
      }

      // === 量子機率雲位置更新 ===
      // 為每個量子頭計算位置和透明度
      quantumCloud.positions.forEach((quantumPos, i) => {
        // 基礎機率位置
        const baseX = initialPosition.current.x + quantumPos.x;
        const baseY = initialPosition.current.y + quantumPos.y;
        const baseZ = initialPosition.current.z + quantumPos.z;
        
        // 每個量子頭都有相關但略有不同的擾動
        const phaseOffset = i * Math.PI * 0.67; // 120度相位差
        const coherentDriftX = driftX * (0.7 + 0.3 * Math.sin(quantumCloud.coherencePhase + phaseOffset));
        const coherentDriftY = driftY * (0.7 + 0.3 * Math.cos(quantumCloud.coherencePhase + phaseOffset));
        const coherentDriftZ = driftZ * (0.7 + 0.3 * Math.sin(quantumCloud.coherencePhase * 0.7 + phaseOffset));
        
        // 量子糾纏效果 - 說話時三個頭會有相關聯的額外運動
        let entanglementX = 0, entanglementY = 0, entanglementZ = 0;
        if (quantumCloud.entanglementFactor > 0.1) {
          const entanglementPhase = quantumCloud.coherencePhase * 2 + phaseOffset;
          entanglementX = Math.sin(entanglementPhase) * quantumCloud.entanglementFactor * 0.05;
          entanglementY = Math.cos(entanglementPhase * 1.3) * quantumCloud.entanglementFactor * 0.03;
          entanglementZ = Math.sin(entanglementPhase * 0.8) * quantumCloud.entanglementFactor * 0.02;
        }
        
        // 設置每個量子頭的位置
        const finalX = baseX + coherentDriftX + extraOffsetX + entanglementX;
        const finalY = baseY + coherentDriftY + extraOffsetY + entanglementY;
        const finalZ = baseZ + coherentDriftZ + extraOffsetZ + entanglementZ;
        
        if (i === 0 && group.current) {
          // 主要頭部（中心）
          group.current.position.set(finalX, finalY, finalZ);
          group.current.rotation.set(
            initialRotation.current.x + rotationVariationX + afterimageRotationX,
            initialRotation.current.y + rotationVariationY + afterimageRotationY,
            initialRotation.current.z
          );
        }
        
                 // 設置量子頭的位置（量子頭2和3在useFrame中動態更新）
         if (i === 1 && quantumGroup2.current) {
           quantumGroup2.current.position.set(finalX, finalY, finalZ);
           quantumGroup2.current.rotation.set(
             initialRotation.current.x + rotationVariationX + afterimageRotationX + entanglementX * 2,
             initialRotation.current.y + rotationVariationY + afterimageRotationY + entanglementY * 2,
             initialRotation.current.z + entanglementZ
           );
         } else if (i === 2 && quantumGroup3.current) {
           quantumGroup3.current.position.set(finalX, finalY, finalZ);
           quantumGroup3.current.rotation.set(
             initialRotation.current.x + rotationVariationX + afterimageRotationX - entanglementX * 2,
             initialRotation.current.y + rotationVariationY + afterimageRotationY - entanglementY * 2,
             initialRotation.current.z - entanglementZ
           );
         }
      });
    }

    if (meshRefs.current.length === 0 || !localMorphTargetDictionary || Object.keys(localMorphTargetDictionary).length === 0) {
      return; 
    }
    
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
    
    // --- Apply final weights with Lerp - 支持多個 mesh --- 
    meshRefs.current.forEach((mesh) => {
      if (!mesh.morphTargetInfluences || !mesh.morphTargetDictionary) return;
      
      const influences = mesh.morphTargetInfluences;
      const dictionary = mesh.morphTargetDictionary;
      
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
    });
    // --- Apply End ---
  });
  // --- 更新結束 ---

  // 更新返回的 JSX - 量子機率雲三頭系統
  return (
    <>
      {/* 主要頭部（中心） - 總是存在 */}
      <group ref={group} position={position} rotation={rotation}>
        <Center scale={scale} position={[0, 0, 0]}>
          <primitive 
            object={scene} 
            key={`${headModelUrl}-main`} 
          />
        </Center>
      </group>
      
      {/* 量子機率頭部 1（左側） - 說話時出現 */}
      {quantumCloudRef.current.positions[1].probability > 0.02 && scene && (
        <group 
          ref={quantumGroup2} 
          position={position} 
          rotation={rotation}
        >
          <Center scale={scale} position={[0, 0, 0]}>
            <primitive 
              object={scene.clone(true)} 
              key={`${headModelUrl}-quantum1`}
            />
          </Center>
        </group>
      )}
      
      {/* 量子機率頭部 2（右側） - 說話時出現 */}
      {quantumCloudRef.current.positions[2].probability > 0.02 && scene && (
        <group 
          ref={quantumGroup3} 
          position={position} 
          rotation={rotation}
        >
          <Center scale={scale} position={[0, 0, 0]}>
            <primitive 
              object={scene.clone(true)} 
              key={`${headModelUrl}-quantum2`}
            />
          </Center>
        </group>
      )}
    </>
  );
};

// 導出 HeadModel
// export default HeadModel; // <-- 如果有 default export 