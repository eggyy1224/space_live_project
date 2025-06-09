import { useEffect, useRef, useState } from 'react';
import AudioService from './AudioService';

const WS_URL = `ws://${window.location.host}/api/real-time/ws`;

export function useRealtimeVoice() {
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const [streaming, setStreaming] = useState(false);

  useEffect(() => {
    return () => {
      mediaRef.current?.stop();
      wsRef.current?.close();
    };
  }, []);

  const start = async () => {
    if (streaming) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => {
      const recorder = new MediaRecorder(stream);
      mediaRef.current = recorder;
      recorder.ondataavailable = (e) => {
        if (ws.readyState === WebSocket.OPEN) ws.send(e.data);
      };
      recorder.start(250);
      setStreaming(true);
    };
    ws.onmessage = (event) => {
      const data = event.data;
      if (data instanceof Blob) {
        AudioService.getInstance().playAudio(data).catch((err) => {
          console.error('Failed to play realtime audio', err);
        });
      }
    };
    ws.onclose = () => {
      setStreaming(false);
      recorderCleanup();
    };
  };

  const stop = () => {
    wsRef.current?.close();
    recorderCleanup();
  };

  const recorderCleanup = () => {
    mediaRef.current?.stop();
    mediaRef.current = null;
  };

  return { start, stop, streaming };
}

