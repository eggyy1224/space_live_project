#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

FRONTEND_DIR="$SCRIPT_DIR/prototype/frontend"
BACKEND_DIR="$SCRIPT_DIR/prototype/backend"

echo "快速重啟前後端服務..."

echo "正在關閉後端服務..."
pkill -f "uvicorn main:app"
if [ $? -eq 0 ]; then
    echo "後端服務已成功終止。"
else
    echo "未找到後端服務程序或終止失敗。"
fi

echo "正在關閉前端開發伺服器..."
pkill -f "vite"
if [ $? -eq 0 ]; then
    echo "前端開發伺服器已成功終止。"
else
    echo "未找到前端開發伺服器程序或終止失敗。"
fi

sleep 2

echo "正在重新啟動後端..."
osascript <<EOF2
tell application "Terminal"
    activate
    do script "cd '$BACKEND_DIR' && ./run.sh"
    delay 0.3
    try
        set custom title of selected tab of front window to "BACKEND"
    end try
end tell
EOF2

sleep 2

echo "正在重新啟動前端..."
osascript <<EOF3
tell application "Terminal"
    activate
    do script "cd '$FRONTEND_DIR' && npm run dev"
    delay 0.3
    try
        set custom title of selected tab of front window to "FRONTEND"
    end try
end tell
EOF3

echo "前後端已重新啟動完成。"
