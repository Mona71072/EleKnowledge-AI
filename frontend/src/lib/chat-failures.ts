import { getIdToken, authHeaders } from './auth-helpers';

const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || '';

export type FailureKind = 'all' | 'bad' | 'not_found';
export type FeedbackReason = 'wrong_doc' | 'wrong_page' | 'bad_answer' | 'other';

export interface FailureItem {
  sessionId: string;
  messageId: string;
  timestamp: string;
  signals: Array<'bad' | 'not_found'>;
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
  kind: string;
  note?: string;
}

export const FEEDBACK_REASON_LABELS: Record<FeedbackReason, string> = {
  wrong_doc: '資料が違う',
  wrong_page: '頁が違う',
  bad_answer: '回答がおかしい',
  other: 'その他',
};

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
