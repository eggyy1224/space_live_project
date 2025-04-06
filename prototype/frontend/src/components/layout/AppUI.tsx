import React from 'react';
import ChatInterface from '../ChatInterface';
import ControlPanel from '../ControlPanel';
import AudioControls from '../AudioControls';

// 定義 AppUI 需要接收的所有 props
interface AppUIProps {
  // Tab 狀態與切換
  activeTab: 'control' | 'chat';
  switchTab: (tab: 'control' | 'chat') => void;
  
  // WebSocket 連接狀態
  wsConnected: boolean;
  
  // 音頻控制相關 props
  isRecording: boolean;
  isSpeaking: boolean;
  audioProcessing: boolean;
  micPermission: string;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  playAudio: (url: string) => void;
  
  // 控制面板相關 props
  modelLoaded: boolean;
  modelScale: number;
  currentAnimation: string | null;
  currentEmotion: string;
  emotionConfidence: number;
  availableAnimations: string[];
  morphTargetDictionary: Record<string, number> | null;
  manualMorphTargets: Record<string, number>;
  selectedMorphTarget: string | null;
  setSelectedMorphTarget: (target: string | null) => void;
  updateMorphTargetInfluence: (name: string, value: number) => void;
  resetAllMorphTargets: () => void;
  rotateModel: (direction: 'right' | 'left') => void;
  scaleModel: (factor: number) => void;
  resetModel: () => void;
  toggleBackground: () => void;
  selectAnimation: (name: string) => void;
  applyPresetExpression: (expression: string) => Promise<boolean>;
  showSpaceBackground: boolean;
  
  // 聊天界面相關 props
  messages: any[]; // 替換為更精確的類型
  userInput: string;
  isProcessing: boolean;
  setUserInput: (input: string) => void;
  sendMessage: () => void; // 修改這裡，對應 App.tsx 傳遞的函數
  handleKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void; // 添加 handleKeyDown
  clearMessages: () => void; // 添加 clearMessages
  
  // 調試按鈕相關 props
  debugMode: boolean;
  showModelAnalyzer: boolean;
  modelUrl: string; // 用於顯示在切換模型按鈕上
  toggleDebugMode: () => void;
  toggleModelAnalyzer: () => void;
  handleModelSwitch: () => void;
}

const AppUI: React.FC<AppUIProps> = ({
  activeTab,
  switchTab,
  wsConnected,
  isRecording,
  isSpeaking,
  audioProcessing,
  micPermission,
  startRecording,
  stopRecording,
  playAudio,
  modelLoaded,
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
  messages,
  userInput,
  isProcessing,
  setUserInput,
  sendMessage,
  handleKeyDown, // 接收 handleKeyDown
  clearMessages, // 接收 clearMessages
  debugMode,
  showModelAnalyzer,
  modelUrl,
  toggleDebugMode,
  toggleModelAnalyzer,
  handleModelSwitch,
}) => {
  return (
    <>
      {/* 音頻控制 */}
      <AudioControls
        isRecording={isRecording}
        isSpeaking={isSpeaking}
        isProcessing={isProcessing || audioProcessing} // 組合後端和前端的處理狀態
        startRecording={startRecording}
        stopRecording={stopRecording}
        playAudio={playAudio}
        wsConnected={wsConnected}
        micPermission={micPermission}
      />

      {/* 控制面板和聊天界面 */}
      {activeTab === 'control' ? (
        <ControlPanel
          activeTab={activeTab}
          switchTab={switchTab}
          wsConnected={wsConnected}
          isModelLoaded={modelLoaded}
          modelScale={modelScale}
          currentAnimation={currentAnimation}
          currentEmotion={currentEmotion}
          emotionConfidence={emotionConfidence}
          availableAnimations={availableAnimations}
          morphTargetDictionary={morphTargetDictionary}
          manualMorphTargets={manualMorphTargets}
          selectedMorphTarget={selectedMorphTarget}
          setSelectedMorphTarget={setSelectedMorphTarget}
          updateMorphTargetInfluence={updateMorphTargetInfluence}
          resetAllMorphTargets={resetAllMorphTargets}
          rotateModel={rotateModel}
          scaleModel={scaleModel}
          resetModel={resetModel}
          toggleBackground={toggleBackground}
          selectAnimation={selectAnimation}
          applyPresetExpression={applyPresetExpression}
          showSpaceBackground={showSpaceBackground}
        />
      ) : (
        <ChatInterface
          messages={messages}
          userInput={userInput}
          isProcessing={isProcessing}
          wsConnected={wsConnected}
          setUserInput={setUserInput}
          sendMessage={sendMessage}
          handleKeyDown={handleKeyDown}
          clearMessages={clearMessages}
          startRecording={startRecording}
          stopRecording={stopRecording}
          isRecording={isRecording}
          activeTab={activeTab}
          switchTab={switchTab}
        />
      )}

      {/* 調試按鈕 */}
      <div style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        <button
          onClick={toggleDebugMode}
          style={{
            padding: '5px 10px',
            background: debugMode ? '#f44336' : '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {debugMode ? '關閉調試' : '開啟調試'}
        </button>

        <button
          onClick={toggleModelAnalyzer}
          style={{
            padding: '5px 10px',
            background: showModelAnalyzer ? '#f44336' : '#9C27B0',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {showModelAnalyzer ? '關閉模型分析' : '模型分析工具'}
        </button>

        <button
          onClick={handleModelSwitch}
          style={{
            padding: '5px 10px',
            background: '#FF9800',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          切換模型：{modelUrl.split('/').pop()?.replace('.glb', '')}
        </button>
      </div>
    </>
  );
};

export default AppUI; 