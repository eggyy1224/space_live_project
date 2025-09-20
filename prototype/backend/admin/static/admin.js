(function(){
  const logEl = document.getElementById('ws-log');
  const inputEl = document.getElementById('ws-input');
  const sendBtn = document.getElementById('ws-send');
  const clearBtn = document.getElementById('ws-clear');
  const downloadBtn = document.getElementById('ws-download');

  function appendLog(text){
    logEl.textContent += text + '\n';
    logEl.scrollTop = logEl.scrollHeight;
  }

  function connect(){
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${location.host}/ws`);
    ws.onopen = () => appendLog('[connected]');
    ws.onmessage = evt => appendLog('recv: ' + evt.data);
    ws.onclose = () => appendLog('[closed]');
    sendBtn.onclick = () => {
      if(ws.readyState === WebSocket.OPEN){
        ws.send(inputEl.value);
        appendLog('send: ' + inputEl.value);
      }
    };
    return ws;
  }

  let ws = connect();

  clearBtn.onclick = () => { logEl.textContent = ''; };
  downloadBtn.onclick = () => {
    const blob = new Blob([logEl.textContent], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ws-log.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  // --- Program Manager ---
  const pmList = document.getElementById('pm-list');
  const pmStatus = document.getElementById('pm-status');
  const pmMsg = document.getElementById('pm-msg');
  const pmRefreshBtn = document.getElementById('pm-refresh');
  const pmStopAllBtn = document.getElementById('pm-stop-all');

  async function fetchJson(url, options){
    const res = await fetch(url, options);
    const ct = res.headers.get('content-type') || '';
    let data = null;
    try { data = ct.includes('application/json') ? await res.json() : await res.text(); } catch(e){}
    if(!res.ok){
      throw new Error(`HTTP ${res.status}: ${JSON.stringify(data)}`);
    }
    return data;
  }

  function getDisplayName(fullName){
    try{
      const base = (fullName.split('/').pop() || '').replace(/\.sh$/i, '');
      const m = base.match(/scene(\d+[a-z]?)/i);
      if(m){
        return `S${m[1].toUpperCase()}`;
      }
      const cleaned = base
        .replace(/space_?yoga_?teacher_?/i, '')
        .replace(/yoga_?sessions?_?/i, '')
        .replace(/baseline_?/i, '')
        .replace(/_/g, ' ')
        .trim();
      return cleaned.length > 18 ? cleaned.slice(0,18) + '…' : cleaned;
    }catch(e){
      return fullName;
    }
  }

  function extractSceneKey(fullName){
    const base = (fullName.split('/').pop() || '').replace(/\.sh$/i, '');
    const m = base.match(/scene(\d+)([a-z]?)/i);
    if(m){
      return { has:true, num: parseInt(m[1], 10), suffix: (m[2]||'').toLowerCase(), base };
    }
    return { has:false, num: Number.MAX_SAFE_INTEGER, suffix:'', base };
  }

  function compareScripts(aName, bName){
    const a = extractSceneKey(aName);
    const b = extractSceneKey(bName);
    if(a.has && b.has){
      if(a.num !== b.num) return a.num - b.num;
      if(a.suffix !== b.suffix) return a.suffix < b.suffix ? -1 : 1;
      return 0;
    }
    // fallback to natural compare on base names
    return a.base.localeCompare(b.base, undefined, { numeric: true, sensitivity: 'base' });
  }

  function renderList(registered, running){
    const runningSet = new Set((running?.running_scripts)||[]);
    const sorted = [...registered].sort((a,b) => compareScripts(a.name, b.name));
    const rows = sorted.map(item => {
      const name = item.name;
      const isRunning = item.is_running || runningSet.has(name);
      const desc = item.description || '';
      const playDisabled = isRunning ? 'disabled' : '';
      const stopDisabled = isRunning ? '' : 'disabled';
      const shortName = getDisplayName(name);
      return `
        <tr>
          <td style="white-space:nowrap;">
            <div style="display:flex; align-items:center; gap:8px;">
              <button class="pm-play" data-name="${name}" ${playDisabled}>播放</button>
              <button class="pm-stop" data-name="${name}" ${stopDisabled}>停止</button>
              <span class="pm-name" title="${name}">${shortName}</span>
            </div>
          </td>
          <td style="text-align:center;">${isRunning ? '<span style="color:#2e7d32;">執行中</span>' : '<span style="color:#555;">待機</span>'}</td>
          <td>${desc}</td>
        </tr>
      `;
    }).join('');

    pmList.innerHTML = `
      <table style="width:100%; border-collapse:collapse;">
        <thead>
          <tr style="background:#f7f7f7;">
            <th style="text-align:left;padding:6px 8px; border-bottom:1px solid #eee; width:50%">操作 / 名稱</th>
            <th style="text-align:center;padding:6px 8px; border-bottom:1px solid #eee; width:12%">狀態</th>
            <th style="text-align:left;padding:6px 8px; border-bottom:1px solid #eee;">描述</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;

    // Bind buttons
    pmList.querySelectorAll('.pm-play').forEach(btn => btn.addEventListener('click', async (e) => {
      const name = e.currentTarget.getAttribute('data-name');
      try{
        pmMsg.textContent = `播放中: ${name}...`;
        await fetchJson('/api/scripts/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ script_name: name, background: true })
        });
        pmMsg.textContent = `已觸發播放: ${name}`;
        await refresh();
      }catch(err){
        pmMsg.textContent = `播放失敗: ${err.message}`;
      }
    }));

    pmList.querySelectorAll('.pm-stop').forEach(btn => btn.addEventListener('click', async (e) => {
      const name = e.currentTarget.getAttribute('data-name');
      try{
        pmMsg.textContent = `停止中: ${name}...`;
        // 注意：名稱包含斜線，encodeURIComponent 處理
        await fetchJson(`/api/scripts/stop/${encodeURIComponent(name)}`, { method: 'POST' });
        pmMsg.textContent = `已停止: ${name}`;
        await refresh();
      }catch(err){
        pmMsg.textContent = `停止失敗: ${err.message}`;
      }
    }));
  }

  async function refresh(){
    try{
      const [list, status] = await Promise.all([
        fetchJson('/api/scripts/list'),
        fetchJson('/api/scripts/status')
      ]);
      pmStatus.textContent = `可用腳本: ${list.total_count}，執行中: ${status.total_running}`;
      renderList(list.registered_scripts || [], status);
    }catch(err){
      pmStatus.textContent = `讀取失敗: ${err.message}`;
    }
  }

  pmRefreshBtn.addEventListener('click', refresh);
  pmStopAllBtn.addEventListener('click', async () => {
    try{
      pmMsg.textContent = '正在停止全部...';
      await fetchJson('/api/scripts/stop-all', { method: 'POST' });
      pmMsg.textContent = '已停止全部';
      await refresh();
    }catch(err){
      pmMsg.textContent = `停止全部失敗: ${err.message}`;
    }
  });

  // 啟動輪詢（每 3 秒）
  refresh();
  setInterval(refresh, 3000);
})();
