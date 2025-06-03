#!/bin/bash

# 太空探險劇本 - "毛怪星球大冒險"
# 請確保前後端服務都在運行

BASE_URL="http://localhost:8000/api"

echo "=== 🚀 太空探險劇本：毛怪星球大冒險 🚀 ==="
echo

# 準備工作：關閉 murmur 模式
echo "準備工作：關閉 murmur 模式..."
curl -X POST "$BASE_URL/control/murmur-mode" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }' | jq .

sleep 1

# 第一幕：啟程 - 太空船準備
echo "第一幕：啟程 - 太空船準備"
echo "設定太空船環境音效 BGM..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/spacelive_theme.mp3",
    "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"
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

sleep 30

# 第二幕：太空航行 - 重金屬BGM
echo "第二幕：太空航行 - 衝刺時刻"
echo "切換到重金屬BGM..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3",
    "sfxUrl": "/audio/effects/Energetic_fast_pace.mp3"
  }' | jq .

sleep 2

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "太空船進入超光速模式！感受這股力量，我們正以光速飛向毛怪星球！引擎全開，目標：無限星空！",
    "message_type": "chat-message"
  }' | jq .

sleep 20

# 播放太空船音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio-file/Energetic_fast_pace.mp3",
    "interrupt": false
  }' | jq .

sleep 3

# 第三幕：抵達毛怪星球 - 神秘氛圍
echo "第三幕：抵達毛怪星球 - 神秘探索"
echo "切換到神秘氛圍..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/spacelive_theme2.mp3",
    "sfxUrl": "/audio/effects/winds_blowing.mp3"
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



# 播放風聲音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio-file/winds_blowing.mp3",
    "interrupt": false
  }' | jq .

sleep 20

# 第四幕：發現毛怪 - 戲劇性轉折
echo "第四幕：發現毛怪 - 戲劇性相遇"

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "等等！我看到了什麼...那是...那是毛怪！他們正在向我們走來！",
    "message_type": "chat-message"
  }' | jq .

sleep 3

# 播放戲劇音效
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/songs-file/暴龍吼叫.mp3",
    "interrupt": false
  }' | jq .

sleep 2

curl -X POST "$BASE_URL/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "不要害怕！他們看起來很友善！其中一隻毛怪正在對我們說話...他說：謝謝你們來到我們的星球！",
    "message_type": "chat-message"
  }' | jq .

sleep 4

# 第五幕：友好相遇 - 歡樂結局
echo "第五幕：友好相遇 - 歡樂慶祝"
echo "切換到歡樂BGM..."

curl -X POST "$BASE_URL/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/space_live_country_theme1.mp3",
    "sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"
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

sleep 4

# 播放鳥叫聲慶祝
curl -X POST "$BASE_URL/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/songs-file/鳥叫.mp3",
    "interrupt": false
  }' | jq .

sleep 3

# 尾聲：感謝觀眾
echo "尾聲：感謝觀眾"

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

echo
echo "=== 劇本演出完畢！ ==="
echo "🎭 毛怪星球大冒險 - The End 🎭"
echo
echo "使用的音效資源："
echo "• BGM: spacelive_theme, heavy_metal_bgm_01, spacelive_theme2, space_live_country_theme1"
echo "• 音效: spaceship_ambience_01, Energetic_fast_pace, winds_blowing, taiwan_variety_sfx_01"
echo "• 角色音效: 暴龍吼叫, 鳥叫"
echo "• 情緒變化: neutral → excited → mysterious → joyful"
echo 