import { KnowledgeResearchError } from './knowledge-research.mjs';

const MODES = ['normal', 'law'];
const MAX_QUERY_LENGTH = 2_000;

function chatError(message) {
  return new KnowledgeResearchError('validation', message);
}

function freezeCopy(value) {
  if (Array.isArray(value)) return Object.freeze(value.map(freezeCopy));
  if (!value || typeof value !== 'object') return value;
  const copy = Object.fromEntries(Object.entries(value).map(([key, item]) => [key, freezeCopy(item)]));
  return Object.freeze(copy);
}

function cloneTurn(turn) {
  return Object.freeze({
    id: turn.id,
    query: turn.query,
    normal: Object.freeze({ ...turn.normal, ...(turn.normal.answer ? { answer: freezeCopy(turn.normal.answer) } : {}) }),
    law: Object.freeze({ ...turn.law, ...(turn.law.answer ? { answer: freezeCopy(turn.law.answer) } : {}) }),
  });
}

/**
 * Manage one technical and one law conversation without mixing their server sessions.
 * Failures are treated as ambiguous server state and pause only the affected lane.
 * @param {{querySource:(request:{mode:'normal'|'law',query:string,sessionId?:string,signal:AbortSignal})=>Promise<import('./knowledge-research.mjs').ResearchAnswer>,onChange?:(snapshot:SenpaiChatSnapshot)=>void}} options
 */
export function createSenpaiChat({ querySource, onChange = () => {} }) {
  if (typeof querySource !== 'function') throw chatError('検索サービスの設定を確認してください');

  let turns = [];
  let sessionIds = { normal: null, law: null };
  let pausedReasons = { normal: null, law: null };
  let active = null;
  let running = false;
  let disposed = false;
  let generation = 0;
  let nextTurnId = 1;

  function getSnapshot() {
    return Object.freeze({
      turns: Object.freeze(turns.map(cloneTurn)),
      running,
    });
  }

  function notify() {
    if (disposed) return;
    try {
      onChange(getSnapshot());
    } catch {
      // A view callback must not break the conversation state machine.
    }
  }

  function isCurrent(run) {
    return !disposed && active === run && generation === run.generation;
  }

  function updateLane(run, mode, lane) {
    if (!isCurrent(run)) return;
    turns = turns.map((turn) => turn.id === run.turnId ? { ...turn, [mode]: lane } : turn);
    notify();
  }

  function makeLane(status, message) {
    return { status, ...(message ? { message } : {}) };
  }

  async function runLane(run, mode, query) {
    const priorSessionId = sessionIds[mode];
    try {
      const answer = await querySource({
        mode,
        query,
        ...(priorSessionId ? { sessionId: priorSessionId } : {}),
        signal: run.controller.signal,
      });
      if (!isCurrent(run)) return;
      if (!answer || answer.mode !== mode || typeof answer.sessionId !== 'string'
        || !answer.sessionId.trim() || answer.sessionId.length > 128
        || /[\u0000-\u001f\u007f-\u009f]/u.test(answer.sessionId)
        || (priorSessionId && answer.sessionId !== priorSessionId)) {
        const message = '会話の識別情報を確認できないため、この検索先を一時停止しました。会話をリセットしてください';
        pausedReasons = { ...pausedReasons, [mode]: message };
        updateLane(run, mode, makeLane('paused', message));
        return;
      }
      sessionIds = { ...sessionIds, [mode]: answer.sessionId };
      updateLane(run, mode, { status: 'success', answer });
    } catch (error) {
      if (!isCurrent(run)) return;
      const cancelled = run.controller.signal.aborted || error?.code === 'cancelled';
      const message = error instanceof KnowledgeResearchError
        ? error.message
        : cancelled
          ? '検索を中止しました。続きの会話はリセットして再開してください'
          : '検索に失敗しました。続きの会話はリセットして再開してください';
      pausedReasons = { ...pausedReasons, [mode]: message };
      updateLane(run, mode, makeLane(cancelled ? 'cancelled' : 'error', message));
    }
  }

  function checkSessionCollision(run) {
    if (!isCurrent(run) || !sessionIds.normal || sessionIds.normal !== sessionIds.law) return;
    const message = '技術KBと法令KBの会話識別情報が重複したため、安全のため両方を一時停止しました。会話をリセットしてください';
    pausedReasons = { normal: message, law: message };
    sessionIds = { normal: null, law: null };
    turns = turns.map((turn) => turn.id === run.turnId
      ? { ...turn, normal: makeLane('paused', message), law: makeLane('paused', message) }
      : turn);
    notify();
  }

  async function send(query) {
    if (disposed) return;
    if (running) throw chatError('回答を待ってから、次の質問を送信してください');
    if (typeof query !== 'string' || !query.trim() || Array.from(query.trim()).length > MAX_QUERY_LENGTH) {
      throw chatError('質問を入力してください（2,000文字以内）');
    }

    const normalizedQuery = query.trim();
    const turnId = nextTurnId++;
    const run = {
      turnId,
      generation,
      controller: new AbortController(),
    };
    turns = [...turns, {
      id: turnId,
      query: normalizedQuery,
      normal: pausedReasons.normal ? makeLane('paused', pausedReasons.normal) : makeLane('loading'),
      law: pausedReasons.law ? makeLane('paused', pausedReasons.law) : makeLane('loading'),
    }];
    active = run;
    running = true;
    notify();

    const jobs = MODES
      .filter((mode) => !pausedReasons[mode])
      .map((mode) => runLane(run, mode, normalizedQuery));
    await Promise.all(jobs);
    if (isCurrent(run)) {
      checkSessionCollision(run);
      running = false;
      active = null;
      notify();
    }
  }

  function cancel() {
    if (!active || !running) return;
    const run = active;
    const message = '検索を中止しました。安全のため、この検索先の会話はリセットして再開してください';
    run.controller.abort();
    pausedReasons = { ...pausedReasons };
    turns = turns.map((turn) => {
      if (turn.id !== run.turnId) return turn;
      const next = { ...turn };
      for (const mode of MODES) {
        if (next[mode].status === 'loading') {
          pausedReasons[mode] = message;
          next[mode] = makeLane('cancelled', message);
        }
      }
      return next;
    });
    active = null;
    generation += 1;
    running = false;
    notify();
  }

  function reset() {
    if (active) active.controller.abort();
    active = null;
    generation += 1;
    turns = [];
    sessionIds = { normal: null, law: null };
    pausedReasons = { normal: null, law: null };
    running = false;
    notify();
  }

  function dispose() {
    if (disposed) return;
    if (active) active.controller.abort();
    active = null;
    generation += 1;
    running = false;
    disposed = true;
  }

  return Object.freeze({ getSnapshot, send, cancel, reset, dispose });
}
