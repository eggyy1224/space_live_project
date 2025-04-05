# 在網頁上實現 Three.js + R3F 的 TTS 嘴型同步

## 1. TTS 技術選擇與取得語音時序標記

要在網頁即時將文字轉成語音並同步嘴型，首先要選擇適合的文字轉語音（TTS）方案。常見選項有：

- **瀏覽器 Web Speech API**：現代瀏覽器內建的語音合成功能，可直接使用 `SpeechSynthesis` 將文字轉語音，優點是**不需服務器**。然而，Web Speech API **僅能提供單詞或句子的邊界事件**（透過 `SpeechSynthesisUtterance.onboundary`），無法直接取得精細的音素/viseme 時間點。例如 Chrome 的實現會在講到每個單字時觸發 `boundary` 事件，我們可以取得該單字開始的時間 (`event.elapsedTime`) 和文字索引，但**沒有直接的音素級事件**。可考慮在文字中加入 SSML `<mark>` 標記，搭配 `SpeechSynthesisUtterance.onmark` 來手動標記時間點，但大多僅能標記到單字粒度。
    
    [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance/boundary_event#:~:text=The%20,a%20word%20or%20sentence%20boundary)
    
    [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance/boundary_event#:~:text=charIndex%20Read%20only)
    
- **雲端 TTS 服務**：如 Google Cloud Text-to-Speech、Microsoft Azure TTS、Amazon Polly、ElevenLabs 等。這些服務提供**高品質語音**，且部分服務允許取得語音中詞彙或音素的時間戳資訊：
    - *Google Cloud TTS*：支援 SSML `<mark>` 標籤來**返回自訂時間點**。可以在文本中插入 `<mark name="xyz"/>`，請求時設置 `enable_time_pointing` 或 `TimepointType=SSML_MARK`，則回傳音訊時會給出各標記相對音訊開頭的時間。不過 Google TTS **沒有直接提供音素級時間**，需要開發者在文本中對每個單字或音素插入 `<mark>` 取得近似時序。Google TTS 返回的是完整音訊（二進制或Base64），需自行播放。同時確保選用**支援 SSML `<mark>`*的語音類型（如Standard/Wavenet/Neural2等）。
        
        [cloud.google.com](https://cloud.google.com/text-to-speech/docs/ssml#:~:text=set%20a%20timepoint%20in%20your,the%20audio%20and%20the%20timepoint)
        
        [cloud.google.com](https://cloud.google.com/text-to-speech/docs/ssml#:~:text=match%20at%20L1166%20,appears%20in%20the%20generated%20audio)
        
        [cloud.google.com](https://cloud.google.com/text-to-speech/docs/ssml#:~:text=2.%20Set%20TimepointType%20to%20,are%20not%20returned%20by%20default)
        
        [github.com](https://github.com/met4citizen/TalkingHead#:~:text=%60ttsVoice%60%20Google%20text,A)
        
    - *Microsoft Azure Cognitive Services (Speech SDK)*：Azure 的語音合成支持**語音流事件**，可在合成過程中取得 viseme（嘴型）的編號或名稱，以及對應的時間點。使用 Azure Speech SDK（JavaScript）可以訂閱 `visemeReceived` 事件，每當合成語音到達某個音素的發音時，會提供一個 viseme ID（對應一組預定義嘴型）和相對時間。這讓我們**直接獲取嘴型動畫序列**。Azure 的 TTS 也支援 return 一系列 word boundary 事件與 phoneme 記號。
        
        [github.com](https://github.com/met4citizen/TalkingHead#:~:text=It%20is%20also%20possible%20to,sync%20support%20to%20100%2B%20languages)
        
    - *Amazon Polly*：AWS Polly 容許在請求合成時指定輸出**語音標記**（Speech marks），可以選擇輸出包括單字、標點和 viseme 等資訊的 JSON 列表。例如 Polly 在合成 “Mary had a little lamb” 時，可以返回如下標記序列：單詞 "Mary" 起始於時間6ms，接著 viseme `'p'`（閉嘴音）、`'E'`、`'r'`、`'i'` 等依次發生。這些 viseme**代表發音過程中的口形**，並帶有時間戳，有助於精準同步嘴型。
        
        [stackoverflow.com](https://stackoverflow.com/questions/67396896/how-to-get-phonemes-from-google-cloud-api-text-to-speech#:~:text=%7B,k)
        
        [stackoverflow.com](https://stackoverflow.com/questions/67396896/how-to-get-phonemes-from-google-cloud-api-text-to-speech#:~:text=%7B,k)
        
    - *ElevenLabs API*：ElevenLabs 提供高擬真的 AI 聲音，透過 HTTP 或 WebSocket API 請求。預設情況下 ElevenLabs API **僅返回音頻**，沒有直接的時間標記。然而，他們的**流式 API**（WebSocket）可以逐步傳送音訊片段，搭配一些對齊資訊。例如社群反饋指出 ElevenLabs 的 streaming API 能夠提供**單字對齊**（character alignment）的資料。雖然不像 AWS/Azure 有明確的 viseme 事件，但可以通過流式傳輸推斷單字開始時間，進而劃分音素區間。若需要更細緻的音素級同步，可考慮將 ElevenLabs 產生的音訊二次處理（見下述）。
        
        [github.com](https://github.com/met4citizen/TalkingHead#:~:text=It%20is%20also%20possible%20to,sync%20support%20to%20100%2B%20languages)
        

**整合方式**：若使用雲端 TTS，需要先將文字通過 AJAX/Fetch 傳至服務獲取音頻。取得音頻後，一種方法是在客戶端**創建 Audio 對象播放**，同時利用從服務返回的時間標記驅動動畫。例如，Google TTS 的 `<mark>` 返回時間點、Polly 的 viseme 時間、Azure 的 viseme 事件，都可用於驅動對應的嘴型 morph。在無法取得音素級時間的場合，另一方案是**後處理音訊**：拿到音頻後，使用額外工具分析它對應的音素或viseme（詳見下一節）。總的來說，理想方案是選擇**能提供時間戳**的 TTS 引擎，方便我們同步動畫

[github.com](https://github.com/met4citizen/TalkingHead#:~:text=By%20default%2C%20the%20class%20uses,sync%20language%20modules)

。

> 提示：有現成項目（如後述 TalkingHead 等）會利用 Google TTS 並結合 <mark> 標記取得單字級時間，再通過對單字預估音素的方法實現嘴型同步
> 
> 
> [github.com](https://github.com/met4citizen/TalkingHead#:~:text=service%20that%20can%20provide%20word,sync%20support%20to%20100%2B%20languages)
> 
> **直接提供 viseme**
> 

## 2. 音素與嘴型（Viseme）的對應方法

取得語音及時間點後，需要將語音中的**音素 (phoneme)** 對應到**嘴型 (viseme)**，再用於驅動模型的 morph target。音素是聲音的基本發音單位，而 viseme 則是某些音素對應的**視覺嘴部形狀**群組

[melindaozel.com](https://melindaozel.com/viseme-cheat-sheet/#:~:text=What%20is%20a%20viseme%3F)

。由於許多音素發音時嘴巴形狀相似，我們通常定義一組有限的 viseme，每個 viseme 代表一種嘴部形態，對應一組音素

[melindaozel.com](https://melindaozel.com/viseme-cheat-sheet/#:~:text=A%20viseme%20is%20a%20group,map%20to%20the%20same%20viseme)

。

**對應策略**有以下幾種：

- **預定義映射表**：這是最常見做法，人工定義音素到嘴型的映射。如英語中可採用 Preston Blair 經典的十個嘴形："AI", "O", "E", "U", "L", "WQ", "MBP", "FV", "etc", "rest"。每個嘴形對應一組音素，例如：。在實作時，我們可以建立一個 JavaScript 對照表，例如：`const phonemeToViseme = { "AA": "AI", "AE": "AI", "B": "MBP", ... }`，解析 TTS 輸出的音素序列，轉換成 viseme 名稱。
    
    [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27etc%27%2C%20,Blair%27s%20CDGKNRSThYZ%20mouth%20shape)
    
    - *「AI」嘴型*: 對應發 *A*, *I*, *Ah* 等張大嘴的母音；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=phoneme_conversion%20%3D%20)
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27AY0%27%3A%20%27AI%27%2C%20,AY%20D)
        
    - *「O」嘴型*: 對應 *O*, *AU* 等圓唇音；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27AH2%27%3A%20%27AI%27%2C)
        
    - *「E」嘴型*: 對應 *E*, *IY* 等齒齦接近的音；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27DH%27%3A%20%27etc%27%2C%20,IY)
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27EY0%27%3A%20%27E%27%2C%20,T)
        
    - *「MBP」嘴型*: 對應雙唇閉合音 *M*, *B*, *P*（完全閉嘴）；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27AY2%27%3A%20%27AI%27%2C)
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27L%27%3A%20%27L%27%2C%20,IY)
        
    - *「FV」嘴型*: 對應上齒下唇音 *F*, *V*（咬下唇）；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27EY2%27%3A%20%27E%27%2C)
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27F%27%3A%20%27FV%27%2C%20,IY)
        
    - *「L」嘴型*: 對應舌尖上揚音 *L*, *TH* 等（舌頂上顎）；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27K%27%3A%20%27etc%27%2C%20,IY)
        
    - *「WQ」嘴型*: 對應 *W*, *OO* 等突唇音；
    - *「etc」嘴型*: 其他所有輔音（如 *D*, *G*, *K*, *N*, *R*, *S*, *T*, *Z* 等) 歸為一類；
        
        [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27etc%27%2C%20,Blair%27s%20CDGKNRSThYZ%20mouth%20shape)
        
    - *「rest」嘴型*: 自然閉合的靜止嘴形（無發音時）。
    
    像 Papagayo 這類軟體就內建了上述映射，它將各語音的 CMU 音標自動轉換成上述 10 種嘴型
    
    [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=phoneme_conversion%20%3D%20)
    
    [github.com](https://github.com/andeon/papagayo/blob/master/phonemes_preston_blair.py#:~:text=%27AY2%27%3A%20%27AI%27%2C)
    
- **AI 模型預測**：使用訓練好的模型根據音頻直接預測嘴型參數（如 end-to-end 的 lipsync 模型）。例如 Nvidia 的 Audio2Face、或者一些研究論文模型，可以輸入整段語音波形，輸出每一幀對應的多個 blendshape 權重。這類方法效果好但通常**無即時瀏覽器方案**，多在本地或服務端運算。此外，Meta(Oculus)提供的 OVRLipSync 算法（Unity/原生可用）就是根據音頻算出一系列 viseme 索引，但在 Web 環境缺乏現成對應庫。
- **簡易音量/頻率啟發**：某些實作為了方便，使用音頻的**音量變化**來驅動一個開合嘴的 morph target（例如僅做嘴巴張合）。這種方法不需解析音素，但只能表現張嘴/閉嘴節奏，無法呈現**正確口形**。可將其作為輔助，例如在沒有特定音素對應時，讓嘴部張合跟隨音量。更精細的做法，可能對不同頻段能量或音素長度作 heuristics，但總體精度不如直接基於音素。

在實際應用中，**推薦使用預定義映射結合音素解析**。如果您的 TTS 引擎已提供音素序列或 viseme 序列，那直接利用其映射。例如：

- Azure Speech SDK 給出的 viseme ID 就可直接對應模型的嘴型鍵（Azure 預設一套 viseme清單，開發者可以在模型中實現相同命名的 morph）。
- 若拿到的是音素序列（如從 STT 對齊或預知文本），可以用 CMU Pronouncing Dictionary 等字典把單詞轉音素，再應用映射表。
- **中文的情況**：中文 TTS 通常基於拼音或注音符號作音素。如果模型有對應漢語**韻母/聲母嘴型**，可自行建立類似對照（如把ㄚㄞㄟㄠ歸類）。許多開源工具專注英語，但中文也可用同理方法：先取得拼音序列及聲調，然後映射到預定的口型（例如「ㄅ/ㄆ/ㄇ」→ 閉嘴，「ㄈ」→ 咬下唇，「ㄚ/ㄞ/ㄟ」→ 張大嘴，等等）。

**注意**：Viseme 的設計和數量取決於模型支持的 morph target。像 Apple ARKit 定義了包含嘴唇、下顎、舌頭等共15個語音相關blendshape；Oculus定義了一組Viseme（大約15種）專供嘴型同步。若使用 Ready Player Me 這類 Avatar，它內建 Oculus Viseme morph targets（命名如 `viseme_aa`, `viseme_CH`, `viseme_O`, `viseme_PP` 等）。在這種情況下，我們應使用**同樣的 viseme 列表**做映射，以匹配模型的 blendshape。例如 `phoneme "A"` 對應 `viseme_aa` morph

[medium.com](https://medium.com/@israr46ansari/integrating-a-ready-player-me-3d-model-with-lipsyncing-in-react-for-beginners-af5b0c4977cd#:~:text=The%20onboundary%20event%20listener%20detects,%E2%80%9D)

。

總之，我們需要先將文字或音頻**解析出音素及其時間區間**，再轉換成 viseme 名稱序列和強度。然後才能驅動下一步的 3D 模型變形。

## 3. 在 Three.js/R3F 中加載 GLB 並控制 Morph Targets 動畫

有了時間標記的 viseme 序列後，我們就可以在 Three.js/React Three Fiber 中控制 3D 人臉模型的 **Morph Target 權重** 來實現嘴型動畫同步。實現步驟如下：

- **模型準備與加載**：確保人臉模型（GLB/GLTF 格式）帶有 morph targets（又稱 blend shapes、形狀鍵）。可在 DCC 工具（Blender、Maya等）中為模型添加一系列嘴型的形變，如張嘴、撅嘴、咬唇等。加載模型時，使用 Three.js 的 `GLTFLoader`（在 R3F 中可用 `useGLTF` hook）載入。載入後，可從 `gltf.scene` 找到具體頭部網格(mesh)。通常 mesh 物件會有 `morphTargetDictionary`（鍵名對應 morph 索引）和 `morphTargetInfluences`（數值數組對應每個 morph 權重）屬性。在 R3F，`useGLTF` 會返回包含節點的物件，例如 `const { nodes } = useGLTF('/avatar.glb')`，然後 `nodes.Head.morphTargetDictionary` 即可取得字典。
- **初始化**：在動畫開始前，將所有 morph target 權重初始化為0（確保嘴巴處於基礎姿勢）。例如:
    
    ```
    js
    CopyEdit
    const faceMesh = nodes.Head;
    faceMesh.morphTargetInfluences.fill(0);
    
    ```
    
    如果模型頭部和下巴/牙齒是分開mesh，記得都要處理（如 Ready Player Me 模型嘴巴包含在 Teeth mesh）。
    
- **逐幀更新**：使用 R3F 的 `useFrame` hook 或 Three.js 的動畫循環，在每個渲染幀更新 morphTargetInfluences。需要根據目前音軌播放時間，決定應啟用哪個 viseme：
    1. **同步音頻播放**：將先前取得的語音音頻播放 (`Audio`或`AudioBufferSourceNode`) 並追蹤當前播放時間。例如可以使用 `audio.currentTime` 或自行累計時間。
    2. **查找當前 viseme**：根據播放時間落在哪個音素/viseme 時段，取出對應的 viseme 名稱。例如有序列：在00.1秒 -> "MBP"，0.10.2秒 -> "AI"，0.2~... -> "E"... 等，就選出當前時間的 viseme。
    3. **設置 morph 權重**：找到 viseme 對應的 morph target 索引，設置其 influence 接近1，其它降為0。為避免嘴型生硬跳變，可進行**平滑插值**。例如使用 Three.js 的線性插值函數:。另一種方式是使用動畫庫（GSAP、Tween.js）在幾十毫秒內補間權重。
        
        ```
        js
        CopyEdit
        // prevInfluences 保存上一幀的權重值
        const newWeight = THREE.MathUtils.lerp(prevInfluences[idx], targetValue, 0.2);
        faceMesh.morphTargetInfluences[idx] = newWeight;
        
        ```
        
        如此每幀慢慢逼近目標值，實現平順過渡
        
        [medium.com](https://medium.com/@israr46ansari/integrating-a-ready-player-me-3d-model-with-lipsyncing-in-react-for-beginners-af5b0c4977cd#:~:text=The%20avatar%E2%80%99s%20head%20and%20teeth,that%20define%20different%20mouth%20shapes)
        
        [stackoverflow.com](https://stackoverflow.com/questions/71951363/smooth-and-efficient-lipsync-with-morph-targets-in-three-js#:~:text=It%20depends%20on%20your%20use,CreateFromMorphTargetSequence)
        
    4. **重置先前 viseme**：當嘴型切換時，記得將上一個 viseme 對應的 morph 從1漸漸設回0，否則多個 morph 疊加可能扭曲。不使用動畫補間的簡單做法是在設置新 viseme 權重前，先將所有 `morphTargetInfluences` 清零，再給當前索引設值。但更好的效果是舊嘴型緩慢淡出、新嘴型淡入，兩者短暫共存以過渡自然。
        
        [stackoverflow.com](https://stackoverflow.com/questions/71951363/smooth-and-efficient-lipsync-with-morph-targets-in-three-js#:~:text=,morphTarget%20to%200)
        
        [stackoverflow.com](https://stackoverflow.com/questions/71951363/smooth-and-efficient-lipsync-with-morph-targets-in-three-js#:~:text=It%20depends%20on%20your%20use,CreateFromMorphTargetSequence)
        
- **範例**：假設模型有 morph target 名稱 `"viseme_aa"`、`"viseme_o"`, `"viseme_mbp"` 等：
    
    ```jsx
    jsx
    CopyEdit
    // 假設我們有 currentViseme 表示當前應呈現的嘴型名稱
    const meshRef = useRef();
    useFrame((state, delta) => {
      const mesh = meshRef.current;
      if (!mesh) return;
      // 將所有 morph 權重朝0逼近
      mesh.morphTargetInfluences.forEach((w, i) => {
        mesh.morphTargetInfluences[i] = THREE.MathUtils.lerp(w, 0, 0.1);
      });
      if (currentViseme) {
        const idx = mesh.morphTargetDictionary[currentViseme];
        // 將當前viseme的權重朝1逼近
        mesh.morphTargetInfluences[idx] = THREE.MathUtils.lerp(mesh.morphTargetInfluences[idx], 1, 0.3);
      }
    });
    
    ```
    
    上述代碼在每幀執行，讓非當前嘴型的 morph 權重漸漸歸零，而當前嘴型的 morph 權重漸漸提高到1。這樣在 viseme 切換時會有一兩幀的過渡（依照 lerp 的速率決定快慢），避免瞬間跳變。
    
- **語音事件驅動**：另一種方案是利用 TTS 提供的**事件回調**直接驅動畫面。例如使用 Web Speech API 時，`utter.onboundary` 事件（每當講到一個單字）被觸發時，可以**分析該單字的音素**並立即設置嘴型。Medium 範例顯示，可以在 `onboundary` 內取得當前發音的**音素**，轉換為 viseme 後存入 `currentViseme` state，R3F 的 `useFrame` 持續監聽該 state 更新嘴型。需注意 boundary 事件通常在單字邊界，若單字內有多個音素，仍需在該單字時間內做插值切換音素嘴型。可以通過預先將單字拆音素並假設平均時間劃分，或利用語音長度細分。
    
    [medium.com](https://medium.com/@israr46ansari/integrating-a-ready-player-me-3d-model-with-lipsyncing-in-react-for-beginners-af5b0c4977cd#:~:text=The%20onboundary%20event%20listener%20detects,%E2%80%9D)
    
    [medium.com](https://medium.com/@israr46ansari/integrating-a-ready-player-me-3d-model-with-lipsyncing-in-react-for-beginners-af5b0c4977cd#:~:text=The%20SpeechSynthesisUtterance%20breaks%20the%20text,sounds)
    

實踐中，如果 viseme 的持續時間較長，也可以**預生成Three.js AnimationClip**實現。例如使用 `AnimationClip.CreateFromMorphTargetSequence` 將一系列 morph target 關鍵幀生成 clip

[stackoverflow.com](https://stackoverflow.com/questions/71951363/smooth-and-efficient-lipsync-with-morph-targets-in-three-js#:~:text=GSAP%20or%20Tween,CreateFromMorphTargetSequence)

。但在TTS即時情境下，更靈活的是直接腳本控制 morphInfluences，如上所述。

## 4. 可參考的開源庫與工具

實現 TTS + 嘴型同步是一項複合任務，幸好已有一些工具和開源項目可以參考或使用：

- **D-ID API**（商業服務） – D-ID 提供AI驅動的“說話頭像”服務。給定一張人臉照片和語音（或文字），可生成對嘴的視頻。雖然非開源，但它**封裝了 TTS 與人臉動畫**，適合不想自己實作嘴型動畫的人使用。缺點是無法直接控制三維模型細節，而且使用需連網調用API，成本較高。比較適合快速產出影片或測試概念。
    
    [d-id.com](https://www.d-id.com/api/#:~:text=Boost%20Engagement%20With%20a%20Talking,time%21%20Try%20it%20now)
    
- **Papagayo**（開源軟體） – 一款傳統的嘴型同步工具。它允許使用者導入音訊和劇本文本，手動或自動對齊時間軸上的**音素與嘴型**。Papagayo 使用上述 Preston Blair 的10嘴型系統，並能將對齊結果輸出，例如 Moho 或 Blender 可讀的鍵幀數據。在本項目中，Papagayo 可用於**離線地預先生成**嘴型動畫：例如先用 TTS 得到音訊，再在 Papagayo 對該音訊生成對齊的嘴型時間表，然後將結果匯入Three.js。缺點是需要額外步驟，非全自動實時；但它的自動對齊算法（基於字典的簡單對齊）也可部分參考。
    
    [lostmarble.com](https://www.lostmarble.com/papagayo/#:~:text=What%20Is%20Papagayo%3F)
    
    [lostmarble.com](https://www.lostmarble.com/papagayo/#:~:text=Image%3A%20Papagayo%20Screenshot)
    
- **Rhubarb Lip Sync**（開源 CLI 工具） – 非常受歡迎的自動唇同步工具，命令行使用。輸入一段語音音頻（以及可選文本），Rhubarb 會輸出對應的**viseme 時間序列**（支援多種格式如 JSON、Dat）。它對英語的支持很好，生成的嘴型序列可直接用於動畫。例如 Wawa Sensei 的 R3F Lip Sync 教學項目中，就使用 ElevenLabs TTS 輸出音頻，再用 Rhubarb 萃取 viseme 時間，再映射到 3D 角色。Rhubarb 默認也用 Preston Blair 式嘴型，可產生每幀對應嘴型代號（例如 `"A"`, `"B"`, `"C"` 等代表不同口型）。在Web環境下，可以將 Rhubarb 編譯為 WebAssembly 後端運行，或在服務器上運行後將結果發回客戶端。這是一個**可靠的自動化解決方案**，尤其適合離線或輔助流程。
    
    [wawasensei.dev](https://wawasensei.dev/pt/tuto/react-three-fiber-tutorial-lip-sync#:~:text=%2A%20Generating%20text,with%20Eleven%20Labs)
    
    [wawasensei.dev](https://wawasensei.dev/pt/tuto/react-three-fiber-tutorial-lip-sync#:~:text=%2A%20Generating%20text,with%20Eleven%20Labs)
    
- **Oculus OVR LipSync**（SDK/算法） – Oculus提供的實時音頻->viseme 解算庫。在 Unity/原生平台上廣泛用於 VR 聊天的嘴型同步。其輸出 viseme 列表與 ReadyPlayerMe 預設 morph 對應。雖然 Oculus 沒有發布Web版，但有開發者將其思想移植到 Web（比如以 WebAudio 分析+ML 結合）。如果使用 Ready Player Me 模型，可參考其文檔了解 viseme 列表。另一相關的是 **Meta API Viseme Reference**，列出了每個 viseme 所對應的口型含義，可作為調整嘴型鍵時的指南。
    
    [docs.readyplayer.me](https://docs.readyplayer.me/ready-player-me/api-reference/avatars/morph-targets/oculus-ovr-libsync#:~:text=Oculus%20OVR%20LipSync%20,possible%20to%20build%20applications)
    
    [docs.readyplayer.me](https://docs.readyplayer.me/ready-player-me/api-reference/avatars/morph-targets/oculus-ovr-libsync#:~:text=Oculus%20OVR%20LipSync%20,possible%20to%20build%20applications)
    
    [developers.meta.com](https://developers.meta.com/horizon/documentation/unity/audio-ovrlipsync-viseme-reference/#:~:text=Viseme%20Reference%20,Below%20we%20give)
    
- **Talking Head (met4citizen/TalkingHead)**（開源項目） – 這是一個基於 Three.js 的完整即時虛擬人方案。它支持將 Ready Player Me 角色作為3D頭像，整合 GPT-3.5 聊天、Google TTS 語音合成、以及**內建的唇同步**模組。TalkingHead 項目中實現了多語言的嘴型同步，默認使用 Google TTS 並透過 `<mark>` 取得單字時間，再在客戶端對英語、芬蘭語等實現音素到 viseme 的規則映射。它也支持直接對接提供**時間戳/viseme**的服務（例如 ElevenLabs 流式API 或 Azure SDK）以增強同步精度。開發者可以參考其代碼瞭解如何**組織整個流程**：包括如何請求 TTS、解析返回的時間、以及在 Three.js 中驅動 morph 動畫。此外，它提供了現成的組件可供使用或修改。
    
    [github.com](https://github.com/met4citizen/TalkingHead#:~:text=Talking%20Head%20,convert%20them%20into%20facial%20expressions)
    
    [github.com](https://github.com/met4citizen/TalkingHead#:~:text=By%20default%2C%20the%20class%20uses,sync%20language%20modules)
    
    [github.com](https://github.com/met4citizen/TalkingHead#:~:text=It%20is%20also%20possible%20to,sync%20support%20to%20100%2B%20languages)
    
- **其他**：還有一些工具如 **Gentle**（強制對齊工具，將錄音和文本對齊到音素級，但比較重型），**Microsoft Viseme to Face** 示例（微軟有演示過 viseme 驅動 3D 臉部，搭配 Azure TTS），**Nvidia Audio2Face**（可利用深度學習自動給定音頻生成逼真表情，不過需要安裝專有軟體）等。如果追求品質且允許離線預處理，Audio2Face 等可產生高品質的 blendshape 動畫，再匯入網頁播放。

綜上，建議根據專案需要選用適合的方案：**即時性**要求高且不怕瀏覽器限制，可優先嘗試 Web Speech API + 客戶端簡易映射；**音質和同步**要求高的，可考慮雲端 TTS（Google/ElevenLabs）結合 Rhubarb 或 Azure 等獲取viseme；若希望減少自行實作，可利用現有開源項目（TalkingHead 等）作為基礎。透過合理整合上述技術，即可在網頁上實現文字輸入即時轉語音播放，同步驅動3D頭像做出口型動畫，營造出栩栩如生的對話角色效果。

- *參考資料：**Web Speech API 文檔

[developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance/boundary_event#:~:text=The%20,a%20word%20or%20sentence%20boundary)

、Ready Player Me 官方教程

[medium.com](https://medium.com/@israr46ansari/integrating-a-ready-player-me-3d-model-with-lipsyncing-in-react-for-beginners-af5b0c4977cd#:~:text=The%20onboundary%20event%20listener%20detects,%E2%80%9D)

[medium.com](https://medium.com/@israr46ansari/integrating-a-ready-player-me-3d-model-with-lipsyncing-in-react-for-beginners-af5b0c4977cd#:~:text=The%20avatar%E2%80%99s%20head%20and%20teeth,that%20define%20different%20mouth%20shapes)

、Wawa Sensei Lip Sync 教學

[wawasensei.dev](https://wawasensei.dev/pt/tuto/react-three-fiber-tutorial-lip-sync#:~:text=%2A%20Generating%20text,with%20Eleven%20Labs)

、TalkingHead 專案說明

[github.com](https://github.com/met4citizen/TalkingHead#:~:text=By%20default%2C%20the%20class%20uses,sync%20language%20modules)

等，提供了實現嘴型同步的關鍵技術點和範例實作。
