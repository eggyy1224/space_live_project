import React from 'react';
import MorphTargetControls from './MorphTargetControls';

// 獲取情緒顯示名稱
const getEmotionDisplayName = (emotion: string): string => {
  const emotionMap: Record<string, string> = {
    'happy': '開心',
    'sad': '悲傷',
    'angry': '生氣',
    'surprised': '驚訝',
    'neutral': '中性',
    'question': '疑問'
  };
  return emotionMap[emotion] || emotion;
};

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
  morphTargetInfluences: number[] | null;
  selectedMorphTarget: string | null;
  setSelectedMorphTarget: (target: string | null) => void;
  updateMorphTargetInfluence: (name: string, value: number) => void;
  resetAllMorphTargets: () => void;
  rotateModel: (direction: 'left' | 'right') => void;
  scaleModel: (factor: number) => void;
  resetModel: () => void;
  toggleBackground: () => void;
  showSpaceBackground: boolean;
  selectAnimation: (animationName: string) => void;
  applyPresetExpression: (expression: string) => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({
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
  morphTargetInfluences,
  selectedMorphTarget,
  setSelectedMorphTarget,
  updateMorphTargetInfluence,
  resetAllMorphTargets,
  rotateModel,
  scaleModel,
  resetModel,
  toggleBackground,
  showSpaceBackground,
  selectAnimation,
  applyPresetExpression
}) => {
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
        
        <div className="status-info">
          <p>模型狀態: {isModelLoaded ? '已加載' : '加載中...'}</p>
          <p>模型縮放: {modelScale.toFixed(2)}</p>
          <p>當前動畫: {currentAnimation || '無'}</p>
          <p>當前情緒: <span className={`emotion-tag ${currentEmotion}`}>{getEmotionDisplayName(currentEmotion)}</span> 
             <span className="confidence-indicator" style={{width: `${emotionConfidence * 100}%`}}></span>
          </p>
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
            重置
          </button>
          <button onClick={toggleBackground}>
            {showSpaceBackground ? '隱藏星空' : '顯示星空'}
          </button>
        </div>
        
        {/* 動畫控制面板 */}
        {availableAnimations.length > 0 && (
          <div className="animation-controls">
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
            </div>
          </div>
        )}
        
        {/* 預設表情控制 */}
        <div className="preset-expressions">
          <h3>預設表情</h3>
          <div className="preset-buttons">
            <button onClick={() => applyPresetExpression('happy')} disabled={!isModelLoaded}>
              開心
            </button>
            <button onClick={() => applyPresetExpression('sad')} disabled={!isModelLoaded}>
              悲傷
            </button>
            <button onClick={() => applyPresetExpression('angry')} disabled={!isModelLoaded}>
              生氣
            </button>
            <button onClick={() => applyPresetExpression('surprised')} disabled={!isModelLoaded}>
              驚訝
            </button>
            <button onClick={() => applyPresetExpression('reset')} disabled={!isModelLoaded}>
              重置表情
            </button>
          </div>
        </div>
        
        {/* Morph Target 控制面板 */}
        {morphTargetDictionary && morphTargetInfluences && (
          <MorphTargetControls
            morphTargetDictionary={morphTargetDictionary}
            morphTargetInfluences={morphTargetInfluences}
            selectedMorphTarget={selectedMorphTarget}
            setSelectedMorphTarget={setSelectedMorphTarget}
            updateMorphTargetInfluence={updateMorphTargetInfluence}
            resetAllMorphTargets={resetAllMorphTargets}
            isModelLoaded={isModelLoaded}
          />
        )}
      </div>
    </div>
  );
};

export default ControlPanel; 