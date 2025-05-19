# Realtime Conversation Channel

This document sketches the design of an experimental realtime audio channel. The
feature allows holding a microphone button to stream user audio to the backend
and receive speech from the assistant in realtime.

## Backend

- New websocket endpoint `/ws/realtime` defined in
  `prototype/backend/api/endpoints/realtime.py`.
- The endpoint currently proxies audio frames to OpenAI's upcoming realtime API
  using `openai.AsyncOpenAI`. Returned audio frames are streamed back to the
  client. The implementation is a placeholder and should be adapted once the
  official API is final.

## Frontend

- New service `RealTimeService` manages connection to `/ws/realtime` and streams
  microphone audio using `AudioService`.
- A `PushToTalkButton` component starts and stops streaming on press and release
  events.
- `App.tsx` renders this button below the existing UI.

Emotion and body animation handling continues to rely on the existing hooks
(`useEmotionalSpeaking`, `useBodyService`, etc.). Once realtime audio is
received it is played via `AudioService`, which already drives the head model's
lipsync and emotion logic.

Further integration—such as streaming emotion keyframes—is left as future work.
