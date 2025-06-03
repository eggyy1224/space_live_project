#!/bin/bash

# 實驗腳本 2: 動感戰鬥場景
# 著重展示重金屬背景及激烈鏡位切換

BASE_URL="http://localhost:8000/api"

# 熱血開場台詞
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "準備迎接最震撼的太空戰鬥！", "message_type": "chat-message"}' | jq .

# 切換到重金屬 BGM 並加入加速音效
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3", "sfxUrl": "/audio/effects/Energetic_fast_pace.mp3"}' | jq .

# 荷蘭角鏡位營造緊張感
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 10, "yaw": 30, "roll": 25, "duration": 1.5}' | jq .

# 在第二螢幕播放星際小可愛影片
curl -X PUT "$BASE_URL/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/星際小可愛.mp4", "visible": true, "volume": 0.8}' | jq .

sleep 1

# 播放暴龍吼叫音效加強氣勢
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/暴龍吼叫.mp3", "interrupt": false}' | jq .

# 主角施展 breaking 動畫
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation": "breaking", "loop": true, "transitionDuration": 0.2}' | jq .

# 情緒轉為憤怒
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 3.0, "keyframes": [{"tag": "neutral", "proportion": 0.0}, {"tag": "angry", "proportion": 1.0}]}' | jq .

sleep 3

# 背景 murmurs 營造戰場氛圍
curl -X POST "$BASE_URL/control/trigger-murmur" \
  -H "Content-Type: application/json" \
  -d '{"topic": "battle", "force": true}' | jq .

sleep 2

# 在第三螢幕播放黑洞畫面做結尾
curl -X PUT "$BASE_URL/monitors/screen3" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/黑洞.mp4", "visible": true}' | jq .

# 最後提醒觀眾
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "戰鬥結束，感謝收看！", "message_type": "chat-message"}' | jq .


