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
        print("🚀 Testing simple emotion trajectory (neutral → happy)")
        # Expected: frontend animates along the given emotional keyframes
        payload = {
            "duration": 4.0,
            "keyframes": [
                {"tag": "neutral", "proportion": 0.0},
                {"tag": "happy", "proportion": 1.0},
            ],
        }
        requests.post(f"{API_BASE}/api/control/emotion-trajectory", json=payload)
        data = await wait_for_type(ws, "emotionalTrajectory")
        assert data, "No emotionalTrajectory message received"
        print("✅ emotionalTrajectory:", data)
        print("⏳ Waiting for 4-second emotion transition...")
        time.sleep(4)

        print("\n🚀 Testing complex emotion trajectory (sad → excited → serene)")
        payload = {
            "duration": 8.0,
            "keyframes": [
                {"tag": "sad", "proportion": 0.0},
                {"tag": "excited", "proportion": 0.375},  # 3/8 = 0.375
                {"tag": "serene", "proportion": 1.0},
            ],
        }
        requests.post(f"{API_BASE}/api/control/emotion-trajectory", json=payload)
        data = await wait_for_type(ws, "emotionalTrajectory")
        assert data, "No emotionalTrajectory message received"
        print("✅ emotionalTrajectory:", data)
        print("⏳ Waiting for 8-second complex emotion transition...")
        time.sleep(8)

        print("\n🚀 Testing playful emotion sequence (neutral → playful → amused)")
        payload = {
            "duration": 6.0,
            "keyframes": [
                {"tag": "neutral", "proportion": 0.0},
                {"tag": "playful", "proportion": 0.333},  # 2/6 = 0.333
                {"tag": "amused", "proportion": 1.0},
            ],
        }
        requests.post(f"{API_BASE}/api/control/emotion-trajectory", json=payload)
        data = await wait_for_type(ws, "emotionalTrajectory")
        assert data, "No emotionalTrajectory message received"
        print("✅ emotionalTrajectory:", data)
        print("⏳ Waiting for 6-second playful emotion transition...")
        time.sleep(6)

        print("\n🚀 Testing dramatic emotion change (joyful → angry)")
        payload = {
            "duration": 5.0,
            "keyframes": [
                {"tag": "joyful", "proportion": 0.0},
                {"tag": "angry", "proportion": 1.0},
            ],
        }
        requests.post(f"{API_BASE}/api/control/emotion-trajectory", json=payload)
        data = await wait_for_type(ws, "emotionalTrajectory")
        assert data, "No emotionalTrajectory message received"
        print("✅ emotionalTrajectory:", data)
        print("⏳ Waiting for 5-second dramatic emotion transition...")
        time.sleep(5)

        print("\n🚀 Testing return to neutral")
        payload = {
            "duration": 3.0,
            "keyframes": [
                {"tag": "neutral", "proportion": 1.0},
            ],
        }
        requests.post(f"{API_BASE}/api/control/emotion-trajectory", json=payload)
        data = await wait_for_type(ws, "emotionalTrajectory")
        assert data, "No emotionalTrajectory message received"
        print("✅ emotionalTrajectory:", data)
        print("⏳ Waiting for 3-second return to neutral...")
        time.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
