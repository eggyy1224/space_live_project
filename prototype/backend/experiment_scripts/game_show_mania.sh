#!/bin/bash

# 實驗腳本: 星際綜藝遊戲秀
# 快節奏互動與搞笑鏡位

BASE_URL="http://localhost:8000/api"

echo "=== 星際綜藝遊戲秀開場 ==="

# 熱鬧 BGM 與效果音
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"}' | jq .

sleep 1

# 標準主持人鏡位
curl -X POST "$BASE_URL/control/camera/set-angle" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 0, "roll": 0}' | jq .

sleep 1

# 螢幕1顯示節目畫面
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/太空直播中.mp4", "visible": true, "playing": true, "volume": 0}' | jq .

sleep 1

# 熱情歡迎詞
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "歡迎來到星際綜藝！今天的競賽即將開始～"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "happy", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}' | jq .

sleep 4

# 動感鏡位切換
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": -10, "yaw": 25, "roll": 0, "duration": 2.0}' | jq .

sleep 2

# 歡呼音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/鳥叫.mp3", "volume": 0.2}' | jq .

sleep 1

# Flair 動畫炒熱氣氛
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation_id": "Flair", "loop": false}' | jq .

sleep 3

# 螢幕2顯示計分板
curl -X PUT "$BASE_URL/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/太空瑜伽.mp4", "visible": true, "playing": true, "volume": 0.3}' | jq .

sleep 5

# 360 度鏡位炫技
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 360, "roll": 0, "duration": 4.0}' | jq .

sleep 4

# 結束致詞
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "恭喜參賽者獲勝！感謝各位觀眾收看，下次再會～"}' | jq .

curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "happy", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}' | jq .

sleep 5
