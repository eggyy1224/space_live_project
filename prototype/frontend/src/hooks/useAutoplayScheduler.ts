import { useEffect, useRef } from 'react';
import { useStore } from '../store';

export interface AutoplayOptions {
  startAt: Date;
  interval?: number; // seconds
  count?: number;
}

export function useAutoplayScheduler(options: AutoplayOptions | null): void {
  const {
    setAutoplayEnabled,
    setNextTrigger,
    setIntervalSeconds,
    resetAutoplay,
  } = useStore((state) => ({
    setAutoplayEnabled: state.setAutoplayEnabled,
    setNextTrigger: state.setNextTrigger,
    setIntervalSeconds: state.setIntervalSeconds,
    resetAutoplay: state.resetAutoplay,
  }));

  const timeoutRef = useRef<number>();
  const intervalRef = useRef<number>();

  useEffect(() => {
    if (!options) {
      resetAutoplay();
      return;
    }

    const { startAt, interval, count } = options;
    const delay = startAt.getTime() - Date.now();

    setAutoplayEnabled(true);
    setNextTrigger(startAt.getTime());
    if (interval) {
      setIntervalSeconds(interval);
    }

    const trigger = () => {
      fetch('/api/scripts/execute/random-yoga', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(count !== undefined ? { count } : {}),
      }).catch((err) => console.error('autoplay request failed', err));
    };

    timeoutRef.current = window.setTimeout(() => {
      trigger();
      if (interval) {
        intervalRef.current = window.setInterval(trigger, interval * 1000);
      } else {
        resetAutoplay();
      }
    }, Math.max(0, delay));

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      resetAutoplay();
    };
  }, [options, setAutoplayEnabled, setNextTrigger, setIntervalSeconds, resetAutoplay]);
}
