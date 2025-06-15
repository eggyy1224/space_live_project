#!/bin/bash

# 環境光照控制API測試腳本
# 用法: ./test_environment_api.sh

API_BASE="http://localhost:8000"

echo "=== 環境光照控制API測試 ==="
echo

# 1. 檢查連接狀態
echo "1. 檢查前端連接狀態..."
curl -s -X GET "$API_BASE/api/control/status" | jq '.'
echo
sleep 1

# 2. 設定環境預設為日落
echo "2. 設定環境預設為日落..."
curl -s -X POST "$API_BASE/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "sunset"}' | jq '.'
echo
sleep 2

# 3. 調整光照強度為2倍
echo "3. 調整光照強度為2倍..."
curl -s -X POST "$API_BASE/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 2.0}' | jq '.'
echo
sleep 2

# 4. 開啟環境背景
echo "4. 開啟環境背景..."
curl -s -X POST "$API_BASE/api/control/environment/background" \
  -H "Content-Type: application/json" \
  -d '{"background": true}' | jq '.'
echo
sleep 2

# 5. 批量配置 - 切換到夜晚模式
echo "5. 批量配置 - 切換到夜晚模式..."
curl -s -X POST "$API_BASE/api/control/environment/config" \
  -H "Content-Type: application/json" \
  -d '{"preset": "night", "intensity": 1.5, "background": true}' | jq '.'
echo
sleep 3

# 6. 測試不同預設
echo "6. 測試不同環境預設..."
PRESETS=("studio" "forest" "warehouse" "city" "park")

for preset in "${PRESETS[@]}"; do
  echo "   設定預設: $preset"
  curl -s -X POST "$API_BASE/api/control/environment/preset" \
    -H "Content-Type: application/json" \
    -d "{\"preset\": \"$preset\"}" | jq -r '.message'
  sleep 1.5
done
echo

# 7. 測試強度範圍
echo "7. 測試強度範圍..."
INTENSITIES=(0.3 1.0 2.5)

for intensity in "${INTENSITIES[@]}"; do
  echo "   設定強度: $intensity"
  curl -s -X POST "$API_BASE/api/control/environment/intensity" \
    -H "Content-Type: application/json" \
    -d "{\"intensity\": $intensity}" | jq -r '.message'
  sleep 1
done
echo

# 8. 查詢環境狀態
echo "8. 查詢環境狀態..."
curl -s -X GET "$API_BASE/api/control/environment/status" | jq '.'
echo
sleep 1

# 9. 重置到預設值
echo "9. 重置到預設值..."
curl -s -X POST "$API_BASE/api/control/environment/reset" \
  -H "Content-Type: application/json" \
  -d '{"reset_to_defaults": true}' | jq '.'
echo

# 10. 錯誤測試 - 無效預設
echo "10. 錯誤測試 - 無效預設..."
curl -s -X POST "$API_BASE/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "invalid_preset"}' | jq '.'
echo

# 11. 錯誤測試 - 超出範圍的強度
echo "11. 錯誤測試 - 超出範圍的強度..."
curl -s -X POST "$API_BASE/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 5.0}' | jq '.'
echo

echo "=== 測試完成 ==="
echo "如果前端已連接，你應該看到環境光照的即時變化！" 