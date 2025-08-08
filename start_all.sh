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

# 步驟 2: 在新的 Terminal 標籤頁中啟動前端
echo "正在啟動前端..."
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    do script "cd /Users/spacelive/Desktop/space_live/space_live_project/prototype/frontend && npm run dev"
    delay 0.3
    try
        set custom title of selected tab of front window to "FRONTEND"
    end try
end tell
APPLESCRIPT

# 步驟 3: 在同一個 Terminal 視窗開新分頁啟動後端（確保後端分頁在最前）
echo "正在啟動後端..."
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    -- 不在現有分頁執行，直接開新分頁
    do script "cd /Users/spacelive/Desktop/space_live/space_live_project/prototype/backend && ./run.sh"
    delay 0.3
    try
        set selected tab of front window to last tab of front window
        set custom title of selected tab of front window to "BACKEND"
        set index of front window to 1
    end try
end tell
APPLESCRIPT

# 將後端所在的 Terminal 視窗移到右側（主螢幕，小螢幕）並鋪滿
osascript -l JavaScript -e '
(() => {
  ObjC.import("AppKit");
  const delay = (s) => $.NSThread.sleepForTimeInterval(s);
  const se = Application("System Events");
  const mf = $.NSScreen.mainScreen.frame;
  const mainHeight = Number(mf.size.height);
  const rect = { x: Number(mf.origin.x), y: Number(mf.origin.y), w: Number(mf.size.width), h: Number(mf.size.height) };
  const ax = { x: rect.x, y: mainHeight - (rect.y + rect.h), w: rect.w, h: rect.h };
  let tries = 0;
  while (tries < 80) {
    try {
      const proc = se.processes.byName("Terminal");
      const wins = proc.windows;
      if (wins.length > 0) {
        proc.frontmost = true;
        delay(0.1);
        try { const menu = proc.menuBars[0].menuBarItems.byName("View").menus[0]; if (menu && menu.menuItems.byName("Exit Full Screen").exists()) menu.menuItems.byName("Exit Full Screen").click(); } catch (e) {}
        const win = wins[0];
        win.position = [ax.x, ax.y];
        win.size = [ax.w, ax.h];
        delay(0.2);
        try { const menu2 = proc.menuBars[0].menuBarItems.byName("View").menus[0]; if (menu2 && menu2.menuItems.byName("Enter Full Screen").exists()) menu2.menuItems.byName("Enter Full Screen").click(); } catch (e) {}
        break;
      }
    } catch (e) {}
    delay(0.1);
    tries++;
  }
})();'
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

# ==========================
# 最後：多螢幕自動排版（不要動前面流程）
# - 偵測兩個螢幕尺寸
# - 較大螢幕：放 Google Chrome（主要角色畫面）並全螢幕
# - 較小螢幕：放 Terminal（後端視窗）並全螢幕
# 以 JXA (osascript -l JavaScript) 實作，避免外部依賴
# ==========================

echo ""
echo "開始進行雙螢幕自動排版（Chrome → 大螢幕；Terminal → 小螢幕）..."

osascript -l JavaScript <<'JXA'
(() => {
  ObjC.import('AppKit');
  const delay = (seconds) => $.NSThread.sleepForTimeInterval(seconds);

  // 取得所有螢幕（Cocoa 坐標：原點在左下）
  const nsScreens = $.NSScreen.screens;
  const count = nsScreens.count;
  if (count < 2) {
    console.log('只偵測到 1 個螢幕，略過自動排版');
    return;
  }

  const screens = [];
  for (let i = 0; i < count; i++) {
    const s = nsScreens.objectAtIndex(i);
    // 在 JXA 中，NSScreen 的 frame 在橋接後通常為屬性而非可呼叫方法
    const f = s.frame;
    const x = Number(f.origin.x);
    const y = Number(f.origin.y);
    const w = Number(f.size.width);
    const h = Number(f.size.height);
    // 使用 backingScaleFactor 將點座標換算為近似像素面積，避免 4K 縮放成 1080p 的誤判
    let scale = 1;
    try { scale = Number(s.backingScaleFactor); } catch (e) { scale = 1; }
    const pixelArea = w * h * scale * scale;
    screens.push({ x, y, width: w, height: h, scale, area: w * h, pixelArea, maxY: y + h });
  }

  // 主螢幕高度（JXA UI 坐標系統的 y=0 位於主螢幕左上角，往下為正）
  const mainF = $.NSScreen.mainScreen.frame;
  const mainHeight = Number(mainF.size.height);

  // 找最大/最小螢幕（以像素面積判斷）；若像素面積幾乎相同，預設使用最左邊螢幕作為「大螢幕」
  screens.sort((a, b) => b.pixelArea - a.pixelArea);
  let large = screens[0];
  let small = screens[screens.length - 1];
  if (screens.length >= 2) {
    const a0 = screens[0];
    const a1 = screens[1];
    const relDiff = Math.abs(a0.pixelArea - a1.pixelArea) / Math.max(a0.pixelArea, a1.pixelArea);
    if (relDiff < 0.01) { // 面積幾乎相同 → 用 X 位置（取最左作為「大螢幕」）
      const leftMost = a0.x <= a1.x ? a0 : a1;
      const rightMost = leftMost === a0 ? a1 : a0;
      large = leftMost;
      small = rightMost;
    }
  }

  const toAX = (r) => {
    // 將 AppKit 全域底左座標系（r.x, r.y，原點在主螢幕左下）
    // 轉成 UI 自動化所用的頂左座標系（原點在主螢幕左上，y 向下）
    const x = r.x; // x 可直接使用全域座標（可能為負數，表示在主螢幕左側）
    const y = mainHeight - (r.y + r.height);
    return { x: Math.round(x), y: Math.round(y), w: Math.round(r.width), h: Math.round(r.height) };
  };

  const largeAX = toAX(large);
  const smallAX = toAX(small);

  const sys = Application('System Events');

  const tryMove = (proc, bounds, winIndex = 0) => {
    try {
      const win = proc.windows[winIndex] || proc.windows[0];
      win.position = [bounds.x, bounds.y];
      win.size = [bounds.w, bounds.h];
      delay(0.2);
      return true;
    } catch (e) {
      return false;
    }
  };

  const exitFullScreen = (proc) => {
    try {
      const viewMenu = proc.menuBars[0].menuBarItems.byName('View').menus[0];
      if (viewMenu && viewMenu.menuItems.byName('Exit Full Screen').exists()) {
        viewMenu.menuItems.byName('Exit Full Screen').click();
        delay(0.2);
        return true;
      }
    } catch (e) { /* 忽略 */ }
    // 回退：快捷鍵 Ctrl+Cmd+F
    try { sys.keystroke('f', { using: ['control down', 'command down'] }); delay(0.2); return true; } catch (e) {}
    return false;
  };

  const enterFullScreen = (proc) => {
    try {
      const viewMenu = proc.menuBars[0].menuBarItems.byName('View').menus[0];
      if (viewMenu && viewMenu.menuItems.byName('Enter Full Screen').exists()) {
        viewMenu.menuItems.byName('Enter Full Screen').click();
        delay(0.2);
        return true;
      }
    } catch (e) { /* 忽略 */ }
    // 回退：快捷鍵 Ctrl+Cmd+F
    try { sys.keystroke('f', { using: ['control down', 'command down'] }); delay(0.2); return true; } catch (e) {}
    return false;
  };

  const moveAndFullscreen = (appName, bounds, winIndex = 0) => {
    try {
      const app = Application(appName);
      app.activate();
      delay(0.3);
      const proc = sys.processes.byName(appName);
      proc.frontmost = true;
      delay(0.2);

      // 先嘗試移動；若失敗，先退出全螢幕後再移動
      let moved = tryMove(proc, bounds, winIndex);
      if (!moved) {
        exitFullScreen(proc);
        delay(0.3);
        moved = tryMove(proc, bounds, winIndex);
      }
      // 最後保險：進入全螢幕
      enterFullScreen(proc);
    } catch (e) { /* 忽略單一 app 的錯誤 */ }
  };

  // 先找出 Terminal 中「後端」視窗（名稱或內容包含 backend 的 tab 所在視窗）
  let backendWinIndex = 0;
  try {
    const term = Application('Terminal');
    const wins = term.windows();
    for (let i = 0; i < wins.length; i++) {
      const tabs = wins[i].tabs();
      for (let j = 0; j < tabs.length; j++) {
        const tname = String(tabs[j].name());
        let contents = '';
        try { contents = String(tabs[j].contents()); } catch (e) {}
        if (
          tname.toLowerCase().includes('backend') ||
          tname.includes('/prototype/backend') ||
          contents.includes('/prototype/backend') ||
          /Uvicorn|FastAPI|0\.0\.0\.0:8000|INFO\s*:/.test(contents)
        ) {
          backendWinIndex = i;
          break;
        }
      }
    }
  } catch (e) { /* 若失敗就用 0 */ }

  // 1) Chrome → 大螢幕
  moveAndFullscreen('Google Chrome', largeAX);
  // 2) 只移動後端 Terminal 視窗到小螢幕，並保持其在最前面
  try {
    const term = Application('Terminal');
    term.activate();
    const proc = sys.processes.byName('Terminal');
    // 先把後端視窗帶到最前（依索引）
    try { proc.windows[backendWinIndex].index = 1; } catch (e) {}
    // 再進行移動與全螢幕
    moveAndFullscreen('Terminal', smallAX, backendWinIndex);
    // 確保 Terminal 留在最前（避免剛開的前端視窗搶前景）
    try { proc.frontmost = true; } catch (e) {}
  } catch (e) { /* 忽略 */ }
})();
JXA

echo "雙螢幕自動排版完成。"