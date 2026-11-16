'use client';

import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { findCommentSection, listCommentSections, MAX_REVIEW_COMMENT_CHARS } from '@/lib/knowledge-comment-review.mjs';
import type { KnowledgeReviewComment, KnowledgeReviewCommentInput } from '@/lib/knowledge-workbench.mjs';
import { KnowledgeCommentResearch } from './KnowledgeCommentResearch';

type Props = {
  body: string;
  title: string;
  modelWords: readonly string[];
  comments: readonly KnowledgeReviewComment[];
  bodyRevision: number;
  focusRequest?: { sectionId: string; request: number } | null;
  busy: boolean;
  onAdd: (input: KnowledgeReviewCommentInput) => boolean;
  onApply: (id: string, expectedBody: string, body: string) => boolean;
};

export function KnowledgeReviewComments({ body, title, modelWords, comments, bodyRevision, focusRequest, busy, onAdd, onApply }: Props) {
  const labelId = useId();
  const containerRef = useRef<HTMLElement>(null);
  const commentInputRef = useRef<HTMLTextAreaElement>(null);
  const lastFocusedRequest = useRef<number | null>(null);
  const sections = useMemo(() => listCommentSections(body), [body]);
  const ambiguousLabels = useMemo(() => {
    const seen = new Set<string>();
    return new Set(sections.flatMap(({ label }) => {
      if (seen.has(label)) return [label];
      seen.add(label);
      return [];
    }));
  }, [sections]);
  const [sectionId, setSectionId] = useState('');
  const [text, setText] = useState('');
  const [activeId, setActiveId] = useState('');
  const [notice, setNotice] = useState('');
  const selected = sections.find((section) => section.id === sectionId && !ambiguousLabels.has(section.label));
  const active = comments.find((comment) => comment.id === activeId && comment.status === 'open');
  const target = active && findCommentSection(body, active.sectionId, active.sectionLabel);

  useEffect(() => {
    if (!focusRequest || lastFocusedRequest.current === focusRequest.request) return;
    const section = sections.find((candidate) => candidate.id === focusRequest.sectionId
      && !ambiguousLabels.has(candidate.label));
    if (!section) return;
    lastFocusedRequest.current = focusRequest.request;
    setSectionId(section.id);
    const frame = window.requestAnimationFrame(() => {
      containerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      commentInputRef.current?.focus({ preventScroll: true });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [focusRequest, sections, ambiguousLabels]);

  return (
    <section ref={containerRef} aria-label="コメントから追記案を作る" className="min-w-0 scroll-mt-24 space-y-4 rounded-xl border border-blue-200 bg-white p-4 shadow-sm sm:p-5">
      <header>
        <h2 className="text-lg font-bold text-gray-950">コメントから追記案を作る</h2>
        <p className="mt-1 text-sm text-gray-700">足りない内容を書き、該当する節を指定してください。機種や適用条件が分かる場合は、コメントに含めてください。</p>
      </header>
      <form className="space-y-3" onSubmit={(event) => {
        event.preventDefault();
        if (!selected || !text.trim() || busy) return;
        const id = crypto.randomUUID();
        if (!onAdd({ id, sectionId: selected.id, text })) {
          setNotice('コメントを追加できませんでした。対象の節とコメントを確認してください。');
          return;
        }
        setNotice('');
        setActiveId(id);
        setText('');
      }}>
        <div>
          <label htmlFor={`${labelId}-section`} className="block text-sm font-medium text-gray-900">追記する節</label>
          <select id={`${labelId}-section`} value={selected?.id ?? ''} onChange={(event) => setSectionId(event.target.value)}
            className="mt-1 w-full max-w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm">
            <option value="">節を選ぶ</option>
            {sections.map((section) => (
              <option key={section.id} value={section.id} disabled={ambiguousLabels.has(section.label)}>
                {section.label}（本文 {section.line}行目）
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor={`${labelId}-comment`} className="block text-sm font-medium text-gray-900">足りない内容のコメント</label>
          <textarea ref={commentInputRef} id={`${labelId}-comment`} data-testid="review-comment-input" value={text} onChange={(event) => setText(event.target.value)} rows={3}
            maxLength={MAX_REVIEW_COMMENT_CHARS} placeholder="例: AXIEZの点検でこの手順が当てはまる条件を確認したい。"
            className="mt-1 block w-full resize-y rounded-lg border border-gray-300 px-3 py-2 text-sm" />
        </div>
        <Button type="submit" size="sm" variant="outline" disabled={!selected || !text.trim() || busy}>コメントを追加</Button>
        {notice && <p role="alert" className="text-sm text-red-800">{notice}</p>}
      </form>
      {comments.length > 0 && (
        <ul aria-label="カードのコメント" className="space-y-2">
          {comments.map((comment) => (
            <li key={comment.id} className="min-w-0 space-y-1 rounded-lg border border-gray-200 p-3">
              <p className="break-words text-xs font-semibold text-gray-700">{comment.sectionLabel} · {comment.status === 'applied' ? '下書きに反映済み' : '未反映'}</p>
              <p className="whitespace-pre-wrap break-words text-sm text-gray-950">{comment.text}</p>
              {comment.status === 'open' && comment.id !== activeId && (
                <Button type="button" size="sm" variant="ghost" onClick={() => setActiveId(comment.id)}>このコメントを調べる</Button>
              )}
            </li>
          ))}
        </ul>
      )}
      {active && target && (
        <KnowledgeCommentResearch key={`${active.id}-${bodyRevision}`}
          body={body} title={title} modelWords={modelWords} comment={active} busy={busy} onApply={onApply} />
      )}
      {active && !target && <p role="status" className="text-sm text-amber-900">指定した節を特定できません。現在の節を選んでコメントを追加してください。</p>}
    </section>
  );
}
