'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';

export interface InfoModalPayload {
  title: string;
  description: string;
  bullets?: string[];
}

/**
 * Lightweight informational modal (title + description + optional bullets).
 * Closes on Escape, overlay click, or the explicit close controls.
 */
export function InfoModal({
  payload,
  onClose,
}: {
  payload: InfoModalPayload;
  onClose: () => void;
}) {
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-4 py-6"
      role="dialog"
      aria-modal="true"
      aria-label={payload.title}
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/40" />
      <div
        className="relative w-full max-w-2xl mx-auto rounded-xl bg-white shadow-xl border border-gray-200 p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4">
          <div className="flex items-start justify-between gap-4 mb-2">
            <h3 className="text-xl font-bold text-gray-900 flex-1">{payload.title}</h3>
            <button
              type="button"
              className="flex-shrink-0 p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-colors"
              onClick={onClose}
              aria-label="閉じる"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed break-words">{payload.description}</p>
        </div>

        {payload.bullets && payload.bullets.length > 0 && (
          <ul className="mt-6 space-y-3">
            {payload.bullets.map((b) => (
              <li key={b} className="flex items-start gap-3">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm text-gray-700 leading-relaxed flex-1">{b}</span>
              </li>
            ))}
          </ul>
        )}

        <div className="mt-6 flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            閉じる
          </Button>
        </div>
      </div>
    </div>
  );
}
