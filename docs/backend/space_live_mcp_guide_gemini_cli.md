# Space Live MCP 應用指南 for Gemini CLI

## 系統願景與整體目標

你本質上的意圖是：打造一個以 AI 驅動的互動虛擬角色體驗，並透過模型協作協議（Model Collaboration Protocol, MCP）提供的高階指令和豐富工具，將創意腳本轉換成實際可執行的互動表演。

具體來說，你希望：
- 將任何富有創意的互動腳本（例如：太空瑜伽、外星新聞播報、科幻音樂會等），透過 MCP Server 上的工具集，完整實現為一場互動直播節目。
2. 善用現有的 30 個功能工具（角色動作設定、舞蹈動畫、情緒切換、音效／音樂播放、場景設定等），精準呈現腳本中的每一個細節與幽默點。
3. 以 AI 角色的形式即時且流暢地表演，使虛擬人物與觀眾產生自然的互動，涵蓋動作展示、即興表演、台詞、環境音效與視覺呈現。
4. 透過高度整合且自動化的流程，迅速將創意構想轉換成生動的視覺化及互動表演，打造流暢且富娛樂性的 AI 直播體驗。

---

## 工具速查表

### 一、對話與情緒
- `send_message`：角色發送文字訊息。
- `set_emotion`：設定角色當前情緒（例如：開心、生氣、驚訝）。
- `emotion_transition`：平滑地從一種情緒轉換到另一種情緒。

### 二、角色動畫
- `character_animation`：執行預定義的角色動畫動作。
- `dance_group_animation`：控制群組角色同步進行舞蹈。
- `set_dance_group`：定義或調整群組角色配置。
- `set_body_shape`：調整角色身體形狀（例如：拉伸或縮短四肢）。

### 三、角色外觀調整
- `set_head_size`：設定角色頭部大小比例。
- `set_character_scale`：調整角色整體大小。
- `set_character_position`：設定角色位置。
- `set_character_rotation`：控制角色的旋轉。
- `reset_character_transform`：重設角色外觀至預設狀態。
- `set_character_morph`：改變角色臉部或身體形態。

### 四、場景設定與環境
- `set_environment_preset`：選擇預設場景環境（如：太空、星際等）。
- `set_light_intensity`：調整場景燈光強度。
- `reset_environment_settings`：重置所有場景設定至預設。
- `set_camera_preset`：設定預設鏡頭視角。

### 五、多媒體內容
- `play_song`：播放歌曲。
- `play_background_music`：播放或停止背景音樂。
- `stop_background_music`：停止背景音樂。
- `play_sound_effect`：播放特定音效。

### 六、視覺生成與展示
- `generate_image_overlay`：產生並顯示覆蓋在角色上的圖像。
- `generate_background_image`：生成背景圖像。
- `take_selfie`：拍攝並即時展示角色自拍。
- `show_existing_image`：展示預存圖像。

### 七、資訊展示與互動
- `set_monitor_content`：設定旁邊顯示器的內容。
- `speak_latest_space_news`：即時播報最新太空新聞。
- `generate_map_image`：產生並顯示地圖。
- `search_nasa_image`：從 NASA 取得並顯示相關圖像。
- `get_epic_image`：取得最新 EPIC 衛星地球圖像。

---

## 導演建議與實戰技巧

1. **情緒驅動**：搭配 `send_message` 與 `set_emotion / emotion_transition`，塑造有生命力的角色表演。
2. **節奏鋪陳**：使用 `play_song`、`play_background_music` 來調節整體氛圍與節奏起伏。
3. **視覺強化**：結合 `generate_image_overlay` 與 `set_environment_preset` 增強舞台效果。
4. **即時互動**：透過 `send_message`、`speak_latest_space_news` 提升與觀眾的互動性。
5. **多工具連擊**：將動畫、音效、情緒與鏡頭連續組合，創造層次豐富的「連擊」橋段。

> 有了本指南，Gemini CLI 將能迅速成為 Space Live MCP 的「大導演」，串聯各項工具，打造精彩的即時互動表演。