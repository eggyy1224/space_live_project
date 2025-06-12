import React, { Suspense, useRef, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import { HeadModel } from "./HeadModel";
import CharacterModel from "./CharacterModel";
import DanceGroup from "./DanceGroup";
import DynamicAudioBackgrounds from "./DynamicAudioBackgrounds";
import RoomScene from "./RoomScene";
import { useStore } from "../store";
import * as THREE from "three";
import { useCameraManager, CameraPreset } from "../camera";
import { applyLightingPreset } from "../lighting/lightingRig";
import { CAMERA_PRESETS } from "../config/resources";

interface SceneContainerProps {
  headModelUrl: string;
  isHeadModelLoaded: boolean;
  showSpaceBackground: boolean;
  modelScale: [number, number, number];
}

// 新增全局燈光組件，使其隨著音樂變化
const DynamicLights = () => {
  const ambientLightRef = useRef<THREE.AmbientLight>(null);
  const directionalLightRef = useRef<THREE.DirectionalLight>(null);
  const bgmIntensity = useStore((s) => s.bgmIntensity);
  useEffect(() => {
    applyLightingPreset("dynamic");
  }, []);

  useFrame(() => {
    if (ambientLightRef.current) {
      // 讓環境光隨音樂強度變化（增加幅度）
      ambientLightRef.current.intensity = 2 + bgmIntensity * 10;
    }
    if (directionalLightRef.current) {
      // 讓方向光隨音樂強度變化（增加幅度）
      directionalLightRef.current.intensity = 1.2 + bgmIntensity * 8;

      // 讓燈光的顏色也隨著音樂強度變化（增加色彩變化的幅度）
      const baseColor = new THREE.Color(0xffffff);
      const accentColor = new THREE.Color(0xff44ff); // 更鮮豔的粉紫色
      directionalLightRef.current.color
        .copy(baseColor)
        .lerp(accentColor, Math.min(1, bgmIntensity * 1.5));
    }
  });

  return (
    <>
      <ambientLight ref={ambientLightRef} intensity={0.5} />
      <directionalLight
        ref={directionalLightRef}
        position={[10, 10, 5]}
        intensity={1.5}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
    </>
  );
};

const SceneContainer: React.FC<SceneContainerProps> = ({
  headModelUrl,
  isHeadModelLoaded,
  showSpaceBackground,
  modelScale,
}) => {
  // console.log('[SceneContainer] Rendering...');
  return (
    <Canvas
      shadows
      camera={{ position: [0, 0.5, 3], fov: 50 }}
      style={{ background: showSpaceBackground ? "#000010" : "#111a21" }}
    >
      <SceneContent
        headModelUrl={headModelUrl}
        isHeadModelLoaded={isHeadModelLoaded}
        showSpaceBackground={showSpaceBackground}
        modelScale={modelScale}
      />
    </Canvas>
  );
};

// 將場景內容提取到一個新組件中，以便在 Canvas 內部使用 useThree
const SceneContent: React.FC<SceneContainerProps> = ({
  headModelUrl,
  isHeadModelLoaded,
  showSpaceBackground,
  modelScale,
}) => {
  const { camera } = useThree();

  const cameraManager = useCameraManager(
    camera as THREE.PerspectiveCamera,
    CAMERA_PRESETS,
    "overview",
  );
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const randomMode = useStore((s) => s.randomMode); // 新增：監聽隨機模式狀態
  const cameraPreset = useStore((s) => s.cameraPreset); // 新增：監聽手動相機預設變化
  const cameraAngles = useStore((s) => s.cameraAngles);
  const cameraTransitionDuration = useStore((s) => s.cameraTransitionDuration);
  const orbitControlsRef = useRef<any>(null);

  // 房間場景狀態
  const showRoomScene = useStore((s) => s.showRoomScene);
  const roomSceneUrl = useStore((s) => s.roomSceneUrl);
  const roomPosition = useStore((s) => s.roomPosition);
  const roomRotation = useStore((s) => s.roomRotation);
  const roomScale = useStore((s) => s.roomScale);

  // 監聽手動相機預設變化
  useEffect(() => {
    if (!randomMode && cameraPreset && cameraPreset !== "roam") {
      console.log("Manual camera preset change:", cameraPreset);
      cameraManager.transitionTo(
        cameraPreset,
        cameraTransitionDuration || 1.5,
      );
    }
  }, [cameraPreset, randomMode, cameraTransitionDuration, cameraManager]);

  useEffect(() => {
    if (cameraAngles) {
      // 暫時禁用OrbitControls以避免衝突
      if (orbitControlsRef.current) {
        orbitControlsRef.current.enabled = false;
      }
      
      cameraManager.transitionAngles(
        cameraAngles[0],
        cameraAngles[1],
        cameraAngles[2],
        cameraTransitionDuration,
      );

      // 在轉換完成後重新啟用OrbitControls（加500ms緩衝）
      setTimeout(() => {
        if (orbitControlsRef.current) {
          orbitControlsRef.current.enabled = true;
        }
      }, (cameraTransitionDuration * 1000) + 500);
    }
  }, [cameraAngles, cameraTransitionDuration, cameraManager]);

  useEffect(() => {
    const switchView = () => {
      // 只在隨機模式開啟時才自動切換相機
      if (!randomMode) return;

      const presetNames = CAMERA_PRESETS.map((p) => p.name);
      const randomPresetName =
        presetNames[Math.floor(Math.random() * presetNames.length)];
      cameraManager.transitionTo(randomPresetName, 2.5); // 2.5 秒轉場

      // 隨機設定下一次切換的時間 (5 到 10 秒)
      const randomInterval = Math.random() * 5000 + 5000;
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(switchView, randomInterval);
    };

    if (randomMode) {
      // 隨機模式開啟時，初始延遲後開始第一次切換
      const initialDelay = setTimeout(switchView, 5000); // 5秒後第一次切換
      return () => {
        if (timerRef.current) clearTimeout(timerRef.current);
        clearTimeout(initialDelay);
      };
    } else {
      // 隨機模式關閉時，清除所有定時器
      if (timerRef.current) clearTimeout(timerRef.current);
    }
  }, [cameraManager, randomMode]); // 新增 randomMode 依賴

  return (
    <>
      {showSpaceBackground && (
        <Stars
          radius={100}
          depth={50}
          count={5000}
          factor={4}
          saturation={0}
          fade
          speed={1}
        />
      )}
      <DynamicAudioBackgrounds />
      <DynamicLights />
      <Suspense fallback={null}>
        {/* 房間場景 */}
        {showRoomScene && (
          <RoomScene
            roomModelUrl={roomSceneUrl}
            position={roomPosition}
            rotation={roomRotation}
            scale={roomScale}
          />
        )}

        {(() => {
          // 調整頭部位置：移到圓圈中央
          const baseScale = 10;
          const basePosition: [number, number, number] = [0, -5, 0]; // 中央位置

          return (
            <group position={basePosition} scale={baseScale}>
              <HeadModel headModelUrl={headModelUrl} scale={modelScale} />
            </group>
          );
        })()}
        
        {/* 角色模型 - 放在頭部旁邊 */}
        <CharacterModel />
        {(() => {
          // 圓形軍隊陣列：100個人圍成圓圈
          const armyPosition: [number, number, number] = [0, -25, 0]; // 再往下移動更多
          return (
            <group position={armyPosition}>
              <DanceGroup
                count={100}
                scale={8}
                enableFloating={false}
                forceCircular={true}
                circleRadius={180}
              />
            </group>
          );
        })()}
      </Suspense>
      <OrbitControls
        ref={orbitControlsRef}
        makeDefault
        enablePan
        enableZoom
        enableRotate
        onStart={() => useStore.getState().setRuntime({ cameraPreset: "roam" })}
        target={[0, 0.8, 0]} // OrbitControls 的 target 可能需要根據當前 cameraManager 的 target 動態調整，或者由 cameraManager 完全接管
        mouseButtons={{
          LEFT: THREE.MOUSE.PAN,
          MIDDLE: THREE.MOUSE.DOLLY,
          RIGHT: THREE.MOUSE.ROTATE,
        }}
      />
    </>
  );
};

export default SceneContainer;
