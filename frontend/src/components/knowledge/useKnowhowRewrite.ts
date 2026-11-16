import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getIdToken } from '@/lib/auth-helpers';
import type { CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import { requestKnowhowRewrite, rewriteFailureMessage } from '@/lib/knowhow-rewrite-client.mjs';
import { buildAcceptedRewrites, buildRewriteHistory, buildRewriteRetryRequest, type RewriteHistoryEntry, type RewritePlan, type RewriteProposal } from '@/lib/knowhow-rewrite.mjs';
import { createLatestGuard } from '@/lib/latest-request.mjs';
import type { RewriteView } from './KnowhowRewritePanel';

type State = { view: RewriteView; key: string; requestBody: string };
const IDLE: State = { view: { phase: 'idle' }, key: '', requestBody: '' };

/** 案が前提にした材料（カード・対象の節・根拠）。変わったら案は古い。context は前提に含めない。 */
function planKey(plan: RewritePlan): string {
  const { request } = plan;
  return request ? JSON.stringify([request.knowledgeId, request.cardVersion, request.targets, request.evidence]) : '';
}

const without = <T,>(record: Record<string | number, T>, key: string | number) => {
  const { [key]: _removed, ...rest } = record;
  return rest;
};

/**
 * 書き換え案の作成・確認の状態。二重送信を防ぎ、古い応答とアンマウント後の更新を捨て、
 * 前提（根拠・対象の節）が変わったら案を破棄する。案も本文も保存しない（state のみ）。
 */
export function useKnowhowRewrite(plan: RewritePlan, body: string) {
  const [state, setState] = useState<State>(IDLE);
  const [decisions, setDecisions] = useState<Record<string, CheckDecision | undefined>>({});
  const [conflictDecisions, setConflictDecisions] = useState<Record<number, CheckDecision | undefined>>({});
  const [note, setNote] = useState('');
  const [history, setHistory] = useState<RewriteHistoryEntry[]>([]);
  const [selectedHistoryIndex, setSelectedHistoryIndex] = useState(-1);
  const [instruction, setInstruction] = useState('');
  const guard = useRef(createLatestGuard());
  const controller = useRef<AbortController | null>(null);
  const mounted = useRef(false);
  const key = planKey(plan);
  const phase = state.view.phase;

  useEffect(() => {
    mounted.current = true;
    const latest = guard.current;
    return () => {
      mounted.current = false;
      latest.invalidate();
      controller.current?.abort();
      controller.current = null;
    };
  }, []);

  const discard = useCallback((reason = '') => {
    guard.current.invalidate();
    controller.current?.abort();
    controller.current = null;
    setNote(phase === 'loading' || phase === 'ready' ? reason : '');
    setState(IDLE);
    setDecisions({});
    setConflictDecisions({});
    setHistory([]);
    setSelectedHistoryIndex(-1);
    setInstruction('');
  }, [phase]);

  useEffect(() => {
    if (phase !== 'idle' && state.key !== key) discard('本文の対象の節または確認済みの根拠が変わったため、作った案を破棄しました。');
  }, [key, phase, state.key, discard]);

  const finish = (token: number, own: AbortController, view: RewriteView) => {
    if (controller.current === own) controller.current = null;
    if (mounted.current && guard.current.isLatest(token)) setState((prev) => ({ ...prev, view }));
  };

  const start = (request: NonNullable<RewritePlan['request']>, prompt: string | null, previousProposal?: RewriteProposal) => {
    const { evidenceRefs } = plan;
    if (controller.current) return;
    const own = new AbortController();
    controller.current = own;
    const token = guard.current.begin();
    setNote('');
    setDecisions({});
    setConflictDecisions({});
    setState((previous) => ({ ...previous, view: { phase: 'loading' }, key, requestBody: body }));
    const execute = prompt === null
      ? Promise.resolve(request)
      : previousProposal
        ? buildRewriteRetryRequest({ request, proposal: previousProposal, instruction: prompt })
        : Promise.reject(new Error('直前案を確認できません。'));
    execute.then((prepared) => requestKnowhowRewrite({ baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '', getToken: getIdToken, request: prepared, signal: own.signal }))
      .then(
        (proposal) => {
          const nextHistory = buildRewriteHistory([...(prompt === null ? [] : history), { instruction: prompt ?? '', proposal, evidenceRefs }]);
          setHistory(nextHistory);
          setSelectedHistoryIndex(nextHistory.length - 1);
          setInstruction('');
          finish(token, own, { phase: 'ready', proposal, evidenceRefs });
        },
        (error: unknown) => finish(token, own, { phase: 'error', message: rewriteFailureMessage(error) }),
      );
  };

  const run = () => {
    const { request } = plan;
    if (!request || controller.current) return;
    setHistory([]);
    setSelectedHistoryIndex(-1);
    start(request, null);
  };

  const retry = () => {
    const { request } = plan;
    const prompt = instruction;
    const previousProposal = history.at(-1)?.proposal;
    if (!request || !prompt.trim() || !previousProposal || controller.current || request.evidence.some(({ lane }) => lane === 'field')) return;
    start(request, prompt, previousProposal);
  };

  const selectHistory = (index: number) => {
    const entry = history[index];
    if (!entry || controller.current) return;
    setSelectedHistoryIndex(index);
    setDecisions({});
    setConflictDecisions({});
    setState({ view: { phase: 'ready', proposal: entry.proposal, evidenceRefs: entry.evidenceRefs }, key, requestBody: body });
  };

  const accepted = useMemo(
    () => (state.view.phase === 'ready' ? buildAcceptedRewrites(state.view.proposal, decisions, conflictDecisions) : []),
    [state.view, decisions, conflictDecisions],
  );

  return {
    view: state.view,
    history,
    selectedHistoryIndex,
    instruction,
    decisions,
    conflictDecisions,
    note,
    accepted,
    /** 案を作った時点の本文。節が編集されたかの判定に使う。 */
    expectedBody: state.requestBody,
    run,
    retry,
    selectHistory,
    setInstruction,
    cancel: () => controller.current?.abort(),
    discard,
    decide: (heading: string, decision: CheckDecision | null) =>
      setDecisions((prev) => (decision ? { ...prev, [heading]: decision } : without(prev, heading))),
    decideConflict: (index: number, decision: CheckDecision | null) =>
      setConflictDecisions((prev) => (decision ? { ...prev, [index]: decision } : without(prev, index))),
  };
}
