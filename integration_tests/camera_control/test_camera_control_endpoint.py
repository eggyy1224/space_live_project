#!/usr/bin/env python3
"""End-to-end tests for the camera control API.

Each request triggers a WebSocket message that updates the camera on the
frontend. The script checks those messages to verify the observable effect.
"""

import asyncio
import json
import time
from typing import Any, Dict

import requests
import websockets

API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"


async def wait_for_type(ws: websockets.WebSocketClientProtocol, expected: str, timeout: float = 5.0) -> Dict[str, Any] | None:
    """Wait for a message of the given type."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout - (time.time() - start))
            data = json.loads(message)
            if data.get("type") == expected:
                return data
        except asyncio.TimeoutError:
            pass
    return None


async def main() -> None:
    async with websockets.connect(WS_URL) as ws:
        print("\n🚀 Testing /camera/set-angle")
        # Expected: frontend camera instantly snaps to these angles
        requests.post(f"{API_BASE}/api/control/camera/set-angle", json={"pitch": 30, "yaw": 45, "roll": 0})
        data = await wait_for_type(ws, "camera-angle")
        assert data, "No camera-angle message received"
        print("✅ camera-angle:", data)
        print("⏳ Pausing to observe instant angle change...")
        time.sleep(2)

        print("\n🚀 Testing /camera/transition")
        # Expected: camera smoothly transitions over 6 seconds
        requests.post(
            f"{API_BASE}/api/control/camera/transition",
            json={"pitch": -20, "yaw": -30, "roll": 15, "duration": 6},
        )
        data = await wait_for_type(ws, "camera-transition")
        assert data, "No camera-transition message received"
        print("✅ camera-transition:", data)
        print("⏳ Waiting for 6-second transition to complete...")
        time.sleep(6)

        print("\n🚀 Testing preset save/load")
        # Expected: loading the preset moves the camera using stored angles
        requests.post(
            f"{API_BASE}/api/control/camera/save-preset",
            json={"name": "test-preset", "pitch": 15, "yaw": 30, "roll": 0},
        )
        requests.post(
            f"{API_BASE}/api/control/camera/load-preset",
            params={"name": "test-preset", "duration": 5},
        )
        data = await wait_for_type(ws, "camera-transition")
        assert data and data.get("payload", {}).get("pitch") == 15, "Preset not applied"
        print("✅ preset loaded:", data)
        print("⏳ Waiting for 5-second preset transition to complete...")
        time.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
