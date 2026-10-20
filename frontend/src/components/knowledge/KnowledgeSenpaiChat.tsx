'use client';

import { FormEvent, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useSenpaiHistory } from '@/hooks/useSenpaiHistory';
import { SenpaiConversationSidebar } from './SenpaiConversationSidebar';
import { getIdToken } from '@/lib/auth-helpers';
import { createSenpaiChat, type SenpaiChatController, type SenpaiChatLane, type SenpaiChatSnapshot, type SenpaiChatTurn } from '@/lib/knowledge-senpai-chat.mjs';
import { requestSenpaiSynthesis } from '@/lib/knowledge-senpai-synthesis.mjs';
import { ALL_MODEL_TYPES } from '@/data/kbModelTypes';
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
      querySource: ({ mode, query, modelType, sessionId, senpaiConversationId, senpaiTurnId, signal }) => queryKnowledgeSource({
        baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
        getToken: getIdToken,
        mode,
        query,
        ...(modelType ? { modelType } : {}),
        senpaiConversationId,
        senpaiTurnId,
        ...(sessionId ? { sessionId } : {}),
        ...(mode === 'normal' ? { includeKnowhow: true } : {}),
        signal,
      }),
      synthesisSource: ({ senpaiConversationId, senpaiTurnId, signal }) => requestSenpaiSynthesis({
        baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
        getToken: getIdToken,
        senpaiConversationId,
        senpaiTurnId,
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

const scopeLabels: Record<string, string> = {
  conditions: '対象条件', control_methods: '制御方式', door_families: 'ドアの種類', door_types: 'ドア型式',
  excludes: '適用除外', guide_systems: 'ガイド方式', lists_model_label: '元記録の機種', machine_room: '機械室',
  may_apply_to: '適用可能性（未確認）', model_abbreviations: '機種略称', observed_on: '確認された対象',
  product_lines: '製品系列', scope_note: '対象範囲の補足',
  scope_status: '適用範囲の確認', scope_verified_by: '確認者', scope_verified_at: '確認日',
};
const refLabels: Record<string, string> = {
  list_item_id: 'Lists項目', onenote_id: 'OneNoteページ', source_id: '出典ID', document_number: '資料番号',
  kb_filename: 'KB資料名', kb_verify_status: 'KB確認状況', page_role: 'ページの役割', law_id: '法令ID',
  law_title: '法令名', locator: '参照箇所',
};

// Unknown keys fall back to the raw key so a label never renders as "undefined".
function scopeLabel(key: string) {
  return scopeLabels[key] ?? key;
}

function refLabel(key: string) {
  return refLabels[key] ?? key;
}

function scopeValue(key: string, value: string | string[]) {
  if (key === 'scope_status') return value === 'verified' ? '担当者確認済み' : '未確認';
  return (Array.isArray(value) ? value.join('、') : value) || '未記載';
}

function KnowhowReferences({ answer }: { answer: import('@/lib/knowledge-research.mjs').ResearchAnswer }) {
  const knowhow = answer.knowhow;
  if (!knowhow) return null;
  if (knowhow.status === 'not_found') {
    return <p className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-xs leading-5 text-gray-700">参照できるノウハウMarkdownは見つかりませんでした。この回答は技術KBの検索結果を確認してください。</p>;
  }
  return (
    <section aria-label="参照したノウハウMarkdown" className="rounded-lg border border-violet-200 bg-violet-50/70 p-3">
      <h5 className="text-xs font-semibold text-violet-950">参照したノウハウMarkdown</h5>
      <p className="mt-1 text-xs leading-5 text-violet-950">サーバーで検索が許可されたノウハウMarkdownから、関連する候補を見つけました。記載の版・状態はこの回答時点のものです。これは探索の手掛かりで、技術的な根拠や承認を示しません。</p>
      <ul className="mt-2 space-y-3">
        {knowhow.matches.map((match) => (
          <li key={`${match.knowledgeId}-${match.cardVersion}`} className="rounded-md border border-violet-100 bg-white p-3 text-xs text-gray-800">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold">{match.title}</span>
              <span>v{match.cardVersion}</span>
              <span className="rounded-full bg-amber-100 px-2 py-0.5 font-semibold text-amber-950">{match.status === 'draft' ? '未承認（下書き）' : '承認済みカード・参照用のみ'}</span>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 font-semibold text-gray-700">参照用のみ</span>
            </div>
            <details className="mt-2 rounded border border-gray-200 p-2">
              <summary className="cursor-pointer font-semibold text-violet-900">適用条件・出典と本文を確認</summary>
              <dl className="mt-2 grid grid-cols-[5rem_minmax(0,1fr)] gap-x-2 gap-y-1 break-words text-gray-700">
                <dt className="text-gray-500">ノウハウID</dt><dd>{match.knowledgeId}</dd>
                <dt className="text-gray-500">本文の識別値</dt><dd className="break-all font-mono">{match.sha256}</dd>
                {Object.entries(match.modelScope).map(([key, value]) => (
                  <div key={key} className="contents"><dt className="text-gray-500">{scopeLabel(key)}</dt><dd>{scopeValue(key, value)}</dd></div>
                ))}
              </dl>
              <ul className="mt-2 space-y-2 border-t border-gray-200 pt-2">
                {match.sourceRefs.map((ref, index) => <li key={index} className="break-words">
                  {Object.entries(ref).filter(([key]) => key !== 'ref_type').map(([key, value]) => <p key={key}>{refLabel(key)}: {value}</p>)}
                </li>)}
              </ul>
              <pre className="mt-2 whitespace-pre-wrap break-words font-sans text-gray-800">{match.body}</pre>
            </details>
          </li>
        ))}
      </ul>
      {knowhow.searchTerms.length > 0 && <p className="mt-2 text-xs text-gray-700">技術KB検索へ加えた手掛かり: {knowhow.searchTerms.join('、')}</p>}
    </section>
  );
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
      {mode === 'normal' && <KnowhowReferences answer={answer} />}
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

function canSynthesize(turn: SenpaiChatTurn, running: boolean) {
  const lanes = [turn.normal, turn.law];
  return !running && Boolean(turn.senpaiTurnId)
    && lanes.every((lane) => lane.status !== 'loading')
    && lanes.some((lane) => lane.status === 'success')
    && turn.synthesis?.status !== 'loading' && turn.synthesis?.status !== 'success';
}

function SynthesisSection({ turn, running, onSynthesize }: {
  turn: SenpaiChatTurn;
  running: boolean;
  onSynthesize: (turnId: number) => void;
}) {
  const synthesis = turn.synthesis;
  const button = canSynthesize(turn, running) && (
    <button type="button" onClick={() => onSynthesize(turn.id)} className="rounded-lg border border-violet-300 bg-white px-3 py-1.5 text-xs font-semibold text-violet-900 hover:bg-violet-50 focus:outline-none focus:ring-2 focus:ring-violet-400">工技先輩のまとめを作る</button>
  );
  if (!synthesis) return button ? <div className="mb-3">{button}</div> : null;
  if (synthesis.status === 'loading') return <p role="status" className="mb-3 rounded-xl border border-violet-200 bg-violet-50 p-3 text-sm text-violet-900">まとめを作成しています…</p>;
  if (synthesis.status === 'error') {
    return (
      <div className="mb-3 space-y-2">
        <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{synthesis.message || 'まとめを作成できませんでした。時間をおいて再度お試しください。'}</p>
        {button}
      </div>
    );
  }
  const inputs = synthesis.inputs;
  return (
    <section aria-label="工技先輩のまとめ" className="mb-3 rounded-xl border-2 border-violet-300 bg-violet-50 p-4">
      <h4 className="text-sm font-bold text-violet-950">工技先輩のまとめ（試作・開発中）</h4>
      <p className="mt-1 text-xs leading-5 text-violet-900">下の2つの回答を組み合わせただけの文章です。内容は必ず各回答の出典で確認してください。ノウハウは未承認の参考情報で、根拠にはなりません。</p>
      <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-gray-900">{synthesis.content}</p>
      {inputs && (
        <p className="mt-3 text-xs text-violet-900">
          {!inputs.normal && '技術KBの回答は使っていません。'}{!inputs.law && '法令KBの回答は使っていません。'}
          {inputs.knowhowCount > 0 && `ノウハウ候補${inputs.knowhowCount}件を参考として含めています。`}
        </p>
      )}
    </section>
  );
}

function ChatTurnView({ turn, running, onSynthesize }: { turn: SenpaiChatTurn; running: boolean; onSynthesize: (turnId: number) => void }) {
  return (
    <article className="space-y-4 border-b border-gray-200 pb-5 last:border-0" aria-label={`相談 ${turn.id}`}>
      <div className="ml-auto max-w-3xl rounded-2xl rounded-br-sm bg-violet-700 px-4 py-3 text-sm leading-6 text-white shadow-sm">
        <h3 className="mb-1 text-xs font-semibold text-violet-100">あなた</h3>
        <p className="whitespace-pre-wrap break-words">{turn.query}</p>
        {turn.modelType && <p className="mt-2 inline-block rounded-full bg-violet-600 px-2 py-0.5 text-xs font-semibold text-white">機種: {turn.modelType}</p>}
      </div>
      <div className="max-w-4xl rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-4 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-gray-900">工技先輩の回答</h3>
        <SynthesisSection turn={turn} running={running} onSynthesize={onSynthesize} />
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
  const [modelType, setModelType] = useState('');
  const [sendError, setSendError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const controllerRef = useRef<SenpaiChatController | null>(null);
  const mountedRef = useRef(false);
  const requestIdRef = useRef(0);
  const transcriptRef = useRef<HTMLDivElement | null>(null);
  const nearBottomRef = useRef(true);
  const scrollAfterSendRef = useRef(false);
  useController(setSnapshot, controllerRef, mountedRef);
  const history = useSenpaiHistory(snapshot, controllerRef);
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
  const continuationPaused = snapshot.complete === false || (!snapshot.running && Boolean(latestTurn)
    && [latestTurn!.normal, latestTurn!.law].every((lane) => lane.status !== 'success'));

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = question.trim();
    if (!query || snapshot.running || continuationPaused || history.opening || !controllerRef.current) return;
    const controller = controllerRef.current;
    const requestId = ++requestIdRef.current;
    setSendError('');
    setQuestion('');
    scrollAfterSendRef.current = true;
    try {
      await controller.send(query, ...(modelType ? [{ modelType }] : []));
    } catch (error) {
      const code = (error as { code?: string } | null)?.code;
      if (mountedRef.current && controllerRef.current === controller && requestIdRef.current === requestId) {
        setSendError(code === 'validation' ? '質問を送信できませんでした。入力内容を確認してください。' : '質問を送信できませんでした。時間をおいて再度お試しください。');
      }
    }
  }

  function startNewChat() {
    requestIdRef.current += 1;
    history.resetSelection();
    controllerRef.current?.reset();
    setQuestion('');
    setSendError('');
    setSnapshot(EMPTY_SNAPSHOT);
    setSidebarOpen(false);
  }

  function openSavedChat(conversationId: string) {
    if (conversationId === snapshot.conversationId && !history.opening) {
      setSidebarOpen(false);
      return;
    }
    requestIdRef.current += 1;
    setQuestion('');
    setSendError('');
    setSidebarOpen(false);
    nearBottomRef.current = true;
    void history.openConversation(conversationId);
  }

  function requestSynthesis(turnId: number) {
    // The controller keeps the failure on the turn's synthesis lane; nothing else to show here.
    controllerRef.current?.synthesize(turnId).catch(() => {});
  }

  function cancelSearch() {
    requestIdRef.current += 1;
    controllerRef.current?.cancel();
  }

  return (
    <section aria-label="先輩チャット" className="flex h-dvh min-h-[24rem] flex-col overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="flex shrink-0 items-center justify-between gap-2 border-b border-gray-200 bg-white px-4 py-2.5 shadow-sm sm:px-6">
        <div className="flex min-w-0 items-center gap-2.5">
          <button type="button" aria-label="履歴を開く" aria-controls="senpai-history" aria-expanded={sidebarOpen} onClick={() => setSidebarOpen(true)} className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 md:hidden"><svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg></button>
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 text-white" aria-hidden="true">先</span>
          <div><p className="hidden text-lg font-bold leading-tight text-gray-900 sm:block">EleKnowledge</p><h1 className="text-sm font-semibold text-gray-900 sm:text-xs sm:font-normal sm:text-gray-500">先輩チャット</h1></div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="hidden rounded-full border border-violet-200 bg-violet-50 px-2.5 py-1 text-xs font-semibold text-violet-900 sm:inline">開発中・管理者限定</span>
          <Link href="/admin/knowledge/research" aria-label="ノウハウの確認・編集" className="rounded-lg border border-violet-200 bg-violet-50 px-2.5 py-1.5 text-xs font-semibold text-violet-800"><span className="hidden sm:inline">ノウハウの確認・編集</span><span className="sm:hidden">編集</span></Link>
          <Link href="/" aria-label="ホームへ戻る" className="rounded-lg border border-gray-300 px-2.5 py-1.5 text-xs font-semibold text-gray-700 hover:bg-gray-50"><span className="hidden sm:inline">ホームへ戻る</span><span className="sm:hidden">ホーム</span></Link>
        </div>
      </header>
      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <SenpaiConversationSidebar open={sidebarOpen} entries={history.entries} selectedId={snapshot.conversationId} loading={history.loading} error={history.error} complete={history.complete} onNew={startNewChat} onSelect={openSavedChat} onClose={() => setSidebarOpen(false)} onRetry={history.refresh} />
        <main className="flex min-w-0 flex-1 flex-col">
          {history.openError && <p role="alert" className="border-b border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{history.openError}</p>}
          {history.opening && <p role="status" className="border-b border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-900">相談履歴を開いています…</p>}
      <div ref={transcriptRef} onScroll={(event) => {
        const transcript = event.currentTarget;
        nearBottomRef.current = transcript.scrollHeight - transcript.scrollTop - transcript.clientHeight < 80;
      }} className="min-h-0 flex-1 space-y-5 overflow-y-auto px-4 py-5 sm:px-6" aria-live="polite" aria-relevant="additions text">
        {snapshot.turns.length === 0 ? (
          <div className="mx-auto max-w-2xl rounded-2xl border border-dashed border-violet-200 bg-violet-50/60 p-6 text-center">
            <h2 className="text-base font-semibold text-gray-900">どんなことを調べますか？</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">サーバーで検索が許可されたノウハウMarkdownを参考に技術KBを調べ、法令KBにも個別に問い合わせます。回答は出典とともに分けて表示します。</p>
            <p className="mt-2 text-xs leading-5 text-gray-600">ローカルファイルは送信されません。ノウハウMarkdownは参考情報として表示し、Markdownの編集やOneNoteへの追記は行いません。</p>
            <p className="mt-3 text-xs leading-5 text-gray-600">相談履歴は60日間保存されます。ページを再読み込みした後も、左側の履歴から相談を開き直せます。</p>
          </div>
        ) : snapshot.turns.map((turn) => <ChatTurnView key={turn.id} turn={turn} running={snapshot.running} onSynthesize={requestSynthesis} />)}
        {continuationPaused && <p role="status" className="mx-auto max-w-2xl rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-950">{snapshot.complete === false ? '相談履歴の一部を確認できないため、表示のみ利用できます。' : '両方の検索が失敗または中止されたため、この相談では続けて質問できません。'}内容を確認し、「新しい相談」から再開してください。</p>}
      </div>

      <footer className="shrink-0 border-t border-gray-200 bg-gray-50 px-4 py-4 sm:px-6">
        <form onSubmit={submit} className="mx-auto max-w-5xl space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <label htmlFor="senpai-chat-model" className="text-sm font-semibold text-gray-800">機種（任意）</label>
            <select
              id="senpai-chat-model"
              value={modelType}
              onChange={(event) => setModelType(event.target.value)}
              disabled={snapshot.running || continuationPaused || history.opening}
              className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-900 focus:border-violet-500 focus:outline-none focus:ring-2 focus:ring-violet-200"
            >
              <option value="">指定しない</option>
              {ALL_MODEL_TYPES.map((model) => <option key={model.value} value={model.value}>{model.label}</option>)}
            </select>
            <span className="text-xs text-gray-500">技術KBとノウハウの検索を、その機種に絞り込みます（法令KBは対象外）。</span>
          </div>
          <label htmlFor="senpai-chat-question" className="block text-sm font-semibold text-gray-800">質問を入力</label>
          <textarea
            id="senpai-chat-question"
            aria-label="質問を入力"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            disabled={snapshot.running || continuationPaused || history.opening}
            rows={2}
            maxLength={2000}
            placeholder="例: この機器の交換作業で注意する点は？根拠となる資料も教えてください。"
            className={inputClass}
          />
          {sendError && <p role="alert" className="text-sm text-red-700">{sendError}</p>}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex gap-2">
              <button type="submit" disabled={snapshot.running || continuationPaused || history.opening || !question.trim()} className="rounded-lg bg-violet-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-800 focus:outline-none focus:ring-2 focus:ring-violet-400 disabled:cursor-not-allowed disabled:opacity-50">質問を送信</button>
              {snapshot.running && <button type="button" onClick={cancelSearch} className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-400">中止</button>}
              <button type="button" onClick={startNewChat} disabled={snapshot.turns.length === 0 && !snapshot.running && !history.opening} className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-400 disabled:cursor-not-allowed disabled:opacity-50">新しい相談</button>
            </div>
            <span className="text-xs text-gray-500">質問のみを技術KB・法令KBへ個別に送ります。サーバー許可済みMarkdownを参考検索します。ローカルファイルの送信やMarkdown編集、OneNote追記は行いません。</span>
          </div>
        </form>
      </footer>
        </main>
      </div>
    </section>
  );
}
