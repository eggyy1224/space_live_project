# Cursor API Control Response Guidelines v2.0
## 太空直播系統終極操作指南

### 🎯 核心理念：從API呼叫到藝術表演
這不只是技術文檔，而是將API組合成震撼表演的藝術指南。每個API呼叫都是樂器，組合技就是交響樂。

## 🚨 黃金法則：語音+情緒=生命力
**THE UNBREAKABLE RULE**: `send-message` 和 `emotion-trajectory` 必須成對使用，這是所有表演的基礎。
```bash
# ✅ 正確：生動的角色
curl -X POST http://localhost:8000/api/control/send-message -H "Content-Type: application/json" -d '{"content": "大家好！"}' && \
curl -X POST http://localhost:8000/api/control/emotion-trajectory -H "Content-Type: application/json" -d '{"duration": 3.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}'

# ❌ 錯誤：沒有生命力的機器人
curl -X POST http://localhost:8000/api/control/send-message -H "Content-Type: application/json" -d '{"content": "大家好！"}'  # 只有聲音沒有情感
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
curl -X POST http://localhost:8000/api/control/send-message -H "Content-Type: application/json" -d '{"content": "開始表演！"}' && \
curl -X POST http://localhost:8000/api/control/emotion-trajectory -H "Content-Type: application/json" -d '{"duration": 3.0, "keyframes": [{"tag": "excited", "proportion": 1.0}]}' && \
curl -X POST http://localhost:8000/api/control/character/animation -H "Content-Type: application/json" -d '{"animation": "舞步1", "speed": 2.0}' && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "center_orbit_default", "duration": 2.0}'
```

### Level 2: 進階連續技 (5連擊)
**模式**: BGM → 語音+情緒 → 動作 → 頭部特效 → 鏡頭運動
```bash
curl -X POST http://localhost:8000/api/control/background-audio -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/heavy_metal_bgm_01.mp3"}' && \
curl -X POST http://localhost:8000/api/control/send-message -H "Content-Type: application/json" -d '{"content": "準備震撼！"}' && \
curl -X POST http://localhost:8000/api/control/emotion-trajectory -H "Content-Type: application/json" -d '{"duration": 4.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 1.0}]}' && \
curl -X POST http://localhost:8000/api/control/character/animation -H "Content-Type: application/json" -d '{"animation": "舞步2", "speed": 3.0}' && \
curl -X POST http://localhost:8000/api/control/head-size -H "Content-Type: application/json" -d '{"scaleFactor": 4.0}' && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "dramatic_angle_1", "duration": 1.5}'
```

### Level 3: 終極連續技 (7+連擊)
**模式**: 背景 → BGM → 語音+情緒 → 動作 → 頭部特效 → Monitor牆 → 圖片生成
```bash
curl -X POST http://localhost:8000/api/generate-background-image -H "Content-Type: application/json" -d '{"prompt": "太空演唱會舞台", "aspect_ratio": "16:9"}' && \
curl -X POST http://localhost:8000/api/control/background-audio -H "Content-Type: application/json" -d '{"bgmUrl": "/audio/BGM/spacelive_theme_bgm_04.mp3"}' && \
curl -X POST http://localhost:8000/api/control/send-message -H "Content-Type: application/json" -d '{"content": "史上最強演唱會開始！"}' && \
curl -X POST http://localhost:8000/api/control/emotion-trajectory -H "Content-Type: application/json" -d '{"duration": 8.0, "keyframes": [{"tag": "excited", "proportion": 0.0}, {"tag": "amazed", "proportion": 0.5}, {"tag": "confident", "proportion": 1.0}]}' && \
curl -X POST http://localhost:8000/api/control/character/animation -H "Content-Type: application/json" -d '{"animation": "舞步3", "speed": 4.0}' && \
curl -X POST http://localhost:8000/api/control/head-size -H "Content-Type: application/json" -d '{"scaleFactor": 6.0}' && \
curl -X PUT http://localhost:8000/api/monitors/screen1 -H "Content-Type: application/json" -d '{"content": "/videos/太空辣妹跳舞.mp4", "volume": 0.8, "visible": true, "playing": true}' && \
curl -X PUT http://localhost:8000/api/monitors/screen2 -H "Content-Type: application/json" -d '{"content": "/videos/太空史萊姆.mp4", "volume": 0.7, "visible": true, "playing": true}' && \
curl -X PUT http://localhost:8000/api/monitors/screen3 -H "Content-Type: application/json" -d '{"content": "/videos/太空打卡.mp4", "volume": 0.6, "visible": true, "playing": true}' && \
curl -X POST http://localhost:8000/api/generate-image -H "Content-Type: application/json" -d '{"prompt": "璀璨舞台煙火", "position": "center-left", "size": "large", "duration": 60.0}'
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

#### 核心原理二：多參考圖融合技法 (Multi-Reference Fusion)
以前我們只能用一張參考圖，現在系統升級了！我們可以同時提供 **多張參考圖**，並用精準的 **"食譜式提示詞"**，告訴AI如何融合這些圖片的特徵，創造出前所未有的新角色、新場景。

**食譜式提示詞 (Recipe-style Prompting) 的精髓：**
不要只說「混合它們」，要像寫食譜一樣，明確指示每個「食材」(參考圖) 的哪個部分要用、怎麼用。

**🔥終極範例：四圖融合創造全新角色**
這個例子融合了四張圖片，創造出一個全新的、具有複雜特徵的角色。

```bash
# 注意：`reference_images` 現在是一個列表！
curl -X POST 'http://localhost:8000/api/take-selfie' \
-H 'Content-Type: application/json' \
-d '{
    "prompt": "請你扮演一位頂尖的電影概念設計師，運用你對角色設計的深刻理解，融合以下四張參考圖片的特點，創造一個全新的、獨一無二的科幻角色。這是一份你的創作食譜：\n\n- **主要結構與輪廓**: 請以 `girl_pepe.png` 作為角色的基礎骨架和主要人形輪廓。這是我們的畫布。\n- **服裝與盔甲**: 借鑒 `silver_girl.png` 中那套閃亮的銀色緊身衣，將它的金屬質感和流線型設計融入角色的服裝中。\n- **色彩與氛圍**: 注入 `purple_girl.png` 的視覺風格。我需要你大量使用那種充滿活力的紫色和霓虹燈般的粉紅色調，讓整個角色散發出賽博龐克的迷幻氛圍。\n- **臉部特徵**: 最後，也是最關鍵的一步，請將 `green_alien.png` 的臉部特徵——特別是那雙富有表現力的大眼睛和獨特的頭部形狀——完美地移植到新角色上。我們既要保留外星人的奇異感，又要讓它與人形身體和諧共存。\n\n**最終目標**：創造一個看起來像是來自《銀翼殺手》或《攻殼機動隊》世界的角色，他/她既是人類，又是外星人；既有金屬的冰冷，又有霓虹的溫暖。這是一個關於身份融合與視覺衝擊的藝術挑戰。開始創作吧！",
    "reference_images": [
        "imgs/girl_pepe.png",
        "imgs/silver_girl.png",
        "imgs/purple_girl.png",
        "imgs/green_alien.png"
    ],
    "position": "center",
    "size": "large",
    "duration": 60
}'
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
curl -X POST http://localhost:8000/api/control/head-size -H "Content-Type: application/json" -d '{"scaleFactor": 2.0}' && sleep 1 && \
curl -X POST http://localhost:8000/api/control/head-size -H "Content-Type: application/json" -d '{"scaleFactor": 4.0}' && sleep 1 && \
curl -X POST http://localhost:8000/api/control/head-size -H "Content-Type: application/json" -d '{"scaleFactor": 8.0}' && sleep 2 && \
# 回歸正常
curl -X POST http://localhost:8000/api/control/head-size -H "Content-Type: application/json" -d '{"scaleFactor": 1.5}'
```

### 攝影機編舞
**引導觀眾視線**
```bash
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "center_orbit_default", "duration": 2.0}' && sleep 2 && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "fly_by_left", "duration": 1.0}' && sleep 1 && \
curl -X POST http://localhost:8000/api/control/camera/set-frontend-preset -H "Content-Type: application/json" -d '{"name": "dramatic_angle_1", "duration": 1.5}'
```

## 🔥 特殊組合技

### 場景一體化生成：畫中有人
這是一個更高級的技巧。我們不只生成背景，而是生成一張「本身就包含角色」的插畫，並將其作為背景。這樣可以創造出極具藝術感的「畫中畫」效果，讓3D角色與2D背景完美融合。

**創作理念：** 將我們剛剛創造的融合角色，放置在一個宏大的、與其風格匹配的場景中。

```bash
curl -X POST 'http://localhost:8000/api/generate-background-image' \
-H 'Content-Type: application/json' \
-d '{
    "prompt": "請你扮演一位史詩級的科幻插畫大師。你的任務是創作一幅宏偉的場景，將我們提供的兩個角色無縫地融入其中。這是一份你的創作食譜：\n\n- **參考角色1 (`selfie_1.png`)**: 這位角色擁有獨特的外星人頭部和紫色調的服裝。請將她作為畫面的前景或中景的主要焦點之一。確保她的姿態和表情與宏大的背景相得益彰。\n- **參考角色2 (`selfie_2.png`)**: 這位角色穿著黑色的高科技服裝。讓她以一種動態的、富有故事性的方式出現在場景中，可以是在遠處，或是在一個不同的視覺層次上，與角色1形成對比或互動。\n- **場景設計**: 構建一個巨大的、充滿未來感的城市景觀。想像一下《銀翼殺手2049》那樣的巨型建築、全息廣告牌和飛行器。整個城市需要被一種介於藍色和紫色之間的極光或能量場所籠罩，營造出夢幻而又有些許反烏托邦的感覺。\n- **氛圍與光影**: 使用強烈的戲劇性打光，突出兩個角色和城市的輪廓。光線應該是複雜的，既有來自城市本身的霓虹燈光，也有來自天空極光的漫反射。整體色調要統一在冷色系的藍、紫、黑之中，但可以用少量的暖色（如角色的眼睛或服裝細節）作為點綴。\n\n**最終目標**：創作一幅不僅僅是背景，而是一張完整的、帶有敘事感的電影級概念插畫。觀眾第一眼看到的是宏偉的場景，但細看之下會發現我們的主角們就生活在這個世界裡。開始你的傑作吧！",
    "reference_images": [
        "generated_images/selfie_1.png",
        "generated_images/selfie_2.png"
    ]
}'
```

### 腳本函式建構法 ⭐ **實戰精華**
**從太空媽祖專案學到的模組化架構：讓劇本清晰易懂**

```bash
# 核心函式組合：語音+情緒的黃金組合
speak() {
  CONTENT=$1
  DURATION=$2
  EMOTION_TAG=${3:-happy}
  echo ">> 說話: $CONTENT"
  curl -X POST http://localhost:8000/api/control/send-message -H "Content-Type: application/json" -d "{\"content\": \"$CONTENT\"}" &
  curl -X POST http://localhost:8000/api/control/emotion-trajectory -H "Content-Type: application/json" -d "{\"duration\": $DURATION, \"keyframes\": [{\"tag\": \"$EMOTION_TAG\", \"proportion\": 1.0}]}"
  sleep $(echo "$DURATION * 0.8" | bc)
}

# 主角動畫 vs 舞者動畫 (重要區分！)
animate_character() {
  ANIMATION=$1
  SPEED=${2:-1.0}
  curl -X POST http://localhost:8000/api/control/character/animation -H "Content-Type: application/json" -d "{\"animation\": \"$ANIMATION\", \"speed\": $SPEED}"
}

animate_dancers() {
  ANIMATION=$1
  SPEED=${2:-1.0}
  curl -X POST http://localhost:8000/api/control/body-animation -H "Content-Type: application/json" -d "{\"animation\": \"$ANIMATION\", \"speed\": $SPEED}" &
}

# 專業級圖像生成 (多參考圖片+專業提示詞)
take_selfie() {
  PROMPT=$1
  POSITION=${2:-center-left}
  # 將圖片路徑作為一個JSON字串數組傳遞 e.g., '["imgs/img1.png","imgs/img2.png"]'
  IMAGES_JSON_ARRAY=${3:-'[]'}
  
  curl -X POST http://localhost:8000/api/take-selfie -H "Content-Type: application/json" -d "{
    \"prompt\": \"$PROMPT\", 
    \"reference_images\": $IMAGES_JSON_ARRAY, 
    \"position\": \"$POSITION\"
  }"
}

# 音效正確使用法
play_sound_effect() {
  SOUND_URL=$1
  curl -X POST http://localhost:8000/api/control/background-audio -H "Content-Type: application/json" -d "{\"sfxUrl\": \"$SOUND_URL\"}"
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
curl -X POST http://localhost:8000/api/take-selfie -H "Content-Type: application/json" -d '{"description": "太空DJ", "position": "center-left", "duration": 45.0}' && \
# 第二階段：風格進化 (自動使用前一張作為參考)
curl -X POST http://localhost:8000/api/continue-selfie -H "Content-Type: application/json" -d '{"modification": "變成賽博朋克風格", "position": "center-right", "duration": 50.0}' && \
# 第三階段：背景呼應
curl -X POST http://localhost:8000/api/generate-background-image -H "Content-Type: application/json" -d '{"description": "賽博朋克太空夜店", "aspect_ratio": "16:9"}'
```

### 多圖同時展示技
**四角同時爆發**
```bash
curl -X POST http://localhost:8000/api/show-existing-image -H "Content-Type: application/json" -d '{"filename": "image_xxx.png", "position": "top-left", "size": "medium", "duration": 30.0}' && \
curl -X POST http://localhost:8000/api/show-existing-image -H "Content-Type: application/json" -d '{"filename": "selfie_yyy.png", "position": "top-right", "size": "medium", "duration": 35.0}' && \
curl -X POST http://localhost:8000/api/show-existing-image -H "Content-Type: application/json" -d '{"filename": "background_zzz.png", "position": "bottom-left", "size": "medium", "duration": 40.0}' && \
curl -X POST http://localhost:8000/api/show-existing-image -H "Content-Type: application/json" -d '{"filename": "image_aaa.png", "position": "bottom-right", "size": "medium", "duration": 45.0}'
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
| POST | `/api/control/dance_group` | 🕺舞團控制 | `formation`, `dancerCount`, `position`, `scale` |

**🚨 重要區分：動畫API兩套系統**
- `character/animation`: 主角專用 (太空主題動作)
- `body-animation`: 舞者群組 (標準動作庫)

### 圖片生成端點
| 方法 | 路徑 | 用途 | 控制選項 |
|-----|------|------|---------|
| POST | `/api/generate-image` | 生成新圖片 | 7種位置/3種大小 |
| POST | `/api/generate-map-image` | 🗺️ 生成地圖 | 可控位置/大小 |
| POST | `/api/search-nasa-image` | 🚀 搜尋NASA圖片 | 可控位置/大小 |
| POST | `/api/get-epic-image` | 🌍 **新功能**：取得地球全圖 | 可控位置/大小 |
| POST | `/api/take-selfie` | 角色自拍 | 可控位置/大小 |
| POST | `/api/continue-selfie` | 自拍進化 | 可控位置/大小 |
| POST | `/api/show-existing-image` | 顯示舊圖片 | 可控位置/大小 |
| POST | `/api/generate-background-image` | 背景圖片 | 16:9 最佳 |
| POST | `/api/control/dance_group` | 舞團控制 | - |

### 新聞播報端點
| 方法 | 路徑 | 用途 | 關鍵參數 |
|-----|------|------|----------|
| POST | `/api/news/speak-latest-news` | 📰播報最新太空新聞 | `limit`, `intro_text` |

### Monitor控制
| 方法 | 路徑 | 用途 | 支援格式 |
|-----|------|------|---------|
| PUT | `/api/monitors/{screen1/screen2/screen3}` | 影片控制 | MP4影片檔 |
| GET | `/api/monitors` | 查看狀態 | 三螢幕同步 |

### 舞團控制 (Dance Group)
| 方法 | 路徑 | 用途 |
|-----|------|------|
| POST | `/api/control/dance_group` | 控制舞團的陣型、人數、位置和大小 |

- **`formation`**: `string` - 陣型名稱 ('circle', 'grid', 'line', 'wall').
- **`dancerCount`**: `integer` - 舞者數量.
- **`position`**: `array[float]` - `[x, y, z]`