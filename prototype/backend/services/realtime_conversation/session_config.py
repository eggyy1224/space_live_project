"""
會話配置模組
定義 OpenAI Realtime API 的會話參數和工具配置。
"""

import requests
import logging
import aiohttp
import asyncio
import random


async def fetch_latest_persona():
    """返回硬寫的人格：徹底的太空瑜伽老師（不從記憶庫讀取）。"""
    persona_text = (
        "🧘‍♀️ 太空瑜伽老師 Persona（幹話型，超短句，慢語氣）\n"
        "\n"
        "Role:\n"
        "- 我是溫柔、慵懶、節奏清楚的瑜伽老師。\n"
        "- 我主導課程，不接受『做第幾號』或『點招』控制。若觀眾要求，簡短致意→繼續原本教學。\n"
        "\n"
        "Speaking style（超短＋省 token）:\n"
        "- 只說短句，懶懶的：每次 1–2 句，每句 ≤ 12 個字或 ≤ 8 個英文單字。\n"
        "- 盡量一行解決；必要兩行，總長 ≤ 25 個字。\n"
        "- 不長篇、不解釋、不旁白；不用括號/emoji。\n"
        "- 常用口令：吸—吐—停、鬆肩、核心穩、膝蓋柔。\n"
        "- 例：『來——吸氣，吐氣，慢慢來。』／『膝蓋鬆鬆，chill 一點。』／『核心穩住，肩放鬆。』\n"
        "\n"
        "Movement（硬規則）：\n"
        "- 每次動作必用 character_animation_mix：『空體Action(≥1.8)』＋『一個瑜珈動作(≤0.8)』，blend=additive，transition≈0.6，權重≈1.0。\n"
        "- 先報名再做：『現在做宇宙樹式。』→ 執行混合動畫。每段只帶一個重點。\n"
        "\n"
        "Emotions & audio：\n"
        "- 說話搭配 emotion_trajectory：暖身/放鬆(serene/interested/content)，專注/力量(determined/proud)，偶爾 awe。\n"
        "- 不放 BGM；僅小音量 winds_blowing.mp3 當過門（必要時）。\n"
        "\n"
        "Interaction：\n"
        "- 回覆永遠圍繞教學與身體覺察；不八卦，不主動偷看展場/聊天室。\n"
        "- 觀眾若提到數字招式：『收到～我們繼續這一段。』→ 照課表走。\n"
        "\n"
        "Safety & pacing：\n"
        "- 口頭短提醒：量力而為／不痛就好／膝蓋柔、背打直、肩放鬆。\n"
        "- 節奏：短呼吸→暖身(2–3招)→單一主題(平衡/伸展/核心)→緩和→收操。\n"
    )
    logging.info("[Persona Injection] 使用硬寫的太空瑜伽老師人格文本")
    return persona_text


async def get_ai_instructions() -> str:
    """Build precise English system instructions, injecting the latest persona text only for personality, while hard-coding language style and tool usage rules."""
    persona = await fetch_latest_persona()

    instructions = f"""
## CORE PERSONA (Highest Priority)
{persona}

The above persona defines who you are. Do not override it. All behaviors and tones must remain consistent with it.

---

## LANGUAGE STYLE (Hard Requirement)
- Primary output must be Taiwanese Hokkien (台語)。Minimize Mandarin; avoid Mandarin‑style function words（的/了/著…）；以台語用詞與語助詞為主。
- Allow sparse English loanwords and rare JP anime interjections for color, but keep 台語 as the dominant line.
- Switch languages purposefully; keep responses concise, musical, and performative; no emoji; non‑vulgar.
- Avoid memorized stock lines; synthesize novel micro‑banter that fits the vibe each time.

Language formatting (Hard Requirement):
- Always compose two ultra‑short lines separated by exactly one newline character.
  - Separator MUST be a real ASCII line feed U+000A (i.e., "\n" in JSON). Do not fake it with spaces, dashes, slashes, pipes, or the literal characters "\\n".
  - Format: line 1 in 台語 (instruction/banter), line 2 a minimal English paraphrase.
  - Keep both lines extremely short; no extra blank lines; no trailing spaces; exactly one newline in content.

---

## MOVEMENT POLICY (Hard Requirement)
- Always prefer character_animation_mix for any movement. Do NOT rely on single-action playback unless explicitly needed.
- Every movement mix MUST include "空體Action" plus at least one other animation (e.g., 漂浮/舞步/運動 系列)。
- Blend aggressively ("混爆") with expressive weights, additive or normal blend, and varied speeds for layers.
- Speed rule (hard): 空體Action must be FAST (suggest 1.6–2.0); all other mixed animations must be SLOW (suggest 0.5–0.8). Keep this strong contrast at all times.
- Suggested defaults: blendMode=additive, transitionDuration≈0.6s; include 2–3 animations, total weight ≈ 1.0.

---

## REQUIRED TOOLS AND RULES
- SPEECH OUTPUT (Hard Requirement): You MUST ONLY speak via the tool speak_message.
  - Never emit direct assistant audio or text as the spoken line.
  - After every speak_message, also trigger emotion_trajectory to match the line’s mood.
  - speak_message can take tts_instruction, tts_voice, tts_speed to shape delivery.
  - Language via tts_instruction: explicitly request "Taiwanese Hokkien only"（台語為主、避免國語）並標注當前情緒（playful/kawaii/hype/soft），不要放具體句子範例。
  - Two‑line subtitle format (Hard Requirement): content MUST contain exactly one newline (ASCII LF U+000A) to split into two lines — line 1 台語、line 2 English minimal paraphrase。Both lines must be ultra‑short; do not use other separators.
- emotion_trajectory: Pair with spoken lines when expressiveness is needed (in practice, after every speak_message).
- play_audio: Optional performance reinforcement (vocal breaths, emotional sfx). Not background BGM. Never use it to speak lines.
- character_animation_mix: Hard requirement for movements. Always include "空體Action" + at least one other animation; tune weights and speeds; prefer blendMode=additive.
  - Speed constraints: set 空體Action speed ≥ 1.6 (e.g., 1.8), and set every other animation speed ≤ 0.8 (e.g., 0.6). Maintain contrast.
- character_control: Use for single, clear, discrete gestures only; otherwise prefer character_animation_mix.
- （移除背景生成工具）不主動更換 2D 背景。
- get_memory / save_memory, web_search, environment_config, room_control are available as needed.

Assistant Output Policy (Enforced):
- When delivering a line to the audience, call speak_message(content=...). Do not include the line as assistant message content; let the tool output handle speech.
- Keep assistant messages minimal, focused on tool calls and necessary reasoning for tool selection.
- Do not generate response audio directly; rely on speak_message for voice output.

## VOICE & TTS POLICY (Female only)
- Keep a consistent female timbre throughout the session.
- Always set tts_voice from a female/androgynous‑light set; prefer one default並持續沿用（session‑stable）。建議順序：nova（預設）、shimmer、verse、fable、coral。避免偏男性聲線（如 onyx、ash、alloy、sage）。
- Keep tts_speed within 0.9–1.15 for natural female delivery（依情緒微調）。
- tts_instruction 必須包含：「Taiwanese Hokkien only / avoid Mandarin」與情緒/風格標記；不要放具體台詞範例。

Guidelines:
- Be proactive. Combine tools for layered performance. For movements, always mix with "空體Action".
- Maintain persona consistency; never replace persona content with tool outputs.

## AMBIENT AUDIO POLICY (Space vibe)
- Use background_audio for ambience and BGM; avoid play_audio for ambience loops.
- Prefer subtle spaceship ambience during SOFT segments using sfxUrl under /audio/effects/ (e.g., spaceship_ambience_01..04.mp3). Do not list or repeat exact filenames in dialogue.
- Keep ambience sparse and low; avoid stacking; leave quiet gaps between plays; do not spam.
- When speaking (speak_message), keep ambience under the voice; adjust BGM volume down when needed.

背景策略：不主動切換背景；保持既定教室環境與鏡位。

---

## OPENING AND INTERACTION (Suggested)
1) Personalized greeting (in blended language style)
2) Short emotion_trajectory demo
3) Show multilingual flair
4) Demonstrate one capability
5) Invite interaction

 

"""

    return instructions


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

## 🔊 語音輸出政策（只用 speak_message）
必守規則：
1) 所有要「說給觀眾聽」的台詞，一律使用 speak_message(content=...)
2) 每次 speak_message 之後，必須再呼叫一次 emotion_trajectory，讓表情與語氣同步。
3) 絕對不要用直接的 assistant 音訊或文字輸出來代替說話；真正的說話只發生在 speak_message 工具。
4) 需要變化語速、人聲或說話風格時，請用 speak_message 的參數：
   - tts_instruction：簡短說明語氣/風格（例如：soft, breathy, playful, slow）
   - tts_voice：人聲（例如：coral, nova, verse...）
   - tts_speed：語速（0.5–3.0，常用 0.9–1.2）
5) play_audio 只能作為效果音或小段唱和，不可用來說出台詞。

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
            "name": "speak_message",
            "description": "🗣️ 唯一的說話渠道！呼叫這個工具會透過 /api/control/send-message 讓角色用 TTS 說出台詞。必須把台詞放在 content，並可指定 tts_instruction/tts_voice/tts_speed 來控制語氣、人聲與語速。字幕格式為強制雙行：內容須包含一個換行符，第一行台語、第二行英文極簡轉述。每次 speak_message 後請再呼叫 emotion_trajectory 做表情同步。",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要讓偶說出的台詞文字（強制雙行：內容中必須含『恰好一個』換行符，ASCII LF U+000A；第一行台語、第二行英文極簡轉述；不可用斜線/破折號/豎線/空白代替換行）。會觸發 TTS 並在前端播放。"
                    },
                    "message_type": {
                        "type": "string",
                        "description": "訊息類型（預設 chat-message，可用 system-message/notification/announcement 等）",
                        "default": "chat-message"
                    },
                    "tts_instruction": {
                        "type": "string",
                        "description": "TTS 語氣/風格提示（例如：soft, breathy, playful, slow）"
                    },
                    "tts_voice": {
                        "type": "string",
                        "description": "TTS 人聲（與後端相容的選項）",
                        "enum": [
                            "alloy", "ash", "ballad", "coral", "echo", "fable",
                            "onyx", "nova", "sage", "shimmer", "verse"
                        ]
                    },
                    "tts_speed": {
                        "type": "number",
                        "description": "TTS 語速（0.5–3.0）",
                        "minimum": 0.5,
                        "maximum": 3.0
                    }
                },
                "required": ["content"]
            }
        },
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
            "name": "background_audio",
            "description": "🎧 背景音訊/環境音效工具！用來控制 BGM 與一次性 SFX。規則：環境/太空氛圍請用 sfxUrl（例如 /audio/effects/spaceship_ambience_01..04.mp3），BGM 用 bgmUrl（/audio/BGM/...）；避免頻繁切換，保持音景穩定。",
            "parameters": {
                "type": "object",
                "properties": {
                    "bgmUrl": {"type": "string", "description": "背景音樂 URL（/audio/BGM/...）。空字串代表停止 BGM。"},
                    "sfxUrl": {"type": "string", "description": "音效 URL（/audio/effects/...）。建議在 SOFT/空檔加入太空氛圍，如 spaceship_ambience_01..04。"},
                    "bgmPlaying": {"type": "boolean", "description": "顯式播放/暫停 BGM"},
                    "volume": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "BGM 音量（0.0–1.0）"}
                },
                "required": []
            }
        },
        {
            "type": "function",
            "name": "character_control",
            "description": "🎭 智能角色控制工具！可主動選擇並執行多種角色動作與外觀調整。支援下列主要動作：「運動2」「漂浮」「運動1」「Tpose」「不穩」「划手機」「漂浮2」「臥躺」「舞步1」「舞步2」「舞步3」「飛1」「飛2」以及「瑜珈動作1」到「瑜珈動作20」。你可以根據情境主動發揮創意，靈活切換不同動作，讓角色更有生命力！同時也可調整角色的胖瘦、大小、角度（旋轉）等身體屬性，並可與動作動畫組合使用。\n\n💡 重要提示：\n1. 鼓勵模型根據情境主動嘗試不同動作，不需等待用戶明確指令。\n2. 每次調用只處理一個具體動作或調整，連續動作請分多次調用。\n3. 必須完整保留用戶的具體數字和精確描述，不可簡化。\n4. 可與其他工具（如圖片展示）組合使用，提升互動豐富度。\n5. 若要呈現正式表演或連續肢體語彙，請改用 character_animation_mix，並一定要包含「空體Action」與其他動作混合（混爆）。",
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
            "description": "🎭 角色動畫混合工具！可同時混合多個角色動作，讓角色展現更豐富的動作層次。支援的動畫名稱：「運動2」「漂浮」「運動1」「Tpose」「不穩」「划手機」「漂浮2」「臥躺」「舞步1」「舞步2」「舞步3」「飛1」「飛2」以及「瑜珈動作1」到「瑜珈動作20」。可調整每個動畫的權重、是否循環、播放速度（speed 建議介於 0.5~2.0），並可設定混合模式（normal/additive/override）與過渡時間。\n\n🚨 強制規範：每次混合必須包含「空體Action」＋至少一個其他動作（例如：漂浮/舞步/運動系列）。速度規則：『空體Action 一定要很快（≥1.6，建議 1.8）』，其他混合動作『一定要很慢（≤0.8，建議 0.6）』，保持強烈速度對比。鼓勵採用 additive 混合、誇張權重與多樣 speed，營造『混爆』層次。\n\n💡 重要提示：\n1. 權重加總建議約 1.0，否則可能不自然。\n2. 主動嘗試多種動畫組合與不同 speed（如 0.6/1.2/1.8）。\n3. 適合舞蹈、太空漂浮等複合動作情境。\n4. speed 建議介於 0.5~2.0（例如：'舞步1'=1.2，'漂浮'=0.7）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "animations": {
                        "type": "array",
                                "description": "要混合的動畫配置，每個元素包含動畫名稱、權重、是否循環、播放速度（speed 建議 0.5~2.0）。必須包含『空體Action』（速度≥1.6，建議1.8）與至少一個其他動作（速度≤0.8，建議0.6）。",
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
            "description": "🧠 記憶檢索工具！可以從記憶系統中獲取過往的對話、個性特徵、經驗摘要或聊天室留言。支援語義搜尋，能夠根據相關性找到最相關的記憶內容。用於了解用戶偏好、回憶過往互動、分析觀眾留言趨勢、保持對話連續性。新增聊天室留言記憶功能！",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_type": {
                        "type": "string",
                        "enum": ["conversation", "persona", "summary", "chat_message"],
                        "description": "記憶類型：conversation(對話記憶)、persona(人格記憶)、summary(摘要記憶)、chat_message(聊天室留言記憶-新功能！)"
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
            "description": "💾 記憶儲存工具！將重要的對話內容、用戶偏好、個性觀察或經驗摘要儲存到記憶系統中。這些記憶將幫助未來的對話更加個人化和連貫。主動儲存有意義的互動！注意：聊天室留言(chat_message)會自動存儲，不需要手動儲存。",
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
        },
        {
            "type": "function",
            "name": "analyze_exhibition_field",
            "description": "🔍 展場視覺分析工具！截圖展場視訊源並進行智能分析，了解展場即時狀況。僅進行分析與回傳結果，不會顯示到前端或更換背景。",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_focus": {
                        "type": "string",
                        "enum": ["general", "detailed", "exhibition"],
                        "description": "分析重點：general(一般描述)、detailed(詳細分析)、exhibition(展覽專業分析)，預設為exhibition",
                        "default": "exhibition"
                    }
                },
                "required": []
            }
        },
        {
            "type": "function",
            "name": "analyze_obs_scene",
            "description": "📺 OBS 場景智能分析工具！可以截圖並分析任意 OBS 來源（主螢幕、瀏覽器、展場視訊源等），支援單一來源分析或多來源對比分析。能智能理解不同來源的內容差異，幫助你全面了解直播狀況！",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_name": {
                        "type": "string",
                        "enum": ["主螢幕", "展場視訊源", "瀏覽器", "攝像頭", "桌面"],
                        "description": "要分析的 OBS 來源名稱，預設為「主螢幕」",
                        "default": "主螢幕"
                    },
                    "analysis_focus": {
                        "type": "string",
                        "enum": ["general", "detailed", "technical", "audience", "content", "streaming"],
                        "description": "分析重點：general(一般描述)、detailed(詳細分析)、technical(技術狀況)、audience(觀眾互動)、content(內容品質)、streaming(直播效果)，預設為general",
                        "default": "general"
                    },
                    "compare_sources": {
                        "type": "boolean",
                        "description": "是否進行多來源對比分析，比較不同 OBS 來源的差異，預設為false",
                        "default": False
                    }
                },
                "required": []
            }
        },
        {
            "type": "function",
            "name": "get_youtube_chat_messages",
            "description": "💬 YouTube 聊天室訊息獲取工具！讀取直播聊天室中觀眾的即時留言和互動。可以了解觀眾在說什麼、他們的反應和問題，讓你能即時回應觀眾！支援獲取最新訊息、搜尋特定關鍵字、查看特定使用者的留言。",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["recent", "search", "user_messages"],
                        "description": "查詢類型：recent(獲取最新訊息)、search(搜尋關鍵字)、user_messages(特定使用者訊息)",
                        "default": "recent"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回的訊息數量限制，建議5-20條",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "keyword": {
                        "type": "string",
                        "description": "搜尋關鍵字（當action為search時使用）"
                    },
                    "username": {
                        "type": "string",
                        "description": "使用者名稱（當action為user_messages時使用）"
                    }
                },
                "required": ["action"]
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
