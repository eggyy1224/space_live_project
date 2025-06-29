#!/usr/bin/env python3
"""
調試音效播放流程
"""

import requests
import json
import time
import asyncio
import websockets
from typing import Dict, Any

# 測試配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

async def monitor_websocket():
    """監聽 WebSocket 消息"""
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("🔌 WebSocket 連接成功")
            
            # 等待並顯示收到的消息
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "audio-control":
                        print(f"🎵 收到音效播放消息: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    elif "audio" in data.get("type", "").lower():
                        print(f"🎧 收到音頻相關消息: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"📨 收到其他消息: {data.get('type', 'unknown')}")
                        
                except asyncio.TimeoutError:
                    print("⏰ 等待消息超時...")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket 錯誤: {e}")

def test_generate_and_play():
    """測試生成音效並播放"""
    print("🎯 開始測試音效生成和播放流程")
    print("=" * 50)
    
    # 1. 生成音效
    print("\n📝 步驟 1: 生成音效")
    generate_payload = {
        "prompt": "測試音效 - 短促的嘟嘟聲",
        "duration_seconds": 2.0,
        "filename": "test_beep",
        "play_immediately": True
    }
    
    print(f"發送請求: {json.dumps(generate_payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/control/generate-sound-effect",
            json=generate_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 音效生成成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 2. 驗證文件路徑
            file_path = result.get("file_path")
            if file_path:
                print(f"\n📁 步驟 2: 驗證文件訪問")
                print(f"文件路徑: {file_path}")
                
                # 測試前端是否能訪問文件
                frontend_url = f"http://localhost:5173{file_path}"
                print(f"前端訪問 URL: {frontend_url}")
                
                try:
                    file_response = requests.head(frontend_url, timeout=5)
                    if file_response.status_code == 200:
                        print(f"✅ 前端可以訪問文件 (Content-Type: {file_response.headers.get('Content-Type')})")
                    else:
                        print(f"❌ 前端無法訪問文件 (HTTP {file_response.status_code})")
                except Exception as e:
                    print(f"❌ 前端文件訪問測試失敗: {e}")
                
                # 3. 手動測試音效播放
                print(f"\n🎵 步驟 3: 手動測試音效播放")
                manual_play_payload = {
                    "sfxUrl": file_path
                }
                
                print(f"發送播放請求: {json.dumps(manual_play_payload, indent=2, ensure_ascii=False)}")
                
                try:
                    play_response = requests.post(
                        f"{BASE_URL}/api/control/background-audio",
                        json=manual_play_payload,
                        timeout=10
                    )
                    
                    if play_response.status_code == 200:
                        print("✅ 音效播放請求發送成功")
                        print(f"響應: {play_response.json()}")
                    else:
                        print(f"❌ 音效播放請求失敗 (HTTP {play_response.status_code}): {play_response.text}")
                        
                except Exception as e:
                    print(f"❌ 音效播放請求失敗: {e}")
            
        else:
            print(f"❌ 音效生成失敗 (HTTP {response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ 音效生成請求失敗: {e}")

def test_existing_effect():
    """測試現有音效播放"""
    print("\n🎯 對比測試: 播放現有音效")
    print("=" * 50)
    
    existing_effect_payload = {
        "sfxUrl": "/audio/effects/警告音1.mp3"
    }
    
    print(f"發送現有音效播放請求: {json.dumps(existing_effect_payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/control/background-audio",
            json=existing_effect_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 現有音效播放請求發送成功")
            print(f"響應: {response.json()}")
        else:
            print(f"❌ 現有音效播放請求失敗 (HTTP {response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ 現有音效播放請求失敗: {e}")

async def main():
    """主函數"""
    print("🚀 開始音效播放調試")
    print("=" * 50)
    
    # 啟動 WebSocket 監聽
    websocket_task = asyncio.create_task(monitor_websocket())
    
    # 等待一下讓 WebSocket 連接建立
    await asyncio.sleep(1)
    
    # 在另一個線程中運行測試
    import threading
    
    def run_tests():
        time.sleep(2)  # 等待 WebSocket 準備好
        test_generate_and_play()
        time.sleep(3)  # 等待一下
        test_existing_effect()
        time.sleep(5)  # 等待觀察結果

    test_thread = threading.Thread(target=run_tests)
    test_thread.start()
    
    # 等待 WebSocket 或測試完成
    try:
        await asyncio.wait_for(websocket_task, timeout=30)
    except asyncio.TimeoutError:
        print("⏰ 調試測試完成")
    
    test_thread.join()
    print("\n🎉 調試測試結束")

if __name__ == "__main__":
    asyncio.run(main()) 