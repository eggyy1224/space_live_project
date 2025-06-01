import {
  BgmFile,
  EffectFile,
  VideoFile,
  LightingPreset,
  CameraPresetName,
} from '../../frontend/src/config/resources';

export interface VideoScreenState {
  id: string;
  currentVideo: VideoFile | null;
  visible: boolean;
  playing: boolean;
  volume: number;
  currentTime: number;
  duration: number;
  playbackRate: number;
}

export interface DirectorState {
  bgm: BgmFile | null;
  bgmPlaying: boolean;
  bgmTime: number;
  bgmVolume: number;
  effectVolume: number;
  lightingPreset: LightingPreset | null;
  cameraPreset: CameraPresetName | null;
  randomMode: boolean;
  videoScreens: VideoScreenState[];
}

export interface DirectorStateMessage {
  type: 'director-state';
  payload: Partial<DirectorState>;
}
