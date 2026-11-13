import Link from 'next/link';
import { buildChatSessionHref } from '@/lib/chat-session-link.mjs';
import { researchSourceHref, type ResearchAnswer, type ResearchCitationSource } from '@/lib/knowledge-research.mjs';

type Mode = 'normal' | 'law';
export type LaneState =
  | { status: 'idle' | 'loading' | 'cancelled' }
  | { status: 'success'; answer: ResearchAnswer; contextKey: string | null; targetLabel: string; searchId: number }
  | { status: 'error'; message: string };

export function knowledgeResearchErrorMessage(error: unknown, mode: Mode): string {
  const issue = error as { name?: string; code?: string } | null;
  const code = issue?.code || '';
  const laneName = mode === 'law' ? '法令KB' : '技術KB';
  if (issue?.name === 'AbortError' || code === 'cancelled') return 'この検索は中止されました。';
  if (code === 'auth') return 'ログイン状態または利用権限を確認してください。';
  if (code === 'config') return `${laneName}の接続先が設定されていません。`;
  if (code === 'timeout') return `${laneName}の応答が時間内に届きませんでした。もう一度検索できます。`;
  if (code === 'unavailable') return `${laneName}を利用できません。接続設定・APIの有効化・権限を確認してください。`;
  if (code === 'validation' || code === 'invalid_response') return `${laneName}から想定外の応答が返りました。`;
  if (code === 'server') return `${laneName}でエラーが発生しました。時間をおいて再度お試しください。`;
  return `${laneName}への問い合わせに失敗しました。設定・通信状態を確認してください。`;
}

export function safeResearchHref(mode: Mode, source: ResearchCitationSource): string | undefined {
  try {
    return researchSourceHref(source, mode) || undefined;
  } catch {
    return undefined;
  }
}

export function ResearchResultLane({
  mode,
  state,
  onAdopt,
  canAdopt = false,
  currentContextKey = null,
}: {
  mode: Mode;
  state: LaneState | { status: 'queued' };
  onAdopt?: (answer: ResearchAnswer, expectedContextKey: string | null) => boolean;
  canAdopt?: boolean;
  currentContextKey?: string | null;
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
        {state.status === 'queued' && <p className="text-sm text-gray-700">照合を待っています。</p>}
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
  onAdopt?: (answer: ResearchAnswer, expectedContextKey: string | null) => boolean;
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
  const verifiedSourceCount = sources.filter((source) => Boolean(safeResearchHref(mode, source))).length;
  const showAdoptionControl = onAdopt && answerText.length > 0 && answer.responseType === 'pages';
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
              const href = safeResearchHref(mode, source);
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
            const href = safeResearchHref(mode, candidate);
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
            onClick={() => onAdopt?.(answer, searchedContextKey)}
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

