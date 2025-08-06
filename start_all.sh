#!/bin/bash

echo "先關閉所有相關服務..."
/Users/spacelive/Desktop/space_live/space_live_project/stop_all.sh
sleep 2

echo "啟動所有服務..."

# 確保 Google Chrome 已開啟
echo "正在開啟 Google Chrome..."
open -a "Google Chrome"
sleep 5

# 自動開啟 YouTube 直播後台（用 osascript 方式）
echo "正在開啟 YouTube 直播後台..."
osascript -e '
tell application "Google Chrome"
    activate
    open location "https://studio.youtube.com/channel/UC/livestreaming"
end tell'

# 步驟 1: 啟動 OBS 應用程式
echo "正在開啟 OBS..."
open -a OBS
sleep 5 # 等待 OBS 啟動

# 步驟 2: 在新的 Terminal 標籤頁中啟動後端
echo "正在啟動後端..."
osascript -e 'tell app "Terminal"
    activate
    do script "cd /Users/spacelive/Desktop/space_live/space_live_project/prototype/backend && ./run.sh"
end tell'

# 步驟 3: 在新的 Terminal 標籤頁中啟動前端
echo "正在啟動前端..."
osascript -e 'tell app "Terminal"
    activate
    do script "cd /Users/spacelive/Desktop/space_live/space_live_project/prototype/frontend && npm run dev"
end tell'

echo "等待後端服務啟動..."
sleep 15 # 給予後端足夠的啟動時間

# 步驟 4: 連接到 OBS 並開始串流
echo "正在連接到 OBS..."
curl -X POST -H "Content-Type: application/json" -d '{
    "host": "localhost",
    "port": 4455,
    "password": ""
}' http://localhost:8000/api/perception/obs/connection

# 給予 OBS 一點時間反應
sleep 2

echo "正在啟動 OBS 串流..."
curl -X POST http://localhost:8000/api/perception/obs/stream/start

# 步驟 5: 等待前端服務完全啟動
echo "等待前端服務啟動..."
sleep 10

# 步驟 6: 開啟 Chrome 並導航到前端頁面
echo "正在開啟 Chrome 並導航到 http://localhost:5173/..."
open -a "Google Chrome" http://localhost:5173/

# 等待 Chrome 載入頁面
sleep 8

# 步驟 7: 使用 JavaScript 自動點擊頁面
echo "正在使用 JavaScript 自動點擊頁面..."
osascript -e '
tell application "Google Chrome"
    activate
    delay 2
    
    -- 等待頁面完全載入
    repeat 30 times
        tell active tab of front window
            if loading is false then exit repeat
            delay 1
        end tell
    end repeat
    
    -- 執行 JavaScript 來點擊頁面
    tell active tab of front window
        execute javascript "document.body.click();"
        delay 0.5
        execute javascript "document.body.click();"
    end tell
end tell'

echo ""
echo "啟動腳本執行完畢。"
echo "已自動開啟 Chrome、導航到 http://localhost:5173/ 並使用 JavaScript 點擊頁面"

echo "切換 Chrome 視窗為全螢幕..."
osascript -e 'tell application "Google Chrome" to activate' \
          -e 'tell application "System Events" to keystroke "f" using {control down, command down}' 