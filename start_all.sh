#!/bin/bash

echo "先關閉所有相關服務..."
/Users/spacelive/Desktop/space_live/space_live_project/stop_all.sh
sleep 2

echo "啟動所有服務..."

# 背景播放開機 MV（非同步，不阻塞後續流程）
MV_SCRIPT="/Users/spacelive/Desktop/space_live/space_live_project/prototype/frontend/public/mv/play_mv_loop.sh"
MV_LOG="/Users/spacelive/Desktop/space_live/space_live_project/prototype/frontend/public/mv/play_mv_loop.log"
if [ -f "$MV_SCRIPT" ]; then
  chmod +x "$MV_SCRIPT" 2>/dev/null || true
  echo "背景啟動開機 MV：$MV_SCRIPT (log: $MV_LOG)"
  nohup "$MV_SCRIPT" > "$MV_LOG" 2>&1 &
  echo "MV 背景程序 PID: $!"
else
  echo "找不到 MV 腳本：$MV_SCRIPT，略過播放。"
fi

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

# （移除舊的 Terminal 強制全螢幕與鋪滿步驟，避免被系統切到其它桌面）
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

# 步驟 6: 開啟 Chrome 並導航到前端頁面（不自動初始化）
echo "正在開啟 Chrome 並導航到 http://localhost:5173..."
open -a "Google Chrome" "http://localhost:5173"

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
echo "已自動開啟 Chrome、導航到 http://localhost:5173 並使用 JavaScript 點擊頁面"
echo "如需自動排程與隱藏控制，可使用 headonly 視窗 (稍後將自動開啟)"

echo "等待頁面完全載入..."
sleep 5  # 等待頁面載入

echo ""
echo "🎉 所有設定完成！系統現在處於展示模式："
echo "   ✅ 自動排程可於前端設定啟用（headonly 視窗不使用 autostart）"
echo "   ✅ 控制按鈕已隱藏（在 headonly 視窗）"
echo "   ⏭️ 全螢幕將於排版後依需求再設定（目前改用可視範圍定位以避免卡住）"
echo ""
echo "💡 快捷鍵提醒："
echo "   - 按 C 鍵：顯示/隱藏控制按鈕"
echo "   - 按空白鍵：手動切換即時對話"
echo "   - 按 ESC 鍵：退出全螢幕模式"

# ==========================
# 最後：多螢幕自動排版（不要動前面流程）
# - 偵測兩個螢幕尺寸
# - 較大螢幕：放 Google Chrome（主要角色畫面），非全螢幕，以可視範圍定位
# - 較小螢幕：Terminal 與 headonly Chrome 各佔一半（左右分布），非全螢幕
# 以 JXA (osascript -l JavaScript) 實作，避免外部依賴
# ==========================

echo ""
echo "開始進行雙螢幕自動排版（大螢幕：Chrome 置入左螢幕；小螢幕：Terminal + headonly Chrome 上下各半）..."

# 先開啟 headonly 的新 Chrome 視窗（不含 autostart）
echo "開啟 headonly Chrome 視窗於 http://localhost:5173/?headonly ..."
osascript -e '
tell application "Google Chrome"
    activate
    set newWin to make new window
    set URL of active tab of newWin to "http://localhost:5173/?headonly"
end tell'

sleep 2 # 確保 headonly 視窗已建立再進行排版

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
    // 在 JXA 中，NSScreen 的 frame/visibleFrame 在橋接後通常為屬性
    const f = s.frame;
    const vf = s.visibleFrame; // 排除 Dock 與選單列的可見區域
    const x = Number(f.origin.x);
    const y = Number(f.origin.y);
    const w = Number(f.size.width);
    const h = Number(f.size.height);
    const vx = Number(vf.origin.x);
    const vy = Number(vf.origin.y);
    const vw = Number(vf.size.width);
    const vh = Number(vf.size.height);
    // 使用 backingScaleFactor 將點座標換算為近似像素面積，避免 4K 縮放成 1080p 的誤判
    let scale = 1;
    try { scale = Number(s.backingScaleFactor); } catch (e) { scale = 1; }
    const pixelArea = w * h * scale * scale;
    screens.push({ x, y, width: w, height: h, vx, vy, vw, vh, scale, area: w * h, pixelArea, maxY: y + h });
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

  // 計算全域最高 Y（避免不同螢幕高度導致 y 轉換錯誤）
  const globalMaxY = screens.reduce((acc, s) => Math.max(acc, s.y + s.height), 0);

  const toAX = (r) => {
    // 將 AppKit 全域底左座標系（r.x, r.y，原點在主螢幕左下）
    // 轉成 UI 自動化所用的頂左座標系（原點在主螢幕左上，y 向下）
    const x = r.x; // x 可直接使用全域座標（可能為負數，表示在主螢幕左側）
    const y = globalMaxY - (r.y + r.height);
    return { x: Math.round(x), y: Math.round(y), w: Math.round(r.width), h: Math.round(r.height) };
  };

  // 直接以 X 座標選擇顯示器：
  // - 最左邊的螢幕作為「大螢幕」（主要顯示 Chrome 主畫面）
  // - 最右邊的螢幕作為「小螢幕」（Terminal + headonly）
  // 這樣可避免像素面積較大的直立螢幕被誤判為「大螢幕」。
  const byX = screens.slice().sort((a, b) => a.x - b.x);
  const largeScreen = byX[0];
  const smallScreen = byX[byX.length - 1];

  // 使用可見區域計算 AX 座標，避免超出螢幕（Dock/選單列）
  const largeAX = toAX({ x: largeScreen.x, y: largeScreen.y, width: largeScreen.width, height: largeScreen.height });
  const smallAX = toAX({ x: smallScreen.x, y: smallScreen.y, width: smallScreen.width, height: smallScreen.height });
  // 對可視區域加上安全邊距
  const safePad = 8;
  const largeVisibleAXRaw = toAX({ x: largeScreen.vx, y: largeScreen.vy, width: largeScreen.vw, height: largeScreen.vh });
  const largeVisibleAX = { x: largeVisibleAXRaw.x + safePad, y: largeVisibleAXRaw.y + safePad, w: largeVisibleAXRaw.w - safePad * 2, h: largeVisibleAXRaw.h - safePad * 2 };
  const smallVisibleAXRaw = toAX({ x: smallScreen.vx, y: smallScreen.vy, width: smallScreen.vw, height: smallScreen.vh });
  const smallVisibleAX = { x: smallVisibleAXRaw.x + safePad, y: smallVisibleAXRaw.y + safePad, w: smallVisibleAXRaw.w - safePad * 2, h: smallVisibleAXRaw.h - safePad * 2 };

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

  // 多語系選單工具
  const getMenuBarItem = (proc, names) => {
    try {
      const items = proc.menuBars[0].menuBarItems;
      for (const n of names) {
        try {
          const it = items.byName(n);
          if (it && it.exists()) return it;
        } catch (e) {}
      }
    } catch (e) {}
    return null;
  };

  const getViewMenu = (proc) => {
    const viewItem = getMenuBarItem(proc, ['View', '顯示', '显示', '表示']);
    try { return viewItem ? viewItem.menus[0] : null; } catch (e) { return null; }
  };

  const menuItemExists = (menu, names) => {
    for (const n of names) {
      try { if (menu.menuItems.byName(n).exists()) return n; } catch (e) {}
    }
    return null;
  };

  const clickMenuItemIfExists = (menu, names) => {
    const name = menuItemExists(menu, names);
    if (name) {
      try { menu.menuItems.byName(name).click(); delay(0.2); return true; } catch (e) {}
    }
    return false;
  };

  const isFullScreen = (proc) => {
    const viewMenu = getViewMenu(proc);
    if (!viewMenu) return null;
    if (menuItemExists(viewMenu, ['Exit Full Screen', '退出全螢幕', '退出全屏', '退出全屏幕', '結束全螢幕', 'フルスクリーンを終了'])) return true;
    if (menuItemExists(viewMenu, ['Enter Full Screen', '進入全螢幕', '进入全屏', '進入全屏幕', 'フルスクリーンにする'])) return false;
    return null; // 無法判定
  };

  const exitFullScreen = (proc) => {
    try {
      const viewMenu = getViewMenu(proc);
      if (!viewMenu) return false;
      const state = isFullScreen(proc);
      if (state === true) {
        return clickMenuItemIfExists(viewMenu, ['Exit Full Screen', '退出全螢幕', '退出全屏', '退出全屏幕', '結束全螢幕', 'フルスクリーンを終了']);
      }
      // 非全螢幕就不做任何事（避免誤觸快捷鍵把視窗變全螢幕）
    } catch (e) {}
    return false;
  };

  // 保留但不使用：如需全螢幕，僅點擊對應選單（避免快捷鍵誤觸）
  const enterFullScreen = (proc) => {
    try {
      const viewMenu = getViewMenu(proc);
      if (!viewMenu) return false;
      return clickMenuItemIfExists(viewMenu, ['Enter Full Screen', '進入全螢幕', '进入全屏', '進入全屏幕', 'フルスクリーンにする']);
    } catch (e) {}
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
      // 不再自動進入全螢幕，維持可視範圍定位
    } catch (e) { /* 忽略單一 app 的錯誤 */ }
  };

  // 在目標顯示器建立暫時錨點視窗（Finder），協助把其它 app 視窗帶到該顯示器與該空間
  const anchorOnDisplay = (bounds) => {
    try {
      const finder = Application('Finder');
      finder.activate();
      delay(0.2);
      // 嘗試取得第一個視窗，若沒有則新建
      let win;
      try { win = finder.windows[0]; } catch (e) { win = null; }
      try { if (!win) finder.make({ new: 'Finder window' }); } catch (e) {}
      delay(0.2);
      const sys = Application('System Events');
      const proc = sys.processes.byName('Finder');
      try {
        const fwin = proc.windows[0];
        fwin.position = [bounds.x, bounds.y];
        fwin.size = [bounds.w, bounds.h];
        proc.frontmost = true;
      } catch (e) {}
      delay(0.25);
    } catch (e) {}
  };

  // 允許指定視窗索引的移動（不全螢幕）
  const moveWindow = (appName, bounds, winIndex = 0) => {
    try {
      const app = Application(appName);
      app.activate();
      delay(0.2);
      const proc = sys.processes.byName(appName);
      // 退出全螢幕（若有）以便縮放
      exitFullScreen(proc);
      delay(0.2);
      try {
        const win = proc.windows[winIndex] || proc.windows[0];
        win.position = [bounds.x, bounds.y];
        win.size = [bounds.w, bounds.h];
      } catch (e) {}
    } catch (e) {}
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

  // 便捷：半屏矩形生成器
  const halfRects = (r) => {
    const pad = 6; // 邊界留白，避免貼邊造成捲動條或誤差
    const halfW = Math.round(r.w / 2);
    return {
      left: { x: r.x + pad, y: r.y + pad, w: halfW - pad * 2, h: r.h - pad * 2 },
      right: { x: r.x + halfW + pad, y: r.y + pad, w: halfW - pad * 2, h: r.h - pad * 2 },
    };
  };
  const verticalHalfRects = (r) => {
    const pad = 6;
    const halfH = Math.round(r.h / 2);
    return {
      top: { x: r.x + pad, y: r.y + pad, w: r.w - pad * 2, h: halfH - pad * 2 },
      bottom: { x: r.x + pad, y: r.y + halfH + pad, w: r.w - pad * 2, h: halfH - pad * 2 },
    };
  };

  // 輔助：將特定 URL 條件的 Chrome 視窗設為前景（窗口本身到最前、對應分頁為 active）
  const focusChromeWindowBy = (predicate) => {
    try {
      const chrome = Application('Google Chrome');
      const wins = chrome.windows();
      for (let i = 0; i < wins.length; i++) {
        const tabs = wins[i].tabs();
        for (let j = 0; j < tabs.length; j++) {
          let u = '';
          try { u = String(tabs[j].url()); } catch (e) { u = ''; }
          if (predicate(u)) {
            chrome.activate();
            try { wins[i].activeTabIndex = j + 1; } catch (e) {}
            try { wins[i].index = 1; } catch (e) {}
            delay(0.2);
            return true;
          }
        }
      }
    } catch (e) {}
    return false;
  };

  // 依據分頁 URL 尋找特定 Chrome 視窗索引（找不到則回傳 0）
  const findChromeWindowIndexByUrl = (predicate) => {
    try {
      const chrome = Application('Google Chrome');
      const wins = chrome.windows();
      for (let i = 0; i < wins.length; i++) {
        const tabs = wins[i].tabs();
        for (let j = 0; j < tabs.length; j++) {
          let u = '';
          try { u = String(tabs[j].url()); } catch (e) { u = ''; }
          if (predicate(u)) return i;
        }
      }
    } catch (e) {}
    return -1; // 找不到就傳回 -1，避免誤操作第 0 個視窗
  };

  // 1) 將 Chrome 主視窗（非 headonly，網址以 localhost:5173 開頭且不含 headonly）放到左邊大螢幕
  // 先在左螢幕建立 Finder 錨點以鎖定目標空間
  anchorOnDisplay(largeVisibleAX);
  focusChromeWindowBy((u) => /^https?:\/\/localhost:5173\b/.test(u) && !u.includes('headonly'));
  const mainChromeIndex = findChromeWindowIndexByUrl((u) => /^https?:\/\/localhost:5173\b/.test(u) && !u.includes('headonly'));
  if (mainChromeIndex >= 0) {
    moveWindow('Google Chrome', largeVisibleAX, mainChromeIndex);
  }
  // 再保守縮小 96% 以避免任何邊界或縮放問題（針對目前前景視窗）
  try {
    const proc = sys.processes.byName('Google Chrome');
    const win = (mainChromeIndex >= 0 ? proc.windows[mainChromeIndex] : proc.windows[0]);
    const nx = largeVisibleAX.x;
    const ny = largeVisibleAX.y;
    const nw = Math.round(largeVisibleAX.w * 0.96);
    const nh = Math.round(largeVisibleAX.h * 0.96);
    win.position = [nx, ny];
    win.size = [nw, nh];
    // 驗證是否確實進入左螢幕（以 x 範圍判斷），若否則重試一次
    try {
      const pos = win.position();
      const wx = Number(pos[0]);
      if (wx < (largeVisibleAX.x - 20) || wx > (largeVisibleAX.x + largeVisibleAX.w + 20)) {
        anchorOnDisplay(largeVisibleAX);
        moveWindow('Google Chrome', largeVisibleAX, (mainChromeIndex >= 0 ? mainChromeIndex : 0));
        win.position = [nx, ny];
        win.size = [nw, nh];
      }
    } catch (e) {}
  } catch (e) { /* 忽略 */ }

  // 2) 小螢幕：Terminal（上半） + 新開的 headonly Chrome（下半）
  const halves = verticalHalfRects(smallVisibleAX);

  // 2a) headonly Chrome 視窗 → 上半（先聚焦含 headonly 的視窗，再移動前景視窗）
  focusChromeWindowBy((u) => u.includes('headonly'));
  const headonlyIndex = findChromeWindowIndexByUrl((u) => u.includes('headonly'));
  if (headonlyIndex >= 0) {
    moveWindow('Google Chrome', halves.top, headonlyIndex);
  }

  // 2b) Terminal → 下半（將所有 Terminal 視窗都移到下半，避免有前端視窗留在上半）
  try {
    const term = Application('Terminal');
    term.activate();
    const proc = sys.processes.byName('Terminal');
    try { proc.windows[backendWinIndex].index = 1; } catch (e) {}
    try {
      const total = proc.windows.length;
      for (let i = 0; i < total; i++) {
        moveWindow('Terminal', halves.bottom, i);
      }
    } catch (e) {
      // 後備：至少確保後端視窗在下半
      moveWindow('Terminal', halves.bottom, backendWinIndex);
    }
  } catch (e) { /* 忽略 */ }
 
  // 2c) 再次將 headonly Chrome 聚焦並放置到上半，確保視覺上覆蓋 Terminal
  focusChromeWindowBy((u) => u.includes('headonly'));
  const headonlyIndex2 = findChromeWindowIndexByUrl((u) => u.includes('headonly'));
  if (headonlyIndex2 >= 0) {
    moveWindow('Google Chrome', halves.top, headonlyIndex2);
  }
  try {
    const sys2 = Application('System Events');
    const chromeProc = sys2.processes.byName('Google Chrome');
    // 嘗試把 headonly 的那個視窗放到最前面
    try { if (headonlyIndex2 >= 0) chromeProc.windows[headonlyIndex2].index = 1; } catch (e) {}
    chromeProc.frontmost = true;
  } catch (e) { /* 忽略 */ }

})();
JXA

echo "雙螢幕自動排版完成。"

# ==========================
# 額外：生成直播 QR Code 並顯示於大螢幕左下角（以 Preview 顯示，小尺寸）
# - 來源：抓取頻道 /live 解析當前 videoId → 生成 QR 圖 → 用 Preview 開啟 → 移到大螢幕左下角
# ==========================

echo "準備生成直播 QR Code..."

# 設定頻道 ID（如需變更請同步後端設定）
CHANNEL_ID="UCV60MYR7dQJM8TqY5eXb7YA"

# 解析當前直播 videoId（若無則退回至 /live 頁面）
LIVE_HTML=$(curl -L -s "https://www.youtube.com/channel/${CHANNEL_ID}/live" || true)
VIDEO_ID=$(echo "$LIVE_HTML" | grep -oE '"videoId":"[A-Za-z0-9_-]{11}"' | head -n1 | sed -E 's/"videoId":"([A-Za-z0-9_-]{11})"/\1/')

if [ -n "$VIDEO_ID" ]; then
  LIVE_URL="https://www.youtube.com/watch?v=${VIDEO_ID}"
else
  LIVE_URL="https://www.youtube.com/channel/${CHANNEL_ID}/live"
fi

QR_DIR="/Users/spacelive/Desktop/space_live/space_live_project/prototype/frontend/public/qr"
QR_FILE="${QR_DIR}/live_qr.png"
mkdir -p "$QR_DIR"

# 使用線上 API 生成 QR Code（免安裝依賴）
echo "正在生成 QR 圖檔：$QR_FILE (URL: $LIVE_URL)"
curl -L --silent --show-error --fail --get \
  --data-urlencode "data=${LIVE_URL}" \
  "https://api.qrserver.com/v1/create-qr-code/?size=220x220&qzone=1&margin=1" \
  -o "$QR_FILE" || echo "⚠️ QR 生成可能失敗，將略過顯示。"

# 以 Preview 顯示 QR，之後用 JXA 移動到大螢幕左下角
if [ -f "$QR_FILE" ]; then
  echo "以 Preview 開啟 QR 圖..."
  open -a Preview "$QR_FILE"
  sleep 1.2

  # 直接把 Preview 貼到最右側螢幕的左下角（以主機當前座標）
  osascript -l JavaScript -e '(() => { ObjC.import("AppKit"); const delay=(s)=>$.NSThread.sleepForTimeInterval(s); const nsScreens=$.NSScreen.screens; const count=nsScreens.count; if(count<1){return;} const screens=[]; for (let i=0;i<count;i++){ const s=nsScreens.objectAtIndex(i); const f=s.frame; const vf=s.visibleFrame; screens.push({x:Number(f.origin.x), y:Number(f.origin.y), w:Number(f.size.width), h:Number(f.size.height), vx:Number(vf.origin.x), vy:Number(vf.origin.y), vw:Number(vf.size.width), vh:Number(vf.size.height)});} screens.sort((a,b)=>a.x-b.x); const right=screens[screens.length-1]; const globalMaxY=screens.reduce((acc,s)=>Math.max(acc,s.y+s.h),0); const toAX=(r)=>({x:Math.round(r.x), y:Math.round(globalMaxY-(r.y+r.h)), w:Math.round(r.w), h:Math.round(r.h)}); const visAX=toAX({x:right.vx, y:right.vy, w:right.vw, h:right.vh}); const pad=12; const winW=420; const winH=480; try{ const app=Application("Preview"); app.activate(); delay(0.2);}catch(e){} try{ const sys=Application("System Events"); const proc=sys.processes.byName("Preview"); const wins=proc.windows(); if(!wins||wins.length===0){return;} const win=wins[0]; try{win.size=[winW,winH];}catch(e){} delay(0.15); const yBottom=visAX.y+visAX.h-winH-pad; try{win.position=[visAX.x+pad, yBottom];}catch(e){} delay(0.08); try{win.position=[visAX.x+pad, yBottom];}catch(e){} }catch(e){} })();'
else
  echo "找不到 QR 圖檔，略過顯示。"
fi
