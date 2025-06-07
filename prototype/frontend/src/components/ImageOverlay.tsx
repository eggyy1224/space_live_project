import React, { useEffect, useState } from 'react';
import WebSocketService from '../services/WebSocketService';

const DISPLAY_TIME = 10000; // ms

const ImageOverlay: React.FC = () => {
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    const service = WebSocketService.getInstance();

    const handler = (data: any) => {
      if (data.type === 'generated-image' && data.url) {
        setImage(data.url);
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
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(0,0,0,0.6)',
        zIndex: 1000,
      }}
    >
      <img src={image} alt="Generated" style={{ maxWidth: '90%', maxHeight: '90%' }} />
    </div>
  );
};

export default ImageOverlay;
