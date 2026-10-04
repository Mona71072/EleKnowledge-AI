import { getIdToken, authHeaders } from './auth-helpers';

const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || '';

export type FailureKind = 'all' | 'bad' | 'not_found' | 'reformulated';
/** 履歴に残る旧 reason（wrong_page）も含む。新規 UI では送らない */
export type FeedbackReason =
  | 'wrong_doc'
  | 'unresolved'
  | 'bad_answer'
  | 'other'
  | 'wrong_page';

export type TriageStatus = 'open' | 'in_progress' | 'done' | 'wontfix';
export type TriageCause = 'search' | 'snippet' | 'writing' | 'clarify' | 'kb_missing' | 'scope' | 'user' | 'other';

/** 振り分け（設計 docs/design-2026-09-10-dashboard-v2.md §9.4）。未設定は status=open */
export interface Triage {
  status: TriageStatus;
  cause?: TriageCause | null;
  note?: string | null;
  ref?: string | null;
  by?: string | null;
  at?: string | null;
}

export interface TriageInput {
  status: TriageStatus;
  cause?: TriageCause | '';
  note?: string;
  ref?: string;
}

/** retrievalTrace の要約（トレース実装後に値が入る。無ければ null） */
export interface TraceSummary {
  mergedCount: number;
  selectedCount: number;
  excludedByModelScope: number;
  topScore: number | null;
  inputTokens?: number | null;
  outputTokens?: number | null;
  latencyMs?: { retrieve?: number; generate?: number; total?: number } | null;
}

export interface FailureItem {
  sessionId: string;
  messageId: string;
  timestamp: string;
  signals: Array<'bad' | 'not_found' | 'reformulated'>;
  responseType?: string;
  feedback?: string;
  feedbackReason?: FeedbackReason;
  feedbackComment?: string;
  userQuery: string;
  queryFilters?: {
    category?: string | string[];
    modelType?: string;
  };
  topDocuments: string[];
  assistantPreview?: string;
  /** 引用リンクから文書を開いた回数 */
  opened?: number;
  /** 言い換え（回答直後に次の質問、👍 も資料クリックも無い） */
  reformulated?: boolean;
  triage?: Triage;
  traceSummary?: TraceSummary | null;
  /** 機械的な手がかり（判断ではない） */
  hints?: string[];
}

export interface FailuresResponse {
  failures: FailureItem[];
  count: number;
  matchedCount?: number;
  truncated?: boolean;
  scannedCount: number;
  incomplete?: boolean;
  kind: string;
  since?: string | null;
  until?: string | null;
  triage?: string;
  note?: string;
}

export const FEEDBACK_REASON_LABELS: Record<FeedbackReason, string> = {
  wrong_doc: '資料が違う',
  unresolved: '疑問が解けない',
  bad_answer: '回答がおかしい',
  other: 'その他',
  wrong_page: '頁が違う（旧）',
};

export const TRIAGE_STATUS_LABELS: Record<TriageStatus, string> = {
  open: '未振り分け',
  in_progress: '対応中',
  done: '対応済み',
  wontfix: '対応しない',
};

export const TRIAGE_CAUSE_LABELS: Record<TriageCause, string> = {
  search: '検索ミス',
  snippet: 'snippet が弱い',
  writing: '作文',
  clarify: '聞き返し不足',
  kb_missing: 'KB 欠落',
  scope: '機種スコープ',
  user: '利用者側',
  other: 'その他',
};

/** チャット 👎 理由（新規 UI が送る値のみ） */
export type BadFeedbackReasonId = 'wrong_doc' | 'unresolved' | 'bad_answer' | 'other';

export const BAD_FEEDBACK_REASONS: { id: BadFeedbackReasonId; label: string; hint?: string }[] = [
  { id: 'wrong_doc', label: '資料が違う', hint: '別の資料・機種が出た' },
  { id: 'unresolved', label: '疑問が解けない', hint: '読んでも判断できない' },
  { id: 'bad_answer', label: '回答がおかしい', hint: '要約や断定が違う' },
  { id: 'other', label: 'その他' },
];

export const FEEDBACK_COMMENT_MAX = 200;
export const PRODUCT_WISH_TEXT_MAX = 1000;
export const TRIAGE_NOTE_MAX = 200;

export function getFeedbackReasonLabel(reason?: FeedbackReason | null): string | null {
  if (!reason) return null;
  return FEEDBACK_REASON_LABELS[reason] || reason;
}

/** API 安定キー → 表示ラベル（チャット categoryOptions と揃える） */
export const CATEGORY_LABELS: Record<string, string> = {
  spec: 'C資料',
  tech_info: 'TI',
  std: '据付基準',
  drawing: '据付場用図',
  incident: '災害事例集',
  qsheet: 'Qシート',
  note: '据付ノート',
  w_doc: 'W資料',
};

export function formatCategoryKey(key: string): string {
  return CATEGORY_LABELS[key] || key;
}

async function chatRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getIdToken();
  const res = await fetch(`${CHAT_API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...authHeaders(token), ...(init?.headers || {}) },
  });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      message = data.message || data.error || message;
    } catch {
      /* ignore */
    }
    const err = new Error(message) as Error & { status?: number };
    err.status = res.status;
    throw err;
  }
  return res.json() as Promise<T>;
}

export interface FailuresQuery {
  since?: string | null;
  until?: string | null;
  triage?: TriageStatus | 'all';
}

export async function getChatFailures(kind: FailureKind = 'all', limit = 50, query: FailuresQuery = {}): Promise<FailuresResponse> {
  const params = new URLSearchParams({ kind, limit: String(limit) });
  if (query.since) params.set('since', query.since);
  if (query.until) params.set('until', query.until);
  if (query.triage && query.triage !== 'all') params.set('triage', query.triage);
  return chatRequest<FailuresResponse>(`/chat/admin/failures?${params.toString()}`);
}

/** admin: 振り分けを保存（assistant / product_wish の行） */
export async function updateTriage(sessionId: string, messageId: string, input: TriageInput): Promise<Triage> {
  const body: Record<string, string> = { status: input.status };
  if (input.cause) body.cause = input.cause;
  if (input.note) body.note = input.note;
  if (input.ref) body.ref = input.ref;
  const res = await chatRequest<{ triage: Triage }>(
    `/chat/admin/messages/${encodeURIComponent(sessionId)}/${encodeURIComponent(messageId)}/triage`,
    { method: 'PUT', body: JSON.stringify(body) },
  );
  return res.triage;
}

export interface ProductWish {
  sessionId?: string;
  messageId: string;
  userId: string;
  text: string;
  timestamp: string;
  contextSessionId?: string;
  triage?: Triage;
}

export interface SuggestionsResponse {
  wishes: ProductWish[];
  count: number;
  scannedCount: number;
  incomplete?: boolean;
  note?: string;
}

/** 利用者: 「こうなってほしい」を送信 */
export async function submitProductWish(
  text: string,
  sessionId?: string | null,
): Promise<{ message: string; messageId: string; timestamp: string }> {
  const body: Record<string, string> = { text: text.trim() };
  if (sessionId) body.sessionId = sessionId;
  return chatRequest(`/chat/suggestions`, { method: 'POST', body: JSON.stringify(body) });
}

/** admin: 改善要望一覧 */
export async function getAdminSuggestions(limit = 30): Promise<SuggestionsResponse> {
  return chatRequest<SuggestionsResponse>(`/chat/admin/suggestions?limit=${limit}`);
}

/** golden_set.jsonl 1行分の候補（未ラベル）。工事番号等は人が一般化すること。 */
export function toGoldenCandidateLine(item: FailureItem, index = 0): string {
  const filters: Record<string, unknown> = {};
  const qf = item.queryFilters || {};
  if (qf.category && (Array.isArray(qf.category) ? qf.category.length : qf.category)) {
    filters.category = qf.category;
  }
  if (qf.modelType) {
    filters.modelType = qf.modelType;
  }

  const tags = ['from_prod'];
  if (item.signals.includes('bad')) tags.push('bad_feedback');
  if (item.signals.includes('not_found')) tags.push('not_found');
  if (item.signals.includes('reformulated')) tags.push('reformulated');
  if (item.feedbackReason) tags.push(item.feedbackReason);

  const expectedGate =
    item.responseType === 'not_found'
      ? 'not_found'
      : item.responseType === 'clarify'
        ? 'clarify'
        : 'pages';

  const notesParts = [
    `session=${item.sessionId}`,
    item.feedbackReason ? `reason=${item.feedbackReason}` : null,
    item.topDocuments?.length ? `top=${item.topDocuments.slice(0, 3).join('|')}` : null,
    '※質問文の固有名・工事番号は一般化してからコミット',
  ].filter(Boolean);

  const row = {
    id: `F${(index + 1).toString().padStart(3, '0')}`,
    query: item.userQuery || '',
    filters,
    expected_documents: [] as string[],
    expected_gate: expectedGate,
    tags,
    notes: notesParts.join('; '),
  };
  return JSON.stringify(row);
}
