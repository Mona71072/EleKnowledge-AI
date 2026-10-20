'use client';

import { useEffect, useRef } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import { ALL_MODEL_TYPES } from '@/data/kbModelTypes';
import { shouldRestoreComposerFocus } from '@/lib/knowledge-senpai-dom.mjs';
import { SendIcon, StopIcon } from './SenpaiIcons';

const MAX_ROWS = 6;
const CHARS_PER_LINE = 40;

/** 入力の行数（1〜6行）。内容に合わせて入力欄を広げるための目安。 */
function rowsFor(value: string) {
  const lines = value.split('\n').reduce((count, line) => count + Math.max(1, Math.ceil(line.length / CHARS_PER_LINE)), 0);
  return Math.min(MAX_ROWS, Math.max(1, lines));
}

/**
 * 画面下の入力欄。Enter で送信、Shift+Enter で改行（変換中の Enter は送信しない）。
 * 機種の選択は入力欄の左下、送信／中止は右下に置く。
 */
export function SenpaiComposer({ question, onQuestionChange, modelType, onModelChange, disabled, running, sendError, disclaimer, placeholder, maxLength = 2000, hint, warning, onSubmit, onCancel }: {
  question: string;
  onQuestionChange: (value: string) => void;
  modelType: string;
  onModelChange: (value: string) => void;
  /** 実行中・履歴を開いている間・続けられない相談のとき入力できない。 */
  disabled: boolean;
  running: boolean;
  sendError: string;
  disclaimer: string;
  placeholder: string;
  /** 入力できる最大文字数（聞き返しへの補足では、元の質問を残すぶん小さくなる）。 */
  maxLength?: number;
  /** 入力欄の下に出す補助（残り文字数など）。 */
  hint?: string;
  /** 入力欄の下に出す注意（元の質問が一部省略されるときなど）。 */
  warning?: string;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
}) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const wasDisabled = useRef(disabled);
  // 送信中は入力欄が無効になりフォーカスが外れるので、入力できる状態に戻ったら入力欄へ戻す。
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea && shouldRestoreComposerFocus({ wasDisabled: wasDisabled.current, disabled, activeElement: document.activeElement, body: document.body })) textarea.focus();
    wasDisabled.current = disabled;
  }, [disabled]);
  const modelLabel = ALL_MODEL_TYPES.find((model) => model.value === modelType)?.label ?? '指定なし';

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing || event.keyCode === 229) return;
    event.preventDefault();
    event.currentTarget.form?.requestSubmit();
  }

  return (
    <footer className="shrink-0 bg-white px-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2 sm:px-6">
      <form onSubmit={onSubmit} className="mx-auto max-w-3xl">
        <div className="rounded-3xl border border-gray-300 bg-white px-4 pb-2 pt-3 shadow-sm focus-within:border-gray-400">
          <label htmlFor="senpai-chat-question" className="sr-only">質問を入力</label>
          <textarea
            id="senpai-chat-question"
            ref={textareaRef}
            aria-label="質問を入力"
            value={question}
            onChange={(event) => onQuestionChange(event.target.value)}
            onKeyDown={onKeyDown}
            disabled={disabled}
            rows={rowsFor(question)}
            maxLength={maxLength}
            placeholder={placeholder}
            className="block max-h-40 w-full resize-none bg-transparent text-[15px] leading-7 text-gray-900 placeholder:text-gray-500 focus:outline-none disabled:opacity-60"
          />
          <div className="mt-1 flex items-center justify-between gap-2">
            <label className="relative inline-flex min-h-10 items-center rounded-full px-3 text-xs text-gray-600 focus-within:ring-2 focus-within:ring-violet-500 hover:bg-gray-100">
              <span aria-hidden="true">機種: {modelLabel}</span>
              <select
                aria-label="機種（任意）"
                value={modelType}
                onChange={(event) => onModelChange(event.target.value)}
                disabled={disabled}
                className="absolute inset-0 h-full w-full cursor-pointer opacity-0 disabled:cursor-not-allowed"
              >
                <option value="">指定しない</option>
                {ALL_MODEL_TYPES.map((model) => <option key={model.value} value={model.value}>{model.label}</option>)}
              </select>
            </label>
            {running ? (
              <button type="button" onClick={onCancel} aria-label="中止" title="中止" className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-900 text-white hover:bg-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"><StopIcon /></button>
            ) : (
              <button type="submit" disabled={disabled || !question.trim()} aria-label="質問を送信" title="質問を送信" className="flex h-10 w-10 items-center justify-center rounded-full bg-violet-600 text-white hover:bg-violet-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"><SendIcon /></button>
            )}
          </div>
        </div>
        {warning && <p role="note" className="mt-2 text-center text-xs text-amber-700">{warning}</p>}
        {hint && <p className="mt-1 text-center text-xs text-gray-500">{hint}</p>}
        {sendError && <p role="alert" className="mt-2 text-center text-sm text-red-700">{sendError}</p>}
        <p className="mt-2 text-center text-[11px] leading-4 text-gray-500">{disclaimer}</p>
      </form>
    </footer>
  );
}
