#!/usr/bin/env python3
"""
運行所有角色控制相關的整合測試
"""

import asyncio
import subprocess
import sys
import time
from datetime import datetime


def run_test_script(script_name: str) -> bool:
    """運行單個測試腳本"""
    print(f"\n{'='*60}")
    print(f"🚀 開始運行: {script_name}")
    print(f"{'='*60}")
    
    try:
        # 運行測試腳本
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, timeout=300)  # 5分鐘超時
        
        if result.returncode == 0:
            print(f"✅ {script_name} 測試通過")
            print(f"標準輸出:\n{result.stdout}")
            return True
        else:
            print(f"❌ {script_name} 測試失敗")
            print(f"錯誤輸出:\n{result.stderr}")
            print(f"標準輸出:\n{result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name} 測試超時")
        return False
    except Exception as e:
        print(f"💥 運行 {script_name} 時發生錯誤: {e}")
        return False


def generate_test_report(results: dict):
    """生成測試報告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# 角色控制整合測試報告

## 測試時間
{timestamp}

## 測試結果總覽
"""
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    failed_tests = total_tests - passed_tests
    
    report += f"""
- 總測試數: {total_tests}
- 通過測試: {passed_tests}
- 失敗測試: {failed_tests}
- 成功率: {(passed_tests/total_tests*100):.1f}%

## 詳細結果

"""
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        report += f"- **{test_name}**: {status}\n"
    
    report += f"""
## 測試說明

### test_character_control_endpoints.py
全面測試角色控制 API 端點，包括：
- 角色縮放控制 (0.1-3.0)
- 位置控制 (3D 座標)
- 旋轉控制 (3軸旋轉)
- 服裝控制 (morph targets)
- 動畫控制
- 可見性控制
- 變換重置
- 狀態查詢
- 錯誤處理

### test_outfit_morphtargets.py
專項測試 outfit_shoes030_1 服裝變形，包括：
- 個別 morph target 控制
- 組合 morph target 設置
- 漸進式變形效果
- 極值和邊界測試
- 快速變化響應
- 服裝預設組合

## 備註
所有測試都需要前端和後端服務同時運行。
WebSocket 連接正常時，測試結果更加可靠。
"""
    
    # 寫入報告文件
    with open("test_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📊 測試報告已生成: test_report.md")


def main():
    """主函數"""
    print("🎬 開始運行角色控制整合測試套件")
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定義要運行的測試腳本
    test_scripts = [
        "test_character_control_endpoints.py",
        "test_outfit_morphtargets.py"
    ]
    
    results = {}
    
    print(f"\n🎯 將運行 {len(test_scripts)} 個測試腳本")
    
    for script in test_scripts:
        print(f"\n⏳ 準備運行 {script}...")
        time.sleep(2)  # 給前一個測試一些緩衝時間
        
        success = run_test_script(script)
        results[script] = success
        
        if success:
            print(f"🎉 {script} 完成")
        else:
            print(f"😞 {script} 失敗")
        
        time.sleep(3)  # 測試間隔
    
    # 顯示總結
    print(f"\n{'='*60}")
    print("📋 測試總結")
    print(f"{'='*60}")
    
    for script, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {script}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"\n📊 總計: {passed_tests}/{total_tests} 測試通過")
    
    if passed_tests == total_tests:
        print("🎉 所有測試都通過了！角色控制功能運作正常！")
        exit_code = 0
    else:
        print("⚠️  有測試失敗，請檢查詳細輸出")
        exit_code = 1
    
    # 生成測試報告
    generate_test_report(results)
    
    print(f"\n🏁 測試套件完成，結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 