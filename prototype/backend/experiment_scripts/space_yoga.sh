#!/bin/bash

# --- 《太空辣妹瑜伽教室》 ---
# 一部關於失重環境下的搞笑瑜伽教學腳本

BASE_URL="http://localhost:8000"

echo "🧘‍♀️ 《太空辣妹瑜伽教室》 - 開課啦！ 🚀"
echo "風格：零重力下的爆笑瑜伽體驗"
echo

# --- 準備工作 ---
echo "準備工作：打造完美的太空瑜伽環境..."

echo "清空場景，準備太空瑜伽教室..."
curl -X POST "$BASE_URL/api/control/scene-display" \
  -H "Content-Type: application/json" \
  -d '{"displayScene": false}'

echo "設定房間為不可見..."
curl -X POST "$BASE_URL/api/control/room-visibility" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}'
sleep 1

# 設定初始預設鏡位為 overview
echo "設定初始預設鏡位為 overview..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 2.0
  }'
sleep 0.5
echo "初始鏡位設定完成，等待2秒..."
sleep 2

# --- Part 1：懶人開場篇｜"不流汗也能美到升天" (0:00～3:00) ---
echo
echo "=== Part 1：懶人開場篇｜不流汗也能美到升天 ==="
echo "時間：0:00～3:00"
echo

echo "設定太空瑜伽氛圍：輕鬆 BGM，角色準備開始..."
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/space_live_country_theme1.mp3",
    "bgmPlaying": true,
    "loop": true,
    "volume": 0.4
  }'
sleep 0.5
sleep 0.5

echo "太空瑜伽教室開場 - 飛來飛去找不到方向..."
# 設定環境燈光為夜晚神秘效果
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "night"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 0.8}'

# 放大頭部，增加搞笑效果
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 8.0}'

# 放大角色身體，營造誇張效果
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 5.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "ButterflyTwirl",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Happy",
    "loop": true
  }'
sleep 0.5
sleep 0.5

echo "切換至 head_close_up 進行開場致詞..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 2.0
  }'
sleep 0.5
sleep 2

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "欸欸等一下我怎麼飄過頭了啦～！大家好，歡迎來到太空辣妹瑜伽教室！今天要教大家不流汗也能美到升天的秘訣！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 6.0,
    "keyframes": [
      {"tag": "confused", "proportion": 0.0},
      {"tag": "happy", "proportion": 0.4},
      {"tag": "joyful", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 加入太空環境特效
curl -X PUT "$BASE_URL/api/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "/videos/太空直播中.mp4",
    "visible": true,
    "playing": true,
    "volume": 0.4
  }'
sleep 0.5

echo "生成太空瑜伽教室宣傳圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的可愛辣妹瑜伽教練，穿著時尚的瑜伽服，在失重環境中優雅地做瑜伽動作，背景是美麗的星空和地球，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成在太空中做瑜伽的樣子，背景是星空",
    "position": "center-right",
    "size": "large",
    "duration": 8.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

# 加上話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "看看我這個宣傳照！是不是超級專業的太空瑜伽教練～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "proud", "proportion": 0.0},
      {"tag": "confident", "proportion": 1.0}
    ]
  }'
sleep 0.5

# 加上音效
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_01.mp3",
    "volume": 0.1,
    "interrupt": false
  }'
sleep 0.5
sleep 6

echo "示範『宇宙樹』- 樹式但身體浮起來..."
# 調整環境為森林，配合宇宙樹的概念
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "forest"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.2}'

# 頭部變得超級大，強調樹式的重要性
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 12.0}'

# 身體也要跟著放大
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 8.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "Tpose",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "FemaleStandingPose",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Plank",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "現在來示範第一個動作：宇宙樹！就像樹一樣站著，但是要飄起來～看我多優雅！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "confident", "proportion": 0.0},
      {"tag": "smug", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 鏡頭拉出展示全身動作
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 2.0
  }'
sleep 0.5

echo "生成宇宙樹式的概念圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中漂浮的神秘樹木，星雲背景，瑜伽樹式姿勢，夢幻宇宙風格，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "做樹式瑜伽動作，像樹一樣站立，背景是宇宙星雲",
    "position": "center-left",
    "size": "large",
    "duration": 6.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

# 加上話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你們看這個樹式！我就像宇宙中的神秘樹木一樣優雅～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "graceful", "proportion": 0.0},
      {"tag": "serene", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 3

echo "示範『飛天拜日浮空式』..."
# 生成拜日式的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的拜日式瑜伽，金色陽光穿透星雲，優雅的瑜伽姿勢，宇宙日出背景，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "做拜日式瑜伽動作，雙手向上伸展，背景是宇宙日出",
    "position": "top-right",
    "size": "large",
    "duration": 7.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

# 加上話撈子和音效
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "飛天拜日浮空式！感受宇宙日出的能量～這招只有在太空才做得到哦！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "energetic", "proportion": 0.0},
      {"tag": "inspired", "proportion": 1.0}
    ]
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_02.mp3",
    "volume": 0.08,
    "interrupt": false
  }'
sleep 0.5
sleep 2

# 環境變為日出，配合拜日式
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "dawn"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 2.0}'

# 角色放大到最大，展現拜日式的氣勢
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 12.0}'

# 頭部縮小形成對比
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 3.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步1",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "SalsaDancing",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "接下來是飛天拜日浮空式！這是我最新創立的流派，地球上絕對學不到的哦～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "happy", "proportion": 0.0},
      {"tag": "proud", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 5

echo "示範『彈跳旋轉式』- 慢慢轉圈圈進行冥想..."
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "ButterflyTwirl",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0,
    "yaw": 360,
    "roll": 0,
    "fov": 65,
    "duration": 6.0
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "現在進入彈跳旋轉式！跟著我一起轉圈圈，感受宇宙的能量～冥想的時候如果撞到艙壁，就代表你進入更高次元了！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 6.0,
    "keyframes": [
      {"tag": "thoughtful", "proportion": 0.0},
      {"tag": "peaceful", "proportion": 0.5},
      {"tag": "dreamy", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 3

# 加上中間的話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "欸等等我轉得有點暈...這是正常的嗎？還是我的太空艙在轉？",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "confused", "proportion": 0.0},
      {"tag": "dizzy", "proportion": 1.0}
    ]
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_02.mp3",
    "volume": 0.1,
    "interrupt": false
  }'
sleep 0.5
sleep 1

echo "搞笑台詞時間..."
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_01.mp3",
    "volume": 0.15,
    "interrupt": false
  }'
sleep 0.5

echo "瞬間拍攝彈跳旋轉式的連續自拍..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "旋轉瑜伽動作的動態自拍，表情很專注",
    "position": "top-left",
    "size": "large",
    "duration": 4.0
  }'
sleep 0.5
sleep 1

curl -X POST "$BASE_URL/api/continue-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "modification": "換個更開心的表情繼續旋轉",
    "position": "top-right",
    "size": "large",
    "duration": 4.0
  }'
sleep 0.5
sleep 6

echo "切換至 head_close_up 進行搞笑台詞..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 0.5
sleep 1.5

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "再來一招心靈脫軌式，練完會忘記煩惱，甚至忘記自己是誰～哈哈哈！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "mischievous", "proportion": 0.0},
      {"tag": "laughing", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 5

# --- Part 2：進階凹折篇｜"地球做不到但我可以" (3:00～6:00) ---
echo
echo "=== Part 2：進階凹折篇｜地球做不到但我可以 ==="
echo "時間：3:00～6:00"
echo

echo "BGM 切換，增加進階感..."
# 環境調整為倉庫，營造訓練感
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "warehouse"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.5}'

# 頭部放到超級誇張，營造戲劇效果
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 6.0}'

# 角色身體也放大，雙重誇張
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 10.0}'

curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/hihi (1).mp3",
    "bgmPlaying": true,
    "loop": true,
    "volume": 0.5
  }'
sleep 0.5
sleep 1

echo "示範『無脊椎式下犬式』- 背後彎到快折起來..."
# 生成無脊椎式下犬式的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的下犬式瑜伽，身體如液體般彎曲，無重力環境，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "做下犬式瑜伽動作，身體極度彎曲像液體一樣，背景是太空",
    "position": "bottom-left",
    "size": "large",
    "duration": 6.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

# 加上話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "看我這個無脊椎式下犬式！身體軟得像果凍一樣～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "playful", "proportion": 0.0},
      {"tag": "flexible", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 2

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "運動1",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Breakdance1990",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "現在進入進階課程！這是無脊椎式下犬式，地球上會受傷，但在這裡可以隨便拗！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "confident", "proportion": 0.0},
      {"tag": "focused", "proportion": 0.5},
      {"tag": "determined", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 2

# 加上進階課程的話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "大家不要在家裡試哦～除非你家也在太空中！哈哈哈～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "warning", "proportion": 0.0},
      {"tag": "laughing", "proportion": 1.0}
    ]
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_01.mp3",
    "volume": 0.09,
    "interrupt": false
  }'
sleep 0.5
sleep 1

# 鏡頭特效強化動作
curl -X POST "$BASE_URL/api/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 45,
    "yaw": -20,
    "roll": 15,
    "fov": 55,
    "duration": 3.0
  }'
sleep 0.5

echo "生成進階瑜伽動作示範圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的辣妹做極限瑜伽動作，身體呈現不可思議的彎曲角度，周圍有星雲和太空站，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "做極限瑜伽動作，身體彎曲到不可思議的角度，背景是星雲和太空站",
    "position": "top-right",
    "size": "large",
    "duration": 5.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

# 加上話撈子和音效
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "這個極限動作只有我做得到！地球人看了會嚇死～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "proud", "proportion": 0.0},
      {"tag": "smug", "proportion": 1.0}
    ]
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_01.mp3",
    "volume": 0.12,
    "interrupt": false
  }'
sleep 0.5
sleep 5

echo "示範『太空勇士式』- 正常的勇士式但會亂飄..."
# 生成太空勇士式的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的勇士式瑜伽，超級英雄般的姿勢，星際背景，力量感十足，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "做勇士式瑜伽動作，像超級英雄一樣威武，背景是星際太空",
    "position": "center",
    "size": "large",
    "duration": 8.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

# 加上話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "太空勇士式！我就是宇宙中最威武的瑜伽戰士～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "heroic", "proportion": 0.0},
      {"tag": "powerful", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 2

# 環境變為夕陽，營造英雄感
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "sunset"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.8}'

# 頭部調到中等，但角色放大成超級英雄氣勢
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 6.0}'
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 15.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "運動2",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "JazzDancing",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "接下來是太空勇士式！看似正常的勇士式，但是會在空間中亂飄～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "heroic", "proportion": 0.0},
      {"tag": "confident", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 2.0
  }'
sleep 0.5
sleep 4

echo "示範『螺旋章魚式』- 整個人像章魚捲起來..."
# 生成螺旋章魚式的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的螺旋章魚式瑜伽，身體像章魚般扭曲，夢幻海洋風格，無重力環境，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "身體像章魚一樣螺旋扭曲，做超級柔軟的瑜伽動作，背景是夢幻太空",
    "position": "top-left",
    "size": "large",
    "duration": 7.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

# 加上話撈子和音效
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "螺旋章魚式！我的身體比章魚還軟～這樣扭不會痛嗎？不會啊因為我在太空！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "playful", "proportion": 0.0},
      {"tag": "silly", "proportion": 0.5},
      {"tag": "carefree", "proportion": 1.0}
    ]
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_02.mp3",
    "volume": 0.1,
    "interrupt": false
  }'
sleep 0.5
sleep 2

curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "twistdance",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "現在要示範螺旋章魚式！我好像水管！這招不要在地球學，會GG！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "playful", "proportion": 0.0},
      {"tag": "silly", "proportion": 0.6},
      {"tag": "laughing", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 搞笑音效
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_02.mp3",
    "volume": 0.12,
    "interrupt": false
  }'
sleep 0.5
sleep 5

echo "搞笑解說台詞..."
# 監視器顯示相關瑜伽圖片
curl -X PUT "$BASE_URL/api/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "/videos/模擬星雲圖.mp4",
    "visible": true,
    "playing": true,
    "volume": 0.2
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 0.5
sleep 1.5

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你們看看～這個叫做太空章魚辣妹式，練完保證你的感情也能轉個彎！什麼意思？我也不知道啦～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "mischievous", "proportion": 0.0},
      {"tag": "confused", "proportion": 0.5},
      {"tag": "giggling", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 6

# --- Part 3：互動爆笑篇｜"觀眾點動作我來解釋" (6:00～9:00) ---
echo
echo "=== Part 3：互動爆笑篇｜觀眾點動作我來解釋 ==="
echo "時間：6:00～9:00"
echo

echo "監視器切換到更有趣的內容..."
curl -X PUT "$BASE_URL/api/monitors/screen2" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "/videos/火箭發射.mp4",
    "message_type": "chat-message",
    "visible": true,
    "playing": true,
    "volume": 0.6
  }'
sleep 0.5

echo "同時在 screen1 播放太空瑜伽影片..."
curl -X PUT "$BASE_URL/api/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "/videos/太空瑜伽.mp4",
    
    "visible": true,
    "playing": true,
    "volume": 0.3
  }'
sleep 0.5
sleep 1

echo "互動環節開始..."
# 切換到更活潑的鄉村音樂
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/space_live_country_theme2.mp3",
    "bgmPlaying": true,
    "loop": true,
    "volume": 0.6
  }'
sleep 0.5
sleep 1

# 生成互動瑜伽教室的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空瑜伽教室互動場景，觀眾留言飄浮在空中，熱鬧的直播氛圍，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "在太空瑜伽教室中與觀眾互動，周圍有飄浮的留言，表情很興奮",
    "position": "center-right",
    "size": "large",
    "duration": 6.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

# 加上話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "看看我的互動教室！觀眾的留言都在太空中飄來飄去～好有趣！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "excited", "proportion": 0.0},
      {"tag": "joyful", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 2

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "現在進入互動時間！觀眾可以留言要求：請示範某某動作！我會即興表演給大家看～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "excited", "proportion": 0.0},
      {"tag": "energetic", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 5

echo "即興表演 - 縮成一顆球漂來漂去..."
# 生成球體瑜伽的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的球體瑜伽，人體縮成完美球形，在宇宙中漂浮，可愛搞笑風格，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "縮成一個完美的球形，像球一樣在太空中漂浮，表情很搞笑",
    "position": "bottom-right",
    "size": "large",
    "duration": 6.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

# 加上話撈子和音效
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "球體瑜伽！我變成一顆超級可愛的太空球～滾來滾去～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "silly", "proportion": 0.0},
      {"tag": "giggly", "proportion": 1.0}
    ]
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_01.mp3",
    "volume": 0.08,
    "interrupt": false
  }'
sleep 0.5
sleep 2

# 環境變為城市，配合互動環節
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "city"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.0}'

# 頭部放到極限，營造超級搞笑球體效果
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 8.0}'

# 角色身體縮到最小形成對比
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 3.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "不穩",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "HipHopDancin",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "欸欸欸～這個我最會了！看我變成一顆球在太空中漂來漂去～這是宇宙球體冥想法！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "playful", "proportion": 0.0},
      {"tag": "joyful", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 鏡頭圍繞旋轉
curl -X POST "$BASE_URL/api/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0,
    "yaw": 180,
    "roll": 0,
    "fov": 70,
    "duration": 5.0
  }'
sleep 0.5

echo "拍一張球體瑜伽的搞笑自拍..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "搞笑的球體瑜伽姿勢自拍，表情很驚訝",
    "position": "bottom-left",
    "size": "large",
    "duration": 5.0
  }'
sleep 0.5
sleep 6

echo "模仿狗狗瑜伽..."
# 生成狗狗瑜伽的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的狗狗瑜伽，可愛的太空狗狗做下犬式，星空背景，萌系風格",
    "position": "center-left",
    "size": "large",
    "duration": 5.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5
sleep 2

# 調整比例，營造狗狗的可愛感
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 5.0}'
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 4.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮2",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "CanCan",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "有人要看狗狗瑜伽嗎？汪汪～這是太空狗狗下犬式！比地球上的狗狗更飄逸～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "silly", "proportion": 0.0},
      {"tag": "playful", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 5

echo "外星人拜日式..."
# 環境變為太空風格
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "night"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 0.5}'

# 調整成外星人的超級怪異比例
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 7.0}'
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 5.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "飛1",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Moonwalk",
    "loop": true
  }'
sleep 0.5

echo "生成外星人瑜伽概念圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "可愛的綠色小外星人在太空中做瑜伽，旁邊有UFO和星球，畫風可愛幽默",
    "position": "top-right",
    "size": "large",
    "duration": 6.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "接下來是外星人拜日式！據說這是我從路過的外星人那裡學來的獨門秘技～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "mysterious", "proportion": 0.0},
      {"tag": "confident", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 5

echo "特別橋段 - 亂做姿勢然後說這是宇宙交配式..."
# 生成宇宙交配式的概念圖（搞笑版）
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "搞笑的宇宙瑜伽動作，奇怪的姿勢在太空中飄浮，幽默風格",
    "position": "bottom-left",
    "size": "large",
    "duration": 5.0,
    "aspect_ratio": "square"
  }'
sleep 0.5
sleep 2

# 環境調整為公園，營造自然感
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "park"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.3}'

# 回到比較正常的比例，但還是很誇張
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 10.0}'
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 7.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步3",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "JazzDancing",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "最後這個動作是...呃...宇宙交配式！不要問我為什麼叫這個名字，總之就是很厲害的樣子～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "embarrassed", "proportion": 0.0},
      {"tag": "mischievous", "proportion": 0.5},
      {"tag": "giggling", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 加強失重混亂感的視覺效果
curl -X POST "$BASE_URL/api/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 30,
    "yaw": -45,
    "roll": 20,
    "fov": 80,
    "duration": 3.0
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/songs-file/winds_blowing.mp3",
    "volume": 0.3,
    "loop": true
  }'
sleep 0.5
sleep 6

# --- Part 4：收尾｜靈魂歸位式｜"辣妹宇宙收心操" (9:00～10:00) ---
echo
echo "=== Part 4：收尾｜靈魂歸位式｜辣妹宇宙收心操 ==="
echo "時間：9:00～10:00"
echo

echo "停止風聲，準備進入收尾..."
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/songs-file/winds_blowing.mp3",
    "loop": false,
    "interrupt": true
  }'
sleep 0.5
sleep 0.5

echo "監視器切換到黑洞，營造深度冥想氛圍..."
curl -X PUT "$BASE_URL/api/monitors/screen1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "/videos/黑洞.mp4",
    
    "visible": true,
    "playing": true,
    "volume": 0.3
  }'
sleep 0.5
sleep 1

echo "假裝進入深度冥想（實際在打瞌睡）..."
# 切換到溫和的hihi音樂
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/hihi (2).mp3",
    "bgmPlaying": true,
    "loop": true,
    "volume": 0.3
  }'
sleep 0.5
sleep 1

# 生成深度冥想的概念圖
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "太空中的深度冥想，靈魂歸位，寧靜的宇宙背景，禪意風格",
    "position": "center",
    "size": "large",
    "duration": 8.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5
sleep 2

curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "FemaleStandingPose",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "好啦～現在進入最後的靈魂歸位式，要引導靈魂回艙體...zzz...呃我是說，深度冥想中...",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "peaceful", "proportion": 0.0},
      {"tag": "sleepy", "proportion": 0.6},
      {"tag": "dreamy", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 鏡頭慢慢拉遠
curl -X POST "$BASE_URL/api/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0,
    "yaw": 0,
    "roll": 0,
    "fov": 90,
    "duration": 4.0
  }'
sleep 0.5
sleep 6

echo "假裝飄出畫面..."
# 角色位置向上飄移
curl -X POST "$BASE_URL/api/control/character/position" \
  -H "Content-Type: application/json" \
  -d '{"position": [0, 2.0, 0]}'

# 頭部縮到最小模擬距離感
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "飛2",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "ButterflyTwirl",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Moonwalk",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Flair",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "咦？我怎麼飄出畫面了？等等等等～回來啦～",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 3.0,
    "keyframes": [
      {"tag": "confused", "proportion": 0.0},
      {"tag": "panicked", "proportion": 0.7},
      {"tag": "embarrassed", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 4

echo "最終結尾台詞..."
# 角色回到正常位置
curl -X POST "$BASE_URL/api/control/character/position" \
  -H "Content-Type: application/json" \
  -d '{"position": [0, 0, 0]}'

# 頭部放大，強調結尾感謝
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 12.0}'

curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 2.0
  }'
sleep 0.5

echo "拍一張課程結束的感謝自拍..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "課程結束的感謝自拍，表情很開心很滿足，photoreal風格",
    "reference_image": "截圖 2025-06-16 下午1.35.01.png",
    "modification": "課程結束後很開心很滿足的表情，比讚手勢，背景是太空",
    "position": "bottom-right",
    "size": "large",
    "duration": 8.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

# 加上結尾話撈子
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "來拍張結尾自拍！大家有沒有學會太空瑜伽呀～記得按讚訂閱開小鈴鐺哦！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "happy", "proportion": 0.0},
      {"tag": "grateful", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 2

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "划手機",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Cheering",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "StandingClap",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "SalsaDancing",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "好啦！今天的太空辣妹瑜伽教室就到這裡～看我這麼可愛又火辣的直播是不是要來點抖內呀～好想吃熱熱的台中控肉飯哦！",
    "message_type": "chat-message"
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 6.0,
    "keyframes": [
      {"tag": "happy", "proportion": 0.0},
      {"tag": "hopeful", "proportion": 0.4},
      {"tag": "dreamy", "proportion": 1.0}
    ]
  }'
sleep 0.5
sleep 1

# 最終效果
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/Energetic_fast_pace.mp3",
    "volume": 0.3,
    "interrupt": false
  }'
sleep 0.5
sleep 7

echo "設定最終預設鏡位為 overview..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 3.0
  }'
sleep 0.5
sleep 3

echo "回歸平靜..."
# 環境回歸溫和的工作室燈光
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "studio"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.0}'

# 所有比例回歸正常
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 1.0}'

# 角色位置重置
curl -X POST "$BASE_URL/api/control/character/reset-transform" \
  -H "Content-Type: application/json" \
  -d '{
    "reset_position": true,
    "reset_rotation": true,
    "reset_scale": true
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "臥躺",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Idle",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "Namaste",
    "loop": true
  }'
sleep 0.5
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmPlaying": false
  }'
sleep 0.5
sleep 2

echo
echo "🧘‍♀️ 《太空辣妹瑜伽教室》 - 下課啦！感謝收看！ 🚀" 