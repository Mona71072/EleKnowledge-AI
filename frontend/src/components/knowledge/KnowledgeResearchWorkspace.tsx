'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { getIdToken } from '@/lib/auth-helpers';
import { buildChatSessionHref } from '@/lib/chat-session-link.mjs';
import { KnowledgeComparisonPanel } from './KnowledgeComparisonPanel';
import {
  buildResearchNote,
  queryKnowledgeSource,
  researchSourceHref,
  type ResearchCitationSource,
  type ResearchAnswer,
} from '@/lib/knowledge-research.mjs';

type Mode = 'normal' | 'law';
type LaneState =
  | { status: 'idle' | 'loading' | 'cancelled' }
  | { status: 'success'; answer: ResearchAnswer; contextKey: string | null; targetLabel: string; searchId: number }
  | { status: 'error'; message: string };

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

function errorMessage(error: unknown, mode: Mode): string {
  const issue = error as { name?: string; message?: string; code?: string } | null;
  const code = issue?.code || '';
  const laneName = mode === 'law' ? '法令KB' : '技術KB';
  if (issue?.name === 'AbortError' || code === 'cancelled') return 'この検索は中止されました。';
  if (code === 'auth') return 'ログイン状態または利用権限を確認してください。';
  if (code === 'config') return `${laneName}の接続先が設定されていません。`;
  if (code === 'timeout') return `${laneName}の応答が時間内に届きませんでした。もう一度検索できます。`;
  if (code === 'unavailable') return `${laneName}を利用できません。接続設定・APIの有効化・権限を確認してください。`;
  if (code === 'validation' || code === 'invalid_response') return `${laneName}から想定外の応答が返りました。`;
  if (code === 'server') return `${laneName}でエラーが発生しました。時間をおいて再度お試しください。`;
  if (issue?.message?.includes('設定') || issue?.message?.includes('ログイン')) return issue.message;
  return `${laneName}への問い合わせに失敗しました。設定・通信状態を確認してください。`;
}

function safeHref(mode: Mode, source: ResearchCitationSource): string | undefined {
  try {
    return researchSourceHref(source, mode) || undefined;
  } catch {
    return undefined;
  }
}

function ResultLane({
  mode,
  state,
  onAdopt,
  canAdopt,
  currentContextKey,
}: {
  mode: Mode;
  state: LaneState;
  onAdopt: (answer: ResearchAnswer, expectedContextKey: string | null) => boolean;
  canAdopt: boolean;
  currentContextKey: string | null;
}) {
  const isLaw = mode === 'law';
  const title = isLaw ? '法令KB' : '技術KB';
  return (
    <section className="min-w-0 rounded-xl border border-gray-200 bg-white shadow-sm" aria-label={`${title}の検索結果`}>
      <header className={`border-b px-4 py-3 ${isLaw ? 'border-amber-200 bg-amber-50' : 'border-blue-200 bg-blue-50'}`}>
        <h3 className="font-semibold text-gray-950">{title}</h3>
        <p className="mt-1 text-xs text-gray-600">{isLaw ? '法令モードの独立した検索' : '通常モードの独立した検索'}</p>
      </header>
      <div className="space-y-4 p-4">
        {state.status === 'idle' && <p className="text-sm text-gray-500">質問を入力して照合を始めてください。</p>}
        {state.status === 'loading' && <p role="status" className="text-sm text-gray-700">{title}を検索しています…</p>}
        {state.status === 'cancelled' && <p role="status" className="text-sm text-gray-600">この検索を中止しました。</p>}
        {state.status === 'error' && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-900">{state.message}</p>}
        {state.status === 'success' && (
          <LaneAnswer
            answer={state.answer}
            mode={mode}
            onAdopt={onAdopt}
            canAdopt={canAdopt}
            currentContextKey={currentContextKey}
            searchedContextKey={state.contextKey}
            targetLabel={state.targetLabel}
          />
        )}
      </div>
    </section>
  );
}

function LaneAnswer({
  answer,
  mode,
  onAdopt,
  canAdopt: allowAdoption,
  currentContextKey,
  searchedContextKey,
  targetLabel,
}: {
  answer: ResearchAnswer;
  mode: Mode;
  onAdopt: (answer: ResearchAnswer, expectedContextKey: string | null) => boolean;
  canAdopt: boolean;
  currentContextKey: string | null;
  searchedContextKey: string | null;
  targetLabel: string;
}) {
  const sources = Array.isArray(answer.sourceDocuments) ? answer.sourceDocuments : [];
  const candidates = Array.isArray(answer.pageCandidates) ? answer.pageCandidates : [];
  const questions = Array.isArray(answer.clarifyQuestions) ? answer.clarifyQuestions : [];
  const answerText = typeof answer.content === 'string' ? answer.content.trim() : '';
  const isLaw = mode === 'law';
  const verifiedSourceCount = sources.filter((source) => Boolean(safeHref(mode, source))).length;
  const showAdoptionControl = answerText.length > 0 && answer.responseType === 'pages';
  const targetChanged = searchedContextKey !== currentContextKey;

  return (
    <>
      {answer.responseType === 'not_found' ? (
        <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">このKBでは該当情報を確認できませんでした。もう一方のKBで代用せず、結果を分けて扱ってください。</p>
      ) : answer.responseType === 'clarify' ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">
          <p className="font-semibold">条件の確認が必要です</p>
          {questions.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5">{questions.map((question, index) => <li key={`${index}-${question}`}>{question}</li>)}</ul>}
        </div>
      ) : (
        <div className="rounded-lg bg-gray-50 p-3 text-sm leading-6 text-gray-800">
          <h4 className="mb-2 text-xs font-semibold text-gray-500">回答（文字表示）</h4>
          <p className="whitespace-pre-wrap break-words">{answerText || '回答本文がありません。'}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-semibold text-gray-600">{isLaw ? '法令の出典' : '技術資料の出典'}</h4>
          <ul className="space-y-2">
            {sources.map((source, index) => {
              const law = source.lawCitation;
              const title = isLaw
                ? law?.lawTitle || source.title || source.documentName || '法令資料'
                : source.title || source.documentName || '技術資料';
              const href = safeHref(mode, source);
              return (
                <li key={`${source.documentName || title}-${index}`} className="rounded-lg border border-gray-200 p-3 text-sm">
                  <p className="font-medium text-gray-900">{title}</p>
                  {isLaw && law && (
                    <dl className="mt-2 grid grid-cols-[5rem_minmax(0,1fr)] gap-x-2 gap-y-1 text-xs text-gray-700">
                      <dt className="text-gray-500">法令番号</dt><dd className="break-words">{law.lawNumber || '—'}</dd>
                      <dt className="text-gray-500">条文</dt><dd className="break-words">{law.provisionReference || law.provisionType || '—'}</dd>
                      <dt className="text-gray-500">施行日</dt><dd>{law.effectiveDate || '—'}</dd>
                    </dl>
                  )}
                  {!isLaw && <p className="mt-1 text-xs text-gray-600">{source.documentName || '資料名なし'}{source.pageNumber ? ` · ${source.pageNumber}ページ` : ''}</p>}
                  {href && <a href={href} target="_blank" rel="noopener noreferrer" className="mt-2 inline-flex text-xs font-semibold text-blue-700 underline underline-offset-2">{isLaw ? 'e-Gov法令を開く' : '技術資料を開く'}</a>}
                  {!href && <p className="mt-2 text-xs font-medium text-amber-800">出典を確認できません。安全なリンクとして検証できませんでした。</p>}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {candidates.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-semibold text-gray-600">ページ候補</h4>
          <ul className="space-y-2">{candidates.map((candidate, index) => {
            const href = safeHref(mode, candidate);
            return <li key={`${candidate.documentName}-${candidate.pageNumber || index}`} className="rounded-lg border border-gray-200 p-3 text-sm">
              <p className="font-medium text-gray-900">{candidate.documentName || '資料名なし'}{candidate.pageNumber ? ` · ${candidate.pageNumber}ページ` : ''}</p>
              {candidate.snippet && <p className="mt-2 whitespace-pre-wrap text-xs leading-5 text-gray-700">{candidate.snippet}</p>}
              {href && <a href={href} target="_blank" rel="noopener noreferrer" className="mt-2 inline-flex text-xs font-semibold text-blue-700 underline underline-offset-2">技術資料を開く</a>}
              {!href && <p className="mt-2 text-xs font-medium text-amber-800">出典を確認できません。安全なリンクとして検証できませんでした。</p>}
            </li>;
          })}</ul>
        </div>
      )}

      {answer.sessionId && <Link href={buildChatSessionHref(answer.sessionId, mode)} className="inline-flex text-xs font-semibold text-blue-700 underline underline-offset-2">このモードのチャット履歴を開く</Link>}
      {targetLabel && (
        <p className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-700">
          検索対象: {targetLabel}
        </p>
      )}
      {showAdoptionControl && (
        <div className="space-y-2">
          {targetChanged && <p role="status" className="text-sm font-medium text-amber-900">対象Markdownまたは本文が変わりました。現在の対象を読み直し、再検索して照合してください。</p>}
          <button
            type="button"
            onClick={() => onAdopt(answer, searchedContextKey)}
            disabled={!allowAdoption || verifiedSourceCount === 0 || targetChanged}
            title={targetChanged ? '対象Markdownまたは本文が変更されています。再検索してください。' : verifiedSourceCount === 0 ? 'モードに対応する有効な出典リンクがありません。' : !allowAdoption ? 'Markdownを選ぶと取り込めます。' : undefined}
            className="w-full rounded-lg border border-blue-300 bg-blue-50 px-3 py-2.5 text-sm font-semibold text-blue-900 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {verifiedSourceCount === 0 ? '有効な出典がないため取込不可' : '調査メモとしてMarkdown編集案へ取り込む'}
          </button>
          {verifiedSourceCount === 0 && <p role="status" className="text-xs leading-5 text-amber-900">有効な出典がないため取込不可です。出典のURLまたは法令情報を確認できる結果が必要です。</p>}
        </div>
      )}
    </>
  );
}

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
        return { status: 'error', message: errorMessage(reason, mode) };
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
      && technicalState.answer.sourceDocuments.some((source) => Boolean(safeHref('normal', source)))
      && lawState.answer.sourceDocuments.some((source) => Boolean(safeHref('law', source))),
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
        <ResultLane mode="normal" state={lanes.normal} onAdopt={adopt} canAdopt={canAdopt} currentContextKey={contextKey} />
        <ResultLane mode="law" state={lanes.law} onAdopt={adopt} canAdopt={canAdopt} currentContextKey={contextKey} />
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
