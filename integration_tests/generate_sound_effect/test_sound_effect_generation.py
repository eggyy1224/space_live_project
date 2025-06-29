#!/usr/bin/env python3
"""
測試 ElevenLabs 音效生成功能
"""

import requests
import json
import os
import sys
import time

# 添加後端路徑到系統路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '../../prototype/backend'))

# 測試配置
BASE_URL = "http://localhost:8000"
GENERATE_ENDPOINT = f"{BASE_URL}/api/control/generate-sound-effect"

def test_sound_effect_generation():
    """測試音效生成功能"""
    
    print("🎵 測試 ElevenLabs 音效生成功能")
    print("=" * 50)
    
    # 測試案例（使用英文 prompt 獲得更好的音效品質）
    test_cases = [
        {
            "prompt": "spaceship engine humming and vibrating steadily",
            "duration_seconds": 3.0,
            "filename": "spaceship_engine_start",
            "play_immediately": True
        },
        {
            "prompt": "electronic malfunction with sparks crackling and warning beeps",
            "duration_seconds": 2.5,
            "filename": "electronic_malfunction",
            "play_immediately": False
        },
        {
            "prompt": "deep space ambient cosmic wind and distant rumbling",
            "duration_seconds": 4.0,
            "play_immediately": True
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n測試案例 {i}: {test_case['prompt']}")
        print("-" * 30)
        
        try:
            # 發送請求
            print(f"發送請求到: {GENERATE_ENDPOINT}")
            print(f"請求內容: {json.dumps(test_case, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                GENERATE_ENDPOINT,
                json=test_case,
                timeout=60
            )
            
            print(f"HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功! 檔案名: {result.get('filename', 'N/A')}")
                print(f"   檔案路徑: {result.get('file_path', 'N/A')}")
                print(f"   持續時間: {result.get('duration', 'N/A')} 秒")
                print(f"   立即播放: {result.get('played_immediately', 'N/A')}")
                
                results.append({
                    "test_case": i,
                    "status": "success",
                    "filename": result.get('filename'),
                    "file_path": result.get('file_path')
                })
            else:
                print(f"❌ 失敗! HTTP {response.status_code}")
                print(f"   錯誤訊息: {response.text}")
                
                results.append({
                    "test_case": i,
                    "status": "failed",
                    "error": response.text
                })
        
        except requests.exceptions.ConnectionError:
            print("❌ 連接錯誤: 無法連接到後端服務器")
            print("   請確認後端服務器運行在 http://localhost:8000")
            results.append({
                "test_case": i,
                "status": "connection_error"
            })
        
        except requests.exceptions.Timeout:
            print("❌ 請求超時")
            results.append({
                "test_case": i,
                "status": "timeout"
            })
        
        except Exception as e:
            print(f"❌ 意外錯誤: {str(e)}")
            results.append({
                "test_case": i,
                "status": "error",
                "error": str(e)
            })
        
        # 等待一下再進行下一個測試
        if i < len(test_cases):
            print("等待 2 秒後進行下一個測試...")
            time.sleep(2)
    
    # 測試結果總結
    print("\n" + "=" * 50)
    print("測試結果總結")
    print("=" * 50)
    
    success_count = len([r for r in results if r['status'] == 'success'])
    total_count = len(results)
    
    print(f"成功: {success_count}/{total_count}")
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_emoji} 測試案例 {result['test_case']}: {result['status']}")
        if result['status'] == 'success' and 'filename' in result:
            print(f"   檔案: {result['filename']}")
    
    # 檢查生成的文件
    generated_sounds_dir = "../../prototype/frontend/public/audio/generated_sounds"
    if os.path.exists(generated_sounds_dir):
        print(f"\n生成的音效文件:")
        for filename in os.listdir(generated_sounds_dir):
            if filename.endswith('.mp3'):
                file_path = os.path.join(generated_sounds_dir, filename)
                file_size = os.path.getsize(file_path)
                print(f"  📁 {filename} ({file_size} bytes)")
    
    return results

def check_backend_status():
    """檢查後端服務器狀態"""
    try:
        response = requests.get(f"{BASE_URL}/api/control/status", timeout=5)
        if response.status_code == 200:
            print("✅ 後端服務器運行正常")
            return True
        else:
            print(f"❌ 後端服務器狀態異常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到後端服務器")
        print("   請確認後端服務器運行在 http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ 檢查後端狀態時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    print("🚀 Space Live 音效生成測試")
    print("=" * 50)
    
    # 檢查後端狀態
    if not check_backend_status():
        print("\n請先啟動後端服務器:")
        print("cd prototype/backend && python main.py")
        return
    
    # 執行測試
    results = test_sound_effect_generation()
    
    print("\n測試完成！")

if __name__ == "__main__":
    main() 