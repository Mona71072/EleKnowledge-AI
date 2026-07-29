'use client';

import { useCallback, useEffect, useState } from 'react';
import { Loading } from '@/components/ui/Loading';
import {
  FEEDBACK_REASON_LABELS,
  FailureItem,
  FailureKind,
  FeedbackReason,
  getChatFailures,
  toGoldenCandidateLine,
} from '@/lib/chat-failures';

const KINDS: { key: FailureKind; label: string }[] = [
  { key: 'all', label: 'すべて' },
  { key: 'bad', label: '👎 bad' },
  { key: 'not_found', label: 'not_found' },
];

function formatTs(iso: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('ja-JP', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

function filtersLabel(item: FailureItem): string {
  const qf = item.queryFilters || {};
  const parts: string[] = [];
  if (qf.modelType) parts.push(`機種:${qf.modelType}`);
  const cat = qf.category;
  if (Array.isArray(cat) && cat.length) parts.push(`カテゴリ:${cat.join(',')}`);
  else if (typeof cat === 'string' && cat) parts.push(`カテゴリ:${cat}`);
  return parts.length ? parts.join(' / ') : 'フィルタなし';
}

export default function AdminFailuresPage() {
  const [kind, setKind] = useState<FailureKind>('all');
  const [items, setItems] = useState<FailureItem[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [scannedCount, setScannedCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getChatFailures(kind, 50);
      setItems(res.failures || []);
      setNote(res.note || null);
      setScannedCount(res.scannedCount || 0);
    } catch (e) {
      setError((e as Error).message);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [kind]);

  useEffect(() => {
    load();
  }, [load]);

  const copyGolden = async (item: FailureItem, index: number) => {
    const line = toGoldenCandidateLine(item, index);
    try {
      await navigator.clipboard.writeText(line);
      setCopiedId(item.messageId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('clipboard failed', err);
      setError('クリップボードへコピーできませんでした');
    }
  };

  const copyAll = async () => {
    const text = items.map((it, i) => toGoldenCandidateLine(it, i)).join('\n');
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId('__all__');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('clipboard failed', err);
      setError('クリップボードへコピーできませんでした');
    }
  };

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">失敗一覧（PDCA 入力）</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            👎 と not_found をワンクリックで確認し、ゴールデンセット候補をコピーします
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-lg bg-gray-100 p-1" role="tablist" aria-label="種類">
            {KINDS.map((k) => (
              <button
                key={k.key}
                type="button"
                role="tab"
                aria-selected={kind === k.key}
                onClick={() => setKind(k.key)}
                className={`px-3 py-1 text-sm rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  kind === k.key
                    ? 'bg-white font-semibold text-blue-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {k.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={load}
            className="px-3 py-1.5 text-sm rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
          >
            再読込
          </button>
          <button
            type="button"
            onClick={copyAll}
            disabled={!items.length}
            className="px-3 py-1.5 text-sm rounded-md border border-blue-200 bg-blue-50 text-blue-800 hover:bg-blue-100 disabled:opacity-40"
          >
            {copiedId === '__all__' ? 'コピー済み' : '全件を候補コピー'}
          </button>
        </div>
      </div>

      {note && (
        <p className="mb-4 text-xs text-gray-500 bg-gray-50 border border-gray-200 rounded-md px-3 py-2">
          {note}
          {scannedCount > 0 ? `（scan ${scannedCount}）` : ''}
        </p>
      )}

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading ? (
        <div className="p-12 flex justify-center">
          <Loading size="lg" text="失敗ログを読み込み中..." />
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white px-6 py-12 text-center text-sm text-gray-500">
          該当する失敗はまだありません。試用で 👎 や not_found が出るとここに集まります。
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((item, index) => (
            <li
              key={`${item.sessionId}-${item.messageId}`}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div className="flex flex-wrap items-center gap-1.5">
                  {item.signals.map((s) => (
                    <span
                      key={s}
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                        s === 'bad'
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : 'bg-amber-50 text-amber-800 border border-amber-200'
                      }`}
                    >
                      {s}
                    </span>
                  ))}
                  {item.feedbackReason && (
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                      {FEEDBACK_REASON_LABELS[item.feedbackReason as FeedbackReason] ||
                        item.feedbackReason}
                    </span>
                  )}
                  <span className="text-[11px] text-gray-400">{formatTs(item.timestamp)}</span>
                </div>
                <button
                  type="button"
                  onClick={() => copyGolden(item, index)}
                  className="text-xs px-2.5 py-1 rounded-md border border-blue-200 bg-blue-50 text-blue-800 hover:bg-blue-100"
                >
                  {copiedId === item.messageId ? 'コピー済み' : 'ゴールデン候補をコピー'}
                </button>
              </div>

              <p className="text-sm text-gray-900 font-medium whitespace-pre-wrap break-words">
                {item.userQuery || '（直前の質問を取得できませんでした）'}
              </p>
              <p className="mt-1 text-xs text-gray-500">{filtersLabel(item)}</p>

              {item.topDocuments?.length > 0 && (
                <p className="mt-2 text-xs text-gray-600">
                  候補資料:{' '}
                  <span className="font-mono">{item.topDocuments.slice(0, 5).join(', ')}</span>
                </p>
              )}
              {item.feedbackComment && (
                <p className="mt-1 text-xs text-gray-600">コメント: {item.feedbackComment}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
