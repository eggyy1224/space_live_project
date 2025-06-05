import React, { useEffect, useState, useRef } from 'react';
import { directorBus } from '../director/bus';
import { DirectorState } from '../../../shared/director/types';

interface LogEntry {
  time: number;
  payload: Partial<DirectorState>;
  color: string;
  visualType: 'shape' | 'bar' | 'pixel';
  shape?: 'circle' | 'triangle' | 'square' | 'diamond';
  size: number;
  id: string;
  age: number; // 生命週期
  velocity?: { x: number; y: number }; // 移動速度
  rotation?: number; // 旋轉角度
}

const colors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FED766', '#2AB7CA',
  '#F0F2A6', '#FFD166', '#06D6A0', '#118AB2', '#EF476F',
  '#C2AFF0', '#73D2DE', '#92E6E6', '#D9B4E8', '#B4E8D9'
];

const getRandomColor = () => colors[Math.floor(Math.random() * colors.length)];

// 分析日誌內容並決定視覺化類型
const analyzeLogEntry = (payload: Partial<DirectorState>): { visualType: 'shape' | 'bar' | 'pixel', shape?: 'circle' | 'triangle' | 'square' | 'diamond', size: number } => {
  const content = JSON.stringify(payload);
  const contentLength = content.length;
  
  if (content.includes('video') || content.includes('scene')) {
    return { visualType: 'shape', shape: 'square', size: Math.min(contentLength / 5 + 8, 32) };
  } else if (content.includes('audio') || content.includes('sound')) {
    return { visualType: 'bar', size: Math.min(contentLength / 3 + 10, 40) };
  } else if (content.includes('state') || content.includes('update')) {
    return { visualType: 'shape', shape: 'circle', size: Math.min(contentLength / 4 + 10, 28) };
  } else if (content.includes('error') || content.includes('warning')) {
    return { visualType: 'shape', shape: 'triangle', size: Math.min(contentLength / 4 + 12, 30) };
  } else if (content.includes('data') || content.includes('config')) {
    return { visualType: 'shape', shape: 'diamond', size: Math.min(contentLength / 4 + 8, 25) };
  } else if (contentLength > 50) {
    return { visualType: 'pixel', size: Math.min(contentLength / 8 + 5, 20) };
  } else {
    return { visualType: 'bar', size: Math.min(contentLength / 2 + 8, 35) };
  }
};

// 動態幾何形狀渲染器
const DynamicShapeRenderer: React.FC<{ 
  shape: string; 
  size: number; 
  color: string; 
  time: string; 
  age: number; 
  id: string;
  rotation: number;
  isVisible: boolean; // 新增可見性參數
}> = ({ shape, size, color, time, age, id, rotation, isVisible }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [localRotation, setLocalRotation] = useState(rotation);
  
  useEffect(() => {
    if (!isVisible) return; // 不可見時不執行動畫
    
    const interval = setInterval(() => {
      setLocalRotation(prev => prev + (shape === 'diamond' ? 2 : 1));
    }, 100);
    return () => clearInterval(interval);
  }, [shape, isVisible]);

  const baseStyle = {
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor: color,
    display: 'inline-block',
    margin: '2px',
    position: 'relative' as const,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    transform: `
      scale(${isHovered ? 1.3 : 1}) 
      rotate(${isVisible ? localRotation : rotation}deg)
      translateY(${isVisible ? Math.sin(Date.now() / 1000 + age) * 3 : 0}px)
    `,
    opacity: Math.max(0.3, 1 - age / 100),
    filter: `
      brightness(${isHovered ? 1.3 : 1}) 
      blur(${age > 80 ? (age - 80) / 5 : 0}px)
      hue-rotate(${isVisible ? age * 2 : 0}deg)
    `,
    boxShadow: isHovered ? `0 0 20px ${color}` : `0 0 5px ${color}40`,
    animation: isVisible ? `
      entrySlide 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275),
      float ${2 + Math.random()}s ease-in-out infinite
    ` : 'none',
    zIndex: isHovered ? 100 : 1,
  };

  const getShapeSpecificStyle = () => {
    switch (shape) {
      case 'circle':
        return { borderRadius: '50%' };
      case 'triangle':
        return {
          backgroundColor: 'transparent',
          width: 0,
          height: 0,
          borderLeft: `${size/2}px solid transparent`,
          borderRight: `${size/2}px solid transparent`,
          borderBottom: `${size}px solid ${color}`,
        };
      case 'diamond':
        return { 
          borderRadius: '10%',
        };
      default: // square
        return { borderRadius: '15%' };
    }
  };

  return (
    <div 
      className="inline-block relative group cursor-pointer transform-gpu"
      title={`${time} - Age: ${age}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ animationDelay: `${Math.random() * 0.5}s` }}
    >
      <div style={{...baseStyle, ...getShapeSpecificStyle()}} />
      {isHovered && isVisible && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          {/* 懸停時的粒子效果 - 只在可見時顯示 */}
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 rounded-full"
              style={{
                backgroundColor: color,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animation: `sparkle 1s ease-out infinite`,
                animationDelay: `${i * 0.1}s`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// 動態進度條渲染器
const DynamicBarRenderer: React.FC<{ 
  size: number; 
  color: string; 
  time: string; 
  age: number; 
  id: string;
  isVisible: boolean; // 新增可見性參數
}> = ({ size, color, time, age, id, isVisible }) => {
  const [currentHeight, setCurrentHeight] = useState(0);
  const targetHeight = size;
  
  useEffect(() => {
    if (!isVisible) return; // 不可見時不執行動畫
    
    const timeout = setTimeout(() => {
      setCurrentHeight(targetHeight);
    }, Math.random() * 500);
    return () => clearTimeout(timeout);
  }, [targetHeight, isVisible]);

  const waveOffset = isVisible ? Math.sin(Date.now() / 500 + age) * 5 : 0;
  const opacity = Math.max(0.3, 1 - age / 100);
  
  return (
    <div 
      className="inline-block relative group cursor-pointer mx-1"
      title={`${time} - Age: ${age}`}
      style={{ 
        verticalAlign: 'bottom',
        animation: isVisible ? 'entrySlide 0.6s ease-out' : 'none',
      }}
    >
      <div 
        className="transition-all duration-1000 ease-out relative"
        style={{
          width: '6px',
          height: `${currentHeight}px`,
          backgroundColor: color,
          transform: `
            translateY(${waveOffset}px) 
            scaleX(${isVisible ? 1 + Math.sin(Date.now() / 300 + age) * 0.3 : 1})
          `,
          opacity: opacity,
          filter: `
            brightness(${isVisible ? 1 + Math.sin(Date.now() / 800 + age) * 0.3 : 1}) 
            hue-rotate(${isVisible ? age * 3 : 0}deg)
          `,
          boxShadow: `0 0 10px ${color}60`,
          borderRadius: '3px',
          background: `linear-gradient(to top, ${color}, ${color}80, ${color}40)`,
        }}
      />
      {/* 頂部發光效果 - 只在可見時顯示 */}
      {isVisible && (
        <div
          className="absolute top-0 left-0 w-full h-2"
          style={{
            background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
            animation: 'glow 2s ease-in-out infinite',
          }}
        />
      )}
    </div>
  );
};

// 動態像素渲染器
const DynamicPixelRenderer: React.FC<{ 
  size: number; 
  color: string; 
  time: string; 
  content: string; 
  age: number; 
  id: string;
  isVisible: boolean; // 新增可見性參數
}> = ({ size, color, time, content, age, id, isVisible }) => {
  const pixelCount = Math.min(content.length, 50);
  const gridSize = Math.ceil(Math.sqrt(pixelCount));
  const [animatedPixels, setAnimatedPixels] = useState<boolean[]>([]);
  
  useEffect(() => {
    if (!isVisible) return; // 不可見時不執行動畫
    
    const interval = setInterval(() => {
      setAnimatedPixels(
        Array.from({ length: pixelCount }, () => 
          Math.random() < 0.3
        )
      );
    }, 200);
    return () => clearInterval(interval);
  }, [pixelCount, isVisible]);

  const opacity = Math.max(0.3, 1 - age / 100);
  
  return (
    <div 
      className="inline-block relative group cursor-pointer m-1"
      title={`${time} - Age: ${age}`}
      style={{
        animation: isVisible ? 'entrySlide 0.7s ease-out' : 'none',
        transform: `rotate(${isVisible ? Math.sin(Date.now() / 2000 + age) * 5 : 0}deg)`,
        opacity: opacity,
      }}
    >
      <div 
        className="grid gap-1 transition-transform duration-300"
        style={{ 
          gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
          width: `${size}px`,
          height: `${size}px`,
          transform: `scale(${isVisible ? 1 + Math.sin(Date.now() / 1000 + age) * 0.1 : 1})`,
        }}
      >
        {Array.from({ length: pixelCount }).map((_, i) => (
          <div
            key={i}
            className="w-1 h-1 transition-all duration-300 rounded-sm"
            style={{
              backgroundColor: animatedPixels[i] ? color : 'rgba(255,255,255,0.2)',
              transform: `scale(${animatedPixels[i] ? 1.2 : 0.8})`,
              animation: isVisible ? `pixelDance ${1 + Math.random()}s ease-in-out infinite` : 'none',
              animationDelay: `${i * 0.05}s`,
              filter: `hue-rotate(${isVisible ? age * 2 + i * 10 : 0}deg)`,
              boxShadow: animatedPixels[i] ? `0 0 3px ${color}` : 'none',
            }}
          />
        ))}
      </div>
    </div>
  );
};

const panelStyle = 'fixed bottom-2 left-2 bg-black/85 backdrop-blur-lg text-white p-4 text-xs rounded-xl z-50 max-h-72 overflow-y-auto border border-gray-500 shadow-2xl';
const hiddenPanelStyle = 'hidden';

const DirectorLogPanel: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [panelVisible, setPanelVisible] = useState(import.meta.env.VITE_DIRECTOR === 'true');
  const ageTimerRef = useRef<NodeJS.Timeout | undefined>(undefined);

  // 更新年齡的計時器 - 只在面板可見時運行
  useEffect(() => {
    if (!panelVisible) {
      // 面板不可見時清除計時器
      if (ageTimerRef.current) {
        clearInterval(ageTimerRef.current);
        ageTimerRef.current = undefined;
      }
      return;
    }

    // 面板可見時啟動計時器
    ageTimerRef.current = setInterval(() => {
      setLogs(prevLogs => 
        prevLogs.map(log => ({
          ...log,
          age: log.age + 1
        })).filter(log => log.age < 150) // 移除太老的日誌
      );
    }, 100);

    return () => {
      if (ageTimerRef.current) {
        clearInterval(ageTimerRef.current);
      }
    };
  }, [panelVisible]); // 依賴 panelVisible

  useEffect(() => {
    const handler = (payload: Partial<DirectorState>) => {
      const analysis = analyzeLogEntry(payload);
      const newLog: LogEntry = {
        time: Date.now(),
        payload,
        color: getRandomColor(),
        id: Math.random().toString(36).substring(2, 11),
        age: 0,
        rotation: Math.random() * 360,
        velocity: {
          x: (Math.random() - 0.5) * 2,
          y: (Math.random() - 0.5) * 2,
        },
        ...analysis
      };
      
      setLogs(l => [...l.slice(-49), newLog]);
    };
    
    directorBus.on('stateUpdate', handler);
    return () => directorBus.off('stateUpdate', handler);
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      if (event.key.toLowerCase() === 'l') {
        event.preventDefault();
        setPanelVisible(v => !v);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const renderLogEntry = (log: LogEntry, idx: number) => {
    const timeString = new Date(log.time).toLocaleTimeString();
    const content = JSON.stringify(log.payload);
    
    switch (log.visualType) {
      case 'shape':
        return (
          <DynamicShapeRenderer 
            key={log.id}
            shape={log.shape!}
            size={log.size}
            color={log.color}
            time={timeString}
            age={log.age}
            id={log.id}
            rotation={log.rotation || 0}
            isVisible={panelVisible}
          />
        );
      case 'bar':
        return (
          <DynamicBarRenderer 
            key={log.id}
            size={log.size}
            color={log.color}
            time={timeString}
            age={log.age}
            id={log.id}
            isVisible={panelVisible}
          />
        );
      case 'pixel':
        return (
          <DynamicPixelRenderer 
            key={log.id}
            size={log.size}
            color={log.color}
            time={timeString}
            content={content}
            age={log.age}
            id={log.id}
            isVisible={panelVisible}
          />
        );
      default:
        return null;
    }
  };

  return (
    <>
      <style>{`
        @keyframes entrySlide {
          0% { 
            transform: translateX(300px) scale(0) rotate(180deg); 
            opacity: 0; 
          }
          60% { 
            transform: translateX(-10px) scale(1.1) rotate(-10deg); 
            opacity: 0.8; 
          }
          100% { 
            transform: translateX(0) scale(1) rotate(0deg); 
            opacity: 1; 
          }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-8px) rotate(5deg); }
        }
        
        @keyframes sparkle {
          0% { transform: scale(0) rotate(0deg); opacity: 1; }
          50% { transform: scale(1) rotate(180deg); opacity: 0.8; }
          100% { transform: scale(0) rotate(360deg); opacity: 0; }
        }
        
        @keyframes glow {
          0%, 100% { opacity: 0.5; transform: scaleY(1); }
          50% { opacity: 1; transform: scaleY(1.5); }
        }
        
        @keyframes pixelDance {
          0%, 100% { transform: scale(1) rotate(0deg); }
          25% { transform: scale(1.3) rotate(90deg); }
          50% { transform: scale(0.8) rotate(180deg); }
          75% { transform: scale(1.1) rotate(270deg); }
        }
        
        .dynamic-panel {
          backdrop-filter: blur(15px);
          box-shadow: 
            0 0 30px rgba(0, 150, 255, 0.3),
            inset 0 0 20px rgba(255, 255, 255, 0.05);
        }
      `}</style>
      
      <div className={`${panelStyle} dynamic-panel ${!panelVisible ? hiddenPanelStyle : ''}`}>
        <div className="text-gray-300 mb-3 text-xs flex items-center justify-between">
          <span className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            Director Log Visual (Press 'L' to toggle)
          </span>
          <div className="text-gray-500">
            {logs.length} active logs
          </div>
        </div>
        
        <div className="flex flex-wrap items-end gap-1 min-h-[50px] p-2 rounded-lg bg-black/20">
          {logs.map((log, idx) => renderLogEntry(log, idx))}
        </div>
        
        {logs.length === 0 && (
          <div className="text-center text-gray-500 py-4">
            <div className="animate-pulse">Waiting for director events...</div>
          </div>
        )}
      </div>
    </>
  );
};

export default DirectorLogPanel;
