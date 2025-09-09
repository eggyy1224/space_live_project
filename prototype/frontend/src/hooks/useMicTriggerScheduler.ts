import { useEffect, useRef } from 'react';
import { useStore } from '../store';
import MicTriggerService from '../services/MicTriggerService';

export function useMicTriggerScheduler() {
  const timerRef = useRef<number | null>(null);
  const scheduleEnabled = useStore(s => s.micScheduleEnabled);
  const isManual = useStore(s => s.micIsManualMode);
  const countdown = useStore(s => s.micCurrentCountdown);
  const nextAction = useStore(s => s.micNextAction);
  const enabled = useStore(s => s.micTriggerEnabled);
  const setEnabled = useStore(s => s.setMicTriggerEnabled);
  const _update = useStore(s => s._micUpdateCountdown);

  useEffect(() => {
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    if (!scheduleEnabled || isManual) return;
    timerRef.current = setInterval(() => _update(), 1000);
    return () => { if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; } };
  }, [scheduleEnabled, isManual, _update]);

  useEffect(() => {
    if (!scheduleEnabled || isManual) return;
    if (countdown === 0) {
      if (nextAction === 'enable') {
        MicTriggerService.getInstance().enable();
        setEnabled(true);
      } else {
        MicTriggerService.getInstance().disable();
        setEnabled(false);
      }
    }
  }, [countdown, nextAction, scheduleEnabled, isManual, setEnabled]);

  // sync service with enabled flag (manual toggling)
  useEffect(() => {
    if (isManual) {
      if (enabled) MicTriggerService.getInstance().enable(); else MicTriggerService.getInstance().disable();
    }
  }, [enabled, isManual]);
}

