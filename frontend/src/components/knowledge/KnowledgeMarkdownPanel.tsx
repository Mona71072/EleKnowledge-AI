'use client';

import { useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type Props = {
  title: string;
  originalBody: string;
  body: string;
  onChange: (value: string) => void;
};

function safeExternalHref(href: string | undefined): string | null {
  if (!href) return null;
  try {
    const parsed = new URL(href);
    return parsed.protocol === 'https:' ? parsed.href : null;
  } catch {
    return null;
  }
}

function renderLineDiff(before: string, after: string): Array<{ kind: 'same' | 'removed' | 'added'; text: string }> {
  const left = before.split('\n');
  const right = after.split('\n');
  const rows: Array<{ kind: 'same' | 'removed' | 'added'; text: string }> = [];
  const max = Math.max(left.length, right.length);
  for (let i = 0; i < max; i += 1) {
    if (left[i] === right[i]) {
      if (left[i] !== undefined) rows.push({ kind: 'same', text: left[i] });
      continue;
    }
    if (left[i] !== undefined) rows.push({ kind: 'removed', text: left[i] });
    if (right[i] !== undefined) rows.push({ kind: 'added', text: right[i] });
  }
  return rows;
}

export function KnowledgeMarkdownPanel({ title, originalBody, body, onChange }: Props) {
  const [view, setView] = useState<'edit' | 'compare' | 'preview'>('edit');
  const diff = useMemo(() => renderLineDiff(originalBody, body), [originalBody, body]);
  const changed = originalBody !== body;

  return (
    <section className="min-w-0 rounded-xl border border-gray-200 bg-white shadow-sm" aria-label="Markdown本文">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 px-4 py-3">
        <div>
          <h2 className="font-semibold text-gray-900">Markdown本文</h2>
          <p className="text-xs text-gray-500">修正候補は元ファイルへ直接保存されません</p>
        </div>
        <div className="flex gap-1 rounded-lg bg-gray-100 p-1" role="tablist" aria-label="本文の表示方法">
          {([
            ['edit', '編集'],
            ['compare', '差分'],
            ['preview', 'プレビュー'],
          ] as const).map(([key, label]) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={view === key}
              onClick={() => setView(key)}
              className={`rounded-md px-3 py-1.5 text-sm ${view === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 py-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <h3 className="min-w-0 truncate text-sm font-medium text-gray-800">{title}</h3>
          <span className={`shrink-0 rounded-full px-2 py-1 text-xs ${changed ? 'bg-amber-100 text-amber-900' : 'bg-gray-100 text-gray-600'}`}>
            {changed ? '変更あり' : '原文と同じ'}
          </span>
        </div>

        {view === 'edit' && (
          <label className="block">
            <span className="sr-only">Markdown本文を編集</span>
            <textarea
              aria-label="Markdown本文を編集"
              value={body}
              onChange={(event) => onChange(event.target.value)}
              rows={22}
              className="w-full resize-y rounded-lg border border-gray-300 bg-white p-3 font-mono text-sm leading-6 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              spellCheck={false}
            />
          </label>
        )}

        {view === 'compare' && (
          <div aria-label="原文と修正案の差分" className="max-h-[34rem] overflow-auto rounded-lg border border-gray-200 bg-gray-50 p-3 font-mono text-xs leading-6">
            {!changed && <p className="text-gray-600">原文からの変更はありません。</p>}
            {changed && diff.map((row, index) => (
              <div key={`${index}-${row.kind}`} className={row.kind === 'removed' ? 'bg-red-50 text-red-900' : row.kind === 'added' ? 'bg-green-50 text-green-900' : 'text-gray-700'}>
                <span aria-hidden className="inline-block w-5 select-none text-gray-400">{row.kind === 'removed' ? '−' : row.kind === 'added' ? '+' : ' '}</span>
                <span className="whitespace-pre-wrap break-words">{row.text || ' '}</span>
              </div>
            ))}
          </div>
        )}

        {view === 'preview' && (
          <article className="prose prose-sm max-w-none overflow-auto rounded-lg border border-gray-200 p-4 text-gray-800">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              skipHtml
              components={{
                a: ({ href, children }) => {
                  const safeHref = safeExternalHref(href);
                  return safeHref ? (
                    <a href={safeHref} target="_blank" rel="noopener noreferrer">{children}</a>
                  ) : (
                    <span className="rounded bg-amber-50 px-1 text-amber-900">参照リンク（URL未確認）: {children}</span>
                  );
                },
                img: ({ alt }) => <span className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600">画像参照: {alt || '説明なし'}（自動読込なし）</span>,
              }}
            >
              {body}
            </ReactMarkdown>
          </article>
        )}
      </div>
    </section>
  );
}
