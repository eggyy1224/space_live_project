#!/bin/bash

echo "實驗電影 - 迴響的碎片 - 即將開始..."
echo "請確保後端服務運行在 http://localhost:8000 且前端已連接 WebSocket"
echo "某些資源如音效、動畫名稱為示意，請依實際項目配置調整"
echo "建議在每個指令塊後手動添加適當的 sleep 時間，以觀察效果"
# 首先，檢查連接狀態 (可選，但推薦)
# curl http://localhost:8000/api/control/status
# sleep 2 # 給予API調用和響應時間

# --- 場景 1 開始 ---
echo "場景 1：初始的低語"

# 1. 設定背景音樂 (示意路徑，請替換為您項目中的實際 BGM 路徑)
curl -X POST http://localhost:8000/api/control/background-audio \
  -H "Content-Type: application/json" \
  -d '{
        "bgmUrl": "/audio/BGM/ambient_drone_01.mp3", 
        "bgmPlaying": true
      }'
echo "場景1: BGM設定完成，等待2秒..."
sleep 2

# 2. 攝影機從 top_down_center
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset \
  -H "Content-Type: application/json" \
  -d '{
        "name": "top_down_center", 
        "duration": 0.5 
      }'
echo "場景1: 鏡頭設定為 top_down_center，等待3秒..."
sleep 3

# 2b. 過渡到 head_close_up
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset \
  -H "Content-Type: application/json" \
  -d '{
        "name": "head_close_up", 
        "duration": 4.0 
      }'
echo "場景1: 鏡頭過渡至 head_close_up，等待1秒讓過渡開始..."
sleep 1

# 3. 角色說話 + 情緒
curl -X POST http://localhost:8000/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{
        "content": "這片虛無之中... 是否有迴響？"
      }'
echo "場景1: 角色說話..."

curl -X POST http://localhost:8000/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{
        "duration": 5.0, 
        "keyframes": [
          {"tag": "pensive", "proportion": 0.0}, 
          {"tag": "curious", "proportion": 0.8}
        ]
      }'
echo "場景1: 設定情緒軌跡..."

# 4. 播放細微的思考動畫 (示意動畫名稱)
curl -X POST http://localhost:8000/api/control/body-animation \
  -H "Content-Type: application/json" \
  -d '{
        "animation": "ThinkingSubtle", 
        "loop": false, 
        "speed": 0.8
      }'
echo "場景1: 播放思考動畫..."

echo "場景1: 等待7秒，讓TTS、情緒、動畫和鏡頭完成..."
sleep 7
# --- 場景 1 結束 ---

# --- 場景 2 開始 ---
echo "場景 2：突現的脈動"

# 1. 停止先前BGM 或 切換BGM (示意)
curl -X POST http://localhost:8000/api/control/background-audio \
  -H "Content-Type: application/json" \
  -d '{
        "bgmUrl": "/audio/BGM/energetic_pulse_01.mp3", 
        "bgmPlaying": true
      }' 
echo "場景2: 切換BGM..."

# 2. 播放突然的音效 (示意路徑)
curl -X POST http://localhost:8000/api/control/play-audio \
  -H "Content-Type: application/json" \
  -d '{
        "url": "/audio/SFX/glitch_impact_01.mp3", 
        "interrupt": false 
      }'
echo "場景2: 播放音效，等待1秒..."
sleep 1

# 3. 攝影機快速切換
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset \
  -H "Content-Type: application/json" \
  -d '{
        "name": "dramatic_angle_1", 
        "duration": 0.5 
      }'
echo "場景2: 快速切換鏡頭，等待1秒..."
sleep 1

# 4. 角色驚嘆 + 情緒
curl -X POST http://localhost:8000/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{
        "content": "啊！那是..."
      }'
echo "場景2: 角色說話..."

curl -X POST http://localhost:8000/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{
        "duration": 3.0, 
        "keyframes": [
          {"tag": "surprised", "proportion": 0.0}, 
          {"tag": "excited", "proportion": 0.7}
        ]
      }'
echo "場景2: 設定情緒軌跡..."

# 5. 播放活力動畫 (示意動畫名稱)
curl -X POST http://localhost:8000/api/control/body-animation \
  -H "Content-Type: application/json" \
  -d '{
        "animation": "ExcitedGesture", 
        "loop": false, 
        "speed": 1.2
      }'
echo "場景2: 播放活力動畫..."

echo "場景2: 等待5秒，讓TTS、情緒和動畫播放完成..."
sleep 5
# --- 場景 2 結束 ---

# --- 場景 3 開始 ---
echo "場景 3：流動的視界"

# 1. 切換背景音樂 (示意路徑)
curl -X POST http://localhost:8000/api/control/background-audio \
  -H "Content-Type: application/json" \
  -d '{
        "bgmUrl": "/audio/BGM/ethereal_flow_01.mp3", 
        "bgmPlaying": true
      }'
echo "場景3: 切換BGM，等待2秒..."
sleep 2

# 2. 攝影機運鏡 (示例：從 fly_by_left 平滑移動)
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset \
  -H "Content-Type: application/json" \
  -d '{
        "name": "fly_by_left", 
        "duration": 8.0 
      }'
echo "場景3: 鏡頭 fly_by_left 長運鏡..."

# 3. 角色低語 (可選) 或無言
# curl -X POST http://localhost:8000/api/control/send-message \
#   -H "Content-Type: application/json" \
#   -d '{
#         "content": "流動...變換..."
#       }'
# echo "場景3: 角色低語 (可選)..."

# 4. 情緒保持中性或專注
curl -X POST http://localhost:8000/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{
        "duration": 8.0,
        "keyframes": [
          {"tag": "neutral", "proportion": 0.0},
          {"tag": "focused", "proportion": 0.5},
          {"tag": "neutral", "proportion": 1.0}
        ]
      }'
echo "場景3: 設定情緒軌跡..."

# 5. 持續的流動動畫 (示意動畫名稱)
curl -X POST http://localhost:8000/api/control/body-animation \
  -H "Content-Type: application/json" \
  -d '{
        "animation": "FloatingIdle", 
        "loop": true,
        "speed": 0.7
      }'
echo "場景3: 播放流動動畫..."

echo "場景3: 等待10秒，讓運鏡和動畫有足夠時間..."
sleep 10
# --- 場景 3 結束 ---

# --- 場景 4 開始 ---
echo "場景 4：終末的疑問"

# 1. 背景音樂漸弱
curl -X POST http://localhost:8000/api/control/background-audio \
  -H "Content-Type: application/json" \
  -d '{
        "bgmUrl": "", 
        "bgmPlaying": false
      }'
echo "場景4: 停止BGM，等待2秒..."
sleep 2

# 2. 攝影機回到 overview
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset \
  -H "Content-Type: application/json" \
  -d '{
        "name": "overview", 
        "duration": 5.0 
      }'
echo "場景4: 鏡頭回到 overview，等待2秒讓過渡開始..."
sleep 2

# 3. 角色最後的疑問 + 情緒
curl -X POST http://localhost:8000/api/control/send-message \
  -H "Content-Type: application/json" \
  -d '{
        "content": "這一切... 究竟是什麼？"
      }'
echo "場景4: 角色說話..."

curl -X POST http://localhost:8000/api/control/emotion-trajectory \
  -H "Content-Type: application/json" \
  -d '{
        "duration": 6.0, 
        "keyframes": [
          {"tag": "calm", "proportion": 0.0}, 
          {"tag": "thoughtful", "proportion": 0.7}
        ]
      }'
echo "場景4: 設定情緒軌跡..."

# 4. 停止動畫或變為靜態 (示意動畫名稱)
curl -X POST http://localhost:8000/api/control/body-animation \
  -H "Content-Type: application/json" \
  -d '{
        "animation": "IdleStatic", 
        "loop": false
      }'
echo "場景4: 播放靜態動畫..."

echo "場景4: 等待8秒，讓所有效果完成..."
sleep 8
# --- 場景 4 結束 ---

echo "實驗電影 - 迴響的碎片 - 結束。"
echo "使用 chmod +x prototype/backend/experiment_scripts/meta_self2.sh 使其可執行" 