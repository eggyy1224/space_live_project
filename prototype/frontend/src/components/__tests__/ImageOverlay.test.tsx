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
    handlers['generated-image']?.({ type: 'generated-image', url: '/test.png', duration: 1 });
  });

  expect(screen.getByAltText('Generated')).toBeInTheDocument();

  act(() => {
    jest.advanceTimersByTime(1000);
  });

  expect(screen.queryByAltText('Generated')).toBeNull();
});

test('supports multiple images with independent durations', () => {
  const handlers: Record<string, (d: any) => void> = {};
  (WebSocketService.getInstance as jest.Mock).mockReturnValue({
    registerHandler: (type: string, h: any) => {
      handlers[type] = h;
    },
    removeHandler: () => {},
  });

  render(<ImageOverlay />);

  act(() => {
    handlers['generated-image']?.({ type: 'generated-image', url: '/one.png', duration: 1 });
    handlers['generated-image']?.({ type: 'generated-image', url: '/two.png', duration: 2 });
  });

  expect(screen.getAllByAltText('Generated')).toHaveLength(2);

  act(() => {
    jest.advanceTimersByTime(1000);
  });

  expect(screen.getAllByAltText('Generated')).toHaveLength(1);

  act(() => {
    jest.advanceTimersByTime(1000);
  });

  expect(screen.queryByAltText('Generated')).toBeNull();
});
