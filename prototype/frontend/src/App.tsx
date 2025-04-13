import React, { useState, useCallback, useEffect, useRef } from 'react'
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

// Define a more comprehensive type for expected WebSocket messages
// Especially focusing on the structure we parse for animation name
interface ChatMessagePayload {
  id?: string;
  role?: string;
  content?: string;
  bodyAnimationName?: string | null; // 可能是字符串或 null
  bodyAnimationSequence?: Array<{
    name: string;
    proportion: number;
    transitionDuration?: number;
    loop?: boolean;
    weight?: number;
  }>; // 新增：動畫序列
  timestamp?: any; // Keep as any for now
  audioUrl?: string | null;
  audio_duration?: number; // 新增：音頻時長
}

interface BackendMessage {
  type?: string; // Message type identifier (e.g., 'chat-message', 'emotionalTrajectory')
  message?: ChatMessagePayload; // Payload for chat messages
  payload?: any; // Payload for other message types like emotionalTrajectory
  // ... other potential top-level fields from different message types
}

function App() {
  // === 添加 useWebSocket 調用 ===
  useWebSocket(); // 調用 hook 以建立 WebSocket 連接
  // === 添加結束 ===

  // 從 Zustand Store 獲取 WebSocket 連接狀態
  const wsConnected = useStore((state) => state.isConnected);
  // 從 Zustand Store 獲取最後的 WebSocket 訊息
  const lastJsonMessage = useStore((state) => state.lastJsonMessage) as BackendMessage | null; // Add type assertion
  
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

  // --- 從 Zustand 獲取/設置建議的動畫名稱 ---
  const suggestedAnimationName = useStore((state) => state.suggestedAnimationName);
  const setSuggestedAnimationName = useStore((state) => state.setSuggestedAnimationName);

  // --- 從 Zustand 獲取/設置動畫序列相關的狀態和操作 ---
  const animationSequence = useStore((state) => state.animationSequence);
  const setAnimationSequence = useStore((state) => state.setAnimationSequence);
  const startSequencePlayback = useStore((state) => state.startSequencePlayback);
  const stopSequencePlayback = useStore((state) => state.stopSequencePlayback);

  // 處理 WebSocket 訊息，提取並設置建議的動畫名稱到 Zustand
  useEffect(() => {
    // 使用 JSON.stringify 確保傳遞給 logger 的是字符串
    logger.debug(`[AppWS Parse Effect] Running. lastJsonMessage: ${JSON.stringify(lastJsonMessage)}`, LogCategory.WEBSOCKET);
    // Assert lastJsonMessage to our more comprehensive type
    const currentMessage = lastJsonMessage as BackendMessage | null;

    // 檢查是否是 chat-message 類型並且包含 message 負載
    if (currentMessage && currentMessage.type === 'chat-message') {
        logger.debug('[AppWS Parse Effect] Condition 1 passed: Message exists and type is chat-message.', LogCategory.WEBSOCKET);
        if (currentMessage.message && typeof currentMessage.message === 'object') {
            logger.debug('[AppWS Parse Effect] Condition 2 passed: Message payload exists and is object.', LogCategory.WEBSOCKET);
            
            // message 負載現在符合 ChatMessagePayload 類型
            const messagePayload = currentMessage.message;
            
            // 處理 bodyAnimationSequence (新增)
            if ('bodyAnimationSequence' in messagePayload && 
                Array.isArray(messagePayload.bodyAnimationSequence) && 
                messagePayload.bodyAnimationSequence.length > 0) {
                
                logger.info(`[AppWS] Received animation sequence with ${messagePayload.bodyAnimationSequence.length} keyframes.`, LogCategory.WEBSOCKET);
                
                // 儲存動畫序列到 Zustand
                setAnimationSequence(messagePayload.bodyAnimationSequence);
                
                // 不再處理 bodyAnimationName，因為使用序列
                return;
            }
            
            // 如果沒有序列，則回退到處理單一動畫名稱
            if ('bodyAnimationName' in messagePayload) {
                logger.debug('[AppWS Parse Effect] Condition 3 passed: bodyAnimationName key exists in payload.', LogCategory.WEBSOCKET);
                const backendAnimationName = messagePayload.bodyAnimationName;
                logger.debug(`[AppWS Parse Effect] Extracted bodyAnimationName: ${backendAnimationName}`, LogCategory.WEBSOCKET);
                
                // 檢查提取到的名稱是否為字符串 (可能為 null)
                if (typeof backendAnimationName === 'string' && backendAnimationName.trim() !== '') {
                  logger.debug('[AppWS Parse Effect] Condition 4 passed: Animation name is a non-empty string.', LogCategory.WEBSOCKET);
                  // 驗證是否在可用動畫列表中 (可選但建議)
                  if (availableAnimations.includes(backendAnimationName)) {
                      logger.info(`[AppWS] Received suggested animation: ${backendAnimationName} from chat-message. Storing to Zustand...`, LogCategory.WEBSOCKET);
                      // 存儲到 Zustand
                      setSuggestedAnimationName(backendAnimationName);
                  } else {
                       logger.warn(`[AppWS] Received suggested animation "${backendAnimationName}" not in available list. Ignoring. Available: ${availableAnimations.join(', ')}`, LogCategory.WEBSOCKET);
                       // setSuggestedAnimationName(null);
                  }
                } else if (backendAnimationName === null || backendAnimationName === '') {
                   // 如果後端明確發送 null 或空字符串
                   logger.info(`[AppWS] Received null/empty suggested animation. Setting to null.`, LogCategory.WEBSOCKET);
                   // 設置為 null
                   setSuggestedAnimationName(null);
                } else {
                   logger.warn(`[AppWS] Received bodyAnimationName but it's not a valid string or null: ${backendAnimationName}`, LogCategory.WEBSOCKET);
                }
             } else {
                 logger.debug('[AppWS Parse Effect] Condition 3 FAILED: bodyAnimationName key NOT in payload.', LogCategory.WEBSOCKET);
             }
        } else {
             logger.debug('[AppWS Parse Effect] Condition 2 FAILED: Message payload does not exist or is not an object.', LogCategory.WEBSOCKET);
        }
    } else {
         logger.debug('[AppWS Parse Effect] Condition 1 FAILED: Message is null or type is not chat-message.', LogCategory.WEBSOCKET);
    }
    // 可以添加對其他消息類型的處理
  }, [lastJsonMessage, availableAnimations, setSuggestedAnimationName, setAnimationSequence]); // 依賴項添加 setAnimationSequence
  // ------------------------------------

  // --- 同步身體動畫與語音狀態 ---
  const prevIsSpeaking = useRef<boolean>(isSpeaking);
  const sequenceTimers = useRef<number[]>([]);  // 新增：存放定時器 ID 的數組

  // 新增：清理所有動畫序列定時器的函數
  const clearAllSequenceTimers = () => {
    sequenceTimers.current.forEach(timerId => {
      clearTimeout(timerId);
    });
    sequenceTimers.current = [];
  };

  // 第一部分: 監聽 isSpeaking 狀態變化，處理動畫序列/單一動畫播放
  useEffect(() => {
    // 監聽 isSpeaking 狀態變化
    const speakingStarted = !prevIsSpeaking.current && isSpeaking;
    const speakingStopped = prevIsSpeaking.current && !isSpeaking;
    
    // ---> Add logging here <--- 
    logger.debug(`[AppSync Effect Check] isSpeaking: ${isSpeaking}, prevIsSpeaking: ${prevIsSpeaking.current}, suggestedAnimationName: ${suggestedAnimationName}, animationSequence length: ${animationSequence.length}`, LogCategory.ANIMATION);
    // ---> End logging <--- 

    if (speakingStarted) {
      // 清理任何先前的定時器
      clearAllSequenceTimers();
      
      // 檢查是否有動畫序列
      if (animationSequence.length > 0) {
        // 獲取音頻時長 (從 Zustand store)
        const audioDuration = useStore.getState().audioDuration;
        
        if (audioDuration && audioDuration > 0) {
          logger.info(`[AppSync] Speech started. Playing animation sequence with ${animationSequence.length} keyframes over ${audioDuration.toFixed(2)} seconds.`, LogCategory.ANIMATION);
          
          // 設置動畫序列開始
          startSequencePlayback(); // 這會立即播放第一個動畫
          
          // 為每個後續的動畫設置定時器
          animationSequence.forEach((keyframe, index) => {
            // 跳過第一個動畫，因為它已經在 startSequencePlayback 中開始播放
            if (index === 0) return;
            
            // 計算該動畫的絕對開始時間（毫秒）
            const startTimeMs = keyframe.proportion * audioDuration * 1000;
            
            // 設置定時器
            const timerId = window.setTimeout(() => {
              // 確保仍然在播放狀態和序列播放模式
              if (useStore.getState().isSpeaking && useStore.getState().isPlayingSequence) {
                logger.info(`[AppSync] Playing animation ${keyframe.name} at ${startTimeMs.toFixed(0)}ms (proportion: ${keyframe.proportion})`, LogCategory.ANIMATION);
                useStore.getState().playNextInSequence(index);
              }
            }, startTimeMs);
            
            // 保存定時器 ID 以供後續清除
            sequenceTimers.current.push(timerId);
          });
        } else {
          logger.warn(`[AppSync] Cannot play animation sequence: audio duration is not available or invalid (${audioDuration})`, LogCategory.ANIMATION);
          // 回退到只播放第一個動畫
          if (animationSequence[0] && animationSequence[0].name) {
            selectAnimation(animationSequence[0].name);
          } else {
            // 完全回退到單一動畫名稱處理
            const animToPlay = suggestedAnimationName || 'Idle';
            selectAnimation(animToPlay);
          }
        }
      } else {
        // 如果沒有序列，則使用單一動畫名稱（向後兼容）
        const animToPlay = suggestedAnimationName || 'Idle'; // 如果 Zustand 中沒有建議，播放 Idle
        logger.info(`[AppSync] Speech started. Playing single animation: ${animToPlay}`, LogCategory.ANIMATION);
        selectAnimation(animToPlay);
      }
    } else if (speakingStopped) {
      // 語音停止播放，清理定時器並停止序列播放
      clearAllSequenceTimers();
      
      // 停止序列播放（會切換回 Idle）
      stopSequencePlayback();
      
      logger.info(`[AppSync] Speech stopped. Cleared all timers and reset to Idle animation.`, LogCategory.ANIMATION);
    }

    // 更新 previous state
    prevIsSpeaking.current = isSpeaking;

    // 組件卸載時清理定時器
    return () => {
      clearAllSequenceTimers();
    };

  }, [isSpeaking, selectAnimation, suggestedAnimationName, availableAnimations, animationSequence, startSequencePlayback, stopSequencePlayback]); // 依賴項添加序列相關項
  // ----------------------------

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
          modelScale={modelScale}
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
          modelScale={modelScale}
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
