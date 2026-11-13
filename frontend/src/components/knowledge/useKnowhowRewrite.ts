import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { getIdToken } from '@/lib/auth-helpers';
import type { CheckDecision } from '@/lib/knowhow-card-proposal.mjs';
import { requestKnowhowRewrite, rewriteFailureMessage } from '@/lib/knowhow-rewrite-client.mjs';
import { buildAcceptedRewrites, type RewritePlan } from '@/lib/knowhow-rewrite.mjs';
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
  }, [phase]);

  useEffect(() => {
    if (phase !== 'idle' && state.key !== key) discard('本文の対象の節または確認済みの根拠が変わったため、作った案を破棄しました。');
  }, [key, phase, state.key, discard]);

  const finish = (token: number, own: AbortController, view: RewriteView) => {
    if (controller.current === own) controller.current = null;
    if (mounted.current && guard.current.isLatest(token)) setState((prev) => ({ ...prev, view }));
  };

  const run = () => {
    const { request, evidenceRefs } = plan;
    if (!request || controller.current) return;
    const own = new AbortController();
    controller.current = own;
    const token = guard.current.begin();
    setNote('');
    setDecisions({});
    setConflictDecisions({});
    setState({ view: { phase: 'loading' }, key, requestBody: body });
    requestKnowhowRewrite({ baseUrl: process.env.NEXT_PUBLIC_RAG_API_URL || '', getToken: getIdToken, request, signal: own.signal })
      .then(
        (proposal) => finish(token, own, { phase: 'ready', proposal, evidenceRefs }),
        (error: unknown) => finish(token, own, { phase: 'error', message: rewriteFailureMessage(error) }),
      );
  };

  const accepted = useMemo(
    () => (state.view.phase === 'ready' ? buildAcceptedRewrites(state.view.proposal, decisions, conflictDecisions) : []),
    [state.view, decisions, conflictDecisions],
  );

  return {
    view: state.view,
    decisions,
    conflictDecisions,
    note,
    accepted,
    /** 案を作った時点の本文。節が編集されたかの判定に使う。 */
    expectedBody: state.requestBody,
    run,
    cancel: () => controller.current?.abort(),
    discard,
    decide: (heading: string, decision: CheckDecision | null) =>
      setDecisions((prev) => (decision ? { ...prev, [heading]: decision } : without(prev, heading))),
    decideConflict: (index: number, decision: CheckDecision | null) =>
      setConflictDecisions((prev) => (decision ? { ...prev, [index]: decision } : without(prev, index))),
  };
}
