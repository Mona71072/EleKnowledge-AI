import { getIdToken, authHeaders } from './auth-helpers';

const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || '';

export type FailureKind = 'all' | 'bad' | 'not_found';
/** 履歴に残る旧 reason（wrong_page）も含む。新規 UI では送らない */
export type FeedbackReason =
  | 'wrong_doc'
  | 'unresolved'
  | 'bad_answer'
  | 'other'
  | 'wrong_page';

export interface FailureItem {
  sessionId: string;
  messageId: string;
  timestamp: string;
  signals: Array<'bad' | 'not_found'>;
  ragMode?: 'normal' | 'spec' | 'law';
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
}

export interface FailuresResponse {
  failures: FailureItem[];
  count: number;
  scannedCount: number;
  incomplete?: boolean;
  kind: string;
  note?: string;
}

export const FEEDBACK_REASON_LABELS: Record<FeedbackReason, string> = {
  wrong_doc: '資料が違う',
  unresolved: '疑問が解けない',
  bad_answer: '回答がおかしい',
  other: 'その他',
  wrong_page: '頁が違う（旧）',
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

export async function getChatFailures(
  kind: FailureKind = 'all',
  limit = 50,
): Promise<FailuresResponse> {
  const token = await getIdToken();
  const res = await fetch(
    `${CHAT_API_URL}/chat/admin/failures?kind=${encodeURIComponent(kind)}&limit=${limit}`,
    {
      headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    },
  );
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
  return res.json();
}

export interface ProductWish {
  messageId: string;
  userId: string;
  text: string;
  timestamp: string;
  contextSessionId?: string;
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
  const token = await getIdToken();
  const body: Record<string, string> = { text: text.trim() };
  if (sessionId) body.sessionId = sessionId;

  const res = await fetch(`${CHAT_API_URL}/chat/suggestions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      message = data.message || data.error || message;
    } catch {
      /* ignore */
    }
    throw new Error(message);
  }
  return res.json();
}

/** admin: 改善要望一覧 */
export async function getAdminSuggestions(limit = 30): Promise<SuggestionsResponse> {
  const token = await getIdToken();
  const res = await fetch(
    `${CHAT_API_URL}/chat/admin/suggestions?limit=${limit}`,
    {
      headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    },
  );
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      message = data.message || data.error || message;
    } catch {
      /* ignore */
    }
    throw new Error(message);
  }
  return res.json();
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
