# Space Live MCP 應用指南 for AI 導演

歡迎來到 Space Live MCP 系統！作為 AI 導演，您將運用這套強大的工具集來創造震撼人心的互動表演。無論是太空瑜伽、科幻音樂會、外星新聞播報，還是任何您能想像的創意腳本，這些工具都能幫您實現。

## 🎯 您的使命

您將透過 30+ 個專業工具，將任何創意腳本轉換為生動的互動直播表演：
- 控制 AI 角色的語言、情緒與動作
- 操控攝影機視角與場景環境
- 生成圖像、播放音效與管理多媒體內容
- 創造引人入勝的視覺特效與互動體驗

---

## 🛠️ 完整工具清單

### 一、對話與情緒控制

**`send_message(content, message_type="chat-message")`**
- 讓 AI 角色說話
- 參數：content（訊息內容）

**`set_emotion(emotion, duration=3.0)`**
- 設定角色當前情緒
- 可用情緒：happy, sad, excited, surprised, angry, confused, neutral 等 50+ 種
- 參數：emotion（情緒名稱）、duration（持續秒數）

**`emotion_transition(start_emotion, end_emotion, duration=5.0)`**
- 創造平滑的情緒轉換動畫
- 參數：起始情緒、結束情緒、轉換時間

### 二、角色動畫與動作

**`character_animation(animation, loop=True, speed=1.0)`**
- 控制主角動畫
- 可用動畫：運動1, 運動2, 飛1, 飛2, 漂浮, 舞步1, 舞步2, 舞步3, 划手機, 臥躺等
- 參數：animation（動畫名稱）、loop（是否循環）、speed（播放速度）

**`character_animation_mix(animations_config, blend_mode="normal", transition_duration=0.5)` ⭐ NEW**
- 控制主角的多重動畫混合，可同時播放多個動畫並控制權重
- 參數：
  - animations_config（動畫配置JSON字串）
  - blend_mode（混合模式：normal, additive, override）
  - transition_duration（過渡時間秒數）
- 動畫配置格式：'[{"name": "動畫名稱", "weight": 權重0.0-1.0, "loop": true/false, "speed": 播放速度}]'

**`stop_character_animation_mix()` ⭐ NEW**
- 停止動畫混合，回到單一動畫模式
- 無參數

**`dance_group_animation(animation, speed=1.0, loop=True)`**
- 控制舞群動畫
- 使用標準動畫庫中的動作
- 參數：animation（動畫名稱）、speed（速度）、loop（循環）

**`set_dance_group(formation='circle', count=10, scale=5.0, x=0, y=-25, z=0)`**
- 設定舞群隊形、人數、大小與位置
- 可用隊形：circle, grid, line, wall
- 參數：formation（隊形）、count（人數）、scale（縮放）、x/y/z（位置）

### 三、角色外觀調整

**`set_head_size(scale_factor)`**
- 調整角色頭部大小（戲劇效果）
- 建議範圍：0.5 到 10.0

**`set_character_scale(scale)`**
- 調整角色整體大小
- 建議範圍：0.1 到 3.0

**`set_character_position(x, y, z)`**
- 設定角色 3D 位置

**`set_character_rotation(x, y, z)`**
- 設定角色旋轉角度（弧度）

**`reset_character_transform()`**
- 一鍵重置角色位置、旋轉與大小

**`set_character_morph(morph_name, value)`**
- 調整角色 Morph Target（臉部/身體形態）

**`set_body_shape(value)`**
- 調整角色身材（0.0 最瘦 - 1.0 最胖）

### 四、攝影機控制

**`set_camera_preset(preset_name, duration=2.0)`**
- 設定攝影機預設視角
- 可用預設：
  - 基本：overview, head_close_up, side_view
  - 環繞：center_orbit_high_1/2, center_orbit_low_1/2
  - 戲劇：dramatic_angle_1/2, low_angle_head
  - 動態：fly_by_left, fly_by_right, frontal_dynamic_low/high
  - 特殊：top_down_center, behind_head_looking_out
  - 舞蹈：dance_circle_view, full_shot_dancers
  - 頭部：orbit_head_1/2

### 五、場景與環境

**`set_environment_preset(preset)`**
- 設定環境光照預設
- 可用預設：studio, sunset, sunrise, night, warehouse, forest, apartment, city, park, hall

**`set_light_intensity(intensity)`**
- 調整光照強度（建議 0.1-3.0）

**`reset_environment_settings()`**
- 重置環境設定為預設值

### 六、音頻控制

**`play_song(song_name, interrupt=True)`**
- 播放歌曲檔案
- 檔案位置：`prototype/backend/songs/`

**`play_background_music(bgm_name)`**
- 播放背景音樂
- 檔案位置：`prototype/frontend/public/audio/BGM/`

**`stop_background_music()`**
- 停止背景音樂

**`play_sound_effect(effect_name)`**
- 播放音效
- 檔案位置：`prototype/frontend/public/audio/effects/`

**`generate_sound_effect(prompt, duration_seconds=5, filename=None, play_immediately=True)` 🎵 NEW**
- 使用 ElevenLabs AI 即時生成音效
- **重要：prompt 必須使用英文，中文會導致品質極差**
- 參數：
  - prompt（英文音效描述）
  - duration_seconds（持續秒數，建議 3-15）
  - filename（可選，自訂檔名）
  - play_immediately（是否立即播放）
- 生成的音效保存在：`prototype/frontend/public/audio/generated_sounds/`

### 七、視覺內容生成

**`generate_image_overlay(prompt, position='center', size='large', duration=10.0, aspect_ratio='square', reference_images=None)`**
- 生成圖片浮層
- 位置選項：center, top-left, top-right, bottom-left, bottom-right, center-left, center-right
- 尺寸：small, medium, large

**`generate_background_image(prompt, aspect_ratio='landscape', reference_images=None)`**
- 生成背景圖片
- 長寬比：landscape, portrait, square

**`take_selfie(prompt, reference_images=None, position='center', size='large', duration=15.0)`**
- AI 角色自拍
- 可基於參考圖片進行創作

**`show_existing_image(filename, caption=None, position='center', size='large', duration=15.0)`**
- 顯示已存在的圖片

### 八、專業資訊工具

**`speak_latest_space_news(limit=3, intro_text=None)`**
- 播報最新太空新聞

**`generate_map_image(latitude, longitude, zoom=14, caption=None, position='center', size='large', duration=25.0)`**
- 生成地圖圖片

**`search_nasa_image(query, caption=None, position='center', size='large', duration=25.0)`**
- 搜尋 NASA 圖庫
- **⚠️ 重要：query 參數必須使用英文！NASA API 只接受英文查詢**

**`get_epic_image(date=None, caption=None, position='center', size='large', duration=25.0)`**
- 獲取地球全貌圖

### 九、螢幕控制

**`set_monitor_content(monitor_id, video_name=None, volume=None, visible=None, playing=None, playback_speed=None)`**
- 控制螢幕顯示器
- 螢幕 ID：screen1, screen2, screen3
- 影片位置：`prototype/frontend/public/videos/`

---

## 🎬 導演技巧與最佳實踐

### 黃金法則：語音 + 情緒 = 生命力
**永遠將 `send_message` 與 `set_emotion` 或 `emotion_transition` 配對使用**

```python
# ✅ 正確示範
send_message("歡迎來到太空直播！")
set_emotion("excited", duration=3.0)

# ❌ 錯誤示範（缺乏情感）
send_message("歡迎來到太空直播！")  # 只有聲音沒有情感
```

### 🎵 音效生成黃金法則：必須使用英文 Prompt
**基於實戰驗證，中文 Prompt 會產生品質極差的音效！**

```python
# ✅ 正確示範：專業英文描述
generate_sound_effect("spaceship engine humming and vibrating steadily", duration_seconds=8)

# ❌ 錯誤示範：中文描述品質差
generate_sound_effect("太空船引擎聲音", duration_seconds=8)  # 會產生劣質音效
```

**專業英文音效術語庫**
- **太空主題**: "spaceship engine", "cosmic wind", "stellar atmosphere", "zero gravity ambience"
- **機械音效**: "electronic malfunction", "servo motor whirring", "hydraulic systems", "computer processing"
- **環境音效**: "deep space ambient", "cosmic radiation", "distant nebula", "stellar wind"
- **戲劇音效**: "dramatic tension build", "suspenseful atmosphere", "triumphant fanfare", "ethereal mystical"

### 🛰️ NASA API 黃金法則：必須使用英文搜尋
**基於實戰驗證，中文搜尋會導致 HTTP 500 錯誤！**

```python
# ✅ 正確示範：英文搜尋詞
search_nasa_image("nebula", caption="美麗的星雲景象")
search_nasa_image("mars rover", caption="火星探測車")

# ❌ 錯誤示範：中文搜尋詞會失敗
search_nasa_image("星雲", caption="星雲")      # ❌ HTTP 500 錯誤
search_nasa_image("火星探測器", caption="探測器") # ❌ HTTP 500 錯誤
```

**高品質英文搜尋詞庫**
- **天體現象**: "nebula", "galaxy", "supernova", "aurora", "solar eclipse"
- **太空探索**: "apollo mission", "space shuttle", "mars rover", "space station"  
- **宇宙景觀**: "earth from space", "saturn rings", "jupiter storms", "milky way"
- **科學設備**: "hubble telescope", "james webb", "voyager probe", "cassini spacecraft"

### 連續技系統

**基礎三連擊：語音 → 情緒 → 動作**
```python
send_message("準備開始表演！")
set_emotion("excited")
character_animation("舞步1", speed=2.0)
```

**進階五連擊：音樂 → 語音 → 情緒 → 動作 → 鏡頭**
```python
# ⚠️ 重要：先探索可用資源！
# ls prototype/frontend/public/audio/BGM/

play_background_music("星際狂舞.mp3")  # 實際存在的檔案
send_message("震撼登場！")
emotion_transition("neutral", "amazed", duration=4.0)
character_animation("舞步2", speed=3.0)
set_camera_preset("dramatic_angle_1", duration=2.0)
```

**🎭 NEW 動畫混合連續技：音樂 → 語音 → 情緒 → 混合動畫 → 鏡頭**
```python
# ⚠️ 重要：先探索可用資源！
# ls prototype/frontend/public/audio/BGM/

play_background_music("spacelive_theme.mp3")  # 實際存在的檔案
send_message("史無前例的太空漂浮舞蹈！")
emotion_transition("excited", "transcendent", duration=6.0)
character_animation_mix(
    '[{"name": "漂浮", "weight": 0.6, "speed": 0.8}, {"name": "舞步1", "weight": 0.4, "speed": 1.2}]',
    blend_mode="normal",
    transition_duration=1.0
)
set_camera_preset("center_orbit_high_1", duration=2.0)
```

**🚀 終極混合技：複雜多動畫混合**
```python
# 太空漂浮舞蹈：三個動畫同時混合
character_animation_mix(
    '[{"name": "漂浮", "weight": 0.4}, {"name": "舞步2", "weight": 0.3}, {"name": "飛1", "weight": 0.3}]',
    blend_mode="additive",
    transition_duration=2.0
)

# 停止混合，回到單一動畫
stop_character_animation_mix()
```

**🎵 NEW 音效生成連續技：音效 → 語音 → 情緒 → 動作**
```python
generate_sound_effect("spaceship preparing for takeoff with engines warming up", duration_seconds=5)
send_message("準備起飛！")
set_emotion("excited")
character_animation("飛1", speed=1.5)
```

**🚀 進階音效編排：BGM → 生成音效 → 語音 → 情緒 → 混合動畫**
```python
# ⚠️ 重要：先探索可用資源！
# ls prototype/frontend/public/audio/BGM/

play_background_music("spacelive_theme2.mp3")  # 實際存在的檔案
generate_sound_effect("electronic systems powering up with beeps and whirs", duration_seconds=4)
send_message("系統啟動完成！")
emotion_transition("neutral", "confident", duration=4.0)
character_animation_mix(
    '[{"name": "運動1", "weight": 0.7}, {"name": "舞步1", "weight": 0.3}]',
    blend_mode="normal"
)
```

### 視覺效果技巧

1. **圖片位置策略**：避免使用 center 位置（會遮擋角色），多用 center-left, center-right
2. **頭部特效**：用 `set_head_size` 創造戲劇張力（建議 2.0-8.0 倍）
3. **多圖同時展示**：在四個角落同時顯示不同圖片
4. **攝影機編舞**：連續切換不同視角引導觀眾視線
5. **🎭 動畫混合藝術**：
   - 基礎混合：運動 + 舞蹈 (0.7 + 0.3)
   - 太空主題：漂浮 + 舞步 + 飛行 (0.4 + 0.3 + 0.3)
   - 情緒混合：用 additive 模式創造豐富動作
   - 權重調整：總重量保持在 1.0 左右以獲得最佳效果

### ⚠️ 資源探索指令 - 必讀！

**🚨 重要原則：永遠不要猜測檔案名稱！使用前必須先探索！**

在使用任何媒體檔案前，**必須**先執行對應的探索指令：
- **BGM 音樂**：`ls prototype/frontend/public/audio/BGM/`
- **音效**：`ls prototype/frontend/public/audio/effects/`
- **生成音效**：`ls prototype/frontend/public/audio/generated_sounds/`
- **歌曲**：`ls prototype/backend/songs/`
- **影片**：`ls prototype/frontend/public/videos/`
- **動畫**：`cat prototype/shared/config/animations.json`

**正確流程範例**：
```bash
# 步驟 1: 先探索資源
ls prototype/frontend/public/audio/BGM/

# 步驟 2: 選擇實際存在的檔案
play_background_music("星際狂舞.mp3")  # ✅ 使用實際存在的檔案

# ❌ 錯誤做法：直接猜測檔案名
play_background_music("我猜的檔案.mp3")  # 會失敗！
```

---

## 🎭 動畫混合實戰範例

### 太空瑜伽表演
```python
# 設定太空瑜伽背景
generate_background_image("平靜的太空瑜伽工作室，有漂浮的星雲", aspect_ratio="landscape")
# ⚠️ 重要：先探索可用資源！
# ls prototype/frontend/public/audio/BGM/
play_background_music("spacelive_theme.mp3")  # 實際存在的檔案

# 🎵 NEW: 添加太空環境音效
generate_sound_effect("gentle cosmic wind with distant stellar ambience", duration_seconds=8, play_immediately=False)

# 開場介紹
send_message("歡迎來到太空瑜伽課程，讓我們在無重力環境中找到內在平衡")
set_emotion("serene", duration=3.0)

# 太空瑜伽混合動作：漂浮 + 運動
character_animation_mix(
    '[{"name": "漂浮", "weight": 0.8, "speed": 0.6}, {"name": "運動1", "weight": 0.2, "speed": 0.4}]',
    blend_mode="normal",
    transition_duration=2.0
)
set_camera_preset("center_orbit_low_1", duration=3.0)
```

### 太空DJ表演
```python
# 電子音樂背景
generate_background_image("未來主義的太空DJ台，霓虹燈閃爍", aspect_ratio="landscape") 
play_background_music("星際狂舞.mp3")

# 🎵 NEW: 添加電子音效
generate_sound_effect("electronic beat drops with synthesizer swells and digital glitches", duration_seconds=6)

# 興奮開場
send_message("太空音樂節開始！讓我們一起在星際中狂歡！")
emotion_transition("excited", "ecstatic", duration=4.0)

# 複雜DJ混合動作：舞蹈 + 划手機 + 飛行
character_animation_mix(
    '[{"name": "舞步2", "weight": 0.5, "speed": 2.0}, {"name": "划手機", "weight": 0.3, "speed": 1.5}, {"name": "飛1", "weight": 0.2, "speed": 1.8}]',
    blend_mode="additive",
    transition_duration=1.5
)
set_head_size(4.0)  # 戲劇化效果
```

### 🎵 NEW 太空引擎啟動表演
```python
# 太空船控制室背景
generate_background_image("高科技太空船控制室，儀表板閃爍", aspect_ratio="landscape")

# 引擎預熱音效
generate_sound_effect("spaceship engines warming up with mechanical hums and electrical charges", 
                     duration_seconds=10, filename="engine_warmup.mp3")

send_message("準備啟動引擎，所有系統檢查完畢")
set_emotion("focused", duration=3.0)

# 引擎啟動音效
generate_sound_effect("powerful spaceship engine ignition with roaring flames and metallic vibrations", 
                     duration_seconds=8, filename="engine_ignition.mp3")

send_message("引擎點火成功！準備進入超空間！")
emotion_transition("focused", "exhilarated", duration=5.0)

# 飛行動作配合
character_animation_mix(
    '[{"name": "飛1", "weight": 0.6}, {"name": "運動2", "weight": 0.4}]',
    blend_mode="normal",
    transition_duration=2.0
)
set_camera_preset("dramatic_angle_1", duration=3.0)
```

## 🚀 開始您的創作

現在您已經掌握了所有工具，包括**革命性的動畫混合系統**！開始創造屬於您的互動表演吧！記住：

### ✨ 核心創作原則
- 善用情緒變化創造角色生命力
- 結合音效與視覺強化氛圍
- 運用連續技創造震撼效果
- **🎭 NEW**: 善用動畫混合創造前所未有的動作表現
- **🎵 NEW**: 善用音效生成創造沉浸式聽覺體驗

### 🎭 動畫混合創作秘訣
- **基礎組合**: 運動 + 舞蹈 = 活力四射
- **太空主題**: 漂浮 + 任何動作 = 零重力效果
- **情緒表達**: 用 additive 模式疊加細微動作
- **戲劇高潮**: 三個動畫混合 + 頭部放大 = 震撼登場

### 🎵 音效生成創作秘訣
- **英文描述**: 必須使用專業英文術語，避免中文
- **質感描述**: 加入 "crackling", "humming", "vibrating" 等質感詞彙
- **複合效果**: 結合多種元素，如 "laser charging with electronic whir"
- **情境匹配**: 音效要與場景和角色動作完美配合
- **時長控制**: 建議 3-15 秒，太長會影響品質

### 🚀 無限可能
- 探索工具組合的無限可能
- 創造獨特的太空故事情境
- 運用動畫混合表達複雜情感
- **🎵 NEW**: 運用音效生成打造專屬聽覺世界
- 建構多層次的視聽饗宴

祝您創作愉快，期待看到您運用動畫混合系統和音效生成功能創造的精彩作品！

---

## 📊 實戰經驗總結 (2025年6月)

### 🎯 功能穩定性報告

基於大量實戰表演（星際狂舞 Part 6-9）的測試結果：

#### ✅ 高穩定性功能 (成功率 95%+)
- **音效生成 `generate_sound_effect`**: 100% 成功率 ⭐⭐⭐⭐⭐
  - 所有英文 prompt 都能正確生成高品質音效
  - 延遲時間已優化，前端播放穩定
  - 推薦用於所有需要即時音效的場景
- **角色動畫混合**: 95%+ 成功率
- **舞群控制**: 95%+ 成功率
- **攝影機切換**: 95%+ 成功率
- **螢幕控制**: 95%+ 成功率
- **情緒控制**: 100% 成功率
- **語音對話**: 100% 成功率

#### ⚠️ 中等穩定性功能 (成功率 70-90%)
- **背景圖片生成**: ~85% 成功率
  - 偶爾會遇到生成失敗，建議準備備用描述
- **圖片浮層生成**: ~80% 成功率
  - 複雜場景可能失敗，建議使用簡潔 prompt

#### ❌ 不穩定功能 (成功率 <70%)
- **NASA 圖片搜尋 `search_nasa_image`**: ~30% 成功率 ⚠️
  - **根本原因**: 使用中文搜尋導致 HTTP 500 錯誤
  - **解決方案**: **必須使用英文 prompt**！NASA API 只接受英文查詢
  - **建議**: 優先使用 `get_epic_image` 或預存圖片
  - 如需使用，請準備備用方案

### 🎭 舞群控制最佳實踐

#### 位置優化策略
```python
# ✅ 推薦設定：舞群向左移動避免擋住主角
set_dance_group(formation="wall", count=100, scale=15, x=-20, y=-25, z=0)

# ❌ 避免：舞群在中央擋住主角視線
set_dance_group(formation="wall", count=100, scale=15, x=0, y=-25, z=0)
```

#### 陣型選擇建議
- **wall**: 適合大型表演，建議 x=-20 向左偏移
- **circle**: 適合環繞效果，主角置於中央
- **grid**: 適合整齊劃一的視覺效果
- **line**: 適合簡潔的背景舞群

### 📷 攝影機視角實戦指南

#### 表演階段攝影機配置
```python
# 開場推薦：總覽視角
set_camera_preset("overview", duration=4.0)

# 激烈表演：動態視角
set_camera_preset("frontal_dynamic_high", duration=2.0)  # 高角度動感
set_camera_preset("frontal_dynamic_low", duration=2.0)   # 低角度震撼

# 戲劇高潮：戲劇視角
set_camera_preset("dramatic_angle_1", duration=3.0)      # 經典戲劇角度

# 動作場面：飛越視角
set_camera_preset("fly_by_left", duration=2.0)           # 左側飛越
set_camera_preset("fly_by_right", duration=2.0)          # 右側飛越

# 結尾回歸：總覽視角
set_camera_preset("overview", duration=4.0)
```

#### 攝影機切換頻率建議
- **高能場面**: 每 2-3 秒切換一次
- **抒情場面**: 每 5-8 秒切換一次
- **開場/結尾**: 4-6 秒長鏡頭

### 🎵 音效生成實戰技巧

#### 經過驗證的高品質 Prompt 範例
```python
# 太空主題音效
"spaceship engine humming and vibrating steadily"              # 太空船引擎
"deep space ambient cosmic wind and distant rumbling"         # 深空環境音
"atmospheric entry rumbling and plasma whistling"             # 大氣層進入

# 電子/機械音效
"intense electronic music drop with heavy bass"               # 電子音樂
"thunderous bass drops with distorted synths"                 # 低音震撼
"electronic malfunction with sparks crackling and warning beeps" # 電子故障

# 能量/爆炸音效
"powerful energy surge with a high-pitched whine"             # 能量激增
"massive explosion with a deep rumble and echoing aftermath"  # 大爆炸
"rapid-fire laser blasts with electronic distortion"         # 雷射攻擊

# 情緒/氛圍音效
"overwhelming crowd roar with thunderous applause"            # 群眾歡呼
"grand orchestral finale with a sense of triumph"            # 宏偉結尾
```

#### 音效生成參數建議
- **duration_seconds**: 3-8 秒最佳，15+ 秒可能影響品質
- **filename**: 使用有意義的英文檔名便於重複使用
- **play_immediately**: 建議 true，確保即時播放

### 🎬 複雜表演編排實戰模式

#### 六連擊組合技（經過實戰驗證）
```python
# BGM → 生成音效 → 語音 → 情緒 → 混合動畫 → 攝影機
play_background_music("星際狂舞.mp3")
generate_sound_effect("intense electronic music drop with heavy bass", duration_seconds=4)
send_message("這股能量正在將我們推向超空間！")
set_emotion("excited", duration=4)
character_animation_mix('[{"name": "舞步1", "weight": 0.8}, {"name": "飛2", "weight": 0.2}]')
set_camera_preset("frontal_dynamic_low", duration=2)
```

#### 視覺特效疊加技巧
```python
# 光照 → 頭部放大 → 生成音效 → 圖片浮層
set_light_intensity(3.0)                    # 最高光照強度
set_head_size(8.0)                          # 戲劇性頭部放大
generate_sound_effect("powerful energy surge with a high-pitched whine", duration_seconds=5)
generate_image_overlay("A massive supernova exploding in vibrant colors", duration=8)
```

### 🔧 故障排除指南

#### 音效播放問題
- **現象**: 音效生成成功但前端無聲
- **解決**: 檢查前端音量設定，確認瀏覽器允許自動播放

#### 🛰️ NASA API 英文 Prompt 黃金法則
**基於實戰驗證，中文 prompt 會導致 HTTP 500 錯誤！**

```python
# ✅ 正確示範：必須使用英文搜尋
search_nasa_image("nebula", caption="宇宙星雲")           # 搜尋詞用英文
search_nasa_image("apollo 11", caption="阿波羅11號")      # 搜尋詞用英文
search_nasa_image("mars rover", caption="火星探測器")    # 搜尋詞用英文
search_nasa_image("hubble telescope", caption="哈伯望遠鏡") # 搜尋詞用英文

# ❌ 錯誤示範：中文搜尋會導致失敗
search_nasa_image("星雲", caption="宇宙星雲")           # ❌ 會導致 HTTP 500
search_nasa_image("阿波羅", caption="太空任務")         # ❌ 會導致 HTTP 500
search_nasa_image("火星探測器", caption="火星探測")     # ❌ 會導致 HTTP 500
```

**高品質英文搜尋詞範例**：
- **太空天體**: "nebula", "galaxy", "supernova", "black hole", "pulsar"
- **太空任務**: "apollo 11", "mars rover", "space shuttle", "international space station"
- **天文設備**: "hubble telescope", "james webb telescope", "voyager", "cassini"
- **行星系統**: "saturn rings", "jupiter storms", "mars surface", "venus atmosphere"

#### NASA API 失敗處理
```python
# 備用方案：改用 EPIC 地球圖片
try:
    search_nasa_image("nebula", caption="宇宙星雲")  # 注意：搜尋詞必須用英文
except:
    get_epic_image(caption="地球全貌作為備用背景")
```

#### 舞群擋住主角
```python
# 立即修正：調整舞群位置
set_dance_group(x=-20)  # 向左移動 20 單位
```

### 💡 創新表演模式探索

#### 螢幕多媒體整合
```python
# 三螢幕協調表演
set_monitor_content("screen1", video_name="太空直播中3.mp4", volume=0.8, playing=True)
set_monitor_content("screen2", video_name="太空熱舞.mp3", playback_speed=1.5, playing=True)
set_monitor_content("screen3", video_name="太空熱舞2.mp4", volume=0.5, playing=True)
```

#### 音效層次建構
```python
# 層次 1: 背景 BGM
# ⚠️ 重要：先探索可用資源！
# ls prototype/frontend/public/audio/BGM/
play_background_music("spacelive_theme2.mp3")  # 實際存在的檔案

# 層次 2: 環境音效
generate_sound_effect("deep space ambient cosmic wind", duration_seconds=10, play_immediately=False)

# 層次 3: 預設音效
play_sound_effect("電子砲3.mp3")

# 層次 4: 即時生成音效
generate_sound_effect("thunderous bass drops with distorted synths", duration_seconds=5)
```

---

## 🏆 表演成功要素

### 經過實戰驗證的表演公式

**基礎表演 = BGM + 語音 + 情緒 + 動畫**
**進階表演 = 基礎表演 + 攝影機 + 生成音效**
**震撼表演 = 進階表演 + 動畫混合 + 視覺特效 + 舞群協調**

### 創作節奏控制
1. **開場**: 4-6 秒建立氛圍
2. **建構**: 2-3 秒快速變化
3. **高潮**: 1-2 秒密集切換
4. **緩解**: 3-4 秒讓觀眾消化
5. **結尾**: 5-8 秒完美收束

現在您已掌握所有實戰經驗，準備創造史詩級的互動表演吧！🚀