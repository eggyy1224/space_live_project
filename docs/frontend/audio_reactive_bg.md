# Audio Reactive Background

This canvas lives behind the Three.js stage and reacts to audio.

## Tweaking
- **Sensitivity** – adjust `sensitivity` in `AudioReactiveBg.tsx` to amplify the effect.
- **Colors** – modify the particle color logic inside the sketch.
- **Particle count** – base count scales with RMS. Change `MAX_PARTICLES` for limits.

The component uses a p5.js sketch and `useAudioMeter` hook. When mic input is active, the background follows speech; otherwise it listens to background music.
