#!/usr/bin/env python3
"""End-to-end test for the background audio endpoint.

Verifies that background music and sound effect commands reach the frontend via
`audio-control` WebSocket messages.
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
        print("🚀 Testing BGM control")
        # Expected: frontend starts playing the specified BGM
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmUrl": "/songs-file/電子音樂.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("bgmUrl"), "No BGM message received"
        print("✅ BGM message:", data)

        print("\n🚀 Testing SFX control")
        # Expected: frontend plays the given sound effect
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"sfxUrl": "/songs-file/暴龍吼叫.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("sfxUrl"), "No SFX message received"
        print("✅ SFX message:", data)


if __name__ == "__main__":
    asyncio.run(main())
