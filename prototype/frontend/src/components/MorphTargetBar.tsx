import React from 'react';

interface MorphTargetBarProps {
  name: string;
  value: number;
  onChange: (value: number) => void;
  isSelected?: boolean;
  onSelect: () => void;
}

const MorphTargetBar: React.FC<MorphTargetBarProps> = ({
  name,
  value,
  onChange,
  isSelected = false,
  onSelect
}) => {
  // 將值映射到百分比
  const percent = Math.round(value * 100);
  
  return (
    <div 
      className={`morph-bar ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <div className="morph-bar-header">
        <span className="morph-bar-name">{name}</span>
        <span className="morph-bar-value">{percent}%</span>
      </div>
      <div className="morph-bar-container">
        <div className="morph-bar-track">
          <div 
            className="morph-bar-fill" 
            style={{ width: `${percent}%` }}
          ></div>
        </div>
        {isSelected && (
          <input 
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={value}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            className="morph-bar-slider"
          />
        )}
      </div>
    </div>
  );
};

export default MorphTargetBar; 