import React, { useState, useCallback, useEffect } from 'react'
import './App.css'

// 引入拆分出的組件
import SceneContainer from './components/layout/SceneContainer'
import AppUI from './components/layout/AppUI'
import ModelDebugger from './components/ModelDebugger'
import ModelAnalyzerTool from './components/ModelAnalyzerTool'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastContainer } from './components/Toast'
import FloatingChatWindow from './components/FloatingChatWindow'
import SettingsPanel from './components/SettingsPanel'

// 引入服務
import { 
  useWebSocket, 
  useAudioService, 
  useModelService, 
  useChatService 
} from './services'

// 引入 API 函數
import { speechToText, processSpeechAudio } from './services/api';

// 引入 AudioService
import AudioService from './services/AudioService';

// 引入 Zustand Store
import { useStore } from './store'
import logger, { LogCategory } from './utils/LogManager'
import { toast } from 'react-hot-toast'

function App() {
  // === 添加 useWebSocket 調用 ===
  useWebSocket(); // 調用 hook 以建立 WebSocket 連接
  // === 添加結束 ===

  // 從 Zustand Store 獲取 WebSocket 連接狀態
  const wsConnected = useStore((state) => state.isConnected);
  
  // 從 Zustand Store 獲取聊天視窗狀態和操作
  const isChatWindowVisible = useStore((state) => state.isChatWindowVisible);
  const toggleChatWindow = useStore((state) => state.toggleChatWindow);
  
  // <--- 從 Zustand Store 獲取設定面板狀態和操作 --->
  const isSettingsPanelVisible = useStore((state) => state.isSettingsPanelVisible);
  const toggleSettingsPanel = useStore((state) => state.toggleSettingsPanel);
  // <--- 結束 --->
  
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
    morphTargetDictionary,
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
  
  // 選定的Morph Target
  const [selectedMorphTarget, setSelectedMorphTarget] = useState<string | null>(null);

  // 調試模式狀態
  const [debugMode, setDebugMode] = useState<boolean>(false);
  
  // 模型分析工具狀態
  const [showModelAnalyzer, setShowModelAnalyzer] = useState<boolean>(false);

  // --- Zustand State and Actions ---
  const setProcessing = useStore((state) => state.setProcessing); // <-- Get action via selector
  // --- End Zustand --- 

  // === 定義錄音結束後的回調 ===
  const handleStopRecording = useCallback(async (audioBlob: Blob | null) => {
    if (audioBlob && wsConnected) {
      logger.info('[App] Sending audio for processing...', LogCategory.GENERAL); // 更新日誌
      
      try {
        // 將音頻發送到後端進行完整處理
        const result = await processSpeechAudio(audioBlob); // 改為呼叫 processSpeechAudio
        
        // 檢查處理結果
        if (result && result.success && result.audio) {
          // 記錄識別和回應文本
          logger.info(`[App] STT: "${result.text}"`, LogCategory.GENERAL);
          logger.info(`[App] Response: "${result.response}"`, LogCategory.GENERAL);
          
          // 播放返回的音頻 (假設 AudioService.playAudio 接受 Base64)
          // 注意：playAudio 可能需要調整以接受 Base64 或轉換為 Blob URL
          AudioService.getInstance().playAudio(`data:audio/mp3;base64,${result.audio}`);
          
          // 可選：將 AI 回應添加到聊天記錄 (如果需要顯示的話)
          // addMessage({ sender: 'ai', text: result.response });
          
        } else if (result && !result.success) {
          logger.error(`[App] Audio processing failed: ${result.error}`, LogCategory.GENERAL);
          // 可選：顯示錯誤提示給用戶
          toast.error(`語音處理失敗: ${result.error || '未知錯誤'}`); 
        } else {
          logger.warn('[App] Audio processing returned unexpected result or no audio.', LogCategory.GENERAL);
          toast.warn('無法處理您的語音，請再試一次。');
        }
      } catch (error) {
        logger.error('[App] Audio processing API call error:', LogCategory.GENERAL, error);
        // 可選：顯示錯誤提示給用戶
        toast.error(`語音處理請求失敗: ${error instanceof Error ? error.message : '未知網絡錯誤'}`);
      } finally {
        // 無論成功與否，都重置處理狀態
        setProcessing(false); // <-- Use action from selector
      }
      
    } else if (!wsConnected) {
      logger.warn('[App] Recording finished, but WebSocket not connected. Cannot process audio.', LogCategory.GENERAL);
      // 可選：提示用戶連接狀態問題
    } else if (!audioBlob) {
      logger.warn('[App] Recording finished, but audio blob is null.', LogCategory.GENERAL);
    }
  }, [wsConnected, setProcessing]); // <-- Add setProcessing to dependency array
  // === 回調定義結束 ===

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
          showSpaceBackground={showSpaceBackground}
          morphTargetDictionary={morphTargetDictionary}
          setMorphTargetData={setMorphTargetData}
        />
        
        {/* 調試面板 (保持在 App 層) */}
        {debugMode && <ModelDebugger url={modelUrl} />}
        
        {/* 模型分析工具 (保持在 App 層) */}
        {showModelAnalyzer && <ModelAnalyzerTool availableModels={availableModels} />}

        {/* 渲染新的浮動聊天視窗 */}
        <FloatingChatWindow 
          isVisible={isChatWindowVisible}
          onClose={toggleChatWindow}
          messages={messages || []}
          userInput={userInput}
          setUserInput={setUserInput}
          isProcessing={chatProcessing}
          wsConnected={wsConnected}
          sendMessage={handleSendMessage}
          handleKeyDown={handleKeyDown}
          clearMessages={clearMessages}
          isRecording={isRecording}
          startRecording={() => startRecording(handleStopRecording)}
          stopRecording={stopRecording}
        />

        {/* <--- 渲染設定面板 ---> */}
        <SettingsPanel
          isVisible={isSettingsPanelVisible}
          onClose={toggleSettingsPanel}
          // Pass model control props
          isModelLoaded={modelLoaded}
          modelScale={modelScale[0] || 1.0}
          currentAnimation={currentAnimation}
          availableAnimations={availableAnimations}
          morphTargetDictionary={morphTargetDictionary}
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
          // Pass emotion state for display (optional, but was in old panel)
          currentEmotion={currentEmotion}
          emotionConfidence={emotionConfidence}
          // Pass Debug Control Props
          debugMode={debugMode}                 // Pass debugMode state
          showModelAnalyzer={showModelAnalyzer} // Pass modelAnalyzer state
          modelUrl={modelUrl}                   // Pass modelUrl for display
          toggleDebugMode={toggleDebugMode}       // Pass toggle function
          toggleModelAnalyzer={toggleModelAnalyzer} // Pass toggle function
          handleModelSwitch={handleModelSwitch}   // Pass switch function
        />
        {/* <--- 結束 ---> */}
        
        {/* 渲染 AppUI 組件，傳遞所有需要的 props */}
        <AppUI
          // WebSocket 連接狀態
          wsConnected={wsConnected}
          // 音頻控制相關 props (部分傳遞給 FloatingChatWindow)
          // isRecording={isRecording} // No longer needed here
          // isSpeaking={isSpeaking} // No longer needed here
          // audioProcessing={audioProcessing} // No longer needed here
          // micPermission={micPermission} // No longer needed here
          // playAudio={playAudio} // If not needed, remove later
          
          // 傳遞 toggleChatWindow 給 AppUI 以便添加觸發按鈕
          toggleChatWindow={toggleChatWindow}
          // 傳遞 toggleSettingsPanel 給 AppUI 以便添加觸發按鈕
          toggleSettingsPanel={toggleSettingsPanel}
        />
        
        <ToastContainer />
      </div>
    </ErrorBoundary>
  )
}

export default App;
