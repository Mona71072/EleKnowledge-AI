'use client';

import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import { PRODUCT_WISH_TEXT_MAX } from '@/lib/chat-failures';

export interface ProductWishModalProps {
  open: boolean;
  text: string;
  submitting: boolean;
  sent: boolean;
  error?: string | null;
  onTextChange: (value: string) => void;
  onSubmit: () => void;
  onClose: () => void;
}

export function ProductWishModal({
  open,
  text,
  submitting,
  sent,
  error,
  onTextChange,
  onSubmit,
  onClose,
}: ProductWishModalProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, onClose]);

  useEffect(() => {
    if (open) {
      const t = window.setTimeout(() => textareaRef.current?.focus(), 50);
      return () => window.clearTimeout(t);
    }
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="product-wish-title"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/40" />
      <div
        className="relative w-full sm:max-w-lg bg-white rounded-t-2xl sm:rounded-xl shadow-xl border border-violet-100 p-5 sm:p-6 max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <h2 id="product-wish-title" className="text-lg font-bold text-gray-900">
              こうなってほしい
            </h2>
            <p className="text-sm text-gray-600 mt-1 leading-relaxed">
              使い方や表示について、改善のヒントを自由に書いてください。
              👎 評価とは別に届き、運用チームが確認します。
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700"
            aria-label="閉じる"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => onTextChange(e.target.value.slice(0, PRODUCT_WISH_TEXT_MAX))}
          maxLength={PRODUCT_WISH_TEXT_MAX}
          rows={4}
          placeholder="例: 候補資料をもっと上に出してほしい / 機種を選ばなくても検索してほしい"
          className="w-full text-sm border border-violet-200 rounded-lg px-3 py-2.5 bg-white text-gray-900 placeholder:text-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-violet-400"
        />

        <div className="flex flex-wrap items-center justify-between gap-2 mt-3">
          <span className="text-[11px] text-gray-500">
            {text.length}/{PRODUCT_WISH_TEXT_MAX}
          </span>
          <div className="flex items-center gap-2">
            {sent && (
              <span className="text-xs text-green-700 font-medium">送信しました。ありがとうございます</span>
            )}
            {error && (
              <span className="text-xs text-red-700">{error}</span>
            )}
            <Button variant="secondary" type="button" onClick={onClose}>
              閉じる
            </Button>
            <Button
              type="button"
              onClick={onSubmit}
              disabled={submitting || !text.trim()}
              className="bg-violet-700 hover:bg-violet-800 text-white border-violet-700"
            >
              {submitting ? '送信中…' : '送信'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
