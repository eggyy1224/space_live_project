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
    browInnerUp: 0.25,      // 增強到0.25（原值0.1）
    eyeWideLeft: 0.15,      // 增強到0.15（原值0.05）
    eyeWideRight: 0.15,     // 增強到0.15（原值0.05）
  },
  thinking: {
    browDownLeft: 0.7,      // 增強到0.7（原值0.35）
    browDownRight: 0.7,     // 增強到0.7（原值0.35）
    mouthPressLeft: 0.5,    // 增強到0.5（原值0.25）
    mouthPressRight: 0.5,   // 增強到0.5（原值0.25）
    eyeLookDownLeft: 0.8,   // 增強到0.8（原值0.4）
    eyeLookDownRight: 0.8,  // 增強到0.8（原值0.4）
  },

  // --- Positive Emotions (Expanded) ---
  happy: { // Standard strong happiness
    mouthSmileLeft: 1.5,
    mouthSmileRight: 1.5,
    cheekSquintLeft: 1.2,
    cheekSquintRight: 1.2,
    eyeSquintLeft: 0.7,
    eyeSquintRight: 0.7,
    mouthDimpleLeft: 0.9,
    mouthDimpleRight: 0.9,
    browInnerUp: 0.2,
  },
  joyful: { // More exuberant happiness
    mouthSmileLeft: 1.7,
    mouthSmileRight: 1.7,
    cheekSquintLeft: 1.3,
    cheekSquintRight: 1.3,
    eyeSquintLeft: 0.8,
    eyeSquintRight: 0.8,
    mouthDimpleLeft: 1.1,
    mouthDimpleRight: 1.1,
    browInnerUp: 0.3,
    browOuterUpLeft: 0.2,
    browOuterUpRight: 0.2,
    eyeWideLeft: 0.2,
    eyeWideRight: 0.2,
  },
  content: { // Calm happiness, satisfaction
    mouthSmileLeft: 0.7,    // 增強到0.7（原值0.35）
    mouthSmileRight: 0.7,   // 增強到0.7（原值0.35）
    cheekSquintLeft: 0.3,   // 增強到0.3（原值0.15）
    cheekSquintRight: 0.3,  // 增強到0.3（原值0.15）
    eyeSquintLeft: 0.2,     // 增強到0.2（原值0.1）
    eyeSquintRight: 0.2,    // 增強到0.2（原值0.1）
    // Generally relaxed features
  },
  amused: { // Light-hearted enjoyment, often slightly asymmetrical
    mouthSmileLeft: 1.1,    // 增強到1.1（原值0.6）
    mouthSmileRight: 0.9,   // 增強到0.9（原值0.5）
    cheekSquintLeft: 0.7,   // 增強到0.7（原值0.4）
    cheekSquintRight: 0.55, // 增強到0.55（原值0.3）
    eyeSquintLeft: 0.6,     // 增強到0.6（原值0.3）
    eyeSquintRight: 0.5,    // 增強到0.5（原值0.25）
    browOuterUpLeft: 0.4,   // 增強到0.4（原值0.2）
  },
  excited: {
    eyeWideLeft: 1.0,
    eyeWideRight: 1.0,
    mouthSmileLeft: 1.2,
    mouthSmileRight: 1.2,
    browOuterUpLeft: 1.1,
    browOuterUpRight: 1.1,
    jawOpen: 0.4,
  },
  interested: { // Curiosity, engagement
    browInnerUp: 0.9,       // 增強到0.9（原值0.45）
    browOuterUpLeft: 0.6,   // 增強到0.6（原值0.3）
    browOuterUpRight: 0.6,  // 增強到0.6（原值0.3）
    eyeWideLeft: 0.4,       // 增強到0.4（原值0.2）
    eyeWideRight: 0.4,      // 增強到0.4（原值0.2）
    mouthPucker: 0.2,       // 增強到0.2（原值0.1）
  },
  affectionate: { // Warmth, fondness
    mouthSmileLeft: 1.0,    // 增強到1.0（原值0.5）
    mouthSmileRight: 1.0,   // 增強到1.0（原值0.5）
    cheekSquintLeft: 0.5,   // 增強到0.5（原值0.25）
    cheekSquintRight: 0.5,  // 增強到0.5（原值0.25）
    eyeSquintLeft: 0.4,     // 增強到0.4（原值0.2）
    eyeSquintRight: 0.4,    // 增強到0.4（原值0.2）
    browInnerUp: 0.3,       // 增強到0.3（原值0.15）
  },
  proud: {
    mouthSmileLeft: 0.5,    // 增強到0.5（原值0.25）
    mouthSmileRight: 0.5,   // 增強到0.5（原值0.25）
    mouthPressLeft: 0.7,    // 增強到0.7（原值0.35）
    mouthPressRight: 0.7,   // 增強到0.7（原值0.35）
    cheekSquintLeft: 0.3,   // 增強到0.3（原值0.15）
    cheekSquintRight: 0.3,  // 增強到0.3（原值0.15）
    jawForward: 0.15,       // 增強到0.15（原值0.05）
  },
  relieved: {
    browInnerUp: -0.25,     // 增強到-0.25（原值-0.1）
    browDownLeft: -0.4,     // 增強到-0.4（原值-0.2）
    browDownRight: -0.4,    // 增強到-0.4（原值-0.2）
    mouthPucker: 0.7,       // 增強到0.7（原值0.35）
    jawOpen: 0.4,           // 增強到0.4（原值0.2）
    eyeBlinkLeft: 0.8,      // 增強到0.8（原值0.5）
    eyeBlinkRight: 0.8,     // 增強到0.8（原值0.5）
  },
  grateful: {
    mouthSmileLeft: 0.6,    // 增強到0.6（原值0.3）
    mouthSmileRight: 0.6,   // 增強到0.6（原值0.3）
    browInnerUp: 0.5,       // 增強到0.5（原值0.25）
    eyeSquintLeft: 0.2,     // 增強到0.2（原值0.1）
    eyeSquintRight: 0.2,    // 增強到0.2（原值0.1）
    // Often includes head nod/tilt (animation)
  },
  hopeful: {
    browInnerUp: 0.6,       // 增強到0.6（原值0.3）
    browOuterUpLeft: 0.3,   // 增強到0.3（原值0.15）
    browOuterUpRight: 0.3,  // 增強到0.3（原值0.15）
    mouthSmileLeft: 0.3,    // 增強到0.3（原值0.15）
    mouthSmileRight: 0.3,   // 增強到0.3（原值0.15）
    eyeWideLeft: 0.25,      // 增強到0.25（原值0.1）
    eyeWideRight: 0.25,     // 增強到0.25（原值0.1）
    // Looking forward
  },
  serene: { // Utter calm, peacefulness
    // Very close to neutral, perhaps slightly softer features
    mouthSmileLeft: 0.15,   // 增強到0.15（原值0.05）
    mouthSmileRight: 0.15,  // 增強到0.15（原值0.05）
    eyeBlinkLeft: 0.25,     // 增強到0.25（原值0.1）
    eyeBlinkRight: 0.25,    // 增強到0.25（原值0.1）
    // Relaxed blink rate (control via animation timing)
  },
  playful: {
    mouthSmileLeft: 1.3,    // 增強到1.3（原值0.7）
    mouthSmileRight: 1.1,   // 增強到1.1（原值0.6）
    cheekSquintLeft: 0.9,   // 增強到0.9（原值0.5）
    cheekSquintRight: 0.75, // 增強到0.75（原值0.4）
    eyeSquintLeft: 0.7,     // 增強到0.7（原值0.4）
    eyeSquintRight: 0.6,    // 增強到0.6（原值0.3）
    browOuterUpLeft: 0.6,   // 增強到0.6（原值0.3）
    noseSneerRight: 0.2,    // 增強到0.2（原值0.1）
  },
  triumphant: {
    mouthSmileLeft: 1.4,    // 增強到1.4（原值0.8）
    mouthSmileRight: 1.4,   // 增強到1.4（原值0.8）
    cheekSquintLeft: 1.0,   // 增強到1.0（原值0.6）
    cheekSquintRight: 1.0,  // 增強到1.0（原值0.6）
    jawForward: 0.3,        // 增強到0.3（原值0.15）
    browDownLeft: 0.2,      // 增強到0.2（原值0.1）
    browDownRight: 0.2,     // 增強到0.2（原值0.1）
    // Slight lowering, intensity
  },

  // --- Negative Emotions (Expanded) ---
  sad: { // Standard strong sadness
    browInnerUp: 1.4,
    mouthFrownLeft: 1.2,
    mouthFrownRight: 1.2,
    mouthStretchLeft: 0.3,
    mouthStretchRight: 0.3,
    eyeSquintLeft: 0.25,
    eyeSquintRight: 0.25,
    mouthLowerDownLeft: 0.5,
    mouthLowerDownRight: 0.5,
  },
  gloomy: { // Less intense, more withdrawn sadness
    browInnerUp: 0.9,       // 增強到0.9（原值0.45）
    mouthFrownLeft: 0.9,    // 增強到0.9（原值0.45）
    mouthFrownRight: 0.9,   // 增強到0.9（原值0.45）
    mouthPressLeft: 0.4,    // 增強到0.4（原值0.2）
    mouthPressRight: 0.4,   // 增強到0.4（原值0.2）
    eyeLookDownLeft: 0.7,   // 增強到0.7（原值0.35）
    eyeLookDownRight: 0.7,  // 增強到0.7（原值0.35）
  },
  disappointed: {
    browInnerUp: 1.0,       // 增強到1.0（原值0.55）
    browDownLeft: 0.5,      // 增強到0.5（原值0.25）
    browDownRight: 0.5,     // 增強到0.5（原值0.25）
    mouthFrownLeft: 1.0,    // 增強到1.0（原值0.55）
    mouthFrownRight: 1.0,   // 增強到1.0（原值0.55）
    mouthPucker: 0.5,       // 增強到0.5（原值0.25）
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
  angry: { // Standard strong anger
    browDownLeft: 1.45,
    browDownRight: 1.45,
    noseSneerLeft: 1.2,
    noseSneerRight: 1.2,
    mouthPressLeft: 1.4,
    mouthPressRight: 1.4,
    jawForward: 0.55,
    eyeSquintLeft: 1.0,
    eyeSquintRight: 1.0,
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
  frustrated: {
    browDownLeft: 1.4,      // 增強到1.4（原值0.75）
    browDownRight: 1.4,     // 增強到1.4（原值0.75）
    mouthPressLeft: 1.2,    // 增強到1.2（原值0.65）
    mouthPressRight: 1.2,   // 增強到1.2（原值0.65）
    jawForward: 0.4,        // 增強到0.4（原值0.2）
    cheekPuff: 0.5,         // 增強到0.5（原值0.25）
    noseSneerLeft: 0.5,     // 增強到0.5（原值0.25）
    noseSneerRight: 0.5,    // 增強到0.5（原值0.25）
  },
  fearful: { // Standard strong fear
    eyeWideLeft: 1.5,
    eyeWideRight: 1.5,
    browInnerUp: 1.3,
    browOuterUpLeft: 0.85,
    browOuterUpRight: 0.85,
    mouthStretchLeft: 0.7,
    mouthStretchRight: 0.7,
    jawOpen: 0.4,
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
  disgusted: { // Standard strong disgust
    noseSneerLeft: 1.4,
    noseSneerRight: 1.4,
    mouthUpperUpLeft: 1.1,
    mouthUpperUpRight: 1.1,
    browDownLeft: 1.0,
    browDownRight: 1.0,
    eyeSquintLeft: 0.85,
    eyeSquintRight: 0.85,
    mouthLowerDownLeft: 0.4,
    mouthLowerDownRight: 0.4,
  },
  contemptuous: { // Scorn, disdain - often asymmetrical
    mouthSmileLeft: 0.9,
    noseSneerLeft: 0.7,
    browDownRight: 0.7,
    eyeSquintRight: 0.85,
    jawLeft: 0.2,
  },
  pain: {
    eyeSquintLeft: 1.5,     // 增強到1.5（原值0.95）
    eyeSquintRight: 1.5,    // 增強到1.5（原值0.95）
    browDownLeft: 1.4,      // 增強到1.4（原值0.85）
    browDownRight: 1.4,     // 增強到1.4（原值0.85）
    browInnerUp: 0.9,       // 增強到0.9（原值0.45）
    mouthStretchLeft: 1.2,  // 增強到1.2（原值0.65）
    mouthStretchRight: 1.2, // 增強到1.2（原值0.65）
    jawOpen: 0.5,           // 增強到0.5（原值0.25）
    mouthFrownLeft: 0.7,    // 增強到0.7（原值0.35）
    mouthFrownRight: 0.7,   // 增強到0.7（原值0.35）
  },
  embarrassed: {
    cheekSquintLeft: 0.8,   // 增強到0.8（原值0.45）
    cheekSquintRight: 0.8,  // 增強到0.8（原值0.45）
    mouthPressLeft: 0.7,    // 增強到0.7（原值0.35）
    mouthPressRight: 0.7,   // 增強到0.7（原值0.35）
    eyeLookDownLeft: 1.1,   // 增強到1.1（原值0.65）
    eyeLookDownRight: 1.1,  // 增強到1.1（原值0.65）
    browInnerUp: 0.5,       // 增強到0.5（原值0.25）
  },
  jealous: {
    browDownLeft: 1.1,      // 增強到1.1（原值0.6）
    browDownRight: 1.1,     // 增強到1.1（原值0.6）
    eyeSquintLeft: 0.8,     // 增強到0.8（原值0.4）
    eyeSquintRight: 0.8,    // 增強到0.8（原值0.4）
    mouthPressLeft: 1.0,    // 增強到1.0（原值0.5）
    mouthPressRight: 1.0,   // 增強到1.0（原值0.5）
    noseSneerRight: 0.4,    // 增強到0.4（原值0.2）
    jawLeft: 0.2,           // 增強到0.2（原值0.1）
  },
  regretful: {
    browInnerUp: 1.1,       // 增強到1.1（原值0.6）
    mouthFrownLeft: 0.8,    // 增強到0.8（原值0.4）
    mouthFrownRight: 0.8,   // 增強到0.8（原值0.4）
    mouthLowerDownLeft: 0.4,// 增強到0.4（原值0.2）
    mouthLowerDownRight: 0.4,// 增強到0.4（原值0.2）
    eyeLookDownLeft: 0.8,   // 增強到0.8（原值0.4）
    eyeLookDownRight: 0.8,  // 增強到0.8（原值0.4）
  },
  guilty: {
    browInnerUp: 1.0,       // 增強到1.0（原值0.5）
    mouthPressLeft: 0.8,    // 增強到0.8（原值0.4）
    mouthPressRight: 0.8,   // 增強到0.8（原值0.4）
    eyeLookDownLeft: 1.2,   // 增強到1.2（原值0.7）
    eyeLookDownRight: 1.2,  // 增強到1.2（原值0.7）
    mouthFrownLeft: 0.4,    // 增強到0.4（原值0.2）
    mouthFrownRight: 0.4,   // 增強到0.4（原值0.2）
  },
  ashamed: { // Similar to guilty/embarrassed, perhaps more inward
    browInnerUp: 0.8,       // 增強到0.8（原值0.4）
    browDownLeft: 0.6,      // 增強到0.6（原值0.3）
    browDownRight: 0.6,     // 增強到0.6（原值0.3）
    eyeLookDownLeft: 1.4,   // 增強到1.4（原值0.8）
    eyeLookDownRight: 1.4,  // 增強到1.4（原值0.8）
    mouthPressLeft: 1.0,    // 增強到1.0（原值0.5）
    mouthPressRight: 1.0,   // 增強到1.0（原值0.5）
  },
  despairing: {
    browInnerUp: 1.8,       // 增強到1.8（原值1.0）
    mouthFrownLeft: 1.5,    // 增強到1.5（原值0.8）
    mouthFrownRight: 1.5,   // 增強到1.5（原值0.8）
    mouthLowerDownLeft: 1.0,// 增強到1.0（原值0.5）
    mouthLowerDownRight: 1.0,// 增強到1.0（原值0.5）
    eyeSquintLeft: 0.4,     // 增強到0.4（原值0.2）
    eyeSquintRight: 0.4,    // 增強到0.4（原值0.2）
    jawOpen: 0.3,           // 增強到0.3（原值0.1）
  },
  spiteful: {
    mouthSmileLeft: 0.6,    // 增強到0.6（原值0.3）
    mouthSmileRight: 0.6,   // 增強到0.6（原值0.3）
    eyeSquintLeft: 1.1,     // 增強到1.1（原值0.6）
    eyeSquintRight: 1.1,    // 增強到1.1（原值0.6）
    noseSneerLeft: 0.8,     // 增強到0.8（原值0.4）
    noseSneerRight: 0.8,    // 增強到0.8（原值0.4）
    browDownLeft: 1.0,      // 增強到1.0（原值0.5）
    browDownRight: 1.0,     // 增強到1.0（原值0.5）
  },

  // --- Ambiguous / Cognitive / Other States (Expanded) ---
  surprised: { // Standard strong surprise
    eyeWideLeft: 1.5,
    eyeWideRight: 1.5,
    browInnerUp: 0.8,
    browOuterUpLeft: 1.5,
    browOuterUpRight: 1.5,
    jawOpen: 0.7,
    mouthStretchLeft: 0.3,
    mouthStretchRight: 0.3,
  },
  confused: {
    browDownLeft: 0.7,
    browInnerUp: 1.0,
    browOuterUpRight: 0.55,
    mouthPucker: 0.55,
    jawLeft: 0.3,
  },
  skeptical: {
    browOuterUpLeft: 1.2,
    mouthPressRight: 0.7,
    eyeSquintLeft: 0.7,
    mouthLeft: 0.3,
    jawLeft: 0.15,
  },
  bored: {
    mouthFrownLeft: 0.5,    // 增強到0.5（原值0.25）
    mouthFrownRight: 0.5,   // 增強到0.5（原值0.25）
    eyeBlinkLeft: 0.8,      // 增強到0.8（原值0.4）
    eyeBlinkRight: 0.8,     // 增強到0.8（原值0.4）
    jawOpen: 0.3,           // 增強到0.3（原值0.15）
    eyeLookUpLeft: 0.3,     // 新增：眼睛向上看表示不耐煩
    eyeLookUpRight: 0.3,    // 新增：眼睛向上看表示不耐煩
  },
  sleepy: {
    eyeBlinkLeft: 1.5,      // 增強到1.5（原值0.9）
    eyeBlinkRight: 1.5,     // 增強到1.5（原值0.9）
    jawOpen: 0.5,           // 增強到0.5（原值0.25）
    browInnerUp: 0.1,       // 增強到0.1（原值0.05）
    headTilt: 0.3,          // 新增：頭部微傾表示困倦
  },
  scheming: { // Mischievous, plotting
    mouthSmileLeft: 0.9,    // 增強到0.9（原值0.45）
    mouthSmileRight: 0.2,   // 增強到0.2（原值0.1）
    browDownRight: 0.7,     // 增強到0.7（原值0.35）
    browDownLeft: 0.2,      // 增強到0.2（原值0.1）
    eyeSquintLeft: 0.9,     // 增強到0.9（原值0.55）
    eyeSquintRight: 0.9,    // 增強到0.9（原值0.55）
    noseSneerLeft: 0.3,     // 增強到0.3（原值0.15）
  },
  determined: {
    browDownLeft: 1.2,      // 增強到1.2（原值0.6）
    browDownRight: 1.2,     // 增強到1.2（原值0.6）
    mouthPressLeft: 1.4,    // 增強到1.4（原值0.7）
    mouthPressRight: 1.4,   // 增強到1.4（原值0.7）
    jawForward: 0.4,        // 增強到0.4（原值0.2）
    eyeSquintLeft: 0.6,     // 增強到0.6（原值0.3）
    eyeSquintRight: 0.6,    // 增強到0.6（原值0.3）
  },
  impatient: {
    browDownLeft: 0.8,      // 增強到0.8（原值0.4）
    browDownRight: 0.8,     // 增強到0.8（原值0.4）
    mouthPressLeft: 1.0,    // 增強到1.0（原值0.5）
    mouthPressRight: 1.0,   // 增強到1.0（原值0.5）
    cheekPuff: 0.3,         // 增強到0.3（原值0.15）
    eyeSquintLeft: 0.3,     // 新增：眼睛微眯表示不耐煩
    eyeSquintRight: 0.3,    // 新增：眼睛微眯表示不耐煩
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
  smug: { // Self-satisfied, perhaps slightly contemptuous smile
    mouthSmileLeft: 0.6,    // 增強到0.6（原值0.3）
    mouthSmileRight: 0.6,   // 增強到0.6（原值0.3）
    mouthDimpleLeft: 0.4,   // 增強到0.4（原值0.2）
    mouthDimpleRight: 0.4,  // 增強到0.4（原值0.2）
    browDownLeft: 0.2,      // 增強到0.2（原值0.1）
    browDownRight: 0.2,     // 增強到0.2（原值0.1）
    eyeSquintLeft: 0.4,     // 增強到0.4（原值0.2）
    eyeSquintRight: 0.4,    // 增強到0.4（原值0.2）
    cheekSquintLeft: 0.2,   // 增強到0.2（原值0.1）
    cheekSquintRight: 0.2,  // 增強到0.2（原值0.1）
    jawLeft: 0.15,          // 新增：微微偏頭
  },
  awe: { // Wonder, amazement
    eyeWideLeft: 1.4,       // 增強到1.4（原值0.7）
    eyeWideRight: 1.4,      // 增強到1.4（原值0.7）
    mouthOpen: 0.6,         // 增強到0.6（原值0.3）
    jawOpen: 0.6,           // 增強到0.6（原值0.3）
    browInnerUp: 0.4,       // 增強到0.4（原值0.2）
    browOuterUpLeft: 0.8,   // 增強到0.8（原值0.4）
    browOuterUpRight: 0.8,  // 增強到0.8（原值0.4）
  },
  doubtful: { // Questioning, uncertain
    browInnerUp: 1.0,       // 增強到1.0（原值0.5）
    browOuterUpLeft: 0.4,   // 增強到0.4（原值0.2）
    mouthPucker: 0.4,       // 增強到0.4（原值0.2）
    mouthLeft: 0.2,         // 增強到0.2（原值0.1）
    headTilt: 0.2,          // 新增：頭部微微傾斜
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