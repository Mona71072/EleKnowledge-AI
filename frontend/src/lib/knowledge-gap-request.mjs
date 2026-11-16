const STORAGE_KEY = 'knowledge-gap-request';
const TURN_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/iu;

function browserStorage() {
  try {
    return globalThis.window?.sessionStorage ?? null;
  } catch {
    return null;
  }
}

/** Save one explicit, browser-local handoff marker. No question or account data is retained. */
export function storeKnowledgeGapRequest({ kind = 'senpai', senpaiTurnId } = {}, storage = browserStorage()) {
  if (!storage) return false;
  let value;
  if (kind === 'official_kb') value = { version: 1, kind };
  else if (kind === 'senpai' && typeof senpaiTurnId === 'string' && TURN_ID.test(senpaiTurnId)) {
    value = { version: 1, kind, senpaiTurnId };
  } else return false;
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
}

/** Read and remove the single pending handoff marker. Invalid or stale-shaped values are discarded. */
export function consumeKnowledgeGapRequest(storage = browserStorage()) {
  if (!storage) return null;
  let raw;
  try {
    raw = storage.getItem(STORAGE_KEY);
    storage.removeItem(STORAGE_KEY);
  } catch {
    return null;
  }
  if (typeof raw !== 'string') return null;
  try {
    const value = JSON.parse(raw);
    if (!value || typeof value !== 'object' || Array.isArray(value) || value.version !== 1) return null;
    const keys = Object.keys(value).length;
    if (value.kind === 'official_kb' && keys === 2) return { kind: 'official_kb' };
    if (keys !== 3 || value.kind !== 'senpai'
      || typeof value.senpaiTurnId !== 'string' || !TURN_ID.test(value.senpaiTurnId)) return null;
    return { kind: 'senpai', senpaiTurnId: value.senpaiTurnId };
  } catch {
    return null;
  }
}
