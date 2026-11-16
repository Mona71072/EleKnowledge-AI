import { useEffect, useMemo, useRef, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { getIdToken } from '@/lib/auth-helpers';
import { buildCheckQuestions, type CheckQuestion } from '@/lib/knowhow-card-check.mjs';
import { CHECK_DECISIONS, type CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import { composeCardEdits, buildRewriteEvidence, buildRewriteRequest, isRewriteEnabled, type RewritePlan } from '@/lib/knowhow-rewrite.mjs';
import { createCheckRunner, type CheckRunner } from '@/lib/knowhow-check-runner.mjs';
import { queryKnowledgeSource, KnowledgeResearchError, type ResearchAnswer } from '@/lib/knowledge-research.mjs';
import { KnowhowCheckQuestions } from './KnowhowCheckQuestions';
import { KnowhowCheckResults, proposalForQuestion, type KnowhowCheckSnapshot, type KnowhowCheckTask } from './KnowhowCheckResults';
import { KnowhowRewritePanel } from './KnowhowRewritePanel';
import { KnowledgeLineDiff } from './KnowledgeLineDiff';
import { knowledgeResearchErrorMessage } from './ResearchResultLane';
import { useKnowhowRewrite } from './useKnowhowRewrite';

type Props = {
  frontmatter: Record<string, unknown>;
  originalBody: string;
  body: string;
  /** 取り込めたら true。最新の本文に差し込んだ結果（expectedBody はその差し込み前の本文）を渡す。 */
  onAdopt: (expectedBody: string, revisedBody: string, applied: number, skipped: number, rewritten: number) => boolean;
  busy: boolean;
};

type Preview = { before: string; after: string; applied: number; skipped: number; rewritten: number };

const NO_REWRITE_PLAN: RewritePlan = { request: null, evidenceRefs: [], evidenceOmitted: 0, excluded: [], blocker: '' };
const STALE_NOTE = '本文が変わったため、もう一度案を作ってください。';
const DECISION_CHANGED_NOTE = '確認の選択が変わったため、作った案を破棄しました。';
const RETRY_NOTE = '照合をやり直したため、作った案を破棄しました。';

const steps = ['質問を確認', '照合', '確認する', '差分を確認'];

export function KnowhowCardCheck({ frontmatter, originalBody, body, onAdopt, busy }: Props) {
  const [questions, setQuestions] = useState(() => buildCheckQuestions({ frontmatter, body }));
  const [submitted, setSubmitted] = useState<CheckQuestion[]>([]);
  const [snapshot, setSnapshot] = useState<KnowhowCheckSnapshot | null>(null);
  const [decisions, setDecisions] = useState<Record<string, CheckDecision | undefined>>({});
  const [preview, setPreview] = useState<Preview | null>(null);
  // 照合を始めた時点の本文。本文がその後変わっても一括照合は作り直さず、差し込みは最新の本文に対して行う。
  const [startedBody, setStartedBody] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [previewError, setPreviewError] = useState('');
  const runner = useRef<CheckRunner<KnowhowCheckTask, ResearchAnswer> | null>(null);
  const rewriteEnabled = isRewriteEnabled(process.env.NEXT_PUBLIC_ENABLE_KNOWHOW_REWRITE);
  const rewritePlan = useMemo(() => (rewriteEnabled && snapshot
    ? buildRewriteRequest({ frontmatter, body, evidence: buildRewriteEvidence({ questions: submitted, tasks: snapshot.tasks, decisions }) })
    : NO_REWRITE_PLAN), [rewriteEnabled, snapshot, frontmatter, body, submitted, decisions]);
  const rewrite = useKnowhowRewrite(rewritePlan, body);

  useEffect(() => () => {
    runner.current?.dispose();
    runner.current = null;
  }, []);

  const start = () => {
    if (busy || runner.current) return;
    const active = questions.filter((question) => question.selected && question.text.trim() && question.targets.length);
    if (!active.length) return;
    const tasks = active.flatMap((question) => question.targets.map((mode) => ({
      id: `${question.id}-${mode}`, questionId: question.id, mode, query: question.text.trim(),
    })));
    setSubmitted(active);
    setStartedBody(body);
    setMessage('');
    rewrite.discard();
    runner.current = createCheckRunner({
      tasks,
      execute: (task, signal) => queryKnowledgeSource({
        baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
        getToken: getIdToken,
        mode: task.mode,
        query: task.query,
        signal,
      }),
      describeFailure: (error, task) => knowledgeResearchErrorMessage(error, task.mode),
      isFatal: (error) => error instanceof KnowledgeResearchError && ['auth', 'config'].includes(error.code),
      onUpdate: setSnapshot,
    });
    runner.current.start();
  };

  const reset = () => {
    runner.current?.dispose();
    runner.current = null;
    setSnapshot(null);
    setStartedBody(null);
    setDecisions({});
    setPreview(null);
    setMessage('');
    setPreviewError('');
    rewrite.discard();
  };

  const clearPreview = () => {
    setPreview(null);
    setMessage('');
    setPreviewError('');
  };

  const showPreview = () => {
    setPreview(null);
    if (!snapshot || snapshot.running || busy) return;
    const proposals = submitted.filter((question) => decisions[question.id] === CHECK_DECISIONS.confirm).flatMap((question) => {
      const proposal = proposalForQuestion(question, snapshot.tasks.filter((task) => task.questionId === question.id));
      return proposal ? [proposal] : [];
    });
    setMessage('');
    setPreviewError('');
    try {
      const result = composeCardEdits(body, { rewrites: rewrite.accepted, expectedBody: rewrite.expectedBody, proposals });
      const stale = result.stale.length ? `「${result.stale.join('」「')}」は${STALE_NOTE}` : '';
      if (result.applied + result.rewritten === 0) {
        setMessage(stale || '確認して追記する追記案は、すでに本文にあります。');
        return;
      }
      if (stale) setMessage(stale);
      setPreview({ before: body, after: result.markdown, applied: result.applied, skipped: result.skipped, rewritten: result.rewritten });
    } catch {
      setPreviewError('追記位置を判定できませんでした。Markdownのコードフェンスが閉じているか確認してください。');
    }
  };

  const adopt = () => {
    if (!preview || busy) return;
    if (preview.before !== body) return;
    if (onAdopt(preview.before, preview.after, preview.applied, preview.skipped, preview.rewritten)) reset();
  };

  const bodyChanged = snapshot !== null && startedBody !== null && startedBody !== body;
  const previewStale = preview !== null && preview.before !== body;

  const confirmedCount = Object.values(decisions).filter((value) => value === CHECK_DECISIONS.confirm).length;
  const step = preview ? 3 : snapshot?.running ? 1 : snapshot ? 2 : 0;
  return (
    <section aria-label="カードを一括照合" className="min-w-0 space-y-5 rounded-xl border border-blue-200 bg-white p-4 shadow-sm sm:p-5">
      <header className="space-y-2">
        <h2 className="text-lg font-bold text-gray-950">カードを一括照合</h2>
        <p className="text-sm leading-6 text-gray-700">カードから作った質問を技術KB・法令KBで照合し、回答と出典を管理者が確認し、確認して追記するものだけをカードに入れます。</p>
        <ol aria-label="照合の手順" className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
          {steps.map((label, index) => (
            <li key={label} aria-current={step === index ? 'step' : undefined}
              className={step === index ? 'rounded-md bg-blue-100 px-2 py-2 font-semibold text-blue-950' : 'rounded-md bg-gray-100 px-2 py-2 text-gray-700'}>
              {index + 1}. {label}
            </li>
          ))}
        </ol>
      </header>
      {!snapshot ? (
        <KnowhowCheckQuestions questions={questions} onChange={setQuestions} onStart={start} busy={busy} />
      ) : (
        <>
          <KnowhowCheckResults questions={submitted} snapshot={snapshot} decisions={decisions}
            onCancel={() => runner.current?.cancel()}
            onRetry={(id) => {
              if (busy) return;
              const retried = snapshot.tasks.find((task) => task.id === id)?.questionId;
              if (retried) setDecisions(({ [retried]: _discarded, ...rest }) => rest);
              setPreview(null);
              setMessage('');
              setPreviewError('');
              rewrite.discard(RETRY_NOTE);
              runner.current?.retry(id);
            }}
            onDecide={(id, decision) => {
              setDecisions(({ [id]: _previous, ...rest }) => (decision ? { ...rest, [id]: decision } : rest));
              setPreview(null);
              setMessage('');
              setPreviewError('');
              rewrite.discard(DECISION_CHANGED_NOTE);
            }} />
          <KnowhowRewritePanel hasKnowledgeId={typeof frontmatter.knowledge_id === 'string' && frontmatter.knowledge_id !== ''}
            plan={rewritePlan} view={rewrite.view} decisions={rewrite.decisions} conflictDecisions={rewrite.conflictDecisions}
            note={rewrite.note} checking={snapshot.running} busy={busy}
            onRun={() => { clearPreview(); rewrite.run(); }}
            onCancel={() => { clearPreview(); rewrite.cancel(); }}
            onDecide={(heading, decision) => { clearPreview(); rewrite.decide(heading, decision); }}
            onDecideConflict={(index, decision) => { clearPreview(); rewrite.decideConflict(index, decision); }} />
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="outline" disabled={snapshot.running} onClick={reset}>質問の編集に戻る</Button>
            <Button type="button" disabled={snapshot.running || (!confirmedCount && !rewrite.accepted.length) || busy} onClick={showPreview}>差分を確認</Button>
          </div>
          <p className="text-xs leading-5 text-gray-700">
            {confirmedCount
              ? `「確認して追記する」を選んだ ${confirmedCount} 件だけがカードに入ります。未確認・追記しないものは入りません。`
              : '「確認して追記する」を選んだ追記案が無いため、差分は作れません。出典を確認して選んでください。'}
          </p>
        </>
      )}
      {bodyChanged && (
        <p role="status" className="rounded-lg bg-amber-50 p-3 text-sm text-amber-950">本文が変わりました。追記の差し込みは最新の本文に対して行います。照合の結果と確認の選択はそのままです。</p>
      )}
      {previewStale && (
        <p role="status" className="rounded-lg bg-amber-50 p-3 text-sm text-amber-950">本文が変わったため、差分は古くなりました。もう一度「差分を確認」してください。</p>
      )}
      {preview && !previewStale && (
        <section aria-label="採用する追記案の差分" className="min-w-0 space-y-3 border-t border-gray-200 pt-4">
          <h3 className="font-semibold text-gray-950">読み込んだ原文との差分</h3>
          <KnowledgeLineDiff before={originalBody} after={preview.after} />
          <p className="text-xs leading-5 text-gray-700">
            {preview.rewritten ? `「確認して反映する」を選んだ ${preview.rewritten} 節の書き換えと、「確認して追記する」を選んだ追記を、1つの差分にまとめています。` : '「確認して追記する」を選んだ追記だけが入っています。'}保存したMarkdownは下書きになります。
          </p>
          <Button type="button" disabled={busy || (!confirmedCount && !rewrite.accepted.length)} onClick={adopt}>本文に反映</Button>
        </section>
      )}
      {message && <p role="status" className="rounded-lg bg-blue-50 p-3 text-sm text-blue-950">{message}</p>}
      {previewError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-900">{previewError}</p>}
    </section>
  );
}
