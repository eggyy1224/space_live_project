#!/bin/bash

# 《Space Yoga Teacher — Spicy Nebula Comedy》
# 參考 docs/scrip_prototype/space_yoga.md（太空辣妹瑜伽教室）
# 風格：輕鬆搞笑 × 失重亂飄 × 即興口白（保持安靜氛圍，避免吵雜 SFX）
# 規則：瑜伽段不放 BGM；背景僅少量太空艙 ambience；角色可說短句（台語/漢字 + EN）。
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene7.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"

# --- TTS 設定（台語／漢字）---
TTS_INSTRUCTION="Taiwanese Hokkien, Han characters, natural, lively, playful; accurate tones; avoid Mandarin accent"
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.58
TTS_EVERY_N=3
TTS_COOLDOWN=5
__SAY_COUNT=0
LAST_TTS_TS=0

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_int()   { local MIN=$1; local MAX=$2; awk -v min="$MIN" -v max="$MAX" 'BEGIN{srand(); printf("%d\n", int(min+rand()*(max-min+1)))}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# --- 爆快基底參數（空體Action）---
# 再上兩檔：極快段（爆發）與較慢段（仍偏快）
BASE_FAST_MIN=3.20
BASE_FAST_MAX=3.80
BASE_SLOW_MIN=2.40
BASE_SLOW_MAX=2.80

say() {
  local CONTENT="$1"; local DURATION=${2:-2.6}; local EMOS=${3:-"playful,amused,joyful"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-0}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  __SAY_COUNT=$((__SAY_COUNT + 1)); local DO_TTS=0; local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then DO_TTS=1; else if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )) && (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then DO_TTS=1; fi; fi
  if (( DO_TTS == 1 )); then
    $CURL_POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" \
      -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  fi
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"; 
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.75" | bc)
}

emote() {
  local DURATION=${1:-1.6}; local EMOS=${2:-"playful,amused,joyful"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"; 
  else KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.5" | bc)
}

bgm() { local URL="$1"; local VOL=${2:-0.2}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
sfx() { local URL="$1"; local VOL=${2:-0.03}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$URL\", \"volume\": $VOL}" >/dev/null; }

cam_preset() { local NAME="$1"; local D=${2:-1.0}; $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null; sleep $D; }
cam_transition() { local P=${1:-0}; local Y=${2:-0}; local R=${3:-0}; local F=${4:-56}; local D=${5:-1.0}; $CURL_POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d "{\"pitch\": $P, \"yaw\": $Y, \"roll\": $R, \"fov\": $F, \"duration\": $D}" >/dev/null; sleep $D; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_multi() {
  # 多動作混合（一次混合 3–4 個瑜伽動作），所有 weight=1.0
  # 用法：anim_mix_multi base_spd yoga_spd td float_spd count
  local BASESPD=${1:-3.2}; local YOGA_SPD=${2:-1.0}; local TD=${3:-0.5}; local FLOAT_SPD=${4:-1.0}; local COUNT=${5:-3}
  # 構建動畫項
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
env_intensity() { local I=${1:-0.9}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

say_zh_en() { local ZH="$1"; local EN="$2"; local DUR=${3:-2.4}; local EMO=${4:-"playful,amused,joyful"}; say "$ZH\n$EN" "$DUR" "$EMO" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 0; }

# 20 動作 + 袋子抽樣，避免重複並保證覆蓋
YOGA_MOVES=(
  "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
  "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
  "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
  "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
)
_BAG=(); _LAST=""
_refill_bag() { _BAG=("${YOGA_MOVES[@]}"); for ((i=${#_BAG[@]}-1;i>0;i--)); do j=$((RANDOM%(i+1))); tmp=${_BAG[i]}; _BAG[i]=${_BAG[j]}; _BAG[j]=$tmp; done; }
next_yoga_move() { (( ${#_BAG[@]}==0 )) && _refill_bag; local pick=${_BAG[0]}; _BAG=(${_BAG[@]:1}); if [[ "$pick" == "$_LAST" && ${#_BAG[@]}>0 ]]; then local swap=${_BAG[0]}; _BAG[0]="$pick"; pick="$swap"; fi; _LAST="$pick"; echo "$pick"; }

# 台詞池（取自參考稿，做短句化）
LINES_INTRO=(
  "欸欸等一下，我怎麼飄過頭了啦～！\nOops—overshot orbit!"
  "歡迎來到太空辣妹瑜伽教室～\nWelcome to Spicy Nebula Yoga!"
)
LINES_P1=(
  "宇宙樹，站穩就浮起。\nCosmic Tree—root and rise."
  "飛天拜日浮空式，新流派登場！\nFlying Sun Salute—new cosmic style!"
  "彈跳旋轉式，冥想中不要撞艙壁～\nBounce and spin—watch the bulkhead!"
)
LINES_P2=(
  "無脊椎下犬式，地球做不得。\nBoneless Down Dog—not for Earth."
  "太空勇士式，逆風也要美。\nSpace Warrior—fierce and fabulous."
  "螺旋章魚式，我根本水管啦～\nSpiral Octopus—I’m a space hose!"
)
LINES_GAG=(
  "心靈脫軌式，練完忘記煩惱。\nMind-off-track—forget your troubles."
  "如果撞到艙壁，代表進入更高次元。\nBump the wall? Higher dimension unlocked."
)
LINES_OUTRO=(
  "深冥想，靈魂回艙體…欸人怎麼飄走。\nDeep meditation—return to vessel… oh no, drifting!"
  "下次見，記得補給控肉飯～\nSee you—bring braised pork rice!"
)

echo "=== 🧘 Space Yoga Teacher — Spicy Nebula Comedy 開始 ==="

# 關閉隨機鏡位
$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true

# 初始：夜景 + 輕 ambience
cam_preset "head_close_up" 0.8
env_preset "night" || true
env_intensity 0.9 || true
env_background false || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.2 -33.0
anim_char "空體Action" 3.2 true
cam_transition -6 0 0 58 1.0
sfx "/audio/effects/spaceship_ambience_02.mp3" 0.03

# 開場台詞
say "$(rand_choice LINES_INTRO[@])" 2.6 "playful,amused,joyful" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
emote 1.4 "playful,joyful,content"

# Part 1：飛來飛去找不到方向（3 段）—固定鏡位，不再頻繁搖鏡
for i in {1..3}; do
  # 僅調整角色微位移，鏡頭維持穩定
  char_position $(rand_float -1.4 1.4 1) 8.$(rand_int 0 4) -33.$(rand_int 0 4)
  # 動作混合（速度反差：奇數爆發、偶數慢動）
  if (( i % 2 == 1 )); then
    # 爆發段：更快的 base 與瑜伽速度、較短過渡、漂浮加速
    anim_mix_multi \
      $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) \
      $(rand_float 1.05 1.30 2) \
      $(rand_float 0.35 0.55 2) \
      $(rand_float 0.95 1.15 2) \
      $(rand_int 3 4)
  else
    # 慢動段：較慢的 base 與瑜伽速度、較長過渡、漂浮放慢
    anim_mix_multi \
      $(rand_float $BASE_SLOW_MIN $BASE_SLOW_MAX 2) \
      $(rand_float 0.55 0.70 2) \
      $(rand_float 0.75 0.95 2) \
      $(rand_float 0.60 0.80 2) \
      $(rand_int 3 4)
  fi
  # 台詞穿插
  say "$(rand_choice LINES_P1[@])" 2.4 "playful,amused,joyful"
  if (( RANDOM % 2 == 0 )); then emote 1.2 "smug,playful,joyful"; fi
  sleep 1.0
done

# Part 2：進階凹折（3 段）—仍固定鏡位
for i in {1..3}; do
  char_position $(rand_float -1.0 1.0 1) 8.$(rand_int 1 5) -32.$(rand_int 0 4)
  if (( i % 2 == 1 )); then
    anim_mix_multi \
      $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) \
      $(rand_float 1.10 1.35 2) \
      $(rand_float 0.35 0.55 2) \
      $(rand_float 1.00 1.18 2) \
      $(rand_int 3 4)
  else
    anim_mix_multi \
      $(rand_float $BASE_SLOW_MIN $BASE_SLOW_MAX 2) \
      $(rand_float 0.55 0.70 2) \
      $(rand_float 0.80 0.95 2) \
      $(rand_float 0.60 0.78 2) \
      $(rand_int 3 4)
  fi
  say "$(rand_choice LINES_P2[@])" 2.6 "playful,amused,joyful"
  if (( RANDOM % 3 == 0 )); then say "$(rand_choice LINES_GAG[@])" 2.4 "amused,playful,joyful"; fi
  sleep 1.0
done

# Part 3：互動爆笑（2 段簡化即興）—固定鏡位
for i in {1..2}; do
  char_position $(rand_float -1.6 1.6 1) 8.$(rand_int 0 5) -33.$(rand_int 0 5)
  if (( i % 2 == 1 )); then
    anim_mix_multi \
      $(rand_float $BASE_FAST_MIN $BASE_FAST_MAX 2) \
      $(rand_float 1.05 1.28 2) \
      0.5 \
      $(rand_float 0.95 1.12 2) \
      $(rand_int 3 4)
  else
    anim_mix_multi \
      $(rand_float $BASE_SLOW_MIN $BASE_SLOW_MAX 2) \
      $(rand_float 0.55 0.70 2) \
      0.9 \
      $(rand_float 0.60 0.80 2) \
      $(rand_int 3 4)
  fi
  say_zh_en "觀眾點一招，我隨便示範！" "Your move—I'll improvise!" 2.4 "playful,amused,joyful"
  if (( RANDOM % 2 == 0 )); then say_zh_en "躺平任意式，專家最會。" "Freestyle flop—expert mode." 2.4 "smug,playful,joyful"; fi
  sleep 1.0
done

# 收尾：回艙體（不放 BGM）
cam_transition -8 0 0 56 1.0
char_position 0.0 8.0 -33.0
emote 1.6 "grateful,content,serene"
say "$(rand_choice LINES_OUTRO[@])" 2.8 "playful,grateful,content" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1

echo "=== ✅ Spicy Nebula Comedy 結束（安靜氛圍） ==="
