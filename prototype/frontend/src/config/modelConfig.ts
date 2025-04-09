/**
 * @fileoverview Configuration constants related to 3D models and animations.
 */

/**
 * The URL for the head model.
 */
export const HEAD_MODEL_URL = '/models/headonly.glb';

/**
 * The URL for the body model.
 */
export const BODY_MODEL_URL = '/models/armature001_model.glb';

/**
 * @deprecated The concept of a single default model is deprecated in favor of separate head/body.
 */
// export const DEFAULT_MODEL_URL = '/models/armature001_model.glb';

/**
 * @deprecated Model switching logic needs redesign for separate head/body.
 */
// export const AVAILABLE_MODELS: string[] = [
//   DEFAULT_MODEL_URL, // Add the default model here
//   '/models/mixamowomanwithface.glb',
//   '/models/headonly.glb',
//   '/models/Armature_000A.glb',
//   '/models/Armature_000B.glb'
//   // Add other switchable models here
// ];

/**
 * List of external animation file paths relative to the public directory.
 * These will be used by the body model.
 */
export const EXTERNAL_ANIMATION_PATHS: string[] = [
  '/animations/BaseballHit_animation.glb',
  '/animations/BodyBlock_animation.glb'
  // Add other external animation paths here
]; 