import { useSyncExternalStore } from "react";

const activeFallbacks = new Set<string>();
const listeners = new Set<() => void>();

export const demoStore = {
  getSnapshot: () => activeFallbacks.size > 0,
  subscribe: (listener: () => void) => {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  },
  setFallback: (id: string, isFallback: boolean) => {
    const wasDemo = activeFallbacks.size > 0;

    if (isFallback) {
      activeFallbacks.add(id);
    } else {
      activeFallbacks.delete(id);
    }

    // Only notify listeners if the overall demo state changed
    if (wasDemo !== activeFallbacks.size > 0) {
      listeners.forEach((l) => l());
    }
  },
};

export function useDemoMode() {
  return useSyncExternalStore(demoStore.subscribe, demoStore.getSnapshot);
}
