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

  // Outfit 變形目標 (outfit_shoes030 相關)
  const outfitMorphTargets = morphTargetDictionary ? 
    Object.keys(morphTargetDictionary).filter(name => 
      name.includes('鍵 1') || name.includes('錯置') || name.includes('錯置.001')
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
          <div>位置: [{characterPosition.map(v => v.toFixed(1)).join(', ')}]</div>
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

      {/* 縮放控制 - 改為滑動條 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">縮放</h3>
        <div className="mb-2">
          <input
            type="range"
            min="0.1"
            max="15"
            step="0.1"
            value={characterScale}
            onChange={(e) => setCharacterScale(parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="text-xs text-gray-300 text-center">
            縮放: {characterScale.toFixed(2)}
          </div>
        </div>
      </div>

      {/* 位置控制 - 改為滑動條 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">位置</h3>
        <div className="space-y-2">
          <div>
            <label className="text-xs text-gray-300">X 軸 (左右)</label>
            <input
              type="range"
              min="-10"
              max="10"
              step="0.1"
              value={characterPosition[0]}
              onChange={(e) => moveCharacter([parseFloat(e.target.value), characterPosition[1], characterPosition[2]])}
              className="w-full"
            />
            <div className="text-xs text-gray-300 text-center">{characterPosition[0].toFixed(1)}</div>
          </div>
          <div>
            <label className="text-xs text-gray-300">Y 軸 (上下)</label>
            <input
              type="range"
              min="-5"
              max="5"
              step="0.1"
              value={characterPosition[1]}
              onChange={(e) => moveCharacter([characterPosition[0], parseFloat(e.target.value), characterPosition[2]])}
              className="w-full"
            />
            <div className="text-xs text-gray-300 text-center">{characterPosition[1].toFixed(1)}</div>
          </div>
          <div>
            <label className="text-xs text-gray-300">Z 軸 (前後)</label>
            <input
              type="range"
              min="-10"
              max="10"
              step="0.1"
              value={characterPosition[2]}
              onChange={(e) => moveCharacter([characterPosition[0], characterPosition[1], parseFloat(e.target.value)])}
              className="w-full"
            />
            <div className="text-xs text-gray-300 text-center">{characterPosition[2].toFixed(1)}</div>
          </div>
        </div>
      </div>

      {/* 旋轉控制 - 改為滑動條 */}
      <div className="mb-4">
        <h3 className="text-md font-semibold mb-2">旋轉</h3>
        <div className="space-y-2">
          <div>
            <label className="text-xs text-gray-300">X 軸旋轉</label>
            <input
              type="range"
              min={-Math.PI}
              max={Math.PI}
              step="0.1"
              value={characterRotation[0]}
              onChange={(e) => rotateCharacter([parseFloat(e.target.value), characterRotation[1], characterRotation[2]])}
              className="w-full"
            />
            <div className="text-xs text-gray-300 text-center">{(characterRotation[0] * 180 / Math.PI).toFixed(0)}°</div>
          </div>
          <div>
            <label className="text-xs text-gray-300">Y 軸旋轉</label>
            <input
              type="range"
              min={-Math.PI}
              max={Math.PI}
              step="0.1"
              value={characterRotation[1]}
              onChange={(e) => rotateCharacter([characterRotation[0], parseFloat(e.target.value), characterRotation[2]])}
              className="w-full"
            />
            <div className="text-xs text-gray-300 text-center">{(characterRotation[1] * 180 / Math.PI).toFixed(0)}°</div>
          </div>
          <div>
            <label className="text-xs text-gray-300">Z 軸旋轉</label>
            <input
              type="range"
              min={-Math.PI}
              max={Math.PI}
              step="0.1"
              value={characterRotation[2]}
              onChange={(e) => rotateCharacter([characterRotation[0], characterRotation[1], parseFloat(e.target.value)])}
              className="w-full"
            />
            <div className="text-xs text-gray-300 text-center">{(characterRotation[2] * 180 / Math.PI).toFixed(0)}°</div>
          </div>
        </div>
      </div>

      {/* Outfit 控制 (outfit_shoes030_1) */}
      {outfitMorphTargets.length > 0 && (
        <div className="mb-4">
          <h3 className="text-md font-semibold mb-2">服裝控制 (outfit_shoes030_1)</h3>
          <div className="space-y-2">
            {outfitMorphTargets.map((target) => (
              <div key={target}>
                <label className="text-xs text-gray-300">{target}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={morphTargets[target] || 0}
                  onChange={(e) => {
                    const value = parseFloat(e.target.value);
                    updateCharacterMorphTarget({ [target]: value });
                  }}
                  className="w-full"
                />
                <div className="text-xs text-gray-300 text-center">
                  {(morphTargets[target] || 0).toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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