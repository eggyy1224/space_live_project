#!/bin/bash

# 《Space Yoga Teacher — Meteor Burst Flow》
# 方向：隕石爆發節奏（爆發×短停×再啟），不搖鏡；大量運用 send-message 與情緒軌跡配合。
# 規則：瑜伽段不放 BGM；使用現有 SFX 作為節拍與爆發提示；僅固定鏡位；內容不含場次編號。

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定 ---
TTS_INSTR_COOL="Taiwanese Hokkien, Han characters, calm, warm, intimate; avoid Mandarin accent"
TTS_INSTR_BURST="Taiwanese Hokkien, Han characters, energetic, urgent, crisp articulation; avoid Mandarin accent"
VOICE_COOL="sage"
VOICE_BURST="nova"
SPEED_COOL_MIN=0.50
SPEED_COOL_MAX=0.62
SPEED_BURST_MIN=0.95
SPEED_BURST_MAX=1.20

# TTS 節流（仍保持頻繁發聲）
TTS_EVERY_N=5
TTS_COOLDOWN=8
__SAY_COUNT=0
LAST_TTS_TS=0

rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say_with_inst() {
  # 用法: say_with_inst content duration emos voice speed force instruction
  local CONTENT="$1"; local DURATION=${2:-2.6}; local EMOS=${3:-"serene,content,joyful"}
  local VOICE=${4:-$VOICE_COOL}; local SPEED=${5:-0.6}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR_COOL}
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
  local DURATION=${1:-1.4}; local EMOS=${2:-"serene,content,joyful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"; 
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.55" | bc)
}

sfx() {
  local URL="$1"; local VOL=${2:-0.12}; local INT=${3:-false}
  echo ">> SFX: $URL @ $VOL"
  $CURL_POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d "{\"url\": \"$URL\", \"volume\": $VOL, \"interrupt\": $INT}" >/dev/null
}

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_multi() {
  # 空體Action +（可選漂浮）+ 2~3 瑜伽動作（weight=1.0）
  local BASESPD=${1:-2.6}; local YOGA_SPD=${2:-1.05}; local TD=${3:-0.5}; local FLOAT_W=${4:-0.0}; local COUNT=${5:-2}
  local ITEMS
  ITEMS=$(cat <<JSON
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD}
JSON
  )
  if (( $(echo "$FLOAT_W > 0" | bc -l) )); then
    ITEMS="$ITEMS,
    {\"name\": \"漂浮\", \"weight\": $FLOAT_W, \"loop\": true, \"speed\": 1.0}"
  fi
  for ((k=0;k<COUNT;k++)); do
    local M; M=$(rand_choice YOGA_MOVES[@])
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

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }

# 動作與情緒池
YOGA_MOVES=(
  "瑜珈動作1" "瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作8"
  "瑜珈動作10" "瑜珈動作12" "瑜珈動作14" "瑜珈動作17" "瑜珈動作20"
)
EMO_BURST=("triumphant,proud,joyful" "awe,triumphant,joyful" "determined,proud,triumphant")
EMO_COOL=("serene,content,relieved" "grateful,content,serene" "relieved,grateful,serene")

echo "=== 🧘 Space Yoga Teacher — Meteor Burst Flow 開始 ==="

# 固定鏡位，不搖鏡；安靜環境
$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true
env_preset "studio" || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 2.2 true

# 導入（溫和）
say_with_inst "先找節奏——入氣、吐氣。等會兒一口氣衝刺。\nFind rhythm—inhale… exhale… then burst." 2.8 "serene,content,relieved" "$VOICE_COOL" "$(rand_float $SPEED_COOL_MIN $SPEED_COOL_MAX 2)" 1 "$TTS_INSTR_COOL"
emote 1.2 "serene,content,relieved"
sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03 false

# 主段：爆發 5 回合（每回合：爆→停→收）
for i in {1..5}; do
  # 爆：加速混合 + 衝擊音效（不搖鏡）
  anim_mix_multi \
    $(rand_float 2.6 3.2 2) \
    $(rand_float 1.05 1.30 2) \
    $(rand_float 0.40 0.55 2) \
    0.0 \
    $(shuf -e 2 3 3 2 | head -n1 2>/dev/null || echo 2)
  sfx "/audio/effects/taiwan_variety_sfx_01.mp3" 0.18 false

  # 中段：只用表情，不說話
  emote 1.2 "$(rand_choice EMO_COOL[@])"

  # 額外緩衝，避免語句黏在一起
  sleep 0.8
done

# 收束
emote 1.6 "grateful,content,serene"
say_with_inst "做得真好——讓熱度慢慢沉下來。\nWell done—let the heat settle." 2.8 "grateful,content,serene" "$VOICE_COOL" "$(rand_float $SPEED_COOL_MIN $SPEED_COOL_MAX 2)" 1 "$TTS_INSTR_COOL"

echo "=== ✅ Meteor Burst Flow 結束（安靜氛圍） ==="
