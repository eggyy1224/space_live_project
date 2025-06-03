#!/usr/bin/env python3
"""End-to-end test for the emotion trajectory endpoint.

The API should broadcast an `emotionalTrajectory` message so the frontend
updates the avatar's emotions accordingly.
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
    start = time.time()
    while time.time() - start < timeout:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout - (time.time() - start))
            data = json.loads(msg)
            if data.get("type") == expected:
                return data
        except asyncio.TimeoutError:
            pass
    return None


async def main() -> None:
    async with websockets.connect(WS_URL) as ws:
        print("🚀 Testing /emotion-trajectory")
        # Expected: frontend animates along the given emotional keyframes
        payload = {
            "duration": 2.0,
            "keyframes": [
                {"time": 0, "emotion": "neutral"},
                {"time": 1, "emotion": "happy"},
            ],
        }
        requests.post(f"{API_BASE}/api/control/emotion-trajectory", json=payload)
        data = await wait_for_type(ws, "emotionalTrajectory")
        assert data, "No emotionalTrajectory message received"
        print("✅ emotionalTrajectory:", data)


if __name__ == "__main__":
    asyncio.run(main())
