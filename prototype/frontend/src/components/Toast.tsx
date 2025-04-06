import React, { useEffect, useState } from 'react';
import { useStore } from '../store';
import { Toast as ToastType } from '../store/slices/appSlice';

interface ToastProps {
  message: string;
  type: 'error' | 'success' | 'info';
  duration?: number;
  onClose?: () => void;
}

const Toast: React.FC<ToastProps> = ({ 
  message, 
  type, 
  duration = 3000, 
  onClose 
}) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      if (onClose) onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  // 根據類型選擇不同顏色
  const getBackgroundColor = () => {
    switch (type) {
      case 'error':
        return 'rgba(220, 53, 69, 0.9)'; // 紅色
      case 'success':
        return 'rgba(40, 167, 69, 0.9)'; // 綠色
      case 'info':
      default:
        return 'rgba(0, 123, 255, 0.9)'; // 藍色
    }
  };

  // 根據類型選擇不同圖標
  const getIcon = () => {
    switch (type) {
      case 'error':
        return '⚠️';
      case 'success':
        return '✅';
      case 'info':
      default:
        return 'ℹ️';
    }
  };

  if (!visible) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        backgroundColor: getBackgroundColor(),
        color: 'white',
        padding: '12px 20px',
        borderRadius: '6px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
        zIndex: 1000,
        maxWidth: '400px',
        display: 'flex',
        alignItems: 'center',
        animation: 'slideIn 0.3s ease-out'
      }}
    >
      <span style={{ marginRight: '10px', fontSize: '1.2em' }}>
        {getIcon()}
      </span>
      <div style={{ flex: 1 }}>
        {message}
      </div>
      <button 
        onClick={() => {
          setVisible(false);
          if (onClose) onClose();
        }}
        style={{
          background: 'transparent',
          border: 'none',
          color: 'white',
          fontSize: '1.2em',
          cursor: 'pointer',
          marginLeft: '10px',
          padding: '0 5px'
        }}
      >
        ×
      </button>
    </div>
  );
};

// 用於顯示多個Toast的容器組件
export const ToastContainer: React.FC = () => {
  // 從全局狀態中獲取通知列表
  const toasts = useStore((state) => state.toasts || []);
  const removeToast = useStore((state) => state.removeToast);

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000 }}>
      {toasts.map((toast: ToastType) => (
        <div key={toast.id} style={{ marginBottom: '10px' }}>
          <Toast
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
    </div>
  );
};

export default Toast; 