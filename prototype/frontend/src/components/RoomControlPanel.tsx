import React from 'react';
import { useStore } from '../store';

interface RoomControlPanelProps {
  isVisible: boolean;
}

const RoomControlPanel: React.FC<RoomControlPanelProps> = ({ isVisible }) => {
  const showRoomScene = useStore((state) => state.showRoomScene);
  const roomSceneUrl = useStore((state) => state.roomSceneUrl);
  const roomPosition = useStore((state) => state.roomPosition);
  const roomRotation = useStore((state) => state.roomRotation);
  const roomScale = useStore((state) => state.roomScale);
  const toggleRoomScene = useStore((state) => state.toggleRoomScene);
  const setRoomPosition = useStore((state) => state.setRoomPosition);
  const setRoomRotation = useStore((state) => state.setRoomRotation);
  const setRoomScale = useStore((state) => state.setRoomScale);
  const resetRoomTransform = useStore((state) => state.resetRoomTransform);
  const toggleRoomControlPanel = useStore((state) => state.toggleRoomControlPanel);

  if (!isVisible) return null;

  const handlePositionChange = (axis: number, value: number) => {
    const newPosition = [...roomPosition] as [number, number, number];
    newPosition[axis] = value;
    setRoomPosition(newPosition);
  };

  const handleRotationChange = (axis: number, value: number) => {
    const newRotation = [...roomRotation] as [number, number, number];
    newRotation[axis] = value;
    setRoomRotation(newRotation);
  };

  const handleScaleChange = (axis: number, value: number) => {
    const newScale = [...roomScale] as [number, number, number];
    newScale[axis] = value;
    setRoomScale(newScale);
  };

  const handleUniformScaleChange = (value: number) => {
    setRoomScale([value, value, value]);
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'rgba(0, 0, 0, 0.9)',
      border: '1px solid #555',
      borderRadius: '8px',
      color: 'white',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      zIndex: 1000,
      minWidth: '280px',
      maxHeight: '70vh',
      overflow: 'auto',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
    }}>
      {/* 可收縮的標題欄 */}
      <div 
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 15px',
          borderBottom: '1px solid #444',
          cursor: 'pointer',
          background: 'rgba(255, 255, 255, 0.05)'
        }}
        onClick={toggleRoomControlPanel}
      >
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold' }}>🏠 房間場景控制</h3>
        <span style={{ fontSize: '18px', transition: 'transform 0.2s' }}>×</span>
      </div>
      
      <div style={{ padding: '15px' }}>
      
      {/* 顯示/隱藏控制 */}
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showRoomScene}
            onChange={toggleRoomScene}
            style={{ marginRight: '8px' }}
          />
          顯示房間場景
        </label>
      </div>

      {showRoomScene && (
        <>
          {/* 位置控制 */}
          <div style={{ marginBottom: '15px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>位置</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '20px 1fr', gap: '5px', alignItems: 'center' }}>
              <span>X:</span>
              <input
                type="range"
                min="-50"
                max="50"
                step="0.5"
                value={roomPosition[0]}
                onChange={(e) => handlePositionChange(0, parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <span>Y:</span>
              <input
                type="range"
                min="-50"
                max="50"
                step="0.5"
                value={roomPosition[1]}
                onChange={(e) => handlePositionChange(1, parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <span>Z:</span>
              <input
                type="range"
                min="-50"
                max="50"
                step="0.5"
                value={roomPosition[2]}
                onChange={(e) => handlePositionChange(2, parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
            <div style={{ fontSize: '12px', color: '#aaa', marginTop: '5px' }}>
              ({roomPosition[0].toFixed(1)}, {roomPosition[1].toFixed(1)}, {roomPosition[2].toFixed(1)})
            </div>
          </div>

          {/* 旋轉控制 */}
          <div style={{ marginBottom: '15px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>旋轉 (度)</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '20px 1fr', gap: '5px', alignItems: 'center' }}>
              <span>X:</span>
              <input
                type="range"
                min="-180"
                max="180"
                step="5"
                value={(roomRotation[0] * 180) / Math.PI}
                onChange={(e) => handleRotationChange(0, (parseFloat(e.target.value) * Math.PI) / 180)}
                style={{ width: '100%' }}
              />
              <span>Y:</span>
              <input
                type="range"
                min="-180"
                max="180"
                step="5"
                value={(roomRotation[1] * 180) / Math.PI}
                onChange={(e) => handleRotationChange(1, (parseFloat(e.target.value) * Math.PI) / 180)}
                style={{ width: '100%' }}
              />
              <span>Z:</span>
              <input
                type="range"
                min="-180"
                max="180"
                step="5"
                value={(roomRotation[2] * 180) / Math.PI}
                onChange={(e) => handleRotationChange(2, (parseFloat(e.target.value) * Math.PI) / 180)}
                style={{ width: '100%' }}
              />
            </div>
            <div style={{ fontSize: '12px', color: '#aaa', marginTop: '5px' }}>
              ({Math.round((roomRotation[0] * 180) / Math.PI)}°, {Math.round((roomRotation[1] * 180) / Math.PI)}°, {Math.round((roomRotation[2] * 180) / Math.PI)}°)
            </div>
          </div>

          {/* 縮放控制 */}
          <div style={{ marginBottom: '15px' }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>縮放</h4>
            <div style={{ marginBottom: '8px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>統一縮放:</label>
              <input
                type="range"
                min="0.1"
                max="5"
                step="0.1"
                value={roomScale[0]}
                onChange={(e) => handleUniformScaleChange(parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <div style={{ fontSize: '12px', color: '#aaa', marginTop: '2px' }}>
                {roomScale[0].toFixed(1)}x
              </div>
            </div>
          </div>

          {/* 重置按鈕 */}
          <button
            onClick={resetRoomTransform}
            style={{
              background: '#444',
              border: '1px solid #666',
              borderRadius: '4px',
              color: 'white',
              padding: '8px 12px',
              cursor: 'pointer',
              fontSize: '12px',
              width: '100%'
            }}
            onMouseOver={(e) => (e.target as HTMLElement).style.background = '#555'}
            onMouseOut={(e) => (e.target as HTMLElement).style.background = '#444'}
          >
            重置變換
          </button>
        </>
      )}
      </div>
    </div>
  );
};

export default RoomControlPanel; 