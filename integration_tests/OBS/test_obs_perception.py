#!/usr/bin/env python3
"""
OBS Perception 模組測試腳本

用於測試 OBS 截圖功能和 API 端點
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def test_obs_status():
    """測試 OBS 狀態查詢"""
    print("=== 測試 OBS 狀態查詢 ===")
    try:
        response = requests.get(f"{BASE_URL}/perception/obs/status")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def test_obs_scenes():
    """測試取得場景列表"""
    print("\n=== 測試場景列表查詢 ===")
    try:
        response = requests.get(f"{BASE_URL}/perception/obs/scenes")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def test_obs_sources():
    """測試取得來源列表"""
    print("\n=== 測試來源列表查詢 ===")
    try:
        response = requests.get(f"{BASE_URL}/perception/obs/sources")
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def test_obs_screenshot():
    """測試 OBS 截圖功能"""
    print("\n=== 測試 OBS 截圖功能 ===")
    try:
        # 基本截圖測試
        payload = {
            "width": 1280,
            "height": 720,
            "image_format": "png"
        }
        
        response = requests.post(
            f"{BASE_URL}/perception/obs/screenshot",
            json=payload
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("filename"):
                print(f"截圖成功！檔案: {result['filename']}")
                
                # 測試檔案下載
                download_response = requests.get(
                    f"{BASE_URL}/perception/obs/screenshot/{result['filename']}"
                )
                
                if download_response.status_code == 200:
                    print("檔案下載測試成功！")
                    return True
                else:
                    print(f"檔案下載失敗: {download_response.status_code}")
                    return False
            else:
                print("截圖失敗")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def test_obs_connection_config():
    """測試 OBS 連接設定"""
    print("\n=== 測試 OBS 連接設定 ===")
    try:
        payload = {
            "host": "localhost",
            "port": 4455,
            "password": "",
            "timeout": 10
        }
        
        response = requests.post(
            f"{BASE_URL}/perception/obs/connection",
            json=payload
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("開始測試 OBS Perception 模組...")
    print("確保 OBS Studio 已開啟並啟用 WebSocket 服務 (端口 4455)")
    print("確保後端服務已啟動 (http://localhost:8000)")
    
    input("按 Enter 鍵開始測試...")
    
    tests = [
        ("OBS 狀態查詢", test_obs_status),
        ("OBS 連接設定", test_obs_connection_config),
        ("場景列表查詢", test_obs_scenes),
        ("來源列表查詢", test_obs_sources),
        ("OBS 截圖功能", test_obs_screenshot),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"執行測試: {test_name}")
        print(f"{'='*50}")
        
        result = test_func()
        results.append((test_name, result))
        
        if result:
            print(f"✅ {test_name} - 通過")
        else:
            print(f"❌ {test_name} - 失敗")
        
        time.sleep(1)  # 稍微等待
    
    # 測試結果摘要
    print(f"\n{'='*50}")
    print("測試結果摘要")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    print(f"\n總計: {passed}/{total} 個測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過了！")
    else:
        print("⚠️  有部分測試失敗，請檢查相關設定")

if __name__ == "__main__":
    main() 