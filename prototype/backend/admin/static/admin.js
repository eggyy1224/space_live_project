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
})();
