#!/bin/bash

# 《Space Yoga Teacher — Solar Breeze Cooldown：Scene 10》
# 方向：晨光與太陽風收束。柔和 BGM，沉穩結尾。
# 重點：
# - 全程緩慢動作與漂浮感
# - 雙語導引，語氣溫柔
# - 20 動作袋子抽樣，段內混合 2–3 招式
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene10.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定 ---
TTS_INSTR_SOFT="Taiwanese Hokkien, Han characters, gentle, soothing, whispered; avoid Mandarin accent"
VOICE_SOFT="sage"
SPEED_SOFT_MIN=0.50
SPEED_SOFT_MAX=0.65

# TTS 節流
TTS_EVERY_N=3
TTS_COOLDOWN=5
__SAY_COUNT=0
LAST_TTS_TS=0

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_int()   { local MIN=$1; local MAX=$2; awk -v min="$MIN" -v max="$MAX" 'BEGIN{srand(); printf("%d\n", int(min+rand()*(max-min+1)))}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"serene,content,relieved"}
  local VOICE=${4:-$VOICE_SOFT}; local SPEED=${5:-0.55}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR_SOFT}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS / $VOICE@$SPEED)"
  __SAY_COUNT=$((__SAY_COUNT + 1)); local DO_TTS=0; local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then DO_TTS=1; else if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )) && (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then DO_TTS=1; fi; fi
  if (( DO_TTS == 1 )); then
    $CURL_POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" \
      -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$INSTR\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  fi
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.75" | bc)
}

say_soft_zh_en() {
  local ZH="$1"; local EN="$2"; local DUR=${3:-3.0}; local EMO=${4:-"serene,content,relieved"}
  say_with_inst "$ZH\n$EN" "$DUR" "$EMO" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)" 0 "$TTS_INSTR_SOFT"
}

emote() {
  local DURATION=${1:-1.6}; local EMOS=${2:-"serene,content,relieved"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.5" | bc)
}

bgm() { local URL="$1"; local VOL=${2:-0.2}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
sfx() { local URL="$1"; local VOL=${2:-0.03}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$URL\", \"volume\": $VOL}" >/dev/null; }

cam_preset() { local NAME="$1"; local D=${2:-1.0}; $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null; sleep $D; }
cam_move() { local P=${1:-0}; local Y=${2:-0}; local R=${3:-0}; local F=${4:-56}; local D=${5:-1.0}; $CURL_POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d "{\"pitch\": $P, \"yaw\": $Y, \"roll\": $R, \"fov\": $F, \"duration\": $D}" >/dev/null; sleep $D; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_multi() {
  local BASESPD=${1:-1.6}; local YOGA_SPD=${2:-0.6}; local TD=${3:-0.8}; local FLOAT_SPD=${4:-0.7}; local COUNT=${5:-2}
  local ITEMS
  ITEMS=$(cat <<JSON
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD},
    {"name":"漂浮","weight":1.0,"loop":true,"speed":$FLOAT_SPD}
JSON
  )
  for ((k=0;k<COUNT;k++)); do
    local M; M=$(next_yoga_move)
    ITEMS="$ITEMS,
    {\"name\": \"$M\", \"weight\": 1.0, \"loop\": true, \"speed\": $YOGA_SPD}"
  done
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
$ITEMS
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-1.0}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

YOGA_MOVES=(
  "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
  "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
  "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
  "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
)
_BAG=(); _LAST=""
_refill_bag() { _BAG=("${YOGA_MOVES[@]}"); for ((i=${#_BAG[@]}-1;i>0;i--)); do j=$((RANDOM%(i+1))); tmp=${_BAG[i]}; _BAG[i]=${_BAG[j]}; _BAG[j]=$tmp; done; }
next_yoga_move() { (( ${#_BAG[@]}==0 )) && _refill_bag; local pick=${_BAG[0]}; _BAG=(${_BAG[@]:1}); if [[ "$pick" == "$_LAST" && ${#_BAG[@]}>0 ]]; then local swap=${_BAG[0]}; _BAG[0]="$pick"; pick="$swap"; fi; _LAST="$pick"; echo "$pick"; }

# === 場景開始 ===
echo "=== 🧘 Space Yoga Teacher — Solar Breeze Cooldown：Scene 10 開始 ==="

$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true

cam_preset "head_close_up" 0.8
env_preset "dawn" || true
env_intensity 1.1 || true
env_background false || true
## 使用現成環境音效作為柔和背景
sfx "/audio/effects/winds_blowing.mp3" 0.05
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.8 true

say_with_inst "第十幕——太陽風收束，準備回艙。\nSolar breeze cools us, return to vessel." 3.0 "serene,content,relieved" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)" 1 "$TTS_INSTR_SOFT"
emote 1.6 "serene,content,relieved"

for i in {1..3}; do
  anim_mix_multi \
    $(rand_float 1.4 1.7 2) \
    $(rand_float 0.45 0.60 2) \
    $(rand_float 0.80 1.00 2) \
    $(rand_float 0.60 0.80 2) \
    $(rand_int 2 3)
  say_soft_zh_en "吸入晨光，手臂緩緩展開。" "Inhale dawn light, arms slowly open." 3.0 "serene,content,relieved"
  sleep 1.0
  char_position $(rand_float -0.8 0.8 1) 8.$(rand_int 0 4) -30.$(rand_int 0 4)
done

char_position 0.0 8.0 -30.0
emote 2.0 "grateful,content,serene"
say_soft_zh_en "今天的航行結束，身心都輕。" "Voyage complete, body and mind light." 3.0 "grateful,content,serene"
stop_bgm

echo "=== ✅ Scene 10 結束（柔和收束） ==="
