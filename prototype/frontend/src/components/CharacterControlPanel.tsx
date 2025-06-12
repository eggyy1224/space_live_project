import React, { useState } from 'react';
import { useCharacterService } from '../services/CharacterService';
import { CHARACTER_ANIMATIONS } from '../store/slices/characterSlice';
import { useStore } from '../store';

interface CharacterControlPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

export const CharacterControlPanel: React.FC<CharacterControlPanelProps> = ({
  isVisible,
  onClose,
}) => {
  const {
    characterModelLoaded,
    characterVisible,
    characterPosition,
    characterScale,
    characterRotation,
    currentCharacterAnimation,
    morphTargets,
    morphTargetDictionary,
    setCharacterVisible,
    moveCharacter,
    rotateCharacter,
    updateCharacterMorphTarget,
    resetCharacterMorphTargets,
    resetCharacterTransform,
  } = useCharacterService();

  // 直接從 store 獲取其他需要的方法
  const setCharacterScale = useStore((state) => state.setCharacterScale);
  const setCurrentCharacterAnimation = useStore((state) => state.setCurrentCharacterAnimation);

  const [selectedMorphTarget, setSelectedMorphTarget] = useState<string>('');

  if (!isVisible) return null;

  // 輔助函數
  const toggleCharacterVisibility = () => {
    setCharacterVisible(!characterVisible);
  };

  const selectCharacterAnimation = (animationName: string) => {
    if (CHARACTER_ANIMATIONS.includes(animationName)) {
      setCurrentCharacterAnimation(animationName);
    }
  };

  const adjustCharacterScale = (factor: number) => {
    const newScale = Math.max(0.1, Math.min(3, characterScale * factor));
    setCharacterScale(newScale);
  };

  const moveCharacterDirection = (direction: string) => {
    const [x, y, z] = characterPosition;
    const distance = 0.5;
    let newPosition: [number, number, number];

    switch (direction) {
      case 'left':
        newPosition = [x - distance, y, z];
        break;
      case 'right':
        newPosition = [x + distance, y, z];
        break;
      case 'forward':
        newPosition = [x, y, z - distance];
        break;
      case 'backward':
        newPosition = [x, y, z + distance];
        break;
      case 'up':
        newPosition = [x, y + distance, z];
        break;
      case 'down':
        newPosition = [x, y - distance, z];
        break;
      default:
        newPosition = [x, y, z];
    }
    moveCharacter(newPosition);
  };

  const rotateCharacterAxis = (axis: string, angle: number) => {
    const [x, y, z] = characterRotation;
    let newRotation: [number, number, number];

    switch (axis) {
      case 'x':
        newRotation = [x + angle, y, z];
        break;
      case 'y':
        newRotation = [x, y + angle, z];
        break;
      case 'z':
        newRotation = [x, y, z + angle];
        break;
      default:
        newRotation = [x, y, z];
    }
    rotateCharacter(newRotation);
  };

  // 主要表情變形目標
  const facialMorphTargets = morphTargetDictionary ? 
    Object.keys(morphTargetDictionary).filter(name => 
      name.includes('eye') || name.includes('mouth') || name.includes('brow') ||
      name.includes('jaw') || name.includes('cheek') || name.includes('nose')
    ) : [];

  // 語音變形目標  
  const speechMorphTargets = morphTargetDictionary ?
    Object.keys(morphTargetDictionary).filter(name =>
      ['CH', 'DD', 'E', 'FF', 'PP', 'RR', 'SS', 'TH', 'aa', 'ih', 'kk', 'nn', 'oh', 'ou', 'sil'].includes(name)
    ) : [];

  return (
    <div className="fixed top-4 left-4 w-80 bg-black bg-opacity-80 text-white p-4 rounded-lg shadow-lg z-50 max-h-[90vh] overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">角色控制</h2>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-300 text-xl"
          aria-label="關閉角色控制面板"
        >
          ✕
        </button>
      </div>

      {/* 模型狀態 */}
      <div className="mb-4">
        <div className="text-sm">
          <div>模型狀態: {characterModelLoaded ? '✅ 已載入' : '⏳ 載入中...'}</div>
          <div>可見性: {characterVisible ? '👁️ 顯示' : '👁️‍🗨️ 隱藏'}</div>
          <div>位置: [{characterPosition.join(', ')}]</div>
          <div>縮放: {characterScale.toFixed(2)}</div>
        </div>
      </div>

      {/* 基本控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">基本控制</h3>
        <div className="grid grid-cols-2 gap-2 mb-2">
          <button
            onClick={toggleCharacterVisibility}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            {characterVisible ? '隱藏' : '顯示'}
          </button>
          <button
            onClick={resetCharacterTransform}
            className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm"
          >
            重置位置
          </button>
        </div>
      </div>

      {/* 縮放控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">縮放</h3>
        <div className="grid grid-cols-3 gap-1">
          <button
            onClick={() => adjustCharacterScale(0.9)}
            className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
          >
            縮小
          </button>
          <button
            onClick={() => adjustCharacterScale(1.1)}
            className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
          >
            放大
          </button>
          <button
            onClick={() => adjustCharacterScale(1/characterScale)}
            className="px-2 py-1 bg-gray-600 hover:bg-gray-700 rounded text-xs"
          >
            重置
          </button>
        </div>
      </div>

      {/* 位置控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">位置</h3>
        <div className="grid grid-cols-3 gap-1 mb-2">
          <button onClick={() => moveCharacterDirection('up')} className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">上</button>
          <button onClick={() => moveCharacterDirection('forward')} className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">前</button>
          <button onClick={() => moveCharacterDirection('down')} className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">下</button>
        </div>
        <div className="grid grid-cols-3 gap-1">
          <button onClick={() => moveCharacterDirection('left')} className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">左</button>
          <button onClick={() => moveCharacterDirection('backward')} className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">後</button>
          <button onClick={() => moveCharacterDirection('right')} className="px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs">右</button>
        </div>
      </div>

      {/* 旋轉控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">旋轉</h3>
        <div className="grid grid-cols-3 gap-1">
          <button onClick={() => rotateCharacterAxis('y', Math.PI/4)} className="px-2 py-1 bg-orange-600 hover:bg-orange-700 rounded text-xs">左轉</button>
          <button onClick={() => rotateCharacterAxis('x', Math.PI/4)} className="px-2 py-1 bg-orange-600 hover:bg-orange-700 rounded text-xs">前傾</button>
          <button onClick={() => rotateCharacterAxis('y', -Math.PI/4)} className="px-2 py-1 bg-orange-600 hover:bg-orange-700 rounded text-xs">右轉</button>
        </div>
      </div>

      {/* 動畫控制 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">動畫控制</h3>
        <div className="mb-2">
          <div className="text-sm text-gray-300">當前: {currentCharacterAnimation || '無'}</div>
        </div>
        <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
          {CHARACTER_ANIMATIONS.map((animation) => (
            <button
              key={animation}
              onClick={() => selectCharacterAnimation(animation)}
              className={`px-2 py-1 rounded text-xs ${
                currentCharacterAnimation === animation
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-gray-600 hover:bg-gray-700'
              }`}
            >
              {animation}
            </button>
          ))}
        </div>
      </div>

      {/* 表情控制 */}
      {facialMorphTargets.length > 0 && (
        <div className="mb-4">
          <h3 className="text-md font-semibold mb-2">表情控制 (同步)</h3>
          <div className="mb-2">
            <select
              value={selectedMorphTarget}
              onChange={(e) => setSelectedMorphTarget(e.target.value)}
              className="w-full px-2 py-1 bg-gray-700 text-white rounded text-sm"
            >
              <option value="">選擇表情</option>
              {facialMorphTargets.map((name) => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          </div>
          {selectedMorphTarget && (
            <div className="mb-2">
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={morphTargets[selectedMorphTarget] || 0}
                onChange={(e) => {
                  const value = parseFloat(e.target.value);
                  updateCharacterMorphTarget({ [selectedMorphTarget]: value });
                }}
                className="w-full"
              />
              <div className="text-xs text-gray-300 text-center">
                {selectedMorphTarget}: {(morphTargets[selectedMorphTarget] || 0).toFixed(2)}
              </div>
            </div>
          )}
          <button
            onClick={resetCharacterMorphTargets}
            className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm w-full"
          >
            重置表情 (同步)
          </button>
        </div>
      )}

      {/* 語音變形目標 */}
      {speechMorphTargets.length > 0 && (
        <div className="mb-4">
          <h3 className="text-md font-semibold mb-2">語音控制 (同步)</h3>
          <div className="grid grid-cols-3 gap-1 max-h-32 overflow-y-auto">
            {speechMorphTargets.map((target) => (
              <button
                key={target}
                onClick={() => updateCharacterMorphTarget({ [target]: morphTargets[target] > 0 ? 0 : 1 })}
                className={`px-2 py-1 rounded text-xs ${
                  morphTargets[target] > 0
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                {target}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="text-xs text-gray-400 mt-4">
        * 表情和語音控制會同步到頭部模型
      </div>
    </div>
  );
}; 