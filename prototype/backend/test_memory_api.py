#!/usr/bin/env python3
"""
記憶 API 測試腳本
用於測試新建的記憶系統 API 端點
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_save_memory():
    """測試儲存記憶"""
    print("🧪 測試儲存記憶...")
    
    # 測試儲存人格記憶
    persona_data = {
        "memory_type": "persona",
        "content": "我喜歡在太空中觀察星星，特別是土星的光環",
        "metadata": {
            "type": "learned_preference",
            "category": "hobby"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/memory/save", json=persona_data)
    print(f"人格記憶儲存結果: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ {response.json()['message']}")
    else:
        print(f"❌ {response.text}")
    
    # 測試儲存對話記憶
    conversation_data = {
        "memory_type": "conversation",
        "content": "input: 你今天心情如何？\noutput: 我今天心情很好，因為看到了美麗的地球日出！",
        "metadata": {
            "type": "conversation",
            "user_input": "你今天心情如何？",
            "ai_response": "我今天心情很好，因為看到了美麗的地球日出！"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/memory/save", json=conversation_data)
    print(f"對話記憶儲存結果: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ {response.json()['message']}")
    else:
        print(f"❌ {response.text}")

def test_get_memory():
    """測試獲取記憶"""
    print("\n🧪 測試獲取記憶...")
    
    # 測試獲取人格記憶
    persona_query = {
        "memory_type": "persona",
        "limit": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/memory/get", json=persona_query)
    print(f"人格記憶獲取結果: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 找到 {result.get('count', 0)} 條人格記憶")
        memories = result.get('data', {}).get('memories', [])
        for i, memory in enumerate(memories[:3], 1):  # 只顯示前3條
            print(f"  記憶 {i}: {memory.get('content', '')[:50]}...")
    else:
        print(f"❌ {response.text}")
    
    # 測試語義搜尋
    search_query = {
        "memory_type": "persona",
        "query": "太空 星星",
        "limit": 3
    }
    
    response = requests.post(f"{BASE_URL}/api/memory/get", json=search_query)
    print(f"語義搜尋結果: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 搜尋到 {result.get('count', 0)} 條相關記憶")
        memories = result.get('data', {}).get('memories', [])
        for i, memory in enumerate(memories, 1):
            print(f"  搜尋結果 {i}: {memory.get('content', '')[:50]}...")
    else:
        print(f"❌ {response.text}")

def test_get_memory_stats():
    """測試獲取記憶統計"""
    print("\n🧪 測試獲取記憶統計...")
    
    response = requests.get(f"{BASE_URL}/api/memory/stats")
    print(f"記憶統計結果: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ 記憶統計:")
        stats = result.get('data', {}).get('stats', {})
        for memory_type, info in stats.items():
            print(f"  {memory_type}: {info.get('count', 0)} 條記憶 ({info.get('status', 'unknown')})")
    else:
        print(f"❌ {response.text}")

def main():
    """主測試函數"""
    print("🚀 開始測試記憶 API...")
    print("=" * 50)
    
    # 等待一下讓服務器準備好
    time.sleep(1)
    
    try:
        # 測試儲存記憶
        test_save_memory()
        
        # 等待一下讓記憶被處理
        time.sleep(2)
        
        # 測試獲取記憶
        test_get_memory()
        
        # 測試統計
        test_get_memory_stats()
        
        print("\n" + "=" * 50)
        print("✅ 測試完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務器，請確認服務器是否運行在 http://localhost:8000")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 