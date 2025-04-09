import React, { useState, useCallback, useEffect } from 'react'
import './App.css'

// 引入拆分出的組件
import SceneContainer from './components/SceneContainer'
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
  useHeadService,
  useChatService,
  useBodyService
} from './services'

// 引入 API 函數
import { speechToText, processSpeechAudio } from './services/api';

// 引入 AudioService
import AudioService from './services/AudioService';

// 引入 Zustand Store
import { useStore } from './store'
import logger, { LogCategory } from './utils/LogManager'
import { toast } from 'react-hot-toast'

// --- 引入模型設定 ---
// import { AVAILABLE_MODELS } from './config/modelConfig';
// --- 引入結束 ---

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
    isSpeaking,
    isProcessing: audioProcessing,
    micPermission, 
    startRecording, 
    stopRecording, 
    playAudio
  } = useAudioService();
  
  // --- 使用頭部服務 (替換 useModelService) ---
  const {
    headModelLoaded,
    headModelUrl,
    modelScale,
    modelRotation,
    modelPosition,
    showSpaceBackground,
    morphTargets,
    morphTargetDictionary,
    setMorphTargetData,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    switchHeadModel
  } = useHeadService();
  // --- 結束 --- 
  
  // --- 使用身體服務 ---
  const {
    availableAnimations,
    currentAnimation,
    selectAnimation
  } = useBodyService();
  // --- 結束 ---
  
  // 使用聊天服務
  const {
    messages,
    sendMessage,
    clearMessages
  } = useChatService();
  
  // 從 Zustand 直接獲取處理狀態
  const chatProcessing = useStore((state) => state.isProcessing);
  
  // 從 Zustand 直接獲取情緒狀態
  const currentEmotion = useStore((state) => state.currentEmotion.emotion || 'neutral');
  const emotionConfidence = useStore((state) => state.currentEmotion.confidence || 0);
  
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
          toast('無法處理您的語音，請再試一次。');
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
          headModelUrl={headModelUrl}
          isHeadModelLoaded={headModelLoaded}
          showSpaceBackground={showSpaceBackground}
        />
        
        {/* 調試面板 (保持在 App 層) */}
        {debugMode && <ModelDebugger url={headModelUrl} />}
        
        {/* 模型分析工具 (保持在 App 層) */}
        {showModelAnalyzer && <div>模型分析工具 (模型列表待定)</div>}

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
          // Pass head model control props
          isModelLoaded={headModelLoaded}
          modelScale={modelScale[0] || 1.0}
          morphTargetDictionary={morphTargetDictionary}
          selectedMorphTarget={selectedMorphTarget}
          setSelectedMorphTarget={setSelectedMorphTarget}
          updateMorphTargetInfluence={updateMorphTargetInfluence}
          resetAllMorphTargets={resetAllMorphTargets}
          rotateModel={rotateModel}
          scaleModel={scaleModel}
          resetModel={resetModel}
          toggleBackground={toggleBackground}
          applyPresetExpression={applyPresetExpression}
          showSpaceBackground={showSpaceBackground}
          // Pass body animation props
          availableAnimations={availableAnimations} 
          currentAnimation={currentAnimation} 
          selectAnimation={selectAnimation} 
          // Pass emotion state for display
          currentEmotion={currentEmotion}
          emotionConfidence={emotionConfidence}
          // Pass Debug Control Props
          debugMode={debugMode}
          showModelAnalyzer={showModelAnalyzer}
          modelUrl={headModelUrl} // Use headModelUrl here
          toggleDebugMode={toggleDebugMode}
          toggleModelAnalyzer={toggleModelAnalyzer}
          handleModelSwitch={() => { logger.warn('Model switching is temporarily disabled.', LogCategory.GENERAL); }} // Placeholder
        />
        {/* <--- 結束 ---> */}
        
        {/* 渲染 AppUI (只傳遞必要 props) */}
        <AppUI
          wsConnected={wsConnected} // <-- 從 Zustand 讀取
          toggleChatWindow={toggleChatWindow} // <-- 從 Zustand action
          toggleSettingsPanel={toggleSettingsPanel} // <-- 從 Zustand action
        />
        
        <ToastContainer />
      </div>
    </ErrorBoundary>
  )
}

export default App;
