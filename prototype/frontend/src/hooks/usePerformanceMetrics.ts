import { useEffect, useRef } from 'react';
import { useStore } from '../store';

export function usePerformanceMetrics() {
  const setRuntime = useStore((s) => s.setRuntime);
  const lastFrame = useRef(performance.now());
  const frames = useRef(0);
  const lastFpsUpdate = useRef(performance.now());

  useEffect(() => {
    const loop = () => {
      const now = performance.now();
      frames.current += 1;
      const delta = now - lastFrame.current;
      lastFrame.current = now;
      const cpu = delta;
      if (now - lastFpsUpdate.current >= 1000) {
        setRuntime({ fps: frames.current, cpu });
        frames.current = 0;
        lastFpsUpdate.current = now;
      }
      requestAnimationFrame(loop);
    };
    const id = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(id);
  }, [setRuntime]);
}
