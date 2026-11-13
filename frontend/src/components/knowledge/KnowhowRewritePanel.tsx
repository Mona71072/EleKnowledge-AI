import { Button } from '@/components/ui/Button';
import type { CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import {
  REWRITE_LIMITS,
  isRewriteEnabled,
  summarizeRewriteDecisions,
  type RewriteEvidenceRef,
  type RewriteExcludedReason,
  type RewritePlan,
  type RewriteProposal,
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
        ? <p>確認済みの根拠 {request.evidence.length} 件と、カードの{request.targets.length}つの節を AI に送ります。AI の利用料がかかります。</p>
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
export function KnowhowRewritePanel({ hasKnowledgeId, plan, view, decisions, conflictDecisions, note, checking, busy, onRun, onCancel, onDecide, onDecideConflict }: Props) {
  if (!hasKnowledgeId || !isRewriteEnabled(process.env.NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE)) return null;
  const loading = view.phase === 'loading';
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
      {view.phase === 'ready' && (
        <Results proposal={view.proposal} evidenceRefs={view.evidenceRefs} decisions={decisions}
          conflictDecisions={conflictDecisions} onDecide={onDecide} onDecideConflict={onDecideConflict} />
      )}
    </section>
  );
}
