#!/usr/bin/env python3
"""Integration tests for head-size and scene-display endpoints."""

import asyncio
import json
import time
from typing import Any, Dict

import requests
import websockets

API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"


async def wait_for_type(
    ws: websockets.WebSocketClientProtocol, expected: str, timeout: float = 5.0
) -> Dict[str, Any] | None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            msg = await asyncio.wait_for(
                ws.recv(), timeout=timeout - (time.time() - start)
            )
            data = json.loads(msg)
            if data.get("type") == expected:
                return data
        except asyncio.TimeoutError:
            pass
    return None


async def main() -> None:
    async with websockets.connect(WS_URL) as ws:
        print("🚀 Testing head-size valid value")
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 1.5}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 1.5, "WebSocket head-size mismatch"
        print("✅ head-size:", data)

        print("🚀 Testing head-size invalid negative")
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": -1}
        )
        assert resp.status_code == 400, "Expected 400 for invalid scale"
        print("✅ invalid head-size rejected")

        print("🚀 Testing scene-display with valid scene")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={"displayScene": True, "sceneName": "6面房間"},
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        assert data and data.get("payload", {}).get("sceneName") == "6面房間"
        print("✅ scene-display:", data)

        print("🚀 Testing scene-display invalid scene")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={"displayScene": True, "sceneName": "nope"},
        )
        assert resp.status_code == 404, "Expected 404 for bad scene name"
        print("✅ invalid scene rejected")


if __name__ == "__main__":
    asyncio.run(main())
