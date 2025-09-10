#!/bin/bash

# 《Space Yoga Teacher — Aurora Drift Flow》
# 主題：極光漂移（極慢長尾 × 環境潮汐）。
# 目標：全程不使用產生式服務（無 TTS / 無生成影像），僅用本地環境與動畫混合、表情軌跡。
# 規則：不搖鏡；低音量 BGM 鋪底；以 env_intensity 做「吸/吐」潮汐律動；時長/強度以參數可調。

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# --- 基礎控制（非生成）---
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
bgm() { local URL="$1"; local VOL=${2:-0.16}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-0.8}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-true}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }
anim_mix_tail() {
  # 空體Action + 單式，拉長（tail）
  local BASESPD=${1:-1.7}; local YOGA_SPD=${2:-0.62}; local TD=${3:-0.75}; local MOVE="$4"; local BLEND=${5:-"additive"}
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD},
    {"name":"$MOVE","weight":1.0,"loop":true,"speed":$YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "$BLEND"
}
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; echo ">> 角色位置: [$X,$Y,$Z]"; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }

# 只送表情軌跡（不說話）
emote() {
  local DURATION=${1:-1.8}; local EMOS=${2:-"serene,content,relieved"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]"; 
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  echo ">> 表情: $EMOS ($DURATION s)"; $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null; sleep $(echo "$DURATION * 0.60" | bc); }

# 關閉會用錢的自動行為
cheap_mode_disable_generative() {
  $CURL_POST_NF "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled":false}' >/dev/null || true
  $CURL_POST_NF "$BASE_URL/control/realtime-voice" -H "Content-Type: application/json" -d '{"action":"stop"}' >/dev/null || true
}

# --- 參數區（可自行調整時長/強度） ---
# BGM
BGM_URL="/audio/BGM/spacelive_theme.mp3"
BGM_VOLUME=0.16

# 主循環回合數（增加可拉長時長）
MAIN_LOOPS=12

# 潮汐強度範圍
INHALE_INTENSITY_MIN=0.84
INHALE_INTENSITY_MAX=0.96
EXHALE_INTENSITY_MIN=0.64
EXHALE_INTENSITY_MAX=0.78

# 動作可視時間（tail 段）
TAIL_VISIBLE_MIN=4.8
TAIL_VISIBLE_MAX=6.4

# 表情時長
EMOTE_DUR_MIN=1.8
EMOTE_DUR_MAX=2.6

# tail 動作混合參數
TAIL_BASESPD_MIN=1.65
TAIL_BASESPD_MAX=1.88
TAIL_YOGASPD_MIN=0.55
TAIL_YOGASPD_MAX=0.70
TAIL_TD_MIN=0.70
TAIL_TD_MAX=0.90

# 偶發敬畏表情的觸發機率（分母越小越常出現）
AWE_PROB_DENOM=4

# 動作/情緒池
YOGA_TAIL=("瑜珈動作2" "瑜珈動作6" "瑜珈動作11" "瑜珈動作14" "瑜珈動作17")
EMO_COOL=("serene,content,relieved" "grateful,content,serene")
EMO_FOCUS=("interested,determined,proud" "neutral,determined,proud")
EMO_AWE=("awe,hopeful,joyful" "surprised,awe,joyful")
X_CHOICES=(-1.2 -1.0 -0.8 0 0.8 1.0 1.2)

echo "=== 🧘 Space Yoga Teacher — Aurora Drift Flow 開始（便宜模式） ==="

# 便宜模式開場：關 murmur/即時語音、停 BGM、環境基準、角色基準 + BGM（低音量）
cheap_mode_disable_generative
stop_bgm
env_preset "night" || true
env_background true || true
env_intensity 0.75 || true
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.6 true
bgm "$BGM_URL" $BGM_VOLUME

# 開場表情：安靜進入
emote 1.6 "serene,content,relieved"

# 主段：潮汐多回合（每回合：吸→吐，慢動作拉長 + 表情）
for ((i=1;i<=MAIN_LOOPS;i++)); do
  # 位置微變；吸氣：漸亮
  X=$(rand_choice X_CHOICES[@])
  char_position "$X" 8.0 -30.0
  env_intensity $(rand_float $INHALE_INTENSITY_MIN $INHALE_INTENSITY_MAX 2)
  # 拉長 tail（瑜伽單式）
  M=$(rand_choice YOGA_TAIL[@])
  anim_mix_tail $(rand_float $TAIL_BASESPD_MIN $TAIL_BASESPD_MAX 2) $(rand_float $TAIL_YOGASPD_MIN $TAIL_YOGASPD_MAX 2) $(rand_float $TAIL_TD_MIN $TAIL_TD_MAX 2) "$M" "additive"
  # 可視時間（慢）
  sleep $(rand_float $TAIL_VISIBLE_MIN $TAIL_VISIBLE_MAX 2)
  # 表情（放鬆/冷靜）
  emote $(rand_float $EMOTE_DUR_MIN $EMOTE_DUR_MAX 1) "$(rand_choice EMO_COOL[@])"
  # 吐氣：漸暗 + 小停頓
  env_intensity $(rand_float $EXHALE_INTENSITY_MIN $EXHALE_INTENSITY_MAX 2)
  sleep 0.8
  # 偶發敬畏，增添極光驚喜
  if (( RANDOM % AWE_PROB_DENOM == 0 )); then emote 1.2 "$(rand_choice EMO_AWE[@])"; fi
done

# 收束：回中位，最後一次 tail + 放鬆表情
char_position 0.0 8.0 -30.0
M=$(rand_choice YOGA_TAIL[@])
anim_mix_tail 1.7 0.60 0.8 "$M"
sleep 4.0
emote 2.0 "grateful,content,serene"

echo "=== ✅ Aurora Drift Flow 結束（無 TTS，低音量 BGM 持續播放） ==="
