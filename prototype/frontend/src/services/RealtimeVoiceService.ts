import { useEffect, useRef, useState } from 'react';
import AudioService from './AudioService';
import { useStore } from '../store';

const WS_URL = `ws://${window.location.hostname}:8000/api/real-time/ws`;

// 專門用於實時音頻播放的類
class RealtimeAudioPlayer {
  private audioContext: AudioContext | null = null
  private analyser: AnalyserNode | null = null;
  private gainNode: GainNode | null = null;
  private analysisFrameId: number | null = null;
  private audioQueue: AudioBuffer[] = [];
  private isPlaying = false;
  private nextStartTime = 0;
  private currentSourceNodes: AudioBufferSourceNode[] = []; // 追蹤所有播放中的音頻源

  async initialize() {
    if (!this.audioContext) {
      this.audioContext = new AudioContext();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = 0.8;
      
      this.analyser.connect(this.gainNode);
      this.gainNode.connect(this.audioContext.destination);
    }
    
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
  }

  async addAudioChunk(audioData: ArrayBuffer) {
    if (!this.audioContext) return;
    
    try {
      const audioBuffer = await this.audioContext.decodeAudioData(audioData);
      this.audioQueue.push(audioBuffer);
      
      if (!this.isPlaying) {
        this.startPlayback();
      }
    } catch (error) {
      console.error('[RealtimeAudioPlayer] Failed to decode audio:', error);
    }
  }

  private startPlayback() {
    if (!this.audioContext || !this.analyser) return;
    
    this.isPlaying = true;
    this.nextStartTime = this.audioContext.currentTime;
    
    // 開始音頻分析
    this.startAudioAnalysis();
    
    // 設置 speaking 狀態
    useStore.getState().setSpeaking(true);
    
    this.playNextChunk();
  }

  private playNextChunk() {
    if (!this.audioContext || !this.analyser || this.audioQueue.length === 0) {
      // 如果沒有更多音頻塊，等待一小段時間後檢查
      setTimeout(() => {
        if (this.audioQueue.length === 0 && this.isPlaying) {
          this.stopPlayback();
        } else if (this.audioQueue.length > 0) {
          this.playNextChunk();
        }
      }, 100);
      return;
    }

    const audioBuffer = this.audioQueue.shift()!;
    const source = this.audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.analyser);

    // 追蹤這個音頻源
    this.currentSourceNodes.push(source);

    // 計算開始時間，確保連續播放
    const startTime = Math.max(this.nextStartTime, this.audioContext.currentTime);
    source.start(startTime);
    
    // 更新下次開始時間
    this.nextStartTime = startTime + audioBuffer.duration;
    
    // 設置結束回調
    source.onended = () => {
      // 從追蹤列表中移除這個源
      const index = this.currentSourceNodes.indexOf(source);
      if (index > -1) {
        this.currentSourceNodes.splice(index, 1);
      }
      this.playNextChunk();
    };

    console.log(`[RealtimeAudioPlayer] Playing audio chunk: ${audioBuffer.duration.toFixed(3)}s`);
  }

  // (燈光控制已改為在對話開始/結束時透過 HTTP 控制，移除 WS 連線)

  private startAudioAnalysis() {
    if (!this.analyser) return;
    
    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    
    const analyze = () => {
      if (!this.isPlaying || !this.analyser) {
        this.stopAudioAnalysis();
        return;
      }
      
      this.analyser.getByteTimeDomainData(dataArray);
      let sumOfSquares = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const norm = (dataArray[i] / 128.0) - 1.0;
        sumOfSquares += norm * norm;
      }
      const rms = Math.sqrt(sumOfSquares / dataArray.length);
      
      // 映射到 jawOpen
      const sensitivity = 4.0;
      const threshold = 0.01;
      let jawOpenValue = 0;
      if (rms > threshold) {
        jawOpenValue = Math.min(1.0, rms * sensitivity);
      }
      
      // 更新嘴型
      useStore.getState().setAudioLipsyncTarget('jawOpen', jawOpenValue);
      useStore.getState().setAudioAverageVolume(rms);
      
      this.analysisFrameId = requestAnimationFrame(analyze);
    };
    
    analyze();
  }

  private stopAudioAnalysis() {
    if (this.analysisFrameId !== null) {
      cancelAnimationFrame(this.analysisFrameId);
      this.analysisFrameId = null;
    }
    
    // 重置嘴型
    useStore.getState().setAudioLipsyncTarget('jawOpen', 0);

  }

  stopPlayback() {
    this.isPlaying = false;
    this.audioQueue = [];
    this.nextStartTime = 0;
    
    this.stopAudioAnalysis();
    useStore.getState().setSpeaking(false);
    
    console.log('[RealtimeAudioPlayer] Stopped playback');
  }

  // 新增：立即中斷播放，清空隊列並停止所有播放中的音頻源
  immediateStopPlayback() {
    console.log('[RealtimeAudioPlayer] Immediate stop - clearing queue and stopping all sources');
    
    // 使用setTimeout確保停止操作不阻塞其他音頻處理
    setTimeout(() => {
      // 停止所有正在播放的音頻源
      this.currentSourceNodes.forEach(source => {
        try {
          source.stop();
          source.disconnect();
        } catch (error) {
          // 忽略已經停止的源
        }
      });
      this.currentSourceNodes = [];
      
      // 清空隊列
      this.audioQueue = [];
      this.isPlaying = false;
      this.nextStartTime = 0;
      
      this.stopAudioAnalysis();
      
      // 異步更新狀態，避免阻塞
      requestAnimationFrame(() => {
        useStore.getState().setSpeaking(false);
      });
      
      console.log('[RealtimeAudioPlayer] Immediate stop completed');
    }, 0);
  }

  cleanup() {
    this.stopPlayback();
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.analyser = null;
    this.gainNode = null;

  }

  // 提供公開方法讓外部也能調用立即停止
  public forceStop() {
    this.immediateStopPlayback();
  }
}

export function useRealtimeVoice() {
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorNodeRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioPlayerRef = useRef<RealtimeAudioPlayer | null>(null);
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
      hasAudioPlayer: !!audioPlayerRef.current,
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
    
    if (audioPlayerRef.current) {
      audioPlayerRef.current.cleanup();
      audioPlayerRef.current = null;
    }
    
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

    // 確保會話結束時關閉物理燈光
    fetch('http://localhost:8000/api/physical-light/set-brightness', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ brightness: 0 })
    }).catch(err => console.warn('[RealtimeVoice] Failed to ensure light off:', err));

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
      
      // 初始化實時音頻播放器
      audioPlayerRef.current = new RealtimeAudioPlayer();
      await audioPlayerRef.current.initialize();
      
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

        // 清空之前的文字內容
        useStore.getState().setSpeechText('');

        // 會話啟動時開啟物理燈光
        fetch('http://localhost:8000/api/physical-light/set-brightness', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ brightness: 65535 })
        }).catch(err => console.warn('[RealtimeVoice] Failed to turn on light:', err));
        
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

        setStreaming(false);

        // 會話結束時關閉物理燈光
        fetch('http://localhost:8000/api/physical-light/set-brightness', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ brightness: 0 })
        }).catch(err => console.warn('[RealtimeVoice] Failed to turn off light:', err));
      };
      
      ws.onmessage = async (event) => {
        const data = event.data;
        console.log(`[RealtimeVoice] Received message:`, {
          type: typeof data,
          size: data instanceof Blob ? data.size : 'unknown',
          dataType: data.constructor.name
        });
        
        if (data instanceof Blob) {
          // 檢查是否是中斷訊號或文字數據
          if (data.size <= 1024) { // 檢查小於1KB的數據，可能是控制信號
            try {
              const arrayBuffer = await data.arrayBuffer();
              const text = new TextDecoder().decode(arrayBuffer);
              
              if (text === 'INTERRUPT_SIGNAL') {
                console.log('[RealtimeVoice] 🛑 Received interrupt signal - stopping playback immediately');
                // 使用異步方式處理中斷，避免阻塞新的音頻處理
                requestAnimationFrame(() => {
                  if (audioPlayerRef.current) {
                    audioPlayerRef.current.immediateStopPlayback();
                  }
                });
                return;
              }
              
              // 檢查是否是文字數據
              if (text.startsWith('TEXT_DATA:')) {
                try {
                  const textJson = text.substring('TEXT_DATA:'.length);
                  const textData = JSON.parse(textJson);
                  if (textData.type === 'text' && textData.content) {
                    // 異步處理文字更新，避免阻塞音頻流
                    requestAnimationFrame(() => {
                      if (textData.content === 'CLEAR_TEXT') {
                        console.log('[RealtimeVoice] 🗑️ Clearing previous text');
                        useStore.getState().setSpeechText('');
                      } else {
                        console.log('[RealtimeVoice] 📝 Received text delta:', textData.content);
                        
                        // 累積文字到 store
                        const currentText = useStore.getState().speechText || '';
                        useStore.getState().setSpeechText(currentText + textData.content);
                      }
                    });
                  }
                } catch (textError) {
                  console.error('[RealtimeVoice] Failed to parse text data:', textError);
                }
                return;
              }
            } catch (decodeError) {
              // 如果解碼失敗，就當作普通音頻處理
              console.debug('[RealtimeVoice] Failed to decode potential control signal, treating as audio');
            }
          }
          
          console.log(`[RealtimeVoice] 🔊 Received audio response: ${data.size} bytes, type: ${data.type}`);
          
          if (data.size === 0) {
            console.warn('[RealtimeVoice] Received empty audio blob');
            return;
          }
          
          // 🎯 使用實時音頻播放器處理音頻片段 - 完全異步處理
          setTimeout(async () => {
            try {
              const arrayBuffer = await data.arrayBuffer();
              if (audioPlayerRef.current) {
                await audioPlayerRef.current.addAudioChunk(arrayBuffer);
                console.log('[RealtimeVoice] 🎭 Audio chunk added to realtime player');
              }
            } catch (error) {
              console.error('[RealtimeVoice] ❌ Failed to process audio chunk:', error);
            }
          }, 0);
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

  const forceStopPlayback = () => {
    console.log('[RealtimeVoice] 🛑 Force stopping AI playback...');
    if (audioPlayerRef.current) {
      audioPlayerRef.current.forceStop();
    }
  };

  const recorderCleanup = () => {
    cleanup();
  };

  return { start, stop, forceStopPlayback, streaming, error };
}

