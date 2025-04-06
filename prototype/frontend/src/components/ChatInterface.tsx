import React, { useState } from 'react';

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  userInput: string;
  isProcessing: boolean;
  wsConnected: boolean;
  setUserInput: (input: string) => void;
  sendMessage: () => void;
  startRecording: () => void;
  stopRecording: () => void;
  isRecording: boolean;
  activeTab: 'control' | 'chat';
  switchTab: (tab: 'control' | 'chat') => void;
  handleKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  clearMessages: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  userInput,
  isProcessing,
  wsConnected,
  setUserInput,
  sendMessage,
  startRecording,
  stopRecording,
  isRecording,
  activeTab,
  switchTab,
  handleKeyDown,
  clearMessages
}) => {
  // 處理發送消息並清空輸入
  const handleSendClick = () => {
    if (userInput.trim() && !isProcessing) {
      sendMessage();
      // 在此重複調用setUserInput以確保輸入框被清空
      setTimeout(() => setUserInput(''), 50);
    }
  };

  return (
    <div className="controls-panel">
      <div className="tab-buttons">
        <button 
          className="tab-button"
          onClick={() => switchTab('control')}
        >
          控制面板
        </button>
        <button 
          className="tab-button active"
        >
          聊天
        </button>
      </div>
      
      <div className="chat-tab active">
        <div className="chat-container">
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-chat-message">
                發送訊息開始對話...
              </div>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`chat-message ${msg.role}`}>
                <div className="message-bubble">
                  {msg.content}
                </div>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
              </div>
            ))}
            {isProcessing && (
              <div className="chat-message bot">
                <div className="message-bubble processing">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div className="message-avatar">🤖</div>
              </div>
            )}
          </div>
          
          <div className="chat-input">
            <input 
              type="text" 
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="輸入訊息..."
              disabled={isProcessing}
            />
            <button 
              onClick={handleSendClick}
              disabled={!userInput.trim() || isProcessing}
              className="send-button"
            >
              發送
            </button>
            <button 
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onTouchStart={startRecording}
              onTouchEnd={stopRecording}
              onMouseLeave={isRecording ? stopRecording : undefined}
              disabled={isProcessing}
              className={`mic-button ${isRecording ? 'recording' : ''}`}
              aria-label={isRecording ? '正在錄音，鬆開停止' : '按住開始語音輸入'}
              title={isRecording ? '正在錄音，鬆開停止' : '按住開始語音輸入'}
            >
              {isRecording ? '🔴' : '🎤'}
            </button>
            <button
              onClick={clearMessages}
              disabled={messages.length === 0 || isProcessing}
              className="clear-button"
              title="清除對話紀錄"
              aria-label="清除對話紀錄"
            >
              🗑️
            </button>
          </div>
          
          <div className={`ws-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '已連接' : '未連接'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 