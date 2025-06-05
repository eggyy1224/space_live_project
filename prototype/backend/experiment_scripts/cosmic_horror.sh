#!/bin/bash

# 實驗腳本: 宇宙恐怖降臨
# 展示極端鏡位與恐懼情緒

BASE_URL="http://localhost:8000/api"

echo "=== 宇宙恐怖降臨 ==="

# 關閉 murmur 並停用隨機鏡頭
curl -X POST "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled": false}' | jq .
curl -X POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type": "director-state", "payload": {"randomMode": false}}' | jq .

# 幽暗 BGM 與風聲
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "sfxUrl": "/audio/effects/winds_blowing.mp3", "bgmVolume": 0.4, "sfxVolume": 0.5}' | jq .

sleep 1

# 螢幕1播放黑洞
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/黑洞.mp4", "visible": true, "playing": true, "volume": 0.7}' | jq .

sleep 1

# 初始鏡位
curl -X POST "$BASE_URL/control/camera/set-angle" \
  -H "Content-Type: application/json" \
  -d '{"pitch": -5, "yaw": -20, "roll": 0}' | jq .

sleep 1

# 恐懼獨白
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "我感受到來自宇宙深處的低語… 不祥的預兆在逼近。"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "fear", "proportion": 0.0}, {"tag": "shocked", "proportion": 1.0}]}' | jq .

sleep 5

# 暴龍吼叫音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/暴龍吼叫.mp3", "volume": 0.5}' | jq .

sleep 1

# 荷蘭角鏡位
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 15, "yaw": 40, "roll": 45, "duration": 2.5}' | jq .

sleep 3

# 驚恐步伐動畫
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation_id": "InjuredWalk", "loop": false}' | jq .

sleep 6

# 撤離宣告
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "黑暗正在侵蝕這片空間，我們必須撤離！"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "fear", "proportion": 0.0}, {"tag": "panic", "proportion": 1.0}]}' | jq .

sleep 5
