import * as THREE from 'three';
import { useStore } from '../store';

/** Camera preset describing a target position, look at point and field of view. */
export interface CameraPreset {
  /** Unique name for the preset. */
  name: string;
  /** Camera position. */
  position: THREE.Vector3 | [number, number, number];
  /** Look-at point. */
  target: THREE.Vector3 | [number, number, number];
  /** Camera field of view. */
  fov: number;
}

/** Easing function used for smooth interpolation. */
function easeInOutQuad(t: number): number {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}

/**
 * CameraManager handles camera presets, transitions and tracking.
 * Call update(delta) on each frame to smoothly move the camera.
 */
export class CameraManager {
  private presets: Map<string, CameraPreset> = new Map();
  private camera: THREE.PerspectiveCamera;
  private from?: CameraPreset;
  private to?: CameraPreset;
  private duration = 0;
  private elapsed = 0;
  private targetObject?: THREE.Object3D;

  constructor(camera: THREE.PerspectiveCamera, presets: CameraPreset[] = []) {
    this.camera = camera;
    presets.forEach((p) => this.addPreset(p));
  }

  /** Add or replace a camera preset. */
  addPreset(preset: CameraPreset) {
    // Normalize to Vector3 for internal use.
    preset = {
      ...preset,
      position: new THREE.Vector3().fromArray(preset.position as number[]),
      target: new THREE.Vector3().fromArray(preset.target as number[]),
    };
    this.presets.set(preset.name, preset);
  }

  /** Remove a preset by name. */
  removePreset(name: string) {
    this.presets.delete(name);
  }

  /** Transition the camera to the named preset over a duration in seconds. */
  transitionTo(name: string, duration = 1) {
    const preset = this.presets.get(name);
    if (!preset) return;
    useStore.getState().setRuntime({ cameraPreset: name });
    this.from = {
      name: 'from',
      position: this.camera.position.clone(),
      target: this.getCurrentTarget(),
      fov: this.camera.fov,
    };
    this.to = preset;
    this.duration = Math.max(0.001, duration);
    this.elapsed = 0;
  }

  /** Follow an object each frame, keeping the lookAt on it. */
  track(object: THREE.Object3D | undefined) {
    this.targetObject = object;
  }

  /** Get current camera target. */
  private getCurrentTarget(): THREE.Vector3 {
    const v = new THREE.Vector3();
    this.camera.getWorldDirection(v);
    return this.camera.position.clone().add(v);
  }

  /** Update the camera each frame with delta time in seconds. */
  update(delta: number) {
    if (this.to && this.from) {
      this.elapsed += delta;
      const t = Math.min(this.elapsed / this.duration, 1);
      const eased = easeInOutQuad(t);
      this.camera.position.lerpVectors(this.from.position, this.to.position, eased);
      this.camera.fov = THREE.MathUtils.lerp(this.from.fov, this.to.fov, eased);
      this.camera.updateProjectionMatrix();

      const look = new THREE.Vector3().lerpVectors(this.from.target, this.to.target, eased);
      this.camera.lookAt(look);

      if (t === 1) {
        this.from = undefined;
        this.to = undefined;
      }
    } else if (this.targetObject) {
      const targetPos = new THREE.Vector3();
      this.targetObject.getWorldPosition(targetPos);
      this.camera.lookAt(targetPos);
    }
  }
}
