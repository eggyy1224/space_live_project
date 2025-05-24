import { shaderMaterial } from '@react-three/drei';
import { extend, ReactThreeFiber, useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import { useAudioAnalyser } from '../hooks/useAudioAnalyser';
import * as THREE from 'three';

const MoireMaterialImpl = shaderMaterial(
  { uTime: 0, uVolume: 0, uPitch: 0 },
  `varying vec2 vUv;
   void main() {
     vUv = uv;
     gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
   }`,
  `uniform float uTime;
   uniform float uVolume;
   uniform float uPitch;
   varying vec2 vUv;
   void main() {
     float freq = mix(5.0, 30.0, clamp(uPitch / 3000.0, 0.0, 1.0));
     float speed = 1.0 + uVolume * 3.0;
     float intensity = 0.5 + uVolume * 0.5;
     vec2 st = vUv * freq;
     float pattern = sin(st.x + uTime * speed) * sin(st.y - uTime * speed);
     float val = 0.5 + 0.5 * pattern;
     gl_FragColor = vec4(vec3(val * intensity), intensity * 0.4);
   }`
);

extend({ MoireMaterialImpl });

declare global {
  namespace JSX {
    interface IntrinsicElements {
      moireMaterialImpl: ReactThreeFiber.Object3DNode<any, typeof MoireMaterialImpl>;
    }
  }
}

export const MoireShaderMaterial: React.FC = ({ children }) => {
  const ref = useRef<any>();
  const { volume, pitch } = useAudioAnalyser();
  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.uTime = clock.elapsedTime;
      ref.current.uVolume = volume;
      ref.current.uPitch = pitch;
    }
  });
  return <moireMaterialImpl ref={ref} transparent>{children}</moireMaterialImpl>;
};
