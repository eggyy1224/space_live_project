#!/bin/bash

# 《Space Yoga Teacher — Baseline Flow》
# 以本地 HTTP API 驅動的瑜伽老師底稿腳本（遵循人格規則：所有對外發聲均配對 emotion_trajectory）
# 執行：bash prototype/backend/experiment_scripts/space_yoga_teacher_baseline.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止（避免暫時無連線時整段中斷）

# --- 小工具 ---
rand_float() {
  # 用法: rand_float MIN MAX DECIMALS
  local MIN=$1; local MAX=$2; local DEC=${3:-2}
  awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'
}

rand_choice() {
  # 用法: rand_choice arr[@] -> 回傳隨機元素
  local arr=("${!1}"); local n=${#arr[@]}
  echo "${arr[$((RANDOM % n))]}"
}

say() {
  # 用法: say "內容" 時長(秒) "emotion1,emotion2,..."
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,interested,confident"}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  # 發送文字（TTS/聊天）
  $CURL_POST "$BASE_URL/control/send-message" \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$CONTENT\"}" >/dev/null &
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
  # 用法: emote 時長(秒) "emotion1,emotion2,emotion3"
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
  # 用法: bgm "/audio/BGM/xxx.mp3" 0.4
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
  # 用法: sfx "/audio/effects/xxx.mp3" 0.2 false
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

# 動畫混合（建議預設 additive，務必包含「空體Action」作為基底）
anim_mix() {
  # 用法: anim_mix "瑜珈動作1" [otherWeight] [otherSpeed] [transitionDuration] [blendMode] [baseSpeed]
  # 規則：空體Action 速度快(預設1.8)，瑜伽動作速度慢(預設0.6)，權重可到 1.0（總和>1允許，後端僅警告）
  local OTHER="$1"; local W=${2:-1.0}; local SPEED=${3:-0.6}; local TD=${4:-0.6}; local BLEND=${5:-"additive"}; local BASESPD=${6:-1.8}
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

# 中英雙語字幕
say_zh_en() {
  # 用法: say_zh_en "中文" "English" 時長(秒) "emo1,emo2,emo3"
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"neutral,interested,confident"}
  say "$ZH\n$EN" "$DUR" "$EMO"
}

# 可選瑜珈動作池（由空體Action作為基底混合）
YOGA_MOVES=(
  "瑜珈動作1" "瑜珈動作2" "瑜珈動作3" "瑜珈動作4" "瑜珈動作5"
  "瑜珈動作6" "瑜珈動作7" "瑜珈動作8" "瑜珈動作9" "瑜珈動作10"
  "瑜珈動作11" "瑜珈動作12" "瑜珈動作13" "瑜珈動作14" "瑜珈動作15"
  "瑜珈動作16" "瑜珈動作17" "瑜珈動作18" "瑜珈動作19" "瑜珈動作20"
)

# 左右位移備選（固定 Y、Z）
X_CHOICES=(-1.6 -1.4 -1.2 0 1.2 1.4 1.6)

# 全域參數（可調整）
BLEND_MODE="additive"
TDUR=0.6
BASE_SPEED_MIN=1.8
BASE_SPEED_MAX=2.0
YOGA_SPEED_MIN=0.5
YOGA_SPEED_MAX=0.7
YOGA_WEIGHT_MIN=0.9
YOGA_WEIGHT_MAX=1.0

step_mix_random() {
  # 隨機挑一個瑜珈動作，並用隨機速度/權重與空體Action混合
  local MOVE; MOVE=$(rand_choice YOGA_MOVES[@])
  local BASESPD; BASESPD=$(rand_float "$BASE_SPEED_MIN" "$BASE_SPEED_MAX" 2)
  local YOGASPD; YOGASPD=$(rand_float "$YOGA_SPEED_MIN" "$YOGA_SPEED_MAX" 2)
  local W; W=$(rand_float "$YOGA_WEIGHT_MIN" "$YOGA_WEIGHT_MAX" 2)
  anim_mix "$MOVE" "$W" "$YOGASPD" "$TDUR" "$BLEND_MODE" "$BASESPD"
}

# --- 開始 ---
echo "=== 🧘 Space Yoga Teacher — Baseline Flow 開始 ==="

# 關閉隨機鏡位，避免干擾（若無此功能可忽略）
$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true

########################################
# 初始：固定鏡位、縮小角色、穩定節奏
########################################
# 固定使用 head_close_up 鏡位，不再切換
cam_preset "head_close_up" 1.2
env_preset "dawn" || true
bgm "/audio/BGM/space_live_country_theme1.mp3" 0.25
head_size 1.0
# 角色大小設定為 0.1（API 最小值）；搭配位置退後模擬更小視覺比例
char_scale 0.1
# 位置：往上 Y=8，往後 Z=-30（X=0）
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.0 true
sleep 1.5

# 開場短句（配情緒）+ 明確停頓
say "Lai — tsiah--khí lâi. Breathe in… out…" 3.0 "neutral,interested,content"
sleep 1.0

########################################
# 瑜伽段落：每段 = 動作 4s +（交替）短句或表情 2.6–3.2s + 停頓 1.2s
########################################
for i in {1..8}; do
  # 位置左右切換
  X=$(rand_choice X_CHOICES[@])
  char_position "$X" 8.0 -30.0
  # 動畫混合（隨機瑜珈動作 + 速度/權重）
  step_mix_random
  # 進段音效 + 動作播放時間
  sleep 0.2; sfx "/audio/effects/winds_blowing.mp3" 0.06 false
  sleep 4
  # 交替：奇數講話（雙語字幕），偶數只表情（更密集情緒）
  if (( i % 2 == 1 )); then
    case $((i%4)) in
      1)
        say_zh_en "山式，站高，膝蓋柔軟。" "Mountain — stand tall, soft knees." 2.8 "interested,playful,confident";;
      3)
        say_zh_en "平衡放鬆，眼睛看前方。" "Balance soft—eyes forward." 2.8 "neutral,interested,confident";;
      *)
        say_zh_en "穩住核心，肩膀鬆開。" "Engage core—relax shoulders." 2.8 "neutral,interested,confident";;
    esac
  else
    case $((i%4)) in
      2) emote 3.0 "neutral,focused,confident";;
      0) emote 3.2 "peaceful,content,joyful";;
    esac
  fi
  # 節拍提示 + 停頓拉長一點
  sfx "/audio/effects/taiwan_variety_sfx_01.mp3" 0.16 false
  sleep 1.2
done

# 緩和與收尾（保持相同鏡位與比例）
char_position 0.0 8.0 -30.0
step_mix_random
sleep 0.2; sfx "/audio/effects/winds_blowing.mp3" 0.06 false
sleep 4
say_zh_en "緩和：慢慢吸氣，吐氣更長。" "Cooldown—inhale slow, exhale longer." 3.0 "neutral,peaceful,content"
sleep 1
emote 3.0 "joyful,content,proud"
sleep 0.6
say_zh_en "做得很讚！下次再一起流動。" "Great job—see you next flow!" 2.6 "happy,content,confident"
sleep 0.5

# 收尾處理（不切鏡位）
stop_bgm
echo "=== ✅ Space Yoga Teacher — Baseline Flow 結束 ==="
