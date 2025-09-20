#!/bin/bash

# 《Space Yoga Teacher — Stellar Disco Flow》
# 主題：星際狂舞（律動 × 舞步 × 流暢過渡）。
# 規則：
# - 使用 BGM：/audio/BGM/星際狂舞.mp3（持續播放，不在結尾停止）
# - 不搖鏡；以角色位置/縮放/可見性小變化強化舞感

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# --- 音訊/環境/角色控制（非生成）---
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
bgm() { local URL="$1"; local VOL=${2:-0.24}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
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
  # 安全範圍：主形 0.15–0.60，微調 0.00–0.30
  char_bodyshape $(rand_float 0.15 0.60 2) $(rand_float 0.00 0.30 2) $(rand_float 0.00 0.30 2)
}

# 背景圖片控制
set_background_image() { local F="$1"; [ -z "$F" ] && return 0; $CURL_POST_NF "$BASE_URL/set-background-image" -H "Content-Type: application/json" -d "{\"filename\": \"$F\"}" >/dev/null; }
generate_background_image() { local DESC="$1"; local VARIANT=${2:-"ansi_16color"}; $CURL_POST_NF "$BASE_URL/generate-background-image" -H "Content-Type: application/json" -d "{\"description\": \"$DESC\", \"aspect_ratio\": \"16:9\", \"style_variant\": \"$VARIANT\"}" >/dev/null; }

# 混合器：空體Action + 多重動作（可混舞/運動/瑜伽）
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

TTS_INSTR="Taiwanese Hokkien, Han characters, playful, energetic, crisp articulation; avoid Mandarin accent"
VOICE_NAME="sage"
TTS_SPEED=0.60

say_with_inst() {
  local CONTENT="$1"; local DURATION=${2:-2.6}; local EMOS=${3:-"joyful,excited,triumphant"}
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

emote() { local D=${1:-1.0}; local EMOS=${2:-"joyful,excited,triumphant"}; IFS=',' read -ra K<<<"$EMOS"; local KF; 
  if (( ${#K[@]}==1 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#K[@]}==2 )); then KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.5},{\"tag\":\"${K[1]}\",\"proportion\":1.0}]"; 
  else KF="[{\"tag\":\"${K[0]}\",\"proportion\":0.0},{\"tag\":\"${K[1]}\",\"proportion\":0.6},{\"tag\":\"${K[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $D, \"keyframes\": $KF}" >/dev/null; sleep $(echo "$D * 0.55" | bc); }

# 關閉會用錢的自動行為（保留少量主動台詞）
cheap_mode_disable_generative() {
  $CURL_POST_NF "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled":false}' >/dev/null || true
  $CURL_POST_NF "$BASE_URL/control/realtime-voice" -H "Content-Type: application/json" -d '{"action":"stop"}' >/dev/null || true
}

# --- 參數區 ---
BGM_URL="/audio/BGM/星際狂舞.mp3"
BGM_VOLUME=0.24

# 背景圖片（優先使用現有檔名；若無且允許，才生成）
BG_IMAGE_FILENAME=""    # 例如：disco_grid.png（放在 frontend/public/background_pictures/ 下）
ALLOW_BG_GENERATION=true
BG_IMAGE_DESC="retro-futuristic neon disco grid in space, high contrast, clean silhouettes"
BG_STYLE_VARIANT="ansi_16color"

GROUPS=6               # 組數（每組 4 段）
TDUR_FAST_MIN=0.22     # 快轉場（更短，爆快）
TDUR_FAST_MAX=0.36
TDUR_SLOW=0.50         # 慢轉場也加快

BASE_FAST_MIN=3.00     # 基底高速範圍（更爆）
BASE_FAST_MAX=3.60
BASE_SLOW=2.40         # 「慢」也維持快感

YOGA_FAST_MIN=1.40
YOGA_FAST_MAX=1.70
YOGA_SLOW_MIN=1.10
YOGA_SLOW_MAX=1.30

PULSE_SCALE=0.14       # 脈衝更明顯
BASE_SCALE=0.10
PULSE_DUR=0.06         # 脈衝更短更快

# 畫面位姿/胖瘦（縮放）範圍
POS_X_MIN=-2.0; POS_X_MAX=2.0
POS_Y_MIN=7.8; POS_Y_MAX=8.6
POS_Z_MIN=-31.5; POS_Z_MAX=-28.5
ROT_P_MIN=-0.15; ROT_P_MAX=0.15
ROT_Y_MIN=-0.35; ROT_Y_MAX=0.35
ROT_R_MIN=-0.25; ROT_R_MAX=0.25
SCALE_MIN=0.10; SCALE_MAX=0.14

# 狂舞位姿變換（位置/旋轉/縮放）
burst_pose() {
  char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) $(rand_float $POS_Y_MIN $POS_Y_MAX 2) $(rand_float $POS_Z_MIN $POS_Z_MAX 2)
  char_rotation $(rand_float $ROT_P_MIN $ROT_P_MAX 2) $(rand_float $ROT_Y_MIN $ROT_Y_MAX 2) $(rand_float $ROT_R_MIN $ROT_R_MAX 2)
  char_scale $(rand_float $SCALE_MIN $SCALE_MAX 2)
  char_bodyshape_rand
}

JITTER_X_MIN=-0.6
JITTER_X_MAX=0.6
JITTER_Z_MIN=-30.4
JITTER_Z_MAX=-29.6

LINES_START=(
  $'星際狂舞開啟，跟上拍子！
Stellar disco on—follow the beat!'
  $'燈光就位，身體先熱起來。
Lights set—warm the body first.'
)
LINES_GROUP=(
  $'左—右—轉！
Left—right—spin!'
  $'點頭—側步—延伸。
Nod—side—reach.'
  $'快—慢—收！
Fast—slow—hold!'
)
LINES_BREAK=(
  $'吸氣抬胸，吐氣沉肩。
Inhale lift, exhale soften.'
  $'找核心，腳跟踩穩。
Find core, root the heels.'
)
EMO_HYPE=("joyful,excited,triumphant" "triumphant,proud,joyful")
EMO_SOFT=("interested,determined,proud" "serene,content,relieved")

echo "=== 🧘 Space Yoga Teacher — Stellar Disco Flow 開始 ==="

# 開場：穩定基準 + BGM
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

# 開場台詞（強制一次）
say_with_inst "$(rand_choice LINES_START[@])" 2.6 "joyful,excited,triumphant" "$VOICE_NAME" $TTS_SPEED 1 "$TTS_INSTR"
emote 1.0 "joyful,excited,triumphant"

# 主段：多組（每組4段：強-弱-弱-停）
for ((g=1; g<=GROUPS; g++)); do
  env_intensity $(rand_float 0.90 1.05 2)
  # 強拍：脈衝 + 高速混合
  char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
  burst_pose
  anim_mix_combo $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) $(rand_float $TDUR_FAST_MIN $TDUR_FAST_MAX 2) \
    "舞步1" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2) \
    "運動1" 1.0 $(rand_float $YOGA_FAST_MIN $YOGA_FAST_MAX 2)
  emote 0.9 "$(rand_choice EMO_HYPE[@])"
  # 弱拍1：慢混 + 專注
  anim_mix_combo $BASE_SLOW $TDUR_SLOW \
    "瑜珈動作$(shuf -e 2 6 11 14 17 | head -n1 2>/dev/null || echo 2)" 1.0 $(rand_float $YOGA_SLOW_MIN $YOGA_SLOW_MAX 2)
  burst_pose; emote 1.1 "$(rand_choice EMO_SOFT[@])"
  # 弱拍2：慢混 + 放鬆
  anim_mix_combo $BASE_SLOW $TDUR_SLOW \
    "舞步2" 1.0 $(rand_float 0.95 1.10 2)
  burst_pose; emote 1.1 "serene,content,relieved"
  # 停：微抖動 + 小口令（節流）
  char_position $(rand_float $POS_X_MIN $POS_X_MAX 2) 8.0 $(rand_float $POS_Z_MIN $POS_Z_MAX 2)
  char_rotation $(rand_float -0.08 0.08 2) $(rand_float -0.12 0.12 2) $(rand_float -0.10 0.10 2)
  say_with_inst "$(rand_choice LINES_GROUP[@])" 2.4 "$(rand_choice EMO_HYPE[@])"
  sleep 0.6
done

# 收尾：一句口令 + 表情定格（BGM 繼續）
  say_with_inst $'最後一回—收住，穩住。
Final bar—hold, steady.' 2.6 "interested,determined,proud" "$VOICE_NAME" $TTS_SPEED 1 "$TTS_INSTR"
emote 1.6 "grateful,content,serene"

echo "=== ✅ Stellar Disco Flow 結束（BGM 持續播放） ==="
