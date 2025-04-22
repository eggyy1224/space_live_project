# 🎧 SoundEffectPanel 重構 ＆ AudioCoordinator 設計藍圖（更新版）

## 0. 專案語境與現況回顧

| 重構動機                       | 目前問題                           | 目標                                 |
| ------------------------------ | ---------------------------------- | ------------------------------------ |
| 單一 `SoundEffectPanel` 功能龐雜 | UI 渾沌、維護困難、測試不易        | 「三面板 + 一協調器」模組化              |
| 聲音播放無統一排程               | 背景音、TTS、SFX 容易衝突            | 引入 `AudioCoordinator` 統一時間軸       |
| 無 ducking / 優先級            | 角色說話被背景音蓋過                 | 語音播放時自動壓低其他軌道音量（Ducking） |

**現況分析**：現有的音效控制面板 (`prototype/frontend/src/components/SoundEffectPanel.tsx`) 是一個龐大的單一元件，集成了播放音樂、合成音效以及 Freesound 音效搜尋等多項功能。在當前實作中，各種聲音來源（後端 TTS 語音、前端歌曲、音效）缺乏統一的管控，導致**維護困難**且**擴充性受限**。例如，當前若同時播放語音和背景音樂，兩者可能互相衝突，沒有機制協調音量或順序。為解決這些問題，我們將進行模組化拆分並引入**音訊協調器 (`AudioCoordinator`)**來統一管理所有聲音來源。

---

## 1. 面板拆分（UI Layer）

重構策略是將原先的 `SoundEffectPanel` 拆分為三個子元件，並由一個頂層容器 `SoundEffectPanelLayout` 負責選項卡切換與共享狀態分發。

| 子模組             | 功能摘要                                                              | 預計檔案位置                                     |
| ------------------ | --------------------------------------------------------------------- | ------------------------------------------------ |
| SongLibraryPanel   | • 歌曲清單呈現<br>• 播放 / 暫停 / 進度顯示<br>• 未來：分類、搜尋、波形視覺化 | `src/components/SongLibraryPanel.tsx` （新建）       |
| SynthPanel         | • Tone.js 合成器測試<br>• JSON 音符序列編輯<br>• 快速模板插入             | `src/components/SynthPanel.tsx` （新建）         |
| FreesoundPanel     | • Freesound API 搜尋 / 分頁<br>• 在線預覽、收藏 (IndexedDB)<br>• 標籤 / 授權濾鏡 | `src/components/FreesoundPanel.tsx` （新建）       |
| SoundEffectPanelLayout | • Tab 切換與狀態共享容器                                             | `src/components/SoundEffectPanelLayout.tsx` （新建） |

> **參考現有巨型元件**：
> `prototype/frontend/src/components/SoundEffectPanel.tsx`
> （其邏輯將被拆分到上表四個新檔案中）

### 1.1 SongLibraryPanel（歌曲庫面板）

**功能與規格：**
- 顯示可選歌曲清單（縮圖及標題）。
- 播放/暫停控制。
- 與角色頭部服務 (`HeadService`) 整合，觸發動畫提示。
- **(未來)** 支援分類篩選、搜尋、波形視覺化、進度條、跳轉播放。

**UI 驗證方式：**
- 驗證列表顯示、播放/暫停功能。
- 確認播放時觸發 `HeadService` （或模擬效果）。
- **(未來)** 測試搜尋、篩選、進度條跳轉。

### 1.2 SynthPanel（合成音效面板）

**功能與規格：**
- 利用 Tone.js 播放合成音效。
- 保留測試按鈕和 JSON 序列編輯器。
- **(未來)** 提供「快速模板」下拉選單、動態調整合成參數、整合語音效果處理。

**UI 驗證方式：**
- 驗證基本播放、JSON 編輯後聲音變化。
- **(未來)** 測試模板插入、參數調整響應、穩定性。

### 1.3 FreesoundPanel（音效搜尋面板）

**功能與規格：**
- 整合 `useFreesoundAPI` hook 進行搜尋、分頁。
- 線上預覽、收藏（使用 IndexedDB）。
- 顯示「我的收藏」子頁籤。
- **(未來)** 優化搜尋篩選、預覽控制、顯示更多元數據。

**UI 驗證方式：**
- 驗證搜尋功能、分頁載入。
- 測試音效預覽播放/停止。
- 驗證收藏功能及 IndexedDB 持久化。

---

## 2. AudioCoordinator（Service Layer）

作為前端統一的**聲音調度中心**，負責按時間軸腳本協調音訊管線播放及高級控制。

| 功能                      | 主要 Method / 介面                 | 預計檔案位置                             |
| ------------------------- | ---------------------------------- | ---------------------------------------- |
| 解析 & 排程 `AudioTimeline` | `scheduleFromJson(json)`           | `src/services/AudioCoordinator.ts` （新建） |
| 即時插播                  | `playNow(event)`                   | 同上                                     |
| 播放控制                  | `pause() / resume() / stop() / seek()` | 同上                                     |
| 取得狀態                  | `getEvents() / getPlayhead()`      | 同上                                     |
| 管線連接（語音效果）        | `connectVoiceSource(node)`         | 同上                                     |
| 語音效果更新              | `updateVoiceEffect(config)`        | 同上                                     |

**內部管線（三軌）:**
1.  **Voice Track**: TTS／唱歌聲音，需同步表情/動作。
2.  **Music Track**: 背景歌曲／BGM。
3.  **SFX Track**: 一般音效／Combo 音效。

**核心機制：**
- **Ducking**: 當 Voice Track 播放時，自動降低 Music Track 和 SFX Track 的音量。
- **優先級系統**: 處理事件衝突，確保重要聲音（如提示音）優先播放。

---

## 3. VoiceEffectsProcessor（FX Layer）

負責為 TTS 語音添加實時效果。

| 功能                 | 主要 API                             | 預計檔案位置                                  |
| -------------------- | ------------------------------------ | --------------------------------------------- |
| 初始化 Tone.js 效果鏈 | `initialize()`                       | `src/services/VoiceEffectsProcessor.ts` （新建） |
| 套用預設效果         | `applyPreset(id)`                    | 同上                                          |
| 重置效果             | `resetEffects()`                     | 同上                                          |
| 動態調參             | `setEffectParameter(type, param, value)` | 同上                                          |
| 載入 / 播放 TTS      | `loadTTSAudio(url) + playTTS()`      | 同上                                          |

**對應 UI 面板**：
`src/components/VoiceEffectsPanel.tsx` （新建，用於控制語音效果）

---

## 4. AudioTimeline JSON 格式（Data Layer）

作為後端輸出、前端輸入的標準化時間軸描述。

```jsonc
// 範例結構
{
  "timeline": [
    {
      "track": "sfx",         // 'voice', 'music', 'sfx'
      "startTime": 0.0,       // 秒
      "type": "music",        // 'tts', 'singing', 'music', 'sfx', 'combo'
      "resource": "bgm_forest01", // 資源 ID 或 URL
      "loop": true,
      "volume": 0.8,
      "duration": 120.5     // 可選
    },
    {
      "track": "voice",
      "startTime": 3.8,
      "type": "tts",
      "resource": "line_001",
      "voiceEffect": { "preset": "robot" }, // 可選語音效果
      "animationCues": [ ... ], // 可選動畫提示
      "duration": 2.2
    },
    // ... 更多事件
  ]
}
```

**Schema 定義位置建議**：
`shared/schemas/audioTimeline.schema.json`

---

## 5. 開發節奏與 Commit 切分建議

採用**小步驟、反覆測試**的方式推進。

| Stage | 主要內容                                     | 主要修改路徑                                                              |
| ----- | -------------------------------------------- | ------------------------------------------------------------------------- |
| 1     | 建立 `SoundEffectPanelLayout` + 空白三面板骨架 | `src/components/*`                                                        |
| 2     | SongLibraryPanel MVP （列表 + 基礎播放）       | `SongLibraryPanel.tsx` + `audioPlayer.ts`                                |
| 3     | SynthPanel MVP（Tone.js 基礎播放）             | `SynthPanel.tsx` + Tone.js 相關                                           |
| 4     | FreesoundPanel MVP（搜尋 + 預覽）            | `FreesoundPanel.tsx` + `FreesoundService.ts`                              |
| 5     | AudioTimeline JSON Schema & TimelineInspector (dev tool) | `shared/schemas/` + `src/components/TimelineInspector.tsx` （新建）       |
| 6     | AudioCoordinator 雛形（排程 + 三軌基礎播放）   | `src/services/AudioCoordinator.ts` （新建）                                |
| 7     | VoiceEffectsProcessor + VoiceEffectsPanel    | `VoiceEffectsProcessor.ts` + `VoiceEffectsPanel.tsx` （新建）             |
| 8     | AudioCoordinator 完善（Ducking / 優先級 / 衝突處理） | `AudioCoordinator.ts`                                                    |

**開發注意**：
- **Cursor 指令粒度**：將任務分解為小步驟，避免一次性修改過多。
- **即時驗證**：每步完成後進行測試，確保功能正常且未破壞現有系統。
- **分開提交**：每個 Stage 或主要功能點建議獨立 Commit，方便追蹤和回滾。

---

## 6. 對應現有檔案速查表

| 現有檔案                                             | 用途             | 與新架構關係                                                        |
| ---------------------------------------------------- | ---------------- | ------------------------------------------------------------------- |
| `prototype/frontend/src/components/SoundEffectPanel.tsx` | 舊版巨型面板     | **將被拆分**，邏輯遷移至四個新元件                                      |
| `prototype/frontend/src/services/SoundEffectService.ts`  | 播放音效         | 未來聚焦「資源管理」，排程移交給 `AudioCoordinator`                     |
| `prototype/frontend/src/services/audioPlayer.ts`       | 通用播放器       | SongLibraryPanel 可沿用；之後由 Coordinator 控制                        |
| `prototype/frontend/src/services/FreesoundService.ts`  | Freesound API    | FreesoundPanel 直接呼叫；需加 IndexedDB 快取                            |
| `prototype/frontend/src/services/AudioService.ts`      | TTS / 錄音       | 其 AudioNode 最終需 `connectVoiceSource()` 到 `VoiceEffectsProcessor` |
| `docs/Soundeffect_related/refactor_todo.md`          | 詳細待辦清單     | 本藍圖是其核心部分的具體化設計                                        |
| `docs/Soundeffect_related/TTS_voice_effects_with_Tone.md` | 語音效果設計文檔 | 實作 `VoiceEffectsProcessor` 時的詳細參考                              |

---

## 7. 完成後的預期效果與使用者體驗

1.  **UI 清晰分離**: 使用者可在 `SoundEffectPanel` 中透過 Tab 明確切換歌曲、合成音效、Freesound 搜尋功能。
2.  **智能混音與 Ducking**: `AudioCoordinator` 確保語音清晰，播放語音時自動降低背景音樂/音效音量，語音結束後恢復。
3.  **豐富語音效果**: 可一鍵套用機器人、太空艙等預設效果，或自訂混響、音高等參數，增加角色表現力。
4.  **高效資源管理**: 常用音效/歌曲快速加載（Tier-0/1），不常用資源按需下載（Tier-2），提升響應速度。
5.  **開發調試便捷**: `TimelineInspector` 可視化時間軸事件，方便開發者測試和除錯。
6.  **整體體驗提升**: 聲音與動畫同步更精確，音效層次更豐富，系統穩定性與可維護性增強。

---

*（此文件基於 2025/04/22 的討論和程式碼研究進行更新）*


flowchart LR
    %% ===== UI Panels =====
    SL[SongLibraryPanel]
    SY[SynthPanel]
    FS[FreesoundPanel]

    %% ===== Backend / Timeline =====
    BWS[Backend_WS\nAudioTimeline_JSON]

    %% ===== Coordinator =====
    AC((AudioCoordinator))

    %% ===== Outputs =====
    VO[Voice_Output]
    MU[Music_Output]
    SX[SFX_Output]

    %% ===== Future Viseme / Emotion =====
    VE[Viseme_Emotion]

    %% ---- Main control flow ----
    SL -->|play_request| AC
    SY -->|play_request| AC
    FS -->|play_request| AC
    BWS -->|timeline| AC

    AC -->|voice_track| VO
    AC -->|music_track| MU
    AC -->|sfx_track| SX
    AC -.->|expressions| VE

    VO -.->|ducking| MU
    VO -.->|ducking| SX

    %% ===== Song flow =====
    subgraph SongFlow
        direction LR
        U1[User] -->|select_song| SL
        SL -->|play_song| MU
        U1 -->|pause_stop| SL
        MU -.-> HA[Head_Animation]
    end

    %% ===== Synth flow =====
    subgraph SynthFlow
        direction LR
        U2[User] -->|edit_sequence| SY
        SY --> TZ[ToneJS_Synth]
        TZ --> SX
    end

    %% ===== Freesound flow =====
    subgraph FreesoundFlow
        direction LR
        U3[User] -->|search| FS
        FS --> FAPI[Freesound_API]
        FAPI --> FS
        FS --> SX
    end
