# Cursor API Control and Response Guidelines

## Overview
This document explains how to operate the backend APIs located in `prototype/backend/api`. It lists available endpoints, describes parameters and return values, and provides guidance on interpreting user instructions and forming responses.

## File Locations
APIs are defined in `prototype/backend/api/endpoints/`:

- `control.py` – interaction controls for the frontend.
- `monitors.py` – monitor state management.
- `speech.py` – speech to text processing.
- `health.py` – service health check.
- `websocket.py` – real-time communication endpoint.

The application registers these routes in `prototype/backend/api/__init__.py`.

## API Reference
### Control Endpoints
| Method | Path | Description |
|-------|------|-------------|
|`POST`|`/api/control/send-message`|Send a message to the frontend, optionally generating TTS audio.|
|`POST`|`/api/control/trigger-murmur`|Force a self-talk sequence on the frontend.|
|`POST`|`/api/control/murmur-mode`|Enable or disable the murmur feature.|
|`POST`|`/api/control/play-audio`|Play an audio clip on the frontend.|
|`POST`|`/api/control/background-audio`|Control background music or sound effects.|
|`POST`|`/api/control/emotion-trajectory`|Send an emotional keyframe sequence.|
|`GET`|`/api/control/status`|Return current websocket connection status.|
|`POST`|`/api/control/broadcast`|Broadcast a custom message payload.|
|`POST`|`/api/control/camera/set-angle`|Set camera orientation instantly.|
|`POST`|`/api/control/camera/transition`|Smoothly transition the camera orientation.|
|`POST`|`/api/control/camera/save-preset`|Save a camera preset on the server.|
|`POST`|`/api/control/camera/load-preset`|Load a stored camera preset.|
|`POST`|`/api/control/body-animation`|Control body animation states.|

The request models for these routes are defined at the top of `control.py` and include fields such as `content`, `url`, `duration`, `keyframes`, and camera angles.

### Monitor Endpoints
| Method | Path | Description |
|-------|------|-------------|
|`GET`|`/api/monitors`|List states of all monitors.|
|`GET`|`/api/monitors/{id}`|Retrieve a single monitor state.|
|`PUT`|`/api/monitors/{id}`|Update monitor visibility, content, playback speed and volume.|

### Speech Endpoints
| Method | Path | Description |
|-------|------|-------------|
|`POST`|`/api/speech-to-text`|Upload an audio file and receive transcribed text plus a generated reply.|
|`POST`|`/api/speech-to-text/base64`|Convert base64-encoded audio to text and optional reply.|

### System Endpoint
| Method | Path | Description |
|-------|------|-------------|
|`GET`|`/api/health`|Return a simple service health status.|

### WebSocket
A websocket endpoint at `/ws` provides real-time conversation handling. It manages queues, playback acknowledgements and murmur logic.

## Mapping User Instructions
1. **Direct control commands** – map explicit directives such as "play this audio" or "set camera angle" to the corresponding control endpoint.
2. **Monitor operations** – interpret requests about changing monitor visibility, content or volume and call the monitor endpoints.
3. **Speech processing** – when users supply audio to convert or ask for generated speech, use the speech endpoints.
4. **Status queries** – requests for availability or connection information should call `/api/control/status` or `/api/health`.
5. **Unstructured chat** – route open conversation through the websocket endpoint.

## Response Generation
When an API call succeeds, include key fields from the returned JSON in natural language. For example, a successful `send-message` call should note the connection count. If an error occurs, return a concise summary of the failure and its HTTP status.

## Chaining Examples
- **Automated greeting**: call `/api/control/send-message` to send text, then `/api/control/play-audio` with the generated TTS clip URL to synchronize speech and text.
- **Changing scenes**: `/api/control/background-audio` to start music, followed by `/api/control/camera/transition` and `/api/control/body-animation` for a combined effect.
- **Monitor update**: update a screen via `PUT /api/monitors/{id}` and broadcast the new state with `/api/control/broadcast`.

## Error Handling
- Check for HTTP errors from each request and report the provided `detail` or `error` field to the user.
- If `/api/control/status` shows no active connections, inform the user that the frontend is unavailable.
- For invalid parameters, echo back which field caused the problem when possible.

These guidelines allow Cursor to map instructions to the correct API calls and craft helpful responses.
