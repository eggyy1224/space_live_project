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

## Asset Paths for Understanding
To help Cursor better understand and utilize project assets, here are some key paths:

-   **BGM + Sound Effects**: `prototype/frontend/public/audio`
-   **Animations**: `prototype/shared/config/animations.json`
-   **`play_audio` (songs file)**: `prototype/backend/songs`
-   **Monitor Switching Materials**: `prototype/frontend/public/videos`

## ⚠️ Critical Path & Data Specifications

### Audio & Video File URL Formats
**IMPORTANT**: Different asset sources use different URL prefixes. Using the wrong prefix will result in playback failure.

| Asset Type             | Physical Path Root                 | API URL Prefix | Example Request Body (for `play-audio` or `background-audio`)          | Example for Monitor (`currentVideo`) |
|------------------------|------------------------------------|----------------|----------------------------------------------------------------------|---------------------------------------|
| BGM / Sound Effects    | `prototype/frontend/public/audio/` | `/audio/`        | `{"bgmUrl": "/audio/BGM/spacelive_theme.mp3"}`                     | N/A                                   |
| Songs for `play_audio` | `prototype/backend/songs/`         | `/songs-file/`   | `{"url": "/songs-file/暴龍吼叫.mp3"}`                                 | N/A                                   |
| Monitor Videos         | `prototype/frontend/public/videos/`| `/videos/`       | N/A                                                                  | `{"content": "/videos/太空直播中.mp4"}` (Request uses 'content') |

**Common Path Mistakes:**
-   ❌ **WRONG**: `/songs/filename.mp3` (This prefix is for a different static mount, will likely fail for `play_audio`)
-   ✅ **CORRECT for `play_audio`**: `/songs-file/filename.mp3`
-   ❌ **WRONG**: `/audio-file/BGM/music.mp3` (Incorrect prefix for BGM/SFX)
-   ✅ **CORRECT for BGM/SFX**: `/audio/BGM/music.mp3`

### Emotion Trajectory Data Format
**CRITICAL for natural expression.**
```json
{
  "duration": "float (seconds, total duration of the trajectory, required)",
  "keyframes": [
    {
      "tag": "string (emotion name, e.g., 'happy', 'surprised', required)",
      "proportion": "float (0.0 to 1.0, point in the timeline for this keyframe, required)"
    }
    // Add more keyframes as needed
  ]
}
```
**Common Emotion Data Mistakes:**
-   ❌ **WRONG**: `{"time": 2.0, "emotion": "happy", "intensity": 0.8}` (Outdated/incorrect keys)
-   ✅ **CORRECT**: `{"tag": "happy", "proportion": 0.5}` (Uses correct `tag` and `proportion`)

### Request Body Formats (Key Endpoints)

**1. Send Message (`/api/control/send-message`)**
```json
{
  "content": "string (The text to be spoken, required)",
  "message_type": "string (Optional, e.g., 'chat-message', defaults if omitted)"
}
```

**2. Emotion Trajectory (`/api/control/emotion-trajectory`)**
```json
{
  "duration": "float (seconds, required)",
  "keyframes": [ {"tag": "string", "proportion": "float"} ] // See detailed format above
}
```

**3. Play Audio (`/api/control/play-audio`)**
```json
{
  "url": "string (Full path using correct prefix, e.g., /songs-file/your_song.mp3, required)",
  "interrupt": "boolean (Optional, true to interrupt current audio, default false)"
}
```

**4. Background Audio (`/api/control/background-audio`)**
```json
{
  "bgmUrl": "string (Optional, e.g., /audio/BGM/theme.mp3, use empty string \"\" to stop BGM)",
  "sfxUrl": "string (Optional, e.g., /audio/effects/effect.mp3)",
  "bgmPlaying": "boolean (Optional, true to play/resume, false to pause BGM)"
}
```

**5. Camera Transition (`/api/control/camera/transition`)**
```json
{
  "pitch": "float (degrees, required)",
  "yaw": "float (degrees, required)", 
  "roll": "float (degrees, required)",
  "fov": "float (Optional, field of view in degrees)",
  "duration": "float (seconds for transition, default: 1.0, required)"
}
```

**6. Body Animation (`/api/control/body-animation`)**
```json
{
  "state": "string (Optional, e.g., 'play', 'stop', default: 'play')",
  "animation": "string (Required, animation name from animations.json, e.g., 'Idle', 'Happy')",
  "loop": "boolean (Optional, true to loop, default: model's setting or false)",
  "speed": "float (Optional, playback speed multiplier, default: 1.0)"
}
```

**7. Monitor Update (`PUT /api/monitors/{id}`)**
```json
{
  "content": "string (Optional, e.g., /videos/your_video.mp4, use correct prefix for video path)",
  "visible": "boolean (Optional)",
  "playing": "boolean (Optional, for video playback)",
  "volume": "float (Optional, 0.0 to 1.0, for video volume)"
}
```

## 🎉 Best Practices for a Smooth Show! 🎉

1.  **Always Verify Connection Status First!**
    -   Before sending any commands, especially at the start of a sequence, call `GET /api/control/status` to ensure there's an active frontend connection. If `active_connections` is 0, commands won't be received.

2.  **Master Your Asset Paths!**
    -   Refer to the **Audio & Video File URL Formats** table. Using the wrong prefix (e.g., `/songs/` instead of `/songs-file/` for `play_audio`) is a common source of errors.

3.  **⚠️ THE GOLDEN RULE: Speech & Emotion are a DUO! ⚠️**
    -   **`send-message` (Speech) and `emotion-trajectory` (Emotion) commands MUST be sent back-to-back, as a single, indivisible unit.** Think of it as: "Character says X *while feeling* Y."
    -   **Order**: `send-message` first, then *IMMEDIATELY* `emotion-trajectory`.
    -   **Why?** `send-message` triggers TTS and prepares lip-sync. The emotion must start at the *exact same time* as the speech for natural, synchronized expression. Any delay will cause the character to speak with a neutral/previous emotion initially, or have emotions play on a silent face.
    -   **Emotions are only visually effective when the character is speaking (TTS is active).**

4.  **Be a Smart Director: Orchestrate Your Effects!**
    -   Plan your sequences. The Speech+Emotion DUO is your core. Build around it.
    -   **Example Flow**: `(send-message + emotion-trajectory)` → *brief natural pause (scripted)* → `play-audio` (sound effect) → `body-animation` → `camera/transition`.
    -   Avoid overwhelming the frontend: Don't fire off dozens of commands in rapid succession without allowing time for each to render and play out.

5.  **Data Formats are Key!**
    -   Double-check your JSON payloads against the **Request Body Formats** section. Incorrect field names or data types are common issues (`422 Unprocessable Entity` errors often point to this).

6.  **Handle Errors Gracefully.**
    -   Pay attention to API responses. If a command fails, the response often contains clues in the `detail` field.

7.  **Test Individual Components & Sequences.**
    -   If a complex sequence isn't working, break it down. Test each API call individually first.

8.  **Monitor Backend Logs for Deeper Clues.**
    -   Logs can provide more detailed error information if an API call behaves unexpectedly.

##🎬 Working Examples: Bringing it All Together

**Example 1: The CORE - Synchronized Speech & Emotion (CRITICAL!)**
```bash
# Step 1: Character Speaks (this initiates TTS and lip-sync)
curl -X POST http://localhost:8000/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{"content": "大家好！今天天氣真好，心情非常愉快！"}'

# Step 2: IMMEDIATELY Follow with Emotion for Perfect Sync
curl -X POST http://localhost:8000/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{"duration": 5.0, "keyframes": [{"tag": "happy", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}'
```

**Example 2: Adding a Sound Effect & Animation**
```bash
# (Assuming Speech + Emotion from Example 1 just happened or is happening)
# Wait for a natural pause in speech or after a key phrase, then...

# Play a sound effect (e.g., a cheerful chime)
curl -X POST http://localhost:8000/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/your_cheerful_chime.mp3"}' # Replace with actual file

# Trigger a relevant body animation
curl -X POST http://localhost:8000/api/control/body-animation \
  -H "Content-Type: application/json" \
  -d '{"animation": "Cheering", "loop": false}'
```

**Example 3: Scene Change with Background Music, Camera, and Monitor**
```bash
# Start background music
curl -X POST http://localhost:8000/api/control/background-audio \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true}'

# Transition camera to a new view
curl -X POST http://localhost:8000/api/control/camera/transition \
  -H "Content-Type: application/json" \
  -d '{"pitch": 10, "yaw": -20, "roll": 0, "fov": 75, "duration": 2.5}'

# Update a monitor with a new video
curl -X PUT http://localhost:8000/api/monitors/screen1 \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/太空瑜伽.mp4", "visible": true, "playing": true, "volume": 0.8}'
```

## 🔍 Troubleshooting Common Issues

-   **Audio Not Playing?**
    1.  **Wrong URL Prefix?** Double-check the **Audio & Video File URL Formats** table. (`/songs-file/` for `play_audio`, `/audio/` for BGM/SFX).
    2.  **File Exists?** Ensure the audio file is present at the correct physical path on the server.
    3.  **API Response?** Successful `play-audio` call should return `{"success":true, ...}`.

-   **Video Not Showing on Monitor?**
    1.  **Wrong URL Prefix?** Use `/videos/`.
    2.  **Correct Request Key?** Ensure you are using `"content": "/videos/your_video.mp4"` in your PUT request body.
    3.  **Monitor ID Correct?** (`screen1`, `screen2`, etc.)
    4.  **`visible: true`?** Ensure the monitor is set to be visible.
    5.  **`playing: true`?** (If you want it to autoplay).

-   **Emotions Not Syncing / Character Looks Neutral While Talking?**
    1.  **GOLDEN RULE VIOLATED?** `send-message` and `emotion-trajectory` *MUST* be sent back-to-back. Any significant delay breaks synchronization.
    2.  **Is Character Actually Speaking?** Emotions only apply visually during active TTS/speech.
    3.  **`emotion-trajectory` Payload Correct?** Check `duration` and `keyframes` format (`tag`, `proportion`).

-   **TTS (Text-to-Speech) Not Working?**
    1.  **`content` Field Empty?** The `send-message` request needs text in the `content` field.
    2.  **Active Connection?** (See Best Practice #1).
    3.  **Backend Logs?** Check for errors from the TTS service.

## ✅ Response Validation Guide

-   **Successful Calls Generally Return:** `{"success": true, ...}`. Specific endpoints might include additional data (e.g., `url` for `play-audio`, `connections` for `send-message`).
-   **Common HTTP Error Statuses:**
    -   `200 OK`: Success.
    -   `404 Not Found`: Often for incorrect monitor IDs or non-existent camera presets.
    -   `422 Unprocessable Entity`: Usually means your JSON request body is malformed or has incorrect data types. Check against **Request Body Formats**.
    -   `500 Internal Server Error`: A problem on the server side. Check backend logs.
    -   `503 Service Unavailable`: Often means no active frontend WebSocket connections for control commands.

## 📚 Available Assets Reference (Examples - Verify in your project)

*This is a sample list. Always check your project's actual asset directories.* 

### Songs (for `play_audio` - use `/songs-file/` prefix)
-   `暴龍吼叫.mp3`
-   `電子音樂.mp3`
-   `歌劇1.mp3`

### BGM & SFX (for `background-audio` - use `/audio/` prefix)
-   `BGM/spacelive_theme.mp3`
-   `effects/taiwan_variety_sfx_01.mp3`

### Animations (use exact names from `prototype/shared/config/animations.json`)
-   `Idle`, `Happy`, `Cheering`, `LookAround`, `Flair`, `FemaleStandingPose`, `FemaleDynamicPose`, `InjuredWalk`

### Videos (for Monitors - use `/videos/` prefix)
-   `太空直播中.mp4`
-   `太空瑜伽.mp4`
-   `模擬星雲圖.mp4`
