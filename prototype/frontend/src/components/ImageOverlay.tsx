import React, { useEffect, useState } from 'react';
import WebSocketService from '../services/WebSocketService';

const DISPLAY_TIME = 10000; // ms
// 後端 API 基礎 URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

interface ImageData {
  url: string;
  caption?: string;
  display_config?: {
    position?: { [key: string]: string };
    size?: { [key: string]: string };
  };
}

const ImageOverlay: React.FC = () => {
  const [imageData, setImageData] = useState<ImageData | null>(null);

  useEffect(() => {
    const service = WebSocketService.getInstance();

    const handler = (data: any) => {
      if (data.type === 'generated-image' && data.url) {
        // 將相對路徑轉換為完整的 URL
        const fullImageUrl = data.url.startsWith('http') 
          ? data.url 
          : `${API_BASE_URL}${data.url}`;
        
        setImageData({
          url: fullImageUrl,
          caption: data.caption,
          display_config: data.display_config
        });
        
        setTimeout(() => setImageData(null), DISPLAY_TIME);
      }
    };

    service.registerHandler('generated-image', handler);
    return () => {
      service.removeHandler('generated-image', handler);
    };
  }, []);

  if (!imageData) return null;

  // 獲取樣式配置
  const getStyles = () => {
    const defaultPosition = { top: "50%", right: "50px", transform: "translateY(-50%)" };
    const defaultSize = { width: "350px", height: "280px" };
    
    const position = imageData.display_config?.position || defaultPosition;
    const size = imageData.display_config?.size || defaultSize;
    
    return {
      ...position,
      ...size,
      position: 'fixed' as const,
      borderRadius: '15px',
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      border: '2px solid rgba(255, 255, 255, 0.3)',
      backdropFilter: 'blur(10px)',
      zIndex: 1000,
    };
  };

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
          @keyframes slideInFromLeft {
            from {
              transform: translateX(-100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: scale(0.8);
            }
            to {
              opacity: 1;
              transform: scale(1);
            }
          }
          .image-overlay-right {
            animation: slideInFromRight 0.5s ease-out;
          }
          .image-overlay-left {
            animation: slideInFromLeft 0.5s ease-out;
          }
          .image-overlay-center {
            animation: fadeIn 0.5s ease-out;
          }
        `}
      </style>
      <div
        className={`image-overlay-${
          imageData.display_config?.position?.right ? 'right' : 
          imageData.display_config?.position?.left ? 'left' : 'center'
        }`}
        style={getStyles()}
      >
        <img 
          src={imageData.url} 
          alt="Generated" 
          style={{ 
            width: '100%', 
            height: '100%', 
            objectFit: 'cover',
            borderRadius: '13px'
          }}
          onError={(e) => {
            console.error('圖片載入失敗:', imageData.url);
            console.error('錯誤詳情:', e);
          }}
          onLoad={() => {
            console.log('圖片載入成功:', imageData.url);
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
        {/* 如果有 caption，顯示在右下角 */}
        {imageData.caption && (
          <div
            style={{
              position: 'absolute',
              bottom: '8px',
              right: '8px',
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
              color: 'white',
              padding: '4px 8px',
              borderRadius: '8px',
              fontSize: '10px',
              maxWidth: '60%',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={imageData.caption}
          >
            💬
          </div>
        )}
      </div>
    </>
  );
};

export default ImageOverlay;
