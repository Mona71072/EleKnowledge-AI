'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export interface ChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
  children: React.ReactNode;
}

/**
 * トグル可能なフィルタチップ。選択=塗り (blue)、未選択=アウトライン。
 * 複数選択フィルタ (資料カテゴリ) の各選択肢に使う。
 */
export const Chip = React.forwardRef<HTMLButtonElement, ChipProps>(
  ({ active = false, disabled, className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        type="button"
        role="checkbox"
        aria-checked={active}
        disabled={disabled}
        className={cn(
          'inline-flex items-center gap-1 whitespace-nowrap rounded-full border px-3 py-1 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 disabled:opacity-40 disabled:cursor-not-allowed',
          active
            ? 'border-blue-600 bg-blue-600 text-white hover:bg-blue-700'
            : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50',
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Chip.displayName = 'Chip';
