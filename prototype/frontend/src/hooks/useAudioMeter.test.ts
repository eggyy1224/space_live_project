import { calculateRms } from './useAudioMeter';

describe('calculateRms', () => {
  it('returns value between 0 and 1', () => {
    const data = new Uint8Array([0, 128, 255, 64]);
    const rms = calculateRms(data);
    expect(rms).toBeGreaterThanOrEqual(0);
    expect(rms).toBeLessThanOrEqual(1);
  });
});
