import { getActiveMode } from './mode';

describe('getActiveMode', () => {
  it('prefers autoplay when both modes provided', () => {
    const res = getActiveMode('?mode=autoplay&autostart=true');
    expect(res.mode).toBe('autoplay');
    expect(res.conflict).toBe(true);
  });

  it('returns autostart when only autostart provided', () => {
    const res = getActiveMode('?mode=autostart');
    expect(res.mode).toBe('autostart');
    expect(res.conflict).toBe(false);
  });
});
