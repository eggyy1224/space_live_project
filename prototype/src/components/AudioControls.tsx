import React, { useEffect, useRef } from 'react';

interface AudioControlsProps {
  isRecording: boolean;
  isSpeaking: boolean;
  isProcessing: boolean;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  playAudio: (audioUrl: string) => void;
  wsConnected: boolean;
  micPermission: boolean | null;
}

const AudioControls: React.FC<AudioControlsProps> = ({
  isRecording,
  isSpeaking,
  isProcessing,
  startRecording,
  stopRecording,
  playAudio,
  wsConnected,
  micPermission
}) => {
  // 麥克風橫幅組件
  const renderMicrophoneBanner = () => {
    if (micPermission === null) {
      return (
        <div className="microphone-banner" style={{ backgroundColor: "rgba(50, 50, 50, 0.8)" }}>
          <span>💡 正在檢查麥克風權限...</span>
        </div>
      );
    } else if (micPermission) {
      return (
        <div className="microphone-banner" style={{ backgroundColor: "rgba(0, 100, 0, 0.8)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span>✅ 麥克風權限已獲得授權，您可以使用語音功能與太空人對話。</span>
          <small style={{ marginLeft: "10px", fontSize: "0.8em" }}>
            按住聊天區域的 🎤 按鈕開始語音輸入
          </small>
        </div>
      );
    } else {
      return (
        <div className="microphone-banner" style={{ backgroundColor: "rgba(150, 0, 0, 0.8)" }}>
          <span>⚠️ 請允許網站使用麥克風，以啟用完整的語音互動功能。</span>
          <button 
            onClick={() => window.location.reload()} 
            style={{ marginLeft: "10px", background: "#fff", color: "#000", border: "none", padding: "3px 8px", borderRadius: "4px", cursor: "pointer" }}
          >
            重試
          </button>
        </div>
      );
    }
  };

  return (
    <>
      {/* 錄音和語音狀態指示器 */}
      <div className="status-indicators">
        <div className={`status-indicator ${isRecording ? 'recording' : ''}`} title="正在錄音">
          {isRecording && <div className="status-dot recording-dot"></div>}
          {isRecording && <span className="status-label">錄音中</span>}
        </div>
        <div className={`status-indicator ${isSpeaking ? 'speaking' : ''}`} title="正在說話">
          {isSpeaking && <div className="status-dot speaking-dot"></div>}
          {isSpeaking && <span className="status-label">播放中</span>}
        </div>
        <div className={`status-indicator ${isProcessing ? 'processing' : ''}`} title="處理中">
          {isProcessing && <div className="status-dot processing-dot"></div>}
          {isProcessing && <span className="status-label">處理中</span>}
        </div>
      </div>
      
      {/* 麥克風權限橫幅 */}
      {renderMicrophoneBanner()}
    </>
  );
};

export default AudioControls; 