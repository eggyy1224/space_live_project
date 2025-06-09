import { useEffect, useRef, useState } from 'react';
import AudioService from './AudioService';

const WS_URL = `ws://${window.location.hostname}:8000/api/real-time/ws`;

export function useRealtimeVoice() {
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorNodeRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (window as any).__realtimeVoiceDebug = {
      streaming,
      error,
      wsUrl: WS_URL,
      hasWebSocket: !!wsRef.current,
      hasAudioContext: !!audioContextRef.current,
      hasSourceNode: !!sourceNodeRef.current,
      hasProcessorNode: !!processorNodeRef.current,
      hasMediaStream: !!streamRef.current,
      wsState: wsRef.current?.readyState,
      audioContextState: audioContextRef.current?.state,
      mediaStreamTracks: streamRef.current?.getTracks().map(t => ({
        kind: t.kind,
        label: t.label,
        enabled: t.enabled,
        readyState: t.readyState
      })) || []
    };
  });

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  const cleanup = () => {
    console.log('[RealtimeVoice] Starting cleanup...');
    
    if (processorNodeRef.current) {
      console.log('[RealtimeVoice] Disconnecting processor node...');
      processorNodeRef.current.disconnect();
      processorNodeRef.current = null;
    }

    if (sourceNodeRef.current) {
      console.log('[RealtimeVoice] Disconnecting source node...');
      sourceNodeRef.current.disconnect();
      sourceNodeRef.current = null;
    }

    if (audioContextRef.current) {
      console.log('[RealtimeVoice] Closing audio context...');
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (streamRef.current) {
      console.log('[RealtimeVoice] Stopping media tracks...');
      streamRef.current.getTracks().forEach(track => {
        console.log(`[RealtimeVoice] Stopping track: ${track.kind}, enabled: ${track.enabled}, readyState: ${track.readyState}`);
        track.stop();
      });
      streamRef.current = null;
      console.log('[RealtimeVoice] All media tracks stopped');
    }

    if (wsRef.current) {
      console.log('[RealtimeVoice] Closing WebSocket...');
      wsRef.current.close();
      wsRef.current = null;
    }

    setStreaming(false);
    setError(null);
    console.log('[RealtimeVoice] Cleanup completed');
  };

  // 將 Float32Array 音頻數據轉換為 PCM16 格式
  const convertToPCM16 = (inputBuffer: Float32Array): Int16Array => {
    const outputBuffer = new Int16Array(inputBuffer.length);
    for (let i = 0; i < inputBuffer.length; i++) {
      // 將 [-1, 1] 範圍的浮點數轉換為 [-32768, 32767] 範圍的整數
      const sample = Math.max(-1, Math.min(1, inputBuffer[i]));
      outputBuffer[i] = sample < 0 ? sample * 32768 : sample * 32767;
    }
    return outputBuffer;
  };

  // 重採樣音頻到 24kHz
  const resampleTo24kHz = (inputBuffer: Float32Array, inputSampleRate: number): Float32Array => {
    const targetSampleRate = 24000;
    if (inputSampleRate === targetSampleRate) {
      return inputBuffer;
    }
    
    const resampleRatio = targetSampleRate / inputSampleRate;
    const outputLength = Math.floor(inputBuffer.length * resampleRatio);
    const outputBuffer = new Float32Array(outputLength);
    
    for (let i = 0; i < outputLength; i++) {
      const sourceIndex = i / resampleRatio;
      const index = Math.floor(sourceIndex);
      const fraction = sourceIndex - index;
      
      if (index + 1 < inputBuffer.length) {
        // 線性插值
        outputBuffer[i] = inputBuffer[index] * (1 - fraction) + inputBuffer[index + 1] * fraction;
      } else {
        outputBuffer[i] = inputBuffer[index] || 0;
      }
    }
    
    return outputBuffer;
  };

  const start = async () => {
    if (streaming) {
      console.log('[RealtimeVoice] Already streaming, ignoring start request');
      return;
    }
    
    try {
      console.log('[RealtimeVoice] Starting realtime voice...');
      console.log(`[RealtimeVoice] Target WebSocket URL: ${WS_URL}`);
      setError(null);
      
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('瀏覽器不支援媒體設備 API');
      }
      
      console.log('[RealtimeVoice] Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100, // 高採樣率以便後續重採樣
        } 
      });
      streamRef.current = stream;
      console.log('[RealtimeVoice] Got media stream with tracks:', stream.getTracks().map(t => `${t.kind}:${t.label}`));
      
      // 創建 AudioContext
      audioContextRef.current = new AudioContext({ sampleRate: 44100 });
      await audioContextRef.current.resume();
      
      console.log(`[RealtimeVoice] AudioContext created with sample rate: ${audioContextRef.current.sampleRate}Hz`);
      
      console.log(`[RealtimeVoice] Creating WebSocket connection to: ${WS_URL}`);
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      
      const connectionTimeout = setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
          console.error('[RealtimeVoice] WebSocket connection timeout');
          ws.close();
          cleanup();
          setError('連接超時，請檢查網絡連接');
        }
      }, 10000);
      
      ws.onopen = () => {
        clearTimeout(connectionTimeout);
        console.log('[RealtimeVoice] WebSocket connected successfully!');
        
        try {
          // 創建音頻處理鏈
          const source = audioContextRef.current!.createMediaStreamSource(stream);
          sourceNodeRef.current = source;
          
          // 創建 ScriptProcessorNode 來處理音頻數據
          const bufferSize = 4096; // 較大的緩衝區以減少處理頻率
          const processor = audioContextRef.current!.createScriptProcessor(bufferSize, 1, 1);
          processorNodeRef.current = processor;
          
          processor.onaudioprocess = (event) => {
            if (ws.readyState !== WebSocket.OPEN) return;
            
            const inputBuffer = event.inputBuffer.getChannelData(0); // 獲取單聲道數據
            
            // 重採樣到 24kHz
            const resampledBuffer = resampleTo24kHz(inputBuffer, audioContextRef.current!.sampleRate);
            
            // 轉換為 PCM16 格式
            const pcm16Buffer = convertToPCM16(resampledBuffer);
            
            // 轉換為 bytes
            const audioBytes = new Uint8Array(pcm16Buffer.buffer);
            
            if (audioBytes.length > 0) {
              console.log(`[RealtimeVoice] Sending PCM16 audio: ${audioBytes.length} bytes (${pcm16Buffer.length} samples)`);
              ws.send(audioBytes);
            }
          };
          
          // 連接音頻節點
          source.connect(processor);
          processor.connect(audioContextRef.current!.destination);
          
          setStreaming(true);
          console.log('[RealtimeVoice] ✅ Realtime voice streaming started successfully!');
          console.log('[RealtimeVoice] 🎤 現在可以開始說話了，AI 會即時回應');
        } catch (audioError) {
          console.error('[RealtimeVoice] Failed to setup audio processing:', audioError);
          setError('無法啟動音頻處理功能');
          cleanup();
        }
      };
      
      ws.onerror = (error) => {
        clearTimeout(connectionTimeout);
        console.error('[RealtimeVoice] WebSocket error:', error);
        setError('連接錯誤，請檢查網絡狀態');
        cleanup();
      };
      
      ws.onclose = (event) => {
        clearTimeout(connectionTimeout);
        console.log(`[RealtimeVoice] WebSocket closed: code=${event.code}, reason=${event.reason}`);
        
        if (event.code !== 1000) {
          setError(`連接意外關閉 (${event.code}): ${event.reason || '未知原因'}`);
        }
        
        setStreaming(false);
      };
      
      ws.onmessage = (event) => {
        const data = event.data;
        console.log(`[RealtimeVoice] Received message:`, {
          type: typeof data,
          size: data instanceof Blob ? data.size : 'unknown',
          dataType: data.constructor.name
        });
        
        if (data instanceof Blob) {
          console.log(`[RealtimeVoice] 🔊 Received audio response: ${data.size} bytes, type: ${data.type}`);
          
          if (data.size === 0) {
            console.warn('[RealtimeVoice] Received empty audio blob');
            return;
          }
          
          // 使用簡單的 HTMLAudioElement 直接播放，避免 AudioContext 衝突
          try {
            const audioUrl = URL.createObjectURL(data);
            const audio = new Audio(audioUrl);
            
            // 設置音頻屬性
            audio.volume = 0.8; // 稍微降低音量避免過響
            audio.preload = 'auto';
            
            // 播放完成後清理資源
            audio.onended = () => {
              URL.revokeObjectURL(audioUrl);
              console.log('[RealtimeVoice] ✅ Audio played successfully and resources cleaned up');
            };
            
            audio.onerror = (err) => {
              URL.revokeObjectURL(audioUrl);
              console.error('[RealtimeVoice] ❌ Failed to play realtime audio:', err);
              console.error('[RealtimeVoice] Audio blob details:', {
                size: data.size,
                type: data.type,
                audioUrl: audioUrl
              });
            };
            
            // 開始播放
            audio.play()
              .then(() => {
                console.log('[RealtimeVoice] 🎵 Audio playback started');
              })
              .catch((err) => {
                URL.revokeObjectURL(audioUrl);
                console.error('[RealtimeVoice] ❌ Failed to start audio playback:', err);
              });
              
          } catch (error) {
            console.error('[RealtimeVoice] ❌ Failed to create audio URL:', error);
          }
        } else {
          console.log('[RealtimeVoice] Received non-audio message:', data);
        }
      };
      
    } catch (error) {
      console.error('[RealtimeVoice] Failed to start realtime voice:', error);
      cleanup();
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          setError('需要麥克風權限才能使用實時語音功能');
        } else if (error.name === 'NotFoundError') {
          setError('找不到麥克風設備');
        } else if (error.name === 'NotReadableError') {
          setError('麥克風被其他應用程式占用');
        } else {
          setError(`啟動失敗: ${error.message}`);
        }
      } else {
        setError('無法啟動實時語音功能');
      }
    }
  };

  const stop = () => {
    console.log('[RealtimeVoice] 🛑 Stopping realtime voice...');
    cleanup();
  };

  const recorderCleanup = () => {
    cleanup();
  };

  return { start, stop, streaming, error };
}

