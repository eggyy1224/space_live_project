#!/bin/bash

# 《Space News Reporter — Baseline Scene (Rich Edition)》
# 目的：
# 1) 設定新聞主播風格的場景、鏡位、角色位置與 TTS 語氣/音調
# 2) 生成「太空主播」專屬新聞棚背景圖
# 3) 透過後端 /api/news/speak-latest-news 取得並播報最新太空新聞（Spaceflight News API）
#
# 執行：bash prototype/backend/experiment_scripts/reporter/news_reporter_baseline.sh

set -euo pipefail

BASE_URL="http://localhost:8000/api"
CURL_POST="curl -s -f -X POST"
CURL_POST_NF="curl -s -X POST"  # 不因 HTTP 狀態碼中止

# --- 全域 TTS 設定（新聞主播腔）---
# 建議：清晰、權威、穩定中速，低一點點的音高。
TTS_INSTRUCTION="zh-TW Mandarin, newsroom anchor tone, confident, neutral-warm, medium-low pitch, steady pace, clear enunciation"
TTS_VOICE_DEFAULT="coral"
TTS_SPEED_DEFAULT=1.15

# --- 小工具 ---
say() {
  # 用法: say "內容" 時長(秒) "emotion1,emotion2,..." [voice] [speed] [force]
  local CONTENT="$1"; local DURATION=${2:-3.0}; local EMOS=${3:-"neutral,confident,interested"}
  local VOICE=${4:-$TTS_VOICE_DEFAULT}; local SPEED=${5:-$TTS_SPEED_DEFAULT}; local FORCE=${6:-1}
  echo ">> 說話: $CONTENT ($DURATION s / $EMOS)"
  $CURL_POST "$BASE_URL/control/send-message" \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$CONTENT\", \"tts_instruction\": \"$TTS_INSTRUCTION\", \"tts_voice\": \"$VOICE\", \"tts_speed\": $SPEED}" >/dev/null || true
  # 基於情緒序列送出過渡曲線
  local IFS=','; read -ra KFS <<< "$EMOS"; unset IFS
  local KF_JSON="[]"
  if (( ${#KFS[@]} == 1 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 1.0}]"
  elif (( ${#KFS[@]} == 2 )); then
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.5},{\"tag\": \"${KFS[1]}\", \"proportion\": 1.0}]"
  else
    KF_JSON="[{\"tag\": \"${KFS[0]}\", \"proportion\": 0.0},{\"tag\": \"${KFS[1]}\", \"proportion\": 0.6},{\"tag\": \"${KFS[2]}\", \"proportion\": 1.0}]"
  fi
  $CURL_POST_NF "$BASE_URL/control/emotion-trajectory" \
    -H "Content-Type: application/json" \
    -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null || true
  sleep $(echo "$DURATION * 0.8" | bc)
}

emote() {
  local DURATION=${1:-2.2}; local EMOS=${2:-"neutral,confident,interested"}
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
  $CURL_POST_NF "$BASE_URL/control/emotion-trajectory" \
    -H "Content-Type: application/json" \
    -d "{\"duration\": $DURATION, \"keyframes\": $KF_JSON}" >/dev/null || true
  sleep $(echo "$DURATION * 0.6" | bc)
}

cam_preset() {
  local NAME="$1"; local D=${2:-1.2}
  echo ">> 鏡位 preset: $NAME ($D s)"
  $CURL_POST "$BASE_URL/control/camera/set-frontend-preset" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$NAME\", \"duration\": $D}" >/dev/null || true
  sleep $D
}

env_preset() {
  local PRE="$1"
  echo ">> 環境: $PRE"
  $CURL_POST "$BASE_URL/control/environment/preset" \
    -H "Content-Type: application/json" \
    -d "{\"preset\": \"$PRE\"}" >/dev/null || true
}

# 生成「太空新聞棚」背景並自動套用
gen_space_newsroom_bg() {
  # 提示詞聚焦：未來感、太空視窗、專業棚內光影、藍青色調、清晰且乾淨
  local PROMPT="A futuristic space newsroom interior, holographic overlays, professional broadcast lighting, blue/cyan accents, sleek glass panels, curved LED walls, transparent displays, distant Earth visible through large panoramic window, ultra-clean, cinematic composition"
  echo ">> 生成背景圖：Space Newsroom"
  # 注意：後端參數為 description（不是 prompt），aspect_ratio 建議填 "16:9"
  $CURL_POST_NF "$BASE_URL/generate-background-image" \
    -H "Content-Type: application/json" \
    -d "{\"description\": \"$PROMPT\", \"aspect_ratio\": \"16:9\"}" >/dev/null || true
}

# 叫用後端聚合新聞並朗讀（會使用後端預設 TTS；前後可由 say() 包裝以維持整體聲線）
speak_latest_news() {
  local LIMIT=${1:-5}
  local INTRO=${2:-"接下來為您帶來最新的太空頭條："}
  echo ">> 取得並播報最新太空新聞 ($LIMIT 則)"
  $CURL_POST_NF "$BASE_URL/news/speak-latest-news" \
    -H "Content-Type: application/json" \
    -d "{\"limit\": $LIMIT, \"intro_text\": \"$INTRO\"}" >/dev/null || true
}

# 關閉背景音樂（避免與新聞播報衝突）
stop_bgm() {
  echo ">> 關閉背景音樂"
  $CURL_POST_NF "$BASE_URL/control/background-audio" \
    -H "Content-Type: application/json" \
    -d '{"bgmUrl": "", "bgmPlaying": false}' >/dev/null || true
}

char_scale() { local S=${1:-1.0}; echo ">> 角色大小: $S"; $CURL_POST "$BASE_URL/control/character/scale" -H "Content-Type: application/json" -d "{\"scale\": $S}" >/dev/null || true; }
char_position() { local X=${1:-0.0}; local Y=${2:-0.0}; local Z=${3:-0.0}; echo ">> 角色位置: [$X,$Y,$Z]"; $CURL_POST "$BASE_URL/control/character/position" -H "Content-Type: application/json" -d "{\"position\": [$X,$Y,$Z]}" >/dev/null || true; }
anim_char() { local A="$1"; local S=${2:-1.0}; local L=${3:-true}; echo ">> 主角動畫: $A x$S loop=$L"; $CURL_POST "$BASE_URL/control/character/animation" -H "Content-Type: application/json" -d "{\"animation\": \"$A\", \"loop\": $L, \"speed\": $S}" >/dev/null || true; }

# 動畫混合：可同時播放多個動畫
anim_mix() {
  echo ">> 主角動畫混合: 空體Action + 划手機 + 臥躺"
  $CURL_POST_NF "$BASE_URL/control/character/animation-mix" \
    -H "Content-Type: application/json" \
    -d '{
      "animations": [
        {"name": "空體Action", "weight": 1.0, "loop": true, "speed": 1.0},
        {"name": "划手機", "weight": 0.65, "loop": true, "speed": 1.0},
        {"name": "臥躺", "weight": 0.35, "loop": true, "speed": 1.0}
      ],
      "transitionDuration": 0.8,
      "blendMode": "normal"
    }' >/dev/null || true
}

# 空氣感間隔（降低語速密度）
gap() { local S=${1:-0.8}; echo ">> 空檔: ${S}s"; sleep "$S"; }

echo "=== 🛰️ Space News Reporter — Baseline Scene 開始 ==="

# 關閉隨機導播
$CURL_POST "$BASE_URL/control/broadcast" -H "Content-Type: application/json" -d '{"type":"director-state","payload":{"randomMode":false}}' >/dev/null || true

# 1) 場景：Studio 燈光與新聞室氛圍 + 生成專屬背景
env_preset "studio" || true
# 生成太空新聞棚背景（自動套用於場景背景）
gen_space_newsroom_bg || true
# 可選：若有光照控制 API，可在此調整亮度（保守略過）

# 2) 鏡位 + 角色位置：頭部特寫 + 微調 Z 以便字幕清楚
cam_preset "head_close_up" 1.0
char_scale 0.1
char_position 0.0 0.0 0.0
anim_mix

# 3) 語氣/音調：新聞主播預設 TTS 參數 + 強化版開場
say "各位觀眾晚安，這裡是太空新聞台，我是今晚的主播。" 3.4 "neutral,confident,interested" "$TTS_VOICE_DEFAULT" $TTS_SPEED_DEFAULT 1
gap 0.9
say "現在帶您掌握全球軌道活動、深空任務進度，以及最新的科學觀測重點。" 4.0 "confident,interested,neutral"
gap 1.0
emote 1.8 "neutral,interested,content"

# 4) 今日重點提要（主播口播）
say "今晚頭條：商業補給船即將與國際太空站完成交會對接；" 3.2 "confident,interested,neutral"
gap 0.8
say "火星軌道器傳回新一批高解析影像，地表季節性變化細節首次清晰呈現；" 4.0 "interested,confident,neutral"
gap 0.8
say "而在月球前哨站計畫方面，地面測試進度傳出關鍵里程碑。" 3.4 "confident,neutral,interested"
gap 1.2
emote 2.0 "interested,content,confident"

# 5) 透過後端 API 取得並播報最新太空新聞（使用 Spaceflight News API）
say "接著是即時焦點，我們快速瀏覽最新五則太空動態。" 3.2 "confident,interested,neutral"
gap 1.0
stop_bgm
speak_latest_news 5 "以下是剛剛更新的太空頭條："
gap 1.0
emote 1.6 "interested,neutral,content"

# 6) 短評與轉場
cam_preset "frontal_dynamic_low" 1.0
gap 0.8
say "關於第一則，我們會持續關注任務控制中心的狀態回報，" 3.6 "confident,interested,neutral"
gap 0.8
say "並在確認新的計畫時間軸後，第一時間帶您追蹤。" 3.0 "confident,neutral,interested"
cam_preset "head_close_up" 1.0
gap 0.8
emote 1.6 "content,neutral,serene"

# 7) 收尾
say "以上是本時段的太空快訊。想看更多任務視覺與即時畫面，" 3.6 "confident,interested,neutral"
gap 0.9
say "也歡迎在聊天室告訴我們您想關注的主題。" 3.2 "interested,content,neutral"

echo "=== ✅ Space News Reporter — Baseline Scene 完成（場景/位置/TTS/新聞/背景） ==="
