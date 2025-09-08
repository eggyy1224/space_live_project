播放邏輯工具（playback_tools）

目的
- 放置「播放編排／播放清單」類的工具腳本，例如依序或隨機執行 yoga_sessions 內的場景。
- 這些腳本是透過 API（/api/scripts/*）呼叫真正的場景腳本，不應列在「可被執行的 yoga 腳本清單」之中。

為什麼要獨立資料夾
- /api/scripts 的白名單只會掃描 experiment_scripts/yoga_sessions/*.sh。
- 將播放邏輯腳本與內容腳本分離，避免誤被前端/工具列出與執行。

使用方式
- 預設後端 API 為 http://localhost:8000，可用環境變數覆蓋：
  - export BASE_URL=http://localhost:8000

- 依序播放固定清單：
  - bash prototype/backend/experiment_scripts/playback_tools/run_yoga_playlist.sh

- 隨機挑選 N 個依序播放：
  - bash prototype/backend/experiment_scripts/playback_tools/run_yoga_random_playlist.sh --count 3

需求
- bash、curl 可用。

備註
- 這些腳本會呼叫：/api/scripts/list、/api/scripts/execute、/api/scripts/status、/api/scripts/stop-all。
- 真正的場景腳本仍位於 experiment_scripts/yoga_sessions/ 下，由 /api/scripts 端點白名單管理。

