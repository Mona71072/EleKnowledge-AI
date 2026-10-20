import { KnowledgeResearchError } from './knowledge-research.mjs';

const MODES = ['normal', 'law'];
const MAX_QUERY_LENGTH = 2_000;
const MAX_RESTORED_TURNS = 500;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;
const LANE_STATUSES = new Set(['success', 'error', 'cancelled', 'paused']);

function chatError(message) {
  return new KnowledgeResearchError('validation', message);
}

function freezeCopy(value) {
  if (Array.isArray(value)) return Object.freeze(value.map(freezeCopy));
  if (!value || typeof value !== 'object') return value;
  const copy = Object.fromEntries(Object.entries(value).map(([key, item]) => [key, freezeCopy(item)]));
  return Object.freeze(copy);
}

// SYNC: must equal kbModelTypes.ts ALL_MODEL_TYPES values and RAG UI_MODEL_FILTERS keys (tests/knowledge-senpai-model-types-sync.test.mjs).
export const SENPAI_MODEL_TYPES = new Set(['AXIEZ', 'AXIEZ-LINKs', 'NEXCUBE', 'メルシティ', 'メルワイド', 'エスカレーター']);

/** Return a saved model filter only when it is one of the known UI keys; otherwise undefined. */
export function normalizeSavedModelType(value) {
  if (typeof value !== 'string' || !value || value.length > 64
    || /[\u0000-\u001f\u007f-\u009f]/u.test(value) || !SENPAI_MODEL_TYPES.has(value)) return undefined;
  return value;
}

function cloneTurn(turn) {
  return Object.freeze({
    id: turn.id,
    ...(turn.senpaiTurnId ? { senpaiTurnId: turn.senpaiTurnId } : {}),
    ...(turn.modelType ? { modelType: turn.modelType } : {}),
    query: turn.query,
    normal: Object.freeze({ ...turn.normal, ...(turn.normal.answer ? { answer: freezeCopy(turn.normal.answer) } : {}) }),
    law: Object.freeze({ ...turn.law, ...(turn.law.answer ? { answer: freezeCopy(turn.law.answer) } : {}) }),
  });
}

function defaultCreateId() {
  if (typeof globalThis.crypto?.randomUUID !== 'function') throw chatError('相談履歴の識別情報を作成できませんでした');
  return globalThis.crypto.randomUUID();
}

function validSessionId(value) {
  return typeof value === 'string' && value.trim() && value.length <= 128
    && !/[\u0000-\u001f\u007f-\u009f]/u.test(value);
}

function validateRestore(input) {
  if (!input || typeof input !== 'object' || !UUID.test(input.conversationId)
    || typeof input.complete !== 'boolean' || !Array.isArray(input.turns)
    || input.turns.length > MAX_RESTORED_TURNS) {
    throw chatError('相談履歴の形式を確認できないため、復元できません');
  }
  const turnIds = new Set();
  let nextTurnId = 1;
  const sessions = { normal: null, law: null };
  const pausedReasons = { normal: null, law: null };
  const restored = input.turns.map((turn, index) => {
    if (!turn || typeof turn !== 'object' || !UUID.test(turn.senpaiTurnId)
      || turnIds.has(turn.senpaiTurnId) || typeof turn.query !== 'string'
      || !turn.query.trim() || Array.from(turn.query).length > MAX_QUERY_LENGTH) {
      throw chatError('相談履歴の質問識別情報を確認できないため、復元できません');
    }
    turnIds.add(turn.senpaiTurnId);
    for (const mode of MODES) {
      const lane = turn[mode];
      if (!lane || !LANE_STATUSES.has(lane.status)) {
        throw chatError('相談履歴の回答状態を確認できないため、復元できません');
      }
      if (lane.status === 'success') {
        const answer = lane.answer;
        if (!answer || answer.mode !== mode || answer.query !== turn.query || !validSessionId(answer.sessionId)
          || (sessions[mode] && sessions[mode] !== answer.sessionId)
          || answer.senpaiConversationId !== input.conversationId
          || answer.senpaiTurnId !== turn.senpaiTurnId) {
          throw chatError('相談履歴の回答が質問または検索先と一致しないため、復元できません');
        }
        sessions[mode] = answer.sessionId;
      } else {
        pausedReasons[mode] = typeof lane.message === 'string' && lane.message.trim()
          ? lane.message
          : '保存された回答がないため、この検索先の続きは休止しています';
      }
    }
    const id = Number.isSafeInteger(turn.id) && turn.id > 0 ? turn.id : index + 1;
    if (id >= nextTurnId) nextTurnId = id + 1;
    const modelType = normalizeSavedModelType(turn.modelType);
    return {
      id,
      senpaiTurnId: turn.senpaiTurnId,
      ...(modelType ? { modelType } : {}),
      query: turn.query,
      normal: turn.normal.status === 'success'
        ? { status: 'success', answer: turn.normal.answer }
        : { status: 'paused', message: turn.normal.message || '保存された回答がないため、この検索先の続きは休止しています' },
      law: turn.law.status === 'success'
        ? { status: 'success', answer: turn.law.answer }
        : { status: 'paused', message: turn.law.message || '保存された回答がないため、この検索先の続きは休止しています' },
    };
  });
  if (sessions.normal && sessions.normal === sessions.law) {
    throw chatError('相談履歴の技術KBと法令KBの識別情報が重複しているため、復元できません');
  }
  const latestTurn = restored.at(-1);
  for (const mode of MODES) {
    if (latestTurn?.[mode].status === 'success') {
      sessions[mode] = latestTurn[mode].answer.sessionId;
      pausedReasons[mode] = null;
    } else {
      sessions[mode] = null;
      pausedReasons[mode] = latestTurn?.[mode].message
        || (restored.length ? '保存された回答がないため、この検索先の続きは休止しています' : null);
    }
  }
  return { conversationId: input.conversationId, complete: input.complete, turns: restored, sessions, pausedReasons, nextTurnId };
}

/** Manage isolated technical/law sessions and restore server-backed Senpai history. */
export function createSenpaiChat({ querySource, onChange = () => {}, createId = defaultCreateId }) {
  if (typeof querySource !== 'function') throw chatError('検索サービスの設定を確認してください');
  if (typeof createId !== 'function') throw chatError('相談履歴の識別情報を作成できませんでした');

  let turns = [];
  let sessionIds = { normal: null, law: null };
  let pausedReasons = { normal: null, law: null };
  let conversationId;
  let complete;
  let active = null;
  let running = false;
  let disposed = false;
  let generation = 0;
  let nextTurnId = 1;

  function getSnapshot() {
    return Object.freeze({
      ...(conversationId ? { conversationId } : {}),
      ...(complete !== undefined ? { complete } : {}),
      turns: Object.freeze(turns.map(cloneTurn)),
      running,
    });
  }

  function notify() {
    if (disposed) return;
    try { onChange(getSnapshot()); } catch { /* View callbacks cannot break conversation state. */ }
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

  async function runLane(run, mode, query, modelType) {
    const priorSessionId = sessionIds[mode];
    try {
      const answer = await querySource({
        mode, query,
        ...(modelType ? { modelType } : {}),
        ...(priorSessionId ? { sessionId: priorSessionId } : {}),
        senpaiConversationId: conversationId,
        senpaiTurnId: run.senpaiTurnId,
        signal: run.controller.signal,
      });
      if (!isCurrent(run)) return;
      if (!answer || answer.mode !== mode || !validSessionId(answer.sessionId)
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
        : cancelled ? '検索を中止しました。続きの会話はリセットして再開してください'
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
      ? { ...turn, normal: makeLane('paused', message), law: makeLane('paused', message) } : turn);
    notify();
  }

  async function send(query, options = {}) {
    if (disposed) return;
    if (running) throw chatError('回答を待ってから、次の質問を送信してください');
    if (complete === false) throw chatError('相談履歴が途中までのため、続きの質問は送信できません');
    if (typeof query !== 'string' || !query.trim() || Array.from(query.trim()).length > MAX_QUERY_LENGTH) {
      throw chatError('質問を入力してください（2,000文字以内）');
    }
    const normalizedQuery = query.trim();
    if (options?.modelType !== undefined && typeof options.modelType !== 'string') {
      throw chatError('機種の指定を確認してください');
    }
    const modelType = options?.modelType?.trim() || undefined;
    const nextConversationId = conversationId || createId();
    const senpaiTurnId = createId();
    if (!UUID.test(nextConversationId) || !UUID.test(senpaiTurnId) || nextConversationId === senpaiTurnId
      || turns.some((turn) => turn.senpaiTurnId === senpaiTurnId)) {
      throw chatError('相談履歴の識別情報を作成できませんでした');
    }
    conversationId = nextConversationId;
    const turnId = nextTurnId++;
    const run = { turnId, senpaiTurnId, generation, controller: new AbortController() };
    turns = [...turns, {
      id: turnId, senpaiTurnId, query: normalizedQuery,
      ...(modelType ? { modelType } : {}),
      normal: pausedReasons.normal ? makeLane('paused', pausedReasons.normal) : makeLane('loading'),
      law: pausedReasons.law ? makeLane('paused', pausedReasons.law) : makeLane('loading'),
    }];
    active = run;
    running = true;
    notify();
    await Promise.all(MODES.filter((mode) => !pausedReasons[mode]).map((mode) => runLane(run, mode, normalizedQuery, modelType)));
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
      for (const mode of MODES) if (next[mode].status === 'loading') {
        pausedReasons[mode] = message;
        next[mode] = makeLane('cancelled', message);
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
    conversationId = undefined;
    complete = undefined;
    nextTurnId = 1;
    running = false;
    notify();
  }

  function restore(snapshot) {
    const prepared = validateRestore(snapshot);
    if (active) active.controller.abort();
    active = null;
    generation += 1;
    turns = prepared.turns;
    sessionIds = prepared.sessions;
    pausedReasons = prepared.pausedReasons;
    conversationId = prepared.conversationId;
    complete = prepared.complete;
    nextTurnId = prepared.nextTurnId;
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

  return Object.freeze({ getSnapshot, send, cancel, reset, restore, dispose });
}
