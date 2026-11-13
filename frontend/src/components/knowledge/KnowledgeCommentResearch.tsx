'use client';

import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { getIdToken } from '@/lib/auth-helpers';
import { buildCommentResearchQuery, buildConfirmedCommentBody } from '@/lib/knowledge-comment-review.mjs';
import { classifyCheckAnswer, type CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import { queryKnowledgeSource, type KnowledgeResearchMode, type ResearchAnswer } from '@/lib/knowledge-research.mjs';
import type { KnowledgeReviewComment } from '@/lib/knowledge-workbench.mjs';
import { CommentCandidate } from './KnowledgeCommentCandidate';
import { KnowledgeLineDiff } from './KnowledgeLineDiff';
import { knowledgeResearchErrorMessage, ResearchResultLane, type LaneState } from './ResearchResultLane';

type Props = {
  body: string;
  title: string;
  modelWords: readonly string[];
  comment: KnowledgeReviewComment;
  busy: boolean;
  onApply: (id: string, expectedBody: string, body: string) => boolean;
};

const MODES = ['normal', 'law'] as const;
const LABELS = { normal: '技術KB', law: '法令KB' };
const INITIAL_LANES: Record<KnowledgeResearchMode, LaneState> = { normal: { status: 'idle' }, law: { status: 'idle' } };

type Choice = { decision: CheckDecision; text: string };
type Choices = Partial<Record<KnowledgeResearchMode, Choice>>;

/** 差分を作る。作れないとき（節・コードフェンス・長さの問題）は body が null。 */
function buildPreview(body: string, sectionId: string, entries: Parameters<typeof buildConfirmedCommentBody>[2]) {
  try {
    return buildConfirmedCommentBody(body, sectionId, entries);
  } catch {
    return { body: null, applied: 0 };
  }
}

export function KnowledgeCommentResearch({ body, title, modelWords, comment, busy, onApply }: Props) {
  const [lanes, setLanes] = useState(INITIAL_LANES);
  const [run, setRun] = useState(0);
  const [choices, setChoices] = useState<Choices>({});
  const [error, setError] = useState('');
  const controller = useRef<AbortController | null>(null);
  const running = MODES.some((mode) => lanes[mode].status === 'loading');
  const query = buildCommentResearchQuery({ title, sectionLabel: comment.sectionLabel, comment: comment.text, modelWords });

  useEffect(() => () => {
    controller.current?.abort();
    controller.current = null;
  }, []);

  async function search() {
    if (controller.current || busy) return;
    const request = new AbortController();
    controller.current = request;
    setRun((current) => current + 1);
    setLanes({ normal: { status: 'loading' }, law: { status: 'loading' } });
    setChoices({});
    setError('');
    await Promise.all(MODES.map(async (mode) => {
      let state: LaneState;
      try {
        const answer = await queryKnowledgeSource({
          baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '',
          getToken: getIdToken, mode, query, signal: request.signal,
        });
        state = { status: 'success', answer, contextKey: null, targetLabel: '', searchId: run + 1 };
      } catch (reason) {
        state = { status: 'error', message: knowledgeResearchErrorMessage(reason, mode) };
      }
      if (controller.current === request && !request.signal.aborted) {
        setLanes((current) => ({ ...current, [mode]: state }));
      }
    }));
    if (controller.current === request) controller.current = null;
  }

  function cancel() {
    const request = controller.current;
    controller.current = null;
    request?.abort();
    setLanes((current) => ({
      normal: current.normal.status === 'loading' ? { status: 'cancelled' } : current.normal,
      law: current.law.status === 'loading' ? { status: 'cancelled' } : current.law,
    }));
  }

  function decide(mode: KnowledgeResearchMode, decision: CheckDecision | null, text: string) {
    setError('');
    setChoices(({ [mode]: _previous, ...rest }) => (decision ? { ...rest, [mode]: { decision, text } } : rest));
  }

  function forget(mode: KnowledgeResearchMode) {
    setChoices(({ [mode]: _previous, ...rest }) => rest);
  }

  // 管理者が「確認して追記する」を選んだ追記案だけを本文に足す。未確認・追記しないは入らない。
  const entries = MODES.flatMap((mode) => {
    const state = lanes[mode];
    const choice = choices[mode];
    return state.status === 'success' && choice ? [{ answer: state.answer, text: choice.text, decision: choice.decision }] : [];
  });
  const confirmed = buildPreview(body, comment.sectionId, entries);
  const preview = confirmed.body !== null && confirmed.applied > 0 ? confirmed.body : null;
  const confirmedCount = entries.filter((entry) => entry.decision === 'confirm').length;
  const pendingCount = MODES.filter((mode) => {
    const state = lanes[mode];
    return state.status === 'success' && classifyCheckAnswer(state.answer) === 'found' && !choices[mode];
  }).length;

  return (
    <div className="min-w-0 space-y-4 border-t border-gray-200 pt-4">
      <div className="space-y-2">
        <p className="text-sm font-semibold text-gray-900">AIに送る検索文</p>
        <p className="whitespace-pre-wrap break-words rounded-lg bg-gray-50 p-3 text-sm text-gray-800">{query}</p>
        <p className="text-xs text-gray-700">この検索文を技術KB・法令KBに1回ずつ送り、既存の検索履歴に保存される場合があります。</p>
        <p className="text-xs text-gray-700">OneNote・Listsの原資料は、上の「技術資料との照合」で確認できます。</p>
        <div className="flex flex-wrap gap-2">
          <Button type="button" disabled={busy || running} onClick={search}>AIで技術KB・法令KBを再確認</Button>
          {running && <Button type="button" variant="outline" onClick={cancel}>再確認を中止</Button>}
        </div>
      </div>
      {run > 0 && (
        <div className="grid min-w-0 grid-cols-1 gap-3 xl:grid-cols-2">
          {MODES.map((mode) => {
            const state = lanes[mode];
            const answer = state.status === 'success' ? state.answer : null;
            return (
              <div key={mode} role="group" aria-label={`${LABELS[mode]}の照会と追記案`} className="min-w-0 space-y-2">
                <ResearchResultLane mode={mode} state={state} />
                {answer && classifyCheckAnswer(answer) === 'found' && (
                  <CommentCandidate key={run} answer={answer} decision={choices[mode]?.decision}
                    onEdit={() => forget(mode)}
                    onDecide={(decision, text) => decide(mode, decision, text)} />
                )}
                {answer && classifyCheckAnswer(answer) === 'no_source' && <p className="text-sm text-amber-900">確認できる出典がないため、追記案は作成できません。</p>}
              </div>
            );
          })}
        </div>
      )}
      {run > 0 && !running && (pendingCount > 0 || confirmedCount > 0) && (
        <p role="status" className="rounded-lg bg-gray-50 p-3 text-sm text-gray-900">
          {confirmedCount > 0
            ? `「確認して追記する」を選んだ ${confirmedCount} 件だけが「${comment.sectionLabel}」に入ります。`
            : '「確認して追記する」を選んだ追記案が無いため、差分は作れません。出典を確認して選んでください。'}
          {pendingCount > 0 && `${pendingCount}件が未確認です。未確認のものはカードに入りません。`}
        </p>
      )}
      {confirmed.body === null && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-900">追記案の差分を作れませんでした。対象の節、コードフェンス、追記案の長さを確認してください。</p>}
      {preview !== null && (
        <div className="min-w-0 space-y-3 border-t border-gray-200 pt-4">
          <h3 className="text-sm font-semibold text-gray-950">「{comment.sectionLabel}」への追記前後</h3>
          <KnowledgeLineDiff before={body} after={preview} label="追記前後の差分" />
          <Button type="button" disabled={busy || running} onClick={() => {
            if (!onApply(comment.id, body, preview)) setError('反映できませんでした。本文と追記内容を確認してください。');
          }}>確認した追記を対象の節に反映</Button>
        </div>
      )}
      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-900">{error}</p>}
    </div>
  );
}
