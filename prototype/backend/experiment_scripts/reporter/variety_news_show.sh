#!/bin/bash

# 《Space Variety News — Show Style》
# 目的：打造綜藝節目風格的太空新聞播報（活潑、趣味、帶動感）
# 功能：
# 1) 場景與背景：切換明亮城市燈光＋生成「綜藝舞台」背景
# 2) 動作與鏡位：舞步混合、動態鏡位
# 3) 音樂控制：上/下 BGM、段落中自動降音量
# 4) 內容：沿用太空新聞（Spaceflight News API），但用綜藝主持口吻包裝
#
# 執行：bash prototype/backend/experiment_scripts/reporter/variety_news_show.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"  # 不因 HTTP 狀態碼中止

# --- 全域 TTS 設定（綜藝主持腔）---
# 建議：活潑、俏皮、較高音、稍快。
TTS_INSTRUCTION="zh-TW Mandarin, lively variety show host, playful, energetic, higher pitch, slightly faster pace, crisp articulation"
TTS_VOICE_DEFAULT="nova"
TTS_SPEED_DEFAULT=1.25

# --- 小工具 ---
say() {
  # 用法: say "內容" 時長(秒) "emotion1,emotion2,..." [voice] [speed] [force]
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"happy,playful,excited"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-1}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  $CURL_POST "$BASE_URL/control/send-message" \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null || true
  # 情緒過場
  local IFS=','; read -ra KFS <<< "$EMOS"; unset IFS
  local KF_JSON="[]"
  if (( ${#KFS[@]} == 1 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"
  elif (( ${#KFS[@]} == 2 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"
  else
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"
  fi
  $CURL_POST_NF "$BASE_URL/control/emotion-trajectory" \
    -H "Content-Type: application/json" \
    -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null || true
  sleep $(echo "$DURATION * 0.75" | bc)
}

gap() { local S=${1:-0.8}; echo ">> 空檔: ${S}s"; sleep "$S"; }

cam_preset() { local NAME="$1"; local D=${2:-1.0}; echo ">> 鏡位 preset: $NAME ($D s)"; $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null || true; sleep $D; }
env_preset() { local PRE="$1"; echo ">> 環境: $PRE"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null || true; }
env_intensity() { local I=${1:-1.2}; echo ">> 光照強度: $I"; $CURL_POST_NF "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null || true; }

char_scale() { local S=${1:-1.0}; echo ">> 角色大小: $S"; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null || true; }
char_position() { local X=${1:-0.0}; local Y=${2:-0.0}; local Z=${3:-0.0}; echo ">> 角色位置: [$X,$Y,$Z]"; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null || true; }

anim_mix() {
  echo ">> 主角動畫混合: 空體Action + 舞步1 + 舞步2"
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" \
    -H "Content-Type: application/json" \
    -d '{
      "animations": [
        {"name": "空體Action", "weight": 1.0, "loop": true, "speed": 1.0},
        {"name": "舞步1", "weight": 0.75, "loop": true, "speed": 1.0},
        {"name": "舞步2", "weight": 0.55, "loop": true, "speed": 1.0}
      ],
      "transitionDuration": 0.8,
      "blendMode": "normal"
    }' >/dev/null || true
}

# BGM 控制
bgm_play() { local NAME="$1"; local VOL=${2:-0.22}; echo ">> 播放BGM: $NAME (vol=$VOL)"; $CURL_POST_NF "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"/audio/BGM/$NAME\", \"bgmPlaying\": true, \"volume\": $VOL}" >/dev/null || true; }
bgm_volume() { local VOL=${1:-0.12}; echo ">> 調整BGM音量: $VOL"; $CURL_POST_NF "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"volume\": $VOL}" >/dev/null || true; }
bgm_stop() { echo ">> 關閉BGM"; $CURL_POST_NF "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "", "bgmPlaying": false}' >/dev/null || true; }

# 生成「綜藝舞台」背景並自動套用
gen_variety_stage_bg() {
  local PROMPT="A vibrant neon variety show stage, glossy floor, colorful LED wall, confetti glow, spotlight beams, playful futuristic vibe, clean negative space for overlays; cinematic 16:9 composition"
  echo ">> 生成背景圖：Variety Stage"
  $CURL_POST_NF "$BASE_URL/generate-background-image" \
    -H "Content-Type: application/json" \
    -d "{\"description\": \"$PROMPT\", \"aspect_ratio\": \"16:9\"}" >/dev/null || true
}

# 使用太空新聞聚合（延用 Spaceflight News），後端會口播；前後我們包裝綜藝氛圍
speak_space_news() {
  local LIMIT=${1:-3}
  local INTRO=${2:-"綜藝快訊版，最新的太空話題："}
  echo ">> 取得並播報太空新聞 ($LIMIT 則)"
  $CURL_POST_NF "$BASE_URL/news/speak-latest-news" \
    -H "Content-Type: application/json" \
    -d "{\"limit\": $LIMIT, \"intro_text\": \"$INTRO\"}" >/dev/null || true
}

echo "=== 🎉 Space Variety News — Show Style 開始 ==="

# 0) 先關一次 BGM（保險）
bgm_stop || true

# 1) 場景 + 背景
env_preset "city" || true
env_intensity 1.6 || true
gen_variety_stage_bg || true

# 2) 鏡位 + 角色
cam_preset "frontal_dynamic_high" 1.0
char_scale 0.1
char_position 0.0 0.0 0.0
anim_mix

# 3) 上 BGM（活潑）
bgm_play "星際狂舞.mp3" 0.22

# 4) 開場（綜藝主持口吻）
say "各位朋友們～晚上好！歡迎來到星際綜藝新聞台～" 3.6 "joyful,excited,playful"
gap 0.6
say "今晚用最High的節奏，帶你追上宇宙第一手話題！" 3.2 "excited,playful,joyful"
gap 0.8
cam_preset "head_close_up" 0.9

# 5) 綜藝式提要 + 降BGM
bgm_volume 0.10
say "首先是火線頭條，我們快速上三則！準備好手刀收藏！" 3.2 "excited,joyful,playful"
gap 0.8
speak_space_news 3 "綜藝快訊，來囉！"
gap 0.8

# 6) 互動橋段 + 動態鏡位
cam_preset "frontal_dynamic_low" 1.0
say "欸你們覺得哪一則最酷？聊天室幫我刷起來～" 3.0 "playful,joyful,excited"
gap 0.8
say "我們等一下要做一個小小票選，輸的人現場跳一段太空舞步！" 3.4 "playful,joyful,excited"
gap 0.8
cam_preset "head_close_up" 1.0

# 7) 小結 + 恢復BGM音量
say "好的～以上是綜藝版太空快訊，資訊夠快、氣氛夠嗨！" 3.2 "joyful,content,playful"
gap 0.6
bgm_volume 0.22
say "喜歡這個節奏的朋友幫我們按起來，下一段直接加碼視覺特效！" 3.6 "excited,joyful,playful"

echo "=== ✅ Space Variety News — 完成（場景/背景/舞步/BGM/綜藝口播） ==="

