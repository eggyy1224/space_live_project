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

# 步驟 6: 開啟 Chrome 並導航到前端頁面（啟用自動初始化）
echo "正在開啟 Chrome 並導航到 http://localhost:5173/?autostart=true..."
open -a "Google Chrome" "http://localhost:5173/?autostart=true"

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
echo "已自動開啟 Chrome、導航到 http://localhost:5173/?autostart=true 並使用 JavaScript 點擊頁面"
echo "系統將自動啟用排程模式並隱藏所有控制按鈕"

echo "等待頁面完全載入..."
sleep 5  # 等待頁面載入

echo "使用 chrome-cli 切換為全螢幕模式..."

# 方法1: 使用 chrome-cli 設定視窗大小為全螢幕
echo "設定 Chrome 視窗為螢幕大小..."

# 動態獲取螢幕解析度
RESOLUTION=$(system_profiler SPDisplaysDataType | grep "Resolution:" | head -1 | grep -o '[0-9]* x [0-9]*')
if [ -n "$RESOLUTION" ]; then
    SCREEN_WIDTH=$(echo "$RESOLUTION" | cut -d' ' -f1)
    SCREEN_HEIGHT=$(echo "$RESOLUTION" | cut -d' ' -f3)
    echo "檢測到螢幕解析度: ${SCREEN_WIDTH} x ${SCREEN_HEIGHT}"
else
    # 默認值（你的主螢幕）
    SCREEN_WIDTH=2560
    SCREEN_HEIGHT=1440
    echo "使用默認螢幕解析度: ${SCREEN_WIDTH} x ${SCREEN_HEIGHT}"
fi

# 設定 Chrome 視窗位置和大小
chrome-cli position 0 0
chrome-cli size $SCREEN_WIDTH $SCREEN_HEIGHT

sleep 1

# 方法2: 使用 chrome-cli 執行 JavaScript 全螢幕
echo "嘗試 JavaScript 全螢幕請求..."
chrome-cli execute "
// 在用戶互動後嘗試全螢幕
const attemptFullscreen = () => {
  try {
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
      console.log('✅ JavaScript 全螢幕成功');
      return true;
    }
  } catch (error) {
    console.log('⚠️ JavaScript 全螢幕失敗:', error);
    return false;
  }
  return false;
};

// 立即嘗試（可能因為缺少用戶手勢而失敗）
if (!attemptFullscreen()) {
  // 如果失敗，添加點擊監聽器，在下次用戶點擊時觸發
  document.addEventListener('click', function() {
    attemptFullscreen();
  }, { once: true });
  
  // 也可以在頁面載入完成後再次嘗試
  if (document.readyState === 'complete') {
    setTimeout(attemptFullscreen, 100);
  } else {
    window.addEventListener('load', () => setTimeout(attemptFullscreen, 100));
  }
}
"

sleep 2

# 方法3: 備用 AppleScript（使用 key code 避免輸入法問題）
echo "使用 AppleScript 備用方案（key code）..."
osascript -e '
tell application "Google Chrome"
    activate
    delay 1
end tell

tell application "System Events"
    delay 1
    -- 使用 key code 3 (F 鍵) + Cmd+Shift 組合鍵
    key code 3 using {shift down, command down}
end tell'

# 方法4: 最後手段 - 使用選單方式
echo "嘗試選單方式..."
osascript -e '
tell application "System Events"
    tell process "Google Chrome"
        set frontmost to true
        delay 1
        try
            click menu item "Enter Full Screen" of menu "View" of menu bar 1
        end try
    end tell
end tell'

echo "全螢幕設定完成！"
echo ""
echo "🎉 所有設定完成！系統現在處於展示模式："
echo "   ✅ 自動排程已啟用"
echo "   ✅ 控制按鈕已隱藏"
echo "   ✅ 全螢幕模式已啟用"
echo ""
echo "💡 快捷鍵提醒："
echo "   - 按 C 鍵：顯示/隱藏控制按鈕"
echo "   - 按空白鍵：手動切換即時對話"
echo "   - 按 ESC 鍵：退出全螢幕模式"