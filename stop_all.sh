#!/bin/bash

echo "正在關閉所有服務..."

# 關閉後端 (uvicorn)
echo "正在關閉後端服務..."
pkill -f "uvicorn main:app"
if [ $? -eq 0 ]; then
    echo "後端服務已成功終止。"
else
    echo "未找到後端服務程序或終止失敗。"
fi

# 關閉前端 (vite)
echo "正在關閉前端開發伺服器..."
pkill -f "vite"
if [ $? -eq 0 ]; then
    echo "前端開發伺服器已成功終止。"
else
    echo "未找到前端開發伺服器程序或終止失敗。"
fi

# 關閉 OBS
echo "正在關閉 OBS 應用程式..."
killall OBS
if [ $? -eq 0 ]; then
    echo "OBS 已成功關閉。"
else
    echo "未找到 OBS 應用程式或關閉失敗。"
fi

# 關閉 Chrome 中網址包含 5173 的分頁
echo "正在關閉 Chrome 中網址包含 5173 的分頁..."
osascript -e '
tell application "Google Chrome"
    if it is running then
        repeat with w in windows
            repeat with t in tabs of w
                if URL of t contains "5173" then
                    close t
                end if
            end repeat
        end repeat
    end if
end tell'

echo ""
echo "所有相關程序已嘗試關閉。" 