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

# 關閉 OBS 前先停止 OBS 串流
echo "正在停止 OBS 串流..."
curl -X POST http://localhost:8000/api/perception/obs/stream/stop
sleep 1

# 關閉 OBS
echo "正在關閉 OBS 應用程式..."
osascript -e 'tell application "OBS" to quit'
sleep 3
killall OBS 2>/dev/null
if [ $? -eq 0 ]; then
    echo "OBS 已成功關閉。"
else
    echo "未找到 OBS 應用程式或關閉失敗。"
fi

# 直接關閉整個 Google Chrome
echo "正在關閉 Google Chrome..."
killall "Google Chrome"

# 關閉 Preview（若有用來顯示直播 QR）
echo "正在關閉 Preview..."
osascript -e 'tell application "Preview" to quit'
sleep 1
killall Preview 2>/dev/null || true

# 關閉 QuickTime Player（避免 MV 播放佔用而卡住）
echo "正在關閉 QuickTime Player..."
osascript -e 'tell application "QuickTime Player" to quit'
sleep 1
killall "QuickTime Player" 2>/dev/null || true

echo ""
echo "所有相關程序已嘗試關閉。" 