# Animation Blending Strategy

This document describes the interpolation based animation blending implemented for the body model. When switching animations, the system computes intermediate frames between the previously playing loop and the next keyframe animation.

## Approach

1. **Manual Interpolation** – When a transition is triggered, the current and next `AnimationAction` objects are stored in a transition state.
2. **Per‑Frame Update** – Using `useFrame`, the blend weight is updated each frame. A cubic easing function controls the weight from 0→1 for the new action while the old action fades out.
3. **Loop Handling** – The loop mode of the next animation is preserved. Non‑looping clips clamp on the last frame.

This technique removes visible freezes by ensuring the skeleton poses interpolate smoothly during the blend period.
