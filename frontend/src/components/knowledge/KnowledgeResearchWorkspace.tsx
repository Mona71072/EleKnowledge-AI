'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import { getIdToken } from '@/lib/auth-helpers';
import { KnowledgeComparisonPanel } from './KnowledgeComparisonPanel';
import { knowledgeResearchErrorMessage, ResearchResultLane, safeResearchHref, type LaneState } from './ResearchResultLane';
import {
  buildResearchNote,
  queryKnowledgeSource,
  type ResearchAnswer,
} from '@/lib/knowledge-research.mjs';

type Mode = 'normal' | 'law';

type Props = {
  onAdopt: (note: string, expectedContextKey: string | null) => boolean;
  canAdopt?: boolean;
  contextKey: string | null;
  targetLabel: string;
};

const EMPTY_LANES: Record<Mode, LaneState> = {
  normal: { status: 'idle' },
  law: { status: 'idle' },
};
const inputClass = 'w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200';

export function KnowledgeResearchWorkspace({ onAdopt, canAdopt = false, contextKey, targetLabel }: Props) {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [lanes, setLanes] = useState<Record<Mode, LaneState>>(EMPTY_LANES);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const sequence = useRef(0);
  const controller = useRef<AbortController | null>(null);

  useEffect(() => () => {
    sequence.current += 1;
    controller.current?.abort();
  }, []);

  const cancel = () => {
    if (!controller.current) return;
    sequence.current += 1;
    controller.current.abort();
    controller.current = null;
    setRunning(false);
    setLanes((current) => ({
      normal: current.normal.status === 'loading' ? { status: 'cancelled' } : current.normal,
      law: current.law.status === 'loading' ? { status: 'cancelled' } : current.law,
    }));
  };

  const search = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const submitted = query.trim();
    if (!submitted || submitted.length > 2000) {
      setError(submitted.length > 2000 ? '質問は2000文字以内で入力してください。' : '質問を入力してください。');
      return;
    }
    controller.current?.abort();
    const abort = new AbortController();
    controller.current = abort;
    const run = ++sequence.current;
    const searchedContextKey = contextKey;
    const searchedTargetLabel = targetLabel;
    setError('');
    setSubmittedQuery(submitted);
    setLanes({ normal: { status: 'loading' }, law: { status: 'loading' } });
    setRunning(true);

    const runLane = async (mode: Mode): Promise<LaneState> => {
      try {
        const answer = await queryKnowledgeSource({
          baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
          getToken: getIdToken,
          mode,
          query: submitted,
          signal: abort.signal,
        });
        return { status: 'success', answer, contextKey: searchedContextKey, targetLabel: searchedTargetLabel, searchId: run };
      } catch (reason) {
        if ((reason as { name?: string } | null)?.name === 'AbortError') return { status: 'cancelled' };
        return { status: 'error', message: knowledgeResearchErrorMessage(reason, mode) };
      }
    };
    const runLaneAndDisplay = async (mode: Mode): Promise<void> => {
      const result = await runLane(mode);
      if (sequence.current !== run) return;
      setLanes((current) => ({ ...current, [mode]: result }));
    };
    await Promise.all([runLaneAndDisplay('normal'), runLaneAndDisplay('law')]);
    if (sequence.current !== run) return;
    controller.current = null;
    setRunning(false);
  };

  const adopt = (answer: ResearchAnswer, expectedContextKey: string | null): boolean => {
    try {
      return onAdopt(buildResearchNote(answer), expectedContextKey);
    } catch {
      setError('調査メモを作れませんでした。回答本文と出典を確認してください。');
      return false;
    }
  };

  const technicalState = lanes.normal;
  const lawState = lanes.law;
  const comparisonReady = Boolean(
    canAdopt
      && contextKey
      && technicalState.status === 'success'
      && lawState.status === 'success'
      && technicalState.searchId === lawState.searchId
      && technicalState.contextKey === contextKey
      && lawState.contextKey === contextKey
      && technicalState.answer.mode === 'normal'
      && lawState.answer.mode === 'law'
      && technicalState.answer.responseType === 'pages'
      && lawState.answer.responseType === 'pages'
      && technicalState.answer.query === submittedQuery
      && lawState.answer.query === submittedQuery
      && technicalState.answer.query === lawState.answer.query
      && technicalState.answer.sourceDocuments.some((source) => Boolean(safeResearchHref('normal', source)))
      && lawState.answer.sourceDocuments.some((source) => Boolean(safeResearchHref('law', source))),
  );
  const comparisonKey = comparisonReady && technicalState.status === 'success' && lawState.status === 'success'
    ? JSON.stringify([
        technicalState.searchId,
        contextKey,
        technicalState.answer.query,
        technicalState.answer.sessionId,
        technicalState.answer.messageId,
        lawState.answer.sessionId,
        lawState.answer.messageId,
      ])
    : '';

  return (
    <section className="space-y-5 rounded-2xl border border-violet-200 bg-violet-50/60 p-4 sm:p-6" aria-label="技術KBと法令KBの照合">
      <header>
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-bold text-gray-950">工技先輩</h2>
          <span className="rounded-full bg-violet-200 px-2.5 py-1 text-xs font-semibold text-violet-950">開発中</span>
        </div>
        <p className="mt-2 max-w-4xl text-sm leading-6 text-gray-700">同じ質問を技術KBと法令KBへ別々に送り、回答と出典を並べて確認します。Markdown、OneNote案、ファイル名は送信しません。送るのは質問欄の文章だけです。</p>
      </header>

      <form onSubmit={search} className="space-y-3 rounded-xl border border-violet-200 bg-white p-4">
        <label htmlFor="knowledge-research-query" className="block text-sm font-semibold text-gray-900">照合したい質問</label>
        <textarea
          id="knowledge-research-query"
          aria-label="技術KBと法令KBへの質問"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          maxLength={2000}
          rows={3}
          className={inputClass}
          placeholder="例: この作業で必要な安全措置と、根拠となる法令・技術資料を教えてください。"
        />
        <div className="flex flex-wrap items-center gap-3">
          <button type="submit" disabled={running || !query.trim()} className="rounded-lg bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-800 focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:cursor-not-allowed disabled:opacity-50">技術KBと法令KBを照合</button>
          {running && <button type="button" onClick={cancel} className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50">検索を中止</button>}
          <span className="text-xs text-gray-500">送信時に各モードで別の履歴が作られ、API側の通常の60日保持対象になります。</span>
        </div>
        {error && <p role="alert" className="text-sm text-red-800">{error}</p>}
      </form>

      {submittedQuery && <div className="rounded-lg border border-violet-200 bg-white px-4 py-3"><p className="text-xs font-semibold text-gray-500">今回送った質問</p><p className="mt-1 whitespace-pre-wrap break-words text-sm text-gray-900">{submittedQuery}</p></div>}

      <div className="grid min-w-0 grid-cols-1 gap-4 xl:grid-cols-2">
        <ResearchResultLane mode="normal" state={lanes.normal} onAdopt={adopt} canAdopt={canAdopt} currentContextKey={contextKey} />
        <ResearchResultLane mode="law" state={lanes.law} onAdopt={adopt} canAdopt={canAdopt} currentContextKey={contextKey} />
      </div>
      {comparisonReady && technicalState.status === 'success' && lawState.status === 'success' ? (
        <KnowledgeComparisonPanel
          key={comparisonKey}
          technical={technicalState.answer}
          law={lawState.answer}
          contextKey={contextKey as string}
          targetLabel={targetLabel}
          onAdopt={onAdopt}
        />
      ) : submittedQuery ? (
        <div className="rounded-xl border border-gray-200 bg-white p-4 text-sm leading-6 text-gray-700">
          照合まとめは、同じ対象・同じ質問について技術KBと法令KBの両方に根拠付き回答がそろうと作成できます。片側の失敗・未収載・聞き返しや、対象本文の変更がある場合はまとめを取り込めません。
        </div>
      ) : null}
      <p className="text-xs leading-5 text-gray-600">検索結果は参考情報です。KBにないことと検索に失敗したことは別に扱います。内容の適用条件・矛盾・技術判断は担当者が確認してください。取り込みはローカルMarkdownの調査メモ候補で、OneNoteや原本へは書き込みません。</p>
    </section>
  );
}
