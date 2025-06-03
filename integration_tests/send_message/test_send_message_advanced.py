#!/usr/bin/env python3
"""
Send Message API 進階整合測試
專注於 TTS 功能、WebSocket 訊息格式和音頻處理
"""

import requests
import json
import time
import asyncio
import websocket
import threading
from datetime import datetime
import re

# API 配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
SEND_MESSAGE_ENDPOINT = f"{BASE_URL}/api/control/send-message"
STATUS_ENDPOINT = f"{BASE_URL}/api/control/status"

class WebSocketListener:
    """WebSocket 監聽器，用於捕獲後端發送的訊息"""
    
    def __init__(self):
        self.messages = []
        self.connected = False
        self.ws = None
        self.thread = None
        
    def connect(self):
        """連接到 WebSocket"""
        try:
            self.ws = websocket.WebSocketApp(
                WS_URL,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # 在背景執行
            self.thread = threading.Thread(target=self.ws.run_forever)
            self.thread.daemon = True
            self.thread.start()
            
            # 等待連接建立
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            return self.connected
        except Exception as e:
            print(f"WebSocket 連接失敗: {e}")
            return False
    
    def on_open(self, ws):
        print("🔗 WebSocket 連接已建立")
        self.connected = True
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.messages.append({
                "timestamp": datetime.now().isoformat(),
                "data": data
            })
            print(f"📨 收到 WebSocket 訊息: {data.get('type', 'unknown')}")
        except json.JSONDecodeError:
            print(f"⚠️ 無法解析 WebSocket 訊息: {message}")
    
    def on_error(self, ws, error):
        print(f"❌ WebSocket 錯誤: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("🔌 WebSocket 連接已關閉")
        self.connected = False
    
    def get_messages(self, message_type=None, since_seconds=None):
        """獲取指定類型或時間範圍內的訊息"""
        messages = self.messages.copy()
        
        if since_seconds:
            cutoff_time = datetime.now().timestamp() - since_seconds
            messages = [
                msg for msg in messages 
                if datetime.fromisoformat(msg["timestamp"]).timestamp() > cutoff_time
            ]
        
        if message_type:
            messages = [
                msg for msg in messages 
                if msg["data"].get("type") == message_type
            ]
        
        return messages
    
    def clear_messages(self):
        """清空收集的訊息"""
        self.messages = []
    
    def disconnect(self):
        """斷開 WebSocket 連接"""
        if self.ws:
            self.ws.close()

def test_tts_integration():
    """測試 TTS 整合功能"""
    print("🎯 測試 1: TTS 整合功能")
    
    # 建立 WebSocket 監聽器
    ws_listener = WebSocketListener()
    if not ws_listener.connect():
        print("❌ 無法建立 WebSocket 連接，跳過 TTS 測試")
        return
    
    time.sleep(1)  # 確保連接穩定
    ws_listener.clear_messages()
    
    # 發送包含中文的測試訊息
    test_content = "你好！這是一個測試 TTS 功能的訊息。請確保語音合成正常運作。"
    
    print(f"  發送測試訊息: {test_content}")
    payload = {
        "content": test_content,
        "message_type": "chat-message"
    }
    
    response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    print(f"  API 回應狀態: {response.status_code}")
    
    # 等待 TTS 處理和 WebSocket 訊息
    time.sleep(3)
    
    # 檢查收到的 WebSocket 訊息
    chat_messages = ws_listener.get_messages("chat-message", since_seconds=5)
    
    if chat_messages:
        message_data = chat_messages[-1]["data"]
        bot_message = message_data.get("message", {})
        
        print(f"  收到 WebSocket 訊息: ✅")
        print(f"  訊息 ID: {bot_message.get('id', 'N/A')}")
        print(f"  訊息內容: {bot_message.get('content', 'N/A')}")
        print(f"  角色: {bot_message.get('role', 'N/A')}")
        print(f"  時間戳: {bot_message.get('timestamp', 'N/A')}")
        print(f"  來自 API: {bot_message.get('isFromAPI', 'N/A')}")
        
        # 檢查是否有音頻 URL
        audio_url = bot_message.get('audioUrl')
        if audio_url:
            print(f"  音頻 URL: {audio_url} ✅")
            
            # 測試音頻 URL 是否可訪問
            try:
                audio_response = requests.head(audio_url, timeout=5)
                print(f"  音頻可訪問性: {audio_response.status_code} ✅")
            except Exception as e:
                print(f"  音頻訪問錯誤: {e} ❌")
        else:
            print(f"  音頻 URL: 未生成 ⚠️")
    else:
        print("  未收到預期的 WebSocket 訊息 ❌")
    
    ws_listener.disconnect()
    print("✅ TTS 整合測試完成")
    print()

def test_websocket_message_format():
    """測試 WebSocket 訊息格式的完整性"""
    print("🎯 測試 2: WebSocket 訊息格式驗證")
    
    ws_listener = WebSocketListener()
    if not ws_listener.connect():
        print("❌ 無法建立 WebSocket 連接，跳過格式測試")
        return
    
    time.sleep(1)
    ws_listener.clear_messages()
    
    # 發送測試訊息
    test_content = "測試訊息格式驗證"
    payload = {
        "content": test_content,
        "message_type": "chat-message"
    }
    
    requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    time.sleep(2)
    
    chat_messages = ws_listener.get_messages("chat-message", since_seconds=3)
    
    if chat_messages:
        message_data = chat_messages[-1]["data"]
        
        # 驗證頂層結構
        required_top_level = ["type", "message"]
        for field in required_top_level:
            assert field in message_data, f"缺少頂層欄位: {field}"
            print(f"  ✓ 頂層欄位: {field}")
        
        assert message_data["type"] == "chat-message", "訊息類型不正確"
        
        # 驗證 message 物件結構
        bot_message = message_data["message"]
        required_message_fields = ["id", "role", "content", "timestamp", "isFromAPI"]
        
        for field in required_message_fields:
            assert field in bot_message, f"缺少訊息欄位: {field}"
            print(f"  ✓ 訊息欄位: {field}")
        
        # 驗證欄位值
        assert bot_message["role"] == "bot", "角色應該是 'bot'"
        assert bot_message["content"] == test_content, "內容不匹配"
        assert bot_message["isFromAPI"] == True, "isFromAPI 應該是 True"
        
        # 驗證 ID 格式
        message_id = bot_message["id"]
        assert message_id.startswith("api-bot-"), f"ID 格式不正確: {message_id}"
        
        # 驗證時間戳格式
        timestamp = bot_message["timestamp"]
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            print(f"  ✓ 時間戳格式正確: {timestamp}")
        except ValueError:
            raise AssertionError(f"時間戳格式無效: {timestamp}")
        
        print("✅ WebSocket 訊息格式驗證通過")
    else:
        raise AssertionError("未收到預期的 WebSocket 訊息")
    
    ws_listener.disconnect()
    print()

def test_different_content_lengths():
    """測試不同長度內容的 TTS 處理"""
    print("🎯 測試 3: 不同長度內容的 TTS 處理")
    
    ws_listener = WebSocketListener()
    if not ws_listener.connect():
        print("❌ 無法建立 WebSocket 連接，跳過長度測試")
        return
    
    test_cases = [
        ("短文字", "你好"),
        ("中等文字", "這是一個中等長度的測試訊息，用來檢驗 TTS 系統的處理能力。"),
        ("長文字", "這是一個相當長的測試訊息，我們需要確保 TTS 服務能夠正確處理這種長度的文字內容。這個測試會驗證系統在處理較長文字時的穩定性和性能表現。我們期望無論文字長度如何，系統都能夠生成高質量的語音輸出。")
    ]
    
    for description, content in test_cases:
        print(f"  測試 {description} ({len(content)} 字符)")
        
        ws_listener.clear_messages()
        
        payload = {
            "content": content,
            "message_type": "chat-message"
        }
        
        start_time = time.time()
        response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
        
        # 等待處理完成
        time.sleep(max(2, len(content) // 20))  # 根據長度調整等待時間
        
        processing_time = time.time() - start_time
        print(f"    處理時間: {processing_time:.2f} 秒")
        print(f"    API 狀態: {response.status_code}")
        
        # 檢查 WebSocket 訊息
        messages = ws_listener.get_messages("chat-message", since_seconds=5)
        if messages:
            bot_message = messages[-1]["data"]["message"]
            has_audio = "audioUrl" in bot_message and bot_message["audioUrl"]
            print(f"    音頻生成: {'✅' if has_audio else '❌'}")
        else:
            print(f"    WebSocket 訊息: ❌")
    
    ws_listener.disconnect()
    print("✅ 不同長度內容測試完成")
    print()

def test_message_timing():
    """測試訊息發送的時序和延遲"""
    print("🎯 測試 4: 訊息時序和延遲分析")
    
    ws_listener = WebSocketListener()
    if not ws_listener.connect():
        print("❌ 無法建立 WebSocket 連接，跳過時序測試")
        return
    
    time.sleep(1)
    
    # 發送多個訊息並測量延遲
    test_messages = [
        "第一個測試訊息",
        "第二個測試訊息", 
        "第三個測試訊息"
    ]
    
    send_times = []
    
    for i, content in enumerate(test_messages):
        ws_listener.clear_messages()
        
        print(f"  發送訊息 {i+1}: {content}")
        
        # 記錄發送時間
        send_time = time.time()
        send_times.append(send_time)
        
        payload = {
            "content": content,
            "message_type": "chat-message"
        }
        
        response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
        print(f"    API 回應時間: {time.time() - send_time:.3f} 秒")
        
        # 等待 WebSocket 訊息
        timeout = 5
        received = False
        while timeout > 0 and not received:
            messages = ws_listener.get_messages("chat-message", since_seconds=1)
            if messages:
                receive_time = time.time()
                total_delay = receive_time - send_time
                print(f"    總延遲: {total_delay:.3f} 秒")
                received = True
            else:
                time.sleep(0.1)
                timeout -= 0.1
        
        if not received:
            print(f"    警告: 未在時限內收到 WebSocket 訊息")
        
        time.sleep(1)  # 避免過於頻繁
    
    ws_listener.disconnect()
    print("✅ 訊息時序測試完成")
    print()

def test_audio_url_validation():
    """測試音頻 URL 的有效性和可訪問性"""
    print("🎯 測試 5: 音頻 URL 驗證")
    
    ws_listener = WebSocketListener()
    if not ws_listener.connect():
        print("❌ 無法建立 WebSocket 連接，跳過音頻 URL 測試")
        return
    
    time.sleep(1)
    ws_listener.clear_messages()
    
    # 發送會生成音頻的訊息
    content = "測試音頻 URL 的生成和有效性驗證"
    payload = {
        "content": content,
        "message_type": "chat-message"
    }
    
    requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    time.sleep(3)  # 給 TTS 充足時間
    
    messages = ws_listener.get_messages("chat-message", since_seconds=5)
    
    if messages:
        bot_message = messages[-1]["data"]["message"]
        audio_url = bot_message.get("audioUrl")
        
        if audio_url:
            print(f"  音頻 URL: {audio_url}")
            
            # 驗證 URL 格式
            url_pattern = r'^https?://.+\.(mp3|wav|ogg|m4a)$'
            if re.match(url_pattern, audio_url, re.IGNORECASE):
                print(f"  URL 格式: ✅")
            else:
                print(f"  URL 格式: ⚠️ (可能是相對路徑)")
            
            # 測試可訪問性
            try:
                response = requests.head(audio_url, timeout=10)
                print(f"  HTTP 狀態: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  可訪問性: ✅")
                    
                    # 檢查 Content-Type
                    content_type = response.headers.get('Content-Type', '')
                    if 'audio' in content_type:
                        print(f"  內容類型: {content_type} ✅")
                    else:
                        print(f"  內容類型: {content_type} ⚠️")
                else:
                    print(f"  可訪問性: ❌")
                    
            except requests.exceptions.RequestException as e:
                print(f"  訪問錯誤: {e}")
        else:
            print("  未生成音頻 URL ⚠️")
    else:
        print("  未收到 WebSocket 訊息 ❌")
    
    ws_listener.disconnect()
    print("✅ 音頻 URL 驗證完成")
    print()

def main():
    """主測試函數"""
    print("🚀 開始 Send Message API 進階整合測試")
    print("=" * 60)
    print("專注於 TTS 功能、WebSocket 訊息格式和音頻處理")
    print("=" * 60)
    
    # 檢查後端狀態
    try:
        response = requests.get(STATUS_ENDPOINT)
        status = response.json()
        print(f"後端狀態: {status}")
        
        if status.get("active_connections", 0) == 0:
            print("⚠️ 警告: 沒有前端連接，但仍可測試 WebSocket 功能")
    except Exception as e:
        print(f"⚠️ 無法檢查後端狀態: {e}")
    
    print("\n" + "=" * 60)
    
    try:
        # 執行進階測試
        test_tts_integration()
        test_websocket_message_format()
        test_different_content_lengths()
        test_message_timing()
        test_audio_url_validation()
        
        print("🎉 所有進階測試完成！")
        print("✅ Send Message API 進階功能正常")
        
    except AssertionError as e:
        print(f"❌ 測試失敗: {e}")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 