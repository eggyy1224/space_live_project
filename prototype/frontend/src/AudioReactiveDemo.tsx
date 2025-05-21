import React, { useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import AudioReactiveBg from './components/AudioReactiveBg';

const Demo = () => {
  useEffect(() => {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = 440;
    osc.connect(ctx.destination);
    osc.start();
    return () => {
      osc.stop();
      ctx.close();
    };
  }, []);
  return <AudioReactiveBg />;
};

const root = createRoot(document.getElementById('root')!);
root.render(<Demo />);
