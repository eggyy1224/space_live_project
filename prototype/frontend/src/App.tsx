import React, { useState, useCallback, useEffect } from 'react'
import './App.css'

// 引入拆分出的組件
import SceneContainer from './components/layout/SceneContainer'
import AppUI from './components/layout/AppUI'
import ModelDebugger from './components/ModelDebugger'
import ModelAnalyzerTool from './components/ModelAnalyzerTool'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastContainer } from './components/Toast'

// 引入服務
import { 
  useWebSocket, 
  useAudioService, 
  useModelService, 
  useChatService 
} from './services'

// 引入 API 函數
import { speechToText } from './services/api';

// 引入 Zustand Store
import { useStore } from './store'
import logger, { LogCategory } from './utils/LogManager'

function App() {
  // === 添加 useWebSocket 調用 ===
  useWebSocket(); // 調用 hook 以建立 WebSocket 連接
  // === 添加結束 ===

  // 從 Zustand Store 獲取 WebSocket 連接狀態
  const wsConnected = useStore((state) => state.isConnected);
  
  // 使用音頻服務
  const { 
    isRecording, 
    isPlaying: isSpeaking,
    isProcessing: audioProcessing,
    micPermission, 
    startRecording, 
    stopRecording, 
    playAudio
  } = useAudioService();
  
  // 使用模型服務
  const {
    modelLoaded,
    modelUrl,
    modelScale,
    modelRotation,
    modelPosition,
    showSpaceBackground,
    availableAnimations,
    currentAnimation,
    morphTargets,
    setMorphTargetData,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    selectAnimation,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    switchModel
  } = useModelService();
  
  // 使用聊天服務
  const {
    messages,
    sendMessage,
    clearMessages
  } = useChatService();
  
  // 從 Zustand 直接獲取處理狀態
  const chatProcessing = useStore((state) => state.isProcessing);
  
  // 從 Zustand 直接獲取情緒狀態
  const currentEmotionState = useStore((state) => state.currentEmotion);
  const currentEmotion = currentEmotionState.emotion || 'neutral';
  const emotionConfidence = currentEmotionState.confidence || 0;
  
  // 使用本地狀態管理用戶輸入
  const [userInput, setUserInput] = useState('');
  
  // 標籤切換狀態
  const [activeTab, setActiveTab] = useState<'control' | 'chat'>('control');
  
  // 選定的Morph Target
  const [selectedMorphTarget, setSelectedMorphTarget] = useState<string | null>(null);

  // 調試模式狀態
  const [debugMode, setDebugMode] = useState<boolean>(false);
  
  // 模型分析工具狀態
  const [showModelAnalyzer, setShowModelAnalyzer] = useState<boolean>(false);

  // === 定義錄音結束後的回調 ===
  const handleStopRecording = useCallback(async (audioBlob: Blob | null) => {
    if (audioBlob && wsConnected) {
      logger.info('[App] Recording finished. Audio blob received.', LogCategory.GENERAL);
      
      // 設置處理狀態
      useStore.getState().setProcessing(true);
      logger.info('[App] Sending audio to STT service...', LogCategory.GENERAL);
      
      try {
        // 將音頻發送到 STT 服務
        const result = await speechToText(audioBlob);
        
        // 檢查 STT 結果
        if (result && result.text) {
          // 記錄識別的文本
          logger.info(`[App] STT result: "${result.text}"`, LogCategory.GENERAL);
          
          // 將文本發送給聊天服務
          sendMessage(result.text);
        } else {
          logger.warn('[App] STT returned empty text.', LogCategory.GENERAL);
          // 可選：顯示提示給用戶
          // alert('無法識別您的語音，請再試一次。');
        }
      } catch (error) {
        logger.error('[App] STT processing error:', LogCategory.GENERAL, error);
        // 可選：顯示錯誤提示給用戶
        // alert('語音識別失敗，請再試一次。');
      } finally {
        // 無論成功與否，都重置處理狀態
        useStore.getState().setProcessing(false);
      }
      
    } else if (!wsConnected) {
      logger.warn('[App] Recording finished, but WebSocket not connected. Cannot process audio.', LogCategory.GENERAL);
      // 可選：提示用戶連接狀態問題
    } else if (!audioBlob) {
      logger.warn('[App] Recording finished, but audio blob is null.', LogCategory.GENERAL);
    }
  }, [wsConnected, sendMessage]);
  // === 回調定義結束 ===

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
      sendMessage(userInput);
      setUserInput(''); // 清空輸入
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
        // 確保輸入框被清空
        setTimeout(() => setUserInput(''), 50);
      }
    },
    [handleSendMessage, setUserInput]
  );

  return (
    <ErrorBoundary>
      <div className="app-container">
        <SceneContainer 
          modelUrl={modelUrl}
          modelScale={modelScale[0] || 1.0}
          modelRotation={modelRotation}
          modelPosition={modelPosition}
          currentAnimation={currentAnimation}
          morphTargets={morphTargets as unknown as Record<string, number>}
          showSpaceBackground={showSpaceBackground}
          morphTargetDictionary={morphTargets as unknown as Record<string, number> | null}
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
          startRecording={() => startRecording(handleStopRecording)}
          stopRecording={stopRecording}
          playAudio={playAudio}
          // 控制面板相關 props
          modelLoaded={modelLoaded}
          modelScale={modelScale[0] || 1.0}
          currentAnimation={currentAnimation}
          currentEmotion={currentEmotion}
          emotionConfidence={emotionConfidence}
          availableAnimations={availableAnimations}
          morphTargetDictionary={morphTargets as unknown as Record<string, number> | null}
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
          sendMessage={handleSendMessage}
          handleKeyDown={handleKeyDown}
          clearMessages={clearMessages}
          // 調試按鈕相關 props
          debugMode={debugMode}
          showModelAnalyzer={showModelAnalyzer}
          modelUrl={modelUrl} 
          toggleDebugMode={toggleDebugMode}
          toggleModelAnalyzer={toggleModelAnalyzer}
          handleModelSwitch={handleModelSwitch}
        />
        
        {/* 添加Toast通知容器 */}
        <ToastContainer />
      </div>
    </ErrorBoundary>
  )
}

export default App;
