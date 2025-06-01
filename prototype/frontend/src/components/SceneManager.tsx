import React, { useState } from 'react';
import { AVAILABLE_SCENES, type SceneConfig } from '../config/sceneConfig';

interface SceneManagerProps {
  isVisible: boolean;
  onClose: () => void;
}

const SceneManager: React.FC<SceneManagerProps> = ({ isVisible, onClose }) => {
  const [newScene, setNewScene] = useState<Partial<SceneConfig>>({
    id: '',
    name: '',
    url: '',
    description: '',
    defaultScale: [2, 2, 2],
    defaultPosition: [0, 0, 0],
    defaultRotation: [0, 0, 0]
  });

  if (!isVisible) return null;

  const handleAddScene = () => {
    if (newScene.id && newScene.name && newScene.url) {
      // 這裡可以實現添加場景的邏輯
      // 由於 AVAILABLE_SCENES 是靜態的，這裡只是示例
      console.log('新場景配置:', newScene);
      alert(`場景配置已生成！請將以下內容添加到 sceneConfig.ts 文件中：\n\n${JSON.stringify(newScene, null, 2)}`);
      
      // 重置表單
      setNewScene({
        id: '',
        name: '',
        url: '',
        description: '',
        defaultScale: [2, 2, 2],
        defaultPosition: [0, 0, 0],
        defaultRotation: [0, 0, 0]
      });
    } else {
      alert('請填寫必要欄位：ID、名稱、URL');
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      background: 'rgba(0, 0, 0, 0.95)',
      border: '1px solid #555',
      borderRadius: '12px',
      padding: '20px',
      color: 'white',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      zIndex: 2000,
      width: '90%',
      maxWidth: '500px',
      maxHeight: '80vh',
      overflow: 'auto',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.8)'
    }}>
      {/* 標題欄 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        paddingBottom: '10px',
        borderBottom: '1px solid #444'
      }}>
        <h2 style={{ margin: 0, fontSize: '18px' }}>🎬 場景管理器</h2>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            fontSize: '20px',
            cursor: 'pointer'
          }}
        >
          ×
        </button>
      </div>

      {/* 現有場景列表 */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>現有場景</h3>
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.05)', 
          padding: '10px', 
          borderRadius: '6px',
          maxHeight: '150px',
          overflow: 'auto'
        }}>
          {AVAILABLE_SCENES.map((scene, index) => (
            <div key={scene.id} style={{ 
              marginBottom: '8px', 
              padding: '8px',
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '4px'
            }}>
              <div style={{ fontWeight: 'bold' }}>{scene.name}</div>
              <div style={{ fontSize: '12px', color: '#aaa' }}>
                ID: {scene.id} | URL: {scene.url}
              </div>
              {scene.description && (
                <div style={{ fontSize: '12px', color: '#ccc', marginTop: '2px' }}>
                  {scene.description}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 添加新場景表單 */}
      <div>
        <h3 style={{ margin: '0 0 15px 0', fontSize: '16px' }}>添加新場景</h3>
        
        <div style={{ display: 'grid', gap: '12px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>場景 ID *</label>
            <input
              type="text"
              value={newScene.id || ''}
              onChange={(e) => setNewScene({ ...newScene, id: e.target.value })}
              placeholder="例如: room-c"
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #555',
                background: '#333',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>場景名稱 *</label>
            <input
              type="text"
              value={newScene.name || ''}
              onChange={(e) => setNewScene({ ...newScene, name: e.target.value })}
              placeholder="例如: 新場景"
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #555',
                background: '#333',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>GLB 文件路徑 *</label>
            <input
              type="text"
              value={newScene.url || ''}
              onChange={(e) => setNewScene({ ...newScene, url: e.target.value })}
              placeholder="例如: /scenes/新場景.glb"
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #555',
                background: '#333',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px' }}>描述</label>
            <input
              type="text"
              value={newScene.description || ''}
              onChange={(e) => setNewScene({ ...newScene, description: e.target.value })}
              placeholder="場景描述（可選）"
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #555',
                background: '#333',
                color: 'white',
                fontSize: '14px'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '10px' }}>
            <button
              onClick={handleAddScene}
              style={{
                background: '#4CAF50',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                padding: '10px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              生成配置
            </button>
            <button
              onClick={onClose}
              style={{
                background: '#666',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                padding: '10px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              關閉
            </button>
          </div>
        </div>
      </div>

      <div style={{
        marginTop: '15px',
        padding: '10px',
        background: 'rgba(255, 193, 7, 0.1)',
        border: '1px solid rgba(255, 193, 7, 0.3)',
        borderRadius: '6px',
        fontSize: '12px',
        color: '#FFC107'
      }}>
        💡 提示：生成配置後，請將內容手動添加到 sceneConfig.ts 文件中，然後重啟應用程式以使新場景生效。
      </div>
    </div>
  );
};

export default SceneManager; 