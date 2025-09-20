#!/bin/bash

# 《Space Yoga Teacher — Galactic Battle Groove》
# 主題：星際狂舞（對拍 × 反拍 × 爆發橋段）。
# 規則：
# - 使用 BGM：/audio/BGM/星際狂舞.mp3（持續播放）
# - 不搖鏡；以縮放脈衝、可見性快閃、位置抖動表現節拍

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# --- 控制工具 ---
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
bgm() { local URL="$1"; local VOL=${2:-0.26}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-0.95}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }
char_rotation() { local RX=${1:-0.0}; local RY=${2:-0.0}; local RZ=${3:-0.0}; $CURL_POST "$BASE_URL/control/character/rotation" -H "Content-Type: application/json" -d "{\"rotation\": [$RX,$RY,$RZ]}" >/dev/null; }

# 體型（胖瘦）控制：使用 outfit morph targets
char_bodyshape() {
  local KEY1=${1:-0.0}; local MIS=${2:-0.0}; local MIS1=${3:-0.0}
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{ "outfit_morphs": {"鍵 1": $KEY1, "錯置": $MIS, "錯置.001": $MIS1} }
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/outfit" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

char_bodyshape_rand() {
  char_bodyshape $(rand_float 0.15 0.60 2) $(rand_float 0.00 0.30 2) $(rand_float 0.00 0.30 2)
}

# 背景圖片控制
set_background_image() { local F="$1"; [ -z "$F" ] && return 0; $CURL_POST_NF "$BASE_URL/set-background-image" -H "Content-Type: application/json" -d "{\"filename\": \"$F\"}" >/dev/null; }
generate_background_image() { local DESC="$1"; local VARIANT=${2:-"ansi_16color"}; $CURL_POST_NF "$BASE_URL/generate-background-image" -H "Content-Type: application/json" -d "{\"description\": \"$DESC\", \"aspect_ratio\": \"16:9\", \"style_variant\": \"$VARIANT\"}" >/dev/null; }

anim_mix_combo() {
  local BASESPD=$1; local TD=$2; shift 2
  local ITEMS
  ITEMS=$(cat <<JSON
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD}
JSON
  )
  while (( "$#" )); do
    local NAME=$1; local WEIGHT=$2; local SPEED=$3; shift 3
    ITEMS="$ITEMS,
    {\"name\": \"$NAME\", \"weight\": $WEIGHT, \"loop\": true, \"speed\": $SPEED}"
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

TTS_INSTR="Taiwanese Hokkien, Han characters, energetic, confident, crisp articulation; avoid Mandarin accent"
VOICE_NAME="sage"
TTS_SPEED=0.64

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.6}; local EMOS=${3:-"triumphant,proud,joyful"}
  local VOICE=${4:-$VOICE_NAME}; local SPEED=${5:-$TTS_SPEED}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR}
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
  else KF_JSON="[{\"tag\": \"${KFS[0]}\",\"proportion\": 0.0},{\"tag\": \"${KFS[1]}\",\"proportion\": 0.6},{\"tag\": \"${KFS[2]}\",\"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.75" | bc)
}

emote() { local D=${1:-1.0}; local EMOS=${2:-"triumphant,proud,joyful"}; IFS=',' read -ra K<<<"$EMOS"; local KF; 
  if (( ${#K[@]}==1 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#K[@]}==2 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.5},{\"tag\":\"${K[1]}\",\"proportion\":1.0}]"; 
  else KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.0},{\"tag\":\"${K[1]}\",\"proportion\":0.6},{\"tag\":\"${K[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $D, \"keyframes\": $KF}" >/dev/null; sleep $(echo "$D * 0.55" | bc); }

cheap_mode_disable_generative() {
  $CURL_POST_NF "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled":false}' >/dev/null || true
  $CURL_POST_NF "$BASE_URL/control/realtime-voice" -H "Content-Type: application/json" -d '{"action":"stop"}' >/dev/null || true
}

# --- 參數區 ---
BGM_URL="/audio/BGM/星際狂舞.mp3"
BGM_VOLUME=0.26

# 背景圖片（優先使用現有檔名；若無且允許，才生成）
BG_IMAGE_FILENAME=""
ALLOW_BG_GENERATION=true
BG_IMAGE_DESC="retro neon laser floor and starlit disco backdrop, high contrast"
BG_STYLE_VARIANT="ansi_16color"

SETS=5                 # 大段數（每段有 A/B/C 三拍 + 停）
FAST_TD_MIN=0.30       # 更短轉場（爆快）
FAST_TD_MAX=0.45
SLOW_TD=0.60           # 「慢」也拉快

BASE_A_MIN=2.60        # A：爆發（更高速）
BASE_A_MAX=3.30
YOGA_A_MIN=1.20
YOGA_A_MAX=1.50

BASE_B=2.40            # B：對拍（舞+運動混合）
YOGA_B_DANCE_MIN=1.20
YOGA_B_DANCE_MAX=1.50
YOGA_B_SPORT_MIN=1.30
YOGA_B_SPORT_MAX=1.60

BASE_C=2.10            # C：反拍（拉長但仍快）
YOGA_C_MIN=1.00
YOGA_C_MAX=1.20

PULSE_SCALE=0.14
BASE_SCALE=0.10
PULSE_DUR=0.06
FLASH_PROB_DENOM=3
JITTER_X_MIN=-0.6
JITTER_X_MAX=0.6
JITTER_Z_MIN=-30.4
JITTER_Z_MAX=-29.6

FINAL_BURST_ROUNDS=10  # 最終爆發回合

EMO_HYPE=("triumphant,proud,joyful" "joyful,excited,triumphant")
EMO_FOCUS=("interested,determined,proud" "excited,interested,hopeful")
LINES_INTRO=(
  $'星際對拍，準備！
Galactic beat—ready!'
  $'抓住拍點，身體先放鬆。
Catch the beat—relax first.'
)
LINES_CALL=(
  $'一—二—三—四！
One—two—three—four!'
  $'左—右—前—後！
Left—right—front—back!'
)
LINES_OUTRO=(
  $'最後爆發—精彩收尾！
Final burst—grand finish!'
)

echo "=== 🧘 Space Yoga Teacher — Galactic Battle Groove 開始 ==="

cheap_mode_disable_generative
stop_bgm
env_preset "studio" || true
env_background false || true
env_intensity 0.95 || true
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.9 true
set_background_image "$BG_IMAGE_FILENAME" || true
if [[ "$ALLOW_BG_GENERATION" == "true" && -z "$BG_IMAGE_FILENAME" ]]; then generate_background_image "$BG_IMAGE_DESC" "$BG_STYLE_VARIANT" || true; fi
bgm "$BGM_URL" $BGM_VOLUME

# 強制開場口令一次
say_with_inst "$(rand_choice LINES_INTRO[@])" 2.6 "$(rand_choice EMO_HYPE[@])" "$VOICE_NAME" $TTS_SPEED 1 "$TTS_INSTR"
emote 1.0 "$(rand_choice EMO_HYPE[@])"

# 主體：SETS 段，每段 A(爆發)-B(對拍)-C(反拍)-停
for ((s=1; s<=SETS; s++)); do
  env_intensity $(rand_float 0.90 1.05 2)
  # A：爆發
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
  char_rotation $(rand_float -0.15 0.15 2) $(rand_float -0.30 0.30 2) $(rand_float -0.20 0.20 2)
  char_bodyshape_rand
  anim_mix_combo $(rand_float $BASE_A_MIN $BASE_A_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "舞步1" 1.0 $(rand_float $YOGA_A_MIN $YOGA_A_MAX 2) \
    "舞步3" 1.0 $(rand_float $YOGA_A_MIN $YOGA_A_MAX 2)
  emote 0.9 "$(rand_choice EMO_HYPE[@])"

  # B：對拍（舞+運動）
  anim_mix_combo $BASE_B $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "舞步2" 1.0 $(rand_float $YOGA_B_DANCE_MIN $YOGA_B_DANCE_MAX 2) \
    "運動2" 1.0 $(rand_float $YOGA_B_SPORT_MIN $YOGA_B_SPORT_MAX 2)
  char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
  char_rotation $(rand_float -0.10 0.10 2) $(rand_float -0.20 0.20 2) $(rand_float -0.15 0.15 2)
  if (( RANDOM % 2 == 0 )); then char_bodyshape_rand; fi
  emote 1.0 "$(rand_choice EMO_FOCUS[@])"

  # C：反拍（拉長）
  anim_mix_combo $BASE_C $SLOW_TD \
    "瑜珈動作$(shuf -e 2 6 11 14 17 | head -n1 2>/dev/null || echo 2)" 1.0 $(rand_float $YOGA_C_MIN $YOGA_C_MAX 2)
  char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
  char_rotation $(rand_float -0.08 0.08 2) $(rand_float -0.12 0.12 2) $(rand_float -0.10 0.10 2)
  emote 1.2 "serene,content,relieved"

  # 停：位置抖動 + 短口令（節流）
  char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
  char_rotation $(rand_float -0.06 0.06 2) $(rand_float -0.10 0.10 2) $(rand_float -0.08 0.08 2)
  say_with_inst "$(rand_choice LINES_CALL[@])" 2.4 "$(rand_choice EMO_HYPE[@])"
  sleep 0.6
done

# 最終爆發段（連續強拍）
for ((k=1; k<=FINAL_BURST_ROUNDS; k++)); do
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  # 狂舞：隨機位姿 + 旋轉
  char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
  char_rotation $(rand_float -0.20 0.20 2) $(rand_float -0.35 0.35 2) $(rand_float -0.25 0.25 2)
  char_bodyshape_rand
  anim_mix_combo $(rand_float $BASE_A_MIN $BASE_A_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "舞步1" 1.0 $(rand_float $YOGA_A_MIN $YOGA_A_MAX 2) \
    "運動1" 1.0 $(rand_float $YOGA_A_MIN $YOGA_A_MAX 2)
  emote 1.0 "$(rand_choice EMO_HYPE[@])"
  if (( RANDOM % FLASH_PROB_DENOM == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
  sleep $(rand_float 1.0 1.4 2)
done

# 收尾口令 + 定格（BGM 繼續）
say_with_inst "$(rand_choice LINES_OUTRO[@])" 2.6 "$(rand_choice EMO_HYPE[@])" "$VOICE_NAME" $TTS_SPEED 1 "$TTS_INSTR"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Galactic Battle Groove 結束（BGM 持續播放） ==="
