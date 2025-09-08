#!/bin/bash

# 《Space Yoga Teacher — Nebula Stillness》
# 方向：星雲靜定。以極穩的鏡頭與慢速動作，營造「靜中有動」。
# 規則：瑜伽進行期間不放 BGM；僅在段落邊界給極輕環境音效提示；結尾不播 BGM。
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene6.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止（避免暫時無連線時整段中斷）

# --- 全域 TTS 設定（台語／漢字）---
TTS_INSTRUCTION="Taiwanese Hokkien, Han characters, natural, warm, friendly, accurate tones; avoid Mandarin accent"
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.5

# TTS 節流/降載
TTS_EVERY_N=3
TTS_COOLDOWN=5
__SAY_COUNT=0
LAST_TTS_TS=0

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_int()   { local MIN=$1; local MAX=$2; awk -v min="$MIN" -v max="$MAX" 'BEGIN{srand(); printf("%d\n", int(min+rand()*(max-min+1)))}'; }

say() {
  # 用法: say "內容" 時長(秒) "emo1,emo2,emo3" [voice] [speed] [force]
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"serene,content,grateful"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-0}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  __SAY_COUNT=$((__SAY_COUNT + 1)); local DO_TTS=0; local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then DO_TTS=1; else if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )) && (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then DO_TTS=1; fi; fi
  if (( DO_TTS == 1 )); then
    $CURL_POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" \
      -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  else
    echo "   >> [SKIP TTS]（降載：僅表情過渡）"
  fi
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.85" | bc)
}

emote() {
  local DURATION=${1:-1.6}; local EMOS=${2:-"serene,content,grateful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.6" | bc)
}

bgm() { local URL="$1"; local VOL=${2:-0.2}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
sfx() { local URL="$1"; local VOL=${2:-0.06}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$URL\", \"volume\": $VOL}" >/dev/null; }

## 鏡位相關操作已移除

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

# 動畫混合（優先空體Action，偶爾加入漂浮第三層）
anim_mix_diverse() {
  local MOVE="$1"
  local BASESPD=${2:-1.45}
  local YOGA_W=${3:-0.72}
  local YOGA_SPD=${4:-0.62}
  local TD=${5:-0.8}
  local ADD_FLOAT=${6:-0}   # 1 則加入「漂浮」
  local PAYLOAD
  if (( ADD_FLOAT == 1 )); then
    PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name": "空體Action", "weight": 1.0, "loop": true, "speed": $BASESPD},
    {"name": "漂浮", "weight": 0.3, "loop": true, "speed": 0.8},
    {"name": "$MOVE", "weight": $YOGA_W, "loop": true, "speed": $YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
)
  else
    PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name": "空體Action", "weight": 1.0, "loop": true, "speed": $BASESPD},
    {"name": "$MOVE", "weight": $YOGA_W, "loop": true, "speed": $YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
)
  fi
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-0.8}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

say_zh_en() {
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"serene,content,grateful"}
  local VOICE=${5:-$TTS_VOICE_DEFAULT}; local SPEED=${6:-$TTS_SPEED_DEFAULT}; local FORCE=${7:-0}
  say "$ZH\n$EN" "$DUR" "$EMO" "$VOICE" "$SPEED" "$FORCE"
}

# ---- 多樣性：20 動作 + 袋子抽樣，避免重複並保證覆蓋 ----
YOGA_MOVES=(
  "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
  "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
  "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
  "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
)

_BAG=()
_LAST=""
_refill_bag() {
  _BAG=("${YOGA_MOVES[@]}")
  # 洗牌（Fisher–Yates）
  for ((i=${#_BAG[@]}-1; i>0; i--)); do
    j=$((RANDOM % (i+1)))
    tmp=${_BAG[i]}; _BAG[i]=${_BAG[j]}; _BAG[j]=$tmp
  done
}

next_yoga_move() {
  if (( ${#_BAG[@]} == 0 )); then _refill_bag; fi
  local pick=${_BAG[0]}
  _BAG=(${_BAG[@]:1})
  # 避免立即重複
  if [[ "$pick" == "$_LAST" && ${#_BAG[@]} -gt 0 ]]; then
    local swap=${_BAG[0]}; _BAG[0]="$pick"; pick="$swap"
  fi
  _LAST="$pick"
  echo "$pick"
}

step_mix_diverse() {
  local MOVE; MOVE=$(next_yoga_move)
  local BASESPD; BASESPD=$(rand_float 1.35 1.55 2)
  local YOGASPD; YOGASPD=$(rand_float 0.55 0.70 2)
  local W; W=$(rand_float 0.60 0.80 2)
  local TD; TD=$(rand_float 0.70 0.90 2)
  local ADD_FLOAT=0; if (( RANDOM % 4 == 0 )); then ADD_FLOAT=1; fi
  anim_mix_diverse "$MOVE" "$BASESPD" "$W" "$YOGASPD" "$TD" "$ADD_FLOAT"
}

# ---- 情緒序列 ----
EMO_WARM=("serene,interested,content" "serene,content,grateful")
EMO_STILL=("serene,content,grateful" "grateful,content,serene")
EMO_AWE=("awe,hopeful,joyful" "surprised,awe,joyful")

echo "=== 🧘 Space Yoga Teacher — Nebula Stillness 開始 ==="

# 關閉隨機鏡位（若前端無此狀態則忽略）
## 已移除：關閉隨機鏡位（randomMode）

# 初始：黎明/夜色的靜定氛圍
## 已移除：鏡位 preset 設定
env_preset "dawn" || true
env_intensity 0.85 || true
env_background false || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.0 true
## 已移除：鏡位過渡

# 開場短句（承上啟下）
OPEN=$(shuf -e "${EMO_WARM[@]}" | head -n1 2>/dev/null || echo "serene,content,grateful")
say_zh_en "星雲靜定。細看一息一動。" "Nebula stillness—one breath, subtle move." 3.0 "$OPEN" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
emote 1.6 "$OPEN"
# 僅保留安靜的太空艙環境音，音量極低
sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03

# 主段：5 回合（每回合約 7–9 秒）
for i in {1..5}; do
  emote 1.2 "serene,content,grateful"
  step_mix_diverse
  case $((RANDOM % 3)) in
    0) sleep 4.6 ;;
    1) sleep 4.9 ;;
    *) sleep 5.2 ;;
  esac

  # 每 2 回合一個極短 cue
  if (( i % 2 == 1 )); then
    case $((i%4)) in
      1) say_zh_en "肩鬆、背長。" "Shoulders soft, back long." 2.4 "serene,interested,content";;
      3) say_zh_en "停一息，入內。" "Pause one breath—sink in." 2.4 "serene,content,grateful";;
    esac
  fi

  # 低機率驚喜但不打破沉靜
  if (( RANDOM % 5 == 0 )); then emote 1.0 "awe,hopeful,joyful"; fi

  # 不使用喧鬧的效果音，僅以微弱太空艙環境音維持空間感（間歇性）
  if (( RANDOM % 3 == 0 )); then sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03; fi
  case $((RANDOM % 3)) in
    0) sleep 1.0 ;;
    1) sleep 1.1 ;;
    *) sleep 1.2 ;;
  esac
done

# 中段輕推鏡（可選）
## 已移除：鏡位過渡
emote 1.4 "grateful,content,serene"

# 收束：臥躺 → 靜停
char_position 0.0 8.0 -30.0
anim_char "臥躺" 1.0 true
emote 2.0 "relieved,grateful,serene"
say_zh_en "收心歸靜，呼吸仍在。" "Return to quiet—the breath remains." 2.8 "grateful,content,serene" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1

echo "=== ✅ Nebula Stillness 結束（不播放 BGM） ==="
