import React, { useState, useCallback } from 'react'
import './App.css'

// 引入拆分出的組件
import ModelViewer from './components/ModelViewer'
import ChatInterface from './components/ChatInterface'
import ControlPanel from './components/ControlPanel'
import AudioControls from './components/AudioControls'
import ModelDebugger from './components/ModelDebugger'
import ModelAnalyzerTool from './components/ModelAnalyzerTool'

// 引入服務
import { 
  useWebSocket, 
  useAudioService, 
  useModelService, 
  useChatService 
} from './services'

function App() {
  // 使用WebSocket服務
  const { isConnected: wsConnected } = useWebSocket();
  
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
    morphTargetInfluences,
    morphTargets,
    modelUrl,
    rotateModel,
    scaleModel,
    resetModel,
    toggleBackground,
    selectAnimation,
    updateMorphTargetInfluence,
    resetAllMorphTargets,
    applyPresetExpression,
    setAnimations,
    setMorphTargetData,
    switchModel
  } = useModelService();
  
  // 使用聊天服務
  const {
    messages,
    isProcessing,
    emotion,
    userInput,
    setUserInput,
    sendMessage,
    clearMessages
  } = useChatService();
  
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

  // 切換調試模式 (不需要 useCallback，除非傳遞給 memoized 子組件)
  const toggleDebugMode = () => {
    setDebugMode(!debugMode);
  };
  
  // 切換模型分析工具 (不需要 useCallback，除非傳遞給 memoized 子組件)
  const toggleModelAnalyzer = () => {
    setShowModelAnalyzer(!showModelAnalyzer);
  };
  
  // 切換模型 (不需要 useCallback，除非傳遞給 memoized 子組件)
  const handleModelSwitch = () => {
    // 定義模型循環順序
    const models = [
      '/models/headonly.glb',
      '/models/mixamowomanwithface.glb',
      '/models/armature001_model.glb'
    ];
    
    // 找出當前模型在數組中的索引
    const currentIndex = models.findIndex(model => modelUrl.includes(model));
    
    // 計算下一個模型的索引（循環）
    const nextIndex = (currentIndex + 1) % models.length;
    
    // 切換到下一個模型
    switchModel(models[nextIndex]);
  };
  
  // 可用模型列表
  const availableModels = [
    '/models/mixamowomanwithface.glb',
    '/models/headonly.glb',
    '/models/armature001_model.glb'
  ];

  // 為傳遞給 ModelViewer 的函數創建 useCallback 版本
  const handleSetMorphTargetDictionary = useCallback((dict: Record<string, number> | null) => {
    setMorphTargetData(dict, null);
    // setMorphTargetData 來自 useModelService，其引用理論上穩定，但為確保，可以加入依賴
  }, [setMorphTargetData]); 

  const handleSetMorphTargetInfluences = useCallback((inf: number[] | null) => {
    setMorphTargetData(null, inf);
    // setMorphTargetData 來自 useModelService，其引用理論上穩定，但為確保，可以加入依賴
  }, [setMorphTargetData]);

  return (
    <div className="app-container">
      {/* 3D 模型顯示 - 傳遞 useCallback 後的函數 */}
      <ModelViewer 
        modelUrl={modelUrl}
        modelScale={modelScale}
        modelRotation={modelRotation}
        modelPosition={modelPosition}
        currentAnimation={currentAnimation}
        morphTargets={morphTargets}
        showSpaceBackground={showSpaceBackground}
        setAvailableAnimations={setAnimations} // 來自 useModelService，引用穩定
        setMorphTargetDictionary={handleSetMorphTargetDictionary}
        setMorphTargetInfluences={handleSetMorphTargetInfluences}
        morphTargetDictionary={morphTargetDictionary} // 來自 useModelService
        morphTargetInfluences={morphTargetInfluences} // 來自 useModelService
      />
      
      {/* 調試面板 */}
      {debugMode && <ModelDebugger url={modelUrl} />}
      
      {/* 模型分析工具 */}
      {showModelAnalyzer && <ModelAnalyzerTool availableModels={availableModels} />}
      
      {/* 音頻控制 */}
      <AudioControls 
        isRecording={isRecording}
        isSpeaking={isSpeaking}
        isProcessing={isProcessing || audioProcessing}
        startRecording={startRecording}
        stopRecording={stopRecording}
        playAudio={playAudio}
        wsConnected={wsConnected}
        micPermission={micPermission}
      />
      
      {/* 控制面板和聊天界面 - 傳遞 useCallback 後的 switchTab */}
      {activeTab === 'control' ? (
        <ControlPanel 
          activeTab={activeTab}
          switchTab={switchTab}
          wsConnected={wsConnected}
          isModelLoaded={modelLoaded}
          modelScale={modelScale}
          currentAnimation={currentAnimation}
          currentEmotion={emotion.emotion}
          emotionConfidence={emotion.confidence}
          availableAnimations={availableAnimations} // 來自 useModelService
          morphTargetDictionary={morphTargetDictionary} // 來自 useModelService
          morphTargetInfluences={morphTargetInfluences} // 來自 useModelService
          selectedMorphTarget={selectedMorphTarget}
          setSelectedMorphTarget={setSelectedMorphTarget} // 來自 useState，引用穩定
          // 以下函數來自 useModelService，引用穩定
          updateMorphTargetInfluence={updateMorphTargetInfluence}
          resetAllMorphTargets={resetAllMorphTargets}
          rotateModel={rotateModel}
          scaleModel={scaleModel}
          resetModel={resetModel}
          toggleBackground={toggleBackground}
          selectAnimation={selectAnimation}
          applyPresetExpression={applyPresetExpression}
          // 以下 prop 來自 useState 或 useWebSocket/useChatService，引用穩定
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
          startRecording={startRecording}
          stopRecording={stopRecording}
          isRecording={isRecording}
          activeTab={activeTab}
          switchTab={switchTab} // 也傳遞給 ChatInterface
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
    </div>
  )
}

export default App
