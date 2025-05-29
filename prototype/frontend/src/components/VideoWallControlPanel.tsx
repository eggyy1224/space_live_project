import React from 'react';
import { useStore } from '../store';
import { DIRECTOR_VIDEOS } from '../config/resources';

const panelStyle =
  'fixed top-2 left-2 bg-black/70 text-white text-xs p-2 rounded shadow z-50';

const VideoWallControlPanel: React.FC = () => {
  const screens = useStore((s) => s.videoScreens);
  const setVideoScreen = useStore((s) => s.setVideoScreen);

  if (import.meta.env.VITE_DIRECTOR !== 'true') return null;

  return (
    <div className={panelStyle}>
      {screens.map((screen) => (
        <div
          key={screen.id}
          className="mb-2 last:mb-0 border-b last:border-b-0 border-white/20 pb-1"
        >
          <div className="font-bold mb-1">{screen.id}</div>
          <select
            value={screen.currentVideo}
            onChange={(e) =>
              setVideoScreen(screen.id, { currentVideo: e.target.value })
            }
            className="bg-gray-800 text-white text-xs rounded w-full mb-1"
          >
            <option value="" disabled>
              選擇影片
            </option>
            {DIRECTOR_VIDEOS.map((v) => (
              <option key={v} value={v}>
                {v.split('/').pop()?.replace('.mp4', '')}
              </option>
            ))}
          </select>
          <label className="flex items-center space-x-1">
            <input
              type="checkbox"
              checked={screen.visible}
              onChange={(e) =>
                setVideoScreen(screen.id, { visible: e.target.checked })
              }
            />
            <span>顯示</span>
          </label>
          <div className="mt-1 text-[10px]">
            {screen.visible ? screen.currentVideo.split('/').pop() : 'hidden'}
          </div>
        </div>
      ))}
    </div>
  );
};

export default VideoWallControlPanel;
