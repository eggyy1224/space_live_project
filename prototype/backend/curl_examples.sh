#!/bin/bash

# 後端控制 API 使用範例
# 請確保後端服務正在運行 (http://localhost:8000)

BASE_URL="http://localhost:8000/api"

echo "=== 虛擬太空人後端控制 API 範例 ==="
echo

# 1. 檢查前端連接狀態
echo "1. 檢查前端連接狀態："
curl -X GET "$BASE_URL/control/status" \
  -H "Content-Type: application/json" | jq .
echo

# 2. 向前端發送消息 (模擬機器人說話)
echo "2. 向前端發送消息："
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "哈囉！這是透過 API 發送的消息～",
    "message_type": "chat-message"
  }' | jq .
echo

# 3. 觸發 murmur (自言自語)
echo "3. 觸發 murmur："
curl -X POST "$BASE_URL/control/trigger-murmur" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "太空生活",
    "force": true
  }' | jq .
echo

# 4. 播放音頻 (需要有效的音頻 URL)
echo "4. 播放音頻："
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio-file/example.mp3",
    "interrupt": false
  }' | jq .
echo

# 5. 發送情緒軌跡
echo "5. 發送情緒軌跡："
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"time": 0, "emotion": "neutral", "intensity": 0.5},
      {"time": 1.5, "emotion": "happy", "intensity": 0.8},
      {"time": 3.0, "emotion": "neutral", "intensity": 0.5}
    ]
  }' | jq .
echo

# 6. 廣播自定義消息
echo "6. 廣播自定義消息："
curl -X POST "$BASE_URL/control/broadcast" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "custom-event",
    "payload": {
      "action": "test",
      "data": "這是自定義事件"
    }
  }' | jq .
echo

# 7. 控制背景音訊
echo "7. 控制背景音訊："
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio-file/example.mp3",
    "sfxUrl": "/audio-file/example.mp3"
  }' | jq .
echo

# 8. 切換 murmur 模式
echo "8. 切換 murmur 模式："
curl -X POST "$BASE_URL/control/murmur-mode" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }' | jq .
echo

# 9. 設定相機角度
echo "9. 設定相機角度："
curl -X POST "$BASE_URL/control/camera/set-angle" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 10,
    "yaw": 45,
    "roll": 0
  }' | jq .
echo

# 10. 相機角度平滑轉場
echo "10. 相機角度平滑轉場："
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0,
    "yaw": 90,
    "roll": 0,
    "duration": 2
  }' | jq .
echo

# 11. 儲存相機預設
echo "11. 儲存相機預設："
curl -X POST "$BASE_URL/control/camera/save-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo",
    "pitch": 0,
    "yaw": 0,
    "roll": 0
  }' | jq .
echo

# 12. 載入相機預設
echo "12. 載入相機預設："
curl -X POST "$BASE_URL/control/camera/load-preset?name=demo&duration=1" \
  -H "Content-Type: application/json" | jq .
echo

# 13. 健康檢查
echo "13. 健康檢查："
curl -X GET "$BASE_URL/health" \
  -H "Content-Type: application/json" | jq .
echo

echo "=== 使用說明 ==="
echo "• 確保前端已開啟並連接到 WebSocket"
echo "• 安裝 jq 來美化 JSON 輸出: brew install jq (macOS)"
echo "• 修改 BASE_URL 如果你的後端不在 localhost:8000"
echo "• 所有 API 都支援 CORS，可以從瀏覽器直接呼叫"
echo

echo "=== 快速測試指令 ==="
echo "# 快速發送一條消息："
echo "curl -X POST '$BASE_URL/control/send-message' -H 'Content-Type: application/json' -d '{\"content\":\"Hello from API!\"}'"
echo
echo "# 檢查連接狀態："
echo "curl -X GET '$BASE_URL/control/status'"
echo 