#!/usr/bin/env python3
"""
YouTube 聊天室監控功能測試腳本

測試新增的 YouTube 聊天室即時監控功能
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"


def test_youtube_chat_monitor():
    """測試 YouTube 聊天室監控功能"""
    
    print("🎯 開始測試 YouTube 聊天室監控功能")
    print("=" * 50)
    
    # 您的直播 URL
    video_url = "https://youtube.com/live/vs4gTWg5pGk?feature=share"
    
    try:
        # 1. 測試開始監控
        print("\n📺 1. 測試開始監控聊天室...")
        start_data = {"video_url_or_id": video_url}
        response = requests.post(
            f"{BASE_URL}/perception/youtube-chat/start",
            json=start_data
        )
        
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 開始監控成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 開始監控失敗: {response.text}")
            return
        
        # 2. 測試查詢狀態
        print("\n📊 2. 測試查詢監控狀態...")
        response = requests.get(f"{BASE_URL}/perception/youtube-chat/status")
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ 狀態查詢成功: {json.dumps(status, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 狀態查詢失敗: {response.text}")
        
        # 3. 等待一段時間讓聊天訊息累積
        print("\n⏳ 3. 等待 30 秒讓聊天訊息累積...")
        time.sleep(30)
        
        # 4. 測試取得最近訊息
        print("\n💬 4. 測試取得最近的聊天訊息...")
        response = requests.get(f"{BASE_URL}/perception/youtube-chat/messages?limit=10")
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ 取得訊息成功，共 {messages['count']} 條訊息")
            for i, msg in enumerate(messages['messages'][:3]):  # 只顯示前3條
                print(f"  {i+1}. [{msg['author']}] {msg['message']}")
            if messages['count'] > 3:
                print(f"  ... 還有 {messages['count'] - 3} 條訊息")
        else:
            print(f"❌ 取得訊息失敗: {response.text}")
        
        # 5. 測試搜尋功能
        print("\n🔍 5. 測試搜尋功能...")
        search_data = {"keyword": "太空", "limit": 5}
        response = requests.post(
            f"{BASE_URL}/perception/youtube-chat/search",
            json=search_data
        )
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ 搜尋成功，找到 {search_results['count']} 條包含 '太空' 的訊息")
            for msg in search_results['messages']:
                print(f"  [{msg['author']}] {msg['message']}")
        else:
            print(f"❌ 搜尋失敗: {response.text}")
        
        # 6. 再次查詢狀態
        print("\n📊 6. 再次查詢監控狀態...")
        response = requests.get(f"{BASE_URL}/perception/youtube-chat/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ 當前狀態: 監控中={status['monitoring']}, 訊息數={status['message_count']}")
        
        # 7. 測試停止監控
        print("\n🛑 7. 測試停止監控...")
        response = requests.post(f"{BASE_URL}/perception/youtube-chat/stop")
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 停止監控成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 停止監控失敗: {response.text}")
        
        # 8. 確認停止狀態
        print("\n📊 8. 確認停止狀態...")
        response = requests.get(f"{BASE_URL}/perception/youtube-chat/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ 停止後狀態: 監控中={status['monitoring']}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務，請確認後端是否已啟動")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 YouTube 聊天室監控功能測試完成")


def test_specific_features():
    """測試特定功能"""
    
    print("\n🧪 測試特定功能...")
    
    # 測試清空緩衝區
    print("\n🗑️ 測試清空訊息緩衝區...")
    response = requests.delete(f"{BASE_URL}/perception/youtube-chat/clear")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 清空成功: {result['message']}")
    else:
        print(f"❌ 清空失敗: {response.text}")


def test_url_parsing():
    """測試 URL 解析功能"""
    
    print("\n🔗 測試 URL 解析功能...")
    
    test_urls = [
        "https://youtube.com/live/vs4gTWg5pGk?feature=share",
        "https://www.youtube.com/watch?v=vs4gTWg5pGk",
        "https://youtu.be/vs4gTWg5pGk",
        "vs4gTWg5pGk"  # 直接使用 video_id
    ]
    
    for url in test_urls:
        print(f"\n測試 URL: {url}")
        start_data = {"video_url_or_id": url}
        response = requests.post(
            f"{BASE_URL}/perception/youtube-chat/start",
            json=start_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ URL 解析成功: video_id = {result.get('video_id')}")
            # 立即停止
            requests.post(f"{BASE_URL}/perception/youtube-chat/stop")
        else:
            print(f"❌ URL 解析失敗: {response.text}")


if __name__ == "__main__":
    print("🚀 YouTube 聊天室監控功能測試")
    print("請確認後端服務已啟動 (python main.py)")
    print("測試將使用您的直播網址: https://youtube.com/live/vs4gTWg5pGk")
    
    input("\n按 Enter 開始測試...")
    
    # 執行主要測試
    test_youtube_chat_monitor()
    
    # 測試特定功能
    test_specific_features()
    
    # 測試 URL 解析
    test_url_parsing()
    
    print("\n✨ 所有測試完成！")
    print("\n📋 使用說明：")
    print("1. 使用 POST /api/perception/youtube-chat/start 開始監控")
    print("2. 使用 GET /api/perception/youtube-chat/messages 取得最新訊息")
    print("3. 使用 POST /api/perception/youtube-chat/search 搜尋特定內容")
    print("4. 使用 GET /api/perception/youtube-chat/status 查詢狀態")
    print("5. 使用 POST /api/perception/youtube-chat/stop 停止監控")