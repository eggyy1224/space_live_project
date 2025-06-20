#!/bin/bash
# 太空艙辣台妹拜媽祖 - 直播腳本
#
# 使用方法:
# 1. 確保後端伺服器正在運行
# 2. 在終端機中執行 `bash prototype/backend/experiment_scripts/mazu_live_show.sh`

# --- 全域變數 ---
BASE_URL="http://localhost:8000/api"
# 讓 curl 安靜模式，並在失敗時顯示錯誤
CURL_CMD="curl -s -f -X POST"

# --- 函式定義 ---
# 說話 + 情緒 (黃金法則)
speak() {
  CONTENT=$1
  DURATION=$2
  EMOTION_TAG=${3:-happy} # 預設情緒為 happy
  echo ">> 說話: $CONTENT"
  $CURL_CMD $BASE_URL/control/send-message -H "Content-Type: application/json" -d "{\"content\": \"$CONTENT\"}" &
  $CURL_CMD $BASE_URL/control/emotion-trajectory -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": [{\"tag\": \"$EMOTION_TAG\", \"proportion\": 1.0}]}"
  sleep $(echo "$DURATION * 0.8" | bc)
}

# 角色動畫
animate_character() {
  ANIMATION=$1
  SPEED=${2:-1.0}
  echo ">> 角色動畫: $ANIMATION"
  $CURL_CMD $BASE_URL/control/character/animation -H "Content-Type: application/json" -d "{\"animation\": \"$ANIMATION\", \"speed\": $SPEED, \"loop\": true}"
}

# 舞者動畫
animate_dancers() {
  ANIMATION=$1
  SPEED=${2:-1.0}
  echo ">> 舞者動畫: $ANIMATION"
  # 使用 & 讓舞者動畫在背景執行，不影響主流程
  $CURL_CMD $BASE_URL/control/body-animation -H "Content-Type: application/json" -d "{\"animation\": \"$ANIMATION\", \"speed\": $SPEED, \"loop\": true}" &
}

# 停止舞者動畫
stop_dancers() {
  echo ">> 停止舞者動畫"
  # 假設送出 Idle 動畫可以讓舞者停止
  animate_dancers "Idle" 1.0
}

# 播放背景音樂
play_bgm() {
  BGM_URL=$1
  VOLUME=${2:-0.6} # 設置一個適合當背景的音量
  echo ">> 播放BGM: $BGM_URL"
  $CURL_CMD $BASE_URL/control/background-audio -H "Content-Type: application/json" -d "{\"bgmUrl\": \"$BGM_URL\", \"volume\": $VOLUME, \"loop\": true}"
}

# 停止BGM
stop_bgm() {
  echo ">> 停止BGM"
  # 發送一個不帶 bgmUrl 的請求來停止音樂
  $CURL_CMD $BASE_URL/control/background-audio -H "Content-Type: application/json" -d "{\"bgmUrl\": \"\"}"
}

# 播放音效 - 修正為使用 background-audio 端點
play_sound_effect() {
  SOUND_URL=$1
  VOLUME=${2:-0.8}
  echo ">> 播放音效: $SOUND_URL"
  $CURL_CMD $BASE_URL/control/background-audio -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$SOUND_URL\"}"
}

# 播放角色語音 - 使用 play-audio 端點 (角色嘴巴發出的聲音)
play_character_voice() {
  VOICE_FILE=$1
  INTERRUPT=${2:-false}
  echo ">> 角色語音: $VOICE_FILE"
  $CURL_CMD $BASE_URL/control/play-audio -H "Content-Type: application/json" -d "{\"url\": \"/songs-file/$VOICE_FILE\", \"interrupt\": $INTERRUPT}"
}

# 拍角色自拍 (參考主角模型)
take_selfie() {
    DESCRIPTION=$1
    POSITION=${2:-center-left}
    DURATION=${3:-10.0}
    REFERENCE_IMAGE="full_body/full_body2.png" # 鎖定參考圖像，使用相對於 selfies 資料夾的正確路徑
    echo ">> 角色自拍 (參考 $REFERENCE_IMAGE): $DESCRIPTION at $POSITION"
    $CURL_CMD $BASE_URL/take-selfie -H "Content-Type: application/json" -d "{\"description\": \"Photorealistic selfie of me. $DESCRIPTION\", \"reference_image\": \"$REFERENCE_IMAGE\", \"position\": \"$POSITION\", \"duration\": \"$DURATION\"}"
}

# 攝影機運鏡
move_camera() {
  PRESET=$1
  DURATION=${2:-2.0}
  echo ">> 運鏡: $PRESET"
  $CURL_CMD $BASE_URL/control/camera/set-frontend-preset -H "Content-Type: application/json" -d "{\"name\": \"$PRESET\", \"duration\": $DURATION}"
  sleep $DURATION
}

# 產生背景
generate_background() {
  DESCRIPTION=$1
  REFERENCE_IMAGE="full_body/full_body2.png" # 使用主角作為參考
  echo ">> 產生背景 (參考 $REFERENCE_IMAGE): $DESCRIPTION"
  $CURL_CMD $BASE_URL/generate-background-image -H "Content-Type: application/json" -d "{\"description\": \"$DESCRIPTION\", \"reference_image\": \"$REFERENCE_IMAGE\", \"aspect_ratio\": \"16:9\"}"
}

# 產生物件圖片
generate_object_image() {
    DESCRIPTION=$1
    POSITION=${2:-center-left}
    SIZE=${3:-medium}
    DURATION=${4:-10.0}
    REFERENCE_IMAGE="full_body/full_body2.png" # 使用主角作為參考
    echo ">> 產生物件圖片 (參考 $REFERENCE_IMAGE): $DESCRIPTION at $POSITION"
    $CURL_CMD $BASE_URL/generate-image -H "Content-Type: application/json" -d "{\"description\": \"$DESCRIPTION\", \"reference_image\": \"$REFERENCE_IMAGE\", \"position\": \"$POSITION\", \"size\": \"$SIZE\", \"duration\": $DURATION}"
}

# 顯示現有圖片
show_existing_image() {
    FILENAME=$1
    CAPTION=${2:-"現有圖片"}
    POSITION=${3:-center}
    SIZE=${4:-large}
    DURATION=${5:-10.0}
    echo ">> 顯示現有圖片: $FILENAME at $POSITION"
    $CURL_CMD $BASE_URL/show-existing-image -H "Content-Type: application/json" -d "{\"filename\": \"$FILENAME\", \"caption\": \"$CAPTION\", \"position\": \"$POSITION\", \"size\": \"$SIZE\", \"duration\": $DURATION}"
}

# 環境光
set_environment() {
    PRESET=$1
    echo ">> 環境光: $PRESET"
    $CURL_CMD $BASE_URL/control/environment/preset -H "Content-Type: application/json" -d "{\"preset\": \"$PRESET\"}"
}

# --- 腳本開始 ---
echo "=== 太空艙辣台妹拜媽祖 直播秀 開始 ==="
play_sound_effect "/audio/effects/通訊聲1.mp3" 0.4 # 太空通訊音效開場
sleep 1
play_sound_effect "/audio/effects/spaceship_ambience_01.mp3" 0.5 # 太空船環境音，增加音量營造氛圍
sleep 1
play_bgm "/audio/BGM/太空媽祖.mp3"
sleep 2

# 1. 開場
echo "--- 1. 開場 ---"
generate_background "(cinematic composition, dramatic lighting, 8K photorealistic, no text) 單一焦點：台灣女太空人主播站在月球表面，穿著反光銀色太空服，戴著透明VR頭盔。背景：深藍色宇宙中的巨大地球，散發柔和藍光。前景：幾個發光的透明立方體懸浮，內含水果。三層構圖，高對比度，邊緣光效果。"
sleep 3
animate_character "運動2" 1.0
animate_dancers "Cheering" 1.2 # 舞者歡呼開場
move_camera "overview" 2.0
sleep 1
speak "大家好～歡迎來到『太空媽祖直播間』，我是你們最辣的太空台妹！" 4.0 "excited"
play_sound_effect "/audio/effects/聖光音效1.mp3" 0.5 # 神聖登場音效
show_existing_image "截圖 2025-06-19 下午5.47.24.png" "辣台妹太空主播" "center-right" "large" 4.0
move_camera "head_close_up" 2.0
sleep 1
generate_background "(futuristic space station interior, holographic displays, LED panels, blue ambient lighting, cinematic depth of field, no text) 太空艙控制室特寫，全息螢幕顯示地球數據，藍色科技光效，電影級構圖"
sleep 2
animate_character "漂浮" 1.0
speak "哇～看看這個太空艙，是不是超美的？我們現在在離地球38萬公里的地方耶！" 4.0 "amazed"
play_sound_effect "/audio/effects/物件漂浮音效1.mp3" 0.4 # 太空漂浮音效
show_existing_image "background_1750390962517.png" "太空媽祖場景" "center-left" "large" 3.0
move_camera "side_view" 2.0
animate_character "運動1" 1.0
speak "今天，不管你在地球還是火星，都來跟我一起拜拜保平安！" 3.0 "happy"
generate_background "(space window view, Earth in distance, starfield, warm interior lighting, professional photography, no text) 太空艙觀景窗，遠方地球閃耀，星空背景，溫暖艙內光線"
sleep 2
move_camera "center_orbit_high_1" 2.0
animate_character "Tpose" 1.0
speak "欸對了，如果你是從木星來的朋友，訊號可能會有點延遲，沒關係啦～媽祖有聽到！" 4.0 "happy"
play_sound_effect "/audio/effects/spaceship_ambience_02.mp3" 0.4 # 太空環境音取代木星通訊
sleep 2

# 2. 拜拜儀式開始
echo "--- 2. 拜拜儀式開始 ---"
generate_background "(sacred temple interior, golden decorations, incense smoke, warm lighting, traditional meets futuristic, no text) 神聖媽祖廟宇內部，金碧輝煌，香煙裊裊，溫暖金光"
sleep 2
stop_dancers # 儀式開始，舞者先靜下來
set_environment "dawn" # 柔和暖黃光
move_camera "low_angle_head" 2.0
animate_character "不穩" 0.8
speak "我們先點香囉，欸～在太空不能用真的火啦，不然警報器會亂叫～" 4.0 "happy"
play_sound_effect "/audio/effects/警告音1.mp3" 0.2 # 模擬警報聲
sleep 0.5
play_sound_effect "/audio/effects/spaceship_ambience_02.mp3" 0.6 # 太空環境音
sleep 1
show_existing_image "截圖 2025-06-20 上午11.46.44.png" "媽祖保佑" "center-left" "large" 4.0
move_camera "center_orbit_high_2" 2.0
animate_character "划手機" 1.0
speak "你們看，這個VR點香系統是我們太空站最新的科技！" 3.0 "excited"
generate_background "(holographic incense ceremony, digital flames, sacred atmosphere, blue and gold lighting, no text) 全息點香儀式，數位火焰，神聖氛圍，藍金光效"
sleep 2
animate_character "漂浮2" 0.8
speak "而且還有香味模擬器，聞起來跟真的檀香一模一樣耶～" 3.0 "happy"
play_sound_effect "/audio/effects/聖光音效2.mp3" 0.4 # 香火燃燒音效
move_camera "orbit_head_1" 2.0
take_selfie "(close-up portrait, dramatic rim lighting, photorealistic, no text) 特寫：我虔誠專注的表情，雙手捧著發光的數位香。背景：模糊的流線型金屬香爐，散發溫暖橙光。構圖：人物佔畫面70%，表情清晰可見。光效：臉部柔和打光，輪廓邊緣光。" "center" 6.0
sleep 1
generate_background "(Mazu goddess manifestation, divine light, celestial background, sacred atmosphere, no text) 太空中媽祖顯靈，慈悲面容，天后鳳冠，聖光環繞"
sleep 2
move_camera "dramatic_angle_1" 2.0
animate_character "臥躺" 1.0
speak "媽祖慈悲，香火靠VR也一樣靈驗喔！" 3.0 "confident"
play_sound_effect "/audio/effects/聖光音效3.mp3" 0.5 # 媽祖顯靈音效
speak "而且在太空拜拜特別有效，因為離天堂比較近嘛～哈哈！" 3.0 "happy"
sleep 1

# 3. 線上互動祈福
echo "--- 3. 線上互動祈福 ---"
show_existing_image "image_1750332380923.png" "祈福天燈" "center-right" "large" 4.0
move_camera "center_orbit_low_1" 2.0
animate_character "舞步1" 1.0
animate_dancers "SalsaDancing" 1.5 # 舞者用熱情的舞蹈回應觀眾
speak "現在留言祈福的，我都幫你們唸出來給媽祖聽喔～" 3.0 "happy"
play_sound_effect "/audio/effects/通訊聲3.mp3" 0.4 # 收到觀眾留言音效
generate_background "(interactive holographic display wall, floating messages, futuristic interface, blue lighting, no text) 太空艙互動螢幕牆，祈福留言飛舞，科技感介面"
sleep 2
move_camera "frontal_dynamic_low" 2.0
animate_character "舞步2" 1.0
speak "哇～留言好多喔，大家都好虔誠！我一個一個幫你們唸～" 3.0 "excited"
play_sound_effect "/audio/effects/物件漂浮音效2.mp3" 0.3 # 祈福訊息漂浮音效
generate_object_image "(wide shot, cinematic depth of field, photorealistic, no text) 主體：數十盞彩色全息天燈漂浮在深邃宇宙中。構圖：天燈分佈在不同景深層次，前大後小。光效：每盞燈散發柔和彩光（紅、藍、金、紫）。背景：星空與月球山脈輪廓。無任何文字元素。" "center-left" "large" 8.0
play_sound_effect "/audio/effects/Ambient_keyboard_cli_2.mp3"
sleep 1
move_camera "orbit_head_2" 2.0
animate_character "舞步3" 1.0
speak "來，台中小美祈求脫單成功！" 2.0 "happy"
play_sound_effect "/audio/effects/媽祖遶境2.mp3" 0.4 # 祈福音效
speak "小美加油喔～媽祖會幫你牽紅線的！" 2.0 "confident"
generate_background "(warm family blessing scene, Mazu benevolent smile, golden aura, harmonious atmosphere, no text) 溫馨家庭祝福場景，媽祖慈悲笑容，金光環繞"
sleep 2
move_camera "dramatic_angle_2" 2.0
animate_character "飛1" 1.0
speak "台南阿哲想要升職加薪！" 2.0 "excited"
play_sound_effect "/audio/effects/spaceship_ambience_03.mp3" 0.5 # 太空祝福環境音
speak "阿哲你要記得多拜拜，媽祖會保佑你工作順利！" 2.0 "happy"
sleep 1
animate_character "飛2" 1.0
speak "哇～還有月球基地的朋友祈求平安，媽祖有聽到喔！" 3.0 "amazed"
play_sound_effect "/audio/effects/spaceship_ambience_04.mp3" 0.4 # 月球基地太空環境音
generate_background "(lunar base connection, space communication, Earth in background, technological blessing, no text) 月球基地連線，太空通訊，地球背景，科技祝福"
sleep 2
move_camera "fly_by_left" 2.0
speak "月球基地的朋友你好～太空人之間要互相照顧喔！" 3.0 "happy"
play_sound_effect "/audio/effects/物件漂浮音效3.mp3" 0.4 # 太空互動音效
sleep 2

# 4. 趣味小意外
echo "--- 4. 趣味小意外 ---"
generate_background "(space station malfunction, warning lights, orange alert lighting, humorous atmosphere, no text) 太空艙意外狀況，警示燈閃爍，橘紅警示光，幽默氛圍"
sleep 2
play_sound_effect "/audio/effects/警告音2.mp3" 0.6 # 太空艙警報音效
animate_dancers "LookAround" 1.0 # 舞者也跟著東張西望
show_existing_image "截圖 2025-06-20 上午11.48.56.png" "意外狀況" "center-left" "large" 3.0
play_sound_effect "/audio/effects/故障音1.mp3" 0.4 # 系統故障音效
play_sound_effect "/audio/effects/spaceship_ambience_03.mp3" 0.6 # 太空故障環境音
move_camera "fly_by_right" 2.0
animate_character "不穩" 1.5 # 手忙腳亂
speak "欸欸欸，炮仔飛去哪裡啦？" 2.0 "surprised"
play_sound_effect "/audio/effects/電子砲1.mp3" 0.5 # 電子炮音效
generate_background "(zero gravity environment, floating objects, hair floating, humorous scene, soft lighting, no text) 零重力環境，物品飄浮，髮絲飛舞，幽默場面"
sleep 2
move_camera "top_down_center" 2.0
animate_character "飛1" 1.5
speak "完蛋了，零重力真的很難控制耶！" 2.0 "surprised"
play_sound_effect "/audio/effects/故障音2.mp3" 0.3 # 控制失靈音效
generate_object_image "(action shot, motion blur, photorealistic, no text) 動態特寫：一個精緻的電子炮竹在零重力中旋轉飛離。構圖：物體佔畫面中央，有輕微運動模糊。光效：金屬表面反射環境光。背景：模糊的太空艙內部結構。高對比度，無文字。" "center-right" "large" 4.0
sleep 1
play_sound_effect "/audio/effects/電子砲2.mp3" 0.4 # 電子炮射擊音效
play_sound_effect "/audio/effects/測試音效1.mp3"
move_camera "behind_head_looking_out" 2.0
animate_character "飛2" 1.5 # 追逐
speak "哎呀～撞到了！" 1.5 "surprised"
play_sound_effect "/audio/effects/故障音3.mp3" 0.5 # 碰撞故障音效
generate_background "(space station restored, protagonist stable, starfield background, relieved atmosphere, no text) 太空艙恢復正常，主播重新站穩，星空背景，輕鬆氛圍"
sleep 2
play_sound_effect "/audio/effects/警告音3.mp3" 0.2 # 系統恢復警示音
move_camera "frontal_dynamic_high" 2.0
animate_character "Tpose" 1.0
speak "媽祖抱歉抱歉，太空真的很難控制啦～" 2.0 "happy"
speak "各位地球朋友，不好意思喔，稍微技術性問題一下，馬上回來！" 3.0 "confident"
play_sound_effect "/audio/effects/電子砲3.mp3" 0.3 # 恢復正常音效
animate_character "運動2" 1.0
speak "這就是太空直播的真實面啦，沒有彩排的！哈哈～" 2.0 "happy"
sleep 1

# 5. 特殊環節：媽祖空間站抽籤
echo "--- 5. 特殊環節：媽祖空間站抽籤 ---"
show_existing_image "background_1750391174471.png" "媽祖神像" "center-right" "large" 4.0
play_sound_effect "/audio/effects/spaceship_ambience_01.mp3" 0.6 # 太空神聖環境音
generate_background "(epic wide shot, divine lighting, 8K photorealistic, no text) 壯觀構圖：巨大的媽祖全息雕像矗立在月球隕石坑中央。細節：紅金色天后服，鳳冠，手持如意。光效：雕像散發聖潔藍白光暈，與周圍岩石形成強烈對比。背景：深邃星空。三分法構圖，無文字。"
sleep 3
animate_dancers "HipHopDancin" 2.0 # 為了慶祝抽籤，來段街舞
move_camera "full_shot_dancers" 2.0
animate_character "運動1" 1.0
speak "來來來～抽籤時間到！媽祖說，心誠則靈！" 2.0 "excited"
play_sound_effect "/audio/effects/聖光音效2.mp3" 0.5 # 神聖抽籤音效
generate_background "(sacred fortune drawing hall, holographic Mazu statue, divine atmosphere, gold and blue lighting, no text) 神聖抽籤殿堂，全息媽祖神像，神聖氛圍，金藍光效"
sleep 2
move_camera "center_orbit_low_2" 2.0
animate_character "漂浮" 1.0
speak "這個太空籤筒是用量子科技做的，超準的喔！" 3.0 "amazed"
play_sound_effect "/audio/effects/物件漂浮音效1.mp3" 0.4 # 量子籤筒音效
sleep 1
move_camera "dance_circle_view" 2.0
animate_character "划手機" 1.0
speak "我們看看你今天的太空籤詩是什麼～" 2.0 "happy"
speak "媽祖～請給我們一個好籤喔～" 2.0 "confident"
play_sound_effect "/audio/effects/spaceship_ambience_02.mp3" 0.5 # 太空祈求環境音
show_existing_image "image_1750332671876.png" "太空籤詩" "center-left" "large" 4.0
generate_object_image "(macro close-up, golden hour lighting, photorealistic, no text) 特寫鏡頭：一張發光的數位籤詩懸浮在空中。構圖：籤詩佔畫面80%，清晰可見「上上籤：升官發財，好運連連」字樣。光效：金色邊緣光，內容發光。背景：柔焦的媽祖雕像輪廓。" "center-right" "large" 6.0
sleep 2
move_camera "head_close_up" 2.0
animate_character "舞步1" 1.0
speak "嘿，這一支太空籤很讚耶，升官發財，好運連連！" 3.0 "amazed"
play_sound_effect "/audio/effects/聖光音效3.mp3" 0.6 # 上上籤音效
generate_background "(auspicious scene, rainbow light rays, Mazu smiling, auspicious clouds, celebratory atmosphere, no text) 吉祥如意場景，彩虹光芒，媽祖笑容，祥雲繚繞，喜慶氛圍"
sleep 2
move_camera "side_view" 2.0
animate_character "舞步2" 1.0
speak "哇～媽祖真的很疼愛大家耶，給了上上籤！" 2.0 "excited"
play_sound_effect "/audio/effects/spaceship_ambience_03.mp3" 0.5 # 太空感謝環境音
show_existing_image "截圖 2025-06-20 上午11.49.37.png" "開心辣台妹" "center-right" "large" 3.0
animate_character "舞步3" 1.0
speak "大家記得要感謝媽祖喔～" 2.0 "happy"
sleep 1

# 6. 收尾祈福祝福
echo "--- 6. 收尾祈福祝福 ---"
stop_dancers # 進入莊嚴的祈福環節
generate_background "(epic cosmic vista, divine rays, artistic photorealism, no text) 藝術構圖：媽祖身著未來科技與傳統融合服裝，站在月球最高峰。姿態：慈祥面向地球，雙手散發光芒。光效：聖潔光束從她延伸至地球，如絲帶般優美。背景：壯麗的地球與星河。極高對比度，無任何文字。"
show_existing_image "background_1750397258711.png" "媽祖祝福" "center-left" "large" 10.0
sleep 5
play_sound_effect "/audio/effects/聖光音效1.mp3" 0.4 # 最終祝福音效
set_environment "night" # 寧靜的氛圍
show_existing_image "background_1750397400440.png" "太空祈福" "center-right" "large" 12.0
animate_character "漂浮2" 0.5 # 緩慢、虔誠
move_camera "slow_zoom_in" 5.0
play_sound_effect "/audio/effects/spaceship_ambience_04.mp3" 0.3 # 寧靜太空音
speak "太空媽祖有保佑，讓大家平安健康、快樂幸福。" 6.0 "happy"
sleep 2
speak "不論你現在在哪個星球，記得常常來太空媽祖直播間，辣台妹我隨時等你喔！" 7.0 "confident"
play_sound_effect "/audio/effects/通訊聲1.mp3" 0.3 # 跨星球通訊音效
speak "我們這個太空站24小時都有服務，媽祖的愛無時無刻都在！" 6.0 "happy"
speak "而且我們還有宇宙快遞服務，可以把祝福直接送到你家門口～" 6.0 "excited"
play_sound_effect "/audio/effects/物件漂浮音效2.mp3" 0.3 # 宇宙快遞音效
sleep 3

# 7. 結尾
echo "--- 7. 結尾 ---"
animate_dancers "twistdance" 1.8 # 最終的慶祝舞蹈
set_environment "default" # 恢復正常燈光
move_camera "overview" 3.0
animate_character "運動1" 1.0
speak "掰掰囉，記得按讚、訂閱、分享，媽祖也會記得你的功德無量喔！" 6.0 "excited"
play_sound_effect "/audio/effects/spaceship_ambience_04.mp3" 0.4 # 太空功德環境音
move_camera "center_orbit_high_1" 2.0
animate_character "漂浮" 1.0
speak "還有記得開小鈴鐺，這樣就不會錯過我們的太空直播了！" 5.0 "happy"
play_sound_effect "/audio/effects/通訊聲2.mp3" 0.3 # 訂閱通知音效
show_existing_image "background_1750395362321.png" "太空告別" "center-left" "large" 8.0
sleep 2
move_camera "frontal_dynamic_low" 2.0
animate_character "舞步1" 1.0
speak "太空再見啦～" 3.0 "happy"
play_sound_effect "/audio/effects/聖光音效2.mp3" 0.5 # 告別祝福音效
move_camera "fly_by_left" 2.0
animate_character "飛1" 1.0
speak "下次見面可能在火星，也可能在木星，誰知道呢～" 5.0 "excited"
play_sound_effect "/audio/effects/通訊聲3.mp3" 0.4 # 跨星球期待音效
sleep 2
show_existing_image "image_1750391210188.png" "最後祝福" "center-right" "large" 6.0
play_sound_effect "/audio/effects/spaceship_ambience_01.mp3" 0.5 # 太空告別環境音
move_camera "behind_head_looking_out" 3.0
animate_character "飛2" 1.0
speak "媽祖保佑大家～886！" 4.0 "happy"
play_sound_effect "/audio/effects/聖光音效3.mp3" 0.6 # 最終媽祖祝福音效
sleep 3 # 讓音樂再播一下下
stop_bgm
play_sound_effect "/audio/effects/故障音4.mp3" 0.3 # 有趣的結束音效（模擬傳輸結束）
play_sound_effect "/audio/effects/測試音效5.mp3" # 結束音效
echo "=== 直播秀 結束 ===" 