#!/bin/bash

# 《Space Yoga Teacher — Pulse Flow》
# 以「脈動 × 定格」結束整輪：變焦、縮放、定格與再啟；語句更短，表情更豐富。
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene5.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定（自然樣態）---
TTS_INSTRUCTION="Taiwanese Hokkien, Han characters, natural, warm, friendly, accurate tones; avoid Mandarin accent"
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.5
TTS_EVERY_N=4
TTS_COOLDOWN=6
__SAY_COUNT=0
LAST_TTS_TS=0

rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

say() {
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,interested,confident"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-0}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  __SAY_COUNT=$((__SAY_COUNT + 1)); local DO_TTS=0; local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then DO_TTS=1; else if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )) && (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then DO_TTS=1; fi; fi
  if (( DO_TTS == 1 )); then
    $CURL_POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" \
      -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$TTS_VOICE_DEFAULT\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  fi
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]";
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]";
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.85" | bc)
}

emote() {
  local DURATION=${1:-2.0}; local EMOS=${2:-"playful,amused,joyful"}
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

cam_preset() { local NAME="$1"; local D=${2:-1.2}; $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null; sleep $D; }
cam_transition() { local P=${1:-0}; local Y=${2:-0}; local R=${3:-0}; local F=${4:-55}; local D=${5:-1.0}; $CURL_POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d "{\"pitch\": $P, \"yaw\": $Y, \"roll\": $R, \"fov\": $F, \"duration\": $D}" >/dev/null; sleep $D; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
anim_mix() {
  local OTHER="$1"; local W=${2:-0.95}; local SPEED=${3:-0.7}; local TD=${4:-0.5}; local BLEND=${5:-"additive"}; local BASESPD=${6:-1.9}
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name": "空體Action", "weight": 1.0, "loop": true, "speed": $BASESPD},
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
env_intensity() { local I=${1:-1.2}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

# 中英併行語句（保持一致風格）
say_zh_en() {
  # 用法: say_zh_en "中文" "English" 時長(秒) "emo1,emo2,emo3" [voice] [speed] [force]
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"neutral,interested,confident"}
  local VOICE=${5:-$TTS_VOICE_DEFAULT}; local SPEED=${6:-$TTS_SPEED_DEFAULT}; local FORCE=${7:-0}
  say "$ZH\n$EN" "$DUR" "$EMO" "$VOICE" "$SPEED" "$FORCE"
}

YOGA_MOVES=("瑜珈動作2" "瑜珈動作4" "瑜珈動作6" "瑜珈動作8" "瑜珈動作10" "瑜珈動作11" "瑜珈動作14" "瑜珈動作17")
EMO_IMPACT=("awe,triumphant,joyful" "surprised,awe,joyful" "determined,proud,triumphant")
EMO_GROOVE=("playful,amused,joyful" "smug,playful,joyful" "interested,playful,joyful")
EMO_SINK=("relieved,grateful,serene" "serene,content,joyful" "grateful,content,serene")

echo "=== 🧘 Space Yoga Teacher — Pulse Flow 開始 ==="

$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true
cam_preset "head_close_up" 0.8
env_preset "studio" || true
env_intensity 1.3 || true
env_background false || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.0 true

# 開場：單一穩定推鏡（取消連續變焦）
cam_transition -2 0 0 55 1.0
say_zh_en "這段，照脈動收束。" "This segment—ride the pulse to close." 2.8 "interested,hopeful,joyful" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
emote 1.4 "playful,amused,joyful"

# 主段：6 回合 — 定格(Freeze) × 動作 × 再啟
for i in {1..6}; do
  MOVE=$(rand_choice YOGA_MOVES[@])
  anim_mix "$MOVE" 0.95 0.72 0.5 "additive" 1.9
  # 快速縮放脈動（移除音效）
  char_scale 0.12; sleep 0.08; char_scale 0.1
  # 微位移（取消每回合變焦與左右搖鏡）
  DX=$(rand_float -1.0 1.0 2); char_position "$DX" 8.0 -30.0
  # 在第三回合做一次有意義的推鏡以強化段落感
  if (( i == 3 )); then cam_transition -3 0 0 52 1.0; fi
  # 表情 groove / impact 交替
  if (( i % 2 == 1 )); then EM=$(rand_choice EMO_GROOVE[@]); else EM=$(rand_choice EMO_IMPACT[@]); fi
  emote 1.2 "$EM"
  # cue（更完整的引導語）
  case $((i%6)) in
    1) say_zh_en "旋轉，目線跟行，脊椎照直。" "Spiral—eyes follow, keep the spine long." 2.6 "interested,playful,joyful";;
    2) say_zh_en "停一下，呼吸猶在。" "Freeze just a beat—breath continues." 2.4 "serene,content,serene";;
    3) say_zh_en "腳根發力，核心撐住。" "Press through heels—hold from the center." 2.6 "determined,proud,triumphant";;
    4) say_zh_en "肩膀落下，面容鬆開。" "Drop the shoulders—soften the face." 2.6 "relieved,grateful,serene";;
    5) say_zh_en "手臂畫弧，側肋打開。" "Arc the arms—open the side ribs." 2.6 "hopeful,joyful,awe";;
    0) say_zh_en "回到中線，穩穩收回。" "Return to midline—gather steady." 2.6 "serene,content,serene";;
  esac
  # Freeze（定格）—移除音效，保留停頓
  sleep 0.25
done

# 緩落：臥躺 → 漂浮微起
anim_char "臥躺" 1.0 true; emote 2.0 "relieved,grateful,serene"; sleep 1.0
anim_char "漂浮" 0.9 true; emote 1.6 "serene,hopeful,joyful"
say_zh_en "感謝共下流動，下擺見。" "Thank you for flowing—see you next time." 2.8 "grateful,content,serene" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1

# 收束（不播放 BGM）
echo "=== ✅ Pulse Flow 結束 ==="
