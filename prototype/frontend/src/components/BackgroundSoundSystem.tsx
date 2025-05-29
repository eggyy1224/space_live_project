import React, { useState, useEffect, useRef } from 'react';
import { useStore } from '../store';

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

const BGM_PATH = '/audio/BGM/';
const EFFECTS_PATH = '/audio/effects/';

// 假設 public/audio/BGM 和 public/audio/effects 中有以下檔案
// 您需要根據實際檔案名稱進行修改
const bgmFiles = ['spacelive_theme.mp3', 'spacelive_theme2.mp3', 'heavy_metal_bgm_01.mp3', 'heavy_metal_bgm_02.mp3', 'heavy_metal_bgm_03.mp3', 'space_live_country_theme1.mp3', 'space_live_country_theme2.mp3', 'hihi (1).mp3', 'hihi (2).mp3', 'hihi (3).mp3', 'hihi.mp3']; // 更新後的 BGM 檔案列表
const effectFiles = ['winds_blowing.mp3', 'Energetic_fast_pace.mp3', 'Ambient_keyboard_cli_2.mp3', 'spaceship_ambience_01.mp3', 'spaceship_ambience_02.mp3', 'spaceship_ambience_03.mp3', 'spaceship_ambience_04.mp3', 'taiwan_variety_sfx_01.mp3', 'taiwan_variety_sfx_02.mp3', 'taiwan_variety_sfx_03.mp3', 'taiwan_variety_sfx_04.mp3', '測試音效1.mp3', '測試音效2.mp3', '測試音效3.mp3', '測試音效4.mp3', '測試音效5.mp3']; // 更新後的音效檔案列表

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
  }, [isUserInteracted]); // 當 isUserInteracted 改變時，此 useEffect 不會重新執行，我們只需要它執行一次

  // 載入並播放 BGM
  useEffect(() => {
    if (!audioContext || !bgmGainNodeRef.current || bgmFiles.length === 0 || !isUserInteracted) return;

    let currentBgmIndex = -1; // 雖然 currentBgmIndex 在此處宣告了，但並未在新邏輯中用來防止重複播放。

    const playBGM = async () => {
      if (!audioContext || !bgmGainNodeRef.current) return;

      // 停止目前播放的 BGM (如果有的話)
      if (bgmSourceRef.current) {
        bgmSourceRef.current.onended = null; // 清除舊的 onended 處理器
        bgmSourceRef.current.stop();
        bgmSourceRef.current.disconnect();
      }

      // 隨機選擇一個 BGM 檔案
      // 如果只有一首歌，則 randomIndex 永遠是 0
      // 如果有多首歌，則隨機選擇
      let randomIndex = Math.floor(Math.random() * bgmFiles.length);
      
      // 如果有多於一首歌，且新選的歌和上一首相同，則重新選擇，直到不同為止
      // (這個邏輯可以確保下一首歌和當前歌曲不同，但如果歌曲列表只有一首歌，則無效)
      if (bgmFiles.length > 1 && randomIndex === currentBgmIndex) {
        randomIndex = (currentBgmIndex + 1 + Math.floor(Math.random() * (bgmFiles.length -1))) % bgmFiles.length;
      }
      currentBgmIndex = randomIndex;
      const selectedBGM = bgmFiles[randomIndex];

      try {
        const response = await fetch(`${BGM_PATH}${selectedBGM}`);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.loop = false; // 修改：不再循環播放單曲
        source.connect(bgmGainNodeRef.current);
        source.start();
        bgmSourceRef.current = source;
        bgmStartRef.current = audioContext.currentTime;
        setRuntime({ bgm: selectedBGM, bgmTime: 0 });
        startBgmAnalysis();

        // 新增：當歌曲播放完畢時，再次呼叫 playBGM 以播放下一首
        source.onended = () => {
          if (audioContext && audioContext.state === 'running') {
            setRuntime({ bgm: null });
            playBGM();
          }
        };

      } catch (error) {
        console.error(`Error loading BGM: ${selectedBGM}`, error);
        // 如果載入失敗，也可以嘗試在一段時間後播放下一首，避免立即重試相同的錯誤
        if (audioContext && audioContext.state === 'running') {
          setTimeout(() => playBGM(), 5000); // 5秒後重試
        }
      }
    };

    playBGM();

    return () => {
      if (bgmSourceRef.current) {
        bgmSourceRef.current.onended = null; // 清除 onended 處理器
        bgmSourceRef.current.stop();
        bgmSourceRef.current.disconnect();
      }
      stopBgmAnalysis();
      setRuntime({ bgm: null });
    };
  }, [audioContext, isUserInteracted]); // 依賴 audioContext 和 isUserInteracted

  // 載入並隨機播放音效
  useEffect(() => {
    if (!audioContext || !effectGainNodeRef.current || effectFiles.length === 0 || !isUserInteracted) return;

    let effectTimeoutId: NodeJS.Timeout | null = null;

    const playRandomEffect = async () => {
      if (!audioContext || !effectGainNodeRef.current) return;

      // 停止目前播放的音效 (如果有的話)
      // 雖然通常音效是短暫的，但以防萬一
      if (effectSourceRef.current) {
        try {
          effectSourceRef.current.stop();
          effectSourceRef.current.disconnect();
        } catch (e) {
          // 忽略 "InvalidStateNode" 錯誤，這可能在音效已經自然結束時發生
          if ((e as DOMException).name !== 'InvalidStateError') {
            console.error("Error stopping previous effect:", e);
          }
        }
      }

      // 隨機選擇一個音效檔案
      const randomIndex = Math.floor(Math.random() * effectFiles.length);
      const selectedEffect = effectFiles[randomIndex];

      try {
        const response = await fetch(`${EFFECTS_PATH}${selectedEffect}`);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(effectGainNodeRef.current);
        source.start();
        effectSourceRef.current = source;
        triggerEffect();
        setRuntime({ sfxActive: true });

        // 音效播放完畢後，設定下一次隨機播放
        source.onended = () => {
          setRuntime({ sfxActive: false });
          scheduleNextEffect();
        };

      } catch (error) {
        console.error(`Error loading effect: ${selectedEffect}`, error);
        // 如果載入失敗，也嘗試安排下一個音效
        scheduleNextEffect();
      }
    };

    const scheduleNextEffect = () => {
      // 隨機時間間隔 (例如 5 到 15 秒)
      const randomInterval = Math.random() * 10000 + 5000;
      if (effectTimeoutId) {
        clearTimeout(effectTimeoutId);
      }
      effectTimeoutId = setTimeout(playRandomEffect, randomInterval);
    };

    scheduleNextEffect(); // 初始啟動

    return () => {
      if (effectTimeoutId) {
        clearTimeout(effectTimeoutId);
      }
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
  }, [audioContext, isUserInteracted]); // 依賴 audioContext 和 isUserInteracted

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