import { Button } from '@/components/ui/Button';
import { buildCheckProposal, CHECK_DECISIONS, classifyProposalEvidence, formatCheckDate, summarizeCheckDecisions, type CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import { summarizeCheckRun, type CheckRunSnapshot, type CheckTaskState } from '@/lib/knowhow-check-runner.mjs';
import type { CheckQuestion, CheckTarget } from '@/lib/knowhow-card-check.mjs';
import type { ResearchAnswer } from '@/lib/knowledge-research.mjs';
import { ResearchResultLane } from './ResearchResultLane';

export type KnowhowCheckTask = { id: string; questionId: string; mode: CheckTarget; query: string };
export type KnowhowCheckSnapshot = CheckRunSnapshot<KnowhowCheckTask, ResearchAnswer>;
type Result = CheckTaskState<KnowhowCheckTask, ResearchAnswer>;

/** AI の回答に付ける注記。確認は人の作業で、AI の結果はそのままカードに入れない。 */
export const AI_ANSWER_NOTICE = 'AI が KB を検索した結果です。出典を確認してから追記してください。';

/** Build a note once each requested lane has returned an answer. */
export function proposalForQuestion(question: CheckQuestion, tasks: readonly Result[]) {
  if (!tasks.length || tasks.length !== question.targets.length || tasks.some((task) => !task.result)) return null;
  const technical = tasks.find((task) => task.mode === 'normal')?.result;
  const law = tasks.find((task) => task.mode === 'law')?.result;
  const latestReceivedAt = [technical, law].flatMap((answer) => answer ? [answer.receivedAt] : []).sort().at(-1);
  const checkedOn = formatCheckDate(new Date(latestReceivedAt ?? ''));
  return {
    question: question.text,
    checkedOn,
    evidence: classifyProposalEvidence({ technical, law }),
    markdown: buildCheckProposal({ question: question.text, checkedOn, technical, law }),
  };
}

type Props = {
  questions: CheckQuestion[];
  snapshot: KnowhowCheckSnapshot;
  decisions: Readonly<Record<string, CheckDecision | undefined>>;
  onDecide: (id: string, decision: CheckDecision | null) => void;
  onRetry: (taskId: string) => void;
  onCancel: () => void;
};

function CheckLane({ task, onRetry }: { task: Result; onRetry: (taskId: string) => void }) {
  const state = task.result
    ? { status: 'success' as const, answer: task.result, contextKey: null, targetLabel: '', searchId: 0 }
    : task.status === 'failed'
      ? { status: 'error' as const, message: task.failure || '照合に失敗しました。' }
      : { status: task.status === 'cancelled' ? 'cancelled' as const : task.status === 'running' ? 'loading' as const : 'queued' as const };
  return (
    <div className="min-w-0 space-y-2">
      <ResearchResultLane mode={task.mode} state={state} />
      {(task.status === 'failed' || task.status === 'cancelled') && (
        <Button type="button" size="sm" variant="outline" onClick={() => onRetry(task.id)}>再試行</Button>
      )}
    </div>
  );
}

const DECISION_LABEL: Record<CheckDecision, string> = { confirm: '追記する', skip: '追記しない' };

function DecisionPanel({ id, evidence, checkedOn, decision, onDecide }: {
  id: string;
  evidence: 'sourced' | 'not_found' | 'no_source';
  checkedOn: string;
  decision: CheckDecision | undefined;
  onDecide: Props['onDecide'];
}) {
  const choose = (value: CheckDecision) => onDecide(id, decision === value ? null : value);
  return (
    <div className="space-y-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
      <p className="text-xs leading-5 text-blue-950">{AI_ANSWER_NOTICE}</p>
      <p className="text-xs leading-5 text-blue-950">
        {evidence === 'sourced'
          ? '出典を確認して追記する場合、確認日と「管理者が出典を確認」の記録つきで「KB確認に基づく追記」に入ります。'
          : evidence === 'not_found'
            ? `出典がありません。確認すると「KB に該当資料なし（${checkedOn}）」の記録として入ります。未確認事項の解消ではなく、確認した記録です。`
            : `根拠になる出典が見つかりませんでした（聞き返し・出典なしの回答を含む）。確認すると「根拠になる出典が見つからなかった（聞き返し・出典なしの回答を含む）（${checkedOn}）」の記録として入ります。確認した記録で、未確認事項の解消ではありません。`}
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" size="sm" variant={decision === CHECK_DECISIONS.confirm ? 'primary' : 'outline'}
          aria-pressed={decision === CHECK_DECISIONS.confirm} onClick={() => choose(CHECK_DECISIONS.confirm)}>確認して追記する</Button>
        <Button type="button" size="sm" variant={decision === CHECK_DECISIONS.skip ? 'primary' : 'outline'}
          aria-pressed={decision === CHECK_DECISIONS.skip} onClick={() => choose(CHECK_DECISIONS.skip)}>追記しない</Button>
        <span className="text-sm font-semibold text-blue-950">{decision ? `確認済み: ${DECISION_LABEL[decision]}` : '未確認'}</span>
      </div>
    </div>
  );
}

export function KnowhowCheckResults({ questions, snapshot, decisions, onDecide, onRetry, onCancel }: Props) {
  const { total, done, failed, cancelled, finished } = summarizeCheckRun(snapshot);
  const proposals = new Map(questions.flatMap((question) => {
    const proposal = proposalForQuestion(question, snapshot.tasks.filter((task) => task.questionId === question.id));
    return proposal ? [[question.id, proposal] as const] : [];
  }));
  const counts = summarizeCheckDecisions(Array.from(proposals.keys()), decisions);
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-semibold text-gray-950">照合結果と追記案</h3>
          <p role="status" className="mt-1 text-sm text-gray-700">{finished} / {total} 件 · 成功 {done} · 失敗 {failed} · 中止 {cancelled}</p>
        </div>
        {snapshot.running && <Button type="button" variant="outline" onClick={onCancel}>中止</Button>}
      </div>
      {counts.total > 0 && (
        <p role="status" className="rounded-lg bg-gray-50 p-3 text-sm text-gray-900">
          {`${counts.total}件中 ${counts.confirmed}件を追記・${counts.skipped}件を追記しない・${counts.pending}件が未確認。未確認のものはカードに入りません。`}
        </p>
      )}
      <progress aria-label="照合の進捗" className="h-2 w-full accent-blue-700" max={total} value={finished} />
      {questions.map((question) => {
        const tasks = snapshot.tasks.filter((task) => task.questionId === question.id);
        const proposal = proposals.get(question.id);
        return (
          <section key={question.id} className="min-w-0 space-y-3 rounded-lg border border-gray-200 p-3 sm:p-4">
            <h4 className="break-words text-sm font-semibold text-gray-950">{question.text}</h4>
            <div className="grid min-w-0 grid-cols-1 gap-3 xl:grid-cols-2">
              {tasks.map((task) => <CheckLane key={task.id} task={task} onRetry={onRetry} />)}
            </div>
            {proposal && (
              <>
                <DecisionPanel id={question.id} evidence={proposal.evidence} checkedOn={proposal.checkedOn}
                  decision={decisions[question.id]} onDecide={onDecide} />
                <details>
                  <summary className="cursor-pointer text-sm text-blue-950">追記される内容を読む</summary>
                  <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-md bg-white p-3 text-xs leading-5 text-gray-900">{proposal.markdown}</pre>
                </details>
              </>
            )}
          </section>
        );
      })}
    </div>
  );
}
