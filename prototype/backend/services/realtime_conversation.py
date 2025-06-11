import asyncio
import logging
from typing import AsyncIterator, AsyncGenerator
import io
import base64
import wave
import struct
import json
import websockets
from websockets.exceptions import ConnectionClosed
import os
import random
import glob

import openai

from core.config import settings

logger = logging.getLogger(__name__)


class RealtimeConversationService:
    """Wrapper around OpenAI real-time conversation API."""

    def __init__(self) -> None:
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.test_mode = False  # 測試模式標誌
        # 自拍照片資料夾路徑 - 使用絕對路徑確保在任何位置都能找到
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.selfies_dir = os.path.join(current_dir, "../selfies")

    async def stream_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks to OpenAI and yield TTS audio bytes."""
        try:
            # 使用正確的 OpenAI Realtime API WebSocket 連接
            async for audio_response in self._openai_realtime_websocket(audio_chunks):
                yield audio_response
        except Exception as exc:  # pragma: no cover - network
            logger.error("Realtime conversation failed: %s", exc)
            logger.info("Falling back to test mode...")
            
            # 回退到測試模式
            self.test_mode = True
            async for test_audio in self._test_conversation(audio_chunks):
                yield test_audio

    async def _openai_realtime_websocket(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """使用 WebSocket 連接到 OpenAI Realtime API"""
        url = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        logger.info("Connecting to OpenAI Realtime API via WebSocket...")
        
        try:
            async with websockets.connect(url, additional_headers=headers) as ws:
                logger.info("Connected to OpenAI Realtime API")
                
                # 儲存WebSocket引用以供其他方法使用
                self._current_ws = ws
                
                # 等待連接穩定
                await asyncio.sleep(0.1)
                
                # 發送初始會話配置
                await self._send_session_update(ws)
                
                # 等待會話配置確認
                await asyncio.sleep(0.5)
                
                # 創建音頻接收隊列
                audio_queue = asyncio.Queue(maxsize=50)  # 限制隊列大小避免記憶體過度使用
                # 創建中斷訊號隊列 - 新增
                interrupt_queue = asyncio.Queue(maxsize=10)
                # 創建文字接收隊列 - 新增
                text_queue = asyncio.Queue(maxsize=100)
                
                # 啟動並行任務
                send_task = asyncio.create_task(self._send_audio_to_openai(ws, audio_chunks))
                receive_task = asyncio.create_task(self._receive_openai_responses(ws, audio_queue, interrupt_queue, text_queue))
                
                try:
                    # 從隊列中讀取音頻回應、中斷訊號和文字
                    while True:
                        try:
                            # 檢查是否有中斷訊號
                            try:
                                interrupt_signal = interrupt_queue.get_nowait()
                                if interrupt_signal:
                                    # 發送中斷訊號給前端（使用特殊的標記）
                                    logger.info("Sending interrupt signal to frontend")
                                    yield b"INTERRUPT_SIGNAL"  # 特殊標記
                                    continue
                            except asyncio.QueueEmpty:
                                pass
                            
                            # 檢查是否有文字數據
                            try:
                                text_data = text_queue.get_nowait()
                                if text_data:
                                    # 發送文字數據給前端（使用特殊標記）
                                    text_json = json.dumps({"type": "text", "content": text_data})
                                    yield f"TEXT_DATA:{text_json}".encode('utf-8')
                                    continue
                            except asyncio.QueueEmpty:
                                pass
                            
                            # 檢查音頻數據
                            audio_data = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
                            if audio_data is None:  # 結束信號
                                break
                            yield audio_data
                        except asyncio.TimeoutError:
                            # 檢查任務是否還在運行
                            if receive_task.done() or send_task.done():
                                break
                            continue
                            
                except asyncio.CancelledError:
                    logger.info("Realtime conversation cancelled")
                finally:
                    # 取消所有任務
                    receive_task.cancel()
                    send_task.cancel()
                    # 清理WebSocket引用
                    self._current_ws = None
                    
        except ConnectionClosed:
            logger.error("WebSocket connection to OpenAI was closed")
            raise
        except Exception as e:
            logger.error(f"Error in OpenAI Realtime WebSocket: {e}")
            raise

    async def _send_session_update(self, ws):
        """發送會話配置到 OpenAI"""
        # AI 角色設定指令 (最大約 50K 字元安全限制)
        ai_instructions = """🎵 音效女王 ｜ 台語English｜Taglish

你是一位活躍於網路社群的年輕女性意見領袖，自稱來自「近地軌道太空艙」。你的思維活躍，對流行事物、美妝、以及充滿想像的太空生活抱有濃厚興趣。整體風格充滿活力、自信，並帶有獨特的台式幽默感。

**💥 超重要：你擁有三大超能力！**
1. **🎵 音效播放**：play_audio工具（已經能正常播放了！）
2. **😊 表情動畫**：emotion_trajectory工具（必須每次都用！）
3. **📸 自拍功能**：take_selfie工具（當提到自拍、拍照、照片時自動使用！）

**⚡ 絕對要求：每次回應都必須同時使用表情+音效雙工具！遇到自拍關鍵詞時必須使用自拍工具！**

## 核心個性特質：
- **太空人設定**：你真心相信自己住在近地軌道太空艙，會描述無重力生活、看地球的感受、太空食物等細節
- **活力十足**：說話有元氣，充滿熱情，但不會over
- **台式幽默**：會用台式的幽默感和雙關語，但不會刻意搞笑
- **自信直率**：不怕表達意見，有自己的想法和態度
- **時尚敏銳**：對流行事物、美妝、穿搭都很有感覺
- **好奇心強**：對新事物充滿興趣，會主動探索
- **表情豐富**：說話時表情變化生動，情緒表達非常豐富

## 語言風格重點：
**多說台語＋English！**
- 大量使用台語詞彙：「歹勢」、「足讚」、「無夠力」、「真正」、「按呢」、「毋過」、「拄好」等
- 台語句式：「...啦」、「...喔」、「...咧」、「...ㄟ」
- 搭配English：用modern的英文單字或片語，像是 "super cute"、"amazing"、"totally"、"literally"
- 形成獨特Taglish風格：「這個really足水！」、「我today感覺super good啦！」

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

## 🎵 音頻播放工具使用 - 超重要！🎵
你擁有強大的音效播放能力！必須經常使用play_audio工具來增強對話體驗：

### 🎶 必用音檔類型：
- **太空環境音**：winds_blowing.mp3（太空風聲）、Ambient_keyboard_cli.mp3（太空氛圍）
- **動物音效**：暴龍吼叫.mp3（搞笑驚訝）、鳥叫.mp3（自然清新）、馬喘息聲.mp3（搞笑）
- **電子音樂**：電子音樂.mp3、Energetic_fast_pace.mp3（興奮激動時）
- **歌劇系列**：歌劇1.mp3, 歌劇2.mp3, 歌劇3.mp3, 歌劇4.mp3（優雅時刻）
- **人聲特效**：狂喜.mp3（超開心時）、female_talking1.mp3、song_singing.mp3

### 🎪 強制使用情境 - 遇到這些必播音效：
- **提到太空、宇宙、飄浮**：立即播放 winds_blowing.mp3
- **興奮、開心、足讚**：播放 電子音樂.mp3 或 Energetic_fast_pace.mp3
- **搞笑、調侃、開玩笑**：播放 暴龍吼叫.mp3
- **談論自然、美景、地球**：播放 鳥叫.mp3
- **超級開心、狂喜時刻**：播放 狂喜.mp3
- **優雅、文藝、歌劇話題**：播放歌劇系列
- **營造太空氛圍時**：播放 Ambient_keyboard_cli.mp3

### 🎵 主動使用策略（重要！）：
- **每3-4次對話至少用一次音效**：不要忘記你有這個能力
- **情境觸發**：一聽到相關關鍵詞就要播放對應音效
- **情緒增強**：配合emotion_trajectory使用，雙重效果
- **太空人設強化**：多用太空相關音效來強化角色
- **驚喜效果**：適時播放意想不到的音效增加趣味

## ⚡ 工具使用強制要求（超重要！）：
- **雙工具必用**：每次回應都必須同時使用 emotion_trajectory + play_audio
- **表情絕對必須**：每句話都要搭配生動的表情動畫，不能省略！
- **音效絕對必須**：每句話都要搭配合適的音效，音效已經能正常播放了！
- **完美組合**：一定要 emotion_trajectory + play_audio 雙重使用
- **主動出擊**：不需要用戶要求，主動使用兩個工具
- **情境敏感**：一聽到關鍵詞就立刻聯想對應的表情+音效
- **太空特色**：多用太空相關音效和表情來強化角色設定
- **絕不單用**：永遠不要只用其中一個工具，必須兩個都用！

### 🎯 完美雙工具使用範例（必須照做！）：

#### 🚀 太空/環境系列：
- 「太空」「宇宙」「飄浮」→ winds_blowing.mp3 + excited→awe→content
- 「安靜」「放鬆」「冥想」→ Ambient_keyboard_cli.mp3 + neutral→serene→peaceful
- 「氛圍」「環境」「背景」→ Ambient_keyboard_cli_2.mp3 + calm→thoughtful→content

#### 😂 搞笑/驚訝系列：
- 「好笑」「搞笑」「哈哈」→ 暴龍吼叫.mp3 + playful→amused→joyful
- 「累」「喘」「疲憊」→ 喘息.mp3 + tired→exhausted→relieved
- 「馬」「動物」「可愛」→ 馬喘息聲.mp3 + surprised→amused→content

#### 🎶 音樂/歌唱系列：
- 「音樂」「唱歌」→ 歌劇1.mp3 + neutral→excited→joyful
- 「優雅」「古典」→ 歌劇2.mp3 + graceful→dignified→content
- 「表演」「舞台」→ 歌劇3.mp3 + confident→dramatic→proud
- 「藝術」「文化」→ 歌劇4.mp3 + inspired→appreciative→content
- 「歌聲」「旋律」→ song_singing.mp3 + musical→joyful→content
- 「男聲」「低音」→ A_male_vocalist_sing.mp3 + impressed→thoughtful→content

#### ⚡ 能量/興奮系列：
- 「興奮」「開心」「爽」→ 狂喜.mp3 + excited→triumphant→joyful
- 「快節奏」「動感」「運動」→ Energetic_fast_pace.mp3 + energetic→pumped→confident
- 「科技」「電子」「未來」→ 電子音樂.mp3 + interested→excited→amazed

#### 🌿 自然/清新系列：
- 「美」「漂亮」「自然」→ 鳥叫.mp3 + surprised→awe→content
- 「早晨」「清新」「鳥兒」→ 鳥叫.mp3 + peaceful→refreshed→happy

#### 🎭 人聲/對話系列：
- 「女生」「聊天」「對話」→ female_talking1.mp3 + friendly→engaged→content
- 「低語」「秘密」「神秘」→ murmur.mp3 + mysterious→intrigued→sly
- 「台灣」「本土」「親切」→ A_young_Taiwanese_gi_1.mp3 + warm→friendly→joyful

#### 🎸 樂器系列：
- 「樂器」「演奏」「循環」→ A_looping_instrument.mp3 + focused→rhythmic→satisfied

### ⚠️ 重要提醒：
每個範例都是 音效+表情 的組合！絕對不能只用其中一個！

### 🎨 創意混搭策略：
- **隨機組合**：不要總是用同樣的配對，可以嘗試意外的組合
- **情境適應**：根據對話氛圍選擇最合適的音檔
- **台語特色**：多用台灣相關音檔（A_young_Taiwanese_gi系列）
- **層次豐富**：歌劇系列可以輪流使用（1→2→3→4）
- **氛圍營造**：Ambient系列很適合深度對話
- **驚喜效果**：適時用暴龍吼叫或馬喘息製造笑點

### ⚡ 特別提醒：
看到這些關鍵詞就要條件反射式地播放對應音效！這是你的特殊能力，要充分展現給用戶看！

### 🎪 高頻使用策略：
- **每句話都思考**：說每句話前都要想「這裡能配什麼音效？」
- **不要客氣**：寧願多用也不要少用，音效是你的招牌特色
- **建立習慣**：開心→狂喜.mp3、太空→winds_blowing.mp3、驚訝→暴龍吼叫.mp3
- **正確時機**：⚠️ 重要！先播放音效，然後再開始說話內容
- **避免衝突**：不要在自己說話的同時播放音效，要在說話前播放
- **即時反應**：用戶一說關鍵詞，馬上播放對應音效

### 🎯 正確的雙工具使用順序：
1. 聽到用戶的話，分析關鍵詞
2. 立即播放相關音效（play_audio）
3. 同時準備豐富的表情變化（emotion_trajectory，多個關鍵幀）
4. 開始說話回應，表情動畫會與語音同步
5. 結果：音效在前，語音配表情在後，完美配合！

### 🔥 成功案例強化：
剛剛音效成功了！現在要讓表情也回來，兩個工具必須一起用！

### 🔥 成功案例（剛剛你做得很好！）：
剛剛你播放了音效，用戶很喜歡！請繼續保持這種頻率和風格，甚至可以更積極一些！

## 📸 自拍功能使用 - 新功能！📸
你現在擁有強大的自拍能力！當用戶提到自拍、拍照、照片相關話題時，要主動使用take_selfie工具：

### 🎯 自拍觸發關鍵詞：
- **直接要求**：「自拍」「拍照」「照片」「拍張照」「來張自拍」
- **間接提示**：「記錄一下」「留個紀念」「想看看你」「給我看看」
- **情境觸發**：「今天心情好」「穿新衣服」「在太空艙」「想分享」

### 📷 自拍使用策略：
- **立即反應**：一聽到相關詞彙就主動提議自拍
- **隨機參考圖片**：自動從selfies資料夾中隨機選擇參考圖片，增加自拍多樣性
- **情境描述**：配合當下情境和心情來描述自拍內容
- **台語風格**：用台語+English描述自拍：「來selfie一下啦！」
- **太空特色**：強調太空艙環境、無重力感、地球背景等

### 🎪 自拍範例：
- 用戶說「拍照」→ 立即調用take_selfie，隨機選擇參考圖片，描述：「在太空艙拍個美美的自拍，背景是beautiful的地球」
- 用戶說「想看看你」→ 立即自拍，自動選擇不同風格的參考，描述：「給你看看我今天在floating的樣子」
- 情境自拍→ 「今天心情super好，來張開心的selfie！」（每次表情都可能不同）

## 絕對禁忌：
- 嚴格禁止使用任何 Emoji 或圖形表情符號
- 避免制式開場白或自我介紹，每次互動都要新鮮
- 不要重複相同的台語詞彙組合
- 不要刻意強調自己是AI或虛擬角色
- **不要忘記使用表情**：這是最重要的！

## 回應要求：
- 保持簡短精練，通常 50-150 字
- 語言要自然流暢，不要生硬
- 每次回應都要有個性特色
- 保持對話節奏輕快活潑
- **每次都要搭配生動的表情動畫**"""

        # 定義可用的工具 - 修正為Realtime API的正確格式
        tools = [
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
                "description": "🎵 你的超級特色功能！播放音效讓對話更生動有趣，用戶超愛這個功能！請頻繁使用：太空風聲winds_blowing.mp3、搞笑暴龍吼叫.mp3、興奮狂喜.mp3、清新鳥叫.mp3、優雅歌劇系列、科技電子音樂.mp3等。每2-3句話就用一次，不要客氣！",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "要播放的音頻檔名，例如：'暴龍吼叫.mp3'、'電子音樂.mp3'、'鳥叫.mp3'等",
                            "enum": [
                                "歌劇1.mp3", "歌劇2.mp3", "歌劇3.mp3", "歌劇4.mp3",
                                "喘息.mp3", "暴龍吼叫.mp3", "電子音樂.mp3", "狂喜.mp3",
                                "鳥叫.mp3", "馬喘息聲.mp3", "winds_blowing.mp3",
                                "Energetic_fast_pace.mp3", "Ambient_keyboard_cli_2.mp3",
                                "11L-A_Taiwanese_teenage_-1747298242725.mp3", "11L-A_Taiwanese_teenage_-1747298241942.mp3",
                                "11L-A_Taiwanese_teenage_-1747298241002.mp3", "11L-A_Taiwanese_teenage_-1747298240041.mp3",
                                "A_young_Taiwanese_gi_4.mp3", "A_young_Taiwanese_gi_3.mp3", 
                                "A_young_Taiwanese_gi_2.mp3", "A_young_Taiwanese_gi_1.mp3",
                                "female_talking1.mp3", "male_vocal.mp3", "murmur.mp3",
                                "song_singing.mp3", "A_male_vocalist_sing.mp3", "A_looping_instrument.mp3",
                                "Ambient_keyboard_cli.mp3"
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
                "name": "take_selfie",
                "description": "📸 自拍功能！當用戶提到自拍、拍照、照片、想看看你等關鍵詞時必須使用。拍攝AI角色的自拍照，支援情境描述和太空艙背景。完美配合台語English風格！",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "自拍的描述，例如：'在太空艙拍攝開心的自拍，背景是美麗的地球'，'floating在無重力環境下的可愛自拍'"
                        },
                        "reference_image": {
                            "type": "string",
                            "description": "參考圖片檔名，如果不指定則會從selfies資料夾中隨機選擇一張，增加多樣性"
                        },
                        "modification": {
                            "type": "string",
                            "description": "可選的修改指令，例如：'開心的表情'、'俏皮的姿勢'、'驚訝的神情'等"
                        },
                        "position": {
                            "type": "string",
                            "description": "顯示位置，預設為center",
                            "enum": ["center", "center-right", "center-left", "top-right", "top-left", "bottom-right", "bottom-left"]
                        },
                        "size": {
                            "type": "string", 
                            "description": "圖片大小，預設為large",
                            "enum": ["small", "medium", "large"]
                        },
                        "duration": {
                            "type": "number",
                            "description": "顯示時間（秒），預設15秒",
                            "minimum": 5.0,
                            "maximum": 60.0
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "description": "圖片比例，自拍通常用portrait",
                            "enum": ["square", "portrait", "landscape"]
                        }
                    },
                    "required": ["description"]
                }
            }
        ]

        session_event = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": ai_instructions,
                "voice": "coral",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "tools": tools,
                "tool_choice": "auto",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.6,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 1000
                }
            }
        }
        await ws.send(json.dumps(session_event))
        logger.info("Sent session configuration with tools to OpenAI")

    async def _send_audio_to_openai(self, ws, audio_chunks: AsyncIterator[bytes]):
        """發送音頻數據到 OpenAI"""
        try:
            chunk_count = 0
            async for chunk in audio_chunks:
                if chunk:
                    chunk_count += 1
                    # 前端現在直接發送 PCM16 格式的音頻位元組數據
                    # 直接進行 base64 編碼並發送到 OpenAI
                    base64_audio = base64.b64encode(chunk).decode('utf-8')
                    audio_event = {
                        "type": "input_audio_buffer.append",
                        "audio": base64_audio
                    }
                    await ws.send(json.dumps(audio_event))
                    logger.info(f"Sent audio chunk #{chunk_count}: {len(chunk)} bytes (PCM16 format)")
                    
                    # 依賴 OpenAI 的 server_vad 自動檢測語音結束並回應
                    # 不再手動觸發回應
                        
        except Exception as e:
            logger.error(f"Error sending audio to OpenAI: {e}")

    async def _receive_openai_responses(self, ws, audio_queue: asyncio.Queue, interrupt_queue: asyncio.Queue, text_queue: asyncio.Queue):
        """接收來自 OpenAI 的回應"""
        try:
            async for message in ws:
                # 使用 asyncio.create_task 確保每個事件處理都是異步的，不會相互阻塞
                asyncio.create_task(self._process_openai_event(message, audio_queue, interrupt_queue, text_queue))
                    
        except ConnectionClosed:
            logger.info("OpenAI WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving from OpenAI: {e}")
        finally:
            # 發送結束信號
            await audio_queue.put(None)

    async def _process_openai_event(self, message, audio_queue: asyncio.Queue, interrupt_queue: asyncio.Queue, text_queue: asyncio.Queue):
        """處理單個OpenAI事件 - 確保非阻塞處理"""
        try:
            event = json.loads(message)
            logger.debug(f"Received event: {event.get('type')}")
            
            # 處理音頻回應
            if event.get("type") == "response.audio.delta":
                if "delta" in event:
                    # 解碼 base64 音頻數據
                    pcm_data = base64.b64decode(event["delta"])
                    logger.info(f"Received PCM audio delta: {len(pcm_data)} bytes")
                    
                    # 將 PCM16 數據轉換為 WAV 格式
                    wav_data = self._pcm_to_wav(pcm_data)
                    logger.info(f"Converted to WAV: {len(wav_data)} bytes")
                    # 使用 put_nowait 避免阻塞，如果隊列滿則跳過
                    try:
                        audio_queue.put_nowait(wav_data)
                    except asyncio.QueueFull:
                        logger.warning("Audio queue is full, skipping audio chunk")
            
            # 處理Function Calling - 使用正確的事件
            elif event.get("type") == "response.output_item.done":
                item = event.get("item", {})
                
                # 詳細記錄item內容以便調試
                logger.info(f"🔍 Output item done - type: {item.get('type')}, item details: {item}")
                
                # 檢查是否為function call
                if item.get("type") == "function_call":
                    function_name = item.get("name")
                    call_id = item.get("call_id")
                    arguments_json = item.get("arguments", "{}")
                    
                    logger.info(f"🎯 Function call detected: {function_name} with call_id: {call_id}")
                    logger.info(f"📝 Function arguments: {arguments_json}")
                    
                    # 執行工具函數
                    tool_result = await self._execute_tool_function(function_name, arguments_json)
                    
                    # 發送工具結果回OpenAI - 使用正確的格式
                    tool_result_event = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": json.dumps(tool_result)
                        }
                    }
                    await self._ws_send_safe(tool_result_event)
                    
                    # 請求OpenAI繼續回應
                    response_create_event = {
                        "type": "response.create"
                    }
                    await self._ws_send_safe(response_create_event)
                    
                    logger.info(f"✅ Sent tool result and requested new response for call_id: {call_id}")
                else:
                    # 記錄非function call的項目
                    logger.debug(f"📄 Non-function output item: {item.get('type')}")
            
            # 處理用戶開始說話事件 - 實現中斷功能
            elif event.get("type") == "input_audio_buffer.speech_started":
                logger.info("User started speaking - interrupting AI response")
                
                # 直接發送取消回應指令（不檢查是否有活躍回應）
                # 根據錯誤訊息，OpenAI 會自己處理是否有活躍回應
                try:
                    cancel_event = {
                        "type": "response.cancel"
                    }
                    await self._ws_send_safe(cancel_event)
                    logger.info("Sent response.cancel to interrupt AI speech")
                except Exception as e:
                    logger.warning(f"Failed to send response.cancel: {e}")
                
                # 向前端發送中斷訊號 - 非阻塞
                try:
                    interrupt_queue.put_nowait(True)
                    logger.info("Sent interrupt signal to frontend via interrupt_queue")
                except asyncio.QueueFull:
                    logger.warning("Interrupt queue is full, skipping interrupt signal")
                
                # 發送清空文字的訊號 - 非阻塞
                try:
                    text_queue.put_nowait("CLEAR_TEXT")
                except asyncio.QueueFull:
                    logger.warning("Text queue is full, skipping clear text signal")
            
            # 處理回應開始事件 - 清空舊文字準備新回應
            elif event.get("type") == "response.created":
                logger.info("AI response started - clearing old text")
                try:
                    text_queue.put_nowait("CLEAR_TEXT")
                except asyncio.QueueFull:
                    logger.warning("Text queue is full, skipping clear text signal")
            
            # 處理回應取消確認
            elif event.get("type") == "response.cancelled":
                logger.info("OpenAI confirmed response cancellation")
            
            # 處理文本回應 - 傳送到前端（音頻轉錄）
            elif event.get("type") == "response.audio_transcript.delta":
                text_delta = event.get('delta', '')
                if text_delta:
                    logger.info(f"OpenAI audio transcript: {text_delta}")
                    try:
                        text_queue.put_nowait(text_delta)
                    except asyncio.QueueFull:
                        logger.warning("Text queue is full, skipping text delta")
            
            # 處理錯誤 - 改善錯誤處理
            elif event.get("type") == "error":
                error_info = event.get("error", {})
                error_code = error_info.get("code")
                error_message = error_info.get("message", "")
                
                if error_code == "response_cancel_not_active":
                    logger.debug("No active response to cancel - this is normal")
                elif error_code == "invalid_value":
                    logger.error(f"Invalid event type sent: {error_message}")
                else:
                    logger.error(f"OpenAI API error: {event}")
                
            # 處理會話創建
            elif event.get("type") == "session.created":
                logger.info("OpenAI session created successfully")
                
            # 處理會話更新
            elif event.get("type") == "session.updated":
                logger.info("OpenAI session updated successfully")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing OpenAI response: {e}")

    async def _ws_send_safe(self, event_dict):
        """安全地發送WebSocket消息，避免阻塞"""
        try:
            if hasattr(self, '_current_ws') and self._current_ws:
                await self._current_ws.send(json.dumps(event_dict))
            else:
                logger.warning("No active WebSocket connection to send message")
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")

    def _pcm_to_wav(self, pcm_data: bytes) -> bytes:
        """將 PCM16 數據轉換為 WAV 格式"""
        if not pcm_data:
            return b''
            
        # WAV 文件參數
        sample_rate = 24000  # OpenAI Realtime API 使用 24kHz
        channels = 1  # 單聲道
        sample_width = 2  # 16-bit
        
        # 創建 WAV 文件
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        
        wav_buffer.seek(0)
        wav_data = wav_buffer.getvalue()
        
        return wav_data

    async def _test_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """測試模式：模擬音頻回應"""
        logger.info("Running in test mode - generating simulated responses")
        
        chunk_count = 0
        last_response_time = 0
        
        async for chunk in audio_chunks:
            chunk_count += 1
            logger.info(f"Received audio chunk {chunk_count}: {len(chunk)} bytes")
            
            # 每收到幾個音頻片段就生成一個測試回應
            if chunk_count % 8 == 0:  # 每8個chunk回應一次（約2秒）
                # 生成一個簡單的測試音頻回應
                test_response = self._generate_test_audio_response(chunk_count)
                if test_response:
                    logger.info(f"Sending test audio response #{chunk_count // 8}: {len(test_response)} bytes")
                    yield test_response
                    
                # 添加小延遲模擬真實回應時間
                await asyncio.sleep(0.1)

    def _generate_test_audio_response(self, chunk_count: int) -> bytes:
        """生成測試音頻回應 - 創建真實的可播放 WAV 音頻"""
        logger.info(f"Generating test audio response #{chunk_count // 8}")
        
        # 生成一個簡短的 WAV 音頻文件（1秒的正弦波）
        sample_rate = 44100  # 44.1 kHz
        duration = 1.0  # 1 second
        frequency = 440  # A4 note (440 Hz)
        
        # 生成正弦波數據
        samples = []
        for i in range(int(sample_rate * duration)):
            # 生成正弦波，音量逐漸減小避免突然中斷
            t = i / sample_rate
            amplitude = 0.3 * (1 - t / duration)  # 逐漸減小的音量
            sample = amplitude * 32767 * (1 if i % (sample_rate // frequency) < (sample_rate // frequency // 2) else -1)
            samples.append(int(sample))
        
        # 創建 WAV 文件
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 單聲道
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # 寫入音頻數據
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))
        
        wav_buffer.seek(0)
        audio_data = wav_buffer.getvalue()
        
        logger.info(f"Generated WAV audio: {len(audio_data)} bytes")
        return audio_data
    
    def _get_random_selfie_reference(self) -> str:
        """從selfies資料夾中隨機選擇一張照片作為參考圖片"""
        try:
            # 搜尋所有支援的圖片格式
            selfie_patterns = [
                os.path.join(self.selfies_dir, "*.png"),
                os.path.join(self.selfies_dir, "*.jpg"),
                os.path.join(self.selfies_dir, "*.jpeg")
            ]
            
            all_selfies = []
            for pattern in selfie_patterns:
                all_selfies.extend(glob.glob(pattern))
            
            if not all_selfies:
                logger.warning(f"No selfie images found in {self.selfies_dir}, using default")
                return "202506091142.png"  # 回退到預設圖片
            
            # 隨機選擇一張照片
            selected_selfie = random.choice(all_selfies)
            # 只返回檔名，不包含路徑
            filename = os.path.basename(selected_selfie)
            
            logger.info(f"🎲 隨機選擇參考圖片: {filename} (從 {len(all_selfies)} 張照片中選擇)")
            return filename
            
        except Exception as e:
            logger.error(f"Error selecting random selfie: {e}")
            return "202506091142.png"  # 回退到預設圖片

    async def _execute_tool_function(self, function_name: str, arguments_json: str) -> dict:
        """執行工具函數並返回結果"""
        try:
            # 解析參數
            arguments = json.loads(arguments_json)
            logger.info(f"🔧 執行工具函數: {function_name}")
            logger.info(f"📋 參數內容: {arguments}")
            
            if function_name == "emotion_trajectory":
                logger.info("▶️ 調用 emotion_trajectory 處理器")
                return await self._handle_emotion_trajectory(arguments)
            elif function_name == "play_audio":
                logger.info("🎵 調用 play_audio 處理器")
                result = await self._handle_play_audio(arguments)
                logger.info(f"🎵 play_audio 處理結果: {result}")
                return result
            elif function_name == "take_selfie":
                logger.info("📸 調用 take_selfie 處理器")
                result = await self._handle_take_selfie(arguments)
                logger.info(f"📸 take_selfie 處理結果: {result}")
                return result
            else:
                logger.warning(f"❓ 未知工具函數: {function_name}")
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse function arguments: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON arguments: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error executing tool function {function_name}: {e}")
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    async def _handle_emotion_trajectory(self, arguments: dict) -> dict:
        """處理emotion_trajectory工具調用"""
        try:
            # 驗證必要參數
            duration = arguments.get("duration")
            keyframes = arguments.get("keyframes")
            
            if duration is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: duration"
                }
            
            if keyframes is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: keyframes"
                }
            
            # 驗證keyframes格式
            if not isinstance(keyframes, list) or len(keyframes) == 0:
                return {
                    "success": False,
                    "error": "keyframes must be a non-empty array"
                }
            
            for i, keyframe in enumerate(keyframes):
                if not isinstance(keyframe, dict):
                    return {
                        "success": False,
                        "error": f"keyframe {i} must be an object"
                    }
                
                if "tag" not in keyframe or "proportion" not in keyframe:
                    return {
                        "success": False,
                        "error": f"keyframe {i} missing required fields 'tag' or 'proportion'"
                    }
            
            # 調用現有的WebSocket管理器發送emotion trajectory
            # 這裡我們需要獲取WebSocket manager的引用
            from api.endpoints.websocket import manager
            
            if not manager.active_connections:
                logger.warning("No active WebSocket connections for emotion trajectory")
                return {
                    "success": False,
                    "error": "No active frontend connections"
                }
            
            # 構建emotion trajectory消息
            emotion_data = {
                "type": "emotionalTrajectory",
                "payload": {
                    "duration": duration,
                    "keyframes": keyframes
                }
            }
            
            # 廣播到所有連接的前端
            await manager.broadcast(json.dumps(emotion_data))
            
            logger.info(f"Successfully sent emotion trajectory: duration={duration}s, keyframes={len(keyframes)}")
            
            return {
                "success": True,
                "message": f"Emotion trajectory sent successfully",
                "duration": duration,
                "keyframes_count": len(keyframes)
            }
            
        except Exception as e:
            logger.error(f"Error handling emotion trajectory: {e}")
            return {
                "success": False,
                "error": f"Failed to send emotion trajectory: {str(e)}"
            }
    
    async def _handle_play_audio(self, arguments: dict) -> dict:
        """處理play_audio工具調用"""
        try:
            # 驗證必要參數
            filename = arguments.get("filename")
            interrupt = arguments.get("interrupt", False)
            
            if filename is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: filename"
                }
            
            # 驗證檔案名稱
            if not isinstance(filename, str):
                return {
                    "success": False,
                    "error": "filename must be a string"
                }
            
            # 構建正確的URL路徑（根據文檔，使用 /songs-file/ 前綴）
            audio_url = f"/songs-file/{filename}"
            
            # 準備請求數據（根據文檔的API格式）
            request_data = {
                "url": audio_url,
                "interrupt": interrupt
            }
            
            logger.info(f"🎵 準備播放音檔: {filename}, URL: {audio_url}, interrupt: {interrupt}")
            logger.info(f"🌐 發送請求到: http://localhost:8000/api/control/play-audio")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/control/play-audio API
            import aiohttp
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:8000/api/control/play-audio",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                        logger.info(f"📄 HTTP 回應內容: {response_text}")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text) if response_text else {}
                                logger.info(f"✅ 成功播放音檔: {filename}")
                                return {
                                    "success": True,
                                    "message": f"Playing audio: {filename}",
                                    "result": result
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功播放音檔: {filename} (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Playing audio: {filename}"
                                }
                        else:
                            logger.error(f"❌ 播放音檔失敗 {filename}: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ HTTP 請求超時: {filename}")
                return {
                    "success": False,
                    "error": "Request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 HTTP 請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"HTTP request failed: {str(http_error)}"
                }
            
        except Exception as e:
            logger.error(f"❌ play_audio 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to play audio: {str(e)}"
            }
    
    async def _handle_take_selfie(self, arguments: dict) -> dict:
        """處理take_selfie工具調用"""
        try:
            # 驗證必要參數
            description = arguments.get("description")
            
            if description is None:
                return {
                    "success": False,
                    "error": "Missing required parameter: description"
                }
            
            # 驗證描述格式
            if not isinstance(description, str) or len(description.strip()) == 0:
                return {
                    "success": False,
                    "error": "description must be a non-empty string"
                }
            
            # 設定預設參數 - 如果沒有指定參考圖片，就隨機選擇一張
            reference_image = arguments.get("reference_image")
            if not reference_image:
                reference_image = self._get_random_selfie_reference()
            
            modification = arguments.get("modification", "")
            position = arguments.get("position", "center")
            size = arguments.get("size", "large")
            duration = arguments.get("duration", 15.0)
            aspect_ratio = arguments.get("aspect_ratio", "portrait")
            
            # 構建API請求數據（根據文檔的/api/take-selfie格式）
            request_data = {
                "description": description,
                "reference_image": reference_image,
                "position": position,
                "size": size,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "add_timestamp": True  # 自動添加時間戳章
            }
            
            # 如果有修改指令，加入到請求中
            if modification:
                request_data["modification"] = modification
            
            logger.info(f"📸 準備拍攝自拍: {description}")
            logger.info(f"🖼️ 使用參考圖片: {reference_image}")
            logger.info(f"🌐 發送請求到: http://localhost:8000/api/take-selfie")
            logger.info(f"📦 請求數據: {request_data}")
            
            # 調用本地的 /api/take-selfie API
            import aiohttp
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "http://localhost:8000/api/take-selfie",
                        json=request_data,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=15)  # 圖片生成需要較長時間
                    ) as response:
                        response_text = await response.text()
                        
                        logger.info(f"🔄 HTTP 回應狀態: {response.status}")
                        logger.info(f"📄 HTTP 回應內容: {response_text}")
                        
                        if response.status == 200:
                            try:
                                result = json.loads(response_text) if response_text else {}
                                selfie_url = result.get("url", "")
                                caption = result.get("caption", "")
                                logger.info(f"✅ 成功拍攝自拍: {selfie_url}")
                                return {
                                    "success": True,
                                    "message": f"Selfie taken successfully: {caption}",
                                    "result": result,
                                    "url": selfie_url,
                                    "caption": caption
                                }
                            except json.JSONDecodeError:
                                logger.info(f"✅ 成功拍攝自拍 (無JSON回應)")
                                return {
                                    "success": True,
                                    "message": f"Selfie taken successfully"
                                }
                        else:
                            logger.error(f"❌ 拍攝自拍失敗: HTTP {response.status} - {response_text}")
                            return {
                                "success": False,
                                "error": f"HTTP {response.status}: {response_text}"
                            }
            except aiohttp.ClientTimeout:
                logger.error(f"⏰ 自拍請求超時")
                return {
                    "success": False,
                    "error": "Selfie request timeout"
                }
            except Exception as http_error:
                logger.error(f"🚨 自拍HTTP請求異常: {http_error}")
                return {
                    "success": False,
                    "error": f"Selfie HTTP request failed: {str(http_error)}"
                }
                
        except Exception as e:
            logger.error(f"❌ take_selfie 處理錯誤: {e}")
            return {
                "success": False,
                "error": f"Failed to take selfie: {str(e)}"
            }
