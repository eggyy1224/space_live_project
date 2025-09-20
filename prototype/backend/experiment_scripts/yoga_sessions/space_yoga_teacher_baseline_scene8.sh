#!/bin/bash

# 《Space Yoga Teacher — Comet Interval Flow》
# 方向：彗星間歇（爆發 × 回復交替）。鏡位穩定、無 BGM、僅安靜太空艙 ambience。
# 重點：
# - 快慢強烈對比（base 與瑜伽速度成對調），過渡時長亦對比（短/長）
# - 20 動作袋子抽樣，段內每次混合 2–3 個招式，weight=1.0
# - TTS 以不同 voice/speed/instruction 呈現「爆發/回復」兩種語氣
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene8.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

TTS_INSTR_COOL="Taiwanese Hokkien, Han characters, calm, warm, intimate, soft consonants; avoid Mandarin accent"
TTS_INSTR_BURST="Taiwanese Hokkien, Han characters, energetic, urgent, crisp articulation; avoid Mandarin accent"

VOICE_COOL="sage"
VOICE_BURST="nova"

SPEED_COOL_MIN=0.50
SPEED_COOL_MAX=0.60
SPEED_BURST_MIN=0.95
SPEED_BURST_MAX=1.10


# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_int()   { local MIN=$1; local MAX=$2; awk -v min="$MIN" -v max="$MAX" 'BEGIN{srand(); printf("%d\n", int(min+rand()*(max-min+1)))}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say_with_inst() {
  # 用法: say_with_inst content duration emos voice speed force instruction
  local CONTENT="$1"; local DURATION=${2:-2.6}; local EMOS=${3:-"serene,content,grateful"}
  local VOICE=${4:-$VOICE_COOL}; local SPEED=${5:-0.6}; local FORCE=${6:-0}; local INSTR=${7:-$TTS_INSTR_COOL}
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
  sleep $(echo "$DURATION * 0.75" | bc)
}

say_burst_zh_en() {
  # 用法: say_burst_zh_en zh en dur emos
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.2}; local EMO=${4:-"triumphant,proud,joyful"}
  local COMBINED
  COMBINED=$(printf "%s\n%s" "$ZH" "$EN")
  say_with_inst "$COMBINED" "$DUR" "$EMO" "$VOICE_BURST" "$(rand_float $SPEED_BURST_MIN $SPEED_BURST_MAX 2)" 0 "$TTS_INSTR_BURST"
}

say_cool_zh_en() {
  # 用法: say_cool_zh_en zh en dur emos
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"serene,content,relieved"}
  local COMBINED
  COMBINED=$(printf "%s\n%s" "$ZH" "$EN")
  say_with_inst "$COMBINED" "$DUR" "$EMO" "$VOICE_COOL" "$(rand_float $SPEED_COOL_MIN $SPEED_COOL_MAX 2)" 0 "$TTS_INSTR_COOL"
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

echo "=== 🧘 Space Yoga Teacher — Comet Interval Flow 開始 ==="

## 已移除：關閉隨機鏡位（randomMode）

# 初始：studio 明亮 + 輕 ambience；固定鏡位
## 已移除：鏡位 preset 設定
env_preset "studio" || true
env_intensity 1.2 || true
env_background false || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 2.2 true
sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03

# 導語（平靜語氣）
say_with_inst $'彗星間歇。快爆一段，慢回一段。
Comet intervals—burst, then recover.' 2.8 "serene,content,relieved" "$VOICE_COOL" "$(rand_float $SPEED_COOL_MIN $SPEED_COOL_MAX 2)" 1 "$TTS_INSTR_COOL"
emote 1.2 "serene,content,relieved"

# 主段：6 回合（爆發×回復 交替）
for i in {1..6}; do
  if (( i % 2 == 1 )); then
    # 爆發：更快 base / 瑜伽，過渡短，漂浮快；台詞急促
    anim_mix_multi \
      $(rand_float 2.8 3.4 2) \
      $(rand_float 1.05 1.30 2) \
      $(rand_float 0.35 0.55 2) \
      $(rand_float 0.95 1.15 2) \
      $(rand_int 2 3)
    say_burst_zh_en "爆一下，胸口開！" "Burst—open the chest!" 2.2 "triumphant,proud,joyful"
    sleep 0.6
  else
    # 回復：較慢 base / 瑜伽，過渡長，漂浮慢；台詞溫和
    anim_mix_multi \
      $(rand_float 1.6 1.9 2) \
      $(rand_float 0.58 0.75 2) \
      $(rand_float 0.80 0.95 2) \
      $(rand_float 0.65 0.82 2) \
      $(rand_int 2 3)
    say_cool_zh_en "停一息，慢慢收回。" "Pause—gather slowly." 2.6 "serene,content,relieved"
    sleep 0.8
  fi

  # 固定鏡位，僅做角色輕微位移，避免搖鏡
  char_position $(rand_float -1.2 1.2 1) 8.$(rand_int 0 4) -30.$(rand_int 0 4)

  # 間歇性極低 ambience 維持空間感
  if (( RANDOM % 3 == 0 )); then sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03; fi
done

# 收束：平穩回正
char_position 0.0 8.0 -30.0
emote 1.6 "grateful,content,serene"
say_with_inst $'完成——速度對比，心猶穩。
Done—contrast held, center steady.' 2.8 "grateful,content,serene" "$VOICE_COOL" "$(rand_float $SPEED_COOL_MIN $SPEED_COOL_MAX 2)" 1 "$TTS_INSTR_COOL"

echo "=== ✅ Comet Interval Flow 結束（安靜氛圍，無 BGM） ==="
