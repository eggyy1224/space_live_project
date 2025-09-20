#!/bin/bash

# 《Space Yoga Teacher — Comet Trail Flow》
# 主題：彗星尾（長尾 × 速閃），不搖鏡；以「拉長—點亮」節奏打造呼吸與爆點的對比。
# 規則：瑜伽段不放 BGM；固定鏡位；內容不含場次編號；語音與情緒軌跡相配。

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

TTS_INSTR_LONG="Taiwanese Hokkien, Han characters, elongated, smooth, calm; avoid Mandarin accent"
TTS_INSTR_SPARK="Taiwanese Hokkien, Han characters, crisp, bright, playful; avoid Mandarin accent"
VOICE_LONG="sage"
VOICE_SPARK="nova"
SPEED_LONG_MIN=0.50
SPEED_LONG_MAX=0.62
SPEED_SPARK_MIN=0.90
SPEED_SPARK_MAX=1.10


rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.8}; local EMOS=${3:-"serene,content,relieved"}
  local VOICE=${4:-$VOICE_LONG}; local SPEED=${5:-0.56}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR_LONG}
  local LOG_CONTENT=${CONTENT//$'\n'/\\n}
  echo ">> 說話: $LOG_CONTENT ($DURATION s / $EMOS / $VOICE@$SPEED)"
  local PAYLOAD
  PAYLOAD=$(CONTENT="$CONTENT" python3 - <<'PY'
import json
import os
import uuid
from datetime import datetime, timezone

content = os.environ.get("CONTENT", "")
message = {
    "id": f"script-bot-{uuid.uuid4().hex[:8]}",
    "role": "bot",
    "content": content,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "audioUrl": None,
    "isFromAPI": True,
}
payload = {"type": "chat-message", "message": message}
print(json.dumps(payload, ensure_ascii=False))
PY
)
  $CURL_POST "$BASE_URL/control/broadcast" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" >/dev/null
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"; 
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.85" | bc)
}

emote() { local D=${1:-1.6}; local EMOS=${2:-"serene,content,relieved"}; IFS=',' read -ra K<<<"$EMOS"; local KF; 
  if (( ${#K[@]}==1 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#K[@]}==2 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.5},{\"tag\":\"${K[1]}\",\"proportion\":1.0}]"; 
  else KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.0},{\"tag\":\"${K[1]}\",\"proportion\":0.6},{\"tag\":\"${K[2]}\",\"proportion\":1.0}]"; fi
  echo ">> 表情: $EMOS ($D s)"; $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $D, \"keyframes\": $KF}" >/dev/null; sleep $(echo "$D * 0.6" | bc); }

# 正確的 SFX 端點：background-audio（使用 sfxUrl）
sfx() { local URL="$1"; local VOL=${2:-0.10}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$URL\", \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_burst() {
  # 空體Action + 兩式，快速點亮（burst）
  local BASESPD=${1:-2.0}; local YOGA_SPD=${2:-0.95}; local TD=${3:-0.55}; local M1="$4"; local M2="$5"
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

anim_mix_tail() {
  # 空體Action + 單式，拉長（tail）
  local BASESPD=${1:-1.7}; local YOGA_SPD=${2:-0.60}; local TD=${3:-0.70}; local MOVE="$4"
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

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }

# 池
YOGA_TAIL=("瑜珈動作2" "瑜珈動作6" "瑜珈動作11" "瑜珈動作14")
YOGA_SPARK=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作9" "瑜珈動作12" "瑜珈動作17")
EMO_TAIL=("serene,content,relieved" "grateful,content,serene")
EMO_SPARK=("playful,amused,joyful" "awe,hopeful,joyful")

echo "=== 🧘 Space Yoga Teacher — Comet Trail Flow 開始 ==="

## 已移除：隨機鏡位/鏡位轉場
env_preset "night" || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.8 true

# 開場：拖尾（拉長呼吸）
say_with_inst $'尾拖長—入氣拉開，吐氣更長。
Tail grows—inhale broad, exhale longer.' 3.0 "serene,content,relieved" "$VOICE_LONG" "$(rand_float $SPEED_LONG_MIN $SPEED_LONG_MAX 2)" 1 "$TTS_INSTR_LONG"
emote 1.2 "serene,content,relieved"

# 主段：Tail（拉長）→ Spark（速閃） × 4 回（加入安靜太空音色）
for i in {1..4}; do
  # Tail：單式拉長
  MT=$(rand_choice YOGA_TAIL[@])
  anim_mix_tail $(rand_float 1.6 1.9 2) $(rand_float 0.55 0.70 2) 0.7 "$MT"
  emote 1.2 "$(rand_choice EMO_TAIL[@])"

  # Spark：兩式速閃 + SFX 節拍
  M1=$(rand_choice YOGA_SPARK[@]); M2=$(rand_choice YOGA_SPARK[@])
  anim_mix_burst $(rand_float 2.0 2.4 2) $(rand_float 0.95 1.10 2) $(rand_float 0.45 0.60 2) "$M1" "$M2"
  emote 1.0 "$(rand_choice EMO_SPARK[@])"
  
  # 小停頓：讓尾巴落下
  sleep 0.8
done

# 收束：長尾漸息（這一幕不開 BGM）
say_with_inst $'光尾漸息—心猶靜，呼吸猶穩。
Trail fades—heart still, breath steady.' 2.8 "grateful,content,serene" "$VOICE_LONG" "$(rand_float $SPEED_LONG_MIN $SPEED_LONG_MAX 2)" 1 "$TTS_INSTR_LONG"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Comet Trail Flow 結束（安靜氛圍） ==="
