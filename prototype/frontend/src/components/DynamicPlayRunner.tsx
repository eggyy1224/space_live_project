import React, { useEffect, useRef, useState } from 'react';
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
 * DynamicPlayRunner schedules and plays media based on a template and package.
 * Media playback is stubbed using basic HTML audio/video elements.
 */
const DynamicPlayRunner: React.FC<DynamicPlayRunnerProps> = ({ template, playPackage }) => {
  const addEvent = useStore((s) => (s as any).addEvent);
  const [bgm, setBgm] = useState<string | null>(null);
  const [video, setVideo] = useState<string | null>(null);
  const [sfx, setSfx] = useState<{ id: number; src: string }[]>([]);
  const idRef = useRef(0);
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
          setBgm(src);
        } else if (slot.slot_name.startsWith('video')) {
          setVideo(src);
        } else if (slot.slot_name.startsWith('sfx')) {
          const id = idRef.current++;
          setSfx((arr) => [...arr, { id, src }]);
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
  }, [template, playPackage, addEvent]);

  return (
    <div>
      {bgm && <audio src={bgm} autoPlay loop />}
      {video && <video src={video} autoPlay />}
      {sfx.map((s) => (
        <audio
          key={s.id}
          src={s.src}
          autoPlay
          onEnded={() => setSfx((arr) => arr.filter((i) => i.id !== s.id))}
        />
      ))}
    </div>
  );
};

export default DynamicPlayRunner;
