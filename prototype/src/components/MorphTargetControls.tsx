import React from 'react';
import MorphTargetBar from './MorphTargetBar';

interface MorphTargetControlsProps {
  morphTargetDictionary: Record<string, number>;
  morphTargetInfluences: number[];
  selectedMorphTarget: string | null;
  setSelectedMorphTarget: (target: string | null) => void;
  updateMorphTargetInfluence: (name: string, value: number) => void;
  resetAllMorphTargets: () => void;
  isModelLoaded: boolean;
}

const MorphTargetControls: React.FC<MorphTargetControlsProps> = ({
  morphTargetDictionary,
  morphTargetInfluences,
  selectedMorphTarget,
  setSelectedMorphTarget,
  updateMorphTargetInfluence,
  resetAllMorphTargets,
  isModelLoaded
}) => {
  return (
    <div className="morph-target-controls">
      <div className="morph-header">
        <h3>表情控制 (Morph Targets)</h3>
        <button 
          onClick={resetAllMorphTargets}
          disabled={!isModelLoaded}
          className="reset-button"
        >
          重置所有表情
        </button>
      </div>
      
      <div className="morph-bar-list">
        {Object.keys(morphTargetDictionary).map((name) => (
          <MorphTargetBar 
            key={name}
            name={name}
            value={morphTargetInfluences[morphTargetDictionary[name]]}
            onChange={(value: number) => updateMorphTargetInfluence(name, value)}
            isSelected={selectedMorphTarget === name}
            onSelect={() => setSelectedMorphTarget(name === selectedMorphTarget ? null : name)}
          />
        ))}
      </div>
    </div>
  );
};

export default MorphTargetControls; 