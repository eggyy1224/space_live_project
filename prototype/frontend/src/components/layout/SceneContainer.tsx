import React from 'react';
import ModelViewer from '../ModelViewer'; // 假設 ModelViewer 在上層 components 目錄

interface SceneContainerProps {
  modelUrl: string;
  modelScale: number;
  modelRotation: [number, number, number];
  modelPosition: [number, number, number];
  currentAnimation: string | null;
  morphTargets: Record<string, number>;
  showSpaceBackground: boolean;
  morphTargetDictionary: Record<string, number> | null;
  getManualMorphTargets: () => Record<string, number>;
  setMorphTargetData: (dictionary: Record<string, number> | null, influences: number[] | null) => void;
}

const SceneContainer: React.FC<SceneContainerProps> = ({
  modelUrl,
  modelScale,
  modelRotation,
  modelPosition,
  currentAnimation,
  morphTargets,
  showSpaceBackground,
  morphTargetDictionary,
  getManualMorphTargets,
  setMorphTargetData,
}) => {
  return (
    <ModelViewer
      modelUrl={modelUrl}
      modelScale={modelScale}
      modelRotation={modelRotation}
      modelPosition={modelPosition}
      currentAnimation={currentAnimation}
      morphTargets={morphTargets}
      showSpaceBackground={showSpaceBackground}
      morphTargetDictionary={morphTargetDictionary}
      getManualMorphTargets={getManualMorphTargets}
      setMorphTargetData={setMorphTargetData}
    />
  );
};

export default SceneContainer; 