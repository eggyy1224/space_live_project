import React from 'react';
import { useStore } from '../store';
import '../styles/subtitles.css';

const SubtitlesOverlay: React.FC = () => {
  const speechText = useStore((s) => s.speechText);

  if (!speechText || speechText.trim() === '') return null;

  return (
    <div className="subtitle-container">
      <div className="subtitle-box">
        <div className="subtitle-text rainbow-neon" aria-live="polite">
          {speechText}
        </div>
      </div>
    </div>
  );
};

export default SubtitlesOverlay;

