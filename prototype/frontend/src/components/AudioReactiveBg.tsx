import React from 'react';
import { ReactP5Wrapper, Sketch } from 'react-p5-wrapper';
import useAudioMeter from '../hooks/useAudioMeter';

const MAX_PARTICLES = 300;

const AudioReactiveBg: React.FC<{ disabled?: boolean }> = ({ disabled }) => {
  const { rms } = useAudioMeter();

  const sketch: Sketch = (p) => {
    class Particle {
      x = p.random(p.width);
      y = p.random(p.height);
      z = p.random(p.width);
      update(speed: number) {
        this.z -= speed;
        if (this.z < 1) {
          this.z = p.width;
          this.x = p.random(p.width);
          this.y = p.random(p.height);
        }
      }
      draw() {
        const sx = (this.x - p.width / 2) / this.z * p.width + p.width / 2;
        const sy = (this.y - p.height / 2) / this.z * p.height + p.height / 2;
        const r = p.map(this.z, 0, p.width, 3, 0);
        p.fill(150 + rms * 105, 150 + rms * 50, 255);
        p.circle(sx, sy, r);
      }
    }
    let particles: Particle[] = [];

    p.setup = () => {
      p.createCanvas(p.windowWidth, p.windowHeight);
      p.pixelDensity(window.devicePixelRatio || 1);
    };

    p.windowResized = () => {
      p.resizeCanvas(p.windowWidth, p.windowHeight);
    };

    p.draw = () => {
      p.background(10, 10, 20, 40);
      const desired = Math.floor(rms * MAX_PARTICLES);
      while (particles.length < desired) particles.push(new Particle());
      while (particles.length > desired) particles.pop();
      const speed = 2 + rms * 20;
      particles.forEach((pt) => {
        pt.update(speed);
        pt.draw();
      });
    };
  };

  if (disabled) return null;
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
      }}
    >
      <ReactP5Wrapper sketch={sketch} />
    </div>
  );
};

export default AudioReactiveBg;
