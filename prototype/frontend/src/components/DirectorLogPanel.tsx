import React, { useEffect, useState } from 'react';
import { directorBus } from '../director/bus';
import { DirectorState } from '../../../shared/director/types';

interface LogEntry {
  time: number;
  payload: Partial<DirectorState>;
  color: string;
}

const colors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FED766', '#2AB7CA', 
  '#F0F2A6', '#FFD166', '#06D6A0', '#118AB2', '#EF476F',
  '#C2AFF0', '#73D2DE', '#92E6E6', '#D9B4E8', '#B4E8D9'
];

const getRandomColor = () => colors[Math.floor(Math.random() * colors.length)];

const panelStyle = 'fixed bottom-2 left-2 bg-black/70 text-white p-2 text-xs rounded z-50 max-h-48 overflow-y-auto';
const hiddenPanelStyle = 'hidden';

const DirectorLogPanel: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [panelVisible, setPanelVisible] = useState(import.meta.env.VITE_DIRECTOR === 'true');

  useEffect(() => {
    const handler = (payload: Partial<DirectorState>) => {
      setLogs((l) => [...l.slice(-49), { time: Date.now(), payload, color: getRandomColor() }]);
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

  if (import.meta.env.VITE_DIRECTOR !== 'true') return null;

  return (
    <div className={`${panelStyle} ${!panelVisible ? hiddenPanelStyle : ''}`}>
      {logs.map((log, idx) => (
        <div key={idx} className="whitespace-pre-wrap" style={{ color: log.color }}>
          {new Date(log.time).toLocaleTimeString()} {JSON.stringify(log.payload)}
        </div>
      ))}
    </div>
  );
};

export default DirectorLogPanel;
