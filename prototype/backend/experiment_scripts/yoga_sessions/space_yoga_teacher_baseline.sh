#!/bin/bash

# 《Space Yoga Teacher — Baseline Flow》
# 以本地 HTTP API 驅動的瑜伽老師底稿腳本（遵循人格規則：所有對外發聲均配對 emotion_trajectory）
# 執行：bash prototype/backend/experiment_scripts/space_yoga_teacher_baseline.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止（避免暫時無連線時整段中斷）

# --- 全域 TTS 設定（台語／漢字）---
# 依最新 TTS 能力：可指定 voice 與 speed（0.5–3.0）
# 預設以「漢字台語」溫柔口吻，慢速教學語氣。
TTS_INSTRUCTION="Taiwanese Hokkien, Han characters, natural, warm, friendly, accurate tones; avoid Mandarin accent"
TTS_VOICE_DEFAULT="sage"
TTS_SPEED_DEFAULT=0.5

# TTS 節流/降載參數
# 僅在每 N 次 say() 中執行 1 次 TTS（其餘僅表情與節奏）
TTS_EVERY_N=3
# 兩次 TTS 之間至少間隔（秒）
TTS_COOLDOWN=5
# 內部狀態（勿手動修改）
__SAY_COUNT=0
LAST_TTS_TS=0

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
  # 用法: say "內容" 時長(秒) "emotion1,emotion2,..." [voice] [speed]
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,interested,confident"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-0}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  # TTS 節流：依比例與冷卻時間決定是否實際發聲
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
  # 用法: sfx "/audio/effects/xxx.mp3" 0.2
  local URL="$1"; local VOL=${2:-0.2}
  echo ">> 音效: $URL @ $VOL"
  $CURL_POST "$BASE_URL/control/background-audio" \
    -H "Content-Type: application/json" \
    -d "{\"sfxUrl\": \"$URL\", \"volume\": $VOL}"
}

## 鏡位相關操作已移除

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
  # 用法: say_zh_en "中文" "English" 時長(秒) "emo1,emo2,emo3" [voice] [speed] [force]
  local ZH="$1"; local EN="$2"; local DUR=${3:-2.6}; local EMO=${4:-"neutral,interested,confident"}
  local VOICE=${5:-$TTS_VOICE_DEFAULT}; local SPEED=${6:-$TTS_SPEED_DEFAULT}; local FORCE=${7:-0}
  say "$ZH\n$EN" "$DUR" "$EMO" "$VOICE" "$SPEED" "$FORCE"
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

# --- 表情序列池（僅調整腳本，不改程式碼） ---
# 每個元素是一條以逗號分隔的 emotion_trajectory 標籤序列
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
  # 隨機挑一個瑜珈動作，並用隨機速度/權重與空體Action混合
  local MOVE; MOVE=$(rand_choice YOGA_MOVES[@])
  local BASESPD; BASESPD=$(rand_float "$BASE_SPEED_MIN" "$BASE_SPEED_MAX" 2)
  local YOGASPD; YOGASPD=$(rand_float "$YOGA_SPEED_MIN" "$YOGA_SPEED_MAX" 2)
  local W; W=$(rand_float "$YOGA_WEIGHT_MIN" "$YOGA_WEIGHT_MAX" 2)
  anim_mix "$MOVE" "$W" "$YOGASPD" "$TDUR" "$BLEND_MODE" "$BASESPD"
}

# --- 開始 ---
echo "=== 🧘 Space Yoga Teacher — Baseline Flow 開始 ==="

## 已移除：關閉隨機鏡位（randomMode）

########################################
# 初始：固定鏡位、縮小角色、穩定節奏
########################################
## 已移除：鏡位 preset 設定（維持現有鏡位）
env_preset "dawn" || true
# 確保瑜伽進行期間沒有背景音樂（若有則先關閉）
stop_bgm
# 調整頭部大小為 10（0.1–20.0 合法範圍內）
head_size 10.0
# 角色大小設定為 0.1（API 最小值）；搭配位置退後模擬更小視覺比例
char_scale 0.1
# 位置：往上 Y=8，往後 Z=-30（X=0）
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.0 true
sleep 1.5

# 開場短句（配情緒）+ 明確停頓（暖身：隨機挑選暖身序列）
OPEN_SEQ=$(rand_choice EMO_WARMUP[@])
# 開場改用「漢字台語」語句（同時保留英語節奏詞），強制一次 TTS
say "來——入氣，吐氣，慢慢來。Breathe in… out…" 3.0 "$OPEN_SEQ" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
# 開場加一段表情過渡，讓臉部更有存在感（同樣從暖身池隨機挑選）
OPEN_EMOTE=$(rand_choice EMO_WARMUP[@])
emote 2.2 "$OPEN_EMOTE"
sleep 1.0

########################################
# 瑜伽段落：每段 = 動作 4s +（交替）短句或表情 2.6–3.2s + 停頓 1.2s
########################################
for i in {1..8}; do
  # 位置左右切換
  X=$(rand_choice X_CHOICES[@])
  char_position "$X" 8.0 -30.0
  # micro 表情預熱（從專注池挑一條，短促）
  MICRO_SEQ=$(rand_choice EMO_FOCUS[@])
  emote 1.0 "$MICRO_SEQ"
  # 動畫混合（隨機瑜珈動作 + 速度/權重）
  step_mix_random
  # 動作播放時間（移除風聲）
  sleep 0.2
  sleep 4
  # 交替：奇數講話（雙語字幕），偶數只表情（更密集情緒）
  if (( i % 2 == 1 )); then
    case $((i%4)) in
      1)
        # 俏皮互動：從 PLAYFUL 池隨機
        PSEQ=$(rand_choice EMO_PLAYFUL[@])
        say_zh_en "山式，站高，膝蓋柔軟。" "Mountain — stand tall, soft knees." 2.8 "$PSEQ";;
      3)
        # 穩定聚焦：從 EFFORT/FOCUS 池隨機
        FSEQ=$(rand_choice EMO_EFFORT[@])
        say_zh_en "平衡放鬆，眼睛看前方。" "Balance soft—eyes forward." 2.8 "$FSEQ";;
      *)
        # 核心力量：從 EFFORT 池隨機
        ESEQ=$(rand_choice EMO_EFFORT[@])
        say_zh_en "穩住核心，肩膀鬆開。" "Engage core—relax shoulders." 2.8 "$ESEQ";;
    esac
  else
    case $((i%4)) in
      2) # 穩定專注：從 FOCUS 池隨機
         F2SEQ=$(rand_choice EMO_FOCUS[@]); emote 3.0 "$F2SEQ";;
      0) # 放鬆愉悅：從 RELAX 池隨機
         RSEQ=$(rand_choice EMO_RELAX[@]); emote 3.2 "$RSEQ";;
    esac
  fi
  # 偶爾穿插驚喜/敬畏，提升節奏變化（約每 6 次機率觸發一次）
  if (( RANDOM % 6 == 0 )); then
    AWE_SEQ=$(rand_choice EMO_AWE[@])
    emote 1.4 "$AWE_SEQ"
  fi
  # 節拍提示 + 停頓拉長一點
  # 移除綜藝音效（保持安靜的節奏）
  sleep 1.2
done

# 緩和與收尾（保持相同鏡位與比例）
char_position 0.0 8.0 -30.0
step_mix_random
# 移除風聲音效（太空環境不應有風）
sleep 4
END_SEQ=$(rand_choice EMO_RELAX[@])
say_zh_en "緩和：慢慢吸氣，吐氣更長。" "Cooldown—inhale slow, exhale longer." 3.0 "$END_SEQ"
sleep 1
TAIL_SEQ=$(rand_choice EMO_PLAYFUL[@])
emote 3.0 "$TAIL_SEQ"
sleep 0.6
say_zh_en "做得很讚！下次再一起流動。" "Great job—see you next flow!" 2.6 "happy,content,proud" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
sleep 0.5

# 收尾處理（不切鏡位）：瑜伽結束後開始播放背景音樂
bgm "/audio/BGM/space_live_country_theme1.mp3" 0.25
echo "=== ✅ Space Yoga Teacher — Baseline Flow 結束 ==="
