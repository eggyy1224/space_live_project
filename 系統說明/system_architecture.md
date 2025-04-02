```mermaid
flowchart TD
    subgraph 展場環境
        A[現場觀眾] -->|按下按鈕啟動麥克風| B[麥克風收音]
        B -->|語音辨識轉文字| I[FastAPI後端系統]
        J[展示螢幕顯示太空人反應與語音回覆] --> A
        I -->|合成語音輸出| SP[現場喇叭播放語音回應]
    end

    subgraph 前端系統["前端系統 - React + Three.js + react-three-fiber"]
        I <-->|API回應含動作表情語音| C[React應用]
        C -->|渲染3D互動畫面| D[Three.js場景]
        D -->|載入GLB/GLTF模型| E[太空人3D模型]
        E -->|表情控制| F[表情管理器MorphTarget]
        E -->|動作控制| G[骨骼動畫管理器]
        C -->|顯示互動動畫與表情| J
    end

    subgraph 後端系統["後端系統 - FastAPI + WebSocket"]
        I -->|語音辨識結果| STT[語音辨識服務 - STT API]
        STT -->|文字訊息| CM[互動協調模組]
        CM -->|文字處理| K[自然語言管理器 - Gemini API]
        K -->|記憶檢索與更新| L[記憶管理器LangGraph]
        K -->|生成文字回應| CM
        CM -->|文字轉語音| TTS[語音合成服務 - TTS API]
        CM -->|控制訊號| ANIM[動畫控制模組]
        TTS -->|合成語音| SP
        ANIM -->|動畫指令| C
    end

    subgraph 記憶系統["記憶系統 - PostgreSQL + pgvector"]
        L -->|記憶存取| P[PostgreSQL資料庫]
        L -->|向量檢索| Q[pgvector擴展]
    end

    subgraph 線上直播系統["線上直播系統"]
        J -->|即時串流| Z[線上觀眾]
        Z -->|觀看即時互動| J
    end

    subgraph 獨立聊天室系統["聊天室系統"]
        Z -->|文字聊天| X[即時聊天室 - Firebase或Socket.IO]
        X -->|文字訊息互動| Z
    end

%% 清楚說明調整部分
    style STT fill:#f96,stroke:#333,stroke-width:2px
    style TTS fill:#f96,stroke:#333,stroke-width:2px
    style CM fill:#f96,stroke:#333,stroke-width:2px
    style ANIM fill:#f96,stroke:#333,stroke-width:2px
    style A fill:#bbf,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style SP fill:#ff9,stroke:#333,stroke-width:2px
    style Z fill:#bfb,stroke:#333,stroke-width:2px
    style X fill:#ffb,stroke:#333,stroke-width:2px

%% 調整說明：
%% 1. 移除即時語音串流處理，改用STT語音辨識與TTS語音合成。
%% 2. 使用Gemini API處理文字訊息，而非即時串流API。
%% 3. 新增互動協調模組同步處理語音、表情和動作。
%% 4. 優化動畫控制流程，使用骨骼動畫與Morph Targets。

# 太空互動展覽系統架構文件

## 技術堆疊說明

### 前端技術
- **React**: 前端應用程式框架，負責用戶界面與互動邏輯
- **Three.js**: 3D繪圖引擎，負責太空人模型渲染與動畫
- **react-three-fiber**: React綁定Three.js的庫，簡化3D場景開發
- **WebSocket**: 實現前後端即時通訊

### 後端技術
- **FastAPI**: Python高效Web框架，處理API請求與WebSocket連接
- **WebSocket**: 提供即時雙向通訊
- **Pydantic**: 資料驗證與設定管理
- **Uvicorn**: ASGI伺服器，執行FastAPI應用

### AI技術
- **Gemini API**: Google AI大型語言模型，處理自然語言理解與生成
- **LangGraph**: 狀態管理與對話流程控制庫
- **PostgreSQL**: 關聯式資料庫，儲存對話記憶與系統資料
- **pgvector**: PostgreSQL向量搜尋擴展，實現語義檢索功能

### 語音技術
- **STT語音辨識**: 將觀眾語音轉換為文字（如Google Speech-to-Text）
- **TTS語音合成**: 將AI生成文字轉換為自然語音（如Google Text-to-Speech）

### 3D資產技術
- **GLB/GLTF**: 3D模型格式，用於太空人模型與場景
- **Blender**: 3D模型製作與動畫製作工具
- **MorphTargets**: 臉部表情控制技術
- **骨骼動畫**: 身體動作控制技術

## 互動協調模組設計

### 模組功能
互動協調模組是系統的核心，負責同步處理：
1. **語音輸出控制**：將生成的文字轉換為語音並控制播放
2. **表情動畫控制**：基於文字內容與情緒生成表情變化
3. **身體動畫控制**：根據對話意圖選擇並控制骨骼動畫

### 工作流程
1. 接收STT服務轉換後的文字訊息
2. 將文字傳送給Gemini API處理
3. 分析Gemini回應中的意圖與情緒
4. 生成協調控制指令：包含語音、表情和動作
5. 調用TTS服務生成語音檔案
6. 建立同步時間點，協調各元素的播放時機
7. 將控制訊息發送給前端執行

## 系統互動流程

1. **語音輸入階段**
   - 觀眾按下按鈕，啟動麥克風
   - 系統收集語音輸入，透過STT服務轉換為文字
   - 文字訊息傳送至互動協調模組

2. **處理理解階段**
   - 互動協調模組將文字傳送給Gemini API
   - Gemini API結合記憶系統生成適當回應
   - 系統分析回應中的情緒和意圖，為表情與動作做準備

3. **回應生成階段**
   - 文字回應傳送給TTS服務轉換為語音
   - 系統根據情緒與意圖生成適合的表情變化（Morph Targets）
   - 系統選擇合適的身體動作（骨骼動畫）

4. **同步呈現階段**
   - 互動協調模組建立播放時間線
   - 前端依據時間線同步執行聲音、表情與動作
   - 觀眾體驗到太空人的完整回應

## 系統優勢

1. **穩定性提升**：使用獨立的STT和TTS服務替代即時語音串流，降低系統複雜度與出錯機率
2. **協調性增強**：通過互動協調模組統一管理所有回應元素，確保行為連貫
3. **擴展性改善**：模組化設計使各組件可獨立升級與替換
4. **反應更自然**：精確控制表情與動作時機，創造更擬人化的互動體驗
5. **易於維護**：簡化的系統架構降低維護成本，提高系統可靠性

通過上述設計，系統能夠協調處理語音輸出、表情變化與肢體動作，使太空人呈現更自然、擬人化的互動體驗，同時保持系統架構簡潔明確。 