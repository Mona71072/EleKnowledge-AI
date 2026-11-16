import { Button } from '@/components/ui/Button';
import type { CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import {
  REWRITE_LIMITS,
  charCount,
  isRewriteEnabled,
  summarizeRewriteDecisions,
  type RewriteEvidenceRef,
  type RewriteExcludedReason,
  type RewritePlan,
  type RewriteProposal,
  type RewriteHistoryEntry,
} from '@/lib/knowhow-rewrite.mjs';
import { RewriteConflicts, RewriteSectionCard } from './KnowhowRewriteSections';

export type RewriteView =
  | { phase: 'idle' }
  | { phase: 'loading' }
  | { phase: 'error'; message: string }
  | { phase: 'ready'; proposal: RewriteProposal; evidenceRefs: RewriteEvidenceRef[] };

/** AI の案に付ける注記。確認は人の作業で、AI の案はそのままカードに入れない。 */
export const AI_REWRITE_NOTICE = 'AI が確認済みの根拠から作った案です。差分と根拠を確認してから反映してください。';
/** 節を書き換えて反映するときの注意書き。frontmatter は自動では変えない。 */
export const REWRITE_CAUTION = '本文の主張を変えました。Git に入れるときは card_version を上げ、台帳を作り直してください。この確認は技術承認ではありません。';
const RUN_LABEL = 'AI に本文の書き換え案を作らせる';
const OPEN_ITEMS_HEADING = '未確認事項';
const EXCLUDED_TEXT: Record<RewriteExcludedReason, string> = {
  duplicate: '同じ見出しが複数ある',
  empty: '本文が空の',
  too_long: `本文が${REWRITE_LIMITS.targetBodyChars.toLocaleString('en-US')}字を超える`,
  total_too_long: `対象の節の合計が${REWRITE_LIMITS.targetTotalChars.toLocaleString('en-US')}字を超える`,
};

type Props = {
  /** カードが knowledge_id を持つか。持たないカードには出さない。 */
  hasKnowledgeId: boolean;
  plan: RewritePlan;
  view: RewriteView;
  decisions: Readonly<Record<string, CheckDecision | undefined>>;
  conflictDecisions: Readonly<Record<number, CheckDecision | undefined>>;
  /** 案を破棄したときに一言見せる文。 */
  note: string;
  /** 一括照合の実行中。 */
  checking: boolean;
  busy?: boolean;
  history: readonly RewriteHistoryEntry[];
  selectedHistoryIndex: number;
  instruction: string;
  onInstructionChange: (value: string) => void;
  onRetry: () => void;
  onSelectHistory: (index: number) => void;
  onRun: () => void;
  onCancel: () => void;
  onDecide: (heading: string, decision: CheckDecision | null) => void;
  onDecideConflict: (index: number, decision: CheckDecision | null) => void;
};

function Preface({ plan }: { plan: RewritePlan }) {
  const { request, blocker, excluded, evidenceOmitted } = plan;
  return (
    <div className="space-y-1 text-sm leading-6 text-gray-800">
      {request
        ? <>
          <p>確認済みの根拠 {request.evidence.length} 件、書き換え対象 {request.targets.length} 節、文脈として参照する節 {request.context.length} 節、カード ID と版を AI に送ります。AI の利用料がかかります。</p>
          <details className="rounded-md border border-gray-200 px-3 py-2 text-sm">
            <summary className="cursor-pointer font-medium">送信内容の詳細</summary>
            <div className="mt-2 space-y-2 text-gray-700">
              <p>カード: {request.knowledgeId}（版 {request.cardVersion}）</p>
              {request.evidence.length > 0 && <div>
                <p className="font-medium">根拠（{request.evidence.length} 件）</p>
                <ul className="list-disc pl-5">{plan.evidenceRefs.slice(0, request.evidence.length).map(({ number, question }) => <li key={number}>{question}</li>)}</ul>
              </div>}
              {request.targets.length > 0 && <div>
                <p className="font-medium">書き換え対象の節（{request.targets.length} 節）</p>
                <ul className="list-disc pl-5">{request.targets.map(({ heading }) => <li key={heading}>{heading}</li>)}</ul>
              </div>}
              {request.context.length > 0 && <div>
                <p className="font-medium">文脈として参照する節（{request.context.length} 節）</p>
                <ul className="list-disc pl-5">{request.context.map(({ heading }) => <li key={heading}>{heading}</li>)}</ul>
              </div>}
            </div>
          </details>
        </>
        : <p role="status" className="text-amber-950">{blocker}</p>}
      {excluded.map(({ heading, reason }) => <p key={heading} className="text-xs text-amber-950">「{heading}」は{EXCLUDED_TEXT[reason]}ため対象から外しました。</p>)}
      {evidenceOmitted > 0 && (
        <p className="text-xs text-amber-950">根拠が多いため、先頭の {REWRITE_LIMITS.evidenceMax} 件だけを送ります。ほか {evidenceOmitted} 件は使いません。</p>
      )}
    </div>
  );
}

function Results({ proposal, evidenceRefs, decisions, conflictDecisions, onDecide, onDecideConflict }: Pick<Props, 'decisions' | 'conflictDecisions' | 'onDecide' | 'onDecideConflict'> & { proposal: RewriteProposal; evidenceRefs: RewriteEvidenceRef[] }) {
  const changed = proposal.sections.filter((section) => section.status === 'changed').map((section) => section.heading);
  const counts = summarizeRewriteDecisions(changed, decisions);
  return (
    <div className="space-y-3">
      <p className="text-xs leading-5 text-blue-950">{AI_REWRITE_NOTICE}</p>
      {counts.total > 0 && (
        <p role="status" className="rounded-lg bg-gray-50 p-3 text-sm text-gray-900">
          {`${counts.total}節中 ${counts.confirmed}節を反映・${counts.skipped}節を反映しない・${counts.pending}節が未確認。未確認のものはカードに入りません。`}
        </p>
      )}
      {proposal.sections.map((section, index) => (
        <RewriteSectionCard key={`${section.heading}-${index}`} section={section} refs={evidenceRefs}
          decision={decisions[section.heading]} onDecide={(decision) => onDecide(section.heading, decision)} />
      ))}
      <RewriteConflicts conflicts={proposal.conflicts} refs={evidenceRefs} decisions={conflictDecisions} onDecide={onDecideConflict}
        canAdd={proposal.bases.some(({ heading }) => heading === OPEN_ITEMS_HEADING)} />
      {counts.confirmed > 0 && <p role="note" className="rounded-lg bg-amber-50 p-3 text-sm font-semibold text-amber-950">{REWRITE_CAUTION}</p>}
    </div>
  );
}

/**
 * AI に本文の書き換え案を作らせ、節ごとに確認して反映するかを選ぶ。
 * `NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE=true` で、knowledge_id を持つカードにだけ出る。
 */
export function KnowhowRewritePanel({ hasKnowledgeId, plan, view, decisions, conflictDecisions, note, checking, busy, history, selectedHistoryIndex, instruction, onInstructionChange, onRetry, onSelectHistory, onRun, onCancel, onDecide, onDecideConflict }: Props) {
  if (!hasKnowledgeId || !isRewriteEnabled(process.env.NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE)) return null;
  const loading = view.phase === 'loading';
  const fieldLane = plan.request?.evidence.some(({ lane }) => lane === 'field') ?? false;
  const selectedInstruction = history[selectedHistoryIndex]?.instruction;
  return (
    <section aria-label="AI による本文の書き換え案" className="min-w-0 space-y-3 rounded-lg border border-blue-200 bg-white p-3 sm:p-4">
      <h3 className="font-semibold text-gray-950">AI による本文の書き換え案</h3>
      <p className="text-sm leading-6 text-gray-700">確認して追記すると決めた、出典つきの根拠だけを材料に、「統合した回答・ノウハウ」「調査・確認手順」「未確認事項」の書き換え案を作ります。</p>
      <Preface plan={plan} />
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" disabled={!plan.request || loading || checking || busy} onClick={onRun}>{RUN_LABEL}</Button>
        {loading && <Button type="button" variant="outline" onClick={onCancel}>中止</Button>}
        {loading && <span role="status" className="text-sm text-gray-700">案を作成しています（最長35秒）。</span>}
      </div>
      {note && <p role="status" className="rounded-lg bg-amber-50 p-3 text-sm text-amber-950">{note}</p>}
      {view.phase === 'error' && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-900">{view.message}</p>}
      {history.length > 0 && <nav aria-label="書き換え案の履歴" className="space-y-2">
        <p className="text-sm font-medium text-gray-900">案の履歴（このページ内のみ）</p>
        <ol className="flex flex-wrap gap-2">{history.map((entry, index) => <li key={`${entry.label}-${index}`} className="max-w-full space-y-1">
          <Button type="button" variant="outline" aria-pressed={selectedHistoryIndex === index} disabled={loading || busy}
            onClick={() => onSelectHistory(index)}>{entry.label}</Button>
          {entry.instruction && <p className="break-words text-xs text-gray-700">指示: {entry.instruction}</p>}
        </li>)}</ol>
      </nav>}
      {view.phase === 'ready' && (
        <>
          {history.length > 1 && <p className="text-sm text-gray-700">表示中: {history[selectedHistoryIndex]?.label ?? '案'}</p>}
          {selectedInstruction && <p role="note" className="rounded-lg bg-amber-50 p-3 text-sm font-semibold text-amber-950">指示で求めた内容は根拠で確認できていません。差分と根拠を確認してから採用してください</p>}
          <Results proposal={view.proposal} evidenceRefs={view.evidenceRefs} decisions={decisions}
            conflictDecisions={conflictDecisions} onDecide={onDecide} onDecideConflict={onDecideConflict} />
          {!fieldLane && history.length > 0 && selectedHistoryIndex === history.length - 1 && <div className="space-y-2 rounded-lg border border-blue-100 bg-blue-50 p-3">
            <label htmlFor="rewrite-instruction" className="block text-sm font-semibold text-gray-950">指示して作り直す</label>
            <textarea id="rewrite-instruction" name="rewrite-instruction" rows={3} value={instruction} onChange={(event) => onInstructionChange(event.currentTarget.value)}
              aria-describedby="rewrite-instruction-count" className="w-full rounded-md border border-gray-300 bg-white p-2 text-sm" />
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span id="rewrite-instruction-count" className="text-xs text-gray-700">{charCount(instruction).toLocaleString('en-US')}/1,000字</span>
              <Button type="button" disabled={loading || checking || busy || !instruction.trim() || charCount(instruction) > 1000}
                onClick={onRetry}>指示して作り直す</Button>
            </div>
          </div>}
          {!fieldLane && history.length > 1 && selectedHistoryIndex !== history.length - 1
            && <p role="status" className="text-sm text-gray-700">再実行する場合は、最新案を選んでください。</p>}
        </>
      )}
    </section>
  );
}
