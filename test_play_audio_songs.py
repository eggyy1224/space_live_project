import asyncio
import json
import time
import websockets
import requests
from typing import List, Dict
from datetime import datetime

# API 配置
API_BASE = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws"

# 本地音頻檔案 URL (使用正確的 /songs-file 端點)
LOCAL_AUDIO_URLS = [
    "/songs-file/電子音樂.mp3",
    "/songs-file/鳥叫.mp3", 
    "/songs-file/暴龍吼叫.mp3",
    "/songs-file/Energetic_fast_pace.mp3",
    "/songs-file/Ambient_keyboard_cli.mp3",
    "/songs-file/male_vocal.mp3",
    "/songs-file/female_talking1.mp3",
    "/songs-file/song_singing.mp3",
    "/songs-file/歌劇1.mp3",
    "/songs-file/喘息.mp3",
    "/songs-file/狂喜.mp3",
    "/songs-file/winds_blowing.mp3"
]

class WebSocketAudioListener:
    """WebSocket 監聽器，專門監聽音頻播放訊息"""
    
    def __init__(self):
        self.messages: List[Dict] = []
        self.is_listening = False
        
    async def connect_and_listen(self, duration=10):
        """連接 WebSocket 並監聽指定時間"""
        self.is_listening = True
        self.messages.clear()
        
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                print(f"🔊 WebSocket 已連接，開始監聽 {duration} 秒...")
                
                end_time = time.time() + duration
                
                while time.time() < end_time and self.is_listening:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        
                        try:
                            data = json.loads(message)
                            timestamp = datetime.now().isoformat()
                            
                            # 只記錄音頻相關訊息
                            if data.get("type") in ["play-audio", "audio-control"]:
                                audio_message = {
                                    "timestamp": timestamp,
                                    "type": data.get("type"),
                                    "data": data
                                }
                                self.messages.append(audio_message)
                                print(f"📨 收到音頻訊息: {data.get('type')} - {data.get('url', 'N/A')}")
                                
                        except json.JSONDecodeError:
                            pass
                            
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("⚠️  WebSocket 連接已關閉")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket 連接錯誤: {e}")
        finally:
            self.is_listening = False
            print(f"🔇 停止 WebSocket 監聽，收到 {len(self.messages)} 條音頻訊息")
    
    def stop_listening(self):
        """停止監聽"""
        self.is_listening = False
    
    def get_messages(self):
        """獲取收到的訊息"""
        return self.messages.copy()

class SongsPlayAudioTester:
    def __init__(self):
        self.results: List[Dict] = []
        self.websocket_listener = WebSocketAudioListener()
        
    async def test_songs_endpoint_basic(self):
        """測試 songs-file 端點基本功能"""
        print("=== 測試 songs-file 端點基本功能 ===")
        
        # 測試不同類型的音頻檔案，設置更長的播放時間
        test_files = [
            {"url": "/songs-file/電子音樂.mp3", "type": "電子音樂", "interrupt": False, "duration": 15},
            {"url": "/songs-file/暴龍吼叫.mp3", "type": "動物聲音", "interrupt": False, "duration": 8},
            {"url": "/songs-file/male_vocal.mp3", "type": "男性人聲", "interrupt": False, "duration": 12},
            {"url": "/songs-file/歌劇1.mp3", "type": "古典音樂", "interrupt": False, "duration": 18}
        ]
        
        for i, test_file in enumerate(test_files):
            print(f"\n測試 {i+1}: 播放 {test_file['type']} - {test_file['url']}")
            print(f"預計播放時間: {test_file['duration']} 秒")
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{API_BASE}/api/control/play-audio",
                    json={"url": test_file['url'], "interrupt": test_file['interrupt']}
                )
                
                response_time = time.time() - start_time
                
                result = {
                    "test": f"songs_basic_{i+1}",
                    "url": test_file['url'],
                    "audio_type": test_file['type'],
                    "interrupt": test_file['interrupt'],
                    "expected_duration": test_file['duration'],
                    "status_code": response.status_code,
                    "response_time": round(response_time, 3),
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    response_data = response.json()
                    result["response_data"] = response_data
                    print(f"✅ 播放開始成功: {response_data}")
                    print(f"🎵 正在播放 {test_file['type']}，請等待 {test_file['duration']} 秒...")
                    
                    # 等待音頻播放完畢
                    await asyncio.sleep(test_file['duration'])
                    print(f"⏹️  {test_file['type']} 播放完畢")
                    
                else:
                    result["error"] = response.text
                    print(f"❌ 失敗: {response.status_code} - {response.text}")
                
                self.results.append(result)
                
                # 音頻之間的間隔時間
                if i < len(test_files) - 1:  # 不是最後一個
                    print("⏳ 等待 3 秒後播放下一個音頻...")
                    await asyncio.sleep(3)
                
            except Exception as e:
                result = {
                    "test": f"songs_basic_{i+1}",
                    "url": test_file['url'],
                    "audio_type": test_file['type'],
                    "error": str(e),
                    "success": False
                }
                self.results.append(result)
                print(f"❌ 錯誤: {e}")

    async def test_songs_with_websocket(self):
        """測試 songs-file 端點配合 WebSocket"""
        print("\n=== 測試 songs-file 端點配合 WebSocket ===")
        
        # 啟動 WebSocket 監聽（延長監聽時間以容納所有音頻播放）
        listen_task = asyncio.create_task(
            self.websocket_listener.connect_and_listen(duration=45)
        )
        
        await asyncio.sleep(1)
        
        # 測試不同的音頻檔案，設置合適的播放時間
        test_sequence = [
            {"url": "/songs-file/鳥叫.mp3", "desc": "自然音效", "duration": 10},
            {"url": "/songs-file/Ambient_keyboard_cli.mp3", "desc": "環境音樂", "duration": 12},
            {"url": "/songs-file/female_talking1.mp3", "desc": "女性人聲", "duration": 8}
        ]
        
        try:
            for i, audio in enumerate(test_sequence):
                print(f"\n步驟 {i+1}: 播放 {audio['desc']} - {audio['url']}")
                print(f"預計播放時間: {audio['duration']} 秒")
                
                response = requests.post(
                    f"{API_BASE}/api/control/play-audio",
                    json={"url": audio['url'], "interrupt": False}  # 全部設為不中斷
                )
                
                if response.status_code == 200:
                    print(f"✅ {audio['desc']} 播放請求成功")
                    print(f"🎵 正在播放 {audio['desc']}，請等待 {audio['duration']} 秒...")
                    
                    # 等待音頻播放完畢
                    await asyncio.sleep(audio['duration'])
                    print(f"⏹️  {audio['desc']} 播放完畢")
                    
                else:
                    print(f"❌ {audio['desc']} 播放請求失敗: {response.status_code}")
                
                # 音頻之間的間隔
                if i < len(test_sequence) - 1:
                    print("⏳ 等待 3 秒後播放下一個音頻...")
                    await asyncio.sleep(3)
            
            # 等待所有 WebSocket 訊息處理完畢
            print("\n⏳ 等待 WebSocket 訊息處理完畢...")
            await asyncio.sleep(3)
            
            messages = self.websocket_listener.get_messages()
            
            result = {
                "test": "songs_websocket",
                "files_tested": len(test_sequence),
                "websocket_messages": len(messages),
                "success": len(messages) >= len(test_sequence)
            }
            
            if messages:
                result["message_details"] = [
                    {
                        "order": i+1,
                        "url": msg["data"].get("url"),
                        "interrupt": msg["data"].get("interrupt"),
                        "timestamp": msg["timestamp"]
                    }
                    for i, msg in enumerate(messages)
                ]
            
            self.results.append(result)
            print(f"✅ WebSocket 測試完成，收到 {len(messages)} 條訊息")
            
        except Exception as e:
            result = {
                "test": "songs_websocket",
                "error": str(e),
                "success": False
            }
            self.results.append(result)
            print(f"❌ 錯誤: {e}")
        
        # 等待監聽任務完成
        self.websocket_listener.stop_listening()
        await listen_task

    async def test_songs_file_accessibility(self):
        """測試 songs-file 檔案可訪問性"""
        print("\n=== 測試 songs-file 檔案可訪問性 ===")
        
        # 測試檔案是否可以透過 HTTP 直接訪問
        test_files = [
            "/songs-file/電子音樂.mp3",
            "/songs-file/暴龍吼叫.mp3",
            "/songs-file/male_vocal.mp3"
        ]
        
        accessibility_results = []
        
        for file_url in test_files:
            print(f"\n檢查檔案可訪問性: {file_url}")
            
            try:
                file_response = requests.get(f"{API_BASE}{file_url}")
                
                access_result = {
                    "file": file_url,
                    "http_status": file_response.status_code,
                    "accessible": file_response.status_code == 200,
                    "content_type": file_response.headers.get("content-type", "unknown")
                }
                
                if file_response.status_code == 200:
                    access_result["file_size"] = len(file_response.content)
                    print(f"✅ 檔案可訪問: {access_result['content_type']}, 大小: {access_result['file_size']} bytes")
                else:
                    print(f"❌ 檔案不可訪問: HTTP {file_response.status_code}")
                
                accessibility_results.append(access_result)
                
            except Exception as e:
                access_result = {
                    "file": file_url,
                    "error": str(e),
                    "accessible": False
                }
                accessibility_results.append(access_result)
                print(f"❌ 檔案檢查錯誤: {e}")
        
        successful_access = sum(1 for r in accessibility_results if r.get("accessible", False))
        
        result = {
            "test": "songs_file_accessibility",
            "total_files": len(test_files),
            "accessible_files": successful_access,
            "success": successful_access > 0,
            "details": accessibility_results
        }
        
        self.results.append(result)
        print(f"\n✅ 檔案可訪問性測試完成: {successful_access}/{len(test_files)} 檔案可訪問")

    def check_backend_status(self):
        """檢查後端狀態"""
        print("=== 檢查後端狀態 ===")
        
        try:
            response = requests.get(f"{API_BASE}/api/control/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ 後端狀態: {status}")
                return status.get("is_available", False)
            else:
                print(f"❌ 後端狀態檢查失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 後端連接失敗: {e}")
            return False

    def print_summary(self):
        """列印測試總結"""
        print("\n" + "="*70)
        print("songs-file 端點 Play Audio API 測試總結")
        print("="*70)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        
        print(f"總測試數: {total_tests}")
        print(f"成功測試: {successful_tests}")
        print(f"失敗測試: {total_tests - successful_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        print("\n詳細結果:")
        for result in self.results:
            status = "✅" if result.get("success", False) else "❌"
            test_name = result.get("test", "unknown")
            
            if "error" in result:
                print(f"{status} {test_name}: {result['error']}")
            else:
                # 顯示特定測試的關鍵指標
                if test_name.startswith("songs_basic_"):
                    audio_type = result.get("audio_type", "unknown")
                    interrupt = result.get("interrupt", False)
                    print(f"{status} {test_name}: {audio_type} (interrupt={interrupt})")
                elif test_name == "songs_websocket":
                    files = result.get("files_tested", 0)
                    messages = result.get("websocket_messages", 0)
                    print(f"{status} {test_name}: {files} 檔案, {messages} 訊息")
                elif test_name == "songs_file_accessibility":
                    accessible = result.get("accessible_files", 0)
                    total = result.get("total_files", 0)
                    print(f"{status} {test_name}: {accessible}/{total} 檔案可訪問")
                else:
                    print(f"{status} {test_name}: OK")
        
        print(f"\n使用的端點: /songs-file/")
        print(f"測試的本地音頻檔案數量: {len(LOCAL_AUDIO_URLS)}")
        print("測試的音頻類型: 電子音樂、動物聲音、人聲、古典音樂、環境音效")

async def main():
    """主測試函數"""
    print("開始 songs-file 端點 Play Audio API 測試...")
    print("測試檔案來源: prototype/backend/songs/")
    print("使用正確的端點: /songs-file/")
    print("確保後端服務器在 localhost:8000 運行")
    print("-" * 70)
    
    tester = SongsPlayAudioTester()
    
    # 檢查後端狀態
    if not tester.check_backend_status():
        print("❌ 後端不可用，停止測試")
        return
    
    try:
        # 執行所有 songs-file 測試
        await tester.test_songs_endpoint_basic()
        await tester.test_songs_file_accessibility()
        await tester.test_songs_with_websocket()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被用戶中斷")
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤: {e}")
    finally:
        # 列印總結
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 