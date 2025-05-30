import React, { useEffect, useRef } from 'react';
import { DynamicTemplate, PlayPackage } from '../types/dynamic';
import { useStore } from '../store';

/**
 * Props for DynamicPlayRunner component.
 */
export interface DynamicPlayRunnerProps {
  template: DynamicTemplate;
  playPackage: PlayPackage;
}

/**
 * DynamicPlayRunner schedules runtime state updates based on a template and
 * package. It drives existing background systems via the Zustand store.
 */
const DynamicPlayRunner: React.FC<DynamicPlayRunnerProps> = ({ template, playPackage }) => {
  const addEvent = useStore((s) => s.addEvent);
  const setRuntime = useStore((s) => s.setRuntime);
  const setVideoScreen = useStore((s) => s.setVideoScreen);
  const triggerEffect = useStore((s) => s.triggerEffect);
  const timers = useRef<number[]>([]);

  useEffect(() => {
    const durationMs = playPackage.total_duration * 1000;
    template.slots.forEach((slot) => {
      const startMs = (slot.percentage / 100) * durationMs;
      const t = window.setTimeout(() => {
        const src = playPackage.contents[slot.slot_name];
        addEvent({ slotName: slot.slot_name, startedAtMs: performance.now() });
        if (!src) return;

        if (slot.slot_name === 'bgm') {
          setRuntime({ bgm: src, bgmPlaying: true });
        } else if (slot.slot_name.startsWith('video')) {
          setVideoScreen('screen1', { currentVideo: src, visible: true });
        } else if (slot.slot_name.startsWith('sfx')) {
          setRuntime({ selectedEffect: null, sfxActive: false });
          window.setTimeout(() => {
            setRuntime({ selectedEffect: src, sfxActive: true });
            triggerEffect();
          }, 10);
        } else {
          console.log('Unhandled slot', slot.slot_name);
        }
      }, startMs);
      timers.current.push(t);
    });
    return () => {
      timers.current.forEach((t) => clearTimeout(t));
      timers.current = [];
    };
  }, [template, playPackage, addEvent, setRuntime, setVideoScreen, triggerEffect]);

  return null;
};

export default DynamicPlayRunner;
