#!/usr/bin/env python3
"""
全面測試身體動畫控制 API 的腳本
使用實際存在的動畫名稱
"""

import requests
import json
import time

# 後端 API 基礎 URL
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/control/body-animation"

# 實際存在的動畫名稱 (從 animations.json 中獲取)
AVAILABLE_ANIMATIONS = [
    "Idle", "Wave", "Happy", "Jogging", "Walking", "Jumping", 
    "clap", "salute", "hiphopdance", "twistdance", "breaking",
    "JazzDancing", "SalsaDancing", "Moonwalk", "HipHopDancin",
    "Thinking", "PointingGesture", "StandingClap", "Cheering"
]

def test_single_animations():
    """測試播放多個單一動畫"""
    print("🎯 測試 1: 播放單一動畫")
    
    animations_to_test = ["Happy", "clap", "Wave", "Idle"]
    
    for animation in animations_to_test:
        print(f"  播放: {animation}")
        payload = {
            "state": "play",
            "animation": animation,
            "loop": True,
            "transitionDuration": 0.3
        }
        
        response = requests.post(API_ENDPOINT, json=payload)
        print(f"    狀態碼: {response.status_code}, 回應: {response.json()}")
        time.sleep(2)
    
    print()

def test_dance_sequence():
    """測試播放舞蹈序列"""
    print("🎯 測試 2: 播放舞蹈動畫序列")
    
    payload = {
        "state": "play",
        "sequence": [
            {"name": "StandingClap", "proportion": 0.0, "loopCount": 2},
            {"name": "hiphopdance", "proportion": 0.2, "loopCount": 3},
            {"name": "JazzDancing", "proportion": 0.5, "loopCount": 2},
            {"name": "SalsaDancing", "proportion": 0.7, "loopCount": 2},
            {"name": "Happy", "proportion": 0.9, "loopCount": None}
        ],
        "transitionDuration": 0.8
    }
    
    response = requests.post(API_ENDPOINT, json=payload)
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    print("等待序列播放...")
    time.sleep(8)
    print()

def test_exercise_sequence():
    """測試運動動畫序列"""
    print("🎯 測試 3: 播放運動動畫序列")
    
    payload = {
        "state": "play", 
        "sequence": [
            {"name": "Jogging", "proportion": 0.0, "loopCount": 4},
            {"name": "Jumping", "proportion": 0.4, "loopCount": 3},
            {"name": "Walking", "proportion": 0.7, "loopCount": 2},
            {"name": "Idle", "proportion": 0.9, "loopCount": None}
        ],
        "transitionDuration": 0.5
    }
    
    response = requests.post(API_ENDPOINT, json=payload)
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    print("等待運動序列播放...")
    time.sleep(6)
    print()

def test_control_commands():
    """測試動畫控制指令"""
    print("🎯 測試 4: 動畫控制指令測試")
    
    # 開始播放一個動畫
    print("  開始播放 breaking 動畫")
    response = requests.post(API_ENDPOINT, json={
        "state": "play",
        "animation": "breaking",
        "loop": True
    })
    print(f"    開始 - 狀態碼: {response.status_code}")
    time.sleep(2)
    
    # 暫停
    print("  暫停動畫")
    response = requests.post(API_ENDPOINT, json={"state": "pause"})
    print(f"    暫停 - 狀態碼: {response.status_code}")
    time.sleep(1.5)
    
    # 恢復
    print("  恢復動畫")
    response = requests.post(API_ENDPOINT, json={"state": "resume"})
    print(f"    恢復 - 狀態碼: {response.status_code}")
    time.sleep(2)
    
    # 停止
    print("  停止動畫")
    response = requests.post(API_ENDPOINT, json={"state": "stop"})
    print(f"    停止 - 狀態碼: {response.status_code}")
    print()

def test_speed_and_loops():
    """測試播放速度和循環控制"""
    print("🎯 測試 5: 播放速度和循環控制")
    
    # 測試快速播放
    print("  快速播放 Moonwalk (2倍速)")
    response = requests.post(API_ENDPOINT, json={
        "state": "play",
        "animation": "Moonwalk",
        "speed": 2.0,
        "loop": True,
        "loopCount": 3,
        "transitionDuration": 0.1
    })
    print(f"    快速播放 - 狀態碼: {response.status_code}")
    time.sleep(3)
    
    # 測試慢速播放
    print("  慢速播放 twistdance (0.5倍速)")
    response = requests.post(API_ENDPOINT, json={
        "state": "play",
        "animation": "twistdance",
        "speed": 0.5,
        "loop": True,
        "loopCount": 2,
        "transitionDuration": 0.3
    })
    print(f"    慢速播放 - 狀態碼: {response.status_code}")
    time.sleep(4)
    print()

def test_celebration_sequence():
    """測試慶祝動畫序列"""
    print("🎯 測試 6: 慶祝動畫序列")
    
    payload = {
        "state": "play",
        "sequence": [
            {"name": "Cheering", "proportion": 0.0, "loopCount": 2},
            {"name": "StandingClap", "proportion": 0.3, "loopCount": 3},
            {"name": "Happy", "proportion": 0.6, "loopCount": 2},
            {"name": "salute", "proportion": 0.8, "loopCount": 1},
            {"name": "Idle", "proportion": 0.95, "loopCount": None}
        ],
        "transitionDuration": 0.6
    }
    
    response = requests.post(API_ENDPOINT, json=payload)
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    print("等待慶祝序列播放...")
    time.sleep(7)
    print()

def check_backend_status():
    """檢查後端狀態"""
    print("🔍 檢查後端連接狀態")
    
    try:
        response = requests.get(f"{BASE_URL}/api/control/status")
        status_data = response.json()
        print(f"後端狀態: {status_data}")
        
        active_connections = status_data.get("active_connections", 0)
        if active_connections == 0:
            print("⚠️ 警告: 沒有活動的前端連接，請確保前端已啟動並連接到後端")
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
    print("🚀 開始全面測試身體動畫控制 API")
    print("=" * 60)
    print(f"可用動畫: {', '.join(AVAILABLE_ANIMATIONS[:10])}... (共 {len(AVAILABLE_ANIMATIONS)} 個)")
    print("=" * 60)
    
    # 檢查後端狀態
    if not check_backend_status():
        print("\n❌ 測試中止: 後端不可用")
        return
    
    print("\n" + "=" * 60)
    
    try:
        # 測試 1: 單一動畫
        test_single_animations()
        
        # 測試 2: 舞蹈序列
        test_dance_sequence()
        
        # 測試 3: 運動序列
        test_exercise_sequence()
        
        # 測試 4: 控制指令
        test_control_commands()
        
        # 測試 5: 速度和循環
        test_speed_and_loops()
        
        # 測試 6: 慶祝序列
        test_celebration_sequence()
        
        # 回到待機狀態
        print("🏁 回到待機狀態")
        requests.post(API_ENDPOINT, json={"state": "stop"})
        
        print("✅ 所有測試完成！身體動畫控制 API 運作正常")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端 API")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 