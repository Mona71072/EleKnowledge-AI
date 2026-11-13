'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { MAX_COMMENT_ADDITION_CHARS } from '@/lib/knowledge-comment-review.mjs';
import { CHECK_DECISIONS, type CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import type { ResearchAnswer } from '@/lib/knowledge-research.mjs';
import { AI_ANSWER_NOTICE } from './KnowhowCheckResults';

const LABELS = { normal: '技術KB', law: '法令KB' };
const DECISION_LABEL: Record<CheckDecision, string> = { confirm: '追記する', skip: '追記しない' };

type Props = {
  answer: ResearchAnswer;
  decision: CheckDecision | undefined;
  /** 同じ選択をもう一度押すと null（未確認に戻す）。text は選んだ時点の編集後の追記案。 */
  onDecide: (decision: CheckDecision | null, text: string) => void;
  /** 追記案を編集したとき。確認結果は未確認に戻る。 */
  onEdit: () => void;
};

/** コメントへの AI の追記案。管理者が出典を確認して「確認して追記する」を選んだものだけがカードに入る。 */
export function CommentCandidate({ answer, decision, onDecide, onEdit }: Props) {
  const label = LABELS[answer.mode];
  const [draft, setDraft] = useState(answer.content);
  const tooLong = Array.from(draft).length > MAX_COMMENT_ADDITION_CHARS;
  const blocked = tooLong || !draft.trim();
  const choose = (value: CheckDecision) => onDecide(decision === value ? null : value, draft);
  return (
    <div className="space-y-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
      <label className="block text-sm font-semibold text-gray-950">
        {label}の追記案
        <textarea aria-label={`${label}の追記案`} value={draft} onChange={(event) => {
          setDraft(event.target.value);
          onEdit();
        }}
          rows={6} className="mt-2 block w-full resize-y rounded-lg border border-gray-300 bg-white p-2 text-sm font-normal" />
      </label>
      {tooLong && <p className="text-sm text-amber-900">追記案を{MAX_COMMENT_ADDITION_CHARS.toLocaleString('ja-JP')}文字以内に編集してください。</p>}
      <p className="text-xs leading-5 text-blue-950">{AI_ANSWER_NOTICE}</p>
      <p className="text-xs leading-5 text-blue-950">出典を確認して追記する場合、根拠資料と確認日つきの「管理者が出典を確認」の行とともに、選んだ節に入ります。</p>
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" size="sm" variant={decision === CHECK_DECISIONS.confirm ? 'primary' : 'outline'} disabled={blocked}
          aria-pressed={decision === CHECK_DECISIONS.confirm} onClick={() => choose(CHECK_DECISIONS.confirm)}>確認して追記する</Button>
        <Button type="button" size="sm" variant={decision === CHECK_DECISIONS.skip ? 'primary' : 'outline'}
          aria-pressed={decision === CHECK_DECISIONS.skip} onClick={() => choose(CHECK_DECISIONS.skip)}>追記しない</Button>
        <span className="text-sm font-semibold text-blue-950">{decision ? `確認済み: ${DECISION_LABEL[decision]}` : '未確認'}</span>
      </div>
    </div>
  );
}
