'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { getIdToken } from '@/lib/auth-helpers';
import { createSenpaiChat, type SenpaiChatController, type SenpaiChatLane, type SenpaiChatSnapshot } from '@/lib/knowledge-senpai-chat.mjs';
import { buildChatSessionHref } from '@/lib/chat-session-link.mjs';
import {
  queryKnowledgeSource,
  researchSourceHref,
  type KnowledgeResearchMode,
  type ResearchCitationSource,
} from '@/lib/knowledge-research.mjs';

const EMPTY_SNAPSHOT: SenpaiChatSnapshot = { turns: [], running: false };
const inputClass = 'w-full resize-y rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm leading-6 text-gray-900 shadow-sm focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-200';

function useController(
  setSnapshot: (snapshot: SenpaiChatSnapshot) => void,
  controllerRef: { current: SenpaiChatController | null },
  mountedRef: { current: boolean },
) {
  useEffect(() => {
    let mounted = true;
    mountedRef.current = true;
    const controller = createSenpaiChat({
      querySource: ({ mode, query, sessionId, signal }) => queryKnowledgeSource({
        baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
        getToken: getIdToken,
        mode,
        query,
        ...(sessionId ? { sessionId } : {}),
        signal,
      }),
      onChange: (nextSnapshot) => {
        if (mounted) setSnapshot(nextSnapshot);
      },
    });
    controllerRef.current = controller;
    setSnapshot(controller.getSnapshot());
    return () => {
      mounted = false;
      mountedRef.current = false;
      if (controllerRef.current === controller) controllerRef.current = null;
      controller.dispose();
    };
  }, [controllerRef, mountedRef, setSnapshot]);
}

function sourceTitle(source: ResearchCitationSource, mode: KnowledgeResearchMode) {
  return mode === 'law'
    ? source.lawCitation?.lawTitle || source.title || source.documentName || '法令資料'
    : source.title || source.documentName || '技術資料';
}

function LaneReply({ lane, mode }: { lane: SenpaiChatLane; mode: KnowledgeResearchMode }) {
  const name = mode === 'law' ? '法令KB' : '技術KB';
  if (lane.status === 'loading') return <p role="status" className="text-sm text-gray-600">{name}を検索しています…</p>;
  if (lane.status === 'error') return <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{lane.message || `${name}への問い合わせに失敗しました。設定・通信状態を確認してください。`}</p>;
  if (lane.status === 'cancelled') return <p role="status" className="text-sm text-gray-600">{name}への検索は中止されました。</p>;
  if (lane.status === 'paused') return <p role="status" className="text-sm text-amber-900">{lane.message || `${name}への続きの質問を停止しています。新しい相談を始めてください。`}</p>;

  const answer = lane.answer;
  if (!answer) return <p className="text-sm text-gray-600">{name}から回答がありません。</p>;
  const sources = answer.sourceDocuments || [];
  const candidates = answer.pageCandidates || [];
  return (
    <div className="space-y-3">
      {answer.responseType === 'not_found' ? (
        <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">このKBでは該当情報を確認できませんでした。</p>
      ) : answer.responseType === 'clarify' ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">
          <p className="font-semibold">条件の確認が必要です</p>
          {answer.clarifyQuestions.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5">{answer.clarifyQuestions.map((question, index) => <li key={`${index}-${question}`}>{question}</li>)}</ul>}
        </div>
      ) : (
        <p className="whitespace-pre-wrap break-words text-sm leading-6 text-gray-800">{answer.content || '回答本文がありません。'}</p>
      )}
      {sources.length > 0 && (
        <div className="border-t border-gray-200 pt-2">
          <h5 className="mb-1 text-xs font-semibold text-gray-600">{mode === 'law' ? '法令の出典' : '技術資料の出典'}</h5>
          <ul className="space-y-1 text-xs">
            {sources.map((source, index) => {
              const href = researchSourceHref(source, mode);
              return (
                <li key={`${source.documentName || source.title || mode}-${index}`} className="break-words">
                  {href
                    ? <a href={href} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-700 underline underline-offset-2">{sourceTitle(source, mode)}{source.pageNumber ? ` · ${source.pageNumber}ページ` : ''}</a>
                    : <span className="text-gray-700">{sourceTitle(source, mode)}（安全なリンクを確認できません）</span>}
                  {mode === 'law' && source.lawCitation && <dl className="mt-1 grid grid-cols-[3.5rem_minmax(0,1fr)] gap-x-2 gap-y-0.5 text-gray-600">
                    {source.lawCitation.lawNumber && <><dt className="text-gray-500">法令番号</dt><dd>{source.lawCitation.lawNumber}</dd></>}
                    {(source.lawCitation.provisionReference || source.lawCitation.provisionType) && <><dt className="text-gray-500">条文</dt><dd>{source.lawCitation.provisionReference || source.lawCitation.provisionType}</dd></>}
                    {source.lawCitation.effectiveDate && <><dt className="text-gray-500">施行日</dt><dd>{source.lawCitation.effectiveDate}</dd></>}
                  </dl>}
                </li>
              );
            })}
          </ul>
        </div>
      )}
      {candidates.length > 0 && (
        <div className="border-t border-gray-200 pt-2">
          <h5 className="mb-1 text-xs font-semibold text-gray-600">ページ候補（参考）</h5>
          <ul className="space-y-1 text-xs">
            {candidates.map((source, index) => {
              const href = researchSourceHref(source, mode);
              const title = `${sourceTitle(source, mode)}${source.pageNumber ? ` · ${source.pageNumber}ページ` : ''}`;
              return <li key={`${source.documentName || source.title || mode}-candidate-${index}`} className="break-words">{href ? <a href={href} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-700 underline underline-offset-2">{title}</a> : <span className="text-gray-700">{title}（安全なリンクを確認できません）</span>}{source.snippet && <p className="mt-1 whitespace-pre-wrap text-gray-600">{source.snippet}</p>}</li>;
            })}
          </ul>
        </div>
      )}
      {answer.sessionId && (
        <Link href={buildChatSessionHref(answer.sessionId, mode)} className="inline-flex text-xs font-semibold text-blue-700 underline underline-offset-2">
          {mode === 'law' ? '法令チャットの履歴を開く' : '技術チャットの履歴を開く'}
        </Link>
      )}
    </div>
  );
}

function ChatTurnView({ turn }: { turn: SenpaiChatSnapshot['turns'][number] }) {
  return (
    <article className="space-y-4 border-b border-gray-200 pb-5 last:border-0" aria-label={`相談 ${turn.id}`}>
      <div className="ml-auto max-w-3xl rounded-2xl rounded-br-sm bg-violet-700 px-4 py-3 text-sm leading-6 text-white shadow-sm">
        <h3 className="mb-1 text-xs font-semibold text-violet-100">あなた</h3>
        <p className="whitespace-pre-wrap break-words">{turn.query}</p>
      </div>
      <div className="max-w-4xl rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-gray-900">工技先輩の回答</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <section aria-label="技術KBからの回答" className="min-w-0 space-y-2 rounded-xl bg-blue-50/70 p-3">
            <h4 className="text-xs font-bold uppercase tracking-wide text-blue-900">技術KB</h4>
            <LaneReply lane={turn.normal} mode="normal" />
          </section>
          <section aria-label="法令KBからの回答" className="min-w-0 space-y-2 rounded-xl bg-emerald-50/70 p-3">
            <h4 className="text-xs font-bold uppercase tracking-wide text-emerald-900">法令KB</h4>
            <LaneReply lane={turn.law} mode="law" />
          </section>
        </div>
        <p className="mt-3 text-xs text-gray-500">各KBの回答を個別に表示しています。必要に応じて根拠と適用条件を確認してください。</p>
      </div>
    </article>
  );
}

export function KnowledgeSenpaiChat() {
  const [snapshot, setSnapshot] = useState<SenpaiChatSnapshot>(EMPTY_SNAPSHOT);
  const [question, setQuestion] = useState('');
  const [sendError, setSendError] = useState('');
  const controllerRef = useRef<SenpaiChatController | null>(null);
  const mountedRef = useRef(false);
  const requestIdRef = useRef(0);
  const transcriptRef = useRef<HTMLDivElement | null>(null);
  const nearBottomRef = useRef(true);
  const scrollAfterSendRef = useRef(false);
  useController(setSnapshot, controllerRef, mountedRef);
  useEffect(() => {
    const transcript = transcriptRef.current;
    if (!transcript) return;
    if (scrollAfterSendRef.current || nearBottomRef.current) {
      transcript.scrollTop = transcript.scrollHeight;
      nearBottomRef.current = true;
    }
    scrollAfterSendRef.current = false;
  }, [snapshot]);
  const latestTurn = snapshot.turns.at(-1);
  const continuationPaused = !snapshot.running && Boolean(latestTurn)
    && [latestTurn!.normal, latestTurn!.law].every((lane) => lane.status !== 'success');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = question.trim();
    if (!query || snapshot.running || continuationPaused || !controllerRef.current) return;
    const controller = controllerRef.current;
    const requestId = ++requestIdRef.current;
    setSendError('');
    setQuestion('');
    scrollAfterSendRef.current = true;
    try {
      await controller.send(query);
    } catch (error) {
      const code = (error as { code?: string } | null)?.code;
      if (mountedRef.current && controllerRef.current === controller && requestIdRef.current === requestId) {
        setSendError(code === 'validation' ? '質問を送信できませんでした。入力内容を確認してください。' : '質問を送信できませんでした。時間をおいて再度お試しください。');
      }
    }
  }

  function startNewChat() {
    requestIdRef.current += 1;
    controllerRef.current?.reset();
    setQuestion('');
    setSendError('');
    setSnapshot(EMPTY_SNAPSHOT);
  }

  function cancelSearch() {
    requestIdRef.current += 1;
    controllerRef.current?.cancel();
  }

  return (
    <section aria-label="先輩チャット" className="mx-auto flex h-[calc(100dvh-6rem)] min-h-[24rem] max-h-[56rem] max-w-6xl flex-col overflow-hidden rounded-2xl border border-violet-200 bg-white shadow-sm">
      <header className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-gray-200 bg-gradient-to-r from-violet-50 to-indigo-50 px-4 py-4 sm:px-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">先輩チャット</h1>
          <p className="mt-1 text-sm text-gray-600">技術KBと法令KBに質問し、会話を続けながら回答と出典を確認します。</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full border border-violet-200 bg-white px-2.5 py-1 text-xs font-semibold text-violet-900">開発中・管理者限定</span>
          <Link href="/admin/knowledge/research" className="text-xs font-semibold text-violet-800 underline underline-offset-2">ノウハウの確認・編集</Link>
        </div>
      </header>

      <div ref={transcriptRef} onScroll={(event) => {
        const transcript = event.currentTarget;
        nearBottomRef.current = transcript.scrollHeight - transcript.scrollTop - transcript.clientHeight < 80;
      }} className="min-h-0 flex-1 space-y-5 overflow-y-auto px-4 py-5 sm:px-6" aria-live="polite" aria-relevant="additions text">
        {snapshot.turns.length === 0 ? (
          <div className="mx-auto max-w-2xl rounded-2xl border border-dashed border-violet-200 bg-violet-50/60 p-6 text-center">
            <h2 className="text-base font-semibold text-gray-900">どんなことを調べますか？</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">質問すると技術KBと法令KBへそれぞれ問い合わせます。回答は出典とともに分けて表示します。</p>
            <p className="mt-3 text-xs leading-5 text-gray-600">技術チャットと法令チャットの履歴は、それぞれの履歴に60日間保存されます。先輩チャットのまとめ表示は保存されないため、このページを再読み込みすると表示が消えます。</p>
          </div>
        ) : snapshot.turns.map((turn) => <ChatTurnView key={turn.id} turn={turn} />)}
        {continuationPaused && <p role="status" className="mx-auto max-w-2xl rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">両方の検索が失敗または中止されたため、この相談では続けて質問できません。内容を確認し、「新しい相談」から再開してください。</p>}
      </div>

      <footer className="shrink-0 border-t border-gray-200 bg-gray-50 px-4 py-4 sm:px-6">
        <form onSubmit={submit} className="mx-auto max-w-5xl space-y-3">
          <label htmlFor="senpai-chat-question" className="block text-sm font-semibold text-gray-800">質問を入力</label>
          <textarea
            id="senpai-chat-question"
            aria-label="質問を入力"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            disabled={snapshot.running || continuationPaused}
            rows={2}
            maxLength={2000}
            placeholder="例: この機器の交換作業で注意する点は？根拠となる資料も教えてください。"
            className={inputClass}
          />
          {sendError && <p role="alert" className="text-sm text-red-700">{sendError}</p>}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex gap-2">
              <button type="submit" disabled={snapshot.running || continuationPaused || !question.trim()} className="rounded-lg bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-800 focus:outline-none focus:ring-2 focus:ring-violet-400 disabled:cursor-not-allowed disabled:opacity-50">質問を送信</button>
              {snapshot.running && <button type="button" onClick={cancelSearch} className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-400">中止</button>}
              <button type="button" onClick={startNewChat} disabled={snapshot.turns.length === 0 && !snapshot.running} className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-400 disabled:cursor-not-allowed disabled:opacity-50">新しい相談</button>
            </div>
            <span className="text-xs text-gray-500">送信した質問のみ、技術KB・法令KBへ個別に送られます。Markdownは送信されません。</span>
          </div>
        </form>
      </footer>
    </section>
  );
}
