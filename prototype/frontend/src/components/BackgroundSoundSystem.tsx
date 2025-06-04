import React, { useState, useEffect, useRef } from 'react';
import { useStore } from '../store';
import { BGM_FILES, EFFECT_FILES, getBgmPath, getEffectPath } from '../config/resources';

// utility to compute RMS from analyser data
const getRms = (analyser: AnalyserNode, dataArray: Uint8Array) => {
  analyser.getByteTimeDomainData(dataArray);
  let sumSquares = 0;
  for (let i = 0; i < dataArray.length; i++) {
    const v = dataArray[i] / 128 - 1;
    sumSquares += v * v;
  }
  return Math.sqrt(sumSquares / dataArray.length);
};

const BackgroundSoundSystem: React.FC = () => {
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const bgmSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const effectSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const manualEffectSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const bgmGainNodeRef = useRef<GainNode | null>(null);
  const bgmPauseNodeRef = useRef<GainNode | null>(null);
  const effectGainNodeRef = useRef<GainNode | null>(null);
  const bgmAnalyserRef = useRef<AnalyserNode | null>(null);
  const bgmDataRef = useRef<Uint8Array | null>(null);
  const bgmRafRef = useRef<number | null>(null);
  const isRandomEffectRef = useRef<boolean>(false);

  const bgmVolume = useStore((state) => state.bgmVolume);
  const effectVolume = useStore((state) => state.effectVolume);
  const setBgmIntensity = useStore((state) => state.setBgmIntensity);
  const triggerEffect = useStore((state) => state.triggerEffect);
  const setRuntime = useStore((s) => s.setRuntime);

  const bgmStartRef = useRef<number>(0);

  const [isUserInteracted, setIsUserInteracted] = useState(false);

  const startBgmAnalysis = () => {
    if (!bgmAnalyserRef.current || !bgmDataRef.current) return;
    const loop = () => {
      if (!bgmAnalyserRef.current || !bgmDataRef.current) return;
      const rms = getRms(bgmAnalyserRef.current, bgmDataRef.current);
      setBgmIntensity(rms);
      if (audioContext) {
        setRuntime({ bgmTime: audioContext.currentTime - bgmStartRef.current });
      }
      bgmRafRef.current = requestAnimationFrame(loop);
    };
    bgmRafRef.current = requestAnimationFrame(loop);
  };

  const stopBgmAnalysis = () => {
    if (bgmRafRef.current) cancelAnimationFrame(bgmRafRef.current);
    bgmRafRef.current = null;
    setBgmIntensity(0);
  };

  // 更新音量設定
  useEffect(() => {
    if (bgmGainNodeRef.current) {
      bgmGainNodeRef.current.gain.value = bgmVolume;
    }
  }, [bgmVolume]);

  useEffect(() => {
    if (effectGainNodeRef.current) {
      effectGainNodeRef.current.gain.value = effectVolume;
    }
  }, [effectVolume]);

  // 初始化 AudioContext
  useEffect(() => {
    const initAudioContext = () => {
      try {
        const context = new (window.AudioContext || (window as any).webkitAudioContext)();
        setAudioContext(context);

        // 建立 BGM 的 GainNode
        const bgmGain = context.createGain();
        bgmGain.gain.value = bgmVolume; // 預設 BGM 音量
        
        // 建立 BGM 暫停控制節點
        const bgmPauseGain = context.createGain();
        bgmPauseGain.gain.value = 1; // 預設不暫停
        
        const bgmAnalyser = context.createAnalyser();
        bgmAnalyser.fftSize = 256;
        
        // BGM 音頻鏈：source -> bgmGain (音量控制) -> bgmPauseGain (暫停控制) -> analyser -> destination
        bgmGain.connect(bgmPauseGain);
        bgmPauseGain.connect(bgmAnalyser);
        bgmAnalyser.connect(context.destination);
        
        bgmAnalyserRef.current = bgmAnalyser;
        bgmDataRef.current = new Uint8Array(bgmAnalyser.frequencyBinCount);
        bgmGainNodeRef.current = bgmGain;
        bgmPauseNodeRef.current = bgmPauseGain;

        // 建立 Effect 的 GainNode
        const effectGain = context.createGain();
        effectGain.gain.value = effectVolume; // 預設 Effect 音量
        effectGain.connect(context.destination);
        effectGainNodeRef.current = effectGain;

      } catch (e) {
        console.error("Web Audio API is not supported in this browser", e);
      }
    };

    // 由於瀏覽器限制，音訊自動播放通常需要用戶互動
    // 我們監聽第一次用戶互動事件來初始化 AudioContext
    const handleUserInteraction = () => {
      if (!isUserInteracted) {
        initAudioContext();
        setIsUserInteracted(true);
        // 移除監聽器，避免重複初始化
        document.removeEventListener('click', handleUserInteraction);
        document.removeEventListener('keydown', handleUserInteraction);
      }
    };

    document.addEventListener('click', handleUserInteraction);
    document.addEventListener('keydown', handleUserInteraction);

    return () => {
      document.removeEventListener('click', handleUserInteraction);
      document.removeEventListener('keydown', handleUserInteraction);
      if (audioContext) {
        audioContext.close().catch(console.error);
      }
    };
  }, [isUserInteracted]);

  // 根據 runtime 狀態控制 BGM
  const bgm = useStore((s) => s.bgm);
  const bgmPlaying = useStore((s) => s.bgmPlaying);
  const currentBgmRef = useRef<string | null>(null);
  // 標記手動停止 BGM，以避免觸發 onended 邏輯
  const manualStopRef = useRef(false);

  useEffect(() => {
    if (!audioContext || !bgmGainNodeRef.current || !isUserInteracted) return;

    const stopCurrent = () => {
      if (bgmSourceRef.current) {
        manualStopRef.current = true;
        bgmSourceRef.current.onended = null;
        bgmSourceRef.current.stop();
        bgmSourceRef.current.disconnect();
        bgmSourceRef.current = null;
      }
      currentBgmRef.current = null;
      stopBgmAnalysis();
    };

    const loadAndPlay = async (track: string) => {
      stopCurrent();
      try {
        const response = await fetch(getBgmPath(track));
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        const random = useStore.getState().randomMode; // check if random mode is on
        source.loop = !random; // disable loop in random mode so ended event fires
        source.connect(bgmGainNodeRef.current as GainNode);
        source.start();
        bgmSourceRef.current = source;
        bgmStartRef.current = audioContext.currentTime;
        currentBgmRef.current = track;
        setRuntime({ bgm: track, bgmTime: 0, bgmPlaying: true });
        startBgmAnalysis();

        // in random mode, pick next track after current ends
        if (random) {
          source.onended = () => {
            if (manualStopRef.current) {
              manualStopRef.current = false;
              return;
            }
            const available = BGM_FILES.filter((b) => b !== track);
            const next = available[Math.floor(Math.random() * available.length)];
            setRuntime({ bgm: next, bgmPlaying: true });
          };
        }
      } catch (e) {
        console.error('Error loading BGM', e);
      }
    };

    if (!bgm) {
      stopCurrent();
      return;
    }

    if (currentBgmRef.current !== bgm) {
      loadAndPlay(bgm);
      return;
    }

    // 使用音量控制實現 BGM 的暫停/播放，而不是操作 AudioContext 或停止 source
    if (bgmPlaying) {
      console.log('BGM play requested, resuming...');
      // 確保 AudioContext 正在運行
      if (audioContext.state === 'suspended') {
        audioContext.resume().catch(console.error);
      }
      // 取消暫停 BGM
      if (bgmPauseNodeRef.current) {
        bgmPauseNodeRef.current.gain.value = 1;
        console.log('BGM pause node set to 1 (playing)');
      }
      startBgmAnalysis();
    } else {
      console.log('BGM pause requested, muting pause node...');
      // BGM 暫停時將暫停節點音量設為 0，但保持播放源和用戶音量控制不變
      if (bgmPauseNodeRef.current) {
        bgmPauseNodeRef.current.gain.value = 0;
        console.log('BGM pause node set to 0 (paused)');
      }
      stopBgmAnalysis();
    }
  }, [bgm, bgmPlaying, audioContext, isUserInteracted]);

  // 載入並隨機播放音效
  useEffect(() => {
    if (!audioContext || !effectGainNodeRef.current || EFFECT_FILES.length < 1 || !isUserInteracted) return;

    // 清理函數：在組件卸載時清除音效
    return () => {
      if (effectSourceRef.current) {
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
             console.error("Error stopping effect on cleanup:", e);
          }
        }
      }
      setRuntime({ sfxActive: false });
    };
  }, [audioContext, isUserInteracted]);

  // 監聽 selectedEffect 變化，手動播放指定音效
  const selectedEffect = useStore((s) => s.selectedEffect);
  useEffect(() => {
    if (!audioContext || !effectGainNodeRef.current || !isUserInteracted || !selectedEffect) {
      if (selectedEffect) {
        console.log('Manual effect blocked - missing requirements:', {
          audioContext: !!audioContext,
          effectGainNode: !!effectGainNodeRef.current,
          isUserInteracted,
          selectedEffect
        });
      }
      return;
    }

    console.log('Manual effect starting:', selectedEffect);

    const playSpecificEffect = async (effectFile: string) => {
      if (!audioContext || !effectGainNodeRef.current) return;

      console.log('AudioContext state before effect play:', audioContext.state);
      
      if (audioContext.state === 'suspended') {
        console.log('Resuming AudioContext for effect playback...');
        await audioContext.resume();
      }

      // 停止目前播放的手動音效 (如果有的話)
      if (manualEffectSourceRef.current) {
        try {
          manualEffectSourceRef.current.stop();
          manualEffectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping previous manual effect:", e);
          }
        }
      }

      try {
        console.log('Loading manual effect:', effectFile);
        const response = await fetch(getEffectPath(effectFile));
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(effectGainNodeRef.current);
        source.start();
        manualEffectSourceRef.current = source; // 使用 manualEffectSourceRef
        // isRandomEffectRef.current = false; // 不再需要這個標記

        console.log('Manual effect playing:', effectFile);

        source.onended = () => {
          console.log('Manual effect ended:', effectFile);
          setRuntime({ sfxActive: false, selectedEffect: null });
          manualEffectSourceRef.current = null;
        };

      } catch (error) {
        console.error(`Error loading effect: ${effectFile}`, error);
        setRuntime({ sfxActive: false, selectedEffect: null });
      }
    };

    playSpecificEffect(selectedEffect);
  }, [selectedEffect, audioContext, isUserInteracted]);

  // 監聽隨機模式變化，動態開啟/關閉隨機音效
  const randomMode = useStore((s) => s.randomMode);
  const randomEffectTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  useEffect(() => {
    if (!audioContext || !effectGainNodeRef.current || !isUserInteracted) return;
    
    if (!randomMode) {
      console.log('Random mode disabled, clearing random effect timers and stopping current random effect...');
      if (randomEffectTimerRef.current) {
        clearTimeout(randomEffectTimerRef.current);
        randomEffectTimerRef.current = null;
      }
      
      // 停止當前的隨機音效 (如果有的話)
      if (effectSourceRef.current) {
        console.log('Stopping current random effect due to random mode OFF...');
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping random effect:", e);
          }
        }
        effectSourceRef.current = null; // 清理 Ref
        // sfxActive 狀態由 onended 或手動播放控制，這裡不直接改
      }
      return;
    }

    const playRandomEffect = async () => {
      console.log('playRandomEffect called, randomMode:', randomMode);
      if (!audioContext || !effectGainNodeRef.current || !randomMode) {
        console.log('Random effect blocked - randomMode:', randomMode, 'audioContext:', !!audioContext, 'effectGainNode:', !!effectGainNodeRef.current);
        return;
      }
      
      console.log('Playing random effect...');
      
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }
      
      // 停止目前播放的隨機音效 (如果有的話)
      if (effectSourceRef.current) {
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping previous random effect:", e);
          }
        }
      }

      const randomIndex = Math.floor(Math.random() * EFFECT_FILES.length);
      const randomEffectFile = EFFECT_FILES[randomIndex]; // 改名以區分

      try {
        const response = await fetch(getEffectPath(randomEffectFile));
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(effectGainNodeRef.current);
        source.start();
        effectSourceRef.current = source; // 隨機音效使用 effectSourceRef
        triggerEffect();
        setRuntime({ sfxActive: true });

        source.onended = () => {
          setRuntime({ sfxActive: false });
          effectSourceRef.current = null;
          if (randomMode) {
            scheduleNextRandomEffect();
          }
        };

      } catch (error) {
        console.error(`Error loading random effect: ${randomEffectFile}`, error);
        if (randomMode) { // 即使載入失敗也嘗試安排下一個
            scheduleNextRandomEffect();
        }
      }
    };

    const scheduleNextRandomEffect = () => {
      console.log('scheduleNextRandomEffect called, randomMode:', randomMode);
      if (!randomMode) {
        console.log('Random mode off, not scheduling next random effect');
        return; 
      }
      
      const randomInterval = Math.random() * 10000 + 5000; // 5-15秒間隔
      console.log('Scheduling next random effect in', randomInterval / 1000, 'seconds');
      randomEffectTimerRef.current = setTimeout(playRandomEffect, randomInterval);
    };

    // 隨機模式開啟：開始隨機播放音效
    console.log("Initial schedule for random effect in random mode useEffect")
    scheduleNextRandomEffect();

    return () => {
      console.log("Cleaning up random effect useEffect for randomMode:", randomMode);
      if (randomEffectTimerRef.current) {
        clearTimeout(randomEffectTimerRef.current);
        randomEffectTimerRef.current = null;
      }
      //組件卸載或 randomMode 變為 false 時，確保停止正在播放的隨機音效
      if (effectSourceRef.current) {
         console.log('Stopping current random effect due to cleanup or randomMode change...');
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping random effect in cleanup:", e);
          }
        }
        effectSourceRef.current = null;
        setRuntime({ sfxActive: false }); // 確保狀態同步
      }
    };
  }, [randomMode, audioContext, isUserInteracted, setRuntime, triggerEffect]); // 添加依賴項

  // 監聽隨機模式變化，決定是否啟動隨機 BGM
  useEffect(() => {
    if (!audioContext || !isUserInteracted) return;

    if (randomMode && !useStore.getState().bgm) {
      const randomBgm = BGM_FILES[Math.floor(Math.random() * BGM_FILES.length)];
      console.log('Starting random BGM:', randomBgm);
      setRuntime({ bgm: randomBgm, bgmPlaying: true });
    }
  }, [randomMode, audioContext, isUserInteracted]);

  // 這個組件本身不渲染任何 UI，它只在背景運作
  // 但我們可以提供一個按鈕讓用戶手動啟用音訊（如果瀏覽器需要）
  if (!isUserInteracted) {
    return (
      <div style={{ position: 'fixed', top: '10px', left: '10px', zIndex: 9999 }}>
        <button onClick={() => setIsUserInteracted(true)}>
          Enable Background Sounds (Click anywhere or press any key)
        </button>
      </div>
    );
  }

  return null;
};

export default BackgroundSoundSystem; 