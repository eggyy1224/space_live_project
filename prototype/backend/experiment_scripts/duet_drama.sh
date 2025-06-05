#!/bin/bash

# 實驗腳本: 雙人對話劇
# 展示多角色對話與鏡位切換

BASE_URL="http://localhost:8000/api"

echo "=== 雙人對話劇 ==="

# 柔和背景音樂
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/spacelive_theme2.mp3", "bgmVolume": 0.4}' | jq .

sleep 1

# A 登場
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "A: 你好，B。我們終於在這片星空下相遇。"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "happy", "proportion": 0.0}, {"tag": "interested", "proportion": 1.0}]}' | jq .

sleep 4

# 切換至 B 的視角
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 5, "yaw": -20, "roll": 0, "duration": 2.0}' | jq .

sleep 2

# B 回應
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "B: A，是命運指引我們到此，還是巧合？"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "confused", "proportion": 0.0}, {"tag": "thoughtful", "proportion": 1.0}]}' | jq .

sleep 4

# 鏡頭再次轉換
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 20, "roll": 0, "duration": 2.0}' | jq .

sleep 2

# 動作表示和解
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation_id": "FemaleStandingPose", "loop": false}' | jq .

sleep 2

# A 的決心
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "A: 不論答案如何，讓我們共同完成這段旅程。"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "happy", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}' | jq .

sleep 5

# 鏡頭緩緩拉遠
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": -5, "yaw": 0, "roll": 0, "duration": 3.0}' | jq .

sleep 3
