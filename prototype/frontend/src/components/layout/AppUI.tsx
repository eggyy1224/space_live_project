import React from 'react';
// import ChatInterface from '../ChatInterface'; // <-- Remove import
// import ControlPanel from '../ControlPanel'; // <-- Remove import
// import AudioControls from '../AudioControls'; // <-- Remove import

// 定義 AppUI 需要接收的所有 props
interface AppUIProps {
  // // Tab 狀態與切換 (REMOVED)
  // activeTab: 'control' | 'chat';
  // switchTab: (tab: 'control' | 'chat') => void;
  
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
  
  // 新增: 浮動聊天視窗控制
  toggleChatWindow: () => void;
  // 新增: 設定面板控制
  toggleSettingsPanel: () => void;
}

const AppUI: React.FC<AppUIProps> = ({
  // // Tab 狀態與切換 (REMOVED)
  // activeTab,
  // switchTab,
  // WebSocket 連接狀態
  wsConnected,
  // 音頻控制相關 props (Keep for now, maybe needed for status indicators later?)
  isRecording,
  isSpeaking,
  audioProcessing,
  micPermission,
  startRecording, // Pass down to FloatingChatWindow via App
  stopRecording, // Pass down to FloatingChatWindow via App
  playAudio, // Keep if needed elsewhere
  // 控制面板相關 props (Keep for passing to SettingsPanel via App)
  modelLoaded,
  modelScale,
  currentAnimation,
  currentEmotion,
  emotionConfidence,
  availableAnimations,
  morphTargetDictionary,
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
  // 聊天界面相關 props (Keep for passing to FloatingChatWindow via App)
  messages,
  userInput,
  isProcessing,
  setUserInput,
  sendMessage,
  handleKeyDown,
  clearMessages,
  // 新增: 浮動聊天視窗控制
  toggleChatWindow,
  // 新增: 設定面板控制
  toggleSettingsPanel,
}) => {
  // === 添加 micPermission 轉換邏輯 ===
  const micPermissionBool: boolean | null = 
    micPermission === 'granted' ? true : 
    micPermission === 'denied' ? false : 
    null;
  // === 添加結束 ===

  return (
    <>
      {/* // REMOVE AudioControls - Functionality merged or pending migration
      <AudioControls
        isRecording={isRecording}
        isSpeaking={isSpeaking}
        isProcessing={isProcessing || audioProcessing} 
        startRecording={startRecording}
        stopRecording={stopRecording}
        playAudio={playAudio}
        wsConnected={wsConnected}
        micPermission={micPermissionBool}
      />
      */}

      {/* // REMOVE Conditional rendering of ControlPanel/ChatInterface
      {activeTab === 'control' ? (
        <ControlPanel ... />
      ) : (
        <ChatInterface ... />
      )}
      */}

      {/* Keep Debug Buttons and Trigger Buttons */}
      <div 
        // Container for bottom-right buttons (Use Tailwind)
        className="fixed bottom-5 right-5 z-[1000] flex flex-col items-end space-y-2"
      >
        {/* Trigger Floating Chat Window Button */}
        <button
          onClick={toggleChatWindow}
          // Apply Tailwind classes
          className="w-12 h-12 rounded-full bg-green-500 hover:bg-green-600 text-white text-2xl shadow-md flex items-center justify-center cursor-pointer transition-colors duration-200"
          title="開啟/關閉聊天視窗"
          aria-label="開啟/關閉聊天視窗"
        >
          💬
        </button>

        {/* Trigger Settings Panel Button */}
        <button
          onClick={toggleSettingsPanel}
          // Apply Tailwind classes
          className="w-12 h-12 rounded-full bg-gray-600 hover:bg-gray-700 text-white text-2xl shadow-md flex items-center justify-center cursor-pointer transition-colors duration-200"
          title="開啟/關閉設定面板"
          aria-label="開啟/關閉設定面板"
        >
          ⚙️
        </button>
      </div>
    </>
  );
};

export default AppUI; 