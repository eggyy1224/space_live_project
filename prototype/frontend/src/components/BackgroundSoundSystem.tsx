import React, { useState, useEffect, useRef } from 'react';
import { useStore } from '../store';
import { EFFECT_FILES, getBgmPath, getEffectPath } from '../config/resources';

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
  const bgmGainNodeRef = useRef<GainNode | null>(null);
  const effectGainNodeRef = useRef<GainNode | null>(null);
  const bgmAnalyserRef = useRef<AnalyserNode | null>(null);
  const bgmDataRef = useRef<Uint8Array | null>(null);
  const bgmRafRef = useRef<number | null>(null);

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
        const bgmAnalyser = context.createAnalyser();
        bgmAnalyser.fftSize = 256;
        bgmGain.connect(bgmAnalyser);
        bgmAnalyser.connect(context.destination);
        bgmAnalyserRef.current = bgmAnalyser;
        bgmDataRef.current = new Uint8Array(bgmAnalyser.frequencyBinCount);
        bgmGainNodeRef.current = bgmGain;

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

  useEffect(() => {
    if (!audioContext || !bgmGainNodeRef.current || !isUserInteracted) return;

    const stopCurrent = () => {
      if (bgmSourceRef.current) {
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
        source.loop = true;
        source.connect(bgmGainNodeRef.current as GainNode);
        source.start();
        bgmSourceRef.current = source;
        bgmStartRef.current = audioContext.currentTime;
        currentBgmRef.current = track;
        setRuntime({ bgm: track, bgmTime: 0, bgmPlaying: true });
        startBgmAnalysis();
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

    if (bgmPlaying) {
      audioContext.resume().catch(console.error);
      startBgmAnalysis();
    } else {
      audioContext.suspend().catch(console.error);
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
    if (!audioContext || !effectGainNodeRef.current || !isUserInteracted || !selectedEffect) return;

    const playSpecificEffect = async (effectFile: string) => {
      if (!audioContext || !effectGainNodeRef.current) return;

      // 停止目前播放的音效 (如果有的話)
      if (effectSourceRef.current) {
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping previous effect:", e);
          }
        }
      }

      try {
        const response = await fetch(getEffectPath(effectFile));
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(effectGainNodeRef.current);
        source.start();
        effectSourceRef.current = source;

        // 音效播放完畢後重置狀態
        source.onended = () => {
          setRuntime({ sfxActive: false, selectedEffect: null });
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

    const playRandomEffect = async () => {
      if (!audioContext || !effectGainNodeRef.current) return;
      
      // 停止目前播放的音效 (如果有的話)
      if (effectSourceRef.current) {
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping previous effect:", e);
          }
        }
      }

      // 隨機選擇一個音效檔案
      const randomIndex = Math.floor(Math.random() * EFFECT_FILES.length);
      const selectedEffect = EFFECT_FILES[randomIndex];

      try {
        const response = await fetch(getEffectPath(selectedEffect));
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(effectGainNodeRef.current);
        source.start();
        effectSourceRef.current = source;
        triggerEffect();
        setRuntime({ sfxActive: true });

        // 音效播放完畢後重置狀態並安排下一個
        source.onended = () => {
          setRuntime({ sfxActive: false });
          scheduleNextRandomEffect();
        };

      } catch (error) {
        console.error(`Error loading random effect: ${selectedEffect}`, error);
        scheduleNextRandomEffect();
      }
    };

    const scheduleNextRandomEffect = () => {
      if (!randomMode) return; // 如果隨機模式關閉就不安排下一個
      
      const randomInterval = Math.random() * 10000 + 5000; // 5-15秒間隔
      randomEffectTimerRef.current = setTimeout(playRandomEffect, randomInterval);
    };

    if (randomMode) {
      // 隨機模式開啟：開始隨機播放音效
      scheduleNextRandomEffect();
    } else {
      // 隨機模式關閉：清除定時器
      if (randomEffectTimerRef.current) {
        clearTimeout(randomEffectTimerRef.current);
        randomEffectTimerRef.current = null;
      }
    }

    return () => {
      if (randomEffectTimerRef.current) {
        clearTimeout(randomEffectTimerRef.current);
      }
    };
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