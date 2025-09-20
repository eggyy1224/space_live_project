#!/bin/bash

# 《Space Yoga Teacher — Heavy Metal Polyrhythm Flow》（scene22）
# 主題：重金屬多重節拍（3:2 多重節奏 × 對拍 × 圓場 circle-pit）。
# 設計：
# - BGM：/audio/BGM/heavy_metal_bgm_01.mp3（低音量鋪底）
# - 女黑死腔 TTS（台語為主＋英語口令），與表情軌跡成對
# - 技法：縮放脈衝、可見性快閃、Headbang、繞圈旋轉（spin_orbit）、圓場（circle_pit）與水平擺盪（sway_pendulum）
# - 結構：Intro → Polyrhythm Riff（3:2）→ Circle Pit → Breakdown → Blast Finale

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# --- 基礎控制（非生成）---
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
bgm() { local URL="$1"; local VOL=${2:-0.22}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-0.92}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
char_scale() { local S=${1:-0.10}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }
char_rotation() { local RX=${1:-0.0}; local RY=${2:-0.0}; local RZ=${3:-0.0}; $CURL_POST "$BASE_URL/control/character/rotation" -H "Content-Type: application/json" -d "{\"rotation\": [$RX,$RY,$RZ]}" >/dev/null; }

# outfit morph（體型微調）
char_bodyshape() { local KEY1=${1:-0.0}; local MIS=${2:-0.0}; local MIS1=${3:-0.0}; local P; P=$(cat <<JSON
{ "outfit_morphs": {"鍵 1": $KEY1, "錯置": $MIS, "錯置.001": $MIS1} }
JSON
  ); $CURL_POST_NF "$BASE_URL/control/character/outfit" -H "Content-Type: application/json" -d "$P" >/dev/null; }
char_bodyshape_rand() { char_bodyshape $(rand_float 0.15 0.60 2) $(rand_float 0.00 0.30 2) $(rand_float 0.00 0.30 2); }

# 背景圖片（可選）
set_background_image() { local F="$1"; [ -z "$F" ] && return 0; $CURL_POST_NF "$BASE_URL/set-background-image" -H "Content-Type: application/json" -d "{\"filename\": \"$F\"}" >/dev/null; }
generate_background_image() { local DESC="$1"; local VARIANT=${2:-"ansi_16color"}; $CURL_POST_NF "$BASE_URL/generate-background-image" -H "Content-Type: application/json" -d "{\"description\": \"$DESC\", \"aspect_ratio\": \"16:9\", \"style_variant\": \"$VARIANT\"}" >/dev/null; }

# 混合：空體Action + 多重動作
anim_mix_combo() {
  local BASESPD=$1; local TD=$2; shift 2
  local ITEMS; ITEMS=$(cat <<JSON
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD}
JSON
  )
  while (( "$#" )); do local NAME=$1; local WEIGHT=$2; local SPEED=$3; shift 3; ITEMS="$ITEMS,
    {\"name\": \"$NAME\", \"weight\": $WEIGHT, \"loop\": true, \"speed\": $SPEED}"; done
  local PAYLOAD; PAYLOAD=$(cat <<JSON
{
  "animations": [
$ITEMS
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
  ); $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

# 表情（不說話）
emote() { local DURATION=${1:-1.0}; local EMOS=${2:-"triumphant,proud,joyful"}; IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON;
  if (( ${#KFS[@]}==1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#KFS[@]}==2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]"; 
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi;
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null; sleep $(echo "$DURATION * 0.55" | bc); }

# 語音（金屬女黑死腔）+ 表情；含節流
TTS_INSTR="Female contralto black/death metal growl; very low pitch, dark timbre, chest resonance, lower formant; gritty/raspy but intelligible; avoid brightness/air, no scream; short staccato calls; Taiwanese Hokkien primary + English stage calls; strictly avoid Mandarin accent; explicitly avoid male timbre."
VOICE_CANDIDATES=("nova" "coral" "ballad" "verse")
VOICE_NAME="auto"
TTS_SPEED=0.52

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.4}; local EMOS=${3:-"triumphant,proud,joyful"}
  local VOICE=${4:-$VOICE_NAME}; local SPEED=${5:-$TTS_SPEED}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR}
  local LOG_CONTENT=${CONTENT//$'\n'/\\n}
  echo ">> 說話: $LOG_CONTENT ($DURATION s / $EMOS / $VOICE@$SPEED)"
    if [[ "$VOICE" == "auto" ]]; then local N=${#VOICE_CANDIDATES[@]}; VOICE=${VOICE_CANDIDATES[$((RANDOM % N))]}; fi
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
  else KF_JSON="[{\"tag\": \"${KFS[0]}\",\"proportion\": 0.0},{\"tag\": \"${KFS[1]}\",\"proportion\": 0.6},{\"tag\": \"${KFS[2]}\",\"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.70" | bc)
}

# 節拍特效/運動
PULSE_SCALE=0.13; BASE_SCALE=0.10; PULSE_DUR=0.08
POS_X_MIN=-1.6; POS_X_MAX=1.6; POS_Z_MIN=-30.8; POS_Z_MAX=-29.2

headbang_pulse() { local CYCLES=${1:-4}; local AMP=${2:-0.26}; local SPEED=${3:-0.06}; for ((h=1; h<=CYCLES; h++)); do char_rotation $AMP 0 0; sleep $SPEED; char_rotation -$AMP 0 0; sleep $SPEED; done; char_rotation 0 0 0; }
spin_orbit() { local STEPS=${1:-8}; local RADIUS=${2:-1.2}; local DUR=${3:-0.08}; local ANG=0; local STEP_ANG=$(awk -v s=$STEPS 'BEGIN{print 6.283185/s}'); for ((i=1;i<=STEPS;i++)); do local X=$(awk -v r=$RADIUS -v a=$ANG 'BEGIN{print r*cos(a)}'); local Z=$(awk -v r=$RADIUS -v a=$ANG 'BEGIN{print -30.0 + r*sin(a)}'); char_position $X 8.0 $Z; local YAW=$(awk -v a=$ANG 'BEGIN{print a}'); char_rotation 0 $YAW 0; sleep $DUR; ANG=$(awk -v a=$ANG -v da=$STEP_ANG 'BEGIN{print a+da}'); done; }
circle_pit() { local LOOPS=${1:-2}; local R_START=${2:-0.8}; local R_END=${3:-1.8}; local STEPS=${4:-24}; local DUR=${5:-0.05}; for ((c=1;c<=LOOPS;c++)); do for ((i=0;i<STEPS;i++)); do local t=$(awk -v i=$i -v s=$STEPS 'BEGIN{print i/s}'); local R=$(awk -v r0=$R_START -v r1=$R_END -v t=$t 'BEGIN{print r0 + (r1-r0)*t}'); local a=$(awk -v i=$i -v s=$STEPS 'BEGIN{print 6.283185*i/s}'); local X=$(awk -v r=$R 'BEGIN{print r*cos(a)}'); local Z=$(awk -v r=$R 'BEGIN{print -30.0 + r*sin(a)}'); char_position $X 8.0 $Z; char_rotation 0 $a 0; sleep $DUR; done; done; }
sway_pendulum() { local SWINGS=${1:-6}; local AMP=${2:-1.2}; local DUR=${3:-0.10}; for ((s=1;s<=SWINGS;s++)); do char_position $AMP 8.0 -30.0; sleep $DUR; char_position -$AMP 8.0 -30.0; sleep $DUR; AMP=$(awk -v a=$AMP 'BEGIN{print a*0.92}'); done; }

# 動作池與參數
BGM_URL="/audio/BGM/heavy_metal_bgm_01.mp3"; BGM_VOLUME=0.24
FAST_TD_MIN=0.22; FAST_TD_MAX=0.36; SLOW_TD=0.60
BASE_FAST_MIN=2.90; BASE_FAST_MAX=3.50; BASE_SLOW=2.10
YOGA_FAST_MIN=1.20; YOGA_FAST_MAX=1.55; YOGA_SLOW_MIN=0.90; YOGA_SLOW_MAX=1.10
FLASH_PROB_DENOM=3
YOGA_POWER=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作9" "瑜珈動作12" "瑜珈動作17")
YOGA_HOLD=("瑜珈動作2" "瑜珈動作6" "瑜珈動作11" "瑜珈動作14")
DANCE_MOVES=("舞步1" "舞步2" "舞步3")
SPORT_MOVES=("運動1" "運動2")

# 金屬口令（台語 + English）
LINES_INTRO=(
  $'節拍交錯—入位！
Polyrhythm—lock in!'
  $'三拍壓兩拍，穩！
Three over two—steady!'
)
LINES_CALL=(
  $'左—右—轉！
Left—right—spin!'
  $'踩—點—收！
Step—tap—hold!'
)
LINES_PIT=(
  $'開圓場—走！
Circle—move!'
)
LINES_OUTRO=(
  $'收回中心—穩住！
Back to center—hold!'
)

echo "=== 🧘 Space Yoga Teacher — Heavy Metal Polyrhythm Flow（scene22）開始 ==="

cheap_mode_disable_generative() { $CURL_POST_NF "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled":false}' >/dev/null || true; $CURL_POST_NF "$BASE_URL/control/realtime-voice" -H "Content-Type: application/json" -d '{"action":"stop"}' >/dev/null || true; }

# 開場：穩定基準 + BGM
cheap_mode_disable_generative
stop_bgm
env_preset "studio" || true
env_background false || true
env_intensity 0.92 || true
char_scale $BASE_SCALE
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.9 true
bgm "$BGM_URL" $BGM_VOLUME

# Intro（2 回）：脈衝 + 緩 headbang + 口令
for ((i=1;i<=2;i++)); do
  env_intensity $(rand_float 0.90 0.98 2)
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  anim_mix_combo $BASE_SLOW $SLOW_TD "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
  headbang_pulse 3 0.20 0.08
  if (( i==1 )); then say_with_inst "$(rand_choice LINES_INTRO[@])" 2.2 "interested,determined,proud"; else emote 1.0 "interested,determined,proud"; fi
  sleep 0.5
done

# Polyrhythm Riff：3:2（headbang 3次對上 spin_orbit 2段）× 多組
for ((g=1; g<=5; g++)); do
  # 3 次 headbang（短促），穿插強拍混合
  for ((h=1; h<=3; h++)); do
    env_intensity $(rand_float 0.95 1.04 2)
    char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
    anim_mix_combo $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
      "$(rand_choice DANCE_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2) \
      "$(rand_choice SPORT_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2)
    headbang_pulse 3 0.26 0.06
    if (( h==1 )); then say_with_inst "$(rand_choice LINES_CALL[@])" 1.6 "triumphant,proud,joyful"; else emote 0.9 "triumphant,proud,joyful"; fi
  done
  # 2 段 spin_orbit（較長）作為 2 的單位
  spin_orbit 10 1.2 0.06
  spin_orbit 10 1.4 0.06
  # 小停頓
  if (( RANDOM % FLASH_PROB_DENOM == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) 8.0 $(rand_float $POS_Z_MIN $POS_Z_MAX 2)
  sleep 0.5
done

# Circle Pit：半自由圓場運動 + 口令提示
say_with_inst "$(rand_choice LINES_PIT[@])" 2.0 "triumphant,proud,joyful"
circle_pit 2 0.9 1.8 28 0.05
emote 1.0 "interested,determined,proud"
sway_pendulum 6 1.2 0.10

# Breakdown：慢而重（長轉場 + 深表情）
for ((b=1;b<=5;b++)); do
  env_intensity $(rand_float 0.82 0.90 2)
  anim_mix_combo $BASE_SLOW $SLOW_TD "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
  headbang_pulse 2 0.18 0.10
  emote 1.4 "serene,content,relieved"
  sleep 0.6
done

# Blast Finale：爆發（高速雙混 + 口令/繞圈交錯）
for ((k=1;k<=12;k++)); do
  env_intensity $(rand_float 0.96 1.08 2)
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  anim_mix_combo $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "$(rand_choice YOGA_POWER[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2) \
    "$(rand_choice SPORT_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2)
  if (( k % 3 == 1 )); then say_with_inst "$(rand_choice LINES_CALL[@])" 1.8 "triumphant,proud,joyful"; else emote 0.9 "triumphant,proud,joyful"; fi
  if (( RANDOM % 2 == 0 )); then spin_orbit 10 1.5 0.05; else char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) 8.0 $(rand_float $POS_Z_MIN $POS_Z_MAX 2); fi
  if (( RANDOM % FLASH_PROB_DENOM == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  sleep $(rand_float 0.9 1.2 2)
done

# 收尾：定格與放鬆（BGM 持續）
anim_mix_combo $BASE_SLOW $SLOW_TD "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
say_with_inst "$(rand_choice LINES_OUTRO[@])" 2.2 "grateful,content,serene"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Heavy Metal Polyrhythm Flow 結束（BGM 持續播放） ==="
