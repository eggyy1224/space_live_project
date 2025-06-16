#!/bin/bash

# --- 《太空辣妹瑜伽教室 2.0》 ---
# 重新建構版本 - 一步步確認每個環節

BASE_URL="http://localhost:8000"

echo "🧘‍♀️ 《太空辣妹瑜伽教室 2.0》 - 重新開課！ 🚀"
echo "風格：簡潔版太空瑜伽體驗"
echo

# --- 基礎準備工作 ---
echo "=== 基礎準備工作 ==="

echo "1. 清空場景..."
curl -X POST "$BASE_URL/api/control/scene-display" \
  -H "Content-Type: application/json" \
  -d '{"displayScene": false}'
sleep 0.5

echo "2. 設定房間為不可見..."
curl -X POST "$BASE_URL/api/control/room-visibility" \
  -H "Content-Type: application/json" \
  -d '{"visible": false}'
sleep 0.5

echo "3. 設定初始鏡位為 overview..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 2.0
  }'
sleep 2.5

echo "準備工作完成！"

echo "準備完成. 播放準備音效..."
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/taiwan_variety_sfx_01.mp3"
  }'
sleep 0.5

echo "準備完成. 生成課程準備完成圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "日系kawaii風格融合西方動畫特色，可愛角色帶有粗線條輪廓和誇張表情做瑜伽準備，鮮豔色彩搭配科幻元素，太空背景有趣味外星生物和未來裝置，fusion anime風格，幽默可愛",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成日系kawaii融合西方動畫風格的角色，可愛但帶有粗線條誇張表情，科幻太空背景有趣味外星生物",
    "position": "top-left",
    "size": "large",
    "duration": 35.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "同時顯示現有的太空瑜伽素材圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750058069945.png",
    "caption": "太空瑜伽經典動作示範 - 漂浮冥想式",
    "position": "bottom-left",
    "size": "medium",
    "duration": 30.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "顯示更多最新瑜伽素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750060719556.png",
    "caption": "最新太空瑜伽動作 - 銀色太空服展示",
    "position": "top-left",
    "size": "small",
    "duration": 25.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增最新生成的瑜伽素材1..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750061437567.png",
    "caption": "最新生成 - 太空瑜伽準備動作",
    "custom_position": {"top": "8%", "left": "5%"},
    "size": "small",
    "duration": 32.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增最新生成的瑜伽素材2..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750067626459.png",
    "caption": "最新生成 - 銀色太空服瑜伽展示",
    "custom_position": {"top": "12%", "left": "15%"},
    "size": "medium",
    "duration": 35.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增超可愛日系卡通風格瑜伽素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750055046076.png",
    "caption": "超可愛日系卡通風格 - 綠色外星人瑜伽冥想",
    "custom_position": {"top": "18%", "left": "30%"},
    "size": "medium",
    "duration": 38.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增最新生成瑜伽素材15..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072640546.png",
    "caption": "最新生成 - Rick and Morty風格太空瑜伽",
    "custom_position": {"top": "22%", "left": "35%"},
    "size": "small",
    "duration": 33.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增最新生成瑜伽素材16..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072701462.png",
    "caption": "最新生成 - 美漫風格瑜伽展示",
    "custom_position": {"bottom": "18%", "left": "32%"},
    "size": "medium",
    "duration": 36.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片17..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749308648698.png",
    "caption": "經典太空瑜伽場景 - 復古風格",
    "custom_position": {"top": "25%", "left": "40%"},
    "size": "small",
    "duration": 30.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750060708099.png",
    "caption": "進階太空瑜伽姿勢",
    "position": "bottom-left",
    "size": "small",
    "duration": 28.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "顯示經典太空瑜伽圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749886152603.png",
    "caption": "經典太空瑜伽場景",
    "custom_position": {"top": "15%", "left": "20%"},
    "size": "medium",
    "duration": 32.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749309486954.png",
    "caption": "太空瑜伽環境設置",
    "custom_position": {"bottom": "20%", "left": "25%"},
    "size": "small",
    "duration": 26.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo

# --- 開場環節 ---
echo "=== 開場環節 ==="

echo "4. 播放太空瑜伽主題曲..."
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmUrl": "/audio/BGM/space_live_country_theme1.mp3",
    "bgmPlaying": true,
    "loop": true,
    "volume": 0.5
  }'
sleep 0.5

echo "5. 播放太空環境音效..."
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_01.mp3",
    "volume": 0.1,
    "interrupt": false
  }'
sleep 0.5

echo "6. 設定太空瑜伽環境..."
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "studio"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.5}'
sleep 0.5

echo "7. 切換到特寫鏡頭..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 0.5

echo "7a. 放大頭部到最大..."
# 播放頭部放大音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/測試音效4.mp3"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 20.0}'
sleep 1.0

echo "7b. 調整角色體型 - 瑜伽辣妹身材..."
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.3,
      "錯置": 0.1,
      "錯置.001": 0.2
    }
  }'
sleep 0.5

echo "8. 角色開始漂浮（頭內動作）..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮",
    "loop": true
  }'
sleep 1.0

echo "8-1. 先做個Tpose展示太空服..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "Tpose",
    "loop": false
  }'
sleep 2.0

echo "8-2. 回到漂浮狀態..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮",
    "loop": true
  }'
sleep 1.0

echo "8a. 切換到運動2動作..."
# 播放運動準備音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/Energetic_fast_pace.mp3"
  }'
sleep 0.5

# 角色放大增加視覺衝擊力
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 3.0}'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "運動2",
    "loop": true
  }'
sleep 0.5

echo "8a1. 切換到head_close_up觀察運動動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

echo "8b. 生成運動2動作特寫圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "kawaii風格混合歐美卡通特色，可愛角色帶有明顯輪廓線做運動2瑜伽動作，專注表情帶有幽默感，頭部特寫，背景有科幻實驗室和創意裝置，fusion動畫風格，可愛搞笑",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成kawaii融合歐美卡通風格的角色，做運動2瑜伽動作時可愛但帶有幽默專注表情，背景有科幻實驗室裝置",
    "position": "bottom-left",
    "size": "large",
    "duration": 40.0,
    "aspect_ratio": "square"
  }'
sleep 1.0

echo "9. 生成太空瑜伽教室開場圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "日系可愛風格結合西方科幻動畫，瑜伽教練角色在多維度太空中優雅漂浮，大眼睛帶有幽默神情，簡潔但有個性的造型，背景有奇異行星和未來飛行器，fusion sci-fi風格，趣味科幻",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成日系可愛融合西方科幻動畫風格的瑜伽教練，在多維度太空中漂浮，大眼睛帶有幽默神情，背景有奇異行星和未來飛行器",
    "position": "bottom-left",
    "size": "large",
    "duration": 45.0,
    "aspect_ratio": "landscape"
  }'
sleep 1.0

echo "顯示現有太空瑜伽開場素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750058063112.png",
    "caption": "太空瑜伽教室 - 開課前的準備動作",
    "position": "bottom-left",
    "size": "medium",
    "duration": 35.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增開場瑜伽素材3..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750067681327.png",
    "caption": "最新生成 - 開場動作展示",
    "custom_position": {"top": "25%", "left": "12%"},
    "size": "small",
    "duration": 38.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增開場瑜伽素材4..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750067857336.png",
    "caption": "最新生成 - 太空環境適應動作",
    "custom_position": {"bottom": "15%", "left": "22%"},
    "size": "medium",
    "duration": 40.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增fusion風格瑜伽素材18..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072732272.png",
    "caption": "最新生成 - Fusion風格太空瑜伽動作",
    "custom_position": {"top": "28%", "left": "45%"},
    "size": "small",
    "duration": 34.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增創意風格瑜伽素材19..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072738849.png",
    "caption": "最新生成 - 創意科幻瑜伽展示",
    "custom_position": {"bottom": "22%", "left": "38%"},
    "size": "medium",
    "duration": 37.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片20..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749308744864.png",
    "caption": "經典太空瑜伽場景 - 復古科幻風格",
    "custom_position": {"top": "32%", "left": "50%"},
    "size": "small",
    "duration": 31.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "9a. 播放開場音效..."
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/taiwan_variety_sfx_02.mp3"
  }'
sleep 0.5

echo "10. 開場致詞..."
curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "哈囉大家好！歡迎來到太空辣妹瑜伽教室 2.0！看看我的太空瑜伽裝備，今天我們要在零重力環境下體驗全新的瑜伽感受～",
    "message_type": "chat-message"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "happy", "proportion": 0.0},
      {"tag": "excited", "proportion": 0.4},
      {"tag": "confident", "proportion": 0.7},
      {"tag": "joyful", "proportion": 1.0}
    ]
  }'
sleep 5.5

echo "開場環節完成！"
echo

# --- 基礎瑜伽動作示範 ---
echo "=== 基礎瑜伽動作示範 ==="

echo "11. 切換到全景觀察動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 1.5
  }'
sleep 0.5

echo "11a. 調整頭部為正常大小..."
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'
sleep 1.0

echo "12. 設定樹式環境..."
# 播放環境切換音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/測試音效5.mp3"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "forest"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.8}'
sleep 0.5

echo "12a. 示範動作一：太空樹式..."
# 播放樹式音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/Ambient_keyboard_cli_2.mp3"
  }'
sleep 0.5

# 調整體型為優雅樹式身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.2,
      "錯置": 0.05,
      "錯置.001": 0.15
    }
  }'
sleep 0.5

# 角色縮小營造精緻感
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 1.5}'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "運動1",
    "loop": true
  }'
sleep 1.5

echo "12a-1. 展示不穩平衡練習..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "不穩",
    "loop": true
  }'
sleep 2.0

echo "12a-2. 回到運動1穩定樹式..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "運動1",
    "loop": true
  }'
sleep 0.5

echo "12a1. 切換到head_close_up觀察樹式動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "FemaleStandingPose",
    "loop": true
  }'
sleep 0.5

echo "12b. 生成森林瑜伽環境圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "kawaii風格融合西方科幻動畫，角色在奇幻森林環境中做瑜伽，大眼睛帶有幽默享受表情，簡潔但富有個性的造型，背景有未來樹木和科幻生物，fusion nature風格，趣味環保",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成kawaii融合西方科幻動畫風格的角色，在奇幻森林中，大眼睛帶有幽默享受表情，背景有未來樹木和科幻生物",
    "position": "bottom-left",
    "size": "large",
    "duration": 32.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "13. 生成太空樹式示範圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "日系可愛風格混合歐美動畫特色，角色做樹式瑜伽姿勢單腳站立優雅平衡，大眼睛專注帶有幽默感，簡潔但有特色的造型，背景有多維度星雲和奇異行星，fusion balance風格，禪意科幻",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成日系可愛混合歐美動畫風格的角色，做樹式瑜伽時大眼睛專注帶有幽默感，背景有多維度星雲和奇異行星",
    "position": "bottom-left",
    "size": "large",
    "duration": 42.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "顯示現有樹式瑜伽素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750058055136.png",
    "caption": "太空樹式瑜伽 - 平衡與專注的藝術",
    "position": "top-left",
    "size": "medium",
    "duration": 38.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "再顯示另一個樹式變化..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750058047193.png",
    "caption": "進階樹式 - 太空中的優雅平衡",
    "position": "bottom-left",
    "size": "small",
    "duration": 32.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增樹式瑜伽素材5..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750067885608.png",
    "caption": "最新生成 - 森林環境樹式瑜伽",
    "custom_position": {"top": "35%", "left": "18%"},
    "size": "small",
    "duration": 36.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增樹式瑜伽素材6..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750067914496.png",
    "caption": "最新生成 - 平衡與專注練習",
    "custom_position": {"bottom": "25%", "left": "28%"},
    "size": "medium",
    "duration": 42.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增fusion樹式瑜伽素材21..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072762920.png",
    "caption": "最新生成 - Fusion風格樹式平衡",
    "custom_position": {"top": "38%", "left": "55%"},
    "size": "small",
    "duration": 35.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增創意樹式瑜伽素材22..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072786307.png",
    "caption": "最新生成 - 創意科幻樹式動作",
    "custom_position": {"bottom": "30%", "left": "48%"},
    "size": "medium",
    "duration": 38.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片23..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749309547128.png",
    "caption": "經典太空瑜伽場景 - 樹式專精",
    "custom_position": {"top": "42%", "left": "60%"},
    "size": "small",
    "duration": 33.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "展示最新樹式瑜伽變化..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750060697924.png",
    "caption": "最新樹式動作 - 銀色反光太空服",
    "position": "bottom-left",
    "size": "medium",
    "duration": 35.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750060671699.png",
    "caption": "優雅樹式展示",
    "position": "top-left",
    "size": "small",
    "duration": 30.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "展示更多樹式瑜伽圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749308930234.png",
    "caption": "太空樹式瑜伽經典",
    "custom_position": {"bottom": "30%", "left": "15%"},
    "size": "medium",
    "duration": 34.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054319106.png",
    "caption": "完美樹式平衡",
    "custom_position": {"top": "25%", "left": "12%"},
    "size": "small",
    "duration": 31.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "第一個動作是太空樹式！就像樹一樣挺立，但我們會在空中漂浮～看看這個示範圖，感受宇宙的能量！",
    "message_type": "chat-message"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 4.0,
    "keyframes": [
      {"tag": "confident", "proportion": 0.0},
      {"tag": "graceful", "proportion": 0.5},
      {"tag": "peaceful", "proportion": 1.0}
    ]
  }'
sleep 4.5

echo "14. 切換到特寫表情..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 0.5

echo "14a. 放大頭部到最大，準備看頭內動作..."
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 20.0}'
sleep 1.0

echo "15. 設定冥想環境..."
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "dawn"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 1.2}'
sleep 0.5

echo "15a. 示範動作二：漂浮冥想（頭內動作）..."
# 播放冥想氛圍音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/winds_blowing.mp3"
  }'
sleep 0.5

# 調整體型為冥想專注身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.4,
      "錯置": 0.2,
      "錯置.001": 0.1
    }
  }'
sleep 0.5

# 角色放大突出冥想氣勢
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 2.8}'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "不穩",
    "loop": true
  }'
sleep 1.0

echo "15a. 切換到Tpose冥想..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "Tpose",
    "loop": true
  }'
sleep 1.5

echo "15b. 最後切換到漂浮2..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮2",
    "loop": true
  }'
sleep 1.5

echo "15b-1. 展示划手機放鬆冥想..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "划手機",
    "loop": true
  }'
sleep 2.0

echo "15b-2. 進入臥躺深度冥想..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "臥躺",
    "loop": true
  }'
sleep 2.5

echo "15b-3. 回到漂浮2結束冥想..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮2",
    "loop": true
  }'
sleep 0.5

echo "15c. 生成黎明冥想氛圍圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色在鮮豔黎明中冥想，雙手合十坐姿，超大圓圓黑眼睛閉著很寧靜，簡潔卡通造型，背景有粉色橙色漸層天空和彩色雲朵，kawaii anime風格，明亮色彩",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，在鮮豔黎明中冥想，超大圓圓眼睛閉著很寧靜，背景有粉色橙色天空和彩色雲朵",
    "position": "top-left",
    "size": "large",
    "duration": 38.0,
    "aspect_ratio": "portrait"
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

echo "16. 播放冥想音效..."
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/spaceship_ambience_02.mp3",
    "volume": 0.08,
    "interrupt": false
  }'
sleep 0.5

echo "17. 生成漂浮冥想示範圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色深度冥想漂浮姿勢，雙手合十蓮花坐，超大圓圓黑眼睛閉著很平靜，簡潔卡通造型，背景有鮮豔太空和閃亮星星，kawaii anime風格，zen cute",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，做冥想姿勢雙手合十，超大圓圓眼睛閉著很平靜，背景有鮮豔太空和閃亮星星",
    "position": "bottom-left",
    "size": "large",
    "duration": 36.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "顯示現有冥想瑜伽素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750058024567.png",
    "caption": "太空冥想 - 內心平靜的力量",
    "position": "top-left",
    "size": "medium",
    "duration": 34.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "顯示另一個冥想姿勢..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750058018528.png",
    "caption": "深度冥想 - 與宇宙合一",
    "position": "bottom-left",
    "size": "small",
    "duration": 30.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "展示更多冥想變化..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750060635753.png",
    "caption": "最新冥想姿勢 - 太空禪境",
    "position": "top-left",
    "size": "medium",
    "duration": 33.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059913591.png",
    "caption": "進階冥想 - 銀色太空服冥想式",
    "position": "top-left",
    "size": "small",
    "duration": 31.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "展示冥想瑜伽專題圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054386116.png",
    "caption": "太空冥想大師級表現",
    "custom_position": {"bottom": "15%", "left": "8%"},
    "size": "medium",
    "duration": 35.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054059551.png",
    "caption": "深度冥想境界",
    "custom_position": {"bottom": "25%", "left": "5%"},
    "size": "small",
    "duration": 32.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增冥想瑜伽素材7..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068006321.png",
    "caption": "最新生成 - 黎明冥想體驗",
    "custom_position": {"top": "45%", "left": "25%"},
    "size": "small",
    "duration": 44.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增冥想瑜伽素材8..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068020605.png",
    "caption": "最新生成 - 漂浮冥想深度練習",
    "custom_position": {"bottom": "35%", "left": "35%"},
    "size": "medium",
    "duration": 46.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增fusion冥想瑜伽素材24..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072798784.png",
    "caption": "最新生成 - Fusion風格冥想體驗",
    "custom_position": {"top": "48%", "left": "65%"},
    "size": "small",
    "duration": 40.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增創意冥想瑜伽素材25..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072816527.png",
    "caption": "最新生成 - 創意科幻冥想姿勢",
    "custom_position": {"bottom": "40%", "left": "58%"},
    "size": "medium",
    "duration": 43.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片26..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749375871063.png",
    "caption": "經典太空瑜伽場景 - 冥想專精",
    "custom_position": {"top": "52%", "left": "70%"},
    "size": "small",
    "duration": 36.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "接下來是漂浮冥想！閉上眼睛，讓身體在太空中自由漂浮，感受內心的平靜～聽到太空的聲音了嗎？",
    "message_type": "chat-message"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "calm", "proportion": 0.0},
      {"tag": "serene", "proportion": 0.4},
      {"tag": "peaceful", "proportion": 0.7},
      {"tag": "dreamy", "proportion": 1.0}
    ]
  }'
sleep 5.5

echo "18. 切換到全景看旋轉動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 1.5
  }'
sleep 0.5

echo "18a. 調整頭部為正常大小..."
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'
sleep 0.5

echo "18a1. 角色放大準備旋轉表演..."
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 4.5}'
sleep 1.0

echo "19. 設定旋轉環境..."
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "sunset"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 2.0}'
sleep 0.5

echo "19a. 示範動作三：太空旋轉..."
# 播放旋轉音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/taiwan_variety_sfx_03.mp3"
  }'
sleep 0.5

# 調整體型為動感旋轉身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.6,
      "錯置": 0.3,
      "錯置.001": 0.25
    }
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步1",
    "loop": true
  }'
sleep 0.5

echo "19a1. 切換到head_close_up觀察旋轉動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

curl -X POST "$BASE_URL/api/control/body-animation" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "play",
    "animation": "ButterflyTwirl",
    "loop": true
  }'
sleep 0.5

echo "19b. 生成夕陽旋轉動態圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色在鮮豔夕陽中旋轉瑜伽，雙臂展開旋轉動作，超大圓圓黑眼睛很享受，簡潔卡通造型，背景有橙色粉色漸層天空和彩色雲朵，kawaii anime風格，動態感",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，在鮮豔夕陽中旋轉，超大圓圓眼睛很享受，背景有橙色粉色天空和彩色雲朵",
    "position": "center",
    "size": "large",
    "duration": 44.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/camera/transition" \
  -H "Content-Type: application/json" \
  -d '{
    "pitch": 0,
    "yaw": 360,
    "roll": 0,
    "fov": 65,
    "duration": 5.0
  }'
sleep 0.5

echo "20. 生成太空旋轉示範圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色在鮮豔星雲中優雅旋轉瑜伽，像芭蕾舞者一樣優美，超大圓圓黑眼睛很專注，簡潔卡通造型，背景有彩色螺旋星雲和閃亮星星，kawaii anime風格，優雅動態",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，在鮮豔星雲中優雅旋轉像芭蕾舞者，超大圓圓眼睛很專注，背景有彩色螺旋星雲和星星",
    "position": "bottom-center",
    "size": "large",
    "duration": 33.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "顯示現有旋轉瑜伽素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057999248.png",
    "caption": "太空旋轉瑜伽 - 動態平衡的美學",
    "position": "top-left",
    "size": "medium",
    "duration": 35.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增旋轉瑜伽素材9..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068093909.png",
    "caption": "最新生成 - 夕陽旋轉動態美學",
    "custom_position": {"top": "55%", "left": "32%"},
    "size": "small",
    "duration": 38.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增旋轉瑜伽素材10..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068144409.png",
    "caption": "最新生成 - 太空舞步旋轉技巧",
    "custom_position": {"bottom": "45%", "left": "42%"},
    "size": "medium",
    "duration": 41.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增fusion旋轉瑜伽素材27..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072860762.png",
    "caption": "最新生成 - Fusion風格旋轉動態",
    "custom_position": {"top": "58%", "left": "75%"},
    "size": "small",
    "duration": 37.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片28..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749640206818.png",
    "caption": "經典太空瑜伽場景 - 旋轉專精",
    "custom_position": {"bottom": "50%", "left": "68%"},
    "size": "medium",
    "duration": 39.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增創意旋轉瑜伽素材29..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750072696084.png",
    "caption": "最新生成 - 創意科幻旋轉技巧",
    "custom_position": {"top": "62%", "left": "80%"},
    "size": "small",
    "duration": 35.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "顯示舞蹈式旋轉..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057992216.png",
    "caption": "舞蹈式旋轉 - 太空中的優雅舞步",
    "position": "top-left",
    "size": "small",
    "duration": 31.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "展示更多旋轉動作..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750060580400.png",
    "caption": "最新旋轉瑜伽 - 銀色太空服旋轉",
    "position": "bottom-left",
    "size": "medium",
    "duration": 37.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059904840.png",
    "caption": "華麗旋轉動作展示",
    "position": "top-left",
    "size": "small",
    "duration": 35.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "展示旋轉瑜伽藝術圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1750051949438.png",
    "caption": "太空旋轉瑜伽藝術",
    "custom_position": {"top": "40%", "left": "10%"},
    "size": "medium",
    "duration": 38.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1750051935537.png",
    "caption": "優雅旋轉姿態",
    "custom_position": {"bottom": "35%", "left": "18%"},
    "size": "small",
    "duration": 36.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "最後是太空旋轉！慢慢地轉圈圈，讓宇宙的能量在身體裡流動～看看這個旋轉示範，是不是很優雅？",
    "message_type": "chat-message"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "dreamy", "proportion": 0.0},
      {"tag": "graceful", "proportion": 0.4},
      {"tag": "elegant", "proportion": 0.7},
      {"tag": "joyful", "proportion": 1.0}
    ]
  }'
sleep 5.5

echo "基礎動作示範完成！"

echo "總結. 生成三個動作總結圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色完成太空瑜伽三個基礎動作，雙手比勝利手勢，超大圓圓黑眼睛閃閃發光滿滿成就感，簡潔卡通造型，背景有彩色慶祝煙火和閃亮星星，kawaii anime風格，victory pose",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，完成三個基礎動作後超大圓圓眼睛閃閃發光很滿足，雙手比勝利手勢，背景有彩色慶祝煙火",
    "position": "center-left",
    "size": "large",
    "duration": 47.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "顯示課程總結素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057950582.png",
    "caption": "太空瑜伽課程總結 - 完美的三合一體驗",
    "position": "bottom-left",
    "size": "medium",
    "duration": 40.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "顯示成就感滿滿的表情..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057944503.png",
    "caption": "課程完成 - 滿滿的成就感與喜悅",
    "position": "top-left",
    "size": "small",
    "duration": 35.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "展示最新課程完成圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059853029.png",
    "caption": "最新課程總結 - 銀色太空服完美結束",
    "position": "bottom-left",
    "size": "medium",
    "duration": 38.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059833143.png",
    "caption": "太空瑜伽大師完成課程",
    "position": "top-left",
    "size": "small",
    "duration": 36.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "展示課程總結專業圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749438804056.png",
    "caption": "太空瑜伽課程完美總結",
    "custom_position": {"bottom": "10%", "left": "20%"},
    "size": "medium",
    "duration": 39.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054044845.png",
    "caption": "課程成果展示",
    "custom_position": {"top": "20%", "left": "10%"},
    "size": "small",
    "duration": 37.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo

# --- 收尾環節 ---
echo "=== 收尾環節 ==="

echo "21. 設定結尾慶祝環境..."
curl -X POST "$BASE_URL/api/control/environment/preset" \
  -H "Content-Type: application/json" \
  -d '{"preset": "city"}'
curl -X POST "$BASE_URL/api/control/environment/intensity" \
  -H "Content-Type: application/json" \
  -d '{"intensity": 2.2}'
sleep 0.5

echo "21a. 回到特寫位置準備結尾..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 2.0
  }'
sleep 0.5

echo "21b. 放大頭部到最大，準備結尾表演..."
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 20.0}'
sleep 1.0

echo "21b1. 角色也要放大營造盛大結尾..."
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 5.0}'
sleep 2.0

echo "22. 播放結尾音效..."
curl -X POST "$BASE_URL/api/control/play-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "/audio/effects/Energetic_fast_pace.mp3",
    "volume": 0.2,
    "interrupt": false
  }'
sleep 0.5

echo "23. 生成課程結束感謝圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色課程結束超開心，雙手比愛心手勢，超大圓圓黑眼睛閃閃發光，簡潔卡通造型，背景有粉色愛心和感謝文字，kawaii anime風格，感謝pose",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，課程結束後超開心雙手比愛心，超大圓圓眼睛閃閃發光，背景有粉色愛心和感謝文字",
    "position": "top-left",
    "size": "large",
    "duration": 41.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "展示更多感謝圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059826020.png",
    "caption": "感謝大家參與 - 銀色太空服感謝禮",
    "position": "bottom-left",
    "size": "medium",
    "duration": 39.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059805241.png",
    "caption": "課程圓滿結束 - 滿滿的愛與感謝",
    "position": "top-left",
    "size": "small",
    "duration": 37.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "展示感謝與結尾圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1750051916113.png",
    "caption": "感謝參與太空瑜伽之旅",
    "custom_position": {"bottom": "18%", "left": "12%"},
    "size": "medium",
    "duration": 40.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1750047948421.png",
    "caption": "太空瑜伽完美結束",
    "custom_position": {"top": "35%", "left": "18%"},
    "size": "small",
    "duration": 38.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增fusion感謝瑜伽素材36..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750073271148.png",
    "caption": "最新生成 - Fusion風格感謝展示",
    "custom_position": {"top": "85%", "left": "88%"},
    "size": "small",
    "duration": 43.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增創意感謝瑜伽素材37..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750073294691.png",
    "caption": "最新生成 - 創意科幻感謝姿勢",
    "custom_position": {"bottom": "75%", "left": "95%"},
    "size": "medium",
    "duration": 45.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片38..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749890545206.png",
    "caption": "經典太空瑜伽場景 - 完美結束",
    "custom_position": {"top": "88%", "left": "85%"},
    "size": "small",
    "duration": 40.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增最終經典太空瑜伽圖片39..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1750051962146.png",
    "caption": "經典太空瑜伽場景 - 圓滿收尾",
    "custom_position": {"bottom": "80%", "left": "82%"},
    "size": "small",
    "duration": 38.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "24. 結尾感謝（頭內動作表演）..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "划手機",
    "loop": true
  }'
sleep 1.0

echo "24a. 切換到舞步1..."
# 播放舞步音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/taiwan_variety_sfx_04.mp3"
  }'
sleep 0.5

# 調整體型為舞蹈表演身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.7,
      "錯置": 0.4,
      "錯置.001": 0.35
    }
  }'
sleep 0.5

# 角色稍微縮小展現舞蹈細節
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 3.5}'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步1",
    "loop": true
  }'
sleep 2.0

echo "24a-1. 展示不穩舞步變化..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "不穩",
    "loop": true
  }'
sleep 1.5

echo "24a-2. 展示划手機舞步..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "划手機",
    "loop": true
  }'
sleep 1.5

echo "24a-3. 回到舞步1主旋律..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步1",
    "loop": true
  }'
sleep 0.5

echo "24a0. 切換到head_close_up觀察舞步1..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

echo "24a1. 生成舞步1頭內動作圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色在鮮豔城市燈光下跳舞步1，超大圓圓黑眼睛很開心，簡潔卡通造型，頭部特寫，背景有彩色音符和舞蹈特效，kawaii anime風格，dance pose",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，做舞步1動作時超大圓圓眼睛很開心，頭部特寫，背景有彩色音符和舞蹈特效",
    "position": "top-left",
    "size": "large",
    "duration": 39.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "展示專業舞步圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054414349.png",
    "caption": "專業太空舞步表演",
    "custom_position": {"top": "55%", "left": "15%"},
    "size": "medium",
    "duration": 36.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054909243.png",
    "caption": "舞步精華展示",
    "custom_position": {"bottom": "40%", "left": "8%"},
    "size": "small",
    "duration": 34.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增舞步瑜伽素材11..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068197285.png",
    "caption": "最新生成 - 城市燈光舞步展示",
    "custom_position": {"top": "65%", "left": "40%"},
    "size": "small",
    "duration": 43.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增舞步瑜伽素材12..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750054999284.png",
    "caption": "最新生成 - 專業舞步技巧",
    "custom_position": {"bottom": "55%", "left": "48%"},
    "size": "medium",
    "duration": 45.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增fusion舞步瑜伽素材30..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750073196494.png",
    "caption": "最新生成 - Fusion風格舞步展示",
    "custom_position": {"top": "68%", "left": "85%"},
    "size": "small",
    "duration": 41.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增創意舞步瑜伽素材31..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750073202169.png",
    "caption": "最新生成 - 創意科幻舞步動作",
    "custom_position": {"bottom": "60%", "left": "78%"},
    "size": "medium",
    "duration": 44.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片32..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749805626238.png",
    "caption": "經典太空瑜伽場景 - 舞步專精",
    "custom_position": {"top": "72%", "left": "90%"},
    "size": "small",
    "duration": 38.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "24b. 切換到舞步2..."
# 播放測試音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/測試音效1.mp3"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步2",
    "loop": true
  }'
sleep 2.0

echo "24b-1. 混合漂浮舞步..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮",
    "loop": true
  }'
sleep 1.5

echo "24b-2. 回到舞步2..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步2",
    "loop": true
  }'
sleep 1.0

echo "24b1. 切換到head_close_up觀察舞步2..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

echo "24c. 切換到舞步3..."
# 播放高潮音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/測試音效2.mp3"
  }'
sleep 0.5

echo "24c-1. 開始身體變化表演 - 第一次變胖..."
# 調整體型為超胖身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 1.0,
      "錯置": 1.0,
      "錯置.001": 1.0
    }
  }'
sleep 2.0

echo "24c-2. 變回正常身材..."
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.3,
      "錯置": 0.1,
      "錯置.001": 0.2
    }
  }'
sleep 2.0

echo "24c-3. 第二次變胖..."
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 1.0,
      "錯置": 1.0,
      "錯置.001": 1.0
    }
  }'
sleep 2.0

echo "24c-4. 再次變回正常..."
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.3,
      "錯置": 0.1,
      "錯置.001": 0.2
    }
  }'
sleep 2.0

echo "24c-5. 第三次變胖（最後一次）..."
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 1.0,
      "錯置": 1.0,
      "錯置.001": 1.0
    }
  }'
sleep 2.0

# 調整體型為終極表演身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.9,
      "錯置": 0.6,
      "錯置.001": 0.5
    }
  }'
sleep 0.5

# 角色超級放大營造華麗終章
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 6.0}'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "舞步3",
    "loop": true
  }'
sleep 0.5

echo "24c0. 切換到head_close_up觀察舞步3..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

echo "24c1. 生成舞步3華麗終章圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色舞步3華麗終章，雙臂高舉慶祝姿勢，超大圓圓黑眼睛超級開心興奮，簡潔卡通造型，背景有彩色煙火和慶祝特效，鮮豔城市夜景，kawaii anime風格，climax",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，做舞步3動作時超大圓圓眼睛超級開心興奮，雙臂高舉，背景有彩色煙火和慶祝特效",
    "position": "top-left",
    "size": "large",
    "duration": 49.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "24d. 最後飛1和飛2..."
# 播放飛翔音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/spaceship_ambience_01.mp3"
  }'
sleep 0.5

# 調整體型為飛翔輕盈身材
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.15,
      "錯置": 0.05,
      "錯置.001": 0.1
    }
  }'
sleep 0.5

# 角色縮到中等大小展現飛翔輕盈感
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 2.0}'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "飛1",
    "loop": true
  }'
sleep 2.0

echo "24d-1. 混合漂浮2飛翔..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮2",
    "loop": true
  }'
sleep 1.5

echo "24d-2. 展示運動2飛翔技巧..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "運動2",
    "loop": true
  }'
sleep 1.5

echo "24d-3. 回到飛1..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "飛1",
    "loop": true
  }'
sleep 1.0

echo "24d0. 切換到head_close_up觀察飛1動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "飛2",
    "loop": true
  }'
sleep 0.5

echo "24d0-1. 播放更強烈的飛翔音效..."
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/spaceship_ambience_02.mp3"
  }'
sleep 0.5

echo "24d1-pre. 飛2動作時再次放大角色..."
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 4.0}'
sleep 0.5

echo "24d1-pre2. 切換到head_close_up觀察飛2動作..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "head_close_up",
    "duration": 1.5
  }'
sleep 1.5

echo "24d1. 生成飛翔終極圖..."
curl -X POST "$BASE_URL/api/take-selfie" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "超可愛日系卡通風格，綠色外星人角色終極太空飛翔，雙臂展開像超人飛行姿勢，超大圓圓黑眼睛非常自由快樂，簡潔卡通造型，背景有彩虹軌跡和閃亮星星，kawaii anime風格，flying pose",
    "reference_image": "prototype/backend/selfies/full_body/截圖 2025-06-16 下午1.35.01.png",
    "modification": "變成超可愛日系卡通風格的綠色外星人，做飛2飛翔動作雙臂展開像超人，超大圓圓眼睛非常自由快樂，背景有彩虹軌跡和星星",
    "position": "bottom-left",
    "size": "large",
    "duration": 50.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "顯示現有飛翔瑜伽素材..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057933310.png",
    "caption": "太空飛翔瑜伽 - 自由翱翔的極致體驗",
    "position": "top-left",
    "size": "medium",
    "duration": 45.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "顯示更多飛翔動作..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057482589.png",
    "caption": "進階飛翔 - 與星雲共舞",
    "position": "bottom-left",
    "size": "small",
    "duration": 42.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增飛翔瑜伽素材13..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1749630874735.png",
    "caption": "最新生成 - 經典飛翔姿勢",
    "custom_position": {"top": "75%", "left": "48%"},
    "size": "small",
    "duration": 47.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增飛翔瑜伽素材14..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1749717626157.png",
    "caption": "最新生成 - 星空飛翔體驗",
    "custom_position": {"bottom": "65%", "left": "55%"},
    "size": "medium",
    "duration": 49.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增fusion飛翔瑜伽素材33..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750073227962.png",
    "caption": "最新生成 - Fusion風格飛翔動作",
    "custom_position": {"top": "78%", "left": "95%"},
    "size": "small",
    "duration": 46.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增創意飛翔瑜伽素材34..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750073234275.png",
    "caption": "最新生成 - 創意科幻飛翔姿勢",
    "custom_position": {"bottom": "70%", "left": "88%"},
    "size": "medium",
    "duration": 48.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增經典太空瑜伽圖片35..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/image_1749807474024.png",
    "caption": "經典太空瑜伽場景 - 飛翔專精",
    "custom_position": {"top": "82%", "left": "92%"},
    "size": "small",
    "duration": 42.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "最終飛翔展示..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057449567.png",
    "caption": "終極飛翔 - 太空瑜伽的最高境界",
    "position": "bottom-left",
    "size": "large",
    "duration": 48.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "展示更多最新飛翔動作..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059895393.png",
    "caption": "最新飛翔姿勢 - 銀色太空服飛行",
    "position": "top-left",
    "size": "medium",
    "duration": 44.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059887112.png",
    "caption": "優雅飛翔展示 - 太空中的自由",
    "position": "bottom-left",
    "size": "small",
    "duration": 41.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750059859931.png",
    "caption": "進階飛翔技巧展示",
    "position": "top-left",
    "size": "medium",
    "duration": 43.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "展示終極飛翔圖片..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750057482589.png",
    "caption": "終極太空飛翔體驗",
    "custom_position": {"top": "12%", "left": "25%"},
    "size": "medium",
    "duration": 45.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750056410648.png",
    "caption": "完美飛翔姿態收尾",
    "custom_position": {"top": "30%", "left": "12%"},
    "size": "small",
    "duration": 42.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增課程總結圖片15..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1749800106858.png",
    "caption": "最新生成 - 課程總結精華",
    "custom_position": {"top": "82%", "left": "55%"},
    "size": "small",
    "duration": 50.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增課程總結圖片16..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1749733047366.png",
    "caption": "最新生成 - 瑜伽大師級表現",
    "custom_position": {"bottom": "75%", "left": "62%"},
    "size": "medium",
    "duration": 52.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增課程總結圖片17..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1749803759676.png",
    "caption": "最新生成 - 太空瑜伽完美收尾",
    "custom_position": {"top": "90%", "left": "62%"},
    "size": "small",
    "duration": 48.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增課程總結圖片18..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1749887434819.png",
    "caption": "最新生成 - 終極瑜伽成就",
    "custom_position": {"bottom": "85%", "left": "68%"},
    "size": "medium",
    "duration": 45.0,
    "aspect_ratio": "square"
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

# 播放結束慶祝音效
curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "sfxUrl": "/audio/effects/測試音效3.mp3"
  }'
sleep 0.5

echo "新增感謝圖片19..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750053296237.png",
    "caption": "最新生成 - 感謝大家的參與",
    "custom_position": {"top": "95%", "left": "70%"},
    "size": "small",
    "duration": 53.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增感謝圖片20..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750053358355.png",
    "caption": "最新生成 - 課程紀念合照",
    "custom_position": {"bottom": "95%", "left": "75%"},
    "size": "medium",
    "duration": 55.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增感謝圖片21..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750061150930.png",
    "caption": "最新生成 - 下次再見太空瑜伽",
    "custom_position": {"bottom": "8%", "left": "82%"},
    "size": "small",
    "duration": 48.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

echo "新增感謝圖片22..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068272892.png",
    "caption": "最新生成 - 訂閱按讚提醒",
    "custom_position": {"bottom": "5%", "left": "78%"},
    "size": "medium",
    "duration": 50.0,
    "aspect_ratio": "landscape"
  }'
sleep 0.5

echo "新增感謝圖片23..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068259144.png",
    "caption": "最新生成 - 太空瑜伽教室下期預告",
    "custom_position": {"bottom": "18%", "left": "88%"},
    "size": "small",
    "duration": 47.0,
    "aspect_ratio": "square"
  }'
sleep 0.5

echo "新增感謝圖片24..."
curl -X POST "$BASE_URL/api/show-existing-image" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "space_yoga/selfie_1750068203263.png",
    "caption": "最新生成 - 期待下次太空相聚",
    "custom_position": {"bottom": "28%", "left": "92%"},
    "size": "medium",
    "duration": 52.0,
    "aspect_ratio": "portrait"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "今天的太空瑜伽課程就到這裡！謝謝大家的參與，希望你們喜歡這個太空瑜伽體驗～看看我們一起拍的課程紀念照，記得按讚訂閱哦！",
    "message_type": "chat-message"
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/emotion-trajectory" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5.0,
    "keyframes": [
      {"tag": "grateful", "proportion": 0.0},
      {"tag": "happy", "proportion": 0.3},
      {"tag": "proud", "proportion": 0.6},
      {"tag": "content", "proportion": 1.0}
    ]
  }'
sleep 5.5

echo "25. 恢復預設狀態..."
curl -X POST "$BASE_URL/api/control/camera/set-frontend-preset" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "overview",
    "duration": 2.0
  }'
sleep 0.5

echo "25a. 恢復頭部正常大小..."
curl -X POST "$BASE_URL/api/control/head-size" \
  -H "Content-Type: application/json" \
  -d '{"scaleFactor": 1.0}'
sleep 0.5

echo "25a1. 恢復角色正常大小..."
curl -X POST "$BASE_URL/api/control/character/scale" \
  -H "Content-Type: application/json" \
  -d '{"scale": 1.0}'
sleep 0.5

echo "25a2. 恢復角色正常體型..."
curl -X POST "$BASE_URL/api/control/character/outfit" \
  -H "Content-Type: application/json" \
  -d '{
    "outfit_morphs": {
      "鍵 1": 0.0,
      "錯置": 0.0,
      "錯置.001": 0.0
    }
  }'
sleep 0.5

curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "臥躺",
    "loop": true
  }'
sleep 1.5

echo "25a3. 起身準備結束課程..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "Tpose",
    "loop": false
  }'
sleep 2.0

echo "25a4. 最後的漂浮告別..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "漂浮",
    "loop": true
  }'
sleep 1.5

echo "25a5. 划手機跟大家說再見..."
curl -X POST "$BASE_URL/api/control/character/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation": "划手機",
    "loop": true
  }'
sleep 2.0

echo "25a6. 最終臥躺休息..."
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

curl -X POST "$BASE_URL/api/control/background-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "bgmPlaying": false
  }'
sleep 2.5

echo "收尾環節完成！"
echo

echo "🎉 《太空辣妹瑜伽教室 2.0》 - 課程結束！"
echo "基礎版本測試完成，請確認所有環節是否正常運作。"
echo "確認沒問題後，我們可以繼續添加更多有趣的內容！" 