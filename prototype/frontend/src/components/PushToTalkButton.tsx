import React from 'react';
import RealTimeService from '../services/RealTimeService';

const service = RealTimeService.getInstance();

const PushToTalkButton: React.FC = () => {
  const handleMouseDown = () => {
    service.startStreaming();
  };

  const handleMouseUp = () => {
    service.stopStreaming();
  };

  return (
    <button
      className="p-2 bg-blue-600 text-white rounded"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
    >
      Hold to Talk
    </button>
  );
};

export default PushToTalkButton;
