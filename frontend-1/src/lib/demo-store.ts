import { useSyncExternalStore } from 'react';

let isDemoMode = false;
const listeners = new Set<() => void>();

export const demoStore = {
  getSnapshot: () => isDemoMode,
  subscribe: (listener: () => void) => {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
  setDemoMode: (value: boolean) => {
    if (isDemoMode !== value) {
      isDemoMode = value;
      listeners.forEach((l) => l());
    }
  }
};

export function useDemoMode() {
  return useSyncExternalStore(demoStore.subscribe, demoStore.getSnapshot);
}
