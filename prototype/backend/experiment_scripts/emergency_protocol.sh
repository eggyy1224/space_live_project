#!/bin/bash

# 實驗腳本: 緊急撤離程序
# 高張力警報場景

BASE_URL="http://localhost:8000/api"

echo "=== 緊急撤離程序啟動 ==="

# 停用隨機鏡位
curl -X POST "$BASE_URL/control/broadcast" \
  -H "Content-Type: application/json" \
  -d '{"type": "director-state", "payload": {"randomMode": false}}' | jq .

# 警報 BGM 及快節奏音效
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3", "sfxUrl": "/audio/effects/Energetic_fast_pace.mp3"}' | jq .

sleep 1

# 螢幕顯示警告圖像
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/模擬星雲圖.mp4", "visible": true, "playing": true, "volume": 0.9}' | jq .

sleep 1

# 發出警告台詞
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "警報！系統檢測到未知能量衝擊，請立即撤離！"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "panic", "proportion": 0.0}, {"tag": "fear", "proportion": 1.0}]}' | jq .

sleep 4

# 激烈鏡位切換
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 20, "yaw": -30, "roll": -20, "duration": 1.5}' | jq .

sleep 2

# 閃避動作
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation_id": "AerialEvade", "loop": false}' | jq .

sleep 5

# 播放警示音
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/暴龍吼叫.mp3", "interrupt": false}' | jq .

sleep 3

# 終極撤離指令
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "所有人員請就位，準備啟動緊急逃生艙！"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "fear", "proportion": 0.0}, {"tag": "determined", "proportion": 1.0}]}' | jq .

sleep 5
