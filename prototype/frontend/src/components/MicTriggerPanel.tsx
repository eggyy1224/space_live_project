import React, { useEffect } from 'react';
import { useStore } from '../store';
import MicTriggerService from '../services/MicTriggerService';

interface MicTriggerPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

export const MicTriggerPanel: React.FC<MicTriggerPanelProps> = ({ isVisible, onClose }) => {
  const enabled = useStore(s => s.micTriggerEnabled);
  const threshold = useStore(s => s.micThresholdRms);
  const minHold = useStore(s => s.micMinHoldMs);
  const cooldown = useStore(s => s.micCooldownMs);
  const rms = useStore(s => s.micCurrentRms);
  const lastTrig = useStore(s => s.micLastTriggeredAt);
  const error = useStore(s => s.micError);

  const setEnabled = useStore(s => s.setMicTriggerEnabled);
  const setThreshold = useStore(s => s.setMicThresholdRms);
  const setMinHold = useStore(s => s.setMicMinHoldMs);
  const setCooldown = useStore(s => s.setMicCooldownMs);

  // 僅手動控制，不使用排程
  const enableManual = useStore(s => s.enableManualMicMode);

  useEffect(() => {
    if (!isVisible) return;
    return () => { /* panel close cleanup if needed */ };
  }, [isVisible]);

  if (!isVisible) return null;

  const fmt = (t: number | null) => t ? new Date(t).toLocaleTimeString() : '—';

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Mic Trigger（語音觸發隨機瑜伽）</h3>
        <button className="text-sm px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded" onClick={onClose}>關閉</button>
      </div>

      <div className="flex items-center space-x-3">
        <button
          className={`px-4 py-2 rounded ${enabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'} text-white`}
          onClick={async () => {
            enableManual();
            if (!enabled) { await MicTriggerService.getInstance().enable(); } else { MicTriggerService.getInstance().disable(); }
          }}
        >{enabled ? '停止監聽' : '開始監聽'}</button>
        <div className="text-sm text-gray-300">當前 RMS: {(rms).toFixed(3)}，上次觸發: {fmt(lastTrig)}</div>
      </div>

      {error && <div className="text-red-400 text-sm">{error}</div>}

      <div className="grid grid-cols-3 gap-4 text-sm text-gray-200">
        <div>
          <label className="block mb-1">閾值 Threshold (RMS)</label>
          <input type="range" min={0.005} max={0.2} step={0.001} value={threshold}
            onChange={e => setThreshold(parseFloat(e.target.value))} className="w-full"/>
          <div className="mt-1">{threshold.toFixed(3)}</div>
        </div>
        <div>
          <label className="block mb-1">最短持續毫秒 MinHold</label>
          <input type="number" min={50} max={5000} value={minHold}
            onChange={e => setMinHold(parseInt(e.target.value)||250)} className="w-full bg-gray-700 p-1 rounded"/>
        </div>
        <div>
          <label className="block mb-1">冷卻毫秒 Cooldown</label>
          <input type="number" min={500} max={60000} value={cooldown}
            onChange={e => setCooldown(parseInt(e.target.value)||cooldown)} className="w-full bg-gray-700 p-1 rounded"/>
        </div>
      </div>

      {/* 排程功能移除，僅保留手動開始/停止監聽 */}
    </div>
  );
};

export default MicTriggerPanel;
