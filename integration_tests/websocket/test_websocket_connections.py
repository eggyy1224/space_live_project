import asyncio
import json
import requests
import websockets
from datetime import datetime

# API 配置
API_BASE = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws"

async def test_websocket_connections():
    """測試 WebSocket 連接問題"""
    print("=== WebSocket 連接診斷測試 ===")
    
    # 1. 檢查當前後端連接狀態
    print("\n1. 檢查當前後端狀態:")
    try:
        response = requests.get(f"{API_BASE}/api/control/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   活動連接數: {status.get('active_connections', 0)}")
            print(f"   可用狀態: {status.get('is_available', False)}")
            connections = status.get('connections_detail', [])
            for i, conn in enumerate(connections):
                print(f"   連接 {i+1}: {conn.get('client', 'unknown')}")
        else:
            print(f"   無法獲取狀態: {response.status_code}")
    except Exception as e:
        print(f"   狀態檢查錯誤: {e}")
        return
    
    # 2. 建立新的 WebSocket 連接並監聽
    print("\n2. 建立新的測試 WebSocket 連接:")
    
    messages_received = []
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("   ✅ WebSocket 連接成功建立")
            
            # 檢查連接後的狀態
            response = requests.get(f"{API_BASE}/api/control/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   現在活動連接數: {status.get('active_connections', 0)}")
            
            # 設置訊息監聽
            async def listen_for_messages():
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        try:
                            data = json.loads(message)
                            timestamp = datetime.now().isoformat()
                            messages_received.append({
                                "timestamp": timestamp,
                                "type": data.get("type"),
                                "data": data
                            })
                            print(f"   📨 收到訊息: {data.get('type')} - {data.get('url', 'N/A')}")
                        except json.JSONDecodeError:
                            pass
                except asyncio.TimeoutError:
                    pass
                except websockets.exceptions.ConnectionClosed:
                    print("   ⚠️  WebSocket 連接已關閉")
            
            # 啟動監聽任務
            listen_task = asyncio.create_task(listen_for_messages())
            
            # 3. 發送測試音頻請求
            print("\n3. 發送測試音頻播放請求:")
            
            test_url = "/songs-file/鳥叫.mp3"
            print(f"   測試音頻: {test_url}")
            
            response = requests.post(
                f"{API_BASE}/api/control/play-audio",
                json={"url": test_url, "interrupt": False}
            )
            
            if response.status_code == 200:
                print(f"   ✅ API 請求成功: {response.json()}")
            else:
                print(f"   ❌ API 請求失敗: {response.status_code}")
            
            # 等待接收訊息
            print("\n4. 等待 WebSocket 訊息...")
            await asyncio.sleep(3)
            
            # 停止監聽
            listen_task.cancel()
            try:
                await listen_task
            except asyncio.CancelledError:
                pass
            
            # 分析結果
            print(f"\n5. 結果分析:")
            print(f"   收到的訊息總數: {len(messages_received)}")
            
            audio_messages = [msg for msg in messages_received if msg["type"] == "play-audio"]
            print(f"   音頻播放訊息數: {len(audio_messages)}")
            
            for i, msg in enumerate(audio_messages):
                print(f"   音頻訊息 {i+1}: {msg['data'].get('url')} (時間: {msg['timestamp']})")
            
            if len(audio_messages) > 1:
                print("   ⚠️  檢測到重複的音頻播放訊息!")
                print("   原因可能是：")
                print("     - 後端有多個 WebSocket 連接")
                print("     - broadcast 邏輯有問題")
                print("     - 前端重複連接")
            elif len(audio_messages) == 1:
                print("   ✅ 音頻訊息正常，沒有重複")
            else:
                print("   ❌ 沒有收到音頻播放訊息")
                
    except Exception as e:
        print(f"   WebSocket 連接錯誤: {e}")
    
    # 6. 最終狀態檢查
    print("\n6. 最終後端狀態:")
    try:
        response = requests.get(f"{API_BASE}/api/control/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   活動連接數: {status.get('active_connections', 0)}")
        else:
            print(f"   無法獲取狀態: {response.status_code}")
    except Exception as e:
        print(f"   狀態檢查錯誤: {e}")

async def main():
    print("WebSocket 連接診斷測試")
    print("此測試將檢查是否有多個 WebSocket 連接導致音頻重複播放")
    print("-" * 60)
    
    await test_websocket_connections()
    
    print("\n" + "="*60)
    print("診斷完成")

if __name__ == "__main__":
    asyncio.run(main()) 