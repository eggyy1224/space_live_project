#!/bin/bash

# 實驗腳本: 星光浪漫之夜
# 柔和鏡位與浪漫情緒

BASE_URL="http://localhost:8000/api"

echo "=== 星光浪漫之夜 ==="

# 播放浪漫 BGM 與微風
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/space_live_country_theme1.mp3", "sfxUrl": "/audio/effects/winds_blowing.mp3", "bgmVolume": 0.5, "sfxVolume": 0.2}' | jq .

sleep 1

# 緩慢抬頭望向星空
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": -10, "yaw": 15, "roll": 0, "duration": 3.0}' | jq .

sleep 2

# 溫柔台詞與情緒
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "在滿天星斗下，讓我們靜靜感受彼此的心跳。"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "shy", "proportion": 0.0}, {"tag": "happy", "proportion": 1.0}]}' | jq .

sleep 5

# 角色開心舞動
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation_id": "Happy", "loop": true}' | jq .

sleep 2

# 螢幕2播放浪漫影片
curl -X PUT "$BASE_URL/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/太空瑜伽.mp4", "visible": true, "playing": true, "volume": 0.2}' | jq .

sleep 5

# 鳥鳴音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/鳥叫.mp3", "volume": 0.1}' | jq .

sleep 3

# 鏡頭回到溫柔正面
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": -5, "yaw": 0, "roll": 0, "duration": 2.0}' | jq .

sleep 2

# 告白台詞
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "願這片星海見證我們的故事。"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "happy", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}' | jq .

sleep 5
