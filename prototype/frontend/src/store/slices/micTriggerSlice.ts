import { StateCreator } from 'zustand';

export interface MicTriggerSlice {
  // realtime mic trigger
  micTriggerEnabled: boolean;
  micThresholdRms: number; // 0..1
  micMinHoldMs: number;    // ms
  micCooldownMs: number;   // ms
  micCurrentRms: number;
  micLastTriggeredAt: number | null;
  micError: string | null;

  setMicTriggerEnabled: (v: boolean) => void;
  setMicThresholdRms: (v: number) => void;
  setMicMinHoldMs: (v: number) => void;
  setMicCooldownMs: (v: number) => void;
  setMicCurrentRms: (v: number) => void;
  setMicLastTriggeredAt: (t: number | null) => void;
  setMicError: (msg: string | null) => void;

  // schedule
  micScheduleEnabled: boolean;
  micIsManualMode: boolean;
  micOnlineDurationSeconds: number;
  micOfflineDurationSeconds: number;
  micCurrentCountdown: number;
  micNextAction: 'enable' | 'disable';
  micCurrentlyActive: boolean; // mirror of micTriggerEnabled but for schedule logic

  setMicScheduleEnabled: (v: boolean) => void;
  setMicOnlineDuration: (sec: number) => void;
  setMicOfflineDuration: (sec: number) => void;
  startMicSchedule: () => void;
  pauseMicSchedule: () => void;
  resetMicSchedule: () => void;
  enableManualMicMode: () => void;
  disableManualMicMode: () => void;
  setMicCurrentlyActive: (v: boolean) => void;

  _micUpdateCountdown: () => void;
  _micExecuteNextAction: () => Promise<void>;
  _micResetToNextCycle: () => void;
}

export const createMicTriggerSlice: StateCreator<MicTriggerSlice> = (set, get) => ({
  micTriggerEnabled: false,
  micThresholdRms: 0.03,
  micMinHoldMs: 250,
  micCooldownMs: 20000,
  micCurrentRms: 0,
  micLastTriggeredAt: null,
  micError: null,

  setMicTriggerEnabled: (v) => set({ micTriggerEnabled: v, micCurrentlyActive: v }),
  setMicThresholdRms: (v) => set({ micThresholdRms: Math.max(0.001, Math.min(0.5, v)) }),
  setMicMinHoldMs: (v) => set({ micMinHoldMs: Math.max(50, Math.min(5000, v)) }),
  setMicCooldownMs: (v) => set({ micCooldownMs: Math.max(500, Math.min(60000, v)) }),
  setMicCurrentRms: (v) => set({ micCurrentRms: v }),
  setMicLastTriggeredAt: (t) => set({ micLastTriggeredAt: t }),
  setMicError: (msg) => set({ micError: msg }),

  micScheduleEnabled: false,
  micIsManualMode: false,
  micOnlineDurationSeconds: 30,
  micOfflineDurationSeconds: 30,
  micCurrentCountdown: 30,
  micNextAction: 'disable',
  micCurrentlyActive: false,

  setMicScheduleEnabled: (v) => set({ micScheduleEnabled: v }),
  setMicOnlineDuration: (sec) => set({ micOnlineDurationSeconds: sec }),
  setMicOfflineDuration: (sec) => set({ micOfflineDurationSeconds: sec }),
  setMicCurrentlyActive: (v) => set({ micCurrentlyActive: v }),

  startMicSchedule: () => {
    const s = get();
    set({
      micScheduleEnabled: true,
      micIsManualMode: false,
      micNextAction: s.micCurrentlyActive ? 'disable' : 'enable',
      micCurrentCountdown: s.micCurrentlyActive ? s.micOnlineDurationSeconds : s.micOfflineDurationSeconds,
    });
  },
  pauseMicSchedule: () => set({ micScheduleEnabled: false }),
  resetMicSchedule: () => {
    const s = get();
    set({
      micCurrentCountdown: s.micCurrentlyActive ? s.micOnlineDurationSeconds : s.micOfflineDurationSeconds,
      micNextAction: s.micCurrentlyActive ? 'disable' : 'enable',
      micIsManualMode: false,
    });
  },
  enableManualMicMode: () => set({ micIsManualMode: true, micScheduleEnabled: false }),
  disableManualMicMode: () => { set({ micIsManualMode: false }); get().resetMicSchedule(); },

  _micUpdateCountdown: () => {
    const s = get();
    if (!s.micScheduleEnabled || s.micIsManualMode) return;
    const newCountdown = Math.max(0, s.micCurrentCountdown - 1);
    set({ micCurrentCountdown: newCountdown });
    if (newCountdown === 0) {
      get()._micExecuteNextAction();
    }
  },

  _micExecuteNextAction: async () => {
    const s = get();
    const action = s.micNextAction; // 'enable' | 'disable'
    try {
      if (action === 'enable') {
        // 僅更新狀態，實際啟停由 Panel / Hook 調 MicTriggerService
        set({ micTriggerEnabled: true, micCurrentlyActive: true });
      } else {
        set({ micTriggerEnabled: false, micCurrentlyActive: false });
      }
      get()._micResetToNextCycle();
    } catch (e) {
      // no-op
    }
  },

  _micResetToNextCycle: () => {
    const s = get();
    const newActive = s.micNextAction === 'enable';
    set({
      micCurrentlyActive: newActive,
      micNextAction: newActive ? 'disable' : 'enable',
      micCurrentCountdown: newActive ? s.micOnlineDurationSeconds : s.micOfflineDurationSeconds,
    });
  }
});
