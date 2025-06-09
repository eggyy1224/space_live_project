#!/usr/bin/env python3
"""Integration tests for the image generation endpoint."""

import asyncio
import json
import os
import time

import requests
import websockets

API_BASE = "http://localhost:8000"
ENDPOINT = f"{API_BASE}/api/generate-image"
WS_URL = "ws://localhost:8000/ws"
IMAGE_DIR = "prototype/backend/generated_images"


def test_generate_image_api():
    payload = {"description": "simple test pattern", "duration": 1.5, "aspect_ratio": "square"}
    response = requests.post(ENDPOINT, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    filename = data["url"].split("/generated-images/")[-1]
    assert os.path.exists(os.path.join(IMAGE_DIR, filename))
    assert data.get("duration") == 1.5
    assert data.get("aspect_ratio") == "square"


async def test_websocket_notification():
    async with websockets.connect(WS_URL) as ws:
        requests.post(ENDPOINT, json={"description": "ws image", "duration": 2, "aspect_ratio": "portrait"})
        message = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(message)
        assert data.get("type") == "generated-image"
        assert "url" in data
        assert data.get("duration") == 2
        assert data.get("aspect_ratio") == "portrait"


if __name__ == "__main__":
    test_generate_image_api()
    asyncio.run(test_websocket_notification())
