# Background Image Control Integration Tests

## Overview
This directory contains integration tests for the background image generation and control functionality.

## Test Coverage

### API Endpoints
- `POST /api/generate-background-image` - Generate new background images
- `POST /api/set-background-image` - Switch to existing background images
- `POST /api/disable-background-image` - Disable background images

### WebSocket Events
- `background-image-generated` - New background image generated
- `background-image-changed` - Background image changed or disabled

### Test Cases
1. **Background Image Generation**
   - Generate background with specific aspect ratio (16:9)
   - Verify file creation in frontend directory
   - Validate response data structure

2. **Existing Background Control**
   - Switch to predefined backgrounds (`outerspace1.png`, etc.)
   - Handle non-existent background files (404 error)
   - Disable background images

3. **WebSocket Integration**
   - Receive generation notifications
   - Receive background change notifications
   - Validate event data structure

4. **Error Handling**
   - Missing required parameters
   - Invalid file references
   - Network timeouts

## Available Background Images

### Predefined
- `outerspace1.png` - Deep space scene with stars
- `outerspace2.png` - Cosmic nebula view
- `outerspace3.png` - Galaxy cluster background

### Generated Format
- `background_[timestamp].png` - AI generated backgrounds

## Running Tests

### Prerequisites
- Backend server running on `localhost:8000`
- WebSocket connection available at `ws://localhost:8000/ws`
- Required Python packages: `requests`, `websockets`

### Execution
```bash
# From prototype directory
cd integration_tests/background_image_control
python3 test_background_image_api.py
```

### Expected Output
```
🚀 Starting background image control integration tests...

🧪 Testing background image generation...
✅ Background image generated: background_1750322123885.png

🧪 Testing setting existing background...
✅ Successfully set existing background

🧪 Testing background disable...
✅ Successfully disabled background

📡 Testing WebSocket functionality...

🧪 Testing WebSocket notification for background generation...
✅ Received WebSocket notification: background_1750322439708.png

🎉 All background image control tests passed!

📊 Test Summary:
   Generated backgrounds: background_1750322123885.png, background_1750322439708.png
   Predefined backgrounds tested: outerspace1.png
   API endpoints tested: 3
   WebSocket events tested: 1
```

## API Usage Examples

### Generate Background
```bash
curl -X POST "http://localhost:8000/api/generate-background-image" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Beautiful deep space scene with nebulae",
    "aspect_ratio": "16:9"
  }'
```

### Set Background
```bash
curl -X POST "http://localhost:8000/api/set-background-image" \
  -H "Content-Type: application/json" \
  -d '{"filename": "outerspace1.png"}'
```

### Disable Background
```bash
curl -X POST "http://localhost:8000/api/disable-background-image"
```

## File Structure
```
integration_tests/background_image_control/
├── README.md                        # This file
└── test_background_image_api.py     # Main test script
```

## Dependencies
- Python 3.7+
- requests
- websockets
- asyncio (built-in)
- json (built-in)
- os (built-in) 