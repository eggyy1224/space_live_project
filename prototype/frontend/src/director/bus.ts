export type EventMap = Record<string, any>;

type Listener<T> = (payload: T) => void;

export class TypedEventBus<Events extends EventMap> {
  private listeners: { [K in keyof Events]?: Listener<Events[K]>[] } = {};

  on<K extends keyof Events>(event: K, listener: Listener<Events[K]>): void {
    (this.listeners[event] ||= []).push(listener);
  }

  off<K extends keyof Events>(event: K, listener: Listener<Events[K]>): void {
    const arr = this.listeners[event];
    if (arr) this.listeners[event] = arr.filter((l) => l !== listener);
  }

  emit<K extends keyof Events>(event: K, payload: Events[K]): void {
    (this.listeners[event] || []).forEach((l) => l(payload));
  }
}

import { DirectorState } from '../../../shared/director/types';

export interface DirectorEventMap {
  stateUpdate: Partial<DirectorState>;
}

export const directorBus = new TypedEventBus<DirectorEventMap>();
