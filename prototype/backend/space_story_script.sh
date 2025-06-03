#!/bin/bash

# 太空探險劇本 - "毛怪星球大冒險" - 電影級鏡位版本
# 請確保前後端服務都在運行

BASE_URL="http://localhost:8000/api"

echo "=== 🚀 太空探險劇本：毛怪星球大冒險 🚀 ==="
echo "🎬 電影級鏡位版本"
echo

# 準備工作：關閉 murmur 模式 & 關閉隨機相機模式
echo "準備工作：設置拍攝環境..."
curl -X POST "$BASE_URL/control/murmur-mode" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }' | jq .

# 關閉隨機模式，確保鏡位不會被干擾
curl -X POST "$BASE_URL/control/broadcast" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "director-state", 
    "payload": {"randomMode": false}
  }' | jq .

sleep 1

# 開場鏡位：正面迎接觀眾的標準視角
echo "📸 開場鏡位：正面歡迎視角"
curl -X POST "$BASE_URL/control/camera/set-angle" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0, 
    "yaw": 0, 
    "roll": 0
  }' | jq .

sleep 2

# 第一幕：啟程 - 太空船準備
echo "=== 第一幕：啟程 - 太空船準備 ==="
echo "設定太空船環境音效 BGM..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/spacelive_theme.mp3",
    "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"
  }' | jq .

sleep 2

# 📸 低角度仰拍 - 營造英雄感
echo "📸 低角度仰拍 - 太空人登場"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": -20, 
    "yaw": 15, 
    "roll": 0,
    "duration": 2.0
  }' | jq .

sleep 2

echo "太空人開始說話..."
curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "各位太空探險家，歡迎來到太空船！今天我們將前往神秘的毛怪星球進行探險。請大家繫好安全帶，我們即將啟程！",
    "message_type": "chat-message"
  }' | jq .

sleep 1

# 設定興奮情緒
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "neutral", "proportion": 0.0},
      {"tag": "excited", "proportion": 0.5},
      {"tag": "happy", "proportion": 1.0}
    ]
  }' | jq .

sleep 5

# 📸 漸進到側面視角
echo "📸 側面特寫 - 觀察準備細節"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 5, 
    "yaw": 45, 
    "roll": 0,
    "duration": 3.0
  }' | jq .

sleep 25

# 第二幕：太空航行 - 重金屬BGM
echo "=== 第二幕：太空航行 - 衝刺時刻 ==="
echo "切換到重金屬BGM..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3",
    "sfxUrl": "/audio/effects/Energetic_fast_pace.mp3"
  }' | jq .

# 📸 荷蘭角（Dutch Angle）- 營造動感和速度感
echo "📸 荷蘭角動感鏡位 - 超光速啟動"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 10, 
    "yaw": 30, 
    "roll": 25,
    "duration": 1.5
  }' | jq .

sleep 2

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "太空船進入超光速模式！感受這股力量，我們正以光速飛向毛怪星球！引擎全開，目標：無限星空！",
    "message_type": "chat-message"
  }' | jq .

sleep 3

# 📸 極端傾斜角度 - 失重感
echo "📸 極端傾斜 - 失重飛行"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 15, 
    "yaw": -45, 
    "roll": 45,
    "duration": 2.0
  }' | jq .

sleep 5

# 📸 快速360度環繞 - 表現超光速
echo "📸 快速旋轉 - 超光速體驗"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0, 
    "yaw": 180, 
    "roll": 0,
    "duration": 1.0
  }' | jq .

sleep 1

curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0, 
    "yaw": 360, 
    "roll": 0,
    "duration": 1.0
  }' | jq .

sleep 10

# 播放太空船音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio-file/Energetic_fast_pace.mp3",
    "interrupt": false
  }' | jq .

sleep 3

# 第三幕：抵達毛怪星球 - 神秘氛圍
echo "=== 第三幕：抵達毛怪星球 - 神秘探索 ==="
echo "切換到神秘氛圍..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/spacelive_theme2.mp3",
    "sfxUrl": "/audio/effects/winds_blowing.mp3"
  }' | jq .

# 📸 鳥瞰視角 - 俯視星球全景
echo "📸 鳥瞰視角 - 星球全景"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 60, 
    "yaw": 0, 
    "roll": 0,
    "duration": 3.0
  }' | jq .

sleep 2

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我們抵達了毛怪星球！這裡的風聲好神秘，空氣中彌漫著未知的氣息。讓我們小心探索這個奇妙的世界...",
    "message_type": "chat-message"
  }' | jq .

# 設定神秘情緒
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "excited", "proportion": 0.0},
      {"tag": "interested", "proportion": 0.5},
      {"tag": "awe", "proportion": 1.0}
    ]
  }' | jq .

sleep 5

# 📸 慢慢降低到探索視角
echo "📸 降低探索視角 - 謹慎前進"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 10, 
    "yaw": 25, 
    "roll": 5,
    "duration": 4.0
  }' | jq .

# 播放風聲音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio-file/winds_blowing.mp3",
    "interrupt": false
  }' | jq .

sleep 15

# 第四幕：發現毛怪 - 戲劇性轉折
echo "=== 第四幕：發現毛怪 - 戲劇性相遇 ==="

# 📸 急速拉近特寫 - 驚訝發現
echo "📸 震驚特寫 - 發現毛怪！"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0, 
    "yaw": 0, 
    "roll": 10,
    "duration": 0.5
  }' | jq .

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "等等！我看到了什麼...那是...那是毛怪！他們正在向我們走來！",
    "message_type": "chat-message"
  }' | jq .

sleep 1

# 📸 戲劇性荷蘭角 - 緊張感
echo "📸 戲劇性荷蘭角 - 緊張時刻"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 15, 
    "yaw": 45, 
    "roll": -30,
    "duration": 1.0
  }' | jq .

sleep 2

# 播放戲劇音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/songs-file/暴龍吼叫.mp3",
    "interrupt": false
  }' | jq .

sleep 2

# 📸 慢慢回正 - 緊張緩解
echo "📸 緊張緩解 - 友善發現"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 5, 
    "yaw": 15, 
    "roll": 0,
    "duration": 2.0
  }' | jq .

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "不要害怕！他們看起來很友善！其中一隻毛怪正在對我們說話...他說：謝謝你們來到我們的星球！",
    "message_type": "chat-message"
  }' | jq .

sleep 4

# 第五幕：友好相遇 - 歡樂結局
echo "=== 第五幕：友好相遇 - 歡樂慶祝 ==="
echo "切換到歡樂BGM..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/space_live_country_theme1.mp3",
    "sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"
  }' | jq .

# 📸 歡樂的輕微仰角 - 慶祝角度
echo "📸 歡樂仰角 - 慶祝時刻"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": -15, 
    "yaw": -20, 
    "roll": 0,
    "duration": 2.0
  }' | jq .

sleep 2

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "太棒了！毛怪們邀請我們參加他們的星球慶典！他們還送給我們珍貴的禮物 - 給我們臉，給我們頭！這真是一場完美的太空冒險！",
    "message_type": "chat-message"
  }' | jq .

# 設定開心情緒
curl -X POST "$BASE_URL/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 6.0,
    "keyframes": [
      {"tag": "awe", "proportion": 0.0},
      {"tag": "happy", "proportion": 0.5},
      {"tag": "joyful", "proportion": 1.0}
    ]
  }' | jq .

sleep 2

# 📸 360度慶祝旋轉
echo "📸 360度慶祝旋轉 - 歡樂共舞"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": -10, 
    "yaw": 90, 
    "roll": 0,
    "duration": 2.0
  }' | jq .

sleep 2

curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": -10, 
    "yaw": 180, 
    "roll": 0,
    "duration": 2.0
  }' | jq .

# 播放鳥叫聲慶祝
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/songs-file/鳥叫.mp3",
    "interrupt": false
  }' | jq .

sleep 3

# 尾聲：感謝觀眾
echo "=== 尾聲：感謝觀眾 ==="

# 📸 最終致謝鏡位 - 正面感謝
echo "📸 最終致謝鏡位 - 正面告別"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0, 
    "yaw": 0, 
    "roll": 0,
    "duration": 3.0
  }' | jq .

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "感謝大家和我一起完成這場精彩的太空冒險！特別向國網中心以及2049媽祖繞月策展團隊致敬！讓我們繼續探索無限的宇宙奧秘！",
    "message_type": "chat-message"
  }' | jq .

sleep 3

# 最終BGM
curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/spacelive_theme.mp3",
    "sfxUrl": ""
  }' | jq .

# 📸 片尾升起鏡位 - 象徵繼續探索
echo "📸 片尾升起鏡位 - 無限探索"
curl -X POST "$BASE_URL/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": -30, 
    "yaw": 10, 
    "roll": 0,
    "duration": 5.0
  }' | jq .

sleep 5

echo
echo "=== 劇本演出完畢！ ==="
echo "🎬 毛怪星球大冒險 - 電影級鏡位版 - The End 🎭"
echo
echo "🎥 本次使用的電影鏡位技巧："
echo "• 低角度仰拍：英雄視角營造威嚴感"
echo "• 荷蘭角：營造動感和緊張氛圍"
echo "• 鳥瞰視角：展現場景全貌"
echo "• 快速旋轉：表現超光速和慶祝"
echo "• 戲劇性傾斜：增強情感張力"
echo "• 360度環繞：沉浸式體驗"
echo
echo "🎵 使用的音效資源："
echo "• BGM: spacelive_theme, heavy_metal_bgm_01, spacelive_theme2, space_live_country_theme1"
echo "• 音效: spaceship_ambience_01, Energetic_fast_pace, winds_blowing, taiwan_variety_sfx_01"
echo "• 角色音效: 暴龍吼叫, 鳥叫"
echo "• 情緒變化: neutral → excited → mysterious → joyful"
echo
echo "🎯 鏡位設計理念："
echo "• 開場：親切歡迎，建立信任"
echo "• 啟程：英雄仰角，增強期待"
echo "• 航行：動感傾斜，表現速度"
echo "• 探索：鳥瞰俯視，展現未知"
echo "• 發現：戲劇荷蘭角，營造緊張"
echo "• 慶祝：歡樂旋轉，共享喜悅"
echo "• 告別：正面致謝，溫暖結束"
echo 