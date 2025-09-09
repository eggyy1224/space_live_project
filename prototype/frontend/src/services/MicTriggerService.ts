import { useStore } from '../store';
import logger, { LogCategory } from '../utils/LogManager';

type MicTriggerState = {
  enabled: boolean;
  thresholdRms: number;
  minHoldMs: number;
  cooldownMs: number;
};

const API_BASE_URL = `http://${window.location.hostname}:8000`;

class MicTriggerService {
  private static instance: MicTriggerService;
  private audioContext: AudioContext | null = null;
  private enabling: boolean = false;
  private mediaStream: MediaStream | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;
  private analyser: AnalyserNode | null = null;
  private dataArray: Uint8Array | null = null;
  private rafId: number | null = null;
  private holdStart: number | null = null;
  private lastTriggerAt: number = 0;
  private armed: boolean = true;
  private belowSince: number | null = null;

  public static getInstance(): MicTriggerService {
    if (!MicTriggerService.instance) {
      MicTriggerService.instance = new MicTriggerService();
    }
    return MicTriggerService.instance;
  }

  private getState(): MicTriggerState {
    const s = useStore.getState();
    return {
      enabled: s.micTriggerEnabled,
      thresholdRms: s.micThresholdRms,
      minHoldMs: s.micMinHoldMs,
      cooldownMs: s.micCooldownMs,
    };
  }

  async enable(): Promise<void> {
    if (this.enabling) return;
    if (this.audioContext && this.mediaStream) return;
    this.enabling = true;
    try {
      useStore.getState().setMicError(null);
      const CtxCtor: any = (window as any).AudioContext || (window as any).webkitAudioContext;
      if (!CtxCtor) throw new Error('Web Audio API not available');
      const ctx: AudioContext = new CtxCtor();
      this.audioContext = ctx;
      if (ctx.state === 'suspended') {
        await ctx.resume();
      }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('MediaDevices API not available');
      }
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // 使用本地變數 ctx 避免並發時 this.audioContext 被清空
      this.sourceNode = ctx.createMediaStreamSource(this.mediaStream);
      this.analyser = ctx.createAnalyser();
      this.analyser.fftSize = 256;
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
      this.sourceNode.connect(this.analyser);
      this.startLoop();
      useStore.getState().setMicTriggerEnabled(true);
      logger.info('[MicTrigger] enabled', LogCategory.AUDIO);
    } catch (err) {
      logger.error('[MicTrigger] enable failed', LogCategory.AUDIO, err);
      useStore.getState().setMicError(String(err));
      this.disable();
    } finally {
      this.enabling = false;
    }
  }

  disable(): void {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
    try { this.sourceNode?.disconnect(); } catch {}
    try { this.analyser?.disconnect(); } catch {}
    this.sourceNode = null;
    this.analyser = null;
    this.dataArray = null;
    if (this.mediaStream) {
      try {
        this.mediaStream.getTracks().forEach(t => t.stop());
      } catch {}
      this.mediaStream = null;
    }
    const ctx = this.audioContext;
    this.audioContext = null;
    if (ctx) {
      try { ctx.suspend().catch(()=>{}); } catch {}
      try { ctx.close().catch(()=>{}); } catch {}
    }
    this.holdStart = null;
    this.belowSince = null;
    this.armed = true;
    useStore.getState().setMicTriggerEnabled(false);
    logger.info('[MicTrigger] disabled', LogCategory.AUDIO);
  }

  private startLoop() {
    const loop = () => {
      if (!this.analyser || !this.dataArray) { return; }
      this.analyser.getByteTimeDomainData(this.dataArray);
      let sumSq = 0;
      for (let i = 0; i < this.dataArray.length; i++) {
        const norm = (this.dataArray[i] / 128.0) - 1.0;
        sumSq += norm * norm;
      }
      const rms = Math.sqrt(sumSq / this.dataArray.length);
      useStore.getState().setMicCurrentRms(rms);

      const { thresholdRms, minHoldMs, cooldownMs } = this.getState();
      const now = performance.now();

      // Re-arming: ensure signal dropped below threshold*0.7 for 300ms
      if (!this.armed) {
        if (rms < thresholdRms * 0.7) {
          if (this.belowSince === null) this.belowSince = now;
          if (now - (this.belowSince || 0) >= 300 && (now - this.lastTriggerAt) >= cooldownMs) {
            this.armed = true;
            this.belowSince = null;
          }
        } else {
          this.belowSince = null;
        }
      }

      // Hold detection
      if (rms >= thresholdRms) {
        if (this.holdStart === null) this.holdStart = now;
        const holdMs = now - (this.holdStart || now);
        if (this.armed && holdMs >= minHoldMs && (now - this.lastTriggerAt) >= cooldownMs) {
          this.trigger();
          this.armed = false;
          this.lastTriggerAt = now;
          this.holdStart = null;
        }
      } else {
        this.holdStart = null;
      }

      this.rafId = requestAnimationFrame(loop);
    };
    this.rafId = requestAnimationFrame(loop);
  }

  private async trigger() {
    try {
      useStore.getState().setMicLastTriggeredAt(Date.now());
      await fetch(`${API_BASE_URL}/api/scripts/execute/random-yoga`, { method: 'POST' });
      logger.info('[MicTrigger] POST /api/scripts/execute/random-yoga', LogCategory.AUDIO);
    } catch (err) {
      logger.error('[MicTrigger] trigger failed', LogCategory.AUDIO, err);
      useStore.getState().setMicError('Trigger request failed');
    }
  }
}

export default MicTriggerService;
export function useMicTriggerService() {
  return MicTriggerService.getInstance();
}
