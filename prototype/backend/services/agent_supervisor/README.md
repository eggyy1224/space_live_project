# Agent Supervisor Service

基於 [OpenAI Realtime Agents](https://github.com/openai/openai-realtime-agents) 的 Chat-Supervisor 模式實現。

## 🎯 功能說明

這個服務實現了智能控制器模式，讓 Realtime Agent 可以將複雜的工具調用委託給更智能的 Supervisor 處理。

### 🏗️ 架構設計

```
Realtime Agent (基本對話) 
    ↓ 
API Integrations (工具路由)
    ↓
Supervisor Manager (智能決策)
    ↓
Specialized Agents (專門執行)
    ↓
Backend APIs (實際控制)
```

## 📁 檔案結構

- `core.py` - SupervisorManager 核心管理器
- `camera_agent.py` - 攝影機控制專門代理
- `__init__.py` - 模組初始化

## 🔄 工作流程

1. **Realtime Agent** 接收到 `camera_control` 工具調用
2. **API Integrations** 將請求轉發給 Supervisor
3. **Supervisor Manager** 使用 GPT-4 進行智能決策增強
4. **Camera Agent** 執行具體的攝影機控制操作
5. **返回結果** 給 Realtime Agent

## 📹 目前支援的工具

### Camera Control
- **set_preset**: 使用前端預設鏡位
- **set_angle**: 立即設定攝影機角度  
- **transition**: 平滑轉換攝影機角度

支援的預設鏡位：
- overview, head_close_up, dance_circle_view
- center_orbit_high_1/2, dramatic_angle_1/2
- behind_head_looking_out, fly_by_left/right
- 等 19 種預設鏡位

## 🧠 智能增強

Supervisor 使用 GPT-4 根據對話上下文自動選擇最適合的攝影機鏡位和參數，提供比 Realtime Agent 更智能的決策能力。

## 🚀 未來擴展

這個架構為未來加入更多複雜工具奠定了基礎：
- 多步驟視覺效果組合
- 複雜的情境分析
- 更多 AI 服務整合

## 💡 使用方式

Supervisor 完全透明地整合在現有系統中，Realtime Agent 的行為和工具定義保持不變，只是在底層執行時會獲得更智能的決策支援。 