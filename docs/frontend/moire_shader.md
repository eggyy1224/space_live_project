# Moiré Shader Effect

The `MoireShaderMaterial` component overlays a transparent Moiré interference pattern on the astronaut head.

## Parameters
- **uTime** – updated every frame to animate the pattern.
- **uVolume** – real-time RMS volume from `useAudioAnalyser`.
- **uPitch** – spectral centroid (approximate pitch) from `useAudioAnalyser`.

Pattern frequency scales with `uPitch` while animation speed and intensity follow `uVolume`.

## Usage
```tsx
import { MoireShaderMaterial } from '../components/MoireShaderMaterial';

<mesh geometry={geometry}>
  <MoireShaderMaterial />
</mesh>
```
Toggle the effect via the settings panel. The material is only rendered when `enableMoire` is true in the store.
