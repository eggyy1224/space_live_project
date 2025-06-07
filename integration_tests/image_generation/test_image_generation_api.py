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
    payload = {"description": "simple test pattern"}
    response = requests.post(ENDPOINT, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    filename = data["url"].split("/generated-images/")[-1]
    assert os.path.exists(os.path.join(IMAGE_DIR, filename))


async def test_websocket_notification():
    async with websockets.connect(WS_URL) as ws:
        requests.post(ENDPOINT, json={"description": "ws image"})
        message = await asyncio.wait_for(ws.recv(), timeout=10)
        data = json.loads(message)
        assert data.get("type") == "generated-image"
        assert "url" in data


if __name__ == "__main__":
    test_generate_image_api()
    asyncio.run(test_websocket_notification())
