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
        print("🚀 Testing BGM control with Space Live theme")
        # Expected: frontend starts playing the specified BGM
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmUrl": "/audio/BGM/spacelive_theme.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("bgmUrl"), "No BGM message received"
        print("✅ BGM message:", data)
        print("⏳ Playing BGM for 8 seconds...")
        time.sleep(8)

        print("\n🚀 Testing BGM change to country theme")
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmUrl": "/audio/BGM/space_live_country_theme1.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("bgmUrl"), "No BGM message received"
        print("✅ BGM change message:", data)
        print("⏳ Playing new BGM for 6 seconds...")
        time.sleep(6)

        print("\n🚀 Testing SFX - Taiwan variety show sound")
        # Expected: frontend plays the given sound effect
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("sfxUrl"), "No SFX message received"
        print("✅ SFX message:", data)
        print("⏳ Playing SFX for 4 seconds...")
        time.sleep(4)

        print("\n🚀 Testing SFX - Spaceship ambience")
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("sfxUrl"), "No SFX message received"
        print("✅ Spaceship ambience SFX:", data)
        print("⏳ Playing ambient SFX for 5 seconds...")
        time.sleep(5)

        print("\n🚀 Testing heavy metal BGM")
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3"},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data and data.get("bgmUrl"), "No heavy metal BGM message received"
        print("✅ Heavy metal BGM:", data)
        print("⏳ Playing heavy metal for 7 seconds...")
        time.sleep(7)

        print("\n🚀 Testing quick SFX succession")
        for i in range(1, 4):
            print(f"  🔊 Playing test SFX {i}")
            requests.post(
                f"{API_BASE}/api/control/background-audio",
                json={"sfxUrl": f"/audio/effects/測試音效{i}.mp3"},
            )
            data = await wait_for_type(ws, "audio-control")
            assert data and data.get("sfxUrl"), f"No test SFX {i} message received"
            print(f"  ✅ Test SFX {i}:", data)
            time.sleep(2)

        print("\n🚀 Testing BGM stop (method 1: empty URL)")
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmUrl": ""},  # Empty URL should stop BGM
        )
        data = await wait_for_type(ws, "audio-control")
        assert data, "No BGM stop message received"
        print("✅ BGM stop message (empty URL):", data)
        print("⏳ Pausing after BGM stop...")
        time.sleep(3)

        print("\n🚀 Testing BGM pause (method 2: bgmPlaying=false)")
        # First start another BGM
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmUrl": "/audio/BGM/spacelive_theme2.mp3"},
        )
        await wait_for_type(ws, "audio-control")  # Wait for start
        time.sleep(2)
        
        # Then pause it
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmPlaying": False},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data, "No BGM pause message received"
        print("✅ BGM pause message:", data)
        print("⏳ Pausing after BGM pause...")
        time.sleep(3)

        print("\n🚀 Testing BGM resume")
        requests.post(
            f"{API_BASE}/api/control/background-audio",
            json={"bgmPlaying": True},
        )
        data = await wait_for_type(ws, "audio-control")
        assert data, "No BGM resume message received"
        print("✅ BGM resume message:", data)
        print("⏳ Playing resumed BGM for 3 seconds...")
        time.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
