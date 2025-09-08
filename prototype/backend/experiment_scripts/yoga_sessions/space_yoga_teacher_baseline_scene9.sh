#!/bin/bash

# 《Space Yoga Teacher — Gravity Drift Balance》
# 方向：交替重力與漂浮。無 BGM，僅安靜太空艙 ambience。
# 重點：
# - 重力段基底慢、過渡長；漂浮段基底快、過渡短
# - 20 動作袋子抽樣，段內每次混合 2–3 招式，weight=1.0
# - 兩種語氣：沉穩（重力）/輕快（漂浮）
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene9.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定 ---
TTS_INSTR_HEAVY="Taiwanese Hokkien, Han characters, grounded, steady, full-bodied; avoid Mandarin accent"
TTS_INSTR_FLOAT="Taiwanese Hokkien, Han characters, airy, playful, light; avoid Mandarin accent"

VOICE_HEAVY="sage"
VOICE_FLOAT="nova"

SPEED_HEAVY_MIN=0.52
SPEED_HEAVY_MAX=0.60
SPEED_FLOAT_MIN=0.80
SPEED_FLOAT_MAX=0.95

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
  # 用法: say_with_inst content duration emos voice speed force instruction
  local CONTENT="$1"; local DURATION=${2:-2.6}; local EMOS=${3:-"serene,content,grateful"}
  local VOICE=${4:-$VOICE_HEAVY}; local SPEED=${5:-0.6}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR_HEAVY}
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

say_heavy_zh_en() {
  # 用法: say_heavy_zh_en zh en dur emos
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"calm,grounded,focused"}
  say_with_inst "$ZH\n$EN" "$DUR" "$EMO" "$VOICE_HEAVY" "$(rand_float $SPEED_HEAVY_MIN $SPEED_HEAVY_MAX 2)" 0 "$TTS_INSTR_HEAVY"
}

say_float_zh_en() {
  # 用法: say_float_zh_en zh en dur emos
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.4}; local EMO=${4:-"playful,amused,joyful"}
  say_with_inst "$ZH\n$EN" "$DUR" "$EMO" "$VOICE_FLOAT" "$(rand_float $SPEED_FLOAT_MIN $SPEED_FLOAT_MAX 2)" 0 "$TTS_INSTR_FLOAT"
}

emote() {
  local DURATION=${1:-1.4}; local EMOS=${2:-"serene,content,relieved"}
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

## 鏡位相關操作已移除

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

# 多動作混合：空體Action + 漂浮 + 2–3 個瑜伽（weight=1.0）
anim_mix_multi() {
  local BASESPD=${1:-2.2}; local YOGA_SPD=${2:-0.8}; local TD=${3:-0.6}; local FLOAT_SPD=${4:-0.9}; local COUNT=${5:-2}
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

# 20 動作 + 袋子抽樣
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
echo "=== 🧘 Space Yoga Teacher — Gravity Drift Balance 開始 ==="

## 已移除：關閉隨機鏡位（randomMode）

## 已移除：鏡位 preset 設定
env_preset "night" || true
env_intensity 1.0 || true
env_background false || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 2.0 true
sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03

say_with_inst "重力漂浮交錯。\nGravity and drift, finding balance." 2.8 "serene,content,relieved" "$VOICE_HEAVY" "$(rand_float $SPEED_HEAVY_MIN $SPEED_HEAVY_MAX 2)" 1 "$TTS_INSTR_HEAVY"
emote 1.2 "serene,content,relieved"

for i in {1..4}; do
  if (( i % 2 == 1 )); then
    anim_mix_multi \
      $(rand_float 1.5 1.8 2) \
      $(rand_float 0.50 0.70 2) \
      $(rand_float 0.70 0.90 2) \
      $(rand_float 0.45 0.60 2) \
      $(rand_int 2 3)
    say_heavy_zh_en "沉下腳底，找回重量。" "Sink the soles, feel the pull." 2.6 "calm,grounded,focused"
    sleep 0.8
  else
    anim_mix_multi \
      $(rand_float 2.4 2.8 2) \
      $(rand_float 0.90 1.20 2) \
      $(rand_float 0.40 0.55 2) \
      $(rand_float 0.90 1.10 2) \
      $(rand_int 2 3)
    say_float_zh_en "鬆開重量，任意漂浮。" "Release weight, freely drift." 2.4 "playful,amused,joyful"
    sleep 0.6
  fi
  char_position $(rand_float -1.0 1.0 1) 8.$(rand_int 0 4) -30.$(rand_int 0 4)
  if (( RANDOM % 3 == 0 )); then sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03; fi

done

char_position 0.0 8.0 -30.0
emote 1.6 "grateful,content,serene"
say_with_inst "重與輕之間，身心找到軸心。\nBetween weight and drift, the center holds." 2.8 "grateful,content,serene" "$VOICE_HEAVY" "$(rand_float $SPEED_HEAVY_MIN $SPEED_HEAVY_MAX 2)" 1 "$TTS_INSTR_HEAVY"

echo "=== ✅ Gravity Drift Balance 結束（安靜氛圍，無 BGM） ==="
