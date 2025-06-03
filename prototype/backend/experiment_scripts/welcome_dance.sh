#!/bin/bash

# 實驗腳本 1: 歡迎舞蹈示範
# 利用各項 API 功能展示基本互動流程

BASE_URL="http://localhost:8000/api"

# 關閉 murmur 以免干擾
curl -X POST "$BASE_URL/control/murmur-mode" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}' | jq .

sleep 1

# 開場問候
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "大家好，歡迎來到太空舞台！", "message_type": "chat-message"}' | jq .

# 播放歡迎 BGM 與艙內環境音
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"}' | jq .

sleep 2

# 正面鏡位
curl -X POST "$BASE_URL/control/camera/set-angle" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 0, "roll": 0}' | jq .

# 螢幕播放太空熱舞影片
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/太空熱舞.mp4", "visible": true}' | jq .

sleep 1

# 主角揮手致意
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation": "Wave", "loop": false, "transitionDuration": 0.3}' | jq .

# 情緒從 neutral 轉為 happy
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 4.0, "keyframes": [{"tag": "neutral", "proportion": 0.0}, {"tag": "happy", "proportion": 1.0}]}' | jq .

sleep 4

# 播放短暫歌聲
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/male_vocal.mp3", "interrupt": false}' | jq .

sleep 2

# 接續介紹並轉為側面鏡位
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "接下來為各位示範太空熱舞！", "message_type": "chat-message"}' | jq .

curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 5, "yaw": 45, "roll": 0, "duration": 2.0}' | jq .

# 觸發 murmur 以增添氣氛
curl -X POST "$BASE_URL/control/trigger-murmur" \
  -H "Content-Type: application/json" \
  -d '{"topic": "warmup", "force": true}' | jq .

sleep 3

# 結束並停止螢幕播放
curl -X PUT "$BASE_URL/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}' | jq .

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "歡迎各位稍後繼續觀賞！", "message_type": "chat-message"}' | jq .


