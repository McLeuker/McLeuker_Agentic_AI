'use client';

import { useState, useCallback } from 'react';

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

interface ToastState {
  toasts: Toast[];
}

let toastCounter = 0;
const listeners: Set<(state: ToastState) => void> = new Set();
let memoryState: ToastState = { toasts: [] };

function dispatch(action: { type: 'ADD_TOAST' | 'REMOVE_TOAST'; toast?: Toast; toastId?: string }) {
  switch (action.type) {
    case 'ADD_TOAST':
      memoryState = {
        toasts: [...memoryState.toasts, action.toast!].slice(-5),
      };
      break;
    case 'REMOVE_TOAST':
      memoryState = {
        toasts: memoryState.toasts.filter((t) => t.id !== action.toastId),
      };
      break;
  }
  
  listeners.forEach((listener) => listener(memoryState));
}

export function useToast() {
  const [state, setState] = useState<ToastState>(memoryState);

  // Subscribe to changes
  useState(() => {
    listeners.add(setState);
    return () => {
      listeners.delete(setState);
    };
  });

  const toast = useCallback(
    ({ title, description, variant = 'default' }: Omit<Toast, 'id'>) => {
      const id = `toast-${++toastCounter}`;
      const newToast: Toast = { id, title, description, variant };
      
      dispatch({ type: 'ADD_TOAST', toast: newToast });
      
      // Auto dismiss after 5 seconds
      setTimeout(() => {
        dispatch({ type: 'REMOVE_TOAST', toastId: id });
      }, 5000);
      
      return id;
    },
    []
  );

  const dismiss = useCallback((toastId: string) => {
    dispatch({ type: 'REMOVE_TOAST', toastId });
  }, []);

  return {
    toasts: state.toasts,
    toast,
    dismiss,
  };
}
