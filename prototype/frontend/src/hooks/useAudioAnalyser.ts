import { useStore } from '../store';

export const useAudioAnalyser = () => {
  const volume = useStore((s) => s.audioAverageVolume);
  const pitch = useStore((s) => s.audioPitch);
  return { volume, pitch };
};
