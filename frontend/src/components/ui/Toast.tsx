'use client';

import { useEffect } from 'react';
import { cn } from '@/lib/utils';

export interface ToastProps {
  message: string;
  variant?: 'success' | 'error' | 'info';
  onDismiss: () => void;
  /** 自動で消えるまでの ms（0 で無効） */
  durationMs?: number;
}

const VARIANT_STYLES = {
  success: 'bg-green-900/90 text-green-50 border-green-700/50',
  error: 'bg-red-900/90 text-red-50 border-red-700/50',
  info: 'bg-gray-900/90 text-gray-50 border-gray-700/50',
};

export function Toast({
  message,
  variant = 'info',
  onDismiss,
  durationMs = 3200,
}: ToastProps) {
  useEffect(() => {
    if (durationMs <= 0) return;
    const t = window.setTimeout(onDismiss, durationMs);
    return () => window.clearTimeout(t);
  }, [durationMs, onDismiss, message]);

  return (
    <div
      className="fixed bottom-24 sm:bottom-28 left-1/2 z-50 -translate-x-1/2 px-4 w-full max-w-md pointer-events-none"
      role="status"
      aria-live="polite"
    >
      <div
        className={cn(
          'pointer-events-auto rounded-lg border px-4 py-2.5 text-sm shadow-lg backdrop-blur-sm flex items-start gap-2 animate-fade-in',
          VARIANT_STYLES[variant],
        )}
      >
        <p className="flex-1 leading-snug">{message}</p>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 opacity-70 hover:opacity-100 text-xs underline underline-offset-2"
          aria-label="閉じる"
        >
          閉じる
        </button>
      </div>
    </div>
  );
}
