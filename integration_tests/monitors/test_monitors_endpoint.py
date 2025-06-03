#!/usr/bin/env python3
"""End-to-end test for the monitors (video screens) endpoint.

Tests video screen management, including listing monitors, updating monitor state,
playing videos, and WebSocket state synchronization.
"""

import asyncio
import json
import time
from typing import Any, Dict

import requests
import websockets

API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

# 測試用的視頻檔案（從 video_resources.py 中選取）
TEST_VIDEOS = [
    "/videos/太空熱舞.mp4",
    "/videos/太空瑜伽.mp4", 
    "/videos/星際小可愛.mp4",
    "/videos/太空直播中.mp4",
    "/videos/黑洞.mp4"
]

MONITOR_IDS = ["screen1", "screen2", "screen3"]


async def wait_for_type(ws: websockets.WebSocketClientProtocol, expected: str, timeout: float = 5.0) -> Dict[str, Any] | None:
    """等待特定類型的 WebSocket 消息"""
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
        print("🚀 測試場景 1: 獲取所有螢幕狀態")
        # 測試獲取所有監控器狀態
        response = requests.get(f"{API_BASE}/api/monitors")
        assert response.status_code == 200, f"獲取監控器列表失敗: {response.status_code}"
        monitors = response.json()
        assert len(monitors) == 3, f"期望3個監控器，實際{len(monitors)}個"
        print(f"✅ 成功獲取 {len(monitors)} 個監控器狀態")
        for monitor in monitors:
            print(f"  📺 {monitor['id']}: 可見={monitor['visible']}, 播放中={monitor['playing']}")
        print("⏳ 等待 2 秒...")
        time.sleep(2)

        print("\n🚀 測試場景 2: 獲取單個螢幕狀態")
        # 測試獲取單個監控器狀態
        monitor_id = "screen1"
        response = requests.get(f"{API_BASE}/api/monitors/{monitor_id}")
        assert response.status_code == 200, f"獲取 {monitor_id} 狀態失敗: {response.status_code}"
        monitor_state = response.json()
        assert monitor_state["id"] == monitor_id, f"監控器ID不匹配: {monitor_state['id']}"
        print(f"✅ 成功獲取 {monitor_id} 狀態: {monitor_state}")
        print("⏳ 等待 2 秒...")
        time.sleep(2)

        print("\n🚀 測試場景 3: 在 screen1 播放太空熱舞視頻")
        # 測試在 screen1 播放視頻
        payload = {
            "content": TEST_VIDEOS[0],  # 太空熱舞.mp4
            "visible": True
        }
        response = requests.put(f"{API_BASE}/api/monitors/screen1", json=payload)
        assert response.status_code == 200, f"更新 screen1 失敗: {response.status_code}"
        updated_state = response.json()
        assert updated_state["currentVideo"] == TEST_VIDEOS[0], "視頻路徑設定錯誤"
        assert updated_state["visible"] == True, "可見性設定錯誤" 
        assert updated_state["playing"] == True, "播放狀態設定錯誤"
        print(f"✅ screen1 開始播放: {TEST_VIDEOS[0]}")
        
        # 等待並檢查 WebSocket 消息
        data = await wait_for_type(ws, "director-state")
        assert data, "未收到 director-state WebSocket 消息"
        video_screens = data.get("payload", {}).get("videoScreens", [])
        assert len(video_screens) == 3, "WebSocket 中的視頻螢幕數量不正確"
        print("✅ WebSocket 狀態同步成功")
        print("⏳ 播放視頻 8 秒...")
        time.sleep(8)

        print("\n🚀 測試場景 4: 在 screen2 播放瑜伽視頻（調整音量和播放速度）")
        # 測試多參數更新
        payload = {
            "content": TEST_VIDEOS[1],  # 太空瑜伽.mp3
            "visible": True,
            "volume": 0.7,
            "playbackSpeed": 1.5
        }
        response = requests.put(f"{API_BASE}/api/monitors/screen2", json=payload)
        assert response.status_code == 200, f"更新 screen2 失敗: {response.status_code}"
        updated_state = response.json()
        assert updated_state["currentVideo"] == TEST_VIDEOS[1], "視頻路徑設定錯誤"
        assert updated_state["volume"] == 0.7, "音量設定錯誤"
        assert updated_state["playbackRate"] == 1.5, "播放速度設定錯誤"
        print(f"✅ screen2 開始播放: {TEST_VIDEOS[1]} (音量=70%, 速度=1.5x)")
        
        # 檢查 WebSocket 更新
        data = await wait_for_type(ws, "director-state")
        assert data, "未收到 director-state WebSocket 消息"
        print("✅ WebSocket 狀態同步成功")
        print("⏳ 播放視頻 6 秒...")
        time.sleep(6)

        print("\n🚀 測試場景 5: 同時在多個螢幕播放不同視頻")
        # 測試多螢幕同時播放
        test_configs = [
            ("screen1", TEST_VIDEOS[2], 0.8, 1.0),  # 星際小可愛
            ("screen2", TEST_VIDEOS[3], 0.9, 0.75), # 太空直播中
            ("screen3", TEST_VIDEOS[4], 1.0, 2.0)   # 黑洞
        ]
        
        for monitor_id, video, volume, speed in test_configs:
            payload = {
                "content": video,
                "visible": True,
                "volume": volume,
                "playbackSpeed": speed
            }
            response = requests.put(f"{API_BASE}/api/monitors/{monitor_id}", json=payload)
            assert response.status_code == 200, f"更新 {monitor_id} 失敗: {response.status_code}"
            print(f"✅ {monitor_id} 播放: {video.split('/')[-1]} (音量={volume*100}%, 速度={speed}x)")
            
            # 等待 WebSocket 消息
            data = await wait_for_type(ws, "director-state")
            assert data, f"未收到 {monitor_id} 的 WebSocket 消息"
            time.sleep(1)  # 避免消息混亂
        
        print("⏳ 多螢幕同時播放 10 秒...")
        time.sleep(10)

        print("\n🚀 測試場景 6: 測試螢幕控制功能（隱藏/顯示）")
        # 測試隱藏螢幕
        for monitor_id in ["screen1", "screen2"]:
            payload = {"visible": False}
            response = requests.put(f"{API_BASE}/api/monitors/{monitor_id}", json=payload)
            assert response.status_code == 200, f"隱藏 {monitor_id} 失敗: {response.status_code}"
            updated_state = response.json()
            assert updated_state["visible"] == False, f"{monitor_id} 可見性設定錯誤"
            assert updated_state["playing"] == False, f"{monitor_id} 應該停止播放"
            print(f"✅ {monitor_id} 已隱藏並停止播放")
            
            data = await wait_for_type(ws, "director-state")
            assert data, f"未收到 {monitor_id} 隱藏的 WebSocket 消息"
            time.sleep(1)
        
        print("⏳ 等待 3 秒觀察只有 screen3 在播放...")
        time.sleep(3)

        print("\n🚀 測試場景 7: 測試錯誤處理")
        # 測試無效的監控器ID
        response = requests.get(f"{API_BASE}/api/monitors/invalid_screen")
        assert response.status_code == 404, f"期望404錯誤，實際: {response.status_code}"
        print("✅ 無效監控器ID 正確返回 404 錯誤")
        
        # 測試無效的視頻檔案
        payload = {"content": "/videos/nonexistent_video.mp4"}
        response = requests.put(f"{API_BASE}/api/monitors/screen1", json=payload)
        assert response.status_code == 400, f"期望400錯誤，實際: {response.status_code}"
        error_response = response.json()
        assert "Unknown content id" in error_response["detail"], "錯誤訊息不正確"
        print("✅ 無效視頻檔案 正確返回 400 錯誤")
        
        # 測試無效的播放速度
        payload = {"playbackSpeed": 10.0}  # 超出範圍 (0.25-4.0)
        response = requests.put(f"{API_BASE}/api/monitors/screen1", json=payload)
        assert response.status_code == 400, f"期望400錯誤，實際: {response.status_code}"
        print("✅ 無效播放速度 正確返回 400 錯誤")
        
        # 測試無效的音量
        payload = {"volume": 1.5}  # 超出範圍 (0.0-1.0)
        response = requests.put(f"{API_BASE}/api/monitors/screen1", json=payload)
        assert response.status_code == 400, f"期望400錯誤，實際: {response.status_code}"
        print("✅ 無效音量 正確返回 400 錯誤")

        print("\n🚀 測試場景 8: 重置所有螢幕狀態")
        # 清理：隱藏所有螢幕
        for monitor_id in MONITOR_IDS:
            payload = {"visible": False}
            response = requests.put(f"{API_BASE}/api/monitors/{monitor_id}", json=payload)
            assert response.status_code == 200, f"重置 {monitor_id} 失敗: {response.status_code}"
            print(f"✅ {monitor_id} 已重置")
            
            data = await wait_for_type(ws, "director-state")
            assert data, f"未收到 {monitor_id} 重置的 WebSocket 消息"

        print("\n🎉 所有螢幕監控器測試完成！總測試時間約 45 秒")
        
        # 最終狀態檢查
        response = requests.get(f"{API_BASE}/api/monitors")
        final_monitors = response.json()
        all_hidden = all(not monitor["visible"] for monitor in final_monitors)
        assert all_hidden, "部分螢幕未正確重置"
        print("✅ 所有螢幕已成功重置為隱藏狀態")


if __name__ == "__main__":
    asyncio.run(main()) 