/**
 * Defines the mapping from emotion tags to base Blendshape target weights.
 * Keys are emotion tags (string), values are records where keys are ARKit Blendshape names
 * and values are their target weights (0 to 1, or potentially higher for artistic exaggeration).
 * Blendshapes not listed for an emotion default to 0.
 */

export const emotionBaseWeights: Record<string, Record<string, number>> = {
  // --- Foundational States ---
  neutral: {
    // Resets all emotion-related blendshapes to 0
    browDownLeft: 0,
    browDownRight: 0,
    browInnerUp: 0,
    browOuterUpLeft: 0,
    browOuterUpRight: 0,
    eyeSquintLeft: 0,
    eyeSquintRight: 0,
    eyeWideLeft: 0,
    eyeWideRight: 0,
    cheekPuff: 0,
    cheekSquintLeft: 0,
    cheekSquintRight: 0,
    mouthDimpleLeft: 0,
    mouthDimpleRight: 0,
    mouthFrownLeft: 0,
    mouthFrownRight: 0,
    mouthLowerDownLeft: 0,
    mouthLowerDownRight: 0,
    mouthPressLeft: 0,
    mouthPressRight: 0,
    mouthSmileLeft: 0,
    mouthSmileRight: 0,
    mouthStretchLeft: 0,
    mouthStretchRight: 0,
    mouthUpperUpLeft: 0,
    mouthUpperUpRight: 0,
    noseSneerLeft: 0,
    noseSneerRight: 0,
    jawForward: 0,
    // Note: jawOpen and mouthClose are primarily handled by the speaking state logic
  },
  listening: { // Slightly more engaged than neutral
    browInnerUp: 0.1,      // Hint of attention/focus
    eyeWideLeft: 0.05,
    eyeWideRight: 0.05,
  },
  thinking: {
    browDownLeft: 0.35,     // Slight furrow, concentration
    browDownRight: 0.35,
    mouthPressLeft: 0.25,   // Lips slightly pressed
    mouthPressRight: 0.25,
    eyeLookDownLeft: 0.4,  // Simulating looking down/inward (can be overridden by gaze control)
    eyeLookDownRight: 0.4,
  },

  // --- Positive Emotions (Expanded) ---
  happy: { // Standard strong happiness
    mouthSmileLeft: 0.95,
    mouthSmileRight: 0.95,
    cheekSquintLeft: 0.75,  // Smile reaching the eyes
    cheekSquintRight: 0.75,
    eyeSquintLeft: 0.45,    // Eyes narrow slightly with smile
    eyeSquintRight: 0.45,
    mouthDimpleLeft: 0.6,
    mouthDimpleRight: 0.6,
    browInnerUp: 0.1,     // Slight lift, openness
  },
  joyful: { // More exuberant happiness
    mouthSmileLeft: 1.0,    // Max smile
    mouthSmileRight: 1.0,
    cheekSquintLeft: 0.85,
    cheekSquintRight: 0.85,
    eyeSquintLeft: 0.5,
    eyeSquintRight: 0.5,
    mouthDimpleLeft: 0.7,
    mouthDimpleRight: 0.7,
    browInnerUp: 0.15,
    browOuterUpLeft: 0.1,   // Hint of outer brow lift
    browOuterUpRight: 0.1,
    eyeWideLeft: 0.1, // Counteracts squint slightly for 'gleam'
    eyeWideRight: 0.1,
  },
  content: { // Calm happiness, satisfaction
    mouthSmileLeft: 0.35,
    mouthSmileRight: 0.35,
    cheekSquintLeft: 0.15,
    cheekSquintRight: 0.15,
    eyeSquintLeft: 0.1,
    eyeSquintRight: 0.1,
    // Generally relaxed features
  },
  amused: { // Light-hearted enjoyment, often slightly asymmetrical
    mouthSmileLeft: 0.6,
    mouthSmileRight: 0.5,
    cheekSquintLeft: 0.4,
    cheekSquintRight: 0.3,
    eyeSquintLeft: 0.3,
    eyeSquintRight: 0.25,
    browOuterUpLeft: 0.2, // Asymmetry can suggest amusement
  },
  excited: {
    eyeWideLeft: 0.6,
    eyeWideRight: 0.6,
    mouthSmileLeft: 0.75,    // Energetic smile
    mouthSmileRight: 0.75,
    browOuterUpLeft: 0.7,   // Brows raised
    browOuterUpRight: 0.7,
    jawOpen: 0.2,          // Mouth slightly open
  },
  interested: { // Curiosity, engagement
    browInnerUp: 0.45,
    browOuterUpLeft: 0.3,
    browOuterUpRight: 0.3,
    eyeWideLeft: 0.2,
    eyeWideRight: 0.2,
    mouthPucker: 0.1, // Slight lip purse sometimes indicates interest
  },
  affectionate: { // Warmth, fondness
    mouthSmileLeft: 0.5,   // Soft smile
    mouthSmileRight: 0.5,
    cheekSquintLeft: 0.25,
    cheekSquintRight: 0.25,
    eyeSquintLeft: 0.2,
    eyeSquintRight: 0.2,
    browInnerUp: 0.15,
  },
  proud: {
    mouthSmileLeft: 0.25,    // Subtle, controlled smile
    mouthSmileRight: 0.25,
    mouthPressLeft: 0.35,    // Slight lip press, composure
    mouthPressRight: 0.35,
    cheekSquintLeft: 0.15,
    cheekSquintRight: 0.15,
    jawForward: 0.05,
  },
  relieved: {
    browInnerUp: -0.1,       // Brows relaxing from previous tension
    browDownLeft: -0.2,       // Relaxing down
    browDownRight: -0.2,
    mouthPucker: 0.35,       // Part of a sigh shape
    jawOpen: 0.2,          // Slight opening for sigh
    eyeBlinkLeft: 0.5,       // Simulate a slow blink/eye close (can be animation)
    eyeBlinkRight: 0.5,
  },
  grateful: {
    mouthSmileLeft: 0.3,
    mouthSmileRight: 0.3,
    browInnerUp: 0.25,
    eyeSquintLeft: 0.1,
    eyeSquintRight: 0.1,
    // Often includes head nod/tilt (animation)
  },
  hopeful: {
    browInnerUp: 0.3,
    browOuterUpLeft: 0.15,
    browOuterUpRight: 0.15,
    mouthSmileLeft: 0.15,
    mouthSmileRight: 0.15,
    eyeWideLeft: 0.1,
    eyeWideRight: 0.1,
    // Looking forward
  },
  serene: { // Utter calm, peacefulness
    // Very close to neutral, perhaps slightly softer features
    mouthSmileLeft: 0.05,
    mouthSmileRight: 0.05,
    eyeBlinkLeft: 0.1,
    eyeBlinkRight: 0.1,
    // Relaxed blink rate (control via animation timing)
  },
  playful: {
    mouthSmileLeft: 0.7,
    mouthSmileRight: 0.6,
    cheekSquintLeft: 0.5,
    cheekSquintRight: 0.4,
    eyeSquintLeft: 0.4,
    eyeSquintRight: 0.3,
    browOuterUpLeft: 0.3,
    noseSneerRight: 0.1,
  },
  triumphant: {
    mouthSmileLeft: 0.8,
    mouthSmileRight: 0.8,
    cheekSquintLeft: 0.6,
    cheekSquintRight: 0.6,
    jawForward: 0.15,
    browDownLeft: 0.1,
    browDownRight: 0.1,
    // Slight lowering, intensity
  },

  // --- Negative Emotions (Expanded) ---
  sad: { // Standard strong sadness
    browInnerUp: 0.9,       // Very pronounced inner brow lift
    mouthFrownLeft: 0.75,   // Strong downturn
    mouthFrownRight: 0.75,
    mouthStretchLeft: 0.2,
    mouthStretchRight: 0.2,
    eyeSquintLeft: 0.15,
    eyeSquintRight: 0.15,
    mouthLowerDownLeft: 0.3, // Lower lip trembling/down
    mouthLowerDownRight: 0.3,
  },
  gloomy: { // Less intense, more withdrawn sadness
    browInnerUp: 0.45,
    mouthFrownLeft: 0.45,
    mouthFrownRight: 0.45,
    mouthPressLeft: 0.2,
    mouthPressRight: 0.2,
    eyeLookDownLeft: 0.35,   // Gaze often downward
    eyeLookDownRight: 0.35,
  },
  disappointed: {
    browInnerUp: 0.55,
    browDownLeft: 0.25,
    browDownRight: 0.25,
    mouthFrownLeft: 0.55,
    mouthFrownRight: 0.55,
    mouthPucker: 0.25,       // Pursed lips, sigh preparation
  },
  worried: { // Anxiety, concern
    browInnerUp: 0.8,
    browDownLeft: 0.45,
    browDownRight: 0.45,
    mouthStretchLeft: 0.35,  // Tense mouth
    mouthStretchRight: 0.35,
    eyeWideLeft: 0.2,      // Eyes slightly wider
    eyeWideRight: 0.2,
  },
  angry: { // Standard strong anger
    browDownLeft: 0.95,     // Max brow down
    browDownRight: 0.95,
    noseSneerLeft: 0.75,     // Flared nostrils
    noseSneerRight: 0.75,
    mouthPressLeft: 0.9,   // Tightly pressed lips
    mouthPressRight: 0.9,
    jawForward: 0.35,
    eyeSquintLeft: 0.65,     // Intense glare
    eyeSquintRight: 0.65,
  },
  irritated: { // Annoyance, less intense anger
    browDownLeft: 0.55,
    browDownRight: 0.55,
    noseSneerLeft: 0.35,
    noseSneerRight: 0.35,
    mouthPressLeft: 0.45,
    mouthPressRight: 0.45,
    eyeSquintLeft: 0.35,
    eyeSquintRight: 0.35,
  },
  frustrated: {
    browDownLeft: 0.75,
    browDownRight: 0.75,
    mouthPressLeft: 0.65,    // More tension than irritation
    mouthPressRight: 0.65,
    jawForward: 0.2,
    cheekPuff: 0.25,         // Holding breath / tension
    noseSneerLeft: 0.25,
    noseSneerRight: 0.25,
  },
  fearful: { // Standard strong fear
    eyeWideLeft: 0.95,       // Eyes wide open
    eyeWideRight: 0.95,
    browInnerUp: 0.85,       // Raised brows, stress
    browOuterUpLeft: 0.55,
    browOuterUpRight: 0.55,
    mouthStretchLeft: 0.45,  // Mouth stretched horizontally in fear/tension
    mouthStretchRight: 0.45,
    jawOpen: 0.25,           // Mouth slightly agape
  },
  nervous: { // Similar to worried, more agitated
    browInnerUp: 0.65,
    browDownLeft: 0.35,
    browDownRight: 0.35,
    mouthStretchLeft: 0.45,  // Tense, perhaps trembling (use animation?)
    mouthStretchRight: 0.45,
    mouthPressLeft: 0.25,    // Alternating tension
    mouthPressRight: 0.25,
    eyeWideLeft: 0.1,
    eyeWideRight: 0.1,
  },
  disgusted: { // Standard strong disgust
    noseSneerLeft: 0.95,     // Max sneer
    noseSneerRight: 0.95,
    mouthUpperUpLeft: 0.75,  // Upper lip raised significantly
    mouthUpperUpRight: 0.75,
    browDownLeft: 0.65,      // Disapproving frown
    browDownRight: 0.65,
    eyeSquintLeft: 0.55,
    eyeSquintRight: 0.55,
    mouthLowerDownLeft: 0.25, // Lower lip might push out slightly
    mouthLowerDownRight: 0.25,
  },
  contemptuous: { // Scorn, disdain - often asymmetrical
    mouthSmileLeft: 0.55,    // One-sided smirk
    noseSneerLeft: 0.45,     // Slight sneer on the same side
    browDownRight: 0.45,     // Opposite brow slightly down
    eyeSquintRight: 0.55,    // Opposite eye slightly squinted
  },
  pain: {
    eyeSquintLeft: 0.95,     // Eyes squeezed shut or nearly shut
    eyeSquintRight: 0.95,
    browDownLeft: 0.85,
    browDownRight: 0.85,
    browInnerUp: 0.45,       // Can pull up even with brows down
    mouthStretchLeft: 0.65,  // Grimace
    mouthStretchRight: 0.65,
    jawOpen: 0.25,           // Mouth might be open in pain
    mouthFrownLeft: 0.35,
    mouthFrownRight: 0.35,
  },
  embarrassed: {
    cheekSquintLeft: 0.45,   // Similar to smile/grimace cheek
    cheekSquintRight: 0.45,
    mouthPressLeft: 0.35,    // Awkward mouth press
    mouthPressRight: 0.35,
    eyeLookDownLeft: 0.65,   // Averting gaze
    eyeLookDownRight: 0.65,
    browInnerUp: 0.25,       // Slight worry/discomfort
  },
  jealous: {
    browDownLeft: 0.6,
    browDownRight: 0.6,
    eyeSquintLeft: 0.4,
    eyeSquintRight: 0.4,
    mouthPressLeft: 0.5,
    mouthPressRight: 0.5,
    noseSneerRight: 0.2,
    jawLeft: 0.1,
  },
  regretful: {
    browInnerUp: 0.6,
    mouthFrownLeft: 0.4,
    mouthFrownRight: 0.4,
    mouthLowerDownLeft: 0.2,
    mouthLowerDownRight: 0.2,
    eyeLookDownLeft: 0.4,
    eyeLookDownRight: 0.4,
  },
  guilty: {
    browInnerUp: 0.5,
    mouthPressLeft: 0.4,
    mouthPressRight: 0.4,
    eyeLookDownLeft: 0.7,
    eyeLookDownRight: 0.7,
    mouthFrownLeft: 0.2,
    mouthFrownRight: 0.2,
  },
  ashamed: { // Similar to guilty/embarrassed, perhaps more inward
    browInnerUp: 0.4,
    browDownLeft: 0.3,
    browDownRight: 0.3,
    eyeLookDownLeft: 0.8,
    eyeLookDownRight: 0.8,
    mouthPressLeft: 0.5,
    mouthPressRight: 0.5,
  },
  despairing: {
    browInnerUp: 1.0,
    mouthFrownLeft: 0.8,
    mouthFrownRight: 0.8,
    mouthLowerDownLeft: 0.5,
    mouthLowerDownRight: 0.5,
    eyeSquintLeft: 0.2,
    eyeSquintRight: 0.2,
    jawOpen: 0.1,
  },
  spiteful: {
    mouthSmileLeft: 0.3,
    mouthSmileRight: 0.3,
    eyeSquintLeft: 0.6,
    eyeSquintRight: 0.6,
    noseSneerLeft: 0.4,
    noseSneerRight: 0.4,
    browDownLeft: 0.5,
    browDownRight: 0.5,
  },

  // --- Ambiguous / Cognitive / Other States (Expanded) ---
  surprised: { // Standard strong surprise
    eyeWideLeft: 1.0,       // Max eye wide
    eyeWideRight: 1.0,
    browInnerUp: 0.5,
    browOuterUpLeft: 1.0,   // Max brow raise
    browOuterUpRight: 1.0,
    jawOpen: 0.45,           // Mouth agape
    mouthStretchLeft: 0.2,
    mouthStretchRight: 0.2,
  },
  confused: {
    browDownLeft: 0.45,
    browInnerUp: 0.65,
    browOuterUpRight: 0.35,
    mouthPucker: 0.35,
    jawLeft: 0.2,
  },
  skeptical: {
    browOuterUpLeft: 0.75,
    mouthPressRight: 0.45,
    eyeSquintLeft: 0.45,
    mouthLeft: 0.2,
  },
  bored: {
    mouthFrownLeft: 0.25,
    mouthFrownRight: 0.25,
    eyeBlinkLeft: 0.4,
    eyeBlinkRight: 0.4,
    jawOpen: 0.15,
  },
  sleepy: {
    eyeBlinkLeft: 0.9,
    eyeBlinkRight: 0.9,
    jawOpen: 0.25,
    browInnerUp: 0.05,
  },
  scheming: { // Mischievous, plotting
    mouthSmileLeft: 0.45,
    mouthSmileRight: 0.1,
    browDownRight: 0.35,
    browDownLeft: 0.1,
    eyeSquintLeft: 0.55,
    eyeSquintRight: 0.55,
    noseSneerLeft: 0.15,
  },
  determined: {
    browDownLeft: 0.6,
    browDownRight: 0.6,
    mouthPressLeft: 0.7,
    mouthPressRight: 0.7,
    jawForward: 0.2,
    eyeSquintLeft: 0.3,
    eyeSquintRight: 0.3,
  },
  impatient: {
    browDownLeft: 0.4,
    browDownRight: 0.4,
    mouthPressLeft: 0.5,
    mouthPressRight: 0.5,
    cheekPuff: 0.15,
  },
  shy: { // Similar to embarrassed, maybe less negative
    mouthSmileLeft: 0.15,
    mouthSmileRight: 0.15,
    cheekSquintLeft: 0.2,
    cheekSquintRight: 0.2,
    eyeLookDownLeft: 0.5,
    eyeLookDownRight: 0.5,
    browInnerUp: 0.1,
  },
  bashful: { // More pronounced shyness, often with more flushing (cheek color not blendshape)
    mouthSmileLeft: 0.2,
    mouthSmileRight: 0.2,
    cheekSquintLeft: 0.3,
    cheekSquintRight: 0.3,
    eyeLookDownLeft: 0.7,
    eyeLookDownRight: 0.7,
    browInnerUp: 0.15,
    mouthPressLeft: 0.1,
    mouthPressRight: 0.1,
  },
  smug: { // Self-satisfied, perhaps slightly contemptuous smile
    mouthSmileLeft: 0.3,
    mouthSmileRight: 0.3,
    mouthDimpleLeft: 0.2,
    mouthDimpleRight: 0.2,
    browDownLeft: 0.1,
    browDownRight: 0.1,
    eyeSquintLeft: 0.2,
    eyeSquintRight: 0.2,
    cheekSquintLeft: 0.1,
    cheekSquintRight: 0.1,
  },
  awe: { // Wonder, amazement
    eyeWideLeft: 0.7,
    eyeWideRight: 0.7,
    mouthOpen: 0.3,
    jawOpen: 0.3,
    browInnerUp: 0.2,
    browOuterUpLeft: 0.4,
    browOuterUpRight: 0.4,
  },
  doubtful: { // Questioning, uncertain
    browInnerUp: 0.5,
    browOuterUpLeft: 0.2,
    mouthPucker: 0.2,
    mouthLeft: 0.1,
  },
};

/**
 * Gets the base Blendshape weights for a given emotion tag.
 * Returns weights for 'neutral' if the tag is not found.
 * @param tag The emotion tag
 * @returns A record of Blendshape weights for the tag, inheriting from 'neutral'.
 */
export const getEmotionBaseWeights = (tag: string): Record<string, number> => {
  // Start with neutral weights (all zeros for emotion shapes)
  const base = { ...emotionBaseWeights.neutral };
  const specific = emotionBaseWeights[tag];
  if (specific) {
    // Override neutral with specific emotion weights
    return { ...base, ...specific };
  } else {
    console.warn(`[emotionMappings] Emotion tag "${tag}" not found. Falling back to neutral.`);
    return base;
  }
};

// Export the list of available emotion tags for reference and validation
export const availableEmotionTags = Object.keys(emotionBaseWeights); 