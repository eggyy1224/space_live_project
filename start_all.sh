#!/bin/bash

echo "啟動所有服務..."

# 步驟 1: 啟動 OBS 應用程式
echo "正在開啟 OBS..."
open -a OBS
sleep 5 # 等待 OBS 啟動

# 步驟 2: 在新的 Terminal 標籤頁中啟動後端
echo "正在啟動後端..."
osascript -e 'tell app "Terminal"
    activate
    do script "cd '$(pwd)'/prototype/backend && ./run.sh"
end tell'

# 步驟 3: 在新的 Terminal 標籤頁中啟動前端
echo "正在啟動前端..."
osascript -e 'tell app "Terminal"
    activate
    do script "cd '$(pwd)'/prototype/frontend && npm run dev"
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

echo ""
echo "啟動腳本執行完畢。" 