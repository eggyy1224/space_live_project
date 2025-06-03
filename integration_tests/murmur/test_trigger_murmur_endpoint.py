#!/usr/bin/env python3
"""End-to-end test for the trigger-murmur endpoint.

Calling this API should broadcast a `trigger-murmur` message so the frontend
starts a murmuring sequence.
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
        print("🚀 Testing trigger-murmur")
        # Expected: frontend shows murmur text and audio about the topic
        requests.post(
            f"{API_BASE}/api/control/trigger-murmur",
            json={"topic": "loneliness", "force": True},
        )
        data = await wait_for_type(ws, "trigger-murmur")
        assert data, "No trigger-murmur message received"
        print("✅ trigger-murmur:", data)


if __name__ == "__main__":
    asyncio.run(main())
