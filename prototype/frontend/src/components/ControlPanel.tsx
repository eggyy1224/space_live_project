import React, { useEffect, useState } from 'react';
import logger, { LogCategory } from '../utils/LogManager'; // Import logger
import { getPresetsList } from '../services/api';

// 子組件：單個Morph Target控制條
interface MorphTargetBarProps {
  name: string;
  value: number; // 這個值現在應該來自 manualMorphTargets
  onSelect: (name: string) => void;
  onChange: (name: string, value: number) => void;
  isSelected: boolean;
}

const MorphTargetBar: React.FC<MorphTargetBarProps> = React.memo(({ name, value, onSelect, onChange, isSelected }) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(name, parseFloat(event.target.value));
  };

  return (
    <div 
      className={`morph-target-bar ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(name)}
    >
      <label>{name}</label>
      <input 
        type="range" 
        min="0" 
        max="1" 
        step="0.01" 
        value={value} // 直接使用傳入的 value (來自 manualMorphTargets)
        onChange={handleChange} 
      />
      <span>{value.toFixed(2)}</span>
    </div>
  );
});

// 子組件：動畫控制
interface AnimationControlProps {
  availableAnimations: string[];
  currentAnimation: string | null;
  selectAnimation: (animationName: string) => void;
  isModelLoaded: boolean;
}

const AnimationControl: React.FC<AnimationControlProps> = React.memo(({
  availableAnimations,
  currentAnimation,
  selectAnimation,
  isModelLoaded
}) => {
  if (!availableAnimations || availableAnimations.length === 0) return null;

  return (
    <div className="control-section animation-control">
      <h3>動畫控制</h3>
      <div className="animation-buttons">
        {availableAnimations.map((anim) => (
          <button
            key={anim}
            onClick={() => selectAnimation(anim)}
            className={currentAnimation === anim ? 'active' : ''}
            disabled={!isModelLoaded}
          >
            {anim}
          </button>
        ))}
        {/* Optionally add a button to stop animation */}
        <button onClick={() => selectAnimation('')} disabled={!currentAnimation || !isModelLoaded}>停止動畫</button>
      </div>
    </div>
  );
});

// 子組件：模型變換控制
interface ModelTransformControlProps {
  modelScale: number;
  rotateModel: (direction: 'left' | 'right') => void;
  scaleModel: (factor: number) => void;
  resetModel: () => void;
  toggleBackground: () => void;
  showSpaceBackground: boolean;
  isModelLoaded: boolean;
}

const ModelTransformControl: React.FC<ModelTransformControlProps> = React.memo(({
  modelScale,
  rotateModel,
  scaleModel,
  resetModel,
  toggleBackground,
  showSpaceBackground,
  isModelLoaded
}) => (
  <div className="control-section model-transform-control">
    <h3>模型變換</h3>
     <div className="status-info"> {/* Moved status here */}
       <p>模型狀態: {isModelLoaded ? '已加載' : '加載中...'}</p>
       <p>模型縮放: {modelScale.toFixed(2)}</p>
     </div>
    <div className="button-row">
      <button onClick={() => rotateModel('left')} disabled={!isModelLoaded}>
        向左旋轉
      </button>
      <button onClick={() => rotateModel('right')} disabled={!isModelLoaded}>
        向右旋轉
      </button>
      <button onClick={() => scaleModel(0.1)} disabled={!isModelLoaded}>
        放大
      </button>
      <button onClick={() => scaleModel(-0.1)} disabled={!isModelLoaded}>
        縮小
      </button>
      <button onClick={resetModel} disabled={!isModelLoaded}>
        重置模型
      </button>
      <button onClick={toggleBackground}>
        {showSpaceBackground ? '隱藏星空' : '顯示星空'}
      </button>
    </div>
  </div>
));

// 主控制面板 Props
interface ControlPanelProps {
  activeTab: 'control' | 'chat';
  switchTab: (tab: 'control' | 'chat') => void;
  wsConnected: boolean;
  isModelLoaded: boolean;
  modelScale: number;
  currentAnimation: string | null;
  currentEmotion: string;
  emotionConfidence: number;
  availableAnimations: string[];
  morphTargetDictionary: Record<string, number> | null;
  manualMorphTargets: Record<string, number>;
  selectedMorphTarget: string | null;
  setSelectedMorphTarget: (name: string | null) => void;
  updateMorphTargetInfluence: (name: string, value: number) => void;
  resetAllMorphTargets: () => void;
  rotateModel: (direction: 'left' | 'right') => void;
  scaleModel: (factor: number) => void;
  resetModel: () => void;
  toggleBackground: () => void;
  selectAnimation: (animationName: string) => void;
  applyPresetExpression: (expression: string) => Promise<boolean>;
  showSpaceBackground: boolean;
}

// 主控制面板組件
const ControlPanel: React.FC<ControlPanelProps> = React.memo(({
  activeTab,
  switchTab,
  wsConnected,
  isModelLoaded,
  modelScale,
  currentAnimation,
  currentEmotion,
  emotionConfidence,
  availableAnimations,
  morphTargetDictionary,
  manualMorphTargets,
  selectedMorphTarget,
  setSelectedMorphTarget,
  updateMorphTargetInfluence,
  resetAllMorphTargets,
  rotateModel,
  scaleModel,
  resetModel,
  toggleBackground,
  selectAnimation,
  applyPresetExpression,
  showSpaceBackground,
}) => {

  // 預設表情列表
  const [presets, setPresets] = useState<string[]>([]);
  const [loadingPresets, setLoadingPresets] = useState<boolean>(false);

  // 在組件掛載時獲取預設表情列表
  useEffect(() => {
    const fetchPresets = async () => {
      setLoadingPresets(true);
      try {
        const response = await getPresetsList();
        if (response && response.presets) {
          setPresets(response.presets);
          logger.info(`已獲取到 ${response.presets.length} 個預設表情`, LogCategory.MODEL);
        }
      } catch (error) {
        logger.error('無法獲取預設表情列表', LogCategory.MODEL, error);
        // 使用默認表情列表作為備用
        setPresets(['happy', 'sad', 'angry', 'surprised', 'reset']);
      } finally {
        setLoadingPresets(false);
      }
    };

    fetchPresets();
  }, []);

  const handlePresetApply = async (preset: string) => {
    logger.info(`UI: Applying preset ${preset}`, LogCategory.MODEL);
    await applyPresetExpression(preset);
  };

  // 翻譯預設表情名稱
  const translatePreset = (preset: string): string => {
    const translations: Record<string, string> = {
      'happy': '快樂',
      'sad': '悲傷',
      'angry': '生氣',
      'surprised': '驚訝',
      'reset': '重置',
      // 可以添加更多翻譯
    };
    return translations[preset] || preset;
  };

  return (
    <div className="controls-panel">
      <div className="panel-tabs">
        <button
          className={`tab-button ${activeTab === 'control' ? 'active' : ''}`}
          onClick={() => switchTab('control')}
        >
          控制面板
        </button>
        <button
          className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => switchTab('chat')}
        >
          聊天
        </button>
        <div className={`ws-status ${wsConnected ? 'connected' : 'disconnected'}`}>
          {wsConnected ? '已連接' : '未連接'}
        </div>
      </div>

      <div className={`tab-content control-tab ${activeTab === 'control' ? 'active' : ''}`}>
        <h1>虛擬太空人互動原型</h1>

        <div className="control-section expression-control">
          <h3>表情控制</h3>
          <div className="current-emotion">
            當前情緒: {currentEmotion} (可信度: {emotionConfidence.toFixed(2)})
          </div>
          <div className="preset-buttons">
            {loadingPresets ? (
              <p>加載表情中...</p>
            ) : (
              presets.map(preset => (
                <button key={preset} onClick={() => handlePresetApply(preset)}>
                  {translatePreset(preset)}
                </button>
              ))
            )}
          </div>
          <div className="morph-target-list">
            {morphTargetDictionary ? (
              Object.keys(morphTargetDictionary)
                .sort()
                .map(name => (
                  <MorphTargetBar
                    key={name}
                    name={name}
                    value={manualMorphTargets[name] ?? 0}
                    onSelect={setSelectedMorphTarget}
                    onChange={updateMorphTargetInfluence}
                    isSelected={selectedMorphTarget === name}
                  />
                ))
            ) : (
              <p>模型未加載或無Morph Targets</p>
            )}
          </div>
        </div>

        <AnimationControl
          availableAnimations={availableAnimations}
          currentAnimation={currentAnimation}
          selectAnimation={selectAnimation}
          isModelLoaded={isModelLoaded}
        />

        <ModelTransformControl
          modelScale={modelScale}
          rotateModel={rotateModel}
          scaleModel={scaleModel}
          resetModel={resetModel}
          toggleBackground={toggleBackground}
          showSpaceBackground={showSpaceBackground}
          isModelLoaded={isModelLoaded}
        />
      </div>
    </div>
  );
});

export default ControlPanel;