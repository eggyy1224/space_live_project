# Task Master 初始化

這是您的Task Master任務管理系統的初始化文件。

## 專案概述
- 專案名稱: space_live_project
- 創建日期: 2025年4月20日
- 說明: 使用Task Master管理的專案

## 任務管理指南
您可以通過以下方式使用Task Master:

1. **創建新任務**: 
   - 通過AI助手: "幫我創建一個關於[主題]的新任務"
   - 命令行: `npx task-master-ai create`

2. **查看任務列表**:
   - 通過AI助手: "顯示所有任務" 或 "列出待辦事項"
   - 命令行: `npx task-master-ai list`

3. **獲取下一個任務**:
   - 通過AI助手: "什麼是我下一個應該完成的任務?"
   - 命令行: `npx task-master-ai next`

4. **解析需求文檔**:
   - 通過AI助手: "解析位於[路徑]的PRD文檔"
   - 命令行: `npx task-master-ai parse-prd [文件路徑]`

5. **幫助實現任務**:
   - 通過AI助手: "幫我實現任務3" 或 "幫我展開任務4的細節"

## 任務將存儲在:
- `tasks/`: 主要任務目錄
- `tasks/completed/`: 已完成任務
- `tasks/backlog/`: 待辦任務

Task Master已成功初始化！ 