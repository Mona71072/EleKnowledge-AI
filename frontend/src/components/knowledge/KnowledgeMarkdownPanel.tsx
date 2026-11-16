'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { researchSourceHref } from '@/lib/knowledge-research.mjs';
import { KnowledgeLineDiff } from './KnowledgeLineDiff';

type Props = {
  title: string;
  originalBody: string;
  body: string;
  onChange: (value: string) => void;
  onSectionSelect?: (sectionId: string) => void;
};

function safeExternalHref(href: string | undefined): string | null {
  if (!href) return null;
  try {
    if (href.startsWith('/doc?')) {
      const parsed = new URL(href, 'https://example.invalid');
      const sourceUri = parsed.searchParams.get('uri') ?? undefined;
      const pageNumber = Number(/^#page=(\d+)$/u.exec(parsed.hash)?.[1]);
      const rebuilt = researchSourceHref({ sourceUri, pageNumber }, 'normal');
      return href === rebuilt ? rebuilt : null;
    }
    const parsed = new URL(href);
    return parsed.protocol === 'https:' ? parsed.href : null;
  } catch {
    return null;
  }
}

export function KnowledgeMarkdownPanel({ title, originalBody, body, onChange, onSectionSelect }: Props) {
  const [view, setView] = useState<'edit' | 'compare' | 'preview'>('edit');
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

        {view === 'edit' && changed && (
          <div className="mt-4 space-y-2 border-t border-gray-200 pt-4">
            <h4 className="text-sm font-semibold text-gray-950">元のMarkdownからの変更箇所</h4>
            <KnowledgeLineDiff before={originalBody} after={body} onSectionSelect={onSectionSelect} />
          </div>
        )}

        {view === 'compare' && (
          <KnowledgeLineDiff before={originalBody} after={body} onSectionSelect={onSectionSelect} />
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
