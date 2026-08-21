'use client';

import { useEffect, useRef } from 'react';
import {
  BAD_FEEDBACK_REASONS,
  BadFeedbackReasonId,
  FEEDBACK_COMMENT_MAX,
  FeedbackReason,
  getFeedbackReasonLabel,
} from '@/lib/chat-failures';

export interface ChatMessageFeedbackProps {
  messageId: string;
  timestamp: string;
  feedback?: 'good' | 'bad' | null;
  feedbackReason?: FeedbackReason | null;
  feedbackComment?: string | null;
  copied: boolean;
  panelOpen: boolean;
  pendingComment: string;
  busy: boolean;
  onCopy: () => void;
  onGood: () => void;
  onBad: () => void;
  onReason: (reason: BadFeedbackReasonId) => void;
  onCommentChange: (value: string) => void;
  onCommentSubmit: () => void;
  onOpenPanel: () => void;
  onClosePanel: () => void;
}

export function ChatMessageFeedback({
  messageId,
  timestamp,
  feedback,
  feedbackReason,
  feedbackComment,
  copied,
  panelOpen,
  pendingComment,
  busy,
  onCopy,
  onGood,
  onBad,
  onReason,
  onCommentChange,
  onCommentSubmit,
  onOpenPanel,
  onClosePanel,
}: ChatMessageFeedbackProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!panelOpen) return;
    // 理由チップ操作を優先するため、補足欄への自動フォーカスはしない
    panelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [panelOpen, messageId]);

  const reasonLabel = getFeedbackReasonLabel(feedbackReason);

  return (
    <>
      <div className="mt-3 pt-2 border-t border-gray-100 flex flex-wrap items-center gap-1">
        <button
          type="button"
          onClick={onCopy}
          className={`p-1.5 rounded-md transition-colors ${
            copied
              ? 'text-green-600 bg-green-50'
              : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'
          }`}
          aria-label="回答をコピー"
          title={copied ? 'コピーしました' : 'コピー'}
        >
          {copied ? (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          )}
        </button>

        <div className="inline-flex items-center rounded-lg border border-gray-200 bg-gray-50/80 p-0.5">
          <button
            type="button"
            onClick={onGood}
            disabled={busy}
            className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs transition-colors disabled:opacity-50 ${
              feedback === 'good'
                ? 'text-green-700 bg-green-100 font-medium'
                : 'text-gray-500 hover:text-green-700 hover:bg-green-50'
            }`}
            aria-label="疑問が解けた"
            title="疑問が解けた"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
            <span className="hidden sm:inline">解けた</span>
          </button>
          <button
            type="button"
            onClick={onBad}
            disabled={busy}
            className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs transition-colors disabled:opacity-50 ${
              feedback === 'bad'
                ? 'text-red-700 bg-red-100 font-medium'
                : 'text-gray-500 hover:text-red-700 hover:bg-red-50'
            }`}
            aria-label="解けなかった"
            title="解けなかった"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
            </svg>
            <span className="hidden sm:inline">解けない</span>
          </button>
        </div>

        {feedback === 'good' && (
          <span className="text-[11px] text-green-700 font-medium">記録しました</span>
        )}

        {feedback === 'bad' && reasonLabel && !panelOpen && (
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-red-50 text-red-800 border border-red-100">
            {reasonLabel}
          </span>
        )}

        <span className="ml-auto text-[11px] text-gray-400">
          {new Date(timestamp).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {feedback === 'bad' && panelOpen && (
        <div
          ref={panelRef}
          className="mt-2 rounded-lg border border-red-100 bg-red-50/60 px-3 py-2.5"
        >
          <div className="flex items-start justify-between gap-2 mb-2">
            <div>
              <p className="text-xs text-red-900 font-medium">詳しく教えてください（任意）</p>
              <p className="text-[11px] text-red-800/75 mt-0.5 leading-relaxed">
                理由を選んでも 👎 は既に記録済みです。補足があれば続けて書けます。
              </p>
            </div>
            <button
              type="button"
              onClick={onClosePanel}
              className="text-[11px] text-red-700/70 hover:text-red-900 underline underline-offset-2 shrink-0"
            >
              閉じる
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 mb-2">
            {BAD_FEEDBACK_REASONS.map((r) => (
              <button
                key={r.id}
                type="button"
                disabled={busy}
                onClick={() => onReason(r.id)}
                className={`text-left text-xs px-2.5 py-2 rounded-lg border transition-colors disabled:opacity-50 ${
                  feedbackReason === r.id
                    ? 'bg-red-600 text-white border-red-600'
                    : 'bg-white text-red-900 border-red-200 hover:border-red-400'
                }`}
              >
                <span className="font-medium block">{r.label}</span>
                {r.hint && (
                  <span className={`block text-[10px] mt-0.5 ${feedbackReason === r.id ? 'text-red-100' : 'text-red-700/70'}`}>
                    {r.hint}
                  </span>
                )}
              </button>
            ))}
          </div>

          <label htmlFor={`feedback-comment-${messageId}`} className="block text-[11px] text-red-800/90 mb-1">
            補足（任意・{FEEDBACK_COMMENT_MAX}字まで）
          </label>
          <textarea
            id={`feedback-comment-${messageId}`}
            value={pendingComment}
            onChange={(e) => onCommentChange(e.target.value.slice(0, FEEDBACK_COMMENT_MAX))}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                e.preventDefault();
                onCommentSubmit();
              }
            }}
            placeholder="例: 別の機種の資料が出てきた、手順の順番が違う など"
            rows={2}
            className="w-full text-xs rounded-md border border-red-200 bg-white px-2 py-1.5 text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-red-300"
          />
          <div className="flex items-center justify-between gap-2 mt-1.5">
            <span className="text-[10px] text-red-700/60">
              {pendingComment.length}/{FEEDBACK_COMMENT_MAX}
              <span className="hidden sm:inline text-red-700/50"> · ⌘/Ctrl+Enter で送信</span>
            </span>
            <button
              type="button"
              onClick={onCommentSubmit}
              disabled={busy || !pendingComment.trim()}
              className="text-xs px-2.5 py-1 rounded-md border border-red-300 bg-white text-red-800 hover:bg-red-50 disabled:opacity-40"
            >
              補足を送る
            </button>
          </div>
        </div>
      )}

      {feedback === 'bad' && !panelOpen && (
        <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1">
          {feedbackComment && (
            <p className="text-[11px] text-red-700/80 italic max-w-full break-words">
              補足: {feedbackComment}
            </p>
          )}
          <button
            type="button"
            onClick={onOpenPanel}
            className="text-[11px] text-red-700/70 hover:text-red-900 underline underline-offset-2"
          >
            {feedbackReason || feedbackComment ? '理由・補足を編集' : '理由・補足を追加'}
          </button>
        </div>
      )}
    </>
  );
}
