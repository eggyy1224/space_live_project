#!/usr/bin/env python3
"""
角色動畫混合功能測試腳本

測試新實現的動畫混合 API，驗證：
1. 基本動畫混合功能
2. 權重調整
3. 混合模式切換
4. 與單一動畫模式的兼容性
"""

import requests
import time
import json
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

def test_single_animation():
    """測試單一動畫功能（確保向後兼容）"""
    print("🎯 測試單一動畫功能...")
    
    response = requests.post(f"{BASE_URL}/api/control/character/animation", json={
        "animation": "Tpose",
        "loop": True,
        "speed": 1.0
    })
    
    if response.status_code == 200:
        print("✅ 單一動畫測試成功")
        return True
    else:
        print(f"❌ 單一動畫測試失敗: {response.status_code}")
        return False

def test_basic_animation_mix():
    """測試基本動畫混合"""
    print("🎭 測試基本動畫混合...")
    
    animations = [
        {"name": "運動1", "weight": 0.7, "loop": True, "speed": 1.0},
        {"name": "舞步1", "weight": 0.3, "loop": True, "speed": 1.2}
    ]
    
    response = requests.post(f"{BASE_URL}/api/control/character/animation-mix", json={
        "animations": animations,
        "transitionDuration": 0.5,
        "blendMode": "normal"
    })
    
    if response.status_code == 200:
        print("✅ 基本動畫混合測試成功")
        return True
    else:
        print(f"❌ 基本動畫混合測試失敗: {response.status_code}")
        print(response.text)
        return False

def test_complex_mix():
    """測試複雜動畫混合（3個動畫）"""
    print("🎪 測試複雜動畫混合...")
    
    animations = [
        {"name": "舞步1", "weight": 0.5, "speed": 1.0},
        {"name": "舞步2", "weight": 0.3, "speed": 0.8},
        {"name": "漂浮", "weight": 0.2, "speed": 1.5}
    ]
    
    response = requests.post(f"{BASE_URL}/api/control/character/animation-mix", json={
        "animations": animations,
        "blendMode": "normal"
    })
    
    if response.status_code == 200:
        print("✅ 複雜動畫混合測試成功")
        return True
    else:
        print(f"❌ 複雜動畫混合測試失敗: {response.status_code}")
        print(response.text)
        return False

def test_weight_validation():
    """測試權重驗證"""
    print("⚖️ 測試權重驗證...")
    
    # 測試無效權重
    invalid_animations = [
        {"name": "運動1", "weight": 1.5},  # 超過 1.0
        {"name": "舞步1", "weight": -0.1}  # 小於 0.0
    ]
    
    response = requests.post(f"{BASE_URL}/api/control/character/animation-mix", json={
        "animations": invalid_animations
    })
    
    if response.status_code == 400:
        print("✅ 權重驗證測試成功（正確拒絕無效權重）")
        return True
    else:
        print(f"❌ 權重驗證測試失敗: 應該返回 400，實際返回 {response.status_code}")
        return False

def test_animation_sequence():
    """測試動畫序列演示"""
    print("🎬 執行動畫序列演示...")
    
    scenarios = [
        {
            "name": "太空漂浮混合",
            "animations": [
                {"name": "漂浮", "weight": 0.8},
                {"name": "運動1", "weight": 0.2}
            ],
            "duration": 3
        },
        {
            "name": "舞蹈組合",
            "animations": [
                {"name": "舞步1", "weight": 0.6, "speed": 1.2},
                {"name": "舞步3", "weight": 0.4, "speed": 0.9}
            ],
            "duration": 4
        },
        {
            "name": "運動變化",
            "animations": [
                {"name": "運動2", "weight": 0.7},
                {"name": "不穩", "weight": 0.3}
            ],
            "duration": 3
        }
    ]
    
    for scenario in scenarios:
        print(f"  📱 播放: {scenario['name']}")
        
        response = requests.post(f"{BASE_URL}/api/control/character/animation-mix", json={
            "animations": scenario["animations"],
            "blendMode": "normal"
        })
        
        if response.status_code == 200:
            print(f"    ✅ {scenario['name']} 播放成功")
            time.sleep(scenario["duration"])
        else:
            print(f"    ❌ {scenario['name']} 播放失敗")
    
    # 最後回到單一動畫
    print("  🎯 回到單一動畫模式")
    requests.post(f"{BASE_URL}/api/control/character/animation", json={
        "animation": "Tpose"
    })

def main():
    """主測試函數"""
    print("🚀 角色動畫混合測試開始")
    print("=" * 50)
    
    tests = [
        ("單一動畫兼容性", test_single_animation),
        ("基本動畫混合", test_basic_animation_mix),
        ("複雜動畫混合", test_complex_mix),
        ("權重驗證", test_weight_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 執行測試: {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print(f"\n{'=' * 50}")
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！開始演示...")
        test_animation_sequence()
    else:
        print("⚠️ 部分測試失敗，請檢查實現")
    
    print("\n✨ 測試完成")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務器，請確保服務器運行在 http://localhost:8000")
    except KeyboardInterrupt:
        print("\n🛑 測試被用戶中斷")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}") 