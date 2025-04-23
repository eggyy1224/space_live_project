# Task Master 任務管理

這個目錄包含由 Task Master 管理的所有任務。

## 目錄結構

- `tasks/` - 主要任務目錄
- `tasks/completed/` - 已完成的任務
- `tasks/backlog/` - 待辦的任務
- `tasks/config.json` - Task Master 配置

## 使用方法

您可以透過 AI 助手或命令行使用 Task Master：

### 通過 AI 助手

只需詢問 Claude：

- "顯示所有任務"
- "什麼是我下一個任務?"
- "幫我創建一個關於[主題]的新任務"
- "解析位於[路徑]的 PRD 文檔"
- "幫我實現任務3"

### 通過命令行

```bash
# 顯示所有任務
npx task-master-ai list

# 顯示下一個任務
npx task-master-ai next

# 創建新任務
npx task-master-ai create

# 解析 PRD 文檔
npx task-master-ai parse-prd [文件路徑]
```

## 任務格式

每個任務都是一個 Markdown 文件，包含以下部分：

- 任務標題和描述
- 優先級
- 狀態
- 子任務
- 相關資源
- 註釋 