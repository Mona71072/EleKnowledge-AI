import { Button } from '@/components/ui/Button';
import { CHECK_DECISIONS, type CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import {
  describeRewriteWarning,
  type RewriteConflict,
  type RewriteEvidenceRef,
  type RewriteSectionResult,
} from '@/lib/knowhow-rewrite.mjs';
import { KnowledgeLineDiff } from './KnowledgeLineDiff';

/** 結果の確認ブロックの結果の文言（結果の画面で共通）。 */
const ADD_LABEL: Record<CheckDecision, string> = { confirm: '追加する', skip: '追加しない' };
const APPLY_LABEL: Record<CheckDecision, string> = { confirm: '反映する', skip: '反映しない' };
const STATUS_CLASS = 'text-sm font-semibold text-blue-950';

/** 一括照合の結果の質問へ飛ぶページ内リンクの宛先。KnowhowCheckResults の id と合わせる。 */
export const checkQuestionHref = (questionId: string) => `#check-question-${encodeURIComponent(questionId)}`;

function EvidenceLinks({ numbers, refs }: { numbers: readonly number[]; refs: readonly RewriteEvidenceRef[] }) {
  return (
    <ul aria-label="使った根拠" className="list-disc space-y-1 pl-5 text-xs leading-5 text-gray-800">
      {numbers.map((number) => {
        const ref = refs.find((item) => item.number === number);
        return (
          <li key={number}>
            {ref ? <a href={checkQuestionHref(ref.questionId)} className="break-words text-blue-800 underline">根拠 {number}: {ref.question}</a> : `根拠 ${number}`}
          </li>
        );
      })}
    </ul>
  );
}

function DecisionButtons({ decision, labels, choices, onChange }: {
  decision: CheckDecision | undefined;
  labels: Record<CheckDecision, string>;
  choices: readonly [string, string];
  onChange: (decision: CheckDecision | null) => void;
}) {
  const choose = (value: CheckDecision) => onChange(decision === value ? null : value);
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button type="button" size="sm" variant={decision === CHECK_DECISIONS.confirm ? 'primary' : 'outline'}
        aria-pressed={decision === CHECK_DECISIONS.confirm} onClick={() => choose(CHECK_DECISIONS.confirm)}>{choices[0]}</Button>
      <Button type="button" size="sm" variant={decision === CHECK_DECISIONS.skip ? 'primary' : 'outline'}
        aria-pressed={decision === CHECK_DECISIONS.skip} onClick={() => choose(CHECK_DECISIONS.skip)}>{choices[1]}</Button>
      <span className={STATUS_CLASS}>{decision ? `確認済み: ${labels[decision]}` : '未確認'}</span>
    </div>
  );
}

type SectionProps = {
  section: RewriteSectionResult;
  refs: readonly RewriteEvidenceRef[];
  decision: CheckDecision | undefined;
  onDecide: (decision: CheckDecision | null) => void;
};

function ChangedSection({ section, refs, decision, onDecide }: SectionProps) {
  const warned = section.warnings.length > 0;
  return (
    <article aria-label={`${section.heading}の書き換え案`} className={`min-w-0 space-y-3 rounded-lg border p-3 sm:p-4 ${warned ? 'border-amber-400 bg-amber-50' : 'border-gray-200'}`}>
      <h4 className="break-words text-sm font-semibold text-gray-950">{section.heading}</h4>
      {warned && (
        <ul aria-label="警告" className="list-disc space-y-1 pl-5 text-sm font-semibold text-amber-950">
          {section.warnings.map((warning, index) => <li key={index}>{describeRewriteWarning(warning)}</li>)}
        </ul>
      )}
      <KnowledgeLineDiff before={section.baseBody ?? ''} after={section.body ?? ''} label={`${section.heading}の変更前後`} inlineHighlight />
      {section.reason && <p className="break-words text-sm leading-6 text-gray-900">変更理由: {section.reason}</p>}
      <EvidenceLinks numbers={section.evidence} refs={refs} />
      <DecisionButtons decision={decision} labels={APPLY_LABEL} choices={['確認して反映する', '反映しない']} onChange={onDecide} />
    </article>
  );
}

/** 節ごとの結果。変更あり・変更なし・不採用で見せ方を変える。 */
export function RewriteSectionCard(props: SectionProps) {
  const { section } = props;
  if (section.status === 'changed') return <ChangedSection {...props} />;
  return (
    <article aria-label={`${section.heading}の結果`} className="min-w-0 space-y-1 rounded-lg border border-gray-200 bg-gray-50 p-3">
      <h4 className="break-words text-sm font-semibold text-gray-950">{section.heading}</h4>
      {section.status === 'unchanged'
        ? <p className="text-sm text-gray-700">変更なし</p>
        : <p className="break-words text-sm text-red-900">検査で不採用（{section.warnings.map(describeRewriteWarning).join('／')}）</p>}
    </article>
  );
}

type ConflictProps = {
  conflicts: readonly RewriteConflict[];
  refs: readonly RewriteEvidenceRef[];
  canAdd: boolean;
  decisions: Readonly<Record<number, CheckDecision | undefined>>;
  onDecide: (index: number, decision: CheckDecision | null) => void;
};

/** カードと確認済みの根拠の食い違い。本文は変えず、「未確認事項」へ要確認の1行を足すかを選ぶ。 */
export function RewriteConflicts({ conflicts, refs, canAdd, decisions, onDecide }: ConflictProps) {
  if (!conflicts.length) return null;
  return (
    <section aria-label="カードと根拠の食い違い" className="min-w-0 space-y-3 rounded-lg border border-red-200 bg-red-50 p-3 sm:p-4">
      <h4 className="text-sm font-semibold text-red-950">カードと根拠の食い違い</h4>
      {!canAdd && <p className="text-xs leading-5 text-red-950">カードに「未確認事項」の節が無い（または対象外の）ため、追加できません。</p>}
      {conflicts.map((conflict, index) => (
        <div key={index} className="min-w-0 space-y-2 border-t border-red-200 pt-2 first:border-t-0 first:pt-0">
          <p className="break-words text-sm leading-6 text-gray-950">{conflict.heading ? `【${conflict.heading}】` : ''}{conflict.description}</p>
          <EvidenceLinks numbers={conflict.evidence} refs={refs} />
          {canAdd && (
            <DecisionButtons decision={decisions[index]} labels={ADD_LABEL} choices={['未確認事項に追加する', '追加しない']} onChange={(decision) => onDecide(index, decision)} />
          )}
        </div>
      ))}
    </section>
  );
}
