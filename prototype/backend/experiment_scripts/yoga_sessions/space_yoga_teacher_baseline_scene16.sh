#!/bin/bash

# 《Space Yoga Teacher — Motion Playground Flow》
# 目標：不使用 TTS / SFX，專注在「多動作混合 × 速度對比 × 表情張力」。
# - 固定鏡位、不搖鏡
# - 使用非瑜伽與瑜伽混合（空體Action、運動1/2、漂浮/漂浮2、飛1/飛2、舞步1/2/3、Tpose、不穩、划手機、臥躺、瑜珈動作1–20）
# - 以回合形式組合：滑行 → 舞動 → 飛行/落身，並在段間注入表情炸裂點

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# 說一句話（搭配情緒軌跡）
say_line() {
  # 用法: say_line "內容" 時長(秒) "emo1,emo2,emo3" voice speed instruction
  local CONTENT="$1"; local DURATION=${2:-2.8}; local EMOS=${3:-"playful,amused,joyful"}
  local VOICE=${4:-"sage"}; local SPEED=${5:-0.58}; local INSTR=${6:-"Taiwanese Hokkien, Han characters, playful, warm, friendly; avoid Mandarin accent"}
  local LOG_CONTENT=${CONTENT//$'\n'/\\n}
  echo ">> 說話: $LOG_CONTENT ($DURATION s / $EMOS)"
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
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]"; 
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.85" | bc)
}

# 僅表情（不說話）
emote() {
  local DURATION=${1:-1.2}; local EMOS=${2:-"joyful,excited,triumphant"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]";
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.55" | bc)
}

# 基底/場務
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }

# 可用動作池（含非瑜伽）
MOVES_SLOW=("漂浮" "漂浮2" "臥躺" "Tpose" "不穩" "划手機")
MOVES_DANCE=("舞步1" "舞步2" "舞步3")
MOVES_FLY=("飛1" "飛2")
MOVES_SPORT=("運動1" "運動2")
MOVES_YOGA=(
  "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
  "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
  "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
  "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
)

# 混合器：空體Action + 多重動作（可混舞、飛、體能、瑜伽），速度對比
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

# 表情池（參考 emotionMappings.ts 的有效標籤）
EMO_COOL=("serene,content,relieved" "grateful,content,serene")
EMO_HYPE=("joyful,excited,triumphant" "playful,amused,joyful" "triumphant,proud,joyful")
EMO_FOCUS=("interested,determined,proud" "excited,interested,hopeful")

echo "=== 🧘 Space Yoga Teacher — Motion Playground Flow 開始 ==="

env_preset "studio" || true
stop_bgm
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.6 true

# 僅此一句：活力開場台詞（搭配玩心表情）
say_line $'動起來——身體自由，節奏自己決定。
Move flows—body free, rhythm is yours.' 2.8 "playful,amused,joyful" "sage" 0.58 "Taiwanese Hokkien, Han characters, playful, warm, friendly; avoid Mandarin accent"

# 回合 A（滑行 × 體能 × 瑜伽，慢-快-慢 對比）
for i in {1..2}; do
  # 慢：漂浮/臥躺類（慢速 0.5–0.7）
  SLOW=$(rand_choice MOVES_SLOW[@])
  anim_mix_combo $(rand_float 1.6 1.8 2) $(rand_float 0.5 0.7 2) "$SLOW" 0.9 $(rand_float 0.55 0.70 2)
  # 留出慢速段可視時間
  sleep $(rand_float 1.8 2.4 2)
  emote 1.2 "$(rand_choice EMO_COOL[@])"

  # 快：運動/舞動類（1.2–1.4）
  SPORT=$(rand_choice MOVES_SPORT[@])
  DANCE=$(rand_choice MOVES_DANCE[@])
  anim_mix_combo $(rand_float 1.9 2.1 2) $(rand_float 0.45 0.60 2) "$SPORT" 1.0 $(rand_float 1.15 1.35 2) "$DANCE" 1.0 $(rand_float 1.10 1.30 2)
  # 留出快速段可視時間
  sleep $(rand_float 1.2 1.6 2)
  emote 1.0 "$(rand_choice EMO_HYPE[@])"

  # 再慢：隨機瑜伽一式（0.6–0.8）
  YOGA=$(rand_choice MOVES_YOGA[@])
  anim_mix_combo $(rand_float 1.7 1.9 2) 0.6 "$YOGA" 1.0 $(rand_float 0.60 0.80 2)
  # 留出瑜伽段可視時間
  sleep $(rand_float 1.6 2.0 2)
  emote 1.0 "$(rand_choice EMO_FOCUS[@])"
done

# 回合 B（飛行 × 舞動 × 不穩，加入縮放脈衝與閃爍）
for i in {1..2}; do
  # 飛行：飛1/飛2（1.0–1.2）
  FLY=$(rand_choice MOVES_FLY[@])
  anim_mix_combo $(rand_float 1.8 2.0 2) 0.5 "$FLY" 1.0 $(rand_float 1.00 1.20 2)
  # 留出飛行段可視時間
  sleep $(rand_float 1.2 1.6 2)
  # 脈衝與閃爍
  char_scale 0.11; sleep 0.10; char_scale 0.1
  if (( RANDOM % 3 == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  emote 1.0 "$(rand_choice EMO_HYPE[@])"

  # 舞動混合：舞步 + 運動 + 瑜伽（速度分層）
  DANCE=$(rand_choice MOVES_DANCE[@])
  SPORT=$(rand_choice MOVES_SPORT[@])
  YOGA=$(rand_choice MOVES_YOGA[@])
  anim_mix_combo $(rand_float 1.8 2.1 2) 0.6 \
    "$DANCE" 1.0 $(rand_float 1.00 1.20 2) \
    "$SPORT" 0.9 $(rand_float 1.10 1.30 2) \
    "$YOGA" 0.8 $(rand_float 0.65 0.85 2)
  # 留出舞動段可視時間
  sleep $(rand_float 1.2 1.6 2)
  emote 1.0 "$(rand_choice EMO_FOCUS[@])"

  # 收回：漂浮/不穩（慢速）
  SLOW=$(rand_choice MOVES_SLOW[@])
  anim_mix_combo $(rand_float 1.6 1.8 2) 0.6 "$SLOW" 1.0 $(rand_float 0.55 0.75 2)
  # 留出收回段可視時間
  sleep $(rand_float 1.6 2.2 2)
  emote 1.2 "$(rand_choice EMO_COOL[@])"
done

# 結尾：強表情 + 定格（保持空體Action）
emote 1.6 "triumphant,proud,joyful"

echo "=== ✅ Motion Playground Flow 結束（無語音，純動作與表情） ==="
