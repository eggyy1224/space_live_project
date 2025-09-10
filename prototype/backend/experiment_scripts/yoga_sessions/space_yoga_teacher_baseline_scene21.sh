#!/bin/bash

# 《Space Yoga Teacher — Heavy Metal Forge Flow》（scene21）
# 主題：重金屬瑜伽（脈衝、反拍、爆發、Breakdown）。
# 設計：
# - 使用重金屬 BGM：/audio/BGM/heavy_metal_bgm_03.mp3（持續低音量鋪底）
# - 不搖鏡；以角色縮放脈衝、可見性快閃、姿態抖動與環境亮度脈動表現金屬節拍
# - 預設不使用生成式語音（可用參數開關），表情軌跡配合高能/收束氛圍
# - 多段結構：Intro（預熱）→ Riff 循環（對拍）→ Breakdown（慢而重）→ Blast Finale（爆發）

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
env_intensity() { local I=${1:-0.90}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
char_scale() { local S=${1:-0.10}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }
char_rotation() { local RX=${1:-0.0}; local RY=${2:-0.0}; local RZ=${3:-0.0}; $CURL_POST "$BASE_URL/control/character/rotation" -H "Content-Type: application/json" -d "{\"rotation\": [$RX,$RY,$RZ]}" >/dev/null; }

# outfit morph（體型微調）
char_bodyshape() {
  local KEY1=${1:-0.0}; local MIS=${2:-0.0}; local MIS1=${3:-0.0}
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{ "outfit_morphs": {"鍵 1": $KEY1, "錯置": $MIS, "錯置.001": $MIS1} }
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/outfit" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}
char_bodyshape_rand() { char_bodyshape $(rand_float 0.15 0.60 2) $(rand_float 0.00 0.30 2) $(rand_float 0.00 0.30 2); }

# 背景圖片（可選）
set_background_image() { local F="$1"; [ -z "$F" ] && return 0; $CURL_POST_NF "$BASE_URL/set-background-image" -H "Content-Type: application/json" -d "{\"filename\": \"$F\"}" >/dev/null; }
generate_background_image() { local DESC="$1"; local VARIANT=${2:-"ansi_16color"}; $CURL_POST_NF "$BASE_URL/generate-background-image" -H "Content-Type: application/json" -d "{\"description\": \"$DESC\", \"aspect_ratio\": \"16:9\", \"style_variant\": \"$VARIANT\"}" >/dev/null; }

# 混合：空體Action + 多重動作
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

# 表情（不說話）
emote() {
  local DURATION=${1:-1.0}; local EMOS=${2:-"triumphant,proud,joyful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]";
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.55" | bc)
}

# 語音（金屬黑腔風格）+ 表情；含節流
TTS_INSTR="Female contralto black/death metal growl; very low pitch, dark timbre, chest resonance, lower formant; gritty/raspy but intelligible; avoid brightness/air, no scream/shriek; short staccato calls; Taiwanese Hokkien primary + English stage calls; strictly avoid Mandarin accent; explicitly avoid male timbre."
# 使用自動女性低音音色候選（依序偏低）
VOICE_CANDIDATES=("nova" "coral" "ballad" "verse")
VOICE_NAME="auto"   # 'auto' 代表從 VOICE_CANDIDATES 隨機選擇
TTS_SPEED=0.52
TTS_EVERY_N=4
TTS_COOLDOWN=8
__SAY_COUNT=0
LAST_TTS_TS=0

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.4}; local EMOS=${3:-"triumphant,proud,joyful"}
  local VOICE=${4:-$VOICE_NAME}; local SPEED=${5:-$TTS_SPEED}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS / $VOICE@$SPEED)"
  __SAY_COUNT=$((__SAY_COUNT + 1)); local DO_TTS=0; local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then DO_TTS=1; else if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )) && (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then DO_TTS=1; fi; fi
  if (( DO_TTS == 1 )); then
    # 自動挑選女性低音音色
    if [[ "$VOICE" == "auto" ]]; then
      local N=${#VOICE_CANDIDATES[@]}
      VOICE=${VOICE_CANDIDATES[$((RANDOM % N))]}
    fi
    $CURL_POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$INSTR\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  fi
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"; 
  else KF_JSON="[{\"tag\": \"${KFS[0]}\",\"proportion\": 0.0},{\"tag\": \"${KFS[1]}\",\"proportion\": 0.6},{\"tag\": \"${KFS[2]}\",\"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.70" | bc)
}

# 關閉會用錢的自動行為
cheap_mode_disable_generative() {
  $CURL_POST_NF "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled":false}' >/dev/null || true
  $CURL_POST_NF "$BASE_URL/control/realtime-voice" -H "Content-Type: application/json" -d '{"action":"stop"}' >/dev/null || true
}

# --- 參數區 ---
BGM_URL="/audio/BGM/heavy_metal_bgm_03.mp3"
BGM_VOLUME=0.24

# 結構（可調）
INTRO_BARS=4
RIFF_GROUPS=6           # 每組 4 拍：強-弱-強-停
BREAKDOWN_BARS=6
BLAST_ROUNDS=12

# 轉場與速度
FAST_TD_MIN=0.22; FAST_TD_MAX=0.36
SLOW_TD=0.60
BASE_FAST_MIN=2.80; BASE_FAST_MAX=3.40
BASE_SLOW=2.10
YOGA_FAST_MIN=1.20; YOGA_FAST_MAX=1.50
YOGA_SLOW_MIN=0.90; YOGA_SLOW_MAX=1.10

# 節拍特效
PULSE_SCALE=0.13
BASE_SCALE=0.10
PULSE_DUR=0.08
FLASH_PROB_DENOM=3
POS_X_MIN=-1.2; POS_X_MAX=1.2
POS_Z_MIN=-30.6; POS_Z_MAX=-29.4

# Headbang（俯仰快速點頭）
headbang_pulse() {
  local CYCLES=${1:-4}; local AMP=${2:-0.28}; local SPEED=${3:-0.06}
  for ((h=1; h<=CYCLES; h++)); do
    char_rotation $AMP 0 0; sleep $SPEED; char_rotation -$AMP 0 0; sleep $SPEED
  done
  char_rotation 0 0 0
}

# 環繞旋轉（位置繞圈 + 身體 yaw 旋轉）
spin_orbit() {
  local STEPS=${1:-8}; local RADIUS=${2:-1.2}; local DUR=${3:-0.08};
  local ANG=0; local STEP_ANG=$(awk -v s=$STEPS 'BEGIN{print 6.283185/s}')
  for ((i=1;i<=STEPS;i++)); do
    local X=$(awk -v r=$RADIUS -v a=$ANG 'BEGIN{print r*cos(a)}')
    local Z=$(awk -v r=$RADIUS -v a=$ANG 'BEGIN{print -30.0 + r*sin(a)}')
    char_position $X 8.0 $Z
    local YAW=$(awk -v a=$ANG 'BEGIN{print a}')
    char_rotation 0 $YAW 0
    sleep $DUR
    ANG=$(awk -v a=$ANG -v da=$STEP_ANG 'BEGIN{print a+da}')
  done
}

# 背景圖設定（可選）
BG_IMAGE_FILENAME=""    # 放 frontend/public/background_pictures/ 下的檔名；空字串則忽略
ALLOW_BG_GENERATION=true
BG_IMAGE_DESC="industrial metal stage with red/black lights, smoke, high contrast silhouettes, gritty texture"
BG_STYLE_VARIANT="ansi_16color"

# 情緒池
EMO_HYPE=("triumphant,proud,joyful" "joyful,excited,triumphant")
EMO_DARK=("determined,proud,angry" "interested,determined,proud")
EMO_SOFT=("serene,content,relieved" "grateful,content,serene")

# 金屬口令（台語 + English）
LINES_INTRO=(
  "起火啦—warm up，入拍！\nKhí-hué lā—warm up, hit the beat!"
  "身軀撐穩，重拍進來。\nHold steady—downbeat in."
)
LINES_CALL=(
  "一—二—三—四—轉！\nOne—two—three—four—spin!"
  "落—起—落—起！\nDown—up—down—up!"
)
LINES_BREAKDOWN=(
  "沉—呼—定住。\nSink—breathe—hold."
)
LINES_OUTRO=(
  "最後一波—收！\nFinal wave—lock it!"
)

# 動作池
YOGA_POWER=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作9" "瑜珈動作12" "瑜珈動作17")
YOGA_HOLD=("瑜珈動作2" "瑜珈動作6" "瑜珈動作11" "瑜珈動作14")
DANCE_MOVES=("舞步1" "舞步2" "舞步3")
SPORT_MOVES=("運動1" "運動2")

echo "=== 🧘 Space Yoga Teacher — Heavy Metal Forge Flow（scene21）開始 ==="

# 開場：穩定基準 + BGM
cheap_mode_disable_generative
stop_bgm
env_preset "studio" || true
env_background false || true
env_intensity 0.92 || true
char_scale $BASE_SCALE
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.9 true
set_background_image "$BG_IMAGE_FILENAME" || true
if [[ "$ALLOW_BG_GENERATION" == "true" && -z "$BG_IMAGE_FILENAME" ]]; then generate_background_image "$BG_IMAGE_DESC" "$BG_STYLE_VARIANT" || true; fi
bgm "$BGM_URL" $BGM_VOLUME

# Intro：4 小節，亮度與縮放隨拍漸進，輕 Headbang + 口令
for ((i=1; i<=INTRO_BARS; i++)); do
  env_intensity $(rand_float 0.90 0.98 2)
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  anim_mix_combo $(rand_float $BASE_SLOW $BASE_SLOW 2) $SLOW_TD \
    "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
  headbang_pulse 3 0.20 0.08
  if (( i == 1 )); then say_with_inst "$(rand_choice LINES_INTRO[@])" 2.2 "$(rand_choice EMO_DARK[@])"; else emote 1.0 "$(rand_choice EMO_DARK[@])"; fi
  sleep 0.6
done

# Riff 循環：每組 4 拍（強-弱-強-停），對拍脈衝 + 快速混合
for ((g=1; g<=RIFF_GROUPS; g++)); do
  # 強拍1
  env_intensity $(rand_float 0.95 1.05 2)
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  anim_mix_combo $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "$(rand_choice DANCE_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2) \
    "$(rand_choice SPORT_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2)
  headbang_pulse 4 0.26 0.06
  say_with_inst "$(rand_choice LINES_CALL[@])" 1.8 "$(rand_choice EMO_HYPE[@])"
  if (( RANDOM % 2 == 0 )); then spin_orbit 8 1.0 0.06; fi

  # 弱拍
  anim_mix_combo $BASE_SLOW $SLOW_TD \
    "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
  char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) 8.0 $(rand_float $POS_Z_MIN $POS_Z_MAX 2)
  emote 1.0 "$(rand_choice EMO_DARK[@])"

  # 強拍2
  env_intensity $(rand_float 0.96 1.06 2)
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  anim_mix_combo $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "$(rand_choice YOGA_POWER[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2) \
    "$(rand_choice DANCE_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2)
  if (( RANDOM % 2 == 0 )); then char_bodyshape_rand; fi
  headbang_pulse 4 0.30 0.06
  if (( RANDOM % 2 == 0 )); then say_with_inst "$(rand_choice LINES_CALL[@])" 1.8 "$(rand_choice EMO_HYPE[@])"; else emote 0.9 "$(rand_choice EMO_HYPE[@])"; fi
  if (( RANDOM % 2 == 0 )); then spin_orbit 8 1.2 0.06; fi

  # 停（短休止）：可見性快閃 + 姿態抖動
  if (( RANDOM % FLASH_PROB_DENOM == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) 8.0 $(rand_float $POS_Z_MIN $POS_Z_MAX 2)
  char_rotation $(rand_float -0.08 0.08 2) $(rand_float -0.12 0.12 2) $(rand_float -0.10 0.10 2)
  sleep 0.6
done

# Breakdown：慢而重（長轉場 + 深表情），加強紅暗氛圍
for ((b=1; b<=BREAKDOWN_BARS; b++)); do
  env_intensity $(rand_float 0.82 0.90 2)
  anim_mix_combo $BASE_SLOW $SLOW_TD \
    "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
  headbang_pulse 2 0.18 0.10
  if (( b == 1 )); then say_with_inst "$(rand_choice LINES_BREAKDOWN[@])" 2.0 "$(rand_choice EMO_SOFT[@])"; else emote 1.4 "$(rand_choice EMO_SOFT[@])"; fi
  sleep 0.6
done

# Blast Finale：連續爆發（高速雙混 + 快轉場 + Headbang）
for ((k=1; k<=BLAST_ROUNDS; k++)); do
  env_intensity $(rand_float 0.96 1.08 2)
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  anim_mix_combo $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) $(rand_float $FAST_TD_MIN $FAST_TD_MAX 2) \
    "$(rand_choice YOGA_POWER[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2) \
    "$(rand_choice SPORT_MOVES[@])" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2)
  headbang_pulse 5 0.30 0.06
  if (( k % 3 == 1 )); then say_with_inst "$(rand_choice LINES_CALL[@])" 1.8 "$(rand_choice EMO_HYPE[@])"; else emote 0.9 "$(rand_choice EMO_HYPE[@])"; fi
  if (( RANDOM % FLASH_PROB_DENOM == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  if (( RANDOM % 2 == 0 )); then spin_orbit 10 1.3 0.05; else char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) 8.0 $(rand_float $POS_Z_MIN $POS_Z_MAX 2); fi
  sleep $(rand_float 0.9 1.2 2)
done

# 收尾：定格與放鬆（BGM 持續）
anim_mix_combo $BASE_SLOW $SLOW_TD \
  "$(rand_choice YOGA_HOLD[@])" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
say_with_inst "$(rand_choice LINES_OUTRO[@])" 2.2 "grateful,content,serene" "$VOICE_NAME" $TTS_SPEED 1 "$TTS_INSTR"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Heavy Metal Forge Flow 結束（BGM 持續播放） ==="
