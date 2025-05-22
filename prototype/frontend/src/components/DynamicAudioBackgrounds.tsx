import React from 'react';
import SpeechBackground from './SpeechBackground';
import MusicBackground from './MusicBackground';
import EffectBackground from './EffectBackground';
import P5SpaceEffect from './P5SpaceEffect';

const DynamicAudioBackgrounds: React.FC = () => (
  <>
    <SpeechBackground />
    <MusicBackground />
    <EffectBackground />
    <P5SpaceEffect />
  </>
);

export default DynamicAudioBackgrounds;
