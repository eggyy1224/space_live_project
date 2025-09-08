#!/bin/bash

# 《Space Yoga Teacher — Zero-Gravity Flow》
# 更自由的零重力瑜伽：旋轉、漂浮、縮放脈動；語句極短；情緒更豐富。
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene4.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定（自然樣態）---
TTS_INSTRUCTION="Taiwanese Hokkien, Han characters, natural, warm, friendly, accurate tones; avoid Mandarin accent"
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.5
TTS_EVERY_N=3
TTS_COOLDOWN=5
__SAY_COUNT=0
LAST_TTS_TS=0

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say() {
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,interested,confident"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-0}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  __SAY_COUNT=$((__SAY_COUNT + 1)); local DO_TTS=0; local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then DO_TTS=1; else if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )) && (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then DO_TTS=1; fi; fi
  if (( DO_TTS == 1 )); then
    $CURL_POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" \
      -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  fi
  # 情緒
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON="[]"
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.85" | bc)
}

emote() {
  local DURATION=${1:-2.0}; local EMOS=${2:-"serene,content,joyful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.6" | bc)
}

bgm() { local URL="$1"; local VOL=${2:-0.25}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }

cam_preset() { local NAME="$1"; local D=${2:-1.5}; $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null; sleep $D; }
cam_transition() { local P=${1:-0}; local Y=${2:-0}; local R=${3:-0}; local F=${4:-55}; local D=${5:-1.2}; $CURL_POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d "{\"pitch\": $P, \"yaw\": $Y, \"roll\": $R, \"fov\": $F, \"duration\": $D}" >/dev/null; sleep $D; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
anim_mix() {
  local OTHER="$1"; local W=${2:-0.9}; local SPEED=${3:-0.7}; local TD=${4:-0.8}; local BLEND=${5:-"additive"}; local BASESPD=${6:-1.5}
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name": "空體Action", "weight": 1.0, "loop": true, "speed": $BASESPD},
    {"name": "漂浮", "weight": 0.8, "loop": true, "speed": 0.8},
    {"name": "$OTHER", "weight": $W, "loop": true, "speed": $SPEED}
  ],
  "transitionDuration": $TD,
  "blendMode": "$BLEND"
}
JSON
)
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-1.0}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-true}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }

# 中英併行語句（保持一致風格）
say_zh_en() {
  # 用法: say_zh_en "中文" "English" 時長(秒) "emo1,emo2,emo3" [voice] [speed] [force]
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"neutral,interested,confident"}
  local VOICE=${5:-$TTS_VOICE_DEFAULT}; local SPEED=${6:-$TTS_SPEED_DEFAULT}; local FORCE=${7:-0}
  say "$ZH\n$EN" "$DUR" "$EMO" "$VOICE" "$SPEED" "$FORCE"
}

# 動作池（加入飛行元素）
YOGA_MOVES=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作9" "瑜珈動作12" "瑜珈動作15" "瑜珈動作18")

EMO_FLOAT=("serene,hopeful,joyful" "serene,awe,joyful" "serene,interested,awe")
EMO_PULSE=("determined,proud,triumphant" "interested,determined,proud" "awe,proud,triumphant")
EMO_SOFT=("grateful,content,serene" "relieved,grateful,serene" "serene,content,joyful")

echo "=== 🧘 Space Yoga Teacher — Zero-Gravity Flow 開始 ==="

# 關閉隨機鏡位，切夜景 + 降強度 + 背景可見
$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true
cam_preset "head_close_up" 1.0
env_preset "night" || true
env_intensity 0.7 || true
env_background true || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -38.0
anim_char "空體Action" 1.0 true
sleep 0.8

# 開場：自然的語句
say_zh_en "咱攏輕輕浮起，先攏呼吸的步調。" "We rise light—find a steady rhythm." 2.8 "serene,interested,content" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
emote 1.6 "serene,awe,joyful"
anim_mix "瑜珈動作7" 0.9 0.7 0.8 "additive" 1.5
# 穩定鏡位：取消 yaw/roll 的大幅變化，僅做溫和推進
cam_transition -4 0 0 58 1.4

# 主段：5 回合 — 旋轉、漂浮、縮放脈動，口令更完整
for i in {1..5}; do
  # 輕微縮放脈動
  char_scale 0.11; sleep 0.1; char_scale 0.1
  # 位置輕移（維持鏡位穩定，不再每回合轉動相機）
  DX=$(rand_float -1.0 1.0 2); char_position "$DX" 8.2 -37.8
  # 僅在中段做一次有意義的輕推鏡（pitch 輕微、FOV 微調）
  if (( i == 3 )); then cam_transition -5 0 0 56 1.2; fi
  # 漂浮 + 瑜伽混合（隨機挑）
  MOVE=$(rand_choice YOGA_MOVES[@])
  anim_mix "$MOVE" 0.95 0.75 0.8 "additive" 1.55
  # 情緒：在 FLOAT / PULSE 間切換
  if (( i % 2 == 1 )); then EM=$(rand_choice EMO_FLOAT[@]); else EM=$(rand_choice EMO_PULSE[@]); fi
  emote 1.6 "$EM"
  # 口令（更完整的引導語）
  case $((i%5)) in
    1) say_zh_en "入氣，胸口開，肩膀鬆落。" "Inhale—open the chest, drop the shoulders." 2.6 "serene,interested,content";;
    2) say_zh_en "出氣，肋骨合，肚肚收。" "Exhale—ribs knit, belly draws in." 2.6 "serene,relieved,content";;
    3) say_zh_en "手臂前伸外展，空間較闊。" "Extend—reach forward and out, make more space." 2.6 "hopeful,joyful,awe";;
    4) say_zh_en "核心收回，骨盆中立。" "Gather—draw in the core, pelvis neutral." 2.6 "determined,proud,serene";;
    0) say_zh_en "停一下，找到中心。" "Pause—find your center." 2.4 "serene,content,serene";;
  esac
done

# 短暫隱現（幻影）
char_visible false; sleep 0.25; char_visible true
emote 1.8 "surprised,awe,joyful"

# 收束：回正 — 低角度望上（語句更有情緒）
cam_transition -10 0 0 56 1.4
say_zh_en "慢慢回正，心沉落，呼吸繼續。" "Return to center—let the heart settle, breath continues." 2.8 "grateful,content,serene" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
emote 2.4 "grateful,content,serene"

# 結束（不播放 BGM）
echo "=== ✅ Zero-Gravity Flow 結束 ==="
