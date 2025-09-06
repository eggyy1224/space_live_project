#!/bin/bash

# 《Space Yoga Teacher — Baseline Flow：Scene 3》
# 承接前兩幕，第三幕以「穩定節奏 × 更清晰口令」作為收束；
# 規則維持：瑜伽進行期間不放 BGM，結束後才播放同一首背景音樂。
# 執行：bash prototype/backend/experiment_scripts/yoga_sessions/space_yoga_teacher_baseline_scene3.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止（避免暫時無連線時整段中斷）

# --- 全域 TTS 設定（台語／漢字）---
TTS_INSTRUCTION="Taiwanese Hokkien, Han characters, natural, warm, friendly, accurate tones; avoid Mandarin accent"
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.5

# TTS 節流/降載參數（承接前兩幕設定）
TTS_EVERY_N=3
TTS_COOLDOWN=5
__SAY_COUNT=0
LAST_TTS_TS=0

# --- 小工具 ---
rand_float() {
  local MIN=$1; local MAX=$2; local DEC=${3:-2}
  awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'
}

rand_choice() {
  local arr=("${!1}"); local n=${#arr[@]}
  echo "${arr[$((RANDOM % n))]}"
}

say() {
  # 用法: say "內容" 時長(秒) "emotion1,emotion2,..." [voice] [speed] [force]
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,interested,confident"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-0}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  __SAY_COUNT=$((__SAY_COUNT + 1))
  local DO_TTS=0
  local NOW_TS=$(date +%s)
  if (( FORCE == 1 )); then
    DO_TTS=1
  else
    if (( (__SAY_COUNT % TTS_EVERY_N) == 1 )); then
      if (( NOW_TS - LAST_TTS_TS >= TTS_COOLDOWN )); then
        DO_TTS=1
      fi
    fi
  fi
  if (( DO_TTS == 1 )); then
    echo "   >> [TTS] voice=$VOICE speed=$SPEED"
    $CURL_POST "$BASE_URL/control/send-message" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null
    LAST_TTS_TS=$NOW_TS
  else
    echo "   >> [SKIP TTS]（降載：僅表情過渡）"
  fi
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
  sleep $(echo "$DURATION * 0.85" | bc)
}

emote() {
  local DURATION=${1:-3.0}; local EMOS=${2:-"neutral,interested,content"}
  local IFS=','; read -ra KFS <<< "$EMOS"; unset IFS
  local KF_JSON="[]"
  if (( ${#KFS[@]} == 1 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"
  elif (( ${#KFS[@]} == 2 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"
  else
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"
  fi
  echo ">> 表情: $EMOS ($DURATION s)"
  $CURL_POST "$BASE_URL/control/emotion-trajectory" \
    -H "Content-Type: application/json" \
    -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.6" | bc)
}

bgm() {
  local URL="$1"; local VOL=${2:-0.4}
  echo ">> BGM: $URL @ $VOL"
  $CURL_POST "$BASE_URL/control/background-audio" \
    -H "Content-Type: application/json" \
    -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null
}

stop_bgm() {
  echo ">> 停止 BGM"
  $CURL_POST "$BASE_URL/control/background-audio" \
    -H "Content-Type: application/json" \
    -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null
}

sfx() {
  local URL="$1"; local VOL=${2:-0.2}; local INT=${3:-false}
  echo ">> 音效: $URL @ $VOL (interrupt=$INT)"
  $CURL_POST "$BASE_URL/control/play-audio" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$URL\", \"volume\": $VOL, \"interrupt\": $INT}" >/dev/null
}

cam_preset() {
  local NAME="$1"; local D=${2:-2.0}
  echo ">> 鏡位 preset: $NAME ($D s)"
  $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null
  sleep $D
}

cam_transition() {
  local P=${1:-0}; local Y=${2:-0}; local R=${3:-0}; local F=${4:-55}; local D=${5:-2.0}
  echo ">> 鏡位過渡: pitch=$P yaw=$Y roll=$R fov=$F ($D s)"
  $CURL_POST "$BASE_URL/control/camera/transition" \
    -H "Content-Type: application/json" \
    -d "{\"pitch\": $P, \"yaw\": $Y, \"roll\": $R, \"fov\": $F, \"duration\": $D}" >/dev/null
  sleep $D
}

anim_char() {
  local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}
  echo ">> 主角動畫: $ANIM x$SPEED loop=$LOOP"
  $CURL_POST "$BASE_URL/control/character/animation" \
    -H "Content-Type: application/json" \
    -d "{\"animation\": \"$ANIM\", \"speed\": $SPEED, \"loop\": $LOOP}" >/dev/null
}

anim_mix() {
  local OTHER="$1"; local W=${2:-1.0}; local SPEED=${3:-0.6}; local TD=${4:-0.6}; local BLEND=${5:-"additive"}; local BASESPD=${6:-1.85}
  echo ">> 動畫混合: 空體Action($BASESPD) + $OTHER(w=$W spd=$SPEED) blend=$BLEND td=$TD"
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
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" >/dev/null
}

anim_body() {
  local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}
  echo ">> 身體/舞者動畫: $ANIM x$SPEED loop=$LOOP"
  $CURL_POST "$BASE_URL/control/body-animation" \
    -H "Content-Type: application/json" \
    -d "{\"state\": \"play\", \"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null
}

env_preset() {
  local PRE="$1"
  echo ">> 環境: $PRE"
  $CURL_POST "$BASE_URL/control/environment/preset" \
    -H "Content-Type: application/json" \
    -d "{\"preset\": \"$PRE\"}" >/dev/null
}

head_size() { local S=${1:-1.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-1.0}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-0.0}; local Z=${3:-0.0}; echo ">> 角色位置: [$X,$Y,$Z]"; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

say_zh_en() {
  # 用法: say_zh_en "中文" "English" 時長(秒) "emo1,emo2,emo3" [voice] [speed] [force]
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"neutral,interested,confident"}
  local VOICE=${5:-$TTS_VOICE_DEFAULT}; local SPEED=${6:-$TTS_SPEED_DEFAULT}; local FORCE=${7:-0}
  say "$ZH\n$EN" "$DUR" "$EMO" "$VOICE" "$SPEED" "$FORCE"
}

# 瑜珈動作池（與前兩幕一致）
YOGA_MOVES=(
  "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
  "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
  "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
  "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
)

# Scene 3 輕微收束：位置變化更集中
X_CHOICES=(-1.2 -1.0 -0.8 0 0.8 1.0 1.2)

# 節奏（Scene 3：收束但不鬆散）
BLEND_MODE="additive"
TDUR=0.6
BASE_SPEED_MIN=1.85
BASE_SPEED_MAX=2.05
YOGA_SPEED_MIN=0.65
YOGA_SPEED_MAX=0.85
YOGA_WEIGHT_MIN=0.9
YOGA_WEIGHT_MAX=1.0

# 表情序列池
EMO_WARMUP=(
  "serene,interested,content"
  "listening,interested,serene"
  "serene,grateful,content"
)
EMO_PLAYFUL=(
  "playful,amused,joyful"
  "smug,playful,joyful"
  "playful,joyful,content"
)
EMO_EFFORT=(
  "determined,proud,triumphant"
  "interested,determined,proud"
  "determined,proud,joyful"
)
EMO_FOCUS=(
  "neutral,determined,proud"
  "listening,thinking,determined"
  "interested,determined,proud"
)
EMO_RELAX=(
  "serene,content,joyful"
  "grateful,content,serene"
  "relieved,grateful,serene"
)
EMO_AWE=(
  "awe,hopeful,joyful"
  "surprised,awe,joyful"
)

step_mix_random() {
  local MOVE; MOVE=$(rand_choice YOGA_MOVES[@])
  local BASESPD; BASESPD=$(rand_float "$BASE_SPEED_MIN" "$BASE_SPEED_MAX" 2)
  local YOGASPD; YOGASPD=$(rand_float "$YOGA_SPEED_MIN" "$YOGA_SPEED_MAX" 2)
  local W; W=$(rand_float "$YOGA_WEIGHT_MIN" "$YOGA_WEIGHT_MAX" 2)
  anim_mix "$MOVE" "$W" "$YOGASPD" "$TDUR" "$BLEND_MODE" "$BASESPD"
}

echo "=== 🧘 Space Yoga Teacher — Baseline Flow：Scene 3 開始 ==="

# 關閉隨機鏡位（若前端無此狀態則忽略）
$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true

########################################
# 初始：維持構圖與音場規則；短促進場
########################################
cam_preset "head_close_up" 1.0
env_preset "dawn" || true
stop_bgm
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.0 true
sleep 1.0

# 開場短句（承先啟後）
OPEN_SEQ=$(rand_choice EMO_WARMUP[@])
say "第三幕——穩住呼吸，慢慢收束。Breathe steady—we gather and seal." 3.0 "$OPEN_SEQ" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
emote 1.8 "$OPEN_SEQ"
sleep 0.8

########################################
# 瑜伽段落（Scene 3）：每段 = 動作 4.0–4.4s +（交替）短句/表情 2.6–3.2s + 停頓 0.9–1.1s
########################################
for i in {1..6}; do
  X=$(rand_choice X_CHOICES[@])
  char_position "$X" 8.0 -30.0
  MICRO_SEQ=$(rand_choice EMO_FOCUS[@])
  emote 0.9 "$MICRO_SEQ"
  step_mix_random
  sleep 0.2; sfx "/audio/effects/winds_blowing.mp3" 0.06 false

  # 動作持續時間略帶隨機（4.0/4.2/4.4）以避免過度機械
  case $((RANDOM % 3)) in
    0) sleep 4.0 ;;
    1) sleep 4.2 ;;
    *) sleep 4.4 ;;
  esac

  if (( i % 2 == 1 )); then
    case $((i%6)) in
      1)
        PSEQ=$(rand_choice EMO_PLAYFUL[@])
        say_zh_en "下犬式，背延伸，腳跟沉。" "Down Dog—lengthen back, heels heavy." 2.8 "$PSEQ";;
      3)
        FSEQ=$(rand_choice EMO_EFFORT[@])
        say_zh_en "船式，核心收緊，肩放鬆。" "Boat—engage core, soften shoulders." 2.8 "$FSEQ";;
      5)
        ESEQ=$(rand_choice EMO_EFFORT[@])
        say_zh_en "椅子式，大腿用力，胸口開。" "Chair—power legs, open chest." 2.8 "$ESEQ";;
      *)
        F2=$(rand_choice EMO_FOCUS[@])
        say_zh_en "穩住骨盆，呼氣更長。" "Stabilize pelvis—exhale longer." 2.6 "$F2";;
    esac
  else
    case $((i%4)) in
      2)
        F2SEQ=$(rand_choice EMO_FOCUS[@]); emote 3.0 "$F2SEQ";;
      0)
        RSEQ=$(rand_choice EMO_RELAX[@]); emote 3.2 "$RSEQ";;
    esac
  fi

  # 第三幕提高驚喜頻率（約 1/4）
  if (( RANDOM % 4 == 0 )); then
    AWE_SEQ=$(rand_choice EMO_AWE[@])
    emote 1.2 "$AWE_SEQ"
  fi

  sfx "/audio/effects/taiwan_variety_sfx_01.mp3" 0.16 false
  case $((RANDOM % 3)) in
    0) sleep 0.9 ;;
    1) sleep 1.0 ;;
    *) sleep 1.1 ;;
  esac
done

# 緩和與收尾（維持鏡位與比例）
char_position 0.0 8.0 -30.0
step_mix_random
sleep 0.2; sfx "/audio/effects/winds_blowing.mp3" 0.06 false
sleep 4.2
END_SEQ=$(rand_choice EMO_RELAX[@])
say_zh_en "仰躺休息：全身沉，心更輕。" "Savasana—let body sink, heart lighter." 3.0 "$END_SEQ"
sleep 1.0
TAIL_SEQ=$(rand_choice EMO_PLAYFUL[@])
emote 3.0 "$TAIL_SEQ"
sleep 0.6
say_zh_en "第三幕完成——感謝流動。下次見。" "Scene three complete—thank you for flowing." 2.6 "happy,content,proud" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
sleep 0.5

# 瑜伽結束後才播放相同 BGM（不更換曲目）
bgm "/audio/BGM/space_live_country_theme1.mp3" 0.25
echo "=== ✅ Space Yoga Teacher — Baseline Flow：Scene 3 結束 ==="

