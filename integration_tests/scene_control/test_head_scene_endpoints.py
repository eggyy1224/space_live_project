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
        # First, send a message to make character visible for head size testing
        print("🎬 Making character visible for testing")
        resp = requests.post(
            f"{API_BASE}/api/control/send-message", 
            json={"content": "開始進行頭部大小控制測試！"}
        )
        assert resp.status_code == 200, "Failed to send initial message"
        time.sleep(0.5)  # Brief pause for message to process
        
        print("🚀 Testing head-size normal value (1.5x)")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "現在要測試1.5倍頭部大小～"})
        time.sleep(2.0)  # Wait for character to appear and speak
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 1.5}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 1.5, "WebSocket head-size mismatch"
        print("✅ head-size 1.5x:", data)

        print("🚀 Testing head-size large value (5.0x)")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "哇！接下來是5倍大的頭部！"})
        time.sleep(2.0)  # Wait for character to appear and speak
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 5.0}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 5.0, "WebSocket head-size mismatch"
        print("✅ head-size 5.0x:", data)

        print("🚀 Testing head-size maximum value (20.0x)")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "準備好了嗎？最大20倍巨大頭部來了！"})
        time.sleep(2.0)  # Wait for character to appear and speak
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 20.0}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 20.0, "WebSocket head-size mismatch"
        print("✅ head-size 20.0x (maximum):", data)

        print("🚀 Testing head-size small value (0.3x)")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "現在變成小頭模式，0.3倍大小"})
        time.sleep(2.0)  # Wait for character to appear and speak
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 0.3}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 0.3, "WebSocket head-size mismatch"
        print("✅ head-size 0.3x (small):", data)

        print("🚀 Testing head-size minimum value (0.1x)")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "最小模式！頭部縮到0.1倍，幾乎看不見了"})
        time.sleep(2.0)  # Wait for character to appear and speak
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 0.1}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 0.1, "WebSocket head-size mismatch"
        print("✅ head-size 0.1x (minimum):", data)

        # Reset to normal size
        print("🔄 Resetting to normal size")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "測試完成！恢復正常大小"})
        time.sleep(2.0)  # Wait for character to appear and speak
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 1.0}
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "head-size")
        assert data and data.get("scaleFactor") == 1.0, "WebSocket head-size mismatch"
        print("✅ head-size reset to normal (1.0x):", data)

        print("🚀 Testing head-size invalid negative")
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": -1}
        )
        assert resp.status_code == 400, "Expected 400 for invalid scale"
        print("✅ invalid negative head-size rejected")

        print("🚀 Testing head-size invalid too large (21.0x)")
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 21.0}
        )
        assert resp.status_code == 400, "Expected 400 for scale > 20"
        print("✅ invalid large head-size rejected")

        print("🚀 Testing head-size invalid zero")
        resp = requests.post(
            f"{API_BASE}/api/control/head-size", json={"scaleFactor": 0}
        )
        assert resp.status_code == 400, "Expected 400 for scale = 0"
        print("✅ invalid zero head-size rejected")

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
