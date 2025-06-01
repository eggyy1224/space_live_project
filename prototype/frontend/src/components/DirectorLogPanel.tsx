import React, { useEffect, useState } from 'react';
import { directorBus } from '../director/bus';
import { DirectorState } from '../../../shared/director/types';

interface LogEntry {
  time: number;
  payload: Partial<DirectorState>;
}

const panelStyle = 'fixed bottom-2 left-2 bg-black/70 text-white p-2 text-xs rounded z-50 max-h-48 overflow-y-auto';

const DirectorLogPanel: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    const handler = (payload: Partial<DirectorState>) => {
      setLogs((l) => [...l.slice(-49), { time: Date.now(), payload }]);
    };
    directorBus.on('stateUpdate', handler);
    return () => directorBus.off('stateUpdate', handler);
  }, []);

  if (import.meta.env.VITE_DIRECTOR !== 'true') return null;

  return (
    <div className={panelStyle}>
      {logs.map((log, idx) => (
        <div key={idx} className="whitespace-pre-wrap">
          {new Date(log.time).toLocaleTimeString()} {JSON.stringify(log.payload)}
        </div>
      ))}
    </div>
  );
};

export default DirectorLogPanel;
