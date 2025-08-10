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
echo "   ✅ 自動排程已啟用（headonly 視窗使用 autostart）"
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
echo "開始進行雙螢幕自動排版（大螢幕：Chrome 置入左螢幕；小螢幕：Terminal + headonly Chrome 左右各半）..."

# 先開啟 headonly 的新 Chrome 視窗（自動初始化）
echo "開啟 headonly Chrome 視窗於 http://localhost:5173/?headonly&&autostart=true ..."
osascript -e '
tell application "Google Chrome"
    activate
    set newWin to make new window
    set URL of active tab of newWin to "http://localhost:5173/?headonly&&autostart=true"
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

  // 改為強制：左邊螢幕作為大螢幕、最右邊螢幕作為小螢幕
  screens.sort((a,b) => a.x - b.x);
  const leftMost = screens[0];
  const rightMost = screens[screens.length - 1];
  // 使用可見區域計算 AX 座標，避免超出螢幕（Dock/菜單列）
  const largeAX = toAX({ x: leftMost.x, y: leftMost.y, width: leftMost.width, height: leftMost.height });
  const smallAX = toAX({ x: rightMost.x, y: rightMost.y, width: rightMost.width, height: rightMost.height });
  // 對可視區域再加上安全邊距，避免貼邊造成溢出
  const safePad = 8;
  const largeVisibleAXRaw = toAX({ x: leftMost.vx, y: leftMost.vy, width: leftMost.vw, height: leftMost.vh });
  const largeVisibleAX = { x: largeVisibleAXRaw.x + safePad, y: largeVisibleAXRaw.y + safePad, w: largeVisibleAXRaw.w - safePad * 2, h: largeVisibleAXRaw.h - safePad * 2 };
  const smallVisibleAXRaw = toAX({ x: rightMost.vx, y: rightMost.vy, width: rightMost.vw, height: rightMost.vh });
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

  // 1) 將 Chrome 主視窗（非 headonly，網址以 localhost:5173 開頭且不含 headonly）放到左邊大螢幕
  // 先在左螢幕建立 Finder 錨點以鎖定目標空間
  anchorOnDisplay(largeVisibleAX);
  focusChromeWindowBy((u) => u.startsWith('http://localhost:5173') && !u.includes('headonly'));
  moveWindow('Google Chrome', largeVisibleAX);
  // 再保守縮小 96% 以避免任何邊界或縮放問題（針對目前前景視窗）
  try {
    const proc = sys.processes.byName('Google Chrome');
    const win = proc.windows[0]; // frontmost chrome window
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
        moveWindow('Google Chrome', largeVisibleAX);
        win.position = [nx, ny];
        win.size = [nw, nh];
      }
    } catch (e) {}
  } catch (e) { /* 忽略 */ }

  // 2) 小螢幕：Terminal（左半） + 新開的 headonly Chrome（右半）
  const halves = halfRects(smallVisibleAX);

  // 2a) Terminal → 左半
  try {
    const term = Application('Terminal');
    term.activate();
    const proc = sys.processes.byName('Terminal');
    try { proc.windows[backendWinIndex].index = 1; } catch (e) {}
    moveWindow('Terminal', halves.left, backendWinIndex);
  } catch (e) { /* 忽略 */ }

  // 2b) headonly Chrome 視窗 → 右半（先聚焦含 headonly 的視窗，再移動前景視窗）
  focusChromeWindowBy((u) => u.includes('headonly'));
  moveWindow('Google Chrome', halves.right);
})();
JXA

echo "雙螢幕自動排版完成。"