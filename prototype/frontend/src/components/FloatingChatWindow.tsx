import React, { useRef, useEffect, useState, useCallback } from 'react';
import Draggable from 'react-draggable';
import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css'; // Import default styles for resizable

import { ChatMessage } from '../store/slices/chatSlice'; // Import ChatMessage type

interface FloatingChatWindowProps {
  // TODO: Define props later (e.g., messages, input state, send function, visibility toggle)
  isVisible: boolean; // Example prop to control visibility
  onClose: () => void; // Example prop to handle closing
  // Chat related props
  messages: ChatMessage[];
  userInput: string;
  isProcessing: boolean;
  wsConnected: boolean; // Needed for enabling/disabling input
  setUserInput: (input: string) => void;
  sendMessage: () => void;
  handleKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  clearMessages: () => void;
  // Audio related props for mic button
  isRecording: boolean;
  startRecording: () => void;
  stopRecording: () => void;
}

const FloatingChatWindow: React.FC<FloatingChatWindowProps> = ({
  isVisible,
  onClose,
  messages,
  userInput,
  isProcessing,
  wsConnected,
  setUserInput,
  sendMessage,
  handleKeyDown,
  clearMessages,
  isRecording,
  startRecording,
  stopRecording,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const nodeRef = useRef<HTMLDivElement>(null); // Ref for Draggable - specify HTMLDivElement type
  
  // State for size (needed for ResizableBox)
  const [size, setSize] = useState({ width: 320, height: 480 }); 
  // 增加打字機效果索引狀態，追蹤對每條消息的處理進度
  const [typingStates, setTypingStates] = useState<Record<string, number>>({});
  // 當前處理階段狀態 (思考中 -> 組織語言 -> 生成語音)
  const [processingStage, setProcessingStage] = useState<number>(0);

  // 如果 isProcessing 變成 true，啟動階段轉變定時器
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | null = null;
    
    if (isProcessing) {
      setProcessingStage(0); // 重置為「正在思考」
      
      // 2秒後轉為「組織語言」
      timer = setTimeout(() => {
        setProcessingStage(1);
        
        // 再過2秒轉為「生成語音」
        timer = setTimeout(() => {
          setProcessingStage(2);
        }, 2000);
      }, 2000);
    } else {
      setProcessingStage(0); // 重置
    }
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isProcessing]);

  // 處理打字機效果
  useEffect(() => {
    // 尋找需要打字機效果的消息
    const typingMessages = messages.filter(msg => msg.isTyping && msg.fullContent);
    
    if (typingMessages.length === 0) return;
    
    // 為每條需要打字機效果的消息設置一個打字定時器
    const timers: ReturnType<typeof setTimeout>[] = [];
    
    typingMessages.forEach(message => {
      if (!message.id || !message.fullContent) return;
      
      const fullContent = message.fullContent;
      const currentIndex = typingStates[message.id] || 0;
      
      if (currentIndex < fullContent.length) {
        // 根據語音長度計算打字速度
        // 如果消息中有 speechDuration 屬性，使用它來計算打字速度
        // 否則回退到默認速度 (30ms 每字符)
        let typingInterval = 30; // 默認值
        
        if (message.speechDuration) {
          // 將語音時長(秒)分配給所有字符，稍微保留一些時間給最後幾個字符
          // 因為語音在一開始可能有較長的停頓
          const totalDuration = message.speechDuration * 1000; // 轉換為毫秒
          const charsLeft = fullContent.length - currentIndex;
          // 根據剩余字符數來計算每個字符的打字間隔
          // 這裡我們保留一個平滑系數：使內容在語音期間的約90%時間內完成
          typingInterval = Math.max(20, (totalDuration * 0.9) / fullContent.length);
        }
        
        const timer = setTimeout(() => {
          setTypingStates(prev => ({
            ...prev,
            [message.id]: currentIndex + 1
          }));
        }, typingInterval);
        
        timers.push(timer);
      }
    });
    
    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [messages, typingStates]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typingStates]); // 增加 typingStates 依賴，確保打字過程中也滾動

  // 獲取消息顯示內容的輔助函數
  const getMessageContent = useCallback((message: ChatMessage) => {
    if (message.isTyping && message.fullContent) {
      const contentIndex = typingStates[message.id] || 0;
      return message.fullContent.substring(0, contentIndex);
    }
    return message.content;
  }, [typingStates]);

  if (!isVisible) {
    return null;
  }

  // Handle send click and ensure input is cleared
  const handleSendClick = () => {
    if (userInput.trim() && !isProcessing && wsConnected) {
      sendMessage();
      // Delay clearing to allow sendMessage to potentially use the value
      setTimeout(() => setUserInput(''), 0); 
    }
  };

  // Combine processing states for disabling input
  const isDisabled = isProcessing || !wsConnected;

  return (
    <Draggable nodeRef={nodeRef as React.RefObject<HTMLElement>} handle=".drag-handle" bounds="parent"> 
      <div
        ref={nodeRef} // Attach ref for Draggable
        className={`fixed bottom-28 right-5 z-50 bg-white dark:bg-gray-800 rounded-lg shadow-xl flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700`}
        style={{ width: size.width, height: size.height }} // Control size via state
      >
        <ResizableBox 
          width={size.width}
          height={size.height}
          onResizeStop={(e, data) => {
            setSize({ width: data.size.width, height: data.size.height });
          }}
          minConstraints={[250, 300]} // Min width 250px, Min height 300px
          maxConstraints={[window.innerWidth * 0.8, window.innerHeight * 0.8]} // Max 80% of viewport
          className="flex flex-col flex-grow" // Ensure ResizableBox fills the container initially and allows content to grow
          handle={<span className="react-resizable-handle" />} // Default handle style
          // axis="both" // Already default
        >
          <div className="flex flex-col h-full"> {/* Inner container to hold layout */} 
            {/* Header with handle */}
            <div className="drag-handle flex justify-between items-center p-2 bg-gray-100 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 cursor-move flex-shrink-0">
              <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200">聊天視窗</h2>
              <button 
                onClick={onClose} 
                className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none rounded-full hover:bg-gray-200 dark:hover:bg-gray-600"
                aria-label="關閉聊天視窗"
              >
                {/* Close icon */}
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Chat Content Area */}
            <div className="flex-grow p-3 overflow-y-auto space-y-3">
              {messages.length === 0 && (
                <div className="text-center text-xs text-gray-400 dark:text-gray-500 pt-4">
                  開始對話吧！
                </div>
              )}
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] px-3 py-1.5 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200'}`}>
                    <p className="text-sm whitespace-pre-wrap inline">
                      {getMessageContent(msg)}
                      {msg.isTyping && typingStates[msg.id] < (msg.fullContent?.length || 0) && (
                        <span className="typing-cursor inline-block h-4 w-0.5 bg-current animate-pulse ml-0.5 align-text-bottom"></span>
                      )}
                    </p>
                  </div>
                </div>
              ))}
              {isProcessing && (
                <div className="flex flex-col space-y-2">
                  <div className="flex justify-start">
                    <div className="max-w-[80%] px-3 py-2.5 rounded-lg bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200">
                      {/* 思考泡泡框 */}
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gray-300 dark:bg-gray-500 rounded-full flex items-center justify-center">
                          <span role="img" aria-label="thinking" className="text-lg animate-pulse">💭</span>
                        </div>
                        <div>
                          <div className="typing-indicator flex space-x-1 items-center h-5">
                            <span className="block w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce-1"></span>
                            <span className="block w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce-2"></span>
                            <span className="block w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full animate-bounce-3"></span>
                          </div>
                          <div className="text-xs mt-1 text-gray-500 dark:text-gray-400">
                            {processingStage === 0 && "正在思考..."}
                            {processingStage === 1 && "正在組織語言..."}
                            {processingStage === 2 && "正在生成語音..."}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} /> {/* Anchor for scrolling */}
            </div>

            {/* Input Area */}
            <div className="p-2 border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 flex-shrink-0">
              <div className="flex items-center space-x-2">
                <input 
                  type="text" 
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={wsConnected ? "輸入訊息..." : "連接中..."}
                  disabled={isDisabled}
                  className="flex-grow px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-500 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-600 dark:text-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <button 
                  onMouseDown={startRecording}
                  onMouseUp={stopRecording}
                  onTouchStart={startRecording}
                  onTouchEnd={stopRecording}
                  onMouseLeave={isRecording ? stopRecording : undefined} // Stop if mouse leaves while recording
                  disabled={isDisabled}
                  className={`p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed ${isRecording ? 'bg-red-500 text-white hover:bg-red-600' : ''}`}
                  aria-label={isRecording ? '正在錄音，鬆開停止' : '按住開始語音輸入'}
                  title={isRecording ? '正在錄音，鬆開停止' : '按住開始語音輸入'}
                >
                  {/* Mic icon */}
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
                  </svg>
                </button>
                <button 
                  onClick={handleSendClick}
                  disabled={!userInput.trim() || isDisabled}
                  className="p-2 rounded-full text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="發送訊息"
                  title="發送訊息"
                >
                  {/* Send icon */}
                   <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                  </svg>
                </button>
                 <button
                  onClick={clearMessages}
                  disabled={messages.length === 0 || isDisabled}
                  className="p-2 rounded-full text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="清除對話紀錄"
                  aria-label="清除對話紀錄"
                >
                   {/* Trash icon */}
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12.502 0a48.097 48.097 0 0 1 3.478-.397m7.552 0a48.097 48.097 0 0 1-3.478-.397m3.478-.397L11.25 4.125m-.980 0a48.097 48.097 0 0 1-3.478-.397M5.7 5.79m12.502 0a48.108 48.108 0 0 1 3.478-.397m-12.502 0a48.097 48.097 0 0 0-3.478-.397" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </ResizableBox>
      </div>
    </Draggable>
  );
};

export default FloatingChatWindow;

// Add basic bounce animation for typing indicator
const styleSheet = document.styleSheets[0];
styleSheet.insertRule(`
@keyframes bounce-1 {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(-4px); opacity: 0.7; }
}
`, styleSheet.cssRules.length);
styleSheet.insertRule(`
@keyframes bounce-2 {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(-4px); opacity: 0.7; }
}
`, styleSheet.cssRules.length);
styleSheet.insertRule(`
@keyframes bounce-3 {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(-4px); opacity: 0.7; }
}
`, styleSheet.cssRules.length);
styleSheet.insertRule(`
.animate-bounce-1 { animation: bounce-1 1s infinite; animation-delay: 0s; }
`, styleSheet.cssRules.length);
styleSheet.insertRule(`
.animate-bounce-2 { animation: bounce-2 1s infinite; animation-delay: 0.1s; }
`, styleSheet.cssRules.length);
styleSheet.insertRule(`
.animate-bounce-3 { animation: bounce-3 1s infinite; animation-delay: 0.2s; }
`, styleSheet.cssRules.length); 