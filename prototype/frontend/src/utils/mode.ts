export type Mode = 'autostart' | 'autoplay' | null;

export interface ModeResult {
  mode: Mode;
  conflict: boolean;
}

export function getActiveMode(search: string): ModeResult {
  const params = new URLSearchParams(search);
  const modeParam = params.get('mode');
  const legacyAutostart = params.get('autostart') === 'true';
  const hasAutoplay = modeParam === 'autoplay';
  const hasAutostart = modeParam === 'autostart' || legacyAutostart;
  const conflict = hasAutoplay && hasAutostart && modeParam !== 'autoplay';
  const mode: Mode = hasAutoplay ? 'autoplay' : hasAutostart ? 'autostart' : null;
  return { mode, conflict };
}
