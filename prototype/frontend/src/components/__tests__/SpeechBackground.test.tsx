import { render } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import { act } from 'react-dom/test-utils';
import SpeechBackground from '../SpeechBackground';
import { useStore } from '../../store';

test('updates speech text from store', () => {
  render(
    <Canvas>
      <SpeechBackground />
    </Canvas>
  );

  act(() => {
    useStore.getState().setSpeechText('hello');
  });

  expect(useStore.getState().speechText).toBe('hello');
});
