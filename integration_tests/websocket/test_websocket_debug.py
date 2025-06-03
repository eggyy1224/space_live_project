import asyncio
import json
import requests
import websockets
from datetime import datetime
import time

# API 配置
API_BASE = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws"

class WebSocketMonitor:
    """WebSocket 連接監控器"""
    
    def __init__(self):
        self.connection_history = []
        self.active_connections = set()
        
    async def monitor_connections(self, duration=60):
        """持續監控 WebSocket 連接狀態"""
        print(f"=== 開始監控 WebSocket 連接狀態 ({duration} 秒) ===")
        
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            try:
                # 檢查後端連接狀態
                response = requests.get(f"{API_BASE}/api/control/status")
                if response.status_code == 200:
                    status = response.json()
                    current_connections = status.get('active_connections', 0)
                    connections_detail = status.get('connections_detail', [])
                    
                    # 記錄連接變化
                    timestamp = datetime.now().isoformat()
                    
                    # 提取連接標識
                    current_ids = set()
                    for conn in connections_detail:
                        client_info = conn.get('client', 'unknown')
                        current_ids.add(client_info)
                    
                    # 檢查是否有新連接或斷開連接
                    new_connections = current_ids - self.active_connections
                    closed_connections = self.active_connections - current_ids
                    
                    if new_connections or closed_connections or len(self.connection_history) == 0:
                        connection_event = {
                            "timestamp": timestamp,
                            "total_connections": current_connections,
                            "new_connections": list(new_connections),
                            "closed_connections": list(closed_connections),
                            "all_connections": list(current_ids)
                        }
                        
                        self.connection_history.append(connection_event)
                        
                        # 實時輸出
                        print(f"\n[{timestamp}] 連接狀態變化:")
                        print(f"  總連接數: {current_connections}")
                        if new_connections:
                            print(f"  新建連接: {new_connections}")
                        if closed_connections:
                            print(f"  關閉連接: {closed_connections}")
                        
                        self.active_connections = current_ids
                
                # 每秒檢查一次
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"監控錯誤: {e}")
                await asyncio.sleep(1)
        
        print(f"\n=== 監控結束 ===")
        self.print_summary()
    
    def print_summary(self):
        """打印監控總結"""
        print("\n" + "="*60)
        print("WebSocket 連接監控總結")
        print("="*60)
        
        if not self.connection_history:
            print("未檢測到任何連接變化")
            return
        
        print(f"總連接事件數: {len(self.connection_history)}")
        print("\n連接變化時間線:")
        
        for i, event in enumerate(self.connection_history):
            print(f"\n{i+1}. [{event['timestamp']}]")
            print(f"   總連接數: {event['total_connections']}")
            
            if event['new_connections']:
                print(f"   新建連接: {event['new_connections']}")
            if event['closed_connections']:
                print(f"   關閉連接: {event['closed_connections']}")
            
            print(f"   所有連接: {event['all_connections']}")
        
        # 分析重複連接問題
        max_connections = max(event['total_connections'] for event in self.connection_history)
        
        if max_connections > 1:
            print(f"\n⚠️  檢測到最多 {max_connections} 個同時連接!")
            print("可能的原因:")
            print("1. 前端重複連接 (useWebSocket hook 和其他地方)")
            print("2. 連接斷開處理不當")
            print("3. 重連邏輯問題")
            print("4. 多個瀏覽器標籤頁")
            
            # 查找同時連接最多的時間點
            peak_event = max(self.connection_history, key=lambda x: x['total_connections'])
            print(f"\n最多連接發生在: {peak_event['timestamp']}")
            print(f"連接詳情: {peak_event['all_connections']}")
        else:
            print("\n✅ 連接狀態正常，沒有檢測到重複連接")

async def test_api_while_monitoring():
    """在監控期間測試音頻 API"""
    print("\n開始音頻 API 測試...")
    
    test_files = [
        "/songs-file/電子音樂.mp3",
        "/songs-file/鳥叫.mp3",
        "/songs-file/暴龍吼叫.mp3"
    ]
    
    for i, audio_url in enumerate(test_files):
        print(f"\n測試 {i+1}: 播放 {audio_url}")
        
        try:
            response = requests.post(
                f"{API_BASE}/api/control/play-audio",
                json={"url": audio_url, "interrupt": False}
            )
            
            if response.status_code == 200:
                print(f"✅ 播放請求成功")
            else:
                print(f"❌ 播放請求失敗: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 請求錯誤: {e}")
        
        # 等待一段時間再進行下一個測試
        await asyncio.sleep(10)

async def main():
    """主函數"""
    print("WebSocket 連接監控和音頻測試工具")
    print("此工具將持續監控後端 WebSocket 連接狀態")
    print("並在監控期間進行音頻播放測試")
    print("-" * 60)
    
    # 檢查初始狀態
    try:
        response = requests.get(f"{API_BASE}/api/control/status")
        if response.status_code == 200:
            status = response.json()
            print(f"初始連接數: {status.get('active_connections', 0)}")
            print(f"後端可用: {status.get('is_available', False)}")
        else:
            print(f"❌ 無法連接到後端: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 後端連接錯誤: {e}")
        return
    
    # 創建監控器
    monitor = WebSocketMonitor()
    
    # 啟動監控任務
    monitor_task = asyncio.create_task(monitor.monitor_connections(duration=45))
    
    # 等待一段時間讓初始狀態穩定
    await asyncio.sleep(5)
    
    # 啟動 API 測試任務
    api_test_task = asyncio.create_task(test_api_while_monitoring())
    
    # 等待兩個任務完成
    await asyncio.gather(monitor_task, api_test_task)
    
    print("\n監控和測試完成")

if __name__ == "__main__":
    asyncio.run(main()) 