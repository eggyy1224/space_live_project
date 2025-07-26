/**
 * Defines the mapping from emotion tags to base Blendshape target weights.
 * Keys are emotion tags (string), values are records where keys are ARKit Blendshape names
 * and values are their target weights (0 to 1, or potentially higher for artistic exaggeration).
 * Blendshapes not listed for an emotion default to 0.
 */

// Global multiplier applied to all emotion weights for exaggerated effect.
// Set to 1.0 to disable exaggeration, >1.0 for stronger expressions, <1.0 for subtler ones.
export const EXAGGERATION_FACTOR = 0.9;

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
  listening: { // Slightly more engaged than neutral - Fun version
    browInnerUp: 0.4,
    eyeWideLeft: 0.3,
    eyeWideRight: 0.3,
    mouthPucker: 0.2, // Subtle "ooh?" shape
    // Original: browInnerUp: 0.25, eyeWideLeft: 0.15, eyeWideRight: 0.15
  },
  thinking: { // Magical version - Retained from previous changes
    browInnerUp: 1.8,
    browOuterUpLeft: 1.0,
    mouthPressLeft: 0.2,
    mouthPressRight: 0.2,
    mouthPucker: 0.7,
    eyeLookUpLeft: 1.2,
    eyeLookUpRight: 1.2,
  },

  // --- Positive Emotions (Expanded) ---
  happy: { // Magical version - Retained from previous changes
    mouthSmileLeft: 4.0,
    mouthSmileRight: 4.0,
    cheekSquintLeft: 2.0,
    cheekSquintRight: 2.0,
    eyeSquintLeft: 1.8,
    eyeSquintRight: 1.8,
    mouthDimpleLeft: 0.9,
    mouthDimpleRight: 0.9,
    browInnerUp: 0.8,
    jawOpen: 0.6,
    eyeWideLeft: 0.5,
    eyeWideRight: 0.5,
  },
  joyful: { // More exuberant happiness - Fun version
    mouthSmileLeft: 3.8,
    mouthSmileRight: 3.8,
    cheekSquintLeft: 2.0,
    cheekSquintRight: 2.0,
    eyeWideLeft: 1.8,
    eyeWideRight: 1.8,
    browOuterUpLeft: 1.0,
    browOuterUpRight: 1.0,
    jawOpen: 1.5,
    // Original: mouthSmileLeft: 3.0, mouthSmileRight: 3.0, cheekSquintLeft: 1.3, cheekSquintRight: 1.3, eyeSquintLeft: 0.8, eyeSquintRight: 0.8, mouthDimpleLeft: 1.1, mouthDimpleRight: 1.1, browInnerUp: 0.3, browOuterUpLeft: 0.2, browOuterUpRight: 0.2, eyeWideLeft: 0.5, eyeWideRight: 0.5, jawOpen: 0.8
  },
  content: { // Calm happiness, satisfaction - Fun version
    mouthSmileLeft: 1.2,
    mouthSmileRight: 1.2,
    cheekSquintLeft: 1.0,
    cheekSquintRight: 1.0,
    eyeSquintLeft: 0.7,
    eyeSquintRight: 0.7,
    eyeBlinkLeft: 0.2,
    eyeBlinkRight: 0.2,
    browInnerUp: 0.2,
  },
  amused: { // Light-hearted enjoyment, often slightly asymmetrical - Fun version
    mouthSmileLeft: 2.0,
    mouthSmileRight: 1.2, // Asymmetrical smile
    cheekSquintLeft: 1.6,
    eyeSquintLeft: 1.3,
    eyeSquintRight: 0.6, // Knowing squint
    browOuterUpLeft: 1.3,
    browOuterUpRight: 0.4,
    // Original: mouthSmileLeft: 1.8, mouthSmileRight: 1.6, cheekSquintLeft: 1.2, cheekSquintRight: 1.0, eyeSquintLeft: 1.1, eyeSquintRight: 1.0, browOuterUpLeft: 1.0
  },
  excited: { // Fun version - Very animated
    eyeWideLeft: 2.0,
    eyeWideRight: 2.0,
    mouthSmileLeft: 2.0,
    mouthSmileRight: 2.0,
    browOuterUpLeft: 2.0,
    browOuterUpRight: 2.0,
    jawOpen: 2.0,
    // Original: eyeWideLeft: 2.0, eyeWideRight: 2.0, mouthSmileLeft: 2.0, mouthSmileRight: 2.0, browOuterUpLeft: 2.0, browOuterUpRight: 2.0, jawOpen: 1.2
  },
  interested: { // Fun version - Curious
    browInnerUp: 2.0,
    browOuterUpLeft: 1.2,
    browOuterUpRight: 1.2,
    eyeWideLeft: 1.6,
    eyeWideRight: 1.6,
    mouthPucker: 0.5,
    jawOpen: 0.7,
    headTilt: 0.2,
  },
  affectionate: { // Fun version - Warm & fuzzy
    mouthSmileLeft: 1.4,
    mouthSmileRight: 1.4,
    cheekSquintLeft: 1.2,
    cheekSquintRight: 1.2,
    eyeSquintLeft: 0.8,
    eyeSquintRight: 0.8,
    browInnerUp: 0.6,
    eyeWideLeft: 0.3,
    eyeWideRight: 0.3,
  },
  proud: { // Fun version - Chin up
    mouthSmileLeft: 0.8,
    mouthSmileRight: 0.8,
    mouthPressLeft: 1.8,
    mouthPressRight: 1.8,
    cheekSquintLeft: 0.5,
    cheekSquintRight: 0.5,
    jawForward: 1.2,
    browDownLeft: 1.0,
    browDownRight: 1.0,
    browOuterUpLeft: 0.5,
    browOuterUpRight: 0.5,
  },
  relieved: { // Fun version - Big sigh
    browInnerUp: -0.4,
    browDownLeft: -0.2,
    browDownRight: -0.2,
    mouthPucker: 1.8,
    jawOpen: 0.6,
    eyeBlinkLeft: 2.0,
    eyeBlinkRight: 2.0,
    mouthSmileLeft: 0.4,
    mouthSmileRight: 0.4,
  },
  grateful: { // Fun version - Thankful
    mouthSmileLeft: 1.0,
    mouthSmileRight: 1.0,
    browInnerUp: 0.8,
    eyeSquintLeft: 0.4,
    eyeSquintRight: 0.4,
    headTilt: 0.15,
  },
  hopeful: { // Fun version - Looking forward
    browInnerUp: 1.5,
    browOuterUpLeft: 1.0,
    browOuterUpRight: 1.0,
    mouthSmileLeft: 0.8,
    mouthSmileRight: 0.8,
    eyeWideLeft: 1.2,
    eyeWideRight: 1.2,
  },
  serene: { // Fun version - Peaceful glow
    mouthSmileLeft: 0.5,
    mouthSmileRight: 0.5,
    eyeBlinkLeft: 0.3,
    eyeBlinkRight: 0.3,
    browInnerUp: -0.1,
    headTilt: 0.1,
  },
  playful: { // Fun version - Cheeky
    mouthSmileLeft: 1.8,    // Cheeky grin
    mouthSmileRight: 1.0,
    browOuterUpLeft: 1.0,
    browOuterUpRight: 0.4,  // One eyebrow raised
    eyeBlinkLeft: 0.8,      // Wink-like
    eyeSquintRight: 0.5,
    tongueOut: 0.5,         // Slightly out
    // Original: mouthSmileLeft: 1.3, mouthSmileRight: 1.1, cheekSquintLeft: 0.9, cheekSquintRight: 0.75, eyeSquintLeft: 1.2, eyeSquintRight: 1.1, browOuterUpLeft: 0.6, noseSneerRight: 0.5
  },
  triumphant: { // Fun version - Victorious
    mouthSmileLeft: 2.0,
    mouthSmileRight: 2.0,
    cheekSquintLeft: 1.4,
    cheekSquintRight: 1.4,
    jawForward: 0.6,
    browDownLeft: 0.4,
    browDownRight: 0.4,
    eyeWideLeft: 0.8,
    eyeWideRight: 0.8,
  },

  // --- Negative Emotions (Expanded) ---
  sad: { // Standard strong sadness - Comically tragic fun version
    browInnerUp: 2.0,
    mouthFrownLeft: 2.0,
    mouthFrownRight: 2.0,
    mouthLowerDownLeft: 1.5,
    mouthLowerDownRight: 1.5,
    eyeSquintLeft: 1.0,
    eyeSquintRight: 1.0,
    jawOpen: 0.7, // Quivering lip effect
    // Original: browInnerUp: 2.0, mouthFrownLeft: 2.0, mouthFrownRight: 2.0, mouthStretchLeft: 0.3, mouthStretchRight: 0.3, eyeSquintLeft: 0.5, eyeSquintRight: 0.5, mouthLowerDownLeft: 0.5, mouthLowerDownRight: 0.5
  },
  gloomy: { // Fun version - Melancholic
    browInnerUp: 2.0,
    mouthFrownLeft: 1.2,
    mouthFrownRight: 1.2,
    mouthPressLeft: 0.6,
    mouthPressRight: 0.6,
    eyeLookDownLeft: 1.4,
    eyeLookDownRight: 1.4,
    jawOpen: 0.3,
  },
  disappointed: { // Fun version - Heavy sigh
    browInnerUp: 1.8,
    browDownLeft: 1.2,
    browDownRight: 1.2,
    mouthFrownLeft: 1.3,
    mouthFrownRight: 1.3,
    mouthPucker: 1.2,
    eyeSquintLeft: 0.4,
    eyeSquintRight: 0.4,
  },
  worried: { // Anxiety, concern
    browInnerUp: 1.4,       // 增強到1.4（原值0.8）
    browDownLeft: 0.9,      // 增強到0.9（原值0.45）
    browDownRight: 0.9,     // 增強到0.9（原值0.45）
    mouthStretchLeft: 0.7,  // 增強到0.7（原值0.35）
    mouthStretchRight: 0.7, // 增強到0.7（原值0.35）
    eyeWideLeft: 0.4,       // 增強到0.4（原值0.2）
    eyeWideRight: 0.4,      // 增強到0.4（原值0.2）
  },
  angry: { // Magical version - Retained from previous changes
    browDownLeft: 1.8,
    browDownRight: 1.8,
    noseSneerLeft: 1.4,
    noseSneerRight: 1.4,
    mouthPressLeft: 1.8,
    mouthPressRight: 1.8,
    jawForward: 0.9,
    eyeSquintLeft: 0.6,
    eyeSquintRight: 0.6,
    eyeWideLeft: 0.2,
    eyeWideRight: 0.2,
  },
  irritated: { // Annoyance, less intense anger
    browDownLeft: 1.0,      // 增強到1.0（原值0.55）
    browDownRight: 1.0,     // 增強到1.0（原值0.55）
    noseSneerLeft: 0.7,     // 增強到0.7（原值0.35）
    noseSneerRight: 0.7,    // 增強到0.7（原值0.35）
    mouthPressLeft: 0.9,    // 增強到0.9（原值0.45）
    mouthPressRight: 0.9,   // 增強到0.9（原值0.45）
    eyeSquintLeft: 0.7,     // 增強到0.7（原值0.35）
    eyeSquintRight: 0.7,    // 增強到0.7（原值0.35）
  },
  frustrated: { // Fun version - Steam out the ears
    browDownLeft: 2.0,
    browDownRight: 2.0,
    mouthPressLeft: 1.6,
    mouthPressRight: 1.6,
    jawForward: 1.2,
    cheekPuff: 1.8,
    noseSneerLeft: 1.0,
    noseSneerRight: 1.0,
    eyeSquintLeft: 0.9,
    eyeSquintRight: 0.9,
  },
  fearful: { // Standard strong fear - Exaggerated terror fun version
    eyeWideLeft: 3.8, // 彩蛋，保留誇張
    eyeWideRight: 3.8, // 彩蛋，保留誇張
    browInnerUp: 2.0,
    browOuterUpLeft: 2.0,
    browOuterUpRight: 2.0,
    mouthStretchLeft: 1.8,
    mouthStretchRight: 1.8,
    jawOpen: 2.0,
    cheekSquintLeft: 1.2, // Eyes so wide cheeks bunch up
    cheekSquintRight: 1.2,
    // Original: eyeWideLeft: 2.5, eyeWideRight: 2.5, browInnerUp: 2.0, browOuterUpLeft: 0.85, browOuterUpRight: 0.85, mouthStretchLeft: 0.7, mouthStretchRight: 0.7, jawOpen: 1.0
  },
  nervous: { // Similar to worried, more agitated
    browInnerUp: 1.2,       // 增強到1.2（原值0.65）
    browDownLeft: 0.7,      // 增強到0.7（原值0.35）
    browDownRight: 0.7,     // 增強到0.7（原值0.35）
    mouthStretchLeft: 0.9,  // 增強到0.9（原值0.45）
    mouthStretchRight: 0.9, // 增強到0.9（原值0.45）
    mouthPressLeft: 0.5,    // 增強到0.5（原值0.25）
    mouthPressRight: 0.5,   // 增強到0.5（原值0.25）
    eyeWideLeft: 0.25,      // 增強到0.25（原值0.1）
    eyeWideRight: 0.25,     // 增強到0.25（原值0.1）
  },
  disgusted: { // Fun version - Eww!
    noseSneerLeft: 2.0,
    noseSneerRight: 2.0,
    mouthUpperUpLeft: 1.6,
    mouthUpperUpRight: 1.6,
    browDownLeft: 1.4,
    browDownRight: 1.4,
    eyeSquintLeft: 1.0,
    eyeSquintRight: 1.0,
    mouthLowerDownLeft: 0.6,
    mouthLowerDownRight: 0.6,
  },
  contemptuous: { // Fun version - Really?
    mouthSmileLeft: 1.4,
    noseSneerLeft: 0.9,
    browDownRight: 1.2,
    eyeSquintRight: 1.1,
    jawLeft: 0.4,
    mouthRight: 0.2,
  },
  pain: { // Fun version - Ow!
    eyeSquintLeft: 2.0,
    eyeSquintRight: 2.0,
    browDownLeft: 2.0,
    browDownRight: 2.0,
    browInnerUp: 1.2,
    mouthStretchLeft: 1.6,
    mouthStretchRight: 1.6,
    jawOpen: 1.0,
    mouthFrownLeft: 1.0,
    mouthFrownRight: 1.0,
  },
  embarrassed: { // Fun version - Blushing
    cheekSquintLeft: 1.2,
    cheekSquintRight: 1.2,
    mouthPressLeft: 0.9,
    mouthPressRight: 0.9,
    eyeLookDownLeft: 1.4,
    eyeLookDownRight: 1.4,
    browInnerUp: 0.6,
    headTilt: -0.2,
  },
  jealous: { // Fun version - Side-eye
    browDownLeft: 1.4,
    browDownRight: 1.4,
    eyeSquintLeft: 1.0,
    eyeSquintRight: 1.0,
    mouthPressLeft: 1.2,
    mouthPressRight: 1.2,
    noseSneerRight: 0.6,
    jawLeft: 0.3,
    eyeLookUpLeft: 0.3,
    eyeLookDownRight: 0.3,
  },
  regretful: { // Fun version - Shouldn't have...
    browInnerUp: 1.4,
    mouthFrownLeft: 1.0,
    mouthFrownRight: 1.0,
    mouthLowerDownLeft: 0.6,
    mouthLowerDownRight: 0.6,
    eyeLookDownLeft: 1.2,
    eyeLookDownRight: 1.2,
    jawOpen: 0.3,
  },
  guilty: { // Fun version - Caught red-handed
    browInnerUp: 1.2,
    mouthPressLeft: 1.0,
    mouthPressRight: 1.0,
    eyeLookDownLeft: 1.4,
    eyeLookDownRight: 1.4,
    mouthFrownLeft: 0.8,
    mouthFrownRight: 0.8,
    cheekPuff: 0.2,
  },
  ashamed: { // Fun version - Can't look
    browInnerUp: 1.0,
    browDownLeft: 0.8,
    browDownRight: 0.8,
    eyeLookDownLeft: 1.6,
    eyeLookDownRight: 1.6,
    mouthPressLeft: 1.2,
    mouthPressRight: 1.2,
    headTilt: -0.3,
  },
  despairing: { // Fun version - Utter woe
    browInnerUp: 2.0,
    mouthFrownLeft: 2.0,
    mouthFrownRight: 2.0,
    mouthLowerDownLeft: 1.2,
    mouthLowerDownRight: 1.2,
    eyeSquintLeft: 0.6,
    eyeSquintRight: 0.6,
    jawOpen: 0.6,
  },
  spiteful: { // Fun version - Evil grin
    mouthSmileLeft: 0.8,
    mouthSmileRight: 0.3,
    eyeSquintLeft: 1.3,
    eyeSquintRight: 1.3,
    noseSneerLeft: 1.0,
    noseSneerRight: 1.0,
    browDownLeft: 1.3,
    browDownRight: 1.3,
  },

  // --- Ambiguous / Cognitive / Other States (Expanded) ---
  surprised: { // Standard strong surprise - Cartoonish pop-eyes fun version
    eyeWideLeft: 3.5, // 彩蛋，保留誇張
    eyeWideRight: 3.5, // 彩蛋，保留誇張
    browOuterUpLeft: 3.2, // 彩蛋，保留誇張
    browOuterUpRight: 3.2, // 彩蛋，保留誇張
    jawOpen: 3.0, // 彩蛋，保留誇張
    mouthPucker: 0.8,
  },
  confused: { // Fun version - More exaggerated asymmetry
    browDownLeft: 2.0,
    browInnerUp: 2.0,
    browOuterUpRight: 1.2,
    mouthPucker: 1.3,
    jawRight: 0.9, // Move jaw to one side
    eyeLookUpLeft: 0.6,
    eyeLookDownRight: 0.6, // Eyes looking different directions subtly
    // Original: browDownLeft: 1.5, browInnerUp: 1.8, browOuterUpRight: 0.55, mouthPucker: 1.0, jawLeft: 0.6
  },
  skeptical: { // Fun version - Stronger one-sided expression
    browOuterUpLeft: 2.0,
    browDownRight: 0.7,
    mouthPressRight: 1.2,
    eyeSquintLeft: 1.2,
    mouthLeft: 0.6, // Pull mouth corner
    jawLeft: 0.4,
    // Original: browOuterUpLeft: 1.2, mouthPressRight: 0.7, eyeSquintLeft: 0.7, mouthLeft: 0.3, jawLeft: 0.15
  },
  bored: { // Fun version - Extremely droopy and disinterested
    mouthFrownLeft: 1.8,
    mouthFrownRight: 1.8,
    eyeBlinkLeft: 0.9, // Almost closed
    eyeBlinkRight: 0.9,
    jawOpen: 1.2, // Slack jaw
    browDownLeft: 0.5, // Droopy eyebrows
    browDownRight: 0.5,
    // Original: mouthFrownLeft: 1.0, mouthFrownRight: 1.0, eyeBlinkLeft: 1.5, eyeBlinkRight: 1.5, jawOpen: 0.6, eyeLookUpLeft: 0.6, eyeLookUpRight: 0.6
  },
  sleepy: { // Fun version - Snoozing
    eyeBlinkLeft: 2.0,
    eyeBlinkRight: 2.0,
    jawOpen: 0.7,
    browInnerUp: -0.1,
    headTilt: 0.5,
    mouthClose: 0.4,
  },
  scheming: { // Mischievous, plotting - Fun version, more villainous
    mouthSmileLeft: 1.5,
    mouthSmileRight: 0.5,
    browDownLeft: 1.2,
    browDownRight: 0.7,
    eyeSquintLeft: 1.2,
    eyeSquintRight: 1.2,
    noseSneerLeft: 0.8,
  },
  determined: {
    browDownLeft: 1.8,
    browDownRight: 1.8,
    mouthPressLeft: 2.0,
    mouthPressRight: 2.0,
    jawForward: 0.8,
    eyeSquintLeft: 1.0,
    eyeSquintRight: 1.0,
  },
  impatient: { // Fun version - Hurry up!
    browDownLeft: 1.2,
    browDownRight: 1.2,
    mouthPressLeft: 1.4,
    mouthPressRight: 1.4,
    cheekPuff: 0.5,
    eyeSquintLeft: 0.5,
    eyeSquintRight: 0.5,
    headTilt: 0.25,
  },
  shy: { // Similar to embarrassed, maybe less negative
    mouthSmileLeft: 0.3,    // 增強到0.3（原值0.15）
    mouthSmileRight: 0.3,   // 增強到0.3（原值0.15）
    cheekSquintLeft: 0.4,   // 增強到0.4（原值0.2）
    cheekSquintRight: 0.4,  // 增強到0.4（原值0.2）
    eyeLookDownLeft: 1.0,   // 增強到1.0（原值0.5）
    eyeLookDownRight: 1.0,  // 增強到1.0（原值0.5）
    browInnerUp: 0.2,       // 增強到0.2（原值0.1）
  },
  bashful: { // More pronounced shyness, often with more flushing (cheek color not blendshape)
    mouthSmileLeft: 0.4,    // 增強到0.4（原值0.2）
    mouthSmileRight: 0.4,   // 增強到0.4（原值0.2）
    cheekSquintLeft: 0.6,   // 增強到0.6（原值0.3）
    cheekSquintRight: 0.6,  // 增強到0.6（原值0.3）
    eyeLookDownLeft: 1.2,   // 增強到1.2（原值0.7）
    eyeLookDownRight: 1.2,  // 增強到1.2（原值0.7）
    browInnerUp: 0.3,       // 增強到0.3（原值0.15）
    mouthPressLeft: 0.2,    // 增強到0.2（原值0.1）
    mouthPressRight: 0.2,   // 增強到0.2（原值0.1）
  },
  smug: {
    mouthSmileRight: 1.5,
    cheekPuff: 0.4,
    browDownLeft: 0.3,
    browOuterUpRight: 1.0,
    eyeSquintLeft: 0.6,
    eyeSquintRight: 0.3,
  },
  awe: {
    eyeWideLeft: 3.0, // 彩蛋，保留誇張
    eyeWideRight: 3.0, // 彩蛋，保留誇張
    jawOpen: 2.8, // 彩蛋，保留誇張
    mouthPucker: 1.0,
    browInnerUp: 1.8,
    browOuterUpLeft: 1.8,
    browOuterUpRight: 1.8,
  },
  doubtful: {
    browInnerUp: 1.2,
    browOuterUpLeft: 0.8,
    mouthPucker: 0.6,
    mouthLeft: 0.4,
    headTilt: 0.3,
    eyeSquintLeft: 0.3,
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
  // Merge neutral with emotion‑specific weights (if any)
  const merged = specific ? { ...base, ...specific } : base;

  // Apply exaggeration
  const scaled: Record<string, number> = {};
  Object.keys(merged).forEach((key) => {
    scaled[key] = merged[key] * EXAGGERATION_FACTOR;
  });

  if (!specific) {
    console.warn(`[emotionMappings] Emotion tag "${tag}" not found. Falling back to neutral.`);
  }
  return scaled;
};

// Export the list of available emotion tags for reference and validation
export const availableEmotionTags = Object.keys(emotionBaseWeights); 