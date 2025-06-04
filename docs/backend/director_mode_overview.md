# Director Mode Overview

本文件說明如何透過 `DirectorGraph` 使用 LangGraph 自動化協調角色對白與電影級鏡位效果。此模式會根據即時文字輸入生成對應的鏡位、背景音樂及情緒表達指令，再呼叫後端既有 API 完成控制。

## 主要特色

- **即時文字解析**：使用語言模型分析輸入內容，產生角色台詞與情緒設定。
- **動態視聽決策**：依情境選擇低角度仰拍、荷蘭角、俯視全景等攝影機效果，並切換 BGM 與環境音效。
- **API 協調**：自動串接 `/control/send-message`、`/control/background-audio`、`/control/camera/transition`、`/control/emotion-trajectory`、`/control/play-audio` 及 `/control/broadcast` 等端點。

## 工作流程簡述

1. `DirectorGraph` 接收文字輸入，傳入語言模型以 JSON 格式產生計畫。
2. 解析計畫後依序調用控制 API，包括鏡位切換、音樂播放及情緒曲線等指令。
3. 所有結果會回寫至狀態物件，可供後續調整或記錄。

此模式讓虛擬太空人能以更具戲劇性的方式回應觀眾，並保持架構模組化，方便未來擴充更多導演技巧。
