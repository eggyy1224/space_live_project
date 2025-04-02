# 虛擬太空人互動原型

本項目是一個虛擬太空人互動原型，實現了以下功能：

1. 3D模型加載和控制
2. 語音輸入和輸出
3. 聊天界面
4. 表情控制

## 服務模塊架構

項目採用模塊化的服務架構，分為以下幾個核心服務：

### WebSocketService

管理WebSocket連接和消息處理。

```typescript
// 導入服務
import { useWebSocket } from './services';

// 在組件中使用
function MyComponent() {
  const { 
    isConnected,          // WebSocket連接狀態
    sendMessage,          // 發送任意消息
    sendTextMessage,      // 發送文本消息
    registerHandler,      // 註冊消息處理器
    removeHandler         // 移除消息處理器
  } = useWebSocket();
  
  return (
    <div>連接狀態: {isConnected ? '已連接' : '未連接'}</div>
  );
}
```

### AudioService

管理音頻錄製和播放功能。

```typescript
// 導入服務
import { useAudioService } from './services';

// 在組件中使用
function MyComponent() {
  const { 
    isRecording,          // 是否正在錄音
    isSpeaking,           // 是否正在播放語音
    isProcessing,         // 是否正在處理音頻
    micPermission,        // 麥克風權限狀態
    startRecording,       // 開始錄音
    stopRecording,        // 停止錄音
    playAudio             // 播放音頻
  } = useAudioService();
  
  return (
    <div>
      <button 
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
      >
        {isRecording ? '正在錄音...' : '按住說話'}
      </button>
    </div>
  );
}
```

### ModelService

管理3D模型加載和控制。

```typescript
// 導入服務
import { useModelService } from './services';

// 在組件中使用
function MyComponent() {
  const { 
    modelLoaded,           // 模型是否已加載
    modelScale,            // 模型縮放
    modelRotation,         // 模型旋轉
    modelPosition,         // 模型位置
    showSpaceBackground,   // 是否顯示太空背景
    currentAnimation,      // 當前動畫
    availableAnimations,   // 可用動畫列表
    morphTargets,          // Morph Target 值
    rotateModel,           // 旋轉模型
    scaleModel,            // 縮放模型
    resetModel,            // 重置模型
    toggleBackground,      // 切換背景
    selectAnimation,       // 選擇動畫
    updateMorphTargetInfluence,  // 更新Morph Target影響值
    resetAllMorphTargets,        // 重置所有Morph Target
    applyPresetExpression        // 應用預設表情
  } = useModelService();
  
  return (
    <div>
      <button onClick={() => rotateModel('left')}>向左旋轉</button>
      <button onClick={() => rotateModel('right')}>向右旋轉</button>
      <button onClick={() => scaleModel(0.1)}>放大</button>
      <button onClick={() => scaleModel(-0.1)}>縮小</button>
      <button onClick={resetModel}>重置</button>
      <button onClick={toggleBackground}>
        {showSpaceBackground ? '隱藏星空' : '顯示星空'}
      </button>
    </div>
  );
}
```

### ChatService

管理聊天消息和對話狀態。

```typescript
// 導入服務
import { useChatService } from './services';

// 在組件中使用
function MyComponent() {
  const { 
    messages,           // 聊天消息列表
    isProcessing,       // 是否正在處理消息
    emotion,            // 當前情緒狀態
    userInput,          // 用戶輸入
    setUserInput,       // 設置用戶輸入
    sendMessage,        // 發送消息
    clearMessages       // 清空聊天記錄
  } = useChatService();
  
  return (
    <div>
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <input 
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
      />
      <button onClick={sendMessage}>發送</button>
    </div>
  );
}
```

## 擴展服務

可以通過以下方式擴展現有服務或添加新服務：

1. 在 `services` 目錄下創建新的服務文件
2. 實現服務類和 React Hook
3. 在 `services/index.ts` 中導出服務

## 技術棧

- React
- TypeScript
- Three.js / React Three Fiber
- WebSocket
- Web Audio API 