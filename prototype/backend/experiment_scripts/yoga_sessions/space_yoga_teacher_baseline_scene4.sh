#!/bin/bash

# 《Space Yoga Teacher — Zero-Gravity Flow》
# 更自由的零重力瑜伽：旋轉、漂浮、縮放脈動；語句極短；情緒更豐富。
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene4.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# ---- 文本播放設定（無 TTS，僅字幕同步） ----
# 保留 voice/speed 預設值以維持腳本介面相容；實際不再觸發雲端語音。
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.5

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say() {
# 用法: say "內容" 時長(秒) "emotion1,emotion2,..." [legacy_voice] [legacy_speed]
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,interested,confident"}
  # 參數4+（voice/speed/force）保留相容性，目前僅用於字幕同步，不再觸發 TTS。
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
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
  echo "   >> [字幕] payload -> chat-message"
  $CURL_POST "$BASE_URL/control/broadcast" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" >/dev/null
  # 發送情緒軌跡（將情緒清單分三段過渡）
  local IFS=','; read -ra KFS <<< "$EMOS"; unset IFS
  local KF_JSON="[]"
  if (( ${#KFS[@]} == 1 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"
  elif (( ${#KFS[@]} == 2 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"
  else
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"
  fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" \
    -H "Content-Type: application/json" \
    -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  # 節奏控制（略短於全時長，避免阻塞下一拍）
  sleep $(echo "$DURATION * 0.85" | bc)
}

# 只走表情（不說話）
emote() {
  local DURATION=${1:-2.0}; local EMOS=${2:-"serene,content,joyful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.6" | bc)
}

bgm() { local URL="$1"; local VOL=${2:-0.25}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }

## 鏡位相關操作已移除

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
anim_mix() {
  local OTHER="$1"; local W=${2:-0.9}; local SPEED=${3:-0.7}; local TD=${4:-0.8}; local BLEND=${5:-"additive"}; local BASESPD=${6:-1.5}
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name": "空體Action", "weight": 1.0, "loop": true, "speed": $BASESPD},
    {"name": "漂浮", "weight": 0.8, "loop": true, "speed": 0.8},
    {"name": "$OTHER", "weight": $W, "loop": true, "speed": $SPEED}
  ],
  "transitionDuration": $TD,
  "blendMode": "$BLEND"
}
JSON
)
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-1.0}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-true}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }

# 中英併行語句（保持一致風格）
say_zh_en() {
  # 用法: say_zh_en "中文" "English" 時長(秒) "emo1,emo2,emo3" [legacy_voice] [legacy_speed] [legacy_force]
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"neutral,interested,confident"}
  local COMBINED
  COMBINED=$(printf "%s\n%s" "$ZH" "$EN")
  say "$COMBINED" "$DUR" "$EMO"
}

YOGA_MOVES=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作9" "瑜珈動作12" "瑜珈動作15" "瑜珈動作18")

EMO_FLOAT=("serene,hopeful,joyful" "serene,awe,joyful" "serene,interested,awe")
EMO_PULSE=("determined,proud,triumphant" "interested,determined,proud" "awe,proud,triumphant")
EMO_SOFT=("grateful,content,serene" "relieved,grateful,serene" "serene,content,joyful")

echo "=== 🧘 Space Yoga Teacher — Zero-Gravity Flow 開始 ==="

# 關閉隨機鏡位，切夜景 + 降強度 + 背景可見
## 已移除：關閉隨機鏡位與鏡位 preset 設定
env_preset "night" || true
env_intensity 0.7 || true
env_background true || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -38.0
anim_char "空體Action" 1.0 true
sleep 0.8

# 開場：自然的語句
say_zh_en "咱攏輕輕浮起，先攏呼吸的步調。" "We rise light—find a steady rhythm." 2.8 "serene,interested,content"
emote 1.6 "serene,awe,joyful"
anim_mix "瑜珈動作7" 0.9 0.7 0.8 "additive" 1.5
# 穩定鏡位：取消 yaw/roll 的大幅變化，僅做溫和推進
## 已移除：鏡位過渡

# 主段：5 回合 — 旋轉、漂浮、縮放脈動，口令更完整
for i in {1..5}; do
  # 輕微縮放脈動
  char_scale 0.11; sleep 0.1; char_scale 0.1
  # 位置輕移（維持鏡位穩定，不再每回合轉動相機）
  DX=$(rand_float -1.0 1.0 2); char_position "$DX" 8.2 -37.8
  # 僅在中段做一次有意義的輕推鏡（pitch 輕微、FOV 微調）
  # 已移除：鏡位過渡（第 3 回合）
  # 漂浮 + 瑜伽混合（隨機挑）
  MOVE=$(rand_choice YOGA_MOVES[@])
  anim_mix "$MOVE" 0.95 0.75 0.8 "additive" 1.55
  # 情緒：在 FLOAT / PULSE 間切換
  if (( i % 2 == 1 )); then EM=$(rand_choice EMO_FLOAT[@]); else EM=$(rand_choice EMO_PULSE[@]); fi
  emote 1.6 "$EM"
  # 口令（更完整的引導語）
  case $((i%5)) in
    1) say_zh_en "入氣，胸口開，肩膀鬆落。" "Inhale—open the chest, drop the shoulders." 2.6 "serene,interested,content";;
    2) say_zh_en "出氣，肋骨合，肚肚收。" "Exhale—ribs knit, belly draws in." 2.6 "serene,relieved,content";;
    3) say_zh_en "手臂前伸外展，空間較闊。" "Extend—reach forward and out, make more space." 2.6 "hopeful,joyful,awe";;
    4) say_zh_en "核心收回，骨盆中立。" "Gather—draw in the core, pelvis neutral." 2.6 "determined,proud,serene";;
    0) say_zh_en "停一下，找到中心。" "Pause—find your center." 2.4 "serene,content,serene";;
  esac
done

# 短暫隱現（幻影）
char_visible false; sleep 0.25; char_visible true
emote 1.8 "surprised,awe,joyful"

# 收束：回正 — 低角度望上（語句更有情緒）
## 已移除：鏡位過渡
say_zh_en "慢慢回正，心沉落，呼吸繼續。" "Return to center—let the heart settle, breath continues." 2.8 "grateful,content,serene"
emote 2.4 "grateful,content,serene"

# 結束（不播放 BGM）
echo "=== ✅ Zero-Gravity Flow 結束 ==="
