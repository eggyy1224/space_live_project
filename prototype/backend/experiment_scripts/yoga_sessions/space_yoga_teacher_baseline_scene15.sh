#!/bin/bash

# 《Space Yoga Teacher — Supernova Burst Flow》
# 目標：無 TTS 純動作＋表情「炸裂」演出，維持不搖鏡，強節奏、強能量。
# 規則：
# - 不觸發任何 TTS 或 SFX / BGM
# - 僅使用表情軌跡與高速動畫混合，短暫可見性/縮放脈衝，營造爆裂感
# - 鏡位固定（不使用相機控制）

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
  local CONTENT="$1"; local DURATION=${2:-2.8}; local EMOS=${3:-"triumphant,proud,joyful"}
  local VOICE=${4:-"nova"}; local SPEED=${5:-1.0}; local INSTR=${6:-"Taiwanese Hokkien, Han characters, energetic, triumphant, crisp articulation; avoid Mandarin accent"}
  $CURL_POST "$BASE_URL/control/send-message" \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$INSTR\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null

  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]"; 
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.85" | bc)
}

# 僅表情（不說話）
emote() {
  local DURATION=${1:-1.0}; local EMOS=${2:-"triumphant,proud,joyful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]";
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.55" | bc)
}

# 基底設定（無音樂）
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }

# 高速混合：空體Action + 2~3 瑜伽動作（高權重、高速度），短轉場
anim_mix_blast() {
  local BASESPD=$(rand_float 2.1 2.6 2)   # 基底高速
  local YOGA_SPD=$(rand_float 1.05 1.30 2) # 瑜伽動作高速
  local TD=$(rand_float 0.35 0.55 2)       # 短轉場
  local COUNT=$(( (RANDOM % 2) + 2 ))      # 2 或 3 個動作

  local MOVES=(
    "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
    "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
    "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
    "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
  )

  local ITEMS
  ITEMS=$(cat <<JSON
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD}
JSON
  )
  for ((k=0;k<COUNT;k++)); do
    local M; M=$(rand_choice MOVES[@])
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

# 情緒池（高能）
EMO_BLAST=(
  "triumphant,proud,joyful"
  "awe,triumphant,joyful"
  "determined,proud,triumphant"
  "smug,playful,joyful"
)

echo "=== 🧘 Space Yoga Teacher — Supernova Burst Flow 開始 ==="

env_preset "studio" || true
stop_bgm
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 2.0 true

# 僅此一句：高能開場台詞（搭配炸裂情緒）
say_line "引爆能量——光灑整個艙室。\nSupernova burst—light up the bay." 2.8 "triumphant,proud,joyful" "nova" 1.02 "Taiwanese Hokkien, Han characters, energetic, triumphant, crisp articulation; avoid Mandarin accent"

# 爆裂段落：6 回合（每回合：脈衝縮放→高速混合→炸裂表情→可見性閃爍）
for i in {1..6}; do
  # 縮放脈衝
  char_scale 0.12; sleep 0.08; char_scale 0.1
  # 位置微抖動（保持鏡位穩定）
  DX=$(rand_float -1.0 1.0 2); DY=$(rand_float 7.8 8.4 2); DZ=$(rand_float -30.4 -29.6 2)
  char_position "$DX" "$DY" "$DZ"
  # 高速混合
  anim_mix_blast
  # 給高速混合留出可見時間
  sleep $(rand_float 1.2 1.6 2)
  # 炸裂表情
  EM=$(rand_choice EMO_BLAST[@]); emote 1.0 "$EM"
  # 可見性閃爍（幻影感）
  if (( RANDOM % 3 == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
  # 段落停頓，避免過快切換
  sleep 1.0
done

# 收束：強而穩的表情
emote 1.4 "triumphant,proud,joyful"

echo "=== ✅ Supernova Burst Flow 結束（無語音，純動作與表情） ==="
