# Cursor API Control Response Guidelines v2.0
## 太空直播系統終極操作指南

### 🎯 核心理念：從API呼叫到藝術表演
這不只是技術文檔，而是將API組合成震撼表演的藝術指南。每個API呼叫都是樂器，組合技就是交響樂。

## 🚨 黃金法則：語音+情緒=生命力
**THE UNBREAKABLE RULE**: `send-message` 和 `emotion-trajectory` 必須成對使用，這是所有表演的基礎。
```bash
# ✅ 正確：生動的角色
curl -X POST .../send-message -d '{"content": "大家好！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 3.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}'

# ❌ 錯誤：沒有生命力的機器人
curl -X POST .../send-message -d '{"content": "大家好！"}'  # 只有聲音沒有情感
```

## 📁 快速導航：資源在哪裡找？
**不要死記硬背！學會探索！**

| 資源類型 | 探索指令 | URL前綴 | 使用場景 |
|---------|---------|---------|---------|
| BGM音樂 | `ls prototype/frontend/public/audio/BGM/` | `/audio/BGM/` | 背景氛圍 |
| 音效 | `ls prototype/frontend/public/audio/effects/` | `/audio/effects/` | 特殊效果 |
| 歌曲 | `ls prototype/backend/songs/` | `/songs-file/` | play-audio |
| 影片 | `ls prototype/frontend/public/videos/` | `/videos/` | Monitor螢幕 |
| 動畫 | `cat prototype/shared/config/animations.json` | 直接使用名稱 | 角色動作 |
| 生成圖片 | `ls prototype/backend/generated_images/` | 檔案名稱 | 重複使用 |

## 🎪 連續技系統：從基礎到終極

### Level 1: 基礎連續技 (3連擊)
**模式**: 語音+情緒 → 動作 → 鏡頭
```bash
curl -X POST .../send-message -d '{"content": "開始表演！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 3.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步1", "speed": 2.0}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "center_orbit_default", "duration": 2.0}'
```

### Level 2: 進階連續技 (5連擊)
**模式**: BGM → 語音+情緒 → 動作 → 頭部特效 → 鏡頭運動
```bash
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3"}' && \
curl -X POST .../send-message -d '{"content": "準備震撼！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 4.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步2", "speed": 3.0}' && \
curl -X POST .../head-size -d '{"scaleFactor": 4.0}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "dramatic_angle_1", "duration": 1.5}'
```

### Level 3: 終極連續技 (7+連擊)
**模式**: 背景 → BGM → 語音+情緒 → 動作 → 頭部特效 → Monitor牆 → 圖片生成
```bash
curl -X POST .../generate-background-image -d '{"description": "太空演唱會舞台", "aspect_ratio": "16:9"}' && \
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/spacelive_theme_bgm_04.mp3"}' && \
curl -X POST .../send-message -d '{"content": "史上最強演唱會開始！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 8.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 0.5}, {"tag": "confident", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步3", "speed": 4.0}' && \
curl -X POST .../head-size -d '{"scaleFactor": 6.0}' && \
curl -X PUT .../monitors/screen1 -d '{"content": "/videos/太空辣妹跳舞.mp4", "volume": 0.8, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen2 -d '{"content": "/videos/太空史萊姆.mp4", "volume": 0.7, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen3 -d '{"content": "/videos/太空打卡.mp4", "volume": 0.6, "visible": true, "playing": true}' && \
curl -X POST .../generate-image -d '{"description": "璀璨舞台煙火", "position": "center-left", "size": "large", "duration": 60.0}'
```

## 🎨 高級技巧

### 圖像生成革命 ⭐ **品質突破核心**
**從亂碼圖片到專業級品質的完整解決方案**

#### 第一性原理：專業攝影術語
```bash
# ✅ 成功範例：構圖+光影+技術規格
"(cinematic composition, dramatic lighting, 8K photorealistic, no text) 
單一焦點：鳳冠華服的太空媽祖，慈祥凝視遠方，背景是璀璨星雲，
景深虛化，專業人像攝影，高解析度，邊緣光效果"

# ❌ 失敗範例：描述複雜，容易產生文字亂碼
"媽祖在太空船裡面有很多文字說明和標語還有各種複雜的背景元素"
```

#### 參考圖片統一策略
```bash
# 所有圖像生成都使用統一參考 - 確保視覺一致性
REFERENCE_IMAGE="full_body/full_body2.png"

# 應用到所有圖像端點
curl -X POST .../take-selfie -d '{"reference_image": "'$REFERENCE_IMAGE'", ...}'
curl -X POST .../generate-background-image -d '{"reference_image": "'$REFERENCE_IMAGE'", ...}'
curl -X POST .../generate-image -d '{"reference_image": "'$REFERENCE_IMAGE'", ...}'
```

#### 關鍵術語庫
- **光影控制**: "戲劇性打光", "邊緣光效", "黃金時刻光線"
- **技術規格**: "高解析度", "專業攝影", "85mm鏡頭效果"  
- **風格定義**: "科幻寫實主義", "電影級質感"
- **負面提示**: "(no text)", "(no words)", "高對比度"

### 圖片位置戰略
**永遠不要擋住角色！**
- ✅ 安全位置: `center-left`, `center-right`, `top-left`, `top-right`, `bottom-left`, `bottom-right`
- ❌ 危險位置: `center` (會擋住角色)
- 🎯 **太空媽祖經驗**: 圖片尺寸用 `large`，位置多用 `center-left/right`

### Monitor音量階層
**創造聲音層次感**
- 主要內容: `volume: 1.0`
- 次要內容: `volume: 0.8`
- 背景環境: `volume: 0.6`

### 頭部特效進化
**戲劇性漸進式放大**
```bash
# 建立張力
curl -X POST .../head-size -d '{"scaleFactor": 2.0}' && sleep 1 && \
curl -X POST .../head-size -d '{"scaleFactor": 4.0}' && sleep 1 && \
curl -X POST .../head-size -d '{"scaleFactor": 8.0}' && sleep 2 && \
# 回歸正常
curl -X POST .../head-size -d '{"scaleFactor": 1.5}'
```

### 攝影機編舞
**引導觀眾視線**
```bash
curl -X POST .../camera/set-frontend-preset -d '{"name": "center_orbit_default", "duration": 2.0}' && sleep 2 && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "fly_by_left", "duration": 1.0}' && sleep 1 && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "dramatic_angle_1", "duration": 1.5}'
```

## 🔥 特殊組合技

### 腳本函式建構法 ⭐ **實戰精華**
**從太空媽祖專案學到的模組化架構：讓劇本清晰易懂**

```bash
# 核心函式組合：語音+情緒的黃金組合
speak() {
  CONTENT=$1
  DURATION=$2
  EMOTION_TAG=${3:-happy}
  echo ">> 說話: $CONTENT"
  curl -X POST $BASE_URL/control/send-message -d "{\"content\": \"$CONTENT\"}" &
  curl -X POST $BASE_URL/control/emotion-trajectory -d "{\"duration\": $DURATION, \"keyframes\": [{\"tag\": \"$EMOTION_TAG\", \"proportion\": 1.0}]}"
  sleep $(echo "$DURATION * 0.8" | bc)
}

# 主角動畫 vs 舞者動畫 (重要區分！)
animate_character() {
  ANIMATION=$1
  SPEED=${2:-1.0}
  curl -X POST .../character/animation -d "{\"animation\": \"$ANIMATION\", \"speed\": $SPEED}"
}

animate_dancers() {
  ANIMATION=$1
  SPEED=${2:-1.0}
  curl -X POST .../body-animation -d "{\"animation\": \"$ANIMATION\", \"speed\": $SPEED}" &
}

# 專業級圖像生成 (參考圖片+專業提示詞)
take_selfie() {
  DESCRIPTION=$1
  POSITION=${2:-center-left}
  REFERENCE_IMAGE="full_body/full_body2.png"
  curl -X POST .../take-selfie -d "{
    \"description\": \"Photorealistic selfie of me. $DESCRIPTION\", 
    \"reference_image\": \"$REFERENCE_IMAGE\", 
    \"position\": \"$POSITION\"
  }"
}

# 音效正確使用法
play_sound_effect() {
  SOUND_URL=$1
  curl -X POST .../background-audio -d "{\"sfxUrl\": \"$SOUND_URL\"}"
}

# 表演段落模板
performance_segment() {
  SEGMENT_NAME="$1"
  echo "=== $SEGMENT_NAME 開始 ==="
  # 1. 環境設定 → 2. 開場對話 → 3. 視覺效果 → 4. 互動元素 → 5. 段落收尾
  echo "=== $SEGMENT_NAME 結束 ==="
}
```

**為什麼這種函式建構方式這麼棒？**
- ✅ **可讀性極高** - 一目了然每個動作的目的
- ✅ **易於維護** - 修改參數只需要改一個地方
- ✅ **錯誤減少** - 封裝複雜的API呼叫
- ✅ **快速開發** - 組合函式就能創建複雜表演

### 創意循環技
**AI圖片連續進化**
```bash
# 第一階段：基礎自拍
curl -X POST .../take-selfie -d '{"description": "太空DJ", "position": "center-left", "duration": 45.0}' && \
# 第二階段：風格進化 (自動使用前一張作為參考)
curl -X POST .../continue-selfie -d '{"modification": "變成賽博朋克風格", "position": "center-right", "duration": 50.0}' && \
# 第三階段：背景呼應
curl -X POST .../generate-background-image -d '{"description": "賽博朋克太空夜店", "aspect_ratio": "16:9"}'
```

### 多圖同時展示技
**四角同時爆發**
```bash
curl -X POST .../show-existing-image -d '{"filename": "image_xxx.png", "position": "top-left", "size": "medium", "duration": 30.0}' && \
curl -X POST .../show-existing-image -d '{"filename": "selfie_yyy.png", "position": "top-right", "size": "medium", "duration": 35.0}' && \
curl -X POST .../show-existing-image -d '{"filename": "background_zzz.png", "position": "bottom-left", "size": "medium", "duration": 40.0}' && \
curl -X POST .../show-existing-image -d '{"filename": "image_aaa.png", "position": "bottom-right", "size": "medium", "duration": 45.0}'
```

## 📋 完整API參考

### 核心控制端點
| 方法 | 路徑 | 用途 | 關鍵參數 |
|-----|------|------|---------|
| POST | `/api/control/send-message` | 角色說話 | `content` (必須) |
| POST | `/api/control/emotion-trajectory` | 表情控制 | `duration`, `keyframes` (必須) |
| POST | `/api/control/character/animation` | 🎯主角動作 | `animation`: 漂浮/舞步1-3/運動1-2 |
| POST | `/api/control/body-animation` | 🎭舞者動作 | `animation`: Cheering/SalsaDancing |
| POST | `/api/control/head-size` | 頭部縮放 | `scaleFactor` (0.1-20.0) |
| POST | `/api/control/background-audio` | 音樂音效 | `bgmUrl` OR `sfxUrl` |
| POST | `/api/control/camera/set-frontend-preset` | 鏡頭預設 | `name`, `duration` |

**🚨 重要區分：動畫API兩套系統**
- `character/animation`: 主角專用 (太空主題動作)
- `body-animation`: 舞者群組 (標準動作庫)

### 圖片生成端點
| 方法 | 路徑 | 用途 | 位置選項 |
|-----|------|------|---------|
| POST | `/api/generate-image` | 生成新圖片 | 7種位置預設 |
| POST | `/api/generate-map-image` | 🗺️ **新功能**：生成地圖 | 7種位置預設 |
| POST | `/api/take-selfie` | 角色自拍 | 可指定風格描述 |
| POST | `/api/continue-selfie` | 自拍進化 | 自動使用最新自拍 |
| POST | `/api/show-existing-image` | 顯示舊圖片 | 重複利用已生成 |
| POST | `/api/generate-background-image` | 背景圖片 | 16:9 最佳 |

### Monitor控制
| 方法 | 路徑 | 用途 | 支援格式 |
|-----|------|------|---------|
| PUT | `/api/monitors/{screen1/screen2/screen3}` | 影片控制 | MP4影片檔 |
| GET | `/api/monitors` | 查看狀態 | 三螢幕同步 |

## ⚡ 實戰最佳實踐

### 1. 表演前檢查
```bash
# 確認連線狀態
curl -X GET http://localhost:8000/api/control/status
```

### 2. 資源探索習慣
```bash
# 每次表演前都先探索可用資源
ls prototype/frontend/public/audio/BGM/     # 音樂選擇
ls prototype/frontend/public/videos/        # 影片選擇  
ls prototype/backend/generated_images/      # 圖片重用
```

### 3. 組合技執行順序
1. **建立基礎** - 語音+情緒 (核心)
2. **加入層次** - 音樂、動作、視覺
3. **創造高潮** - 特效、多重刺激
4. **優雅收尾** - 復原設定、感謝觀眾

### 4. 錯誤處理策略 ⭐ **實戰除錯經驗**
- **API失敗時檢查 `detail` 欄位**
- **路徑錯誤時參考上方資源表格**
- **連線問題時重新檢查 WebSocket 狀態**
- **效果不如預期時拆解測試各個組件**

**🚨 太空媽祖專案常見陷阱：**
```bash
# ❌ 音效API用錯端點
curl -X POST .../play-audio -d '{"sfxUrl": "..."}'  # 錯誤！

# ✅ 音效正確用法  
curl -X POST .../background-audio -d '{"sfxUrl": "..."}'  # 正確！

# ❌ 圖片路徑問題
"/some/wrong/path/image.png"  # show-existing-image 讀不到

# ✅ 圖片正確路徑
"image_name.png"  # 必須在 generated_images/ 目錄下

# ❌ 動畫API混用
curl -X POST .../body-animation -d '{"animation": "漂浮"}'  # 主角動作用錯API

# ✅ 動畫API正確區分
curl -X POST .../character/animation -d '{"animation": "漂浮"}'  # 主角用這個
curl -X POST .../body-animation -d '{"animation": "Cheering"}'   # 舞者用這個
```

### 5. 創意發展原則 ⭐ **節奏優化精華**
- **不要重複** - 每次都探索新資源組合
- **建立節奏** - 用 sleep 控制時間感
- **層次堆疊** - 從簡單到複雜逐步建構
- **觀眾導向** - 考慮視覺衝擊和情感反應

**🎭 太空媽祖節奏優化經驗：**
```bash
# 經用戶反饋優化的時間設定
SPEECH_DURATION=3      # 語音時間 (原本5-8秒太慢)
SLEEP_SHORT=1          # 短暫停頓 (原本3秒太慢)  
SLEEP_MEDIUM=2         # 中等停頓
IMAGE_DURATION=5       # 圖片顯示 (原本8-15秒太久)

# 鏡頭運動多樣化 - 避免視覺疲勞
CAMERA_PRESETS=("overview" "head_close_up" "side_view" "center_orbit_high_1" 
                "dramatic_angle_1" "fly_by_left" "fly_by_right")
# 隨機選擇：${CAMERA_PRESETS[$((RANDOM % ${#CAMERA_PRESETS[@]}))]}

# 背景變化頻率 - 前面部分常換一點
# 每個段落 2-4 個背景變化，保持視覺新鮮感
```

## 🎭 高級應用場景

### 場景1: 太空夜店模式
```bash
# 環境建立
curl -X POST .../generate-background-image -d '{"description": "霓虹閃爍的太空夜店", "aspect_ratio": "16:9"}' && \
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_02.mp3"}' && \
# 角色表演
curl -X POST .../send-message -d '{"content": "歡迎來到太空夜店！今晚我們徹夜狂歡！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 6.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "happy", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "舞步2", "speed": 3.5}' && \
curl -X POST .../head-size -d '{"scaleFactor": 5.0}'
```

### 場景2: 太空瑜伽教學
```bash
# 寧靜環境
curl -X POST .../control/environment/preset -d '{"preset": "dawn"}' && \
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/spacelive_theme_bgm_01.mp3"}' && \
# 教學開始
curl -X POST .../send-message -d '{"content": "讓我們在太空中找到內心的平靜，開始瑜伽練習"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 8.0, "keyframes": [{"tag": "serene", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "運動1", "speed": 0.8}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "overview", "duration": 3.0}'
```

### 場景3: 太空媽祖直播模式 ⭐ **文化創新典範**
```bash
# 設定太空艙環境
generate_background "(cinematic space station interior, holographic displays, no text) 太空艙控制室，藍色科技光效"
play_bgm "/audio/BGM/太空媽祖.mp3"
play_sound_effect "/audio/effects/spaceship_ambience_01.mp3"

# 辣台妹主播登場
speak "大家好～歡迎來到『太空媽祖直播間』，我是你們最辣的太空台妹！" 4.0 "excited"
animate_character "運動2" 1.0
animate_dancers "Cheering" 1.2
move_camera "overview" 2.0

# 文化融合互動
take_selfie "(close-up portrait, dramatic lighting, no text) 我虔誠專注的表情，雙手捧著發光的數位香" "center-left" 6.0
show_existing_image "mazu_blessing.png" "媽祖保佑" "center-right" "large" 4.0
speak "在太空拜拜特別有效，因為離天堂比較近嘛～哈哈！" 3.0 "happy"
```

### 場景4: 新聞播報模式
```bash
# 專業環境
curl -X POST .../control/environment/preset -d '{"preset": "studio"}' && \
curl -X POST .../camera/set-frontend-preset -d '{"name": "head_close_up", "duration": 2.0}' && \
# 播報開始
curl -X POST .../send-message -d '{"content": "這裡是太空新聞中心，我是您的主播，為您帶來最新的宇宙動態"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 10.0, "keyframes": [{"tag": "confident", "proportion": 0.0}, {"tag": "professional", "proportion": 1.0}]}' && \
curl -X POST .../character/animation -d '{"animation": "Idle", "speed": 1.0}'
```

## 🚀 終極連續技範例

### 史上最強10連擊
```bash
echo "🚀 史上最強連續技開始！" && \
# 1. 場景設定
curl -X POST .../generate-background-image -d '{"description": "史詩太空競技場", "aspect_ratio": "16:9"}' && \
# 2. 音樂啟動
curl -X POST .../background-audio -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_03.mp3"}' && \
# 3. 開場白 (語音+情緒)
curl -X POST .../send-message -d '{"content": "準備迎接史上最震撼的太空表演！"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 5.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 1.0}]}' && \
# 4. 動作表演
curl -X POST .../character/animation -d '{"animation": "舞步3", "speed": 4.0}' && \
# 5. 頭部特效
curl -X POST .../head-size -d '{"scaleFactor": 7.0}' && \
# 6-8. 三螢幕影片牆
curl -X PUT .../monitors/screen1 -d '{"content": "/videos/太空辣妹跳舞.mp4", "volume": 1.0, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen2 -d '{"content": "/videos/太空史萊姆.mp4", "volume": 0.8, "visible": true, "playing": true}' && \
curl -X PUT .../monitors/screen3 -d '{"content": "/videos/space_live_video_1.mp4", "volume": 0.6, "visible": true, "playing": true}' && \
# 9. 圖片特效
curl -X POST .../generate-image -d '{"description": "爆炸性煙火特效", "position": "center-left", "size": "large", "duration": 60.0}' && \
# 10. 攝影機運動
curl -X POST .../camera/set-frontend-preset -d '{"name": "center_orbit_high_1", "duration": 2.0}' && \
echo "🎉 連續技完成！"
```

---

## 📝 快速備忘錄

### 必記口訣
1. **語音情緒不分離** - send-message + emotion-trajectory
2. **資源探索不死記** - 用 ls 指令找新內容  
3. **圖片位置避中央** - 不要擋住角色
4. **音量層次要分明** - 1.0 → 0.8 → 0.6
5. **頭部特效要漸進** - 建立戲劇張力
6. **表演結束要復原** - 回到預設狀態

### 常用指令速查
```bash
# 狀態檢查
curl -X GET http://localhost:8000/api/control/status

# 基礎表演 (語音+情緒)
curl -X POST .../send-message -d '{"content": "內容"}' && \
curl -X POST .../emotion-trajectory -d '{"duration": 3.0, "keyframes": [{"tag": "happy", "proportion": 1.0}]}'

# 資源探索
ls prototype/frontend/public/audio/BGM/
ls prototype/frontend/public/videos/
ls prototype/backend/generated_images/

# 重置狀態
curl -X POST .../head-size -d '{"scaleFactor": 1.0}'
curl -X POST .../camera/set-frontend-preset -d '{"name": "overview", "duration": 2.0}'
```

**記住：這不只是API文檔，這是創造震撼表演的藝術指南！每一次呼叫都是在創作，每一個組合都是在編舞。讓技術服務於藝術，讓API成為你的創意工具！** 🎭✨ 

---

## 📝 太空媽祖專案核心學習

**從實戰中獲得的黃金準則：**

1. **🎯 函式建構是王道** - 模組化讓劇本清晰易懂，維護超簡單
2. **🎨 圖像品質有方法** - 專業攝影術語 + 統一參考圖片 = 專業級效果  
3. **🚨 API區分要精確** - character/body-animation 兩套系統，絕不混用
4. **🔊 音效端點要對準** - background-audio (sfxUrl) ≠ play-audio (url)
5. **⚡ 節奏優化聽用戶** - 3秒語音 + 1秒停頓 = 緊湊吸引人
6. **📸 圖片位置有戰略** - center-left/right + large尺寸，永不擋主角
7. **🎭 測試驅動開發** - 每個功能都要實際驗證，才是真正可用

**未來任何腳本開發，都請遵循這套經過實戰驗證的最佳實踐！** 🚀✨ 