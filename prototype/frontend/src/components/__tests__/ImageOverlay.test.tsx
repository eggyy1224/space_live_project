import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import ImageOverlay from '../ImageOverlay';
import WebSocketService from '../../services/WebSocketService';

jest.useFakeTimers();

jest.mock('../../services/WebSocketService');

test('displays image on message and hides after timeout', () => {
  const handlers: Record<string, (d: any) => void> = {};
  (WebSocketService.getInstance as jest.Mock).mockReturnValue({
    registerHandler: (type: string, h: any) => {
      handlers[type] = h;
    },
    removeHandler: () => {},
  });

  render(<ImageOverlay />);

  act(() => {
    handlers['generated-image']?.({ type: 'generated-image', url: '/test.png' });
  });

  expect(screen.getByAltText('Generated')).toBeInTheDocument();

  act(() => {
    jest.advanceTimersByTime(10000);
  });

  expect(screen.queryByAltText('Generated')).toBeNull();
});
