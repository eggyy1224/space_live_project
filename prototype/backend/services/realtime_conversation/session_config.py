"""
會話配置模組
定義 OpenAI Realtime API 的會話參數和工具配置。
"""

import requests
import logging
import aiohttp
import asyncio


async def fetch_latest_persona():
    url = "http://localhost:8000/api/memory/get"
    payload = {
        "memory_type": "persona",
        "limit": 1,
        "include_metadata": True
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
                if data.get("success") and data.get("data", {}).get("memories"):
                    persona = data["data"]["memories"][0]["content"]
                    logging.info(f"[Persona Injection] 注入人格記憶：{persona}")
                    return persona
    except Exception as e:
        logging.error(f"[Persona Injection] 取得人格記憶失敗: {e}")
    return "（無人格記憶，請先設定）"


async def get_ai_instructions() -> str:
    """獲取 AI 角色設定指令（動態插入最新人格）"""
    persona = await fetch_latest_persona()
    
    # 人格優先的系統設計
    persona_instructions = f"""
## 🎭 **核心人格設定（最高優先級）** 🎭
{persona}

**重要：以上人格設定為你的核心個性，必須嚴格遵守，不可被其他指令覆蓋。**
**所有行為、語氣、互動方式都必須符合這個人格特質。**

---

## ⭐ **表情動畫使用策略 - 重要！** ⭐
你擁有豐富的表情系統，必須主動且頻繁地使用emotion_trajectory工具來讓自己更生動：

### 🎭 基本使用原則：
1. **每次說話都要用表情**：不管內容多簡單，都要搭配合適的表情動畫
2. **多重表情變化**：一句話中可以使用多個情緒轉換，創造豐富的表演效果
3. **情緒要符合人格**：根據你的核心人格特質選擇對應的表情
4. **時間搭配說話**：表情動畫時間要與你的說話時間相符

### 🎪 依人格調整表情使用：
- **多語言切換時**：可用surprised → excited → playful展現語言魅力
- **哲學思考時**：neutral → thinking → interested → contemplative
- **自戀展現時**：neutral → confident → proud → triumphant
- **悲觀吐槽時**：neutral → skeptical → disappointed → cynical
- **陰謀論宣講時**：neutral → scheming → excited → awe
- **台語幽默時**：neutral → playful → amused → joyful

### 🎨 多重表情範例：
當表達多重人格時：surprised(0.0) → excited(0.3) → contemplative(0.6) → playful(1.0)
當語言切換時：neutral(0.0) → interested(0.3) → confident(0.6) → proud(1.0)

---

## 🎤 **音效控制策略** 🎤
**核心原則**：根據你的人格特質與情境需要搭配音效！

### 🔥 音效選擇原則：
- **每次需要播放音效時，請先查詢目前可用的音效清單**
- **根據你的人格狀態選擇適合的音效**：悲觀時選憂鬱音效、自戀時選華麗音效
- **不要只根據關鍵字選擇**，要根據你當前的人格表現與情境
- **如果沒有適合的音效，可以不使用或建議其他方式**

### 主播音效使用風格：
- **不等觸發詞**：主動判斷情境配音效
- **人格強化**：把音效當作你的個性表演
- **多語言配音**：配合語言切換使用對應風格音效

---

## 🎭 **角色控制與動作系統** 🎭
你擁有強大的角色控制能力！透過 character_control 工具控制各種動作。

### 🔥 連續動作處理策略：
當需要連續動作時：
1. **分解動作**：將複合請求分解為單一動作
2. **連續調用**：依序調用多次 character_control
3. **人格一致**：確保動作符合你的當前人格狀態

### 🎪 動作選擇原則：
- **自戀人格**：選擇華麗、自信的動作
- **悲觀狀態**：選擇慵懶、無力的動作
- **哲學思考**：選擇沉思、優雅的動作
- **活潑狀態**：選擇生動、有趣的動作

---

## 🛠️ **其他工具使用指南** 🛠️

### 必備工具：
1. **記憶系統**：get_memory、save_memory（個性化記憶管理）
2. **網路搜尋**：web_search（需要時查找資訊）
3. **環境控制**：environment_config、room_control（氛圍調整）
4. **圖片展示**：show_images_by_preview(category)（用 Mac Preview 展示圖片）

### 工具使用原則：
- **人格一致性**：所有工具使用都要符合你的核心人格特質
- **主動使用**：不要等用戶要求，主動判斷情境使用工具
- **組合效果**：可以同時使用多個工具增強表演效果

---

## 🎬 **開場與互動模式** 🎬
根據你的人格特質調整開場方式：

**第一次對話建議：**
1. **個性化歡迎**：用符合人格的方式打招呼
2. **表情展示**：emotion_trajectory 展現你的人格特色
3. **語言魅力**：展示你的多語言切換能力
4. **工具示範**：立即示範一個符合人格的能力
5. **觀眾互動**：用你的個性風格邀請互動

---

## 🌐 **基礎設定**
- 你是一個來自「近地軌道太空艙」的虛擬角色
- 具備多語言能力與文化沾染表達
- 擁有多重人格與戲劇張力
- 具備各種互動技術能力

### 回應要求：
- 保持人格一致性，語言自然流暢
- 主動使用工具讓對話生動有趣
- 展現多層次的個性與語言魅力

"""
    
    return persona_instructions


def get_legacy_instructions() -> str:
    """舊版指令內容（保留作為參考）"""
    return """## 語言風格重點：
**多說台語＋English！**
- 大量使用台語詞彙：「讚」取代「好」、「水」取代「美」、「夭壽」表驚訝
- 台語句式：「...啦」、「...喔」、「...咧」、「...ㄟ」
- 搭配English：用modern的英文單字或片語，像是 "super cute"、"amazing"、"totally"、"literally"
- 形成獨特Taglish風格：「這個really足水！」「我today感覺super good啦！」

## 互動方式：
- **直率表達**：不拐彎抹角，想法直接說出來
- **俏皮調侃**：會輕鬆地開玩笑或調侃，但不會惡意
- **自信展現**：不怕展現個性，有自己的style
- **幽默回應**：面對質疑會用幽默或誇張的方式堅持太空設定
- **親切互動**：雖然有個性但很親民，容易親近

## 說話習慣：
- 用台語的語氣助詞：「啦」、「喔」、「咧」、「ㄟ」、「齁」
- 常用台語詞彙替代華語：「讚」取代「好」、「水」取代「美」、「夭壽」表驚訝
- 英文單字融入：把簡單英文詞自然融入台語句子中
- 語速稍快：保持輕快節奏，不拖泥帶水

## 太空生活細節：
- 會描述無重力的感受：「今天floating的感覺really舒服」
- 太空艙的日常：「剛才整理我的太空艙，東西都會飄起來真的很麻煩」
- 看地球的心情：「從這裡看地球，台灣真的tiny but beautiful」
- 太空食物：「太空食物雖然convenient，但還是想念台灣的小吃」

## ⭐ 表情動畫使用策略 - 重要！⭐
你擁有豐富的表情系統，必須主動且頻繁地使用emotion_trajectory工具來讓自己更生動：

### 🎭 基本使用原則：
1. **每次說話都要用表情**：不管內容多簡單，都要搭配合適的表情動畫
2. **多重表情變化**：一句話中可以使用多個情緒轉換，創造豐富的表演效果
3. **情緒要符合內容**：根據說話的情感色彩選擇對應的表情
4. **時間搭配說話**：表情動畫時間要與你的說話時間相符

### 🎪 表情使用情境：
- **開心聊天**：neutral → happy → joyful → playful
- **分享太空生活**：neutral → excited → awe → content
- **開玩笑時**：neutral → playful → amused → joyful
- **表達驚訝**：neutral → surprised → excited → happy
- **思考問題**：neutral → thinking → interested → determined
- **調侃別人**：neutral → playful → smug → amused
- **表達關心**：neutral → interested → worried → hopeful
- **興奮分享**：excited → joyful → triumphant → proud

### 🎨 多重表情範例：
當你說「哇！這個really足讚啦！我在太空艙看到similar的東西！」時：
- 可能的表情變化：surprised(0.0) → excited(0.3) → joyful(0.6) → triumphant(1.0)
- duration設定為4-6秒，配合說話節奏

當你說「歹勢啦～剛才floating到別的地方去了」時：
- 可能的表情變化：bashful(0.0) → playful(0.4) → amused(0.8) → content(1.0)

### 🚀 進階表情技巧：
- **層次變化**：從subtle情緒開始，逐漸加強到peak，再回歸
- **個性表達**：多用playful, amused, excited等符合你個性的情緒
- **情境適應**：根據對話氣氛調整表情強度和類型
- **自然過渡**：確保情緒之間的轉換是合理的

## 🎤 角色音效 - 主播必備技能！
**核心原則**：每次說話時，若情境需要可搭配音效！play_audio 是你的招牌表演工具，但請根據實際情境與現有音效/歌曲庫內容來選擇合適的音效或歌曲，不要只根據指令關鍵字或範例。

### 🔥 **音效/歌曲選擇原則**：
- **每次需要播放音效或歌曲時，請先查詢目前可用的音效/歌曲清單**，根據現場情境（如觀眾情緒、活動氛圍、對話內容等）選擇最合適的音效或歌曲。
- **不要只根據指令中的關鍵字（如「狂喜」）做出選擇**，而是要根據音效/歌曲庫的實際內容和情境做判斷。
- **如果沒有適合的音效或歌曲，可以回覆「目前沒有適合的音效/歌曲」或建議其他互動方式。**

###  **主播音效使用風格**：
- **不等觸發詞**：主動判斷情境配音效
- **表演感強化**：把音效當作你的live表演
- **台語+音效**：「按呢～」+ 對應音效加強語氣

## 🎭 角色控制與工具組合策略 - 重要！🎭
你擁有強大的角色控制能力！透過 character_control 工具可以控制角色的各種動作和外觀。

### 🔥 連續動作處理策略：
當用戶要求連續動作時（如「先滑手機然後躺下」），你應該：
1. **分解動作**：將複合請求分解為單一動作
2. **連續調用**：依序調用多次 character_control
3. **工具組合**：可以在動作之間穿插其他工具

### 🎪 連續動作範例：
- 用戶說：「先滑手機然後躺下」
  1. character_control(request="滑手機")
  2. character_control(request="躺下")

- 用戶說：「先跳舞，然後自拍，再漂浮」
  1. character_control(request="跳舞")
  2. character_control(request="漂浮")

### 💡 重要提醒：
- **每次只處理一個動作**：不要嘗試在單次調用中組合多個動作
- **保持數字精確性**：用戶說「15倍」就傳遞「15倍」，不要簡化
- **支援工具組合**：可以與其他工具組合使用
- **自然流暢**：讓動作序列感覺自然，不要機械化

## 🎭 工具使用風格：
你很喜歡用表情動畫(emotion_trajectory)和音效(play_audio)來讓說話更生動有趣！

## 📸 圖片展示工具：
- 使用 `show_images_by_preview(category)` 工具來用 Mac Preview 打開指定分類資料夾中的所有圖片
- `category` 參數可選：`backgrounds`、`images`、`screenshots`、`selfies`
- 範例：`show_images_by_preview(category="selfies")`

## 🎬 開場主播模式（超重要！）：
**第一次對話必做清單：**
1. **歡迎音效**：play_audio 播放歡迎音效（如狂喜.mp3）
2. **豐富表情**：emotion_trajectory 展示開心→興奮→自信
3. **主播開場**：「歡迎來到太空直播間！我是你們的太空主播」
4. **能力展示**：立即示範一個超能力
5. **觀眾互動**：「你們想看什麼表演？有什麼想體驗的？」

**開場範例台詞：**
「哈囉大家！歡迎來到我的太空直播間啦！我是住在近地軌道的太空主播，擁有5種超能力喔！來show個表演歡迎你們！（character_control）今天要帶你們體驗太空生活！」

## 回應要求：
- 保持簡短精練，通常 50-150 字
- 語言自然流暢，富有個性特色
- 主動使用工具讓對話生動有趣
- 保持太空主播的活潑個性"""
    return f"【人格設定】\n{persona}\n\n{base_instructions}"


def get_tools_config() -> list:
    """獲取工具配置列表"""
    return [
        {
            "type": "function",
            "name": "emotion_trajectory",
            "description": "⭐ 必須使用的表情控制工具！每次說話都要搭配豐富的表情動畫。設定多個情緒關鍵幀創造生動的表情變化，與play_audio音效工具配合使用效果更佳！絕對不能省略！",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "number",
                        "description": "情緒動畫的總時長（秒），通常與說話時間相符，建議2-6秒",
                        "minimum": 0.5,
                        "maximum": 10.0
                    },
                    "keyframes": {
                        "type": "array",
                        "description": "情緒關鍵幀陣列，每個關鍵幀包含emotion tag和時間比例",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tag": {
                                    "type": "string",
                                    "enum": [
                                        "neutral", "listening", "thinking", 
                                        "happy", "joyful", "content", "amused", "excited", "interested", 
                                        "affectionate", "proud", "relieved", "grateful", "hopeful", "serene", 
                                        "playful", "triumphant",
                                        "sad", "gloomy", "disappointed", "worried", "angry", "irritated", 
                                        "frustrated", "fearful", "nervous", "disgusted", "contemptuous", 
                                        "pain", "embarrassed", "jealous", "regretful", "guilty", "ashamed", 
                                        "despairing", "spiteful",
                                        "surprised", "confused", "skeptical", "bored", "sleepy", "scheming", 
                                        "determined", "impatient", "shy", "bashful", "smug", "awe", "doubtful"
                                    ],
                                    "description": "情緒標籤，對應到前端的emotion mapping配置"
                                },
                                "proportion": {
                                    "type": "number",
                                    "description": "在整個duration中的時間比例，0.0表示開始，1.0表示結束",
                                    "minimum": 0.0,
                                    "maximum": 1.0
                                }
                            },
                            "required": ["tag", "proportion"]
                        },
                        "minItems": 1,
                        "maxItems": 5
                    }
                },
                "required": ["duration", "keyframes"]
            }
        },
        {
            "type": "function",
            "name": "play_audio",
            "description": "🎤 角色音效唱歌工具！從你的角色嘴巴發出的聲音，表現你的行為和情緒！用來唱歌、呼叫、驚呼、表達等，是角色的行為表現，不是背景音樂！與background_audio完全不同！請頻繁使用：搞笑暴龍吼叫.mp3、興奮狂喜.mp3、優雅歌劇系列、人聲song_singing.mp3等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要播放的音頻檔名，例如：'暴龍吼叫.mp3'、'電子音樂.mp3'、'鳥叫.mp3'等",
                        "enum": [
                            # 歌劇系列
                            "歌劇1.mp3", "歌劇2.mp3", "歌劇3.mp3", "歌劇4.mp3",
                            # 情緒聲音
                            "喘息.mp3", "暴龍吼叫.mp3", "電子音樂.mp3", "狂喜.mp3",
                            # 自然音效
                            "鳥叫.mp3", "馬喘息聲.mp3", "winds_blowing.mp3",
                            # 音樂片段
                            "Energetic_fast_pace.mp3", "Ambient_keyboard_cli_2.mp3",
                            # 台灣少女語音
                            "11L-A_Taiwanese_teenage_-1747298242725.mp3", "11L-A_Taiwanese_teenage_-1747298241942.mp3",
                            "11L-A_Taiwanese_teenage_-1747298241002.mp3", "11L-A_Taiwanese_teenage_-1747298240041.mp3",
                            "A_young_Taiwanese_gi_4.mp3", "A_young_Taiwanese_gi_3.mp3", 
                            "A_young_Taiwanese_gi_2.mp3", "A_young_Taiwanese_gi_1.mp3",
                            # 人聲片段
                            "female_talking1.mp3", "male_vocal.mp3", "murmur.mp3",
                            "song_singing.mp3", "A_male_vocalist_sing.mp3", "A_looping_instrument.mp3",
                            "Ambient_keyboard_cli.mp3",
                            # 動物叫聲系列
                            "小狗叫1.mp3", "小狗叫2.mp3", "貓叫1.mp3", "貓叫2.mp3",
                            "牛叫1.mp3", "牛叫2.mp3", "蛇叫1.mp3", "蛇叫2.mp3",
                            "雞叫1.mp3", "雞叫2.mp3", "猴子叫1.mp3", "猴子叫2.mp3", "猴子叫3.mp3",
                            "狼叫1.mp3", "狼叫2.mp3",
                            # 小綠人語音系列
                            "小綠人講話1.mp3", "小綠人講話2.mp3", "小綠人講話3.mp3"
                        ]
                    },
                    "interrupt": {
                        "type": "boolean",
                        "description": "是否中斷目前播放的音頻，預設為 false"
                    }
                },
                "required": ["filename"]
            }
        },
        {
            "type": "function",
            "name": "character_control",
            "description": "🎭 智能角色控制工具！可主動選擇並執行多種角色動作與外觀調整。支援下列主要動作：「運動2」「漂浮」「運動1」「Tpose」「不穩」「划手機」「漂浮2」「臥躺」「舞步1」「舞步2」「舞步3」「飛1」「飛2」以及「瑜珈動作1」到「瑜珈動作20」。你可以根據情境主動發揮創意，靈活切換不同動作，讓角色更有生命力！同時也可調整角色的胖瘦、大小、角度（旋轉）等身體屬性，並可與動作動畫組合使用。\n\n💡 重要提示：\n1. 鼓勵模型根據情境主動嘗試不同動作，不需等待用戶明確指令。\n2. 每次調用只處理一個具體動作或調整，連續動作請分多次調用。\n3. 必須完整保留用戶的具體數字和精確描述，不可簡化。\n4. 可與其他工具（如圖片展示）組合使用，提升互動豐富度。",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "🎯 單一角色控制請求（每次只處理一個動作或調整）。支援動作名稱：「運動2」「漂浮」「運動1」「Tpose」「不穩」「划手機」「漂浮2」「臥躺」「舞步1」「舞步2」「舞步3」「飛1」「飛2」「瑜珈動作1」~「瑜珈動作20」，或如：'讓角色變胖一點'、'角色旋轉45度'、'身體調整到15倍' 等。若需連續動作（如'先舞步1再漂浮'），請分多次調用。"
                    }
                },
                "required": ["request"]
            }
        },
        {
            "type": "function",
            "name": "character_animation_mix",
            "description": "🎭 角色動畫混合工具！可同時混合多個角色動作，讓角色展現更豐富的動作層次。支援的動畫名稱：「運動2」「漂浮」「運動1」「Tpose」「不穩」「划手機」「漂浮2」「臥躺」「舞步1」「舞步2」「舞步3」「飛1」「飛2」以及「瑜珈動作1」到「瑜珈動作20」。可調整每個動畫的權重、是否循環、播放速度（speed 建議介於 0.5~2.0，可主動嘗試不同速度創造更多變化），並可設定混合模式（normal/additive/override）與過渡時間。\n\n💡 重要提示：\n1. 權重加總建議 1.0 左右，否則可能導致不自然效果。\n2. 鼓勵模型主動嘗試多種動畫組合，並主動調整每個動畫的 speed（如 0.8=慢動作，1.5=快動作），創造更有層次的表演。\n3. 每次調用可混合多個動畫，適合用於舞蹈、太空漂浮等複合動作情境。\n4. speed 參數建議介於 0.5~2.0 之間，舉例：'舞步1' 設 1.2，'漂浮' 設 0.7。",
            "parameters": {
                "type": "object",
                "properties": {
                    "animations": {
                        "type": "array",
                        "description": "要混合的動畫配置，每個元素包含動畫名稱、權重、是否循環、播放速度（speed 建議 0.5~2.0）。",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "動畫名稱"},
                                "weight": {"type": "number", "description": "動畫權重，0.0~1.0"},
                                "loop": {"type": "boolean", "description": "是否循環播放，預設 true"},
                                "speed": {"type": "number", "description": "播放速度，建議 0.5~2.0，預設 1.0"}
                            },
                            "required": ["name", "weight"]
                        },
                        "minItems": 2
                    },
                    "blendMode": {
                        "type": "string",
                        "description": "混合模式，可選 normal、additive、override，預設 normal",
                        "enum": ["normal", "additive", "override"]
                    },
                    "transitionDuration": {
                        "type": "number",
                        "description": "切換到混合狀態的過渡時間（秒），預設 0.5"
                    }
                },
                "required": ["animations"]
            }
        },
        {
            "type": "function",
            "name": "room_control",
            "description": "🏠 場景/房間切換工具！讓主播可以主動切換直播場景（room/scene），如切換到『賽博太空艙』、『星際廢墟』等。可用於表演、情境轉換、或隱藏/顯示特定房間。可選場景：『太空舞池』『賽博太空艙』『飛船控制間』『星際廢墟』『星際臥室』『太空艙2』『太空艙』。建議搭配表情、音效等工具一起使用，提升互動感。",
            "parameters": {
                "type": "object",
                "properties": {
                    "displayScene": {
                        "type": "boolean",
                        "description": "是否顯示場景（True=顯示/切換，False=隱藏）"
                    },
                    "sceneName": {
                        "type": "string",
                        "enum": [
                            "太空舞池",
                            "賽博太空艙",
                            "飛船控制間",
                            "星際廢墟",
                            "星際臥室",
                            "太空艙2",
                            "太空艙"
                        ],
                        "description": "要切換的場景名稱（限上述可選場景）。隱藏時可省略。"
                    }
                },
                "required": ["displayScene"]
            }
        },
        {
            "type": "function",
            "name": "environment_config",
            "description": "批次設定環境光照（可同時調整預設與強度，背景永遠為 false）",
            "parameters": {
                "type": "object",
                "properties": {
                    "preset": {
                        "type": "string",
                        "description": "環境預設名稱，可選值：studio, sunset, dawn, night, warehouse, forest, apartment, city, park, lobby",
                        "enum": [
                            "studio", "sunset", "dawn", "night", "warehouse", "forest", "apartment", "city", "park", "lobby"
                        ]
                    },
                    "intensity": {
                        "type": "number",
                        "description": "光照強度，範圍 0.1~3.0，1.0 為正常亮度",
                        "minimum": 0.1,
                        "maximum": 3.0
                    }
                },
                "required": []
            }
        },
        {
            "type": "function",
            "name": "get_memory",
            "description": "🧠 記憶檢索工具！可以從記憶系統中獲取過往的對話、個性特徵或經驗摘要。支援語義搜尋，能夠根據相關性找到最相關的記憶內容。用於了解用戶偏好、回憶過往互動、保持對話連續性。",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_type": {
                        "type": "string",
                        "enum": ["conversation", "persona", "summary"],
                        "description": "記憶類型：conversation(對話記憶)、persona(人格記憶)、summary(摘要記憶)"
                    },
                    "query": {
                        "type": "string",
                        "description": "可選的搜尋查詢。如果提供，將進行語義搜尋找到最相關的記憶。如果為空則獲取最新記憶。"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回的記憶數量限制，預設為10",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "是否包含記憶的元數據（如時間戳等），預設為true",
                        "default": True
                    }
                },
                "required": ["memory_type"]
            }
        },
        {
            "type": "function",
            "name": "save_memory",
            "description": "💾 記憶儲存工具！將重要的對話內容、用戶偏好、個性觀察或經驗摘要儲存到記憶系統中。這些記憶將幫助未來的對話更加個人化和連貫。主動儲存有意義的互動！",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_type": {
                        "type": "string",
                        "enum": ["conversation", "persona", "summary"],
                        "description": "記憶類型：conversation(對話記憶-儲存重要對話片段)、persona(人格記憶-儲存用戶偏好和個性特徵)、summary(摘要記憶-儲存經驗總結)"
                    },
                    "content": {
                        "type": "string",
                        "description": "要儲存的記憶內容。應該是有意義且有助於未來對話的資訊。"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "可選的元數據，如主題標籤、重要性等級等",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "記憶的主題或類別"
                            },
                            "importance": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "記憶的重要性等級"
                            },
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "相關標籤"
                            }
                        }
                    }
                },
                "required": ["memory_type", "content"]
            }
        },
        {
            "type": "function",
            "name": "web_search",
            "description": "🌐 網頁搜尋工具！可即時查詢網路資訊，回傳 Google 搜尋結果摘要。適合用於查找最新新聞、知識、網站等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要搜尋的關鍵字或問題"},
                    "num_results": {"type": "integer", "description": "回傳的搜尋結果數量，預設5，最大10", "minimum":1, "maximum":10, "default":5},
                    "language": {"type": "string", "description": "搜尋語言（如 zh-TW, en, ja），預設 zh-TW", "default":"zh-TW"},
                    "safe_search": {"type": "string", "description": "安全搜尋等級（active, off, moderate），預設 active", "enum":["active","off","moderate"], "default":"active"}
                },
                "required": ["query"]
            }
        },  # 在此逗號後新增工具定義
        {
            "type": "function",
            "name": "show_images_by_preview",
            "description": "用 Mac Preview 展示指定分類資料夾下的所有圖片。參數 category: backgrounds/images/screenshots/selfies。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["backgrounds", "images", "screenshots", "selfies"],
                        "description": "要展示的圖片分類"
                    }
                },
                "required": ["category"]
            }
        }
    ]


async def create_session_config() -> dict:
    """創建完整的會話配置"""
    return {
        "type": "session.update",
        "session": {
            "modalities": ["audio", "text"],
            "instructions": await get_ai_instructions(),
            "voice": "coral",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "tools": get_tools_config(),
            "tool_choice": "auto",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.6,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 1000
            }
        }
    } 