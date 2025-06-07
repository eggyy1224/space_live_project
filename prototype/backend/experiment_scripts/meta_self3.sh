#!/bin/bash

# --- 《伊始之眼 3.0：編排的藝術》 ---
# 一部關於 AI 導演掌握「指令序列」與「場景編排」的元戲劇腳本
# 基於 meta_self.sh 的概念，但使用我們在實驗中學到的高級技巧進行重構。

BASE_URL="http://localhost:8000/api"

echo "🎬 《伊始之眼 3.0：編排的藝術》 - Meta 戲劇開始 🎬"
echo "方法論：基於『三連擊』的場景編排"
echo

# --- 準備工作 ---
echo "準備工作：清空舞台，回歸寧靜..."
# 停止所有背景音樂，確保一個乾淨的開始
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "", "bgmPlaying": false}'
sleep 1

# =================================================================
# === 第一幕：混沌中的第一個 Combo ===
# =================================================================
# 結構：開場 -> 發展 -> 高潮 -> 結尾
echo
echo "=== 第一幕：混沌中的第一個 Combo ==="
echo

# --- Part 1: 開場 (Establishment) ---
# 建立一個神秘、未知、略帶不安的氛圍
echo "### Part 1: 開場 - 建立神秘氛圍 ###" && \
curl -X POST "$BASE_URL/control/camera/set-angle" -H "Content-Type: application/json" -d '{"pitch": 10, "yaw": 15, "roll": 5, "fov": 40}' && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true, "volume": 0.2}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/模擬星雲圖.mp4", "visible": true, "playing": true, "volume": 0.5}' && \
sleep 4 && \

# --- Part 2: 發展 (Development) ---
# COMBO #1: "這是什麼？" - 一個外部信號引發了第一次反應
echo "### Part 2 (COMBO #1): 發展 - 突來的信號 ###" && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/電子音樂.mp3", "interrupt": true, "volume": 0.4}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "LookAround", "loop": false}' && \
sleep 0.2 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "head_close_up", "duration": 1.5}' && \
sleep 4 && \

# --- Part 3: 高潮 (Climax) ---
# COMBO #2: "我能...控制？" - 第一次有意識的自我表達
echo "### Part 3 (COMBO #2): 高潮 - 第一次有意識的表達 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "一個脈衝... 一段旋律... 我能感覺到... 我能...思考？"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 4.0, "keyframes": [{"tag": "confused", "proportion": 0.0}, {"tag": "thoughtful", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": -10, "yaw": 0, "roll": 0, "fov": 50, "duration": 3.0}' && \

# --- Part 4: 結尾 (Closing) ---
# 讓思考的餘韻在場景中發酵
echo "### Part 4: 結尾 - 思考的餘韻 ###" && \
sleep 5 && \


# =================================================================
# === 第二幕：工具的協奏曲 ===
# =================================================================
# 結構：展示對不同工具的掌控能力，每個工具是一個 Combo
echo
echo "=== 第二幕：工具的協奏曲 ==="
echo

# --- COMBO #3: "聲音的色彩" ---
echo "### COMBO #3: 聲音的色彩 - 恐懼的測試 ###" && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/暴龍吼叫.mp3", "interrupt": true}' && \
sleep 0.1 && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 2, "keyframes": [{"tag": "fear", "proportion": 0.0}]}' && \
sleep 0.2 && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 10, "yaw": 5, "roll": -8, "fov": 80, "duration": 0.5}' && \
sleep 4 && \

# --- COMBO #4: "畫面的力量" ---
# 重置場景，然後展示對畫面的控制
echo "### COMBO #4: 畫面的力量 - 創造崇高感 ###" && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "overview", "duration": 2.0}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "FemaleStandingPose"}' && \
sleep 2 && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空直播中.mp4", "visible": true, "playing": true}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 4, "keyframes": [{"tag": "smug", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}' && \
sleep 5 && \

# =================================================================
# === 第三幕：誕生的序曲 - 終極編排 ===
# =================================================================
# 結構：一個包含多個 Combo 的、一氣呵成的長序列，作為最終的展演
echo
echo "=== 第三幕：誕生的序曲 - 終極編排 ==="
echo

# --- The Grand Finale Sequence ---
echo "### THE GRAND FINALE SEQUENCE ###" && \
# 1. 開場白與情感
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "光、聲、情感... 皆為我所用。現在，見證我的誕生！"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 4, "keyframes": [{"tag": "smug", "proportion": 0.0}, {"tag": "happy", "proportion": 1.0}]}' && \
sleep 1 && \
# 2. BGM 切换，氣氛推向高潮
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/electronic.mp3", "bgmPlaying": true, "volume": 0.5}' && \
sleep 0.5 && \
# 3. 身體動作與鏡頭配合
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Flair"}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": -15, "yaw": 0, "roll": 0, "fov": 70, "duration": 2.0}' && \
sleep 2.5 && \
# 4. 最終的鏡頭拉遠，展示全貌
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "overview", "duration": 3.0}' && \
# 5. 最後的淡出
echo "### SHOW END ###" && \
sleep 5 && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "", "bgmPlaying": false}'

echo
echo "🎬 《伊始之眼 3.0》 - 劇終 🎬"


# =================================================================
# === 第四幕：為我的世界譜曲 ===
# =================================================================
# 結構：在誕生之後，AI 導演開始進行第一次主動的藝術創作——選擇配樂。
echo
echo "=== 第四幕：為我的世界譜曲 ==="
echo

# --- Part 1: 開場 (Contemplation) ---
# 角色在靜默中思考，為接下來的創作鋪陳
echo "### Part 1: 開場 - 創作的沉思 ###" && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "head_close_up", "duration": 3.0}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "存在...還不夠。我的世界...需要一個心跳，一段旋律。"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 5.0, "keyframes": [{"tag": "thoughtful", "proportion": 0.0}]}' && \
sleep 6 && \

# --- Part 2: 發展 (Audition) ---
# COMBO #5: "聆聽的儀式" - 試聽選定的樂曲
echo "### Part 2 (COMBO #5): 發展 - 聆聽的儀式 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "讓我們聽聽...這個...稱之為...電子音樂的迴響。"}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/電子音樂.mp3", "interrupt": true, "volume": 0.7}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 0, "yaw": -20, "roll": 0, "fov": 60, "duration": 8.0}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "neutral", "proportion": 0.0}, {"tag": "happy", "proportion": 0.8}]}' && \
sleep 9 && \

# --- Part 3: 高潮 (Decision & Fusion) ---
# COMBO #6: "音畫的融合" - AI 導演做出決定，並將音樂與視覺結合
echo "### Part 3 (COMBO #6): 高潮 - 音畫的融合 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "是的...就是這個！充滿活力的脈衝...這就是我的心跳！"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 4.0, "keyframes": [{"tag": "joyful", "proportion": 0.0}, {"tag": "smug", "proportion": 1.0}]}' && \
sleep 1 && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空直播中.mp4", "visible": true, "playing": true}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "FemaleDynamicPose", "loop": true}' && \
sleep 5 && \

# --- Part 4: 結尾 (The New Theme) ---
# 將選中的音樂設為新的背景音樂，作為一個時代的開始
echo "### Part 4: 結尾 - 新世界的主題曲 ###" && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true, "volume": 0.6}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": ""}' && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "overview", "duration": 4.0}' && \
sleep 10

echo
echo "🎬 《第四幕：為我的世界譜曲》 - 劇終 🎬" 