import React from 'react';
import SpeechBackground from './SpeechBackground';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';

const DynamicAudioBackgrounds: React.FC = () => (
  <>
    <SpeechBackground />
    <MusicBackground />
    <EffectBackground />
  </>
);

export default DynamicAudioBackgrounds;
