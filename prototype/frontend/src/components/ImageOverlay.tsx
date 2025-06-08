import React, { useEffect, useState, useRef } from 'react';
import WebSocketService from '../services/WebSocketService';

const DEFAULT_DISPLAY_TIME = 10000; // ms
// 後端 API 基礎 URL
const API_BASE_URL = `http://${window.location.hostname}:8000`;

interface ImageData {
  id: string;
  url: string;
  caption?: string;
  display_config?: {
    position?: { [key: string]: string };
    size?: { [key: string]: string };
  };
}

const ImageOverlay: React.FC = () => {
  const [images, setImages] = useState<ImageData[]>([]);
  const timers = useRef<Record<string, NodeJS.Timeout>>({});

  useEffect(() => {
    const service = WebSocketService.getInstance();

    const handler = (data: any) => {
      if (data.type === 'generated-image' && data.url) {
        // 將相對路徑轉換為完整的 URL
        const fullImageUrl = data.url.startsWith('http') 
          ? data.url 
          : `${API_BASE_URL}${data.url}`;
        
        const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
        const duration = typeof data.duration === 'number' ? data.duration * 1000 : DEFAULT_DISPLAY_TIME;

        setImages((prev) => {
          // 移除同 URL 的現有圖片，以支援覆蓋
          const filtered = prev.filter((img) => img.url !== fullImageUrl);
          return [...filtered, { id, url: fullImageUrl, caption: data.caption, display_config: data.display_config }];
        });

        if (timers.current[id]) clearTimeout(timers.current[id]);
        timers.current[id] = setTimeout(() => {
          setImages((prev) => prev.filter((img) => img.id !== id));
          delete timers.current[id];
        }, duration);
      }
    };

    service.registerHandler('generated-image', handler);
    return () => {
      service.removeHandler('generated-image', handler);
    };
  }, []);

  if (images.length === 0) return null;

  // 獲取樣式配置
  const getStyles = (img: ImageData) => {
    const defaultPosition = { top: "50%", right: "50px", transform: "translateY(-50%)" };
    const defaultSize = { width: "350px", height: "280px" };
    
    const position = img.display_config?.position || defaultPosition;
    const size = img.display_config?.size || defaultSize;
    
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
      {images.map((img) => (
        <div
          key={img.id}
          className={`image-overlay-${
            img.display_config?.position?.right ? 'right' :
            img.display_config?.position?.left ? 'left' : 'center'
          }`}
          style={getStyles(img)}
        >
          <img
            src={img.url}
          alt="Generated"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            borderRadius: '13px'
          }}
          onError={(e) => {
            console.error('圖片載入失敗:', img.url);
            console.error('錯誤詳情:', e);
          }}
          onLoad={() => {
            console.log('圖片載入成功:', img.url);
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
        {img.caption && (
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
            title={img.caption}
          >
            💬
          </div>
        )}
        </div>
      ))}
    </>
  );
};

export default ImageOverlay;
