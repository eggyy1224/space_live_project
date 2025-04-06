import React, { useState, useCallback, useEffect } from 'react'
import './App.css'

// 引入拆分出的組件
import SceneContainer from './components/layout/SceneContainer'
import AppUI from './components/layout/AppUI'
import ModelDebugger from './components/ModelDebugger'
import ModelAnalyzerTool from './components/ModelAnalyzerTool'
import ErrorBoundary from './components/ErrorBoundary'

// 引入服務
import { 
  useWebSocket, 
  useAudioService, 
  useModelService, 
  useChatService 
} from './services'

// 引入 Zustand Store
import { useStore } from './store'

function App() {
  // === 添加 useWebSocket 調用 ===
  useWebSocket(); // 調用 hook 以建立 WebSocket 連接
  // === 添加結束 ===

  // 從 Zustand Store 獲取 WebSocket 連接狀態
  const wsConnected = useStore((state) => state.isConnected);
  
  // 使用音頻服務
  const { 
    isRecording, 
    isSpeaking, 
    isProcessing: audioProcessing, 
    micPermission,
    startRecording,
    stopRecording,
    playAudio
  } = useAudioService();
  
  // 使用模型服務
  const { 
    modelLoaded,
    modelScale,
    modelRotation,
    modelPosition,
    showSpaceBackground,
    currentAnimation,
    availableAnimations,
    morphTargetDictionary,
    morphTargets,
    manualMorphTargets,
    modelUrl,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    selectAnimation,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    switchModel,
    getManualMorphTargets,
    setMorphTargetData
  } = useModelService();
  
  // 使用聊天服務
  const {
    messages,
    isProcessing: chatProcessing,
    emotion,
    userInput,
    setUserInput,
    sendMessage,
    clearMessages
  } = useChatService();
  
  // 確保傳遞給 AppUI 的 currentEmotion 為 string 類型
  // 使用類型斷言強制轉換
  const currentEmotion = typeof emotion.emotion === 'string' ? emotion.emotion : 'neutral';
  const emotionConfidence = emotion.confidence || 0;
  
  // 標籤切換狀態
  const [activeTab, setActiveTab] = useState<'control' | 'chat'>('control');
  
  // 選定的Morph Target
  const [selectedMorphTarget, setSelectedMorphTarget] = useState<string | null>(null);

  // 調試模式狀態
  const [debugMode, setDebugMode] = useState<boolean>(false);
  
  // 模型分析工具狀態
  const [showModelAnalyzer, setShowModelAnalyzer] = useState<boolean>(false);

  // 使用 useCallback 包裹 switchTab
  const switchTab = useCallback((tab: 'control' | 'chat') => {
    setActiveTab(tab);
  }, []); // 空依賴數組，因為 setActiveTab 的引用是穩定的

  // 切換調試模式 
  const toggleDebugMode = useCallback(() => {
    setDebugMode(prev => !prev);
  }, []);
  
  // 切換模型分析工具
  const toggleModelAnalyzer = useCallback(() => {
    setShowModelAnalyzer(prev => !prev);
  }, []);
  
  // 可用模型列表 (移到 App 頂層，以便傳遞給 AppUI)
  const availableModels = [
    '/models/mixamowomanwithface.glb',
    '/models/headonly.glb',
    '/models/armature001_model.glb'
  ];

  // 切換模型 (需要 useCallback 因為 handleModelSwitch 依賴 modelUrl)
  const handleModelSwitch = useCallback(() => {
    const models = availableModels;
    const currentIndex = models.findIndex(model => modelUrl.includes(model));
    const nextIndex = (currentIndex + 1) % models.length;
    switchModel(models[nextIndex]);
  }, [modelUrl, switchModel, availableModels]);

  // 處理發送消息 (Enter 鍵或點擊按鈕)
  const handleSendMessage = useCallback(() => {
    if (userInput.trim() && wsConnected) { // 確保已連接才發送
      sendMessage();
    } else if (!wsConnected) {
      console.warn("嘗試發送消息但 WebSocket 未連接");
      // 可以選擇性地給用戶提示
      // alert("連接已斷開，請稍後再試。");
    }
  }, [userInput, wsConnected, sendMessage]);

  // 處理鍵盤事件 (Enter發送)
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  return (
    <ErrorBoundary>
      <div className="app-container">
        <SceneContainer 
          modelUrl={modelUrl}
          modelScale={modelScale}
          modelRotation={modelRotation}
          modelPosition={modelPosition}
          currentAnimation={currentAnimation}
          morphTargets={morphTargets}
          showSpaceBackground={showSpaceBackground}
          morphTargetDictionary={morphTargetDictionary}
          getManualMorphTargets={getManualMorphTargets}
          setMorphTargetData={setMorphTargetData}
        />
        
        {/* 調試面板 (保持在 App 層) */}
        {debugMode && <ModelDebugger url={modelUrl} />}
        
        {/* 模型分析工具 (保持在 App 層) */}
        {showModelAnalyzer && <ModelAnalyzerTool availableModels={availableModels} />}
        
        {/* 渲染 AppUI 組件，傳遞所有需要的 props */}
        <AppUI
          // Tab 狀態與切換
          activeTab={activeTab}
          switchTab={switchTab}
          // WebSocket 連接狀態
          wsConnected={wsConnected}
          // 音頻控制相關 props
          isRecording={isRecording}
          isSpeaking={isSpeaking}
          audioProcessing={audioProcessing}
          micPermission={micPermission}
          startRecording={startRecording}
          stopRecording={stopRecording}
          playAudio={playAudio}
          // 控制面板相關 props
          modelLoaded={modelLoaded}
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
          // 聊天界面相關 props
          messages={messages}
          userInput={userInput}
          isProcessing={chatProcessing}
          setUserInput={setUserInput}
          handleKeyDown={handleKeyDown}
          sendMessage={handleSendMessage}
          clearMessages={clearMessages}
          // 調試按鈕相關 props
          debugMode={debugMode}
          showModelAnalyzer={showModelAnalyzer}
          modelUrl={modelUrl} 
          toggleDebugMode={toggleDebugMode}
          toggleModelAnalyzer={toggleModelAnalyzer}
          handleModelSwitch={handleModelSwitch}
        />
      </div>
    </ErrorBoundary>
  )
}

export default App;
