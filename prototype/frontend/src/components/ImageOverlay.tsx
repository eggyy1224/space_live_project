import React, { useEffect, useState } from 'react';
import WebSocketService from '../services/WebSocketService';

const DISPLAY_TIME = 10000; // ms
// 後端 API 基礎 URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

const ImageOverlay: React.FC = () => {
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    const service = WebSocketService.getInstance();

    const handler = (data: any) => {
      if (data.type === 'generated-image' && data.url) {
        // 將相對路徑轉換為完整的 URL
        const fullImageUrl = data.url.startsWith('http') 
          ? data.url 
          : `${API_BASE_URL}${data.url}`;
        setImage(fullImageUrl);
        setTimeout(() => setImage(null), DISPLAY_TIME);
      }
    };

    service.registerHandler('generated-image', handler);
    return () => {
      service.removeHandler('generated-image', handler);
    };
  }, []);

  if (!image) return null;

  return (
    <>
      <style>
        {`
          @keyframes slideInFromRight {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
          .image-overlay {
            animation: slideInFromRight 0.5s ease-out;
          }
        `}
      </style>
      <div
        className="image-overlay"
        style={{
          position: 'fixed',
          top: '50%',
          right: '50px',
          transform: 'translateY(-50%)',
          width: '350px',
          height: '280px',
          borderRadius: '15px',
          overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          border: '2px solid rgba(255, 255, 255, 0.3)',
          backdropFilter: 'blur(10px)',
          zIndex: 1000,
        }}
      >
        <img 
          src={image} 
          alt="Generated" 
          style={{ 
            width: '100%', 
            height: '100%', 
            objectFit: 'cover',
            borderRadius: '13px'
          }}
          onError={(e) => {
            console.error('圖片載入失敗:', image);
            console.error('錯誤詳情:', e);
          }}
          onLoad={() => {
            console.log('圖片載入成功:', image);
          }}
        />
        {/* 添加一個小標籤顯示這是 AI 生成的圖片 */}
        <div
          style={{
            position: 'absolute',
            bottom: '8px',
            left: '8px',
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: 'bold',
          }}
        >
          AI 生成
        </div>
      </div>
    </>
  );
};

export default ImageOverlay;
