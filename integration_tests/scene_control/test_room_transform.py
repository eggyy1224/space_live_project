#!/usr/bin/env python3
"""Integration tests for room transform functionality."""

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
        print("🏠 Testing room transform functionality")
        
        # 初始化：確保房間顯示
        print("🎬 Initializing: Show default room")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "sceneName": "6面房間"
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        print("✅ room initialized:", data)
        
        # 角色介紹測試
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "歡迎來到房間變換測試！"})
        print("   ⏳ Character introduction...")
        time.sleep(4.0)
        print()
        
        # 測試位置變換
        print("🚀 Testing room position transform")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "現在測試位置變換！"})
        time.sleep(4.0)
        
        print("   → Moving room to position [1.0, 2.0, 3.0]...")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "sceneName": "6面房間",
                "position": [1.0, 2.0, 3.0]
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        assert data and data.get("payload", {}).get("position") == [1.0, 2.0, 3.0]
        print("✅ room position:", data)
        
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "看到了嗎？房間移動了！"})
        print("   ⏳ Observe the position change...")
        time.sleep(5.0)

        # 測試旋轉變換
        print("🚀 Testing room rotation transform")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "接下來測試旋轉功能！"})
        time.sleep(4.0)
        
        print("   → Rotating room [30°, 45°, 60°]...")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "rotation": [30.0, 45.0, 60.0]
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        assert data and data.get("payload", {}).get("rotation") == [30.0, 45.0, 60.0]
        print("✅ room rotation:", data)
        
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "房間旋轉了！很酷吧？"})
        print("   ⏳ Observe the rotation...")
        time.sleep(5.0)

        # 測試縮放變換 (統一縮放)
        print("🚀 Testing room uniform scale")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "現在測試縮放功能！"})
        time.sleep(4.0)
        
        print("   → Scaling room uniformly to 2.0x...")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "scale": [2.0]
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        assert data and data.get("payload", {}).get("scale") == [2.0, 2.0, 2.0]
        print("✅ room uniform scale:", data)
        
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "房間變大了！"})
        print("   ⏳ Observe the uniform scaling...")
        time.sleep(5.0)

        # 測試縮放變換 (分別縮放)
        print("🚀 Testing room individual scale")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "接下來試試不等比例縮放！"})
        time.sleep(4.0)
        
        print("   → Scaling room to [1.5x, 2.0x, 0.8x]...")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "scale": [1.5, 2.0, 0.8]
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        assert data and data.get("payload", {}).get("scale") == [1.5, 2.0, 0.8]
        print("✅ room individual scale:", data)
        
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "房間變形了！很特別對吧？"})
        print("   ⏳ Observe the non-uniform scaling...")
        time.sleep(5.0)

        # 測試組合變換
        print("🚀 Testing combined transform")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "最後測試組合變換！"})
        time.sleep(4.0)
        
        print("   → Switching to 6面房間A with combined transforms...")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "sceneName": "6面房間A",
                "position": [-1.0, 0.5, 2.0],
                "rotation": [0.0, 90.0, 0.0],
                "scale": [1.2, 1.2, 1.2]
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        payload = data.get("payload", {})
        assert payload.get("sceneName") == "6面房間A"
        assert payload.get("position") == [-1.0, 0.5, 2.0]
        assert payload.get("rotation") == [0.0, 90.0, 0.0]
        assert payload.get("scale") == [1.2, 1.2, 1.2]
        print("✅ combined transform:", data)
        
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "太棒了！組合變換完成！"})
        print("   ⏳ Observe the combined effect...")
        time.sleep(6.0)

        # 測試錯誤處理 - 無效位置
        print("🚀 Testing invalid position")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "position": [1.0, 2.0]  # 只有兩個值
            },
        )
        assert resp.status_code == 400, "Expected 400 for invalid position"
        print("✅ invalid position rejected")

        # 測試錯誤處理 - 無效縮放
        print("🚀 Testing invalid scale")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "scale": [-1.0, 2.0, 1.0]  # 負值
            },
        )
        assert resp.status_code == 400, "Expected 400 for negative scale"
        print("✅ negative scale rejected")

        # 重置為預設狀態
        print("🔄 Resetting to default")
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "現在重置房間到原始狀態！"})
        time.sleep(4.0)
        
        print("   → Resetting room to default state...")
        resp = requests.post(
            f"{API_BASE}/api/control/scene-display",
            json={
                "displayScene": True,
                "sceneName": "6面房間",
                "position": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [2.0, 2.0, 2.0]
            },
        )
        assert resp.status_code == 200, f"Unexpected status {resp.status_code}"
        data = await wait_for_type(ws, "scene-display")
        print("✅ reset to default:", data)
        
        requests.post(f"{API_BASE}/api/control/send-message", json={"content": "完美！房間變換測試全部完成！謝謝觀看！"})
        print("   ⏳ Final state observation...")
        time.sleep(6.0)
        print("🎉 Room transform test completed!")


if __name__ == "__main__":
    asyncio.run(main()) 