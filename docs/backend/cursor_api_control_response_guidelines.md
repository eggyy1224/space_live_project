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
- `image_generation.py` – AI image generation using Gemini models.

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
|`POST`|`/api/control/camera/set-frontend-preset`|Command frontend to switch to a named camera preset.|
|`POST`|`/api/control/body-animation`|Control body animation states.|
|`POST`|`/api/control/head-size`|Adjust the scale of the head model (0.1 to 20.0).|
|`POST`|`/api/control/scene-display`|Toggle or change the active 3D scene.|
|`POST`|`/api/control/character/scale`|Set character scale (0.1 to 3.0).|
|`POST`|`/api/control/character/position`|Set character position [x, y, z].|
|`POST`|`/api/control/character/rotation`|Set character rotation [x, y, z] in radians.|
|`POST`|`/api/control/character/outfit`|Control character outfit morph targets (outfit_shoes030_1 etc.).|
|`POST`|`/api/control/character/animation`|Set character animation.|
|`POST`|`/api/control/character/visibility`|Toggle character visibility.|
|`POST`|`/api/control/character/reset-transform`|Reset character transform (position, rotation, scale).|
|`GET`|`/api/control/character/status`|Get current character status.|
|`POST`|`/api/control/environment/preset`|Set environment lighting preset.|
|`POST`|`/api/control/environment/intensity`|Set environment lighting intensity (0.1-3.0).|
|`POST`|`/api/control/environment/background`|Toggle environment background display.|
|`POST`|`/api/control/environment/config`|Batch set environment lighting configuration.|
|`POST`|`/api/control/environment/reset`|Reset environment lighting to default values.|
|`GET`|`/api/control/environment/status`|Get current environment lighting status.|

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

### Image Generation Endpoints
| Method | Path | Description |
|-------|------|-------------|
|`POST`|`/api/generate-image`|Generate an AI image using Gemini 2.0 Flash Preview Image Generation model and broadcast via WebSocket.|

### System Endpoint
| Method | Path | Description |
|-------|------|-------------|
|`GET`|`/api/health`|Return a simple service health status.|

### WebSocket
A websocket endpoint at `/ws` provides real-time conversation handling. It manages queues and playback acknowledgements. Murmur generation now only occurs when explicitly commanded by the frontend or API.

## Mapping User Instructions
1. **Direct control commands** – map explicit directives such as "play this audio", "set camera angle", or "switch to overview camera" to the corresponding control endpoint (e.g., `/api/control/camera/set-frontend-preset` for named camera views).
2. **Monitor operations** – interpret requests about changing monitor visibility, content or volume and call the monitor endpoints.
3. **Speech processing** – when users supply audio to convert or ask for generated speech, use the speech endpoints.
4. **Image generation requests** – when users ask for image generation or want to create visual content, use the `/api/generate-image` endpoint.
5. **Status queries** – requests for availability or connection information should call `/api/control/status` or `/api/health`.
6. **Unstructured chat** – route open conversation through the websocket endpoint.

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
  "animation": "string (Required, animation name from character model, e.g., 'Tpose', '舞步1', '運動1')",
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

**8. Set Frontend Camera Preset (`/api/control/camera/set-frontend-preset`)**
```json
{
  "name": "string (Required, preset name, e.g., 'overview', 'closeup')",
  "duration": "float (Optional, transition duration in seconds, default: 5.0)"
}
```

**9. Character Scale (`/api/control/character/scale`)**
```json
{
  "scale": "float (Required, scale factor 0.1 to 15.0)"
}
```

**10. Character Position (`/api/control/character/position`)**
```json
{
  "position": "array (Required, [x, y, z] coordinates)"
}
```

**11. Character Rotation (`/api/control/character/rotation`)**
```json
{
  "rotation": "array (Required, [x, y, z] rotation angles in radians)"
}
```

**12. Character Outfit (`/api/control/character/outfit`)**
```json
{
  "outfit_morphs": "object (Required, morph target names and values 0.0-1.0, e.g., {'鍵 1': 0.8, '錯置': 0.5})"
}
```

**13. Character Animation (`/api/control/character/animation`)**
```json
{
  "animation": "string (Required, animation name from CHARACTER_ANIMATIONS)",
  "loop": "boolean (Optional, true to loop, default: true)",
  "speed": "float (Optional, playback speed multiplier, default: 1.0)"
}
```

**14. Character Visibility (`/api/control/character/visibility`)**
```json
{
  "visible": "boolean (Required, true to show, false to hide)"
}
```

**15. Character Reset Transform (`/api/control/character/reset-transform`)**
```json
{
  "reset_position": "boolean (Optional, default: true)",
  "reset_rotation": "boolean (Optional, default: true)",
  "reset_scale": "boolean (Optional, default: true)"
}
```

**16. Head Size Control (`/api/control/head-size`)**
```json
{
  "scaleFactor": "float (Scale multiplier for head model, range: 0.1 to 20.0, required. 1.0 = normal size, 2.0 = double size, 0.5 = half size)"
}
```

**17. Scene Display Control (`/api/control/scene-display`)**
```json
{
  "displayScene": "boolean (Whether to show or hide the 3D scene, required)",
  "sceneName": "string (Optional, scene ID to load. Available: '6面房間', '6面房間A')",
  "position": "array (Optional, room position [x, y, z] coordinates in 3D space)",
  "rotation": "array (Optional, room rotation [x, y, z] in degrees)",
  "scale": "array (Optional, room scale [x, y, z] or [uniform] for equal scaling, must be positive)"
}
```

**18. Image Generation (`/api/generate-image`)**
```json
{
  "description": "string (Text description of the image to generate, required. Can be in Chinese or English. Examples: '一隻可愛的橘貓在花園裡', 'a beautiful sunset over mountains')",
  "position": "string (Optional, position preset: 'center-right'(default), 'center-left', 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center')",
  "size": "string (Optional, size preset: 'small', 'medium'(default), 'large')",
  "custom_position": "object (Optional, custom CSS position properties, overrides 'position'. Example: {'top': '50%', 'right': '50px', 'transform': 'translateY(-50%)'})",
  "custom_size": "object (Optional, custom CSS size properties, overrides 'size'. Example: {'width': '400px', 'height': '300px'})",
  "duration": "number (Optional, display duration in seconds, default: 10.0)",
  "aspect_ratio": "string (Optional, image aspect ratio: 'square', 'portrait', 'landscape')"
}
```

**19. Show Existing Image (`/api/show-existing-image`)**
```json
{
  "filename": "string (Required, image filename in generated_images directory. Example: 'image_1749309153863.png')",
  "caption": "string (Optional, display caption text, default: '現有圖片')",
  "position": "string (Optional, position preset: 'center'(default), 'center-left', 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center-right')",
  "size": "string (Optional, size preset: 'small', 'medium', 'large'(default))",
  "custom_position": "object (Optional, custom CSS position properties, overrides 'position'. Example: {'top': '15%', 'right': '300px'})",
  "custom_size": "object (Optional, custom CSS size properties, overrides 'size'. Example: {'width': '500px', 'height': '400px'})",
  "duration": "number (Optional, display duration in seconds, default: 15.0)",
  "aspect_ratio": "string (Optional, aspect ratio hint for display: 'square', 'portrait', 'landscape'(default))"
}
```

**20. Take Selfie (`/api/take-selfie`)**
```json
{
  "description": "string (Optional, selfie description, default: '拍一張自拍照')",
  "reference_image": "string (Optional, reference image filename from selfies/ or generated_images/ directory. Example: 'selfie_1749441340870.png')",
  "modification": "string (Optional, modification instructions. Example: '換個開心的表情', '變成比較酷的眼神')",
  "use_latest_selfie": "boolean (Optional, auto-use latest selfie as reference, default: false)",
  "position": "string (Optional, position preset: 'center'(default), 'center-left', 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center-right')",
  "size": "string (Optional, size preset: 'small', 'medium', 'large'(default))",
  "custom_position": "object (Optional, custom CSS position properties, overrides 'position')",
  "custom_size": "object (Optional, custom CSS size properties, overrides 'size')",
  "duration": "number (Optional, display duration in seconds, default: 15.0)",
  "aspect_ratio": "string (Optional, aspect ratio: 'square', 'portrait'(default), 'landscape')",
  "add_timestamp": "boolean (Optional, add timestamp watermark to image, default: true)"
}
```

**21. Continue Selfie (`/api/continue-selfie`)**
```json
{
  "modification": "string (Optional, modification instructions, default: '稍微改變一下表情和姿勢')",
  "position": "string (Optional, position preset: 'center'(default), 'center-left', 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center-right')",
  "size": "string (Optional, size preset: 'small', 'medium', 'large'(default))",
  "duration": "number (Optional, display duration in seconds, default: 20.0)"
}
```

**22. Environment Preset (`/api/control/environment/preset`)**
```json
{
  "preset": "string (Required, environment preset name. Options: 'studio', 'sunset', 'dawn', 'night', 'warehouse', 'forest', 'apartment', 'city', 'park', 'lobby')"
}
```

**23. Environment Intensity (`/api/control/environment/intensity`)**
```json
{
  "intensity": "float (Required, lighting intensity value, range: 0.1 to 3.0. 1.0 = normal intensity, 2.0 = double brightness, 0.5 = half brightness)"
}
```

**24. Environment Background (`/api/control/environment/background`)**
```json
{
  "background": "boolean (Required, true to show environment as background, false to hide background)"
}
```

**25. Environment Config (`/api/control/environment/config`)**
```json
{
  "preset": "string (Optional, environment preset name)",
  "intensity": "float (Optional, lighting intensity 0.1-3.0)",
  "background": "boolean (Optional, background display toggle)"
}
```

**26. Environment Reset (`/api/control/environment/reset`)**
```json
{
  "reset_to_defaults": "boolean (Optional, default: true. Reset all environment settings to default values)"
}
```

**Image Generation & Show Existing Image Response:**
```json
{
  "success": "boolean (true if generation/display succeeded)",
  "url": "string (Relative URL path to the image, e.g., '/generated-images/image_1234567890.png')",
  "caption": "string (AI-generated description or custom caption text)",
  "display_config": "object (Configuration for frontend display positioning and sizing)",
  "duration": "number (Display duration in seconds)",
  "aspect_ratio": "string (Image aspect ratio: 'square', 'portrait', 'landscape')"
}
```

**Position Presets:**
- `center-right` (default): Middle right, vertically centered
- `center-left`: Middle left, vertically centered  
- `top-right`: Top right corner
- `top-left`: Top left corner
- `bottom-right`: Bottom right corner
- `bottom-left`: Bottom left corner
- `center`: Absolute center of screen

**Size Presets:**
- `small`: 250px × 200px
- `medium` (default): 350px × 280px
- `large`: 450px × 360px

**Image Display & Access:**
- Generated images are automatically saved to `prototype/backend/generated_images/` directory
- Images are accessible via HTTP at `http://localhost:8000{url}` (e.g., `http://localhost:8000/generated-images/image_1234567890.png`)
- Both generated and existing images are broadcasted via WebSocket to connected frontends with message type `generated-image`
- Frontend `ImageOverlay` component can display multiple images simultaneously, each with independent positioning, sizing, and duration
- **Multiple identical images**: The same image file can be displayed multiple times simultaneously at different positions and sizes
- **Image persistence**: Images remain visible for their specified `duration` before automatically disappearing

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

9.  **Give TTS Enough Time to Speak! (Crucial for `send-message`)**
    -   The `send-message` command is non-blocking. This means the script or control flow will continue immediately after the command is sent, *not* after the Text-to-Speech (TTS) has finished speaking.
    -   You **MUST** use `sleep` (or equivalent pauses in your control logic) to allow sufficient time for the character to actually say the entire `content`.
    -   For longer sentences, this `sleep` duration needs to be correspondingly longer. The `duration` field in a paired `emotion-trajectory` can be a hint, but the actual TTS length can vary. **When in doubt, provide a more generous `sleep` duration.** Insufficient sleep will result in speech being cut off.
    -   **Example from a working script (`meta_self.sh`):** A scene with a moderately long sentence, emotion, camera transition, and BGM change was allocated a `sleep 17` at the end of its command block to ensure everything, especially the full speech, completed before the next scene began.

10. **Pace Your Commands, Especially Around TTS.**
    -   Avoid firing off a dense burst of commands immediately after a `send-message`, especially if that speech is critical.
    -   If a `send-message` is followed by many other visual or audio commands, the TTS might get "swamped" or its initiation might fail.
    -   **Consider adding short `sleep` pauses (e.g., `sleep 0.5` to `sleep 2.0`) immediately after `send-message` and its paired `emotion-trajectory` *before* a rapid sequence of other commands.** This gives the TTS system a moment to initialize.
    -   Also, ensure that complex scenes have fully resolved (with adequate `sleep` at the end of their command block) before initiating new scenes, especially new `send-message` commands. This prevents a backlog or resource contention on the frontend/backend.

11. **Validate Frontend Preset Names:**
    -   When using `/api/control/camera/set-frontend-preset`, ensure the `name` provided corresponds to a camera preset defined in the frontend's configuration (e.g., in `prototype/frontend/src/config/resources.ts`). Sending an unknown preset name will likely result in no camera change or an error/warning on the frontend side.
    -   Refer to `docs/backend/camera_control_api.md` for a list of known presets populated from the frontend configuration.

12. **Head Size Effects for Storytelling:**
    -   Use head scaling (`scaleFactor` range: 0.1 to 20.0) for dramatic and comedic effects. Normal size is 1.0.
    -   **Dramatic emphasis**: Scale 1.5-3.0x during important speeches or emotional moments.
    -   **Comedy/surreal effects**: Use extreme scales (0.2x tiny, 5.0x+ huge) for visual gags.
    -   **Gradual transitions**: Change head size progressively (e.g., 1.0 → 1.5 → 2.0 → 1.0) for smooth effects.
    -   Always consider returning to normal size (1.0) unless maintaining the effect is intentional.

13. **Room/Scene Transformation for Visual Impact:**
    -   **Position**: Use `[x, y, z]` coordinates to move rooms. Negative values move in opposite directions.
    -   **Rotation**: Specify in degrees `[x, y, z]`. Use Y-axis rotation (middle value) for left/right turning.
    -   **Scale**: Single value `[2.0]` for uniform scaling, or three values `[x, y, z]` for distortion effects.
    -   **Scene switching**: Available scenes are "6面房間" and "6面房間A". Can combine with transforms.
    -   **Hiding scenes**: Use `"displayScene": false` to completely hide the 3D environment.
    -   **Reset transforms**: Use `[0, 0, 0]` for position/rotation and `[1, 1, 1]` for scale to return to defaults.

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

**Example 4: Command Frontend to Switch Camera Preset**
```bash
# This tells the frontend to use its own 'side_view' preset definition,
# with a 2-second transition.
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset \\
  -H "Content-Type: application/json" \\
  -d '{"name": "side_view", "duration": 2.0}'
```

**Example 5: Head Size Control for Dramatic Effects**
```bash
# Make the head larger for emphasis
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 2.5}'

# Make the head smaller for a cute effect
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 0.7}'

# Return to normal size
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'
```

**Example 6: Scene Display Control**
```bash
# Show the main 6-sided room scene
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": true, "sceneName": "6面房間"}'

# Switch to room A variant
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": true, "sceneName": "6面房間A"}'

# Hide the scene completely
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": false}'
```

**Example 7: Room Transform Control (Position, Rotation, Scale)**
```bash
# Basic room positioning
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": true, "position": [1.0, 2.0, 3.0]}'

# Rotate room 90 degrees on Y-axis
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": true, "rotation": [0.0, 90.0, 0.0]}'

# Scale room uniformly to 1.5x size
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": true, "scale": [1.5]}'

# Scale room differently on each axis (create distortion effects)
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": true, "scale": [2.0, 1.0, 0.8]}'

# Combine multiple transformations with scene switching
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{
    "displayScene": true,
    "sceneName": "6面房間A",
    "position": [-1.0, 0.5, 2.0],
    "rotation": [0.0, 90.0, 0.0],
    "scale": [1.2, 1.2, 1.2]
  }'

# Hide room completely
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{"displayScene": false}'

# Reset room to default transforms
curl -X POST http://localhost:8000/api/control/scene-display \
  -H "Content-Type: application/json" \
  -d '{
    "displayScene": true,
    "sceneName": "6面房間",
    "position": [0.0, 0.0, 0.0],
    "rotation": [0.0, 0.0, 0.0],
    "scale": [1.0, 1.0, 1.0]
  }'
```

**Example 8: Head Size Control for Visual Effects**
```bash
# Enlarge head for dramatic emphasis (2.5x size)
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 2.5}'

# Shrink head for cute or humorous effect (0.7x size)
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 0.7}'

# Extremely large head for comedic effect (5.0x size)
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 5.0}'

# Tiny head for surreal effect (0.3x size)
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 0.3}'

# Return to normal size
curl -X POST http://localhost:8000/api/control/head-size \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'
```

**Example 9: AI Image Generation**
```bash
# Basic image generation (default: center-right, medium)
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "一隻可愛的橘貓在花園裡玩耍"}'

# Position control - left side, large size
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "台灣辣妹在太空夜市吃小籠包", "position": "center-left", "size": "large"}'

# Position control - top corner, small size
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "迷你太空機器人修理衛星", "position": "top-right", "size": "small"}'

# Center large image for dramatic effect
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"description": "銀河中央的太空女王跳舞", "position": "center", "size": "large"}'

# Custom positioning and sizing
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空花園裡的蝴蝶仙子",
    "custom_position": {"bottom": "30px", "left": "30px"},
    "custom_size": {"width": "300px", "height": "400px"}
  }'

# Multiple position presets available:
# - center-right (default): Middle right, vertically centered
# - center-left: Middle left, vertically centered
# - top-right, top-left: Corner positions
# - bottom-right, bottom-left: Bottom corner positions  
# - center: Absolute center (dramatic effect)

# Size presets: small (250x200), medium (350x280), large (450x360)
# Custom sizes and positions override presets

# Note: Generated images will automatically appear in the frontend ImageOverlay
# with the specified position, size, and appropriate entrance animation
```

## 🎬 Director's Cut: The Art of the 3-Command Combo (導演進階：三連擊的藝術)

While individual API calls are powerful, the true art of directing lies in weaving them into a seamless narrative. Since most API calls are **non-blocking** (they return `success` immediately, without waiting for the action to complete), crafting complex scenes requires a method to control timing and order.

The most effective way to do this is with a **Command Sequence**, and the foundational building block of any good sequence is the **3-Command Combo**. While longer chains are possible, thinking in terms of 3-step, cause-and-effect combos is the key to creating clear and impactful moments.

**The Philosophy: Action → Reaction → Emphasis**
A "3-Command Combo" typically follows this narrative structure:
1.  **Action:** An event occurs. (e.g., a sound is heard)
2.  **Reaction:** The character reacts to the event. (e.g., their body language changes)
3.  **Emphasis:** The camera moves to highlight the reaction. (e.g., a close-up on the character's face)

**The Tools:**
-   `curl -X ...`: Your API command.
-   `&&`: The "AND" operator. It links commands, ensuring the next one runs only if the previous one was successful.
-   `sleep <seconds>`: The key to pacing. It pauses execution for a specified duration to create a natural rhythm between actions.

**Example: The "Sudden Noise" Combo**

This is a classic directorial combo. A sudden noise grabs the character's attention, they react, and the camera immediately focuses on them to capture their expression. This creates a powerful, focused moment of drama.

```bash
# This 3-Command Combo creates a classic "What was that?" moment.
# 1. (Action) Play a sharp, attention-grabbing sound.
# 2. (Reaction) Character looks around in surprise.
# 3. (Emphasis) Camera zooms in on the character.

curl -X POST http://localhost:8000/api/control/play-audio -H "Content-Type: application/json" -d '{"url": "/audio/effects/taiwan_variety_sfx_01.mp3", "interrupt": true}' && \
sleep 0.5 && \
curl -X POST http://localhost:8000/api/control/body-animation -H "Content-Type: application/json" -d '{"animation": "LookAround"}' && \
sleep 0.2 && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "head_close_up", "duration": 0.8}'
```
Mastering the 3-Command Combo is the key to unlocking a higher level of narrative direction. It places the power of pacing and choreography firmly in the hands of you, the director, allowing you to build complex scenes from clear, effective, and manageable blocks.

## 🎭 Staging a Full Scene: From Combos to Choreography (編排長戲：從三連擊到完整編舞)

A single combo creates a moment; a series of linked combos creates a **scene**. To build a longer, more engaging experience, we must learn to choreograph these combos into a sequence that tells a story.

A well-structured scene follows a simple narrative arc:
1.  **Opening:** An initial command or combo to set the stage and establish the baseline mood.
2.  **Development:** One or more combos that build on the opening, introducing conflict or new information. This is where the story unfolds.
3.  **Climax:** The peak of the scene—the most dramatic combo that serves as the turning point.
4.  **Closing:** A final command or a moment of `sleep` to let the impact of the climax sink in, before transitioning to the next scene.

By thinking in these four parts, you can transform simple building blocks into a compelling narrative sequence.

**Full Scene Example: "The Anomaly"**

This scene demonstrates how to link combos to tell a story of discovery and shock.

```bash
# Scene: The Anomaly
# A full scene built from multiple command combos, telling a short story.

# Part 1: Opening - Establish the routine
# A single command to set a calm, neutral stage.
echo "### SCENE START: The Anomaly ###" && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "overview", "duration": 2.5}' && \
curl -X POST http://localhost:8000/api/control/body-animation -H "Content-Type: application/json" -d '{"animation": "Idle", "loop": true}' && \
sleep 3 && \

# Part 2: Development - The first sign of trouble (A 3-Command Combo)
echo "### COMBO 1: The Discovery ###" && \
curl -X PUT http://localhost:8000/api/monitors/screen1 -H "Content-Type: application/json" -d '{"content": "/videos/太空瑜伽.mp4", "visible": true, "playing": true}' && \
sleep 1 && \
curl -X POST http://localhost:8000/api/control/body-animation -H "Content-Type: application/json" -d '{"animation": "LookAround"}' && \
sleep 0.5 && \
curl -X POST http://localhost:8000/api/control/camera/transition -H "Content-Type: application/json" -d '{"pitch": 5, "yaw": -5, "roll": 0, "fov": 70, "duration": 2.0}' && \
sleep 4 && \

# Part 3: Climax - The shocking escalation (A 3-Command Combo)
echo "### COMBO 2: The Shock ###" && \
curl -X POST http://localhost:8000/api/control/play-audio -H "Content-Type: application/json" -d '{"url": "/songs-file/暴龍吼叫.mp3", "interrupt": true}' && \
sleep 0.1 && \
curl -X POST http://localhost:8000/api/control/emotion-trajectory -H "Content-Type: application/json" -d '{"duration": 2, "keyframes": [{"tag": "fear", "proportion": 0.0}]}' && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "head_close_up", "duration": 0.5}' && \

# Part 4: Closing - Let the shock register
echo "### SCENE END ###" && \
sleep 5
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
    4.  **Insufficient `sleep` / Speech Cut Off?** If speech starts but gets cut off, the `sleep` duration in your script after the `send-message` (or the block of commands containing it) is likely too short. The script moves on before TTS completes. Increase the `sleep` time to match or exceed the actual speaking duration.
    5.  **Speech Not Heard At All (Especially in Dense Command Sequences)?** If a `send-message` seems to produce no audio, especially when followed quickly by many other commands (camera, other audio, monitors):
        *   Ensure the "Golden Rule" (Speech + Emotion back-to-back) is followed.
        *   Try adding a slightly longer `sleep` (e.g., 1-2 seconds) immediately after the `send-message` / `emotion-trajectory` pair *before* any subsequent rapid-fire commands. This can give the TTS system crucial time to initialize.
        *   Ensure the previous scene or command block had enough `sleep` time to fully complete, preventing system overload when the new `send-message` is issued.

-   **Head Size Control Not Working?**
    1.  **Character Visible?** Make sure character is speaking or animated so you can see the size change.
    2.  **Valid Range?** `scaleFactor` must be between 0.1 and 20.0.
    3.  **Frontend Implementation?** Ensure WebSocket message handling includes `head-size` type.
    4.  **Gradual Changes?** Try extreme values (like 0.3 or 5.0) to make changes more obvious.

-   **Scene Display Not Changing?**
    1.  **Valid Scene Name?** Currently available: "6面房間", "6面房間A".
    2.  **File Exists?** Check that `.glb` files exist in `prototype/frontend/public/scenes/`.
    3.  **Frontend Support?** Ensure frontend has implemented scene switching functionality.
    4.  **`displayScene: true`?** Must be true to show any scene.

-   **Image Generation Not Working?**
    1.  **API Key Set?** Ensure `GOOGLE_API_KEY` is properly configured in backend environment.
    2.  **Description Field?** The request must include a `description` field with text content.
    3.  **Model Access?** Verify access to Gemini 2.0 Flash Preview Image Generation model.
    4.  **Backend Logs?** Check for detailed error messages about image generation failures.
    5.  **Frontend Not Showing Images?** Check if `ImageOverlay` component is properly mounted in `App.tsx`.
    6.  **Image File Access?** Verify that generated images are accessible at `http://localhost:8000/generated-images/`.
    7.  **WebSocket Connection?** Images are broadcast via WebSocket, ensure frontend is connected.
    8.  **Static File Serving?** Confirm `/generated-images/` static route is mounted in backend `__init__.py`.
    9.  **Position/Size Not Working?** Check `display_config` in WebSocket message and frontend style application.
    10. **Invalid Position/Size Values?** Ensure position presets match: 'center-right', 'center-left', 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'center'. Size presets: 'small', 'medium', 'large'.
    11. **Custom CSS Not Applied?** Verify `custom_position` and `custom_size` objects contain valid CSS properties.
    12. **Animation Issues?** Check frontend CSS classes for proper animation based on position (left/right/center).

-   **Environment Lighting Not Working?**
    1.  **Invalid Preset Name?** Ensure preset is one of: 'studio', 'sunset', 'dawn', 'night', 'warehouse', 'forest', 'apartment', 'city', 'park', 'lobby'.
    2.  **Intensity Out of Range?** Intensity must be between 0.1 and 3.0.
    3.  **Frontend Support?** Verify frontend has Environment component from @react-three/drei properly configured.
    4.  **WebSocket Message Handling?** Check frontend WebSocket listener for environment message types: 'environment-preset', 'environment-intensity', 'environment-background', 'environment-config', 'environment-reset'.
    5.  **Store State Update?** Ensure frontend store (Zustand) properly updates environment settings when WebSocket messages are received.
    6.  **Three.js Rendering?** Verify Environment component is rendered in SceneContainer with proper Canvas settings.
    7.  **No Visual Changes?** Some environment changes may be subtle - try extreme values (intensity 0.2 vs 2.5) to see difference.
    8.  **Background Not Showing?** Ensure Canvas has proper `gl` settings and environment intensity > 0.
    9.  **Preset Changes Not Visible?** Different presets may look similar depending on scene lighting - try contrasting presets like 'night' vs 'sunset'.
    10. **Reset Not Working?** Default values are: preset='studio', intensity=1.0, background=false.

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

### Generated Images (automatically created by AI - use `/generated-images/` prefix)
-   Images are dynamically generated using Gemini 2.0 Flash Preview Image Generation
-   File naming pattern: `image_{timestamp}.png` (e.g., `image_1749308094327.png`)
-   Typical resolutions: 1024x684 pixels
-   Format: PNG with RGB color space
-   Storage location: `prototype/backend/generated_images/`
-   Accessible via: `http://localhost:8000/generated-images/{filename}`
-   Frontend display: Shown in `ImageOverlay` component for the backend-provided `duration` (default 10 seconds)
-   WebSocket broadcast: Images are broadcasted with type `generated-image` including URL, caption, and display_config
-   Position control: 7 preset positions (center-right default) plus custom positioning
-   Size control: 3 preset sizes (medium default) plus custom sizing
-   Animation support: Different entrance animations based on position (slide from right/left, fade for center)
-   Display config: Backend controls frontend positioning via `display_config` object in WebSocket message

### Scripts (executable bash scripts - use script names directly)
-   `meta_self.sh` - 《伊始之眼：一個導演的誕生》元戲劇腳本
-   `remix_scene.sh` - 音樂與場景混合劇本
-   `space_story_script.sh` - 太空故事腳本
-   `news_broadcast.sh` - 新聞播報劇本

## 🎬 Script Execution API

The Script Execution API allows you to execute predefined bash scripts that orchestrate complex virtual astronaut performances. These scripts combine multiple API calls into choreographed sequences.

### List Available Scripts
```bash
curl -X GET "http://localhost:8000/api/scripts/list"
```

### Execute a Script (Background Mode)
```bash
curl -X POST "http://localhost:8000/api/scripts/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "meta_self.sh",
    "background": true
  }'
```

### Execute a Script (Synchronous Mode)
```bash
curl -X POST "http://localhost:8000/api/scripts/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script_name": "meta_self.sh",
    "background": false
  }'
```

### Check Script Execution Status
```bash
curl -X GET "http://localhost:8000/api/scripts/status"
```

### Stop Running Script
```bash
curl -X POST "http://localhost:8000/api/scripts/stop/meta_self.sh"
```

**Script Execution Modes:**
- **Background Mode** (recommended): Script runs independently, API returns immediately
- **Synchronous Mode**: API waits for script completion before responding (use for shorter scripts only)

**Safety Features:**
- Only registered scripts can be executed
- Scripts run in isolated processes
- Built-in process management and cleanup
- Graceful termination with fallback to force-kill if needed
