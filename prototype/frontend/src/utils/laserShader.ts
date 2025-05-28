import * as THREE from 'three';
import { ShaderMaterial } from 'three';

export const createLaserMaterial = (color: THREE.ColorRepresentation) => new ShaderMaterial({
  uniforms: {
    color: { value: new THREE.Color(color) },
    intensity: { value: 1 },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 color;
    uniform float intensity;
    varying vec2 vUv;
    void main() {
      float dist = length(vUv - 0.5);
      float alpha = smoothstep(0.5, 0.45, dist) * intensity;
      gl_FragColor = vec4(color, alpha);
    }
  `,
  transparent: true,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});
