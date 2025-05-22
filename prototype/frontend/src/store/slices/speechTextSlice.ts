import { StateCreator } from 'zustand';

export interface SpeechTextSlice {
  speechText: string;
  setSpeechText: (text: string) => void;
}

export const createSpeechTextSlice: StateCreator<SpeechTextSlice> = (set) => ({
  speechText: '',
  setSpeechText: (text) => set({ speechText: text }),
});
