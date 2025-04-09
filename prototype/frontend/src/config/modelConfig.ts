/**
 * @fileoverview Configuration constants related to 3D models and animations.
 */

/**
 * The default model to load when the application starts.
 */
export const DEFAULT_MODEL_URL = '/models/armature001_model.glb';

/**
 * List of model URLs available for switching via the UI.
 * Ensure DEFAULT_MODEL_URL is included if it should be switchable.
 */
export const AVAILABLE_MODELS: string[] = [
  DEFAULT_MODEL_URL, // Add the default model here
  '/models/mixamowomanwithface.glb',
  '/models/headonly.glb',
  '/models/Armature_000A.glb',
  '/models/Armature_000B.glb'
  // Add other switchable models here
];

/**
 * List of external animation file paths relative to the public directory.
 * These animations will be loaded and merged with the model's embedded animations.
 */
export const EXTERNAL_ANIMATION_PATHS: string[] = [
  '/animations/BaseballHit_animation.glb',
  '/animations/BodyBlock_animation.glb'
  // Add other external animation paths here
]; 