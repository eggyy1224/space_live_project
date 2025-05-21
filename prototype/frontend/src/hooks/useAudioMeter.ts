import { useEffect, useRef, useState } from 'react';
import AudioService from '../services/AudioService';
import { getBgmAnalyserNode } from '../components/BackgroundSoundSystem';

export function calculateRms(data: Uint8Array): number {
  let sum = 0;
  for (let i = 0; i < data.length; i++) {
    const v = data[i] / 255;
    sum += v * v;
  }
  return Math.sqrt(sum / data.length);
}

export default function useAudioMeter() {
  const [rms, setRms] = useState(0);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataRef = useRef<Uint8Array>(new Uint8Array(0));
  const rafRef = useRef<number>();

  useEffect(() => {
    const update = () => {
      const node =
        AudioService.getInstance().getAnalysisNode() || getBgmAnalyserNode();
      if (node && node !== analyserRef.current) {
        analyserRef.current = node;
        dataRef.current = new Uint8Array(node.frequencyBinCount);
      }
      if (analyserRef.current) {
        analyserRef.current.getByteFrequencyData(dataRef.current);
        const value = calculateRms(dataRef.current);
        setRms((prev) => prev + (value - prev) * 0.2);
      }
      rafRef.current = requestAnimationFrame(update);
    };
    update();
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return { rms, fft: dataRef.current };
}
