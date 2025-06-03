#!/bin/bash

# 實驗腳本 3: 靜謐反思場景
# 以柔和音樂與慢節奏鏡位展示情緒過渡

BASE_URL="http://localhost:8000/api"

# 靜夜開場
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "夜深了，一起聆聽宇宙的低語。", "message_type": "chat-message"}' | jq .

# 播放輕柔 BGM 與微風音效
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{"bgmUrl": "/audio/BGM/space_live_country_theme1.mp3", "sfxUrl": "/audio/effects/winds_blowing.mp3"}' | jq .

# 鏡位緩慢轉向上方
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": -15, "yaw": 10, "roll": 0, "duration": 3.0}' | jq .

# 在第三螢幕播放黑洞影片
curl -X PUT "$BASE_URL/monitors/screen3" \
  -H "Content-Type: application/json" \
  -d '{"content": "/videos/黑洞.mp4", "visible": true, "volume": 0.6}' | jq .

sleep 2

# 播放鍵盤環境聲
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{"url": "/songs-file/Ambient_keyboard_cli.mp3", "interrupt": false}' | jq .

# 執行思考姿勢動畫
curl -X POST "$BASE_URL/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{"animation": "Thinking", "loop": false, "transitionDuration": 0.4}' | jq .

# 情緒逐漸轉為平靜
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{"duration": 5.0, "keyframes": [{"tag": "sad", "proportion": 0.0}, {"tag": "serene", "proportion": 1.0}]}' | jq .

sleep 5

# murmur 自言自語
curl -X POST "$BASE_URL/control/trigger-murmur" \
  -H "Content-Type: application/json" \
  -d '{"topic": "loneliness", "force": true}' | jq .

sleep 3

# 影片淡出
curl -X PUT "$BASE_URL/monitors/screen3" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}' | jq .

# 結尾致謝並回復正面鏡位
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{"content": "感謝陪伴，願你我都能在寧靜中找到力量。", "message_type": "chat-message"}' | jq .

curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{"pitch": 0, "yaw": 0, "roll": 0, "duration": 2.0}' | jq .


