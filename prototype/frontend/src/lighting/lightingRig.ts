import { useStore } from '../store';

export function applyLightingPreset(name: string) {
  useStore.getState().setRuntime({ lightingPreset: name });
}
