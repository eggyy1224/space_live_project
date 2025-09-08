#!/bin/bash

# 《Space Yoga Teacher — Stardust Echo Flow》
# 方向：星塵回聲（溫和呼喚 × 迅速回應），不搖鏡；大量運用 send-message 與情緒配對；以既有 SFX 加強層次。
# 規則：瑜伽段不放 BGM；固定鏡位；內容不含場次編號。

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定 ---
TTS_INSTR_SOFT="Taiwanese Hokkien, Han characters, gentle, soothing, intimate; avoid Mandarin accent"
TTS_INSTR_SHARP="Taiwanese Hokkien, Han characters, crisp, lively, playful; avoid Mandarin accent"
VOICE_SOFT="sage"
VOICE_SHARP="nova"
SPEED_SOFT_MIN=0.50
SPEED_SOFT_MAX=0.65
SPEED_SHARP_MIN=0.85
SPEED_SHARP_MAX=1.05

# TTS 節流（中度頻率）
TTS_EVERY_N=5
TTS_COOLDOWN=8
__SAY_COUNT=0
LAST_TTS_TS=0

rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.8}; local EMOS=${3:-"serene,content,relieved"}
  local VOICE=${4:-$VOICE_SOFT}; local SPEED=${5:-0.58}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR_SOFT}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS / $VOICE@$SPEED)"
  __SAY_COUNT=$((__SAY_COUNT + 1))
  local DO_TTS=0; local NOW_TS=$(date +%s)
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
  # 讓說話完整結束（保守留白）
  sleep $(echo "$DURATION * 1.35 + 0.65" | bc)
}

emote() {
  local DURATION=${1:-1.6}; local EMOS=${2:-"serene,content,relieved"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"; 
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.6" | bc)
}

sfx() {
  local URL="$1"; local VOL=${2:-0.10}; local INT=${3:-false}
  $CURL_POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d "{\"url\": \"$URL\", \"volume\": $VOL, \"interrupt\": $INT}" >/dev/null
}

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_duo() {
  # 空體Action + 1 瑜伽（溫和）
  local BASESPD=${1:-1.7}; local YOGA_SPD=${2:-0.65}; local TD=${3:-0.7}; local MOVE="$4"
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD},
    {"name":"$MOVE","weight":1.0,"loop":true,"speed":$YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

anim_mix_burst() {
  # 空體Action + 2 招（快速回應）
  local BASESPD=${1:-2.2}; local YOGA_SPD=${2:-0.95}; local TD=${3:-0.5}; local M1="$4"; local M2="$5"
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD},
    {"name":"$M1","weight":1.0,"loop":true,"speed":$YOGA_SPD},
    {"name":"$M2","weight":1.0,"loop":true,"speed":$YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }

YOGA_MOVES_SOFT=("瑜珈動作2" "瑜珈動作4" "瑜珈動作6" "瑜珈動作9" "瑜珈動作11" "瑜珈動作14")
YOGA_MOVES_FAST=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作8" "瑜珈動作12" "瑜珈動作17")

EMO_SOFT=("serene,content,relieved" "grateful,content,serene")
EMO_SHARP=("playful,amused,joyful" "awe,hopeful,joyful")

echo "=== 🧘 Space Yoga Teacher — Stardust Echo Flow 開始 ==="

# 固定鏡位，不搖鏡；安靜環境
## 已移除：關閉隨機鏡位（randomMode）
env_preset "dawn" || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.8 true

# 開場（溫和呼喚）
say_with_inst "聽見星塵回聲—入氣，心較靜。\nHear stardust echo—inhale, soften within." 3.0 "serene,content,relieved" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)" 1 "$TTS_INSTR_SOFT"
emote 1.4 "serene,content,relieved"
sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03 false

# 主段：呼喚-回應 × 4 回
for i in {1..4}; do
  # 呼喚：溫和一式
  M_SOFT=$(rand_choice YOGA_MOVES_SOFT[@])
  anim_mix_duo $(rand_float 1.6 1.9 2) $(rand_float 0.55 0.70 2) $(rand_float 0.70 0.85 2) "$M_SOFT"
  # 中段：只用表情，不說話
  emote 1.2 "$(rand_choice EMO_SOFT[@])"
  emote 1.0 "$(rand_choice EMO_SOFT[@])"

  # 回應：迅速兩式（不搖鏡）+ 节拍 SFX
  M1=$(rand_choice YOGA_MOVES_FAST[@]); M2=$(rand_choice YOGA_MOVES_FAST[@])
  anim_mix_burst $(rand_float 2.0 2.4 2) $(rand_float 0.90 1.10 2) $(rand_float 0.45 0.60 2) "$M1" "$M2"
  sfx "/audio/effects/taiwan_variety_sfx_01.mp3" 0.16 false
  emote 1.0 "$(rand_choice EMO_SHARP[@])"

  # 額外緩衝
  sleep 0.8

  # 小停頓
  emote 1.0 "serene,content,relieved"
done

# 收束
say_with_inst "星塵漸息，呼吸還在。\nStardust fades—breath remains." 2.8 "grateful,content,serene" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)" 1 "$TTS_INSTR_SOFT"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Stardust Echo Flow 結束（安靜氛圍） ==="
