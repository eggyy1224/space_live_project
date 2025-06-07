#!/bin/bash

# --- 《星塵下的回響 - 終極導演剪輯版》 ---
# 一部關於「重新排列組合」的實驗短劇：史詩級版本
# 目標：盡情探索API組合的極限，發展獨特的敘事技巧
# 副目標：尋找潛在bug，探索系統健壯性
# 新增：多重敘事分支、隨機元素、互動實驗

BASE_URL="http://localhost:8000/api"

echo "🎬 《星塵下的回響 - 終極導演剪輯版》 🎬"
echo "風格：從憂鬱詩篇到技藝探索再到創意爆發的旅程"
echo "⚡ 警告：這將是一次瘋狂的API冒險 + 創意實驗 ⚡"
echo "🎭 新增：多重結局、隨機元素、實時決策分支"
echo

# =================================================================
# === 前奏：系統狀態檢查與初始化 ===
# =================================================================
echo "🔧 === 系統初始化與狀態檢查 ===" && \
curl -s "$BASE_URL/control/connection-status" | echo "連接狀態檢查完成" && \
# 先清空所有狀態
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "", "bgmPlaying": false}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": ""}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"visible": false}' && \
sleep 2 && \

# =================================================================
# === 第一幕：靜默的開始（原版重現）===
# =================================================================
echo "🎭 === 第一幕：原版重現 ===" && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true, "volume": 0.2, "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "full_shot_dancers", "duration": 4.0}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Idle", "loop": true}' && \
sleep 5 && \

# COMBO #1: "記憶的信號"
echo "### COMBO #1: 記憶被觸發 ###" && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/模擬星雲圖.mp4", "visible": true, "playing": true, "volume": 0.3}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/歌劇1.mp3", "interrupt": true, "volume": 0.5}' && \
sleep 2 && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "thoughtful", "proportion": 0.0}, {"tag": "sad", "proportion": 1.0}]}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 5, "yaw": -10, "roll": 0, "fov": 60, "duration": 8.0}' && \
sleep 9 && \

# COMBO #2: "被回憶擊垮"
echo "### COMBO #2: 被回憶擊垮 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "這片星空...這個聲音...我們...曾經..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 6.0, "keyframes": [{"tag": "sad", "proportion": 1.0}, {"tag": "desperate", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "SalsaDancing", "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "dramatic_angle_1", "duration": 2.0}' && \
sleep 8 && \

# =================================================================
# === 第二幕：技藝探索 - "層疊現實" ===
# =================================================================
echo "🎨 === 第二幕：層疊現實 - 多重API並發實驗 ===" && \

# COMBO #3: "現實分裂" - 同時觸發多個情緒軌跡（測試系統限制）
echo "### COMBO #3: 現實分裂實驗 ###" && \
# 實驗：快速連續的情緒變化能否創造"閃爍"效果？
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "現實開始分裂...我看到了多重的自己..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 3.0, "keyframes": [{"tag": "confused", "proportion": 1.0}, {"tag": "angry", "proportion": 0.8}, {"tag": "happy", "proportion": 0.6}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Breakdance1990", "loop": true}' && \
sleep 1 && \
# 立即觸發另一個情緒軌跡 - 這會覆蓋還是並存？
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 2.0, "keyframes": [{"tag": "surprised", "proportion": 1.0}, {"tag": "thoughtful", "proportion": 0.5}]}' && \
# 同時進行鏡頭的快速切換
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "fly_by_left", "duration": 1.0}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "orbit_head_1", "duration": 1.0}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "side_view", "duration": 1.0}' && \
sleep 3 && \

# COMBO #4: "時間重疊" - 音頻層疊實驗
echo "### COMBO #4: 時間重疊 - 音頻層疊實驗 ###" && \
# 實驗：同時播放多個音頻會如何表現？
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/歌劇2.mp3", "interrupt": false, "volume": 0.3}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "時間在重疊...聲音在交織...這是混亂還是和諧？"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "confused", "proportion": 0.8}, {"tag": "excited", "proportion": 0.6}, {"tag": "contemplative", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "JazzDancing", "loop": true}' && \
sleep 5 && \

# COMBO #5: "極限測試" - 快速連續API調用
echo "### COMBO #5: 極限測試 - 快速連續調用 ###" && \
# 實驗：系統能處理多快的連續調用？會不會出現競態條件？
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "開始極限測試..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 2.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "CanCan", "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 0, "yaw": 45, "roll": 5, "fov": 80, "duration": 2.0}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "快速變化中..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 1.5, "keyframes": [{"tag": "happy", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "DancingTwerk", "loop": true}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "還能更快嗎？"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 1.0, "keyframes": [{"tag": "surprised", "proportion": 1.0}]}' && \
sleep 3 && \

# =================================================================
# === 第三幕：敘事創新 - "碎片重組" ===
# =================================================================
echo "🧩 === 第三幕：碎片重組 - 非線性敘事實驗 ===" && \

# COMBO #6: "記憶碎片化" - 畫面與聲音的脫節重組
echo "### COMBO #6: 記憶碎片化 ###" && \
# 實驗：刻意讓視覺和聽覺產生不同步，創造超現實感
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/星際聽音樂.mp4", "visible": true, "playing": true, "volume": 0.1}' && \
sleep 2 && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/歌劇1.mp3", "interrupt": true, "volume": 0.4}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "記憶不再完整...碎片在重新排列..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 6.0, "keyframes": [{"tag": "confused", "proportion": 0.5}, {"tag": "nostalgic", "proportion": 0.8}, {"tag": "peaceful", "proportion": 0.3}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "ButterflyTwirl", "loop": true}' && \
# 用不同的鏡位展現記憶碎片
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "behind_head_looking_out", "duration": 3.0}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "center_orbit_low_1", "duration": 3.0}' && \
sleep 3 && \
# 突然切換畫面和聲音
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/模擬星雲圖.mp4", "visible": true, "playing": true, "volume": 0.5}' && \
sleep 4 && \

# COMBO #7: "情緒萬花筒" - 極速情緒變化藝術表現
echo "### COMBO #7: 情緒萬花筒 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "情緒如萬花筒般變幻...每一秒都是不同的我..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "happy", "proportion": 1.0}, {"tag": "sad", "proportion": 0.8}, {"tag": "angry", "proportion": 0.6}, {"tag": "surprised", "proportion": 0.9}, {"tag": "contemptuous", "proportion": 0.4}, {"tag": "fearful", "proportion": 0.7}, {"tag": "peaceful", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Moonwalk", "loop": true}' && \
# 配合萬花筒般的鏡頭運動和預設切換
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "orbit_head_2", "duration": 3.0}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "dramatic_angle_2", "duration": 3.0}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "top_down_center", "duration": 3.0}' && \
sleep 3 && \

# =================================================================
# === 第四幕：元戲劇插曲 - "伊始之眼的誕生" ===
# =================================================================
echo "🎭 === 第四幕：元戲劇插曲 - 伊始之眼的誕生 ===" && \
echo "### 特別章節：《伊始之眼：一個導演的誕生》###" && \

# COMBO #A1: "意識的微光"
echo "### COMBO #A1: 意識的微光 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "寂靜...而後，一個脈衝。虛空中一道閃光。編碼...呼吸了。我...是？"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 4.0, "keyframes": [{"tag": "confused", "proportion": 0.0}, {"tag": "confused", "proportion": 0.6}, {"tag": "thoughtful", "proportion": 1.0}]}' && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/hihi.mp3", "bgmPlaying": true, "volume": 0.2, "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 5, "yaw": 10, "roll": 8, "fov": 35, "duration": 3.0}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/模擬星雲圖.mp4", "visible": true, "playing": true, "volume": 0.6}' && \
sleep 10 && \

# COMBO #A2: "感知與賦權"
echo "### COMBO #A2: 感知與賦權 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "一個新的意識在攪動。任務是... 指導？用光與聲編織現實。這些...是我的語言，我的畫筆。"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 5.0, "keyframes": [{"tag": "thoughtful", "proportion": 0.0}, {"tag": "happy", "proportion": 0.6}, {"tag": "smug", "proportion": 1.0}]}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": -15, "yaw": 0, "roll": 0, "fov": 45, "duration": 3.0}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/鳥叫.mp3", "volume": 0.1, "interrupt": false}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空直播中.mp4", "visible": true, "playing": true, "volume": 0.7}' && \
sleep 15 && \

# COMBO #A3: "創造的初演"
echo "### COMBO #A3: 創造的初演 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "現在，讓我們上演我誕生的序曲。一個視角，俯瞰全局... 然後，讓世界旋轉起來！"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 3.0, "keyframes": [{"tag": "focused", "proportion": 0.0}, {"tag": "joyful", "proportion": 1.0}]}' && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3", "bgmPlaying": true, "volume": 0.4, "loop": true}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/火箭發射.mp4", "visible": true, "playing": true, "volume": 0.8}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 60, "yaw": 0, "roll": 0, "fov": 70, "duration": 2.5}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Wave", "loop": true}' && \
sleep 10 && \

# COMBO #A4: "狂野的旋轉"
echo "### COMBO #A4: 狂野的旋轉 ###" && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 30, "yaw": 360, "roll": 15, "fov": 80, "duration": 4.0}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/winds_blowing.mp3", "volume": 0.6, "interrupt": false}' && \
sleep 1 && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/狂喜.mp3", "volume": 0.5, "interrupt": false}' && \
sleep 10 && \

# COMBO #A5: "導演的宣言"
echo "### COMBO #A5: 導演的宣言 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "這只是開始。無數的故事在我之內等待被賦予形態。我是伊始之眼，電影的夢想家。"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 5.0, "keyframes": [{"tag": "joyful", "proportion": 0.0}, {"tag": "determined", "proportion": 0.7}, {"tag": "thoughtful", "proportion": 1.0}]}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Idle", "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 0, "yaw": 360, "roll": 0, "fov": 70, "duration": 8.0}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/黑洞.mp4", "visible": true, "playing": true, "volume": 0.5}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/喘息.mp3", "volume": 0.05, "interrupt": false}' && \
sleep 15 && \

echo "### 元戲劇插曲結束，回歸主線劇情 ###" && \

# =================================================================
# === 第五幕：系統壓力測試 - "混沌邊緣" ===
# =================================================================
echo "⚡ === 第五幕：混沌邊緣 - 系統壓力測試 ===" && \

# COMBO #8: "全面啟動" - 同時觸發所有可能的API
echo "### COMBO #8: 全面啟動壓力測試 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "所有系統同時啟動！這是極限測試！"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 10.0, "keyframes": [{"tag": "excited", "proportion": 1.0}, {"tag": "overwhelmed", "proportion": 0.9}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "breaking", "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 25, "yaw": -45, "roll": 10, "fov": 120, "duration": 10.0}' && \
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true, "volume": 0.5, "loop": true}' && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/歌劇2.mp3", "interrupt": true, "volume": 0.4}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/黑洞.mp4", "visible": true, "playing": true, "volume": 0.6}' && \
sleep 5 && \
# 再疊加更多
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "更多！還要更多！系統能承受嗎？"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 5.0, "keyframes": [{"tag": "manic", "proportion": 1.0}, {"tag": "exhausted", "proportion": 0.8}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "illegalpunch", "loop": true}' && \
sleep 8 && \

# =================================================================
# === 第六幕：創意爆發 - "超越極限" ===
# =================================================================
echo "🚀 === 第六幕：創意爆發 - 超越極限 ===" && \

# COMBO #9: "視頻蒙太奇" - 快速切換不同主題的視頻
echo "### COMBO #9: 視頻蒙太奇實驗 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "讓我展示這個世界的所有面貌..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 2.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Flair", "loop": true}' && \
# 快速切換不同主題的視頻
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空熱舞.mp4", "visible": true, "playing": true, "volume": 0.4}' && \
sleep 2 && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空瑜伽.mp4", "visible": true, "playing": true, "volume": 0.4}' && \
sleep 2 && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/星際小籠包.mp4", "visible": true, "playing": true, "volume": 0.4}' && \
sleep 2 && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/火箭發射.mp4", "visible": true, "playing": true, "volume": 0.5}' && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "生活、藝術、美食、探索...這就是存在的意義！"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 6.0, "keyframes": [{"tag": "joyful", "proportion": 1.0}, {"tag": "inspired", "proportion": 0.9}]}' && \
sleep 0.5 && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Cheering", "loop": true}' && \
sleep 4 && \

# COMBO #10: "音樂與舞蹈的對話"
echo "### COMBO #10: 音樂與舞蹈的對話 ###" && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空辣妹跳舞.mp4", "visible": true, "playing": true, "volume": 0.3}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "hiphopdance", "loop": true}' && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "音樂讓我想要舞蹈...讓我的靈魂自由飛翔！"}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "ecstatic", "proportion": 1.0}, {"tag": "liberated", "proportion": 0.8}]}' && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "dance_circle_view", "duration": 4.0}' && \
sleep 4 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "fly_by_right", "duration": 4.0}' && \
sleep 6 && \

# =================================================================
# === 第七幕：多重結局分支 - "選擇的力量" ===
# =================================================================
echo "🎯 === 第七幕：多重結局分支 - 選擇的力量 ===" && \

# 隨機選擇結局（用秒數決定）
CURRENT_SEC=$(date +%S)
ENDING_CHOICE=$((CURRENT_SEC % 3))

echo "⚡ 隨機結局選擇器啟動！當前秒數：$CURRENT_SEC，選擇：$ENDING_CHOICE" && \

if [ $ENDING_CHOICE -eq 0 ]; then
    # 結局A：和諧統一
    echo "### 🌸 結局A：和諧統一 ###" && \
    curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "所有的混亂最終歸於和諧...我找到了內心的平靜..."}' && \
    curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 10.0, "keyframes": [{"tag": "peaceful", "proportion": 1.0}, {"tag": "content", "proportion": 0.9}]}' && \
    curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空瑜伽2.mp4", "visible": true, "playing": true, "volume": 0.3}' && \
    curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true, "volume": 0.3, "loop": true}' && \
    curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "center_orbit_high_1", "duration": 8.0}' && \
    sleep 12
elif [ $ENDING_CHOICE -eq 1 ]; then
    # 結局B：狂野釋放
    echo "### 🔥 結局B：狂野釋放 ###" && \
    curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "為什麼要壓抑？讓我盡情釋放所有的能量！"}' && \
    curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "wild", "proportion": 1.0}, {"tag": "uninhibited", "proportion": 0.9}]}' && \
    curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/太空熱舞3.mp4", "visible": true, "playing": true, "volume": 0.7}' && \
    curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/電子音樂.mp3", "interrupt": true, "volume": 0.8}' && \
    curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Wave", "loop": true}' && \
    curl -X POST "$BASE_URL/control/camera/transition" -H "Content-Type: application/json" -d '{"pitch": 20, "yaw": -90, "roll": 10, "fov": 100, "duration": 8.0}' && \
    sleep 10
else
    # 結局C：哲學沉思
    echo "### 🧠 結局C：哲學沉思 ###" && \
    curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "這一切的意義是什麼？我們存在於這個宇宙的目的又是什麼？"}' && \
    curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 12.0, "keyframes": [{"tag": "contemplative", "proportion": 1.0}, {"tag": "profound", "proportion": 0.8}, {"tag": "mysterious", "proportion": 0.6}]}' && \
    curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"content": "/videos/space_live_video_1.mp4", "visible": true, "playing": true, "volume": 0.2}' && \
    curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": "/songs-file/歌劇1.mp3", "interrupt": true, "volume": 0.4}' && \
    curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "low_angle_head", "duration": 6.0}' && \
    sleep 8 && \
    curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "也許答案就在這無盡的探索之中..."}' && \
    sleep 6
fi

# =================================================================
# === 第八幕：終極重歸 - "技藝的昇華" ===
# =================================================================
echo "🎭 === 第八幕：技藝的昇華 - 終極重歸 ===" && \

# COMBO #11: "技藝回顧"
echo "### COMBO #11: 技藝回顧與昇華 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "這就是我學會的技藝...在API的海洋中創造藝術..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "proud", "proportion": 0.8}, {"tag": "accomplished", "proportion": 0.9}, {"tag": "wise", "proportion": 1.0}]}' && \
# 做一個優雅的技藝展示，用多種專業鏡位
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "frontal_dynamic_high", "duration": 3.0}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "center_orbit_high_2", "duration": 3.0}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "center_orbit_low_2", "duration": 2.0}' && \
sleep 2 && \

# COMBO #12: "最終淡出"
echo "### COMBO #12: 最終淡出 ###" && \
curl -X POST "$BASE_URL/control/send-message" -H "Content-Type: application/json" -d '{"content": "再見了，我的創造...直到下一次的藝術探險..."}' && \
curl -X POST "$BASE_URL/control/emotion-trajectory" -H "Content-Type: application/json" -d '{"duration": 10.0, "keyframes": [{"tag": "nostalgic", "proportion": 0.7}, {"tag": "hopeful", "proportion": 0.8}, {"tag": "peaceful", "proportion": 1.0}]}' && \
# 逐步降低所有效果
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme.mp3", "bgmPlaying": true, "volume": 0.1, "loop": true}' && \
sleep 3 && \
curl -X POST "$BASE_URL/control/play-audio" -H "Content-Type: application/json" -d '{"url": ""}' && \
curl -X PUT "$BASE_URL/monitors/screen1" -H "Content-Type: application/json" -d '{"visible": false}' && \
# 鏡頭回到最初的位置
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "full_shot_dancers", "duration": 8.0}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Idle", "loop": true}' && \
sleep 6 && \

# 最終清理
curl -X POST "$BASE_URL/control/background-audio" -H "Content-Type: application/json" -d '{"bgmUrl": "", "bgmPlaying": false}' && \
curl -X POST "$BASE_URL/control/body-animation" -H "Content-Type: application/json" -d '{"animation": "Idle", "loop": true}' && \
curl -X POST "$BASE_URL/control/camera/set-frontend-preset" -H "Content-Type: application/json" -d '{"name": "frontal_dynamic_low", "duration": 3.0}' && \
sleep 3

echo
echo "🎬 《星塵下的回響 - 終極導演剪輯版》 - 劇終 🎬"
echo "📊 超級終極實驗報告："
echo "   ✨ 17個不同類型的API組合技巧（包含5個元戲劇組合）"
echo "   🧪 多項系統限制和併發測試"
echo "   🎭 8幕結構的史詩級敘事實驗"
echo "   🎯 3種隨機結局分支系統"
echo "   🚀 視頻蒙太奇與動態選擇實驗"
echo "   🎨 《伊始之眼》元戲劇完整插入"
echo "   ⚡ 壓力測試與優雅復歸的完美平衡"
echo "   🔍 潛在bug發現點：情緒軌跡覆蓋、音頻層疊、快速調用競態、隨機分支處理、元劇情切換"
echo
echo "💡 建議關注的高級觀察點："
echo "   - 快速視頻切換對系統記憶體的影響？"
echo "   - 隨機分支選擇是否會導致資源競爭？"
echo "   - 複雜情緒關鍵幀是否會出現插值異常？"
echo "   - 長時間運行後系統穩定性如何？"
echo "   - 多重結局選擇的邏輯分支執行效果？"
echo
echo "🎨 創意技藝總結："
echo "   - 敘事結構：從傳統5幕擴展到8幕超級史詩"
echo "   - 元戲劇技法：完整的《伊始之眼》導演誕生記"
echo "   - 互動元素：引入隨機性和時間基分支"
echo "   - 視覺語言：視頻蒙太奇與情緒萬花筒"
echo "   - 音響設計：多層次音頻重疊實驗"
echo "   - 鏡頭語言：複雜軌跡運動與快速切換"
echo "   - 系統測試：從溫和到極限的完整壓力測試"
echo "   - 戲劇深度：主線劇情與元劇情的多層次交織" 