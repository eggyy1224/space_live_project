# 前端 Morph Target 載入與控制

前端**模型載入**與**Morph Target**控制的核心在於 `Model.tsx` 與 `MorphTargetControls.tsx`。`Model.tsx` 使用 React Three Fiber（RTF）的 `useGLTF` hook 載入 3D 角色模型（GLB 檔）並初始化模型的 **Morph Targets**（也稱為 Blend Shapes）。Morph Target 是 3D 模型中預先定義的頂點位置變化，用於表情與嘴型的動畫控制。載入模型後，`Model.tsx` 將模型添加到 Three.js 場景中，確保模型的 **morphTargetInfluences** 陣列正確初始化。

在 `MorphTargetControls.tsx`，前端通過 UI Slider 控制 Morph Target **影響權重**。每個 Slider 對應模型的一個 Morph Target，例如嘴巴開合、微笑、皺眉等。控制邏輯會讀取 Slider 的值（0 到 1），並即時更新模型對應 morphTarget 的影響值。例如，當使用者拖動「張嘴」Slider，內部邏輯會將模型 mesh 的 `morphTargetInfluences[index]` 設置為相應值，從而改變模型嘴巴開合程度。這些 Slider 通常綁定在前端 **狀態管理**（如 React useState 或全域的 ModelService）上，確保 UI 控件與 3D 模型狀態同步。總而言之，前端目前是**手動透過滑桿調整 morphTarget** 來實現表情變化。

# 後端 TTS 語音合成功能

後端在 `prototype/backend/services/speech_to_text.py` 中實作了 TTS（文字轉語音）。目前專案使用 **Google Cloud Text-to-Speech API**，透過提供文字輸入與語言參數，獲取對應的語音音訊。此功能支援**語音檔輸出**：後端會將合成的音訊以檔案或記憶體位元組形式儲存。由於 Google TTS API **無直接 viseme（嘴型）輸出**，我們需要額外的處理來獲取嘴型動畫時序資料。這可透過**Rhubarb Lip Sync** 完成，它是一款開源的 CLI 工具，可根據語音檔分析並輸出嘴型動畫所需的 viseme 序列。因此，後端可以在獲得 TTS 語音檔後，自動呼叫 Rhubarb 進行 viseme 分析，取得每個時間點對應的嘴型代號（如 A、B、C...X 等嘴型）。總結後端現況：**語音合成可產生音訊檔**，但需透過額外整合（Rhubarb）才能取得嘴型時序資料供前端使用。

# WebSocket 即時事件推送

前後端透過 WebSocket 進行即時通訊，程式碼位於 `prototype/backend/api/endpoints/websocket.py`。當後端有新的事件（例如對話回應、動畫指令）時，會透過 WebSocket Server 推送給連接的前端。在前端，`WebSocketService` 客戶端保持與後端的連線，並在收到訊息時觸發相應的處理。WebSocket 訊息通常採用 **JSON 格式**，包含事件類型與資料，例如：`{"type": "chat_response", "text": "..."}`  或 `{"type": "animation", "action": "...", "params": {...}}`。在目前架構中，前端的 `ModelService` 可能監聽到**動畫相關事件**（如表情參數更新），並將對應指令應用於 3D 模型。例如，當後端推送一條嘴型動畫指令，前端會解析該訊息並更新 Morph Target 或播放預先定義的動畫。**即時推送**確保了後端 AI 核心的狀態變化能同步反映到前端 UI 和 3D 模型上，達成即時互動。

# 整合 Rhubarb 與 TalkingHead 的方案

為了實現自動嘴型同步（Lip Sync），我們將整合 **Rhubarb**（語音轉嘴型時序）與 **TalkingHead**（實時驅動 3D 角色說話）。整合思路如下：

1. **語音轉嘴型（Viseme）分析**：當後端 TTS 產生語音後，使用 Rhubarb Lip Sync 分析該音訊檔，得到對應的嘴型序列和時間戳。Rhubarb 可輸出 JSON 格式，其中列出每個時間點應顯示的嘴型代號（如「A」到「X」九種嘴型）。例如，輸出可能為：`[{ time: 0.1, mouth: "B" }, { time: 0.2, mouth: "D" }, ...]`，表示在0.1秒時嘴型為B、0.2秒時轉為D等。這些嘴型代號對應 Ready Player Me 模型的 morph target，例如：「A」可能對應閉嘴、「B」對應張嘴等，我們需要根據模型的 blend shape 定義做好**對照表**。
2. **TalkingHead 實時動畫**：TalkingHead 是一個前端 JavaScript 類，可根據 viseme 時序驅動 3D 角色口型同步。我們可參考其實作，將 Rhubarb 輸出的 viseme 序列轉換為前端動畫指令。透過 TalkingHead 或自訂邏輯，我們讓模型的 Morph Target 在正確時間插值到目標值。例如，當 viseme 為「B」(張嘴)時，增加「張嘴」Morph Target 的權重，而在 viseme 為「X」（靜止嘴型）時將所有口型相關 Morph Target 權重歸零或回到閉嘴狀態。
3. **同步音訊與動畫**：確保前端播放語音的同時執行嘴型動畫。這需要**時間同步機制**：後端在推送 viseme 時序時，包含每個 viseme 的相對時間；前端在播放音訊（Audio元素或 Web Audio API）時，通過 `requestAnimationFrame` 或計時器，根據音訊播放進度來切換 Morph Target。指出此流程的重要步驟：後端音訊 -> Rhubarb viseme -> 前端同步嘴型。透過對音訊時長和 viseme 時間戳的校準，可實現精準的嘴型同步，不會出現聲畫不同步。
4. **資料結構與格式**：設計 WebSocket 傳遞的資料格式以攜帶音訊與嘴型資訊。建議新增一種事件類型，如 `"type": "tts_audio_viseme"`，其中包含 Base64 編碼的音訊數據與 viseme 時序。例如：

```json
json
CopyEdit
{
  "type": "tts_audio_viseme",
  "audio": "<Base64音檔>",
  "visemes": [
    {"t": 0.0, "shape": "X"},
    {"t": 0.1, "shape": "B"},
    {"t": 0.2, "shape": "C"},
    ...
  ]
}

```

前端接收到此訊息後，交由 `AudioService` 播放音訊，並由 `ModelService` 或專門的 LipSyncController 根據 viseme 清單驅動 Morph Target 動畫。

1. **前端處理邏輯**：在前端，我們將擴充 `ModelService` 或新增一個 hook 來處理嘴型同步。該邏輯在播放音訊時啟動一個循環，每幾毫秒檢查音訊播放的當前時間（currentTime），並對比下一個 viseme 時間點，如果已達到或超過該時間，則根據 viseme 的 shape 更新 Morph Target 值。為平滑過渡，可在相鄰 viseme 間做線性插值，使嘴型平順連續。TalkingHead 本身對不同語言 viseme 有對應模組，我們可參考其英文實作方式，將中文 viseme（透過 Rhubarb phonetic 模式分析得到）對應到模型的 blend shapes。

# 具體整合實作方案

整合過程需要前後端多處修改，以下提供具體步驟與檔案變更建議：

**1. 後端資料流修改：**

- *整合 Rhubarb CLI*：在 `speech_to_text.py` 的 TTS 流程中，於成功獲取音檔後，使用 Python 的 `subprocess` 呼叫 Rhubarb。例如：
    
    ```python
    python
    CopyEdit
    audio_path = "/tmp/tts_output.wav"
    # ... 呼叫 Google TTS API 將音訊存檔至 audio_path ...
    subprocess.run(["rhubarb", "-f", "json", "-o", "/tmp/visemes.json", audio_path])
    
    ```
    
    然後讀取 `/tmp/visemes.json` 檔內容，解析出 viseme 時序列表。
    
- *封裝 WebSocket 消息*：修改 `websocket.py`，在適當的位置（例如處理 TTS 回傳的邏輯處）構築前述的 JSON 資料。將音訊檔轉為 Base64 字串（或考慮傳輸二進制音訊），連同 viseme 列表一起通過 WebSocket 發送給前端。確保設置事件類型，如 `event = {"type": "tts_audio_viseme", "audio": audio_b64, "visemes": visemes_list}`。
- *非同步處理*：由於 TTS 和 Rhubarb 需要耗時，建議在後端使用非同步任務（例如 `asyncio` 或背景執行緒）執行，避免阻塞 WebSocket 主執行緒。完成後再透過 WebSocket 將結果推送。

**2. 前端接收與處理：**

- *擴充 WebSocketService*：在前端 `WebSocketService` 增加對 `"tts_audio_viseme"` 類型的處理邏輯。當收到消息時：
    - 提取音訊資料，轉成 Blob 建立音頻物件，由 Audio 元件播放。
    - 提取 viseme 時序，傳遞給模型控制模組（例如 `ModelService` 或新的 LipSyncController）。
- *動畫控制模組*：實作一個 `useLipSync(visemes)` 自訂 Hook 或在 `ModelService` 增加方法。例如：
    
    ```tsx
    typescript
    CopyEdit
    function playVisemes(visemes: VisemeTimeline) {
      const audio = new Audio(audioUrl);
      audio.play();
      let idx = 0;
      audio.ontimeupdate = () => {
        const t = audio.currentTime;
        if (idx < visemes.length && t >= visemes[idx].t) {
          applyMouthShape(visemes[idx].shape);
          idx++;
        }
      };
      audio.onended = () => resetMouthShape();
    }
    
    ```
    
    其中 `applyMouthShape(shape)` 根據 shape 代號調整對應的 Morph Target Slider 值或直接操控模型的 morphInfluences。例如 shape = "B"（張嘴）時，設定「口腔張合」Morph Target接近1，其餘嘴型相關 morph 減為0；shape 轉換時可以短時間內插值。
    
- *MorphTargetControls 調整*：如果目前 MorphTargetControls 僅用於手動控制，需在 LipSync 動畫期間接管控制權。可以暫時停用使用者對口型相關 Slider 的操作（或在動畫播放時覆蓋 Slider 的值），動畫結束後再恢復。

**3. TalkingHead 結合**：如果決定直接使用 TalkingHead 類別，可將其整合至前端項目：

- 引入 TalkingHead 的模組（JS或TS類）。初始化時提供參數：模型對象、TTS 文字或音訊URL等。配置 TalkingHead 使用**自訂 viseme 時序**模式（避免再次調用外部TTS）。
- TalkingHead 可允許外部傳入 viseme 序列並控制模型，因此我們可以將 Rhubarb 輸出的 viseme 序列傳入，讓它為我們處理插值與動畫。若無法順利對接，則按照上述自研方式處理即可。

**4. 測試與優化**：

- 驗證不同長度、語速的句子，調整 Rhubarb 分析模式（英文用 pocketsphinx、中文建議用 `-recognizer phonetic`）以提高嘴型識別準確度。
- 調整**嘴型映射表**：根據角色模型的 morph target，定義 A, B, C...X 各代號如何影響模型。例如模型也許有 15 個 blendshapes（包含表情與口型），我們只調用其中與口型相關的若干個（如 JawOpen、MouthSmile 等組合出所需形狀）。確保代號切換時嘴型自然。中提到 X 是靜止形狀，可映射為嘴微閉的默認狀態。
- 透過**內插**平滑動畫：Rhubarb 輸出離散的關鍵幀，我們可在相鄰幀之間加入過渡。例如下一幀時間是 t=0.2 且形狀不同於當前形狀，則從 t=0.1 到 0.2 期間漸進過渡。

**5. 建議檔案變更**：

- `prototype/backend/services/speech_to_text.py`: 在 TTS 完成後新增 Rhubarb 語音分析步驟，並返回 viseme 結果。
- `prototype/backend/api/endpoints/websocket.py`: 在接收到 TTS 請求或對話需要語音回覆時，組裝包含音訊與 viseme 的消息，使用 WebSocket 推送。
- `prototype/frontend/src/services/WebSocketService.ts`（假設存在）: 增加對 tts_audio_viseme 類型消息的處理，呼叫前端相應服務。
- `prototype/frontend/src/services/AudioService.ts`: 增強播放功能以支援從 WebSocket 接收的音訊資料（可能需要將 Base64 轉 Audio 對象）。
- `prototype/frontend/src/services/ModelService.ts`: 新增方法如 `playVisemeAnimation(visemes)` 控制模型口型。
- `prototype/frontend/src/components/MorphTargetControls.tsx`: 調整以配合自動嘴型動畫（例如在 prop 中接受一個「鎖定」狀態，在播放動畫時禁用手動控制）。

藉由上述整合方案，將 Rhubarb 的精準嘴型時序分析與前端實時 3D 模型驅動結合，可讓太空網紅角色的對話更加生動逼真，真正實現**語音與嘴型同步**的效果。