#!/bin/bash

# 《Space Yoga Teacher — Solar Sail Flow》
# 主題：太陽帆（張帆 × 乘風 × 滑行），不搖鏡；以「展、收」節奏推進。
# 規則：瑜伽段不放 BGM；固定鏡位；內容不含場次編號；語音與情緒軌跡相配。

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定 ---
TTS_INSTR_SOFT="Taiwanese Hokkien, Han characters, gentle, airy, spacious; avoid Mandarin accent"
TTS_INSTR_CRISP="Taiwanese Hokkien, Han characters, light yet clear; avoid Mandarin accent"
VOICE_SOFT="sage"
VOICE_CRISP="nova"
SPEED_SOFT_MIN=0.50
SPEED_SOFT_MAX=0.65
SPEED_CRISP_MIN=0.80
SPEED_CRISP_MAX=0.95

# TTS 節流（溫和頻率）
TTS_EVERY_N=4
TTS_COOLDOWN=7
__SAY_COUNT=0
LAST_TTS_TS=0

rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.8}; local EMOS=${3:-"serene,content,hopeful"}
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
  sleep $(echo "$DURATION * 0.85" | bc)
}

emote() { local D=${1:-1.6}; local EMOS=${2:-"serene,content,hopeful"}; IFS=',' read -ra K<<<"$EMOS"; local KF; 
  if (( ${#K[@]}==1 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#K[@]}==2 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.5},{\"tag\":\"${K[1]}\",\"proportion\":1.0}]"; 
  else KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.0},{\"tag\":\"${K[1]}\",\"proportion\":0.6},{\"tag\":\"${K[2]}\",\"proportion\":1.0}]"; fi
  echo ">> 表情: $EMOS ($D s)"; $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $D, \"keyframes\": $KF}" >/dev/null; sleep $(echo "$D * 0.6" | bc); }

# 正確的 SFX 端點：background-audio（使用 sfxUrl）
sfx() { local URL="$1"; local VOL=${2:-0.08}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$URL\", \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_duo() {
  # 空體Action + 單一瑜伽（張帆/收帆的速度差）
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

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }

# 池
YOGA_SOFT=("瑜珈動作2" "瑜珈動作4" "瑜珈動作6" "瑜珈動作11" "瑜珈動作14")
YOGA_OPEN=("瑜珈動作3" "瑜珈動作5" "瑜珈動作9" "瑜珈動作12" "瑜珈動作18")
EMO_WIND=("serene,hopeful,joyful" "serene,interested,hopeful" "grateful,content,serene")
EMO_GLIDE=("serene,content,relieved" "content,hopeful,serene")

echo "=== 🧘 Space Yoga Teacher — Solar Sail Flow 開始 ==="

## 已移除：隨機鏡位/鏡位轉場
env_preset "dawn" || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.6 true

# 開場：張帆（展開胸腔）
say_with_inst "帆展開—胸口鬆，入氣較深。\nSail opens—chest broad, inhale deeper." 3.0 "serene,hopeful,joyful" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)" 1 "$TTS_INSTR_SOFT"
emote 1.4 "serene,content,hopeful"
# 保持安靜氛圍（不加入 SFX）

# 主段：張—滑—收 × 4 回
for i in {1..4}; do
  # 張（擴展式）：用較慢瑜伽速度
  M1=$(rand_choice YOGA_OPEN[@])
  anim_mix_duo $(rand_float 1.7 1.9 2) $(rand_float 0.55 0.70 2) 0.7 "$M1"
  emote 1.2 "$(rand_choice EMO_WIND[@])"

  # 滑（滑行感）：保持，短語提示
  say_with_inst "慢慢滑過空氣—肩放鬆。\nGlide through—relax the shoulders." 2.6 "serene,content,relieved" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)"

  # 收（收帆）：速度略收、縮放微脈動
  char_scale 0.11; sleep 0.1; char_scale 0.1
  M2=$(rand_choice YOGA_SOFT[@])
  anim_mix_duo $(rand_float 1.6 1.8 2) $(rand_float 0.60 0.75 2) 0.6 "$M2"
  emote 1.0 "$(rand_choice EMO_GLIDE[@])"

  # 小停頓
  sleep 0.7
done

# 收束：收帆入港（不開 BGM）
say_with_inst "帆收好—呼吸還在，身較輕。\nSail tucks—breath remains, body light." 2.8 "grateful,content,serene" "$VOICE_SOFT" "$(rand_float $SPEED_SOFT_MIN $SPEED_SOFT_MAX 2)" 1 "$TTS_INSTR_SOFT"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Solar Sail Flow 結束（安靜氛圍） ==="
