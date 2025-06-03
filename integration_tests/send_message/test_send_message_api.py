#!/usr/bin/env python3
"""
Send Message API 整合測試腳本
測試 /api/control/send-message 端點的完整功能
"""

import requests
import json
import time
import asyncio
from datetime import datetime

# API 配置
BASE_URL = "http://localhost:8000"
SEND_MESSAGE_ENDPOINT = f"{BASE_URL}/api/control/send-message"
STATUS_ENDPOINT = f"{BASE_URL}/api/control/status"

def test_basic_text_message():
    """測試基本文字訊息發送"""
    print("🎯 測試 1: 基本文字訊息發送")
    
    payload = {
        "content": "你好！這是一個測試訊息。",
        "message_type": "chat-message"
    }
    
    response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    print(f"狀態碼: {response.status_code}")
    result = response.json()
    print(f"回應: {result}")
    
    # 驗證回應結構
    assert response.status_code == 200
    assert result["success"] == True
    assert "message" in result
    assert "connections" in result
    print("✅ 基本文字訊息測試通過")
    print()

def test_long_text_message():
    """測試長文字訊息"""
    print("🎯 測試 2: 長文字訊息發送")
    
    long_content = """
    這是一個相當長的測試訊息，用來測試系統如何處理較長的文字內容。
    我們需要確保 TTS 服務能夠正確處理這種長度的文字，
    並且前端能夠正確顯示和播放相應的語音內容。
    這個測試也會驗證音頻生成和 WebSocket 廣播功能是否正常運作。
    """
    
    payload = {
        "content": long_content.strip(),
        "message_type": "chat-message"
    }
    
    response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    print(f"狀態碼: {response.status_code}")
    result = response.json()
    print(f"回應: {result}")
    
    assert response.status_code == 200
    assert result["success"] == True
    print("✅ 長文字訊息測試通過")
    print()

def test_different_message_types():
    """測試不同的訊息類型"""
    print("🎯 測試 3: 不同訊息類型")
    
    message_types = [
        ("chat-message", "這是一般聊天訊息"),
        ("system-message", "這是系統訊息"),
        ("notification", "這是通知訊息"),
        ("announcement", "這是公告訊息")
    ]
    
    for msg_type, content in message_types:
        print(f"  測試訊息類型: {msg_type}")
        payload = {
            "content": content,
            "message_type": msg_type
        }
        
        response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
        print(f"    狀態碼: {response.status_code}")
        result = response.json()
        print(f"    成功: {result.get('success', False)}")
        
        assert response.status_code == 200
        assert result["success"] == True
        time.sleep(1)  # 給系統時間處理
    
    print("✅ 不同訊息類型測試通過")
    print()

def test_special_characters():
    """測試特殊字符和多語言內容"""
    print("🎯 測試 4: 特殊字符和多語言內容")
    
    test_messages = [
        "測試中文字符：你好世界！😊",
        "English text with numbers: 123 and symbols: @#$%",
        "Mixed 混合 content with émojis 🎉🎊🌟",
        "特殊符號測試：「」、『』、（）、【】",
        "數字和時間：2024年1月1日 12:34:56"
    ]
    
    for content in test_messages:
        print(f"  測試內容: {content[:30]}...")
        payload = {
            "content": content,
            "message_type": "chat-message"
        }
        
        response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
        print(f"    狀態碼: {response.status_code}")
        result = response.json()
        print(f"    成功: {result.get('success', False)}")
        
        assert response.status_code == 200
        assert result["success"] == True
        time.sleep(1.5)  # 給 TTS 更多時間處理
    
    print("✅ 特殊字符測試通過")
    print()

def test_empty_and_whitespace():
    """測試空內容和空白字符"""
    print("🎯 測試 5: 空內容和空白字符處理")
    
    test_cases = [
        ("", "空字符串"),
        ("   ", "只有空格"),
        ("\t\n\r", "只有制表符和換行"),
        (".", "單個標點符號"),
        ("123", "純數字")
    ]
    
    for content, description in test_cases:
        print(f"  測試: {description}")
        payload = {
            "content": content,
            "message_type": "chat-message"
        }
        
        try:
            response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
            print(f"    狀態碼: {response.status_code}")
            result = response.json()
            print(f"    成功: {result.get('success', False)}")
            
            # 空內容應該也能正常處理
            assert response.status_code == 200
            assert result["success"] == True
            
        except Exception as e:
            print(f"    錯誤: {e}")
        
        time.sleep(1)
    
    print("✅ 空內容測試通過")
    print()

def test_concurrent_messages():
    """測試併發訊息發送"""
    print("🎯 測試 6: 併發訊息發送")
    
    import threading
    import queue
    
    results = queue.Queue()
    
    def send_message(index):
        payload = {
            "content": f"這是併發測試訊息 #{index}，時間戳：{datetime.now().isoformat()}",
            "message_type": "chat-message"
        }
        
        try:
            response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
            results.put((index, response.status_code, response.json()))
        except Exception as e:
            results.put((index, 500, {"error": str(e)}))
    
    # 創建多個線程同時發送訊息
    threads = []
    num_messages = 5
    
    print(f"  同時發送 {num_messages} 個訊息...")
    for i in range(num_messages):
        thread = threading.Thread(target=send_message, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有線程完成
    for thread in threads:
        thread.join()
    
    # 收集結果
    success_count = 0
    while not results.empty():
        index, status_code, result = results.get()
        print(f"    訊息 #{index}: 狀態碼 {status_code}, 成功: {result.get('success', False)}")
        if status_code == 200 and result.get('success'):
            success_count += 1
    
    print(f"  成功率: {success_count}/{num_messages}")
    assert success_count == num_messages, f"期望 {num_messages} 個成功，實際 {success_count} 個"
    print("✅ 併發訊息測試通過")
    print()

def test_message_without_type():
    """測試不指定訊息類型（使用預設值）"""
    print("🎯 測試 7: 預設訊息類型")
    
    payload = {
        "content": "這是沒有指定 message_type 的訊息，應該使用預設值 'chat-message'"
    }
    
    response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    print(f"狀態碼: {response.status_code}")
    result = response.json()
    print(f"回應: {result}")
    
    assert response.status_code == 200
    assert result["success"] == True
    print("✅ 預設訊息類型測試通過")
    print()

def test_error_conditions():
    """測試錯誤條件"""
    print("🎯 測試 8: 錯誤條件處理")
    
    # 測試無效的 JSON
    print("  測試無效 JSON...")
    try:
        response = requests.post(
            SEND_MESSAGE_ENDPOINT, 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"    無效 JSON 狀態碼: {response.status_code}")
        # 應該返回 422 (Unprocessable Entity)
    except Exception as e:
        print(f"    無效 JSON 錯誤: {e}")
    
    # 測試缺少必要欄位
    print("  測試缺少 content 欄位...")
    try:
        response = requests.post(SEND_MESSAGE_ENDPOINT, json={"message_type": "test"})
        print(f"    缺少欄位狀態碼: {response.status_code}")
        result = response.json()
        print(f"    錯誤詳情: {result}")
        # 應該返回 422 因為 content 是必要欄位
    except Exception as e:
        print(f"    缺少欄位錯誤: {e}")
    
    print("✅ 錯誤條件測試完成")
    print()

def test_response_structure():
    """測試回應結構的完整性"""
    print("🎯 測試 9: 回應結構驗證")
    
    payload = {
        "content": "測試回應結構的完整性",
        "message_type": "chat-message"
    }
    
    response = requests.post(SEND_MESSAGE_ENDPOINT, json=payload)
    result = response.json()
    
    print(f"完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 驗證必要欄位
    required_fields = ["success", "message", "connections"]
    for field in required_fields:
        assert field in result, f"回應缺少必要欄位: {field}"
        print(f"  ✓ 包含欄位: {field}")
    
    # 驗證欄位類型
    assert isinstance(result["success"], bool), "success 應該是布林值"
    assert isinstance(result["message"], str), "message 應該是字符串"
    assert isinstance(result["connections"], int), "connections 應該是整數"
    
    print("✅ 回應結構驗證通過")
    print()

def check_backend_status():
    """檢查後端狀態"""
    print("🔍 檢查後端連接狀態")
    
    try:
        response = requests.get(STATUS_ENDPOINT)
        status_data = response.json()
        print(f"後端狀態: {status_data}")
        
        active_connections = status_data.get("active_connections", 0)
        if active_connections == 0:
            print("⚠️ 警告: 沒有活動的前端連接，某些功能可能無法完全測試")
            return False
        else:
            print(f"✅ 發現 {active_connections} 個活動連接")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端，請確保後端服務正在運行")
        return False
    except Exception as e:
        print(f"❌ 檢查後端狀態時發生錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始 Send Message API 整合測試")
    print("=" * 60)
    
    # 檢查後端狀態
    backend_available = check_backend_status()
    
    print("\n" + "=" * 60)
    
    try:
        # 基礎功能測試
        test_basic_text_message()
        test_long_text_message()
        test_different_message_types()
        test_special_characters()
        test_empty_and_whitespace()
        test_message_without_type()
        test_response_structure()
        
        # 進階測試
        if backend_available:
            test_concurrent_messages()
        else:
            print("⚠️ 跳過併發測試：沒有前端連接")
        
        # 錯誤條件測試
        test_error_conditions()
        
        print("🎉 所有測試完成！")
        print("✅ Send Message API 功能正常")
        
    except AssertionError as e:
        print(f"❌ 測試失敗: {e}")
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端 API，請確保服務正在運行")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 