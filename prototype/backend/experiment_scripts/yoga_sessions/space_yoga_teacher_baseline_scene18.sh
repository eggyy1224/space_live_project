#!/bin/bash

# 《Space Yoga Teacher — Pulsar Cadence Flow》
# 主題：規律脈衝（強-弱-弱 | 強-弱-弱 …）。
# 目標：不使用生成式（無 TTS/無生成圖）；用縮放脈衝、可見性快閃、規律混合節拍做教學節奏。
# 規則：不搖鏡；低音量 BGM 持續鋪底；時長/強度以參數可調（可瘋狂跳舞）。

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"   # 不因 HTTP 狀態碼中止

# --- 小工具 ---
rand_float() { local MIN=$1; local MAX=$2; local DEC=${3:-2}; awk -v min="$MIN" -v max="$MAX" -v dec="$DEC" 'BEGIN{srand(); v=min+rand()*(max-min); printf("%.*f\n", dec, v)}'; }
rand_choice() { local arr=("${!1}"); local n=${#arr[@]}; echo "${arr[$((RANDOM % n))]}"; }

# --- 基礎控制（非生成）---
stop_bgm() { $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl":"","bgmPlaying":false}' >/dev/null; }
bgm() { local URL="$1"; local VOL=${2:-0.20}; $CURL_POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$URL\", \"bgmPlaying\": true, \"loop\": true, \"volume\": $VOL}" >/dev/null; }
env_preset() { local PRE="$1"; $CURL_POST "$BASE_URL/control/environment/preset" -H "Content-Type: application/json" -d "{\"preset\": \"$PRE\"}" >/dev/null; }
env_intensity() { local I=${1:-0.85}; $CURL_POST "$BASE_URL/control/environment/intensity" -H "Content-Type: application/json" -d "{\"intensity\": $I}" >/dev/null; }
env_background() { local B=${1:-false}; $CURL_POST "$BASE_URL/control/environment/background" -H "Content-Type: application/json" -d "{\"background\": $B}" >/dev/null; }

anim_char() { local ANIM="$1"; local SPEED=${2:-1.0}; local LOOP=${3:-true}; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$ANIM\", \"loop\": $LOOP, \"speed\": $SPEED}" >/dev/null; }

anim_mix_strong() {
  # 強拍：空體Action + 2 式，短轉場，高速
  local BASESPD=${1:-2.1}; local YOGA_SPD=${2:-1.02}; local TD=${3:-0.50}; local M1="$4"; local M2="$5"
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD},
    {"name":"$M1","weight":1.0,"loop":true,"speed":$YOGA_SPD},
    {"name":"$M2","weight":1.0,"loop":true,"speed":$YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

anim_mix_weak() {
  # 弱拍：空體Action + 單式，拉長
  local BASESPD=${1:-1.85}; local YOGA_SPD=${2:-0.68}; local TD=${3:-0.75}; local MOVE="$4"
  local PAYLOAD
  PAYLOAD=$(cat <<JSON
{
  "animations": [
    {"name":"空體Action","weight":1.0,"loop":true,"speed":$BASESPD},
    {"name":"$MOVE","weight":1.0,"loop":true,"speed":$YOGA_SPD}
  ],
  "transitionDuration": $TD,
  "blendMode": "additive"
}
JSON
  )
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" -H "Content-Type: application/json" -d "$PAYLOAD" >/dev/null
}

head_size() { local S=${1:-10.0}; $CURL_POST "$BASE_URL/control/head-size" -H "Content-Type: application/json" -d "{\"scaleFactor\": $S}" >/dev/null; }
char_scale() { local S=${1:-0.1}; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null; }
char_position() { local X=${1:-0.0}; local Y=${2:-8.0}; local Z=${3:-30.0}; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null; }
char_visible() { local V=${1:-true}; $CURL_POST "$BASE_URL/control/character/visibility" -H "Content-Type: application/json" -d "{\"visible\": $V}" >/dev/null; }

# 只送表情軌跡（不說話）
emote() {
  local DURATION=${1:-1.0}; local EMOS=${2:-"joyful,excited,triumphant"}
  IFS=',' read -ra KFS <<< "$EMOS"; local KF_JSON
  if (( ${#KFS[@]} == 1 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":1.0}]"; 
  elif (( ${#KFS[@]} == 2 )); then KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.5},{\"tag\":\"${KFS[1]}\",\"proportion\":1.0}]"; 
  else KF_JSON="[{\"tag\":\"${KFS[0]}\",\"proportion\":0.0},{\"tag\":\"${KFS[1]}\",\"proportion\":0.6},{\"tag\":\"${KFS[2]}\",\"proportion\":1.0}]"; fi
  $CURL_POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null
  sleep $(echo "$DURATION * 0.55" | bc)
}

# 關閉會用錢的自動行為
cheap_mode_disable_generative() {
  $CURL_POST_NF "$BASE_URL/control/murmur-mode" -H "Content-Type: application/json" -d '{"enabled":false}' >/dev/null || true
  $CURL_POST_NF "$BASE_URL/control/realtime-voice" -H "Content-Type: application/json" -d '{"action":"stop"}' >/dev/null || true
}

# --- 參數區（可自行調整時長/強度） ---
# BGM
BGM_URL="/audio/BGM/spacelive_theme2.mp3"
BGM_VOLUME=0.22

# 組/節拍結構
GROUP_COUNT=6
BEATS_PER_GROUP=4  # 強-弱-弱-停，固定 4

# 強拍（高速）參數
STRONG_BASE_MIN=2.05
STRONG_BASE_MAX=2.35
STRONG_YOGA_MIN=0.98
STRONG_YOGA_MAX=1.12
STRONG_TD_MIN=0.45
STRONG_TD_MAX=0.55
STRONG_EMOTE_MIN=0.80
STRONG_EMOTE_MAX=1.05

# 弱拍（拉長）參數
WEAK_BASE=1.85
WEAK_YOGA_MIN=0.60
WEAK_YOGA_MAX=0.80
WEAK_TD=0.75
WEAK_EMOTE_MIN=1.00
WEAK_EMOTE_MAX=1.30

# 脈衝縮放/可見性快閃/抖動
PULSE_SCALE=0.12
BASE_SCALE=0.10
PULSE_DUR=0.10
FLASH_PROB_DENOM=3
JITTER_X_MIN=-0.6
JITTER_X_MAX=0.6
JITTER_Z_MIN=-30.4
JITTER_Z_MAX=-29.6

# 最終狂熱段（瘋狂跳舞）
FINAL_FRENZY_ROUNDS=12
FRENZY_BASE_MIN=2.20
FRENZY_BASE_MAX=2.60
FRENZY_YOGA_MIN=1.05
FRENZY_YOGA_MAX=1.30
FRENZY_TD_MIN=0.45
FRENZY_TD_MAX=0.55
FRENZY_SLEEP_MIN=1.0
FRENZY_SLEEP_MAX=1.4

# 池
YOGA_FAST=("瑜珈動作3" "瑜珈動作5" "瑜珈動作7" "瑜珈動作9" "瑜珈動作12" "瑜珈動作17")
YOGA_TAIL=("瑜珈動作2" "瑜珈動作6" "瑜珈動作11" "瑜珈動作14")
EMO_HYPE=("joyful,excited,triumphant" "triumphant,proud,joyful")
EMO_SOFT=("interested,determined,proud" "serene,content,relieved")

echo "=== 🧘 Space Yoga Teacher — Pulsar Cadence Flow 開始（便宜模式） ==="

# 便宜模式開場 + 低音量 BGM
cheap_mode_disable_generative
stop_bgm
env_preset "studio" || true
env_background false || true
env_intensity 0.85 || true
head_size 10.0
char_scale 0.1
char_position 0.0 8.0 -30.0
anim_char "空體Action" 1.9 true
bgm "$BGM_URL" $BGM_VOLUME

# 主段：多組，每組 4 回合（強-弱-弱-停）
for ((g=1; g<=GROUP_COUNT; g++)); do
  # 組起始：輕微亮度提升提示開始
  env_intensity $(rand_float 0.88 0.95 2)
  sleep 0.4

  for ((b=1; b<=BEATS_PER_GROUP; b++)); do
    case $b in
      1) # 強拍
         # 脈衝縮放
         char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
         # 高速混合 + 短轉場
         M1=$(rand_choice YOGA_FAST[@]); M2=$(rand_choice YOGA_FAST[@])
         anim_mix_strong $(rand_float $STRONG_BASE_MIN $STRONG_BASE_MAX 2) $(rand_float $STRONG_YOGA_MIN $STRONG_YOGA_MAX 2) $(rand_float $STRONG_TD_MIN $STRONG_TD_MAX 2) "$M1" "$M2"
         # 強表情（短促）
         emote $(rand_float $STRONG_EMOTE_MIN $STRONG_EMOTE_MAX 2) "$(rand_choice EMO_HYPE[@])"
         ;;
      2|3) # 弱拍
         M=$(rand_choice YOGA_TAIL[@])
         anim_mix_weak $WEAK_BASE $(rand_float $WEAK_YOGA_MIN $WEAK_YOGA_MAX 2) $WEAK_TD "$M"
         # 弱表情（專注/放鬆）
         emote $(rand_float $WEAK_EMOTE_MIN $WEAK_EMOTE_MAX 2) "$(rand_choice EMO_SOFT[@])"
         # 第二個弱拍偶爾可見性快閃
         if [[ $b -eq 3 && $((RANDOM % FLASH_PROB_DENOM)) -eq 0 ]]; then char_visible false; sleep 0.10; char_visible true; fi
         ;;
      4) # 小停頓 + 微抖動定位
         char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
         sleep 0.9
         ;;
    esac
  done

  # 組結束：亮度回落
  env_intensity $(rand_float 0.80 0.86 2)
  sleep 0.5
done

# 最終狂熱段：連續強拍（可調回合數）
if (( FINAL_FRENZY_ROUNDS > 0 )); then
  for ((k=1; k<=FINAL_FRENZY_ROUNDS; k++)); do
    # 脈衝 + 快速混合
    char_scale $PULSE_SCALE; sleep $PULSE_DUR; char_scale $BASE_SCALE
    M1=$(rand_choice YOGA_FAST[@]); M2=$(rand_choice YOGA_FAST[@])
    anim_mix_strong $(rand_float $FRENZY_BASE_MIN $FRENZY_BASE_MAX 2) $(rand_float $FRENZY_YOGA_MIN $FRENZY_YOGA_MAX 2) $(rand_float $FRENZY_TD_MIN $FRENZY_TD_MAX 2) "$M1" "$M2"
    # 高能表情
    emote 1.0 "$(rand_choice EMO_HYPE[@])"
    # 快閃
    if (( RANDOM % FLASH_PROB_DENOM == 0 )); then char_visible false; sleep 0.10; char_visible true; fi
    # 微抖動
    char_position $(rand_float $JITTER_X_MIN $JITTER_X_MAX 2) 8.0 $(rand_float $JITTER_Z_MIN $JITTER_Z_MAX 2)
    # 留出可視時間
    sleep $(rand_float $FRENZY_SLEEP_MIN $FRENZY_SLEEP_MAX 2)
  done
fi

# 收束：放慢兩拍，定格（BGM 繼續）
anim_mix_weak 1.80 0.62 0.80 "$(rand_choice YOGA_TAIL[@])"
sleep 1.6
emote 1.6 "serene,content,relieved"

echo "=== ✅ Pulsar Cadence Flow 結束（無 TTS，低音量 BGM 持續播放） ==="
