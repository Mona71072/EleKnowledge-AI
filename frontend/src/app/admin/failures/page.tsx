'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Loading } from '@/components/ui/Loading';
import { SegmentedControl } from '@/components/ui/SegmentedControl';
import {
  FEEDBACK_REASON_LABELS,
  FailureItem,
  FailureKind,
  FeedbackReason,
  ProductWish,
  formatCategoryKey,
  getAdminSuggestions,
  getChatFailures,
  toGoldenCandidateLine,
} from '@/lib/chat-failures';
import {
  IMPROVEMENT_PROPOSAL_THRESHOLD,
  ReasonFilterKey,
  aggregateFailureSignals,
  buildImprovementProposals,
  filterFailureItems,
} from '@/lib/improvement-proposals';

const KINDS: { key: FailureKind; label: string }[] = [
  { key: 'all', label: 'すべて' },
  { key: 'bad', label: '👎 bad' },
  { key: 'not_found', label: 'not_found' },
];

const REASON_CHIP_ORDER: FeedbackReason[] = [
  'wrong_doc',
  'unresolved',
  'bad_answer',
  'other',
  'wrong_page',
];

const REASON_FILTERS: { key: ReasonFilterKey; label: string }[] = [
  { key: 'all', label: '理由: すべて' },
  { key: 'wrong_doc', label: '資料が違う' },
  { key: 'unresolved', label: '疑問が解けない' },
  { key: 'bad_answer', label: '回答がおかしい' },
  { key: 'other', label: 'その他' },
  { key: 'wrong_page', label: '頁（旧）' },
  { key: 'reason_omitted', label: '理由なし 👎' },
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
  const cats = Array.isArray(cat) ? cat : cat ? [cat] : [];
  if (cats.length) {
    parts.push(`カテゴリ:${cats.map(formatCategoryKey).join(',')}`);
  }
  return parts.length ? parts.join(' / ') : 'フィルタなし';
}

export default function AdminFailuresPage() {
  const [kind, setKind] = useState<FailureKind>('all');
  const [reasonFilter, setReasonFilter] = useState<ReasonFilterKey>('all');
  const [allItems, setAllItems] = useState<FailureItem[]>([]);
  const [wishes, setWishes] = useState<ProductWish[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [wishesNote, setWishesNote] = useState<string | null>(null);
  const [wishesError, setWishesError] = useState<string | null>(null);
  const [scannedCount, setScannedCount] = useState(0);
  const [incomplete, setIncomplete] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showOpsGuide, setShowOpsGuide] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setWishesError(null);
    try {
      const failRes = await getChatFailures('all', 50);
      setAllItems(failRes.failures || []);
      setNote(failRes.note || null);
      setScannedCount(failRes.scannedCount || 0);
      setIncomplete(Boolean(failRes.incomplete));

      try {
        const wishRes = await getAdminSuggestions(30);
        setWishes(wishRes.wishes || []);
        setWishesNote(wishRes.note || null);
        setWishesError(null);
      } catch (wishErr) {
        setWishes([]);
        setWishesNote(null);
        setWishesError(
          (wishErr as Error).message ||
            '要望一覧の取得に失敗しました（phase2 未デプロイの可能性があります）',
        );
      }
    } catch (e) {
      setError((e as Error).message);
      setAllItems([]);
      setWishes([]);
      setWishesError(null);
      setIncomplete(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const summary = useMemo(() => aggregateFailureSignals(allItems), [allItems]);
  const proposals = useMemo(() => buildImprovementProposals(summary), [summary]);
  const items = useMemo(
    () => filterFailureItems(allItems, kind, reasonFilter),
    [allItems, kind, reasonFilter],
  );

  const applyProposalFilter = (proposal: ReturnType<typeof buildImprovementProposals>[number]) => {
    if (proposal.filterKind === 'not_found') {
      setKind('not_found');
      setReasonFilter('all');
      return;
    }
    setKind('bad');
    setReasonFilter(proposal.filterReason || 'all');
  };

  const applyReasonChip = (reason: ReasonFilterKey) => {
    if (reason === 'reason_omitted') {
      setKind('bad');
      setReasonFilter('reason_omitted');
      return;
    }
    setKind('bad');
    setReasonFilter(reason);
  };

  const resetFilters = () => {
    setKind('all');
    setReasonFilter('all');
  };

  const hasActiveFilter = kind !== 'all' || reasonFilter !== 'all';

  const nearThresholdSignals = useMemo(() => {
    const candidates: { label: string; count: number; onClick: () => void }[] = [];
    for (const reason of REASON_CHIP_ORDER) {
      const count = summary.reasonCounts[reason] || 0;
      if (count > 0 && count < IMPROVEMENT_PROPOSAL_THRESHOLD) {
        candidates.push({
          label: FEEDBACK_REASON_LABELS[reason],
          count,
          onClick: () => applyReasonChip(reason),
        });
      }
    }
    if (summary.notFoundCount > 0 && summary.notFoundCount < IMPROVEMENT_PROPOSAL_THRESHOLD) {
      candidates.push({
        label: 'not_found',
        count: summary.notFoundCount,
        onClick: () => {
          setKind('not_found');
          setReasonFilter('all');
        },
      });
    }
    if (summary.badWithoutReason > 0 && summary.badWithoutReason < IMPROVEMENT_PROPOSAL_THRESHOLD) {
      candidates.push({
        label: '理由なし 👎',
        count: summary.badWithoutReason,
        onClick: () => applyReasonChip('reason_omitted'),
      });
    }
    return candidates;
  }, [summary]);

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
          <h2 className="text-xl font-bold text-gray-900">失敗・改善提案（PDCA 入力）</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            👎・not_found と利用者の「こうなってほしい」から改善提案を届けます
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
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
            {copiedId === '__all__' ? 'コピー済み' : '表示中を候補コピー'}
          </button>
        </div>
      </div>

      {/* 改善提案パネル */}
      <section className="mb-6 rounded-lg border border-blue-200 bg-blue-50/40 p-4">
        <div className="flex flex-wrap items-start justify-between gap-2 mb-3">
          <div>
            <h3 className="text-sm font-bold text-blue-950">改善提案（ルール v0）</h3>
            <p className="text-xs text-blue-900/80 mt-0.5">
              直近 {summary.total} 件の失敗信号から集計。件数≥3 でカード表示（出荷判断は第1層 eval のまま）
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowOpsGuide((v) => !v)}
            className="text-xs text-blue-800 underline underline-offset-2"
          >
            {showOpsGuide ? '運用ガイドを閉じる' : '運用ガイド'}
          </button>
        </div>

        <dl className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 text-xs">
          <div className="rounded bg-white/80 px-2 py-1.5 border border-blue-100">
            <dt className="text-gray-500">👎</dt>
            <dd className="font-semibold text-gray-900">{summary.badCount}</dd>
          </div>
          <div className="rounded bg-white/80 px-2 py-1.5 border border-blue-100">
            <dt className="text-gray-500">not_found</dt>
            <dd className="font-semibold text-gray-900">{summary.notFoundCount}</dd>
          </div>
          <div className="rounded bg-white/80 px-2 py-1.5 border border-blue-100">
            <dt className="text-gray-500">理由なし 👎</dt>
            <dd className="font-semibold text-gray-900">{summary.badWithoutReason}</dd>
          </div>
          <div className="rounded bg-white/80 px-2 py-1.5 border border-blue-100">
            <dt className="text-gray-500">要望（文字）</dt>
            <dd className="font-semibold text-gray-900">{wishes.length}</dd>
          </div>
        </dl>

        {(summary.badCount > 0 || summary.notFoundCount > 0) && (
          <div className="mb-3 flex flex-wrap gap-1.5">
            {REASON_CHIP_ORDER.map((reason) => {
              const count = summary.reasonCounts[reason] || 0;
              if (!count) return null;
              const active = kind === 'bad' && reasonFilter === reason;
              return (
                <button
                  key={reason}
                  type="button"
                  onClick={() => applyReasonChip(reason)}
                  className={`text-[11px] px-2 py-1 rounded-full border transition-colors ${
                    active
                      ? 'bg-blue-700 text-white border-blue-700'
                      : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300'
                  }`}
                >
                  {FEEDBACK_REASON_LABELS[reason]} · {count}
                </button>
              );
            })}
            {summary.badWithoutReason > 0 && (
              <button
                type="button"
                onClick={() => applyReasonChip('reason_omitted')}
                className={`text-[11px] px-2 py-1 rounded-full border transition-colors ${
                  kind === 'bad' && reasonFilter === 'reason_omitted'
                    ? 'bg-blue-700 text-white border-blue-700'
                    : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300'
                }`}
              >
                理由なし 👎 · {summary.badWithoutReason}
              </button>
            )}
            {summary.notFoundCount > 0 && (
              <button
                type="button"
                onClick={() => {
                  setKind('not_found');
                  setReasonFilter('all');
                }}
                className={`text-[11px] px-2 py-1 rounded-full border transition-colors ${
                  kind === 'not_found'
                    ? 'bg-amber-700 text-white border-amber-700'
                    : 'bg-white text-gray-700 border-gray-200 hover:border-amber-300'
                }`}
              >
                not_found · {summary.notFoundCount}
              </button>
            )}
          </div>
        )}

        {showOpsGuide && (
          <div className="mb-3 text-xs text-blue-950/90 bg-white/70 rounded-md border border-blue-100 px-3 py-2 space-y-1">
            <p>週次: failures → golden 追加 → run_retrieve_eval.py → 悪化なしなら PR</p>
            <p>
              <code className="text-[11px]">unresolved</code> は KB 悪と決め打ちせず、件ごとに検索／snippet／作文／KB を振り分け
            </p>
            <p>第1層の主指標は <code className="text-[11px]">hit_in_candidates</code>（ラベル済み）</p>
          </div>
        )}

        {proposals.length === 0 ? (
          <div className="text-xs text-gray-600 space-y-1.5">
            <p>
              しきい値（{IMPROVEMENT_PROPOSAL_THRESHOLD} 件）未満のため定型提案はありません。信号が増えたらここにカードが出ます。
            </p>
            {nearThresholdSignals.length > 0 && (
              <p className="text-gray-500">
                注目:{' '}
                {nearThresholdSignals.map((s, i) => (
                  <span key={s.label}>
                    {i > 0 ? ' / ' : ''}
                    <button
                      type="button"
                      onClick={s.onClick}
                      className="underline underline-offset-2 hover:text-blue-800"
                    >
                      {s.label} {s.count}件
                    </button>
                  </span>
                ))}
              </p>
            )}
          </div>
        ) : (
          <ul className="space-y-2">
            {proposals.map((p) => (
              <li
                key={p.id}
                className="rounded-md border border-blue-200 bg-white p-3 text-sm"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-gray-900">
                      {p.title}
                      <span className="ml-2 text-xs font-normal text-gray-500">{p.count} 件</span>
                    </p>
                    <p className="text-xs text-gray-600 mt-1">{p.body}</p>
                    <ul className="mt-2 text-xs text-gray-700 list-disc list-inside space-y-0.5">
                      {p.actions.map((a) => (
                        <li key={a}>{a}</li>
                      ))}
                    </ul>
                    <p className="text-[11px] text-gray-500 mt-1.5">担当目安: {p.owner}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => applyProposalFilter(p)}
                    className="shrink-0 text-xs px-2.5 py-1 rounded-md border border-blue-300 bg-blue-50 text-blue-900 hover:bg-blue-100"
                  >
                    該当を見る
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* 利用者の文字フィードバック */}
      <section className="mb-6 rounded-lg border border-violet-200 bg-violet-50/30 p-4">
        <h3 className="text-sm font-bold text-violet-950 mb-2">こうなってほしい（利用者の文字）</h3>
        {wishesNote && !wishesError && (
          <p className="text-[11px] text-gray-500 mb-2">{wishesNote}</p>
        )}
        {wishesError ? (
          <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-950">
            <p className="font-medium">要望一覧を取得できませんでした</p>
            <p className="mt-1 text-amber-900/80">{wishesError}</p>
            <p className="mt-1 text-amber-900/70">
              phase2（chat-management）のデプロイと <code className="text-[10px]">GET /chat/admin/suggestions</code> を確認してください。
            </p>
            <button
              type="button"
              onClick={load}
              className="mt-2 underline underline-offset-2 hover:text-amber-800"
            >
              再試行
            </button>
          </div>
        ) : wishes.length === 0 ? (
          <p className="text-xs text-gray-600">
            まだ投稿はありません。チャット画面右上の「こうなってほしい」から届きます。
          </p>
        ) : (
          <ul className="space-y-2 max-h-48 overflow-y-auto">
            {wishes.map((w) => (
              <li
                key={w.messageId}
                className="rounded-md border border-violet-100 bg-white px-3 py-2 text-sm"
              >
                <p className="text-gray-900 whitespace-pre-wrap break-words">{w.text}</p>
                <p className="text-[11px] text-gray-500 mt-1">
                  {formatTs(w.timestamp)}
                  {w.contextSessionId && (
                    <>
                      {' · '}
                      <Link
                        href={`/chat?session=${encodeURIComponent(w.contextSessionId)}`}
                        className="text-blue-700 underline"
                      >
                        関連セッション
                      </Link>
                    </>
                  )}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="flex flex-wrap items-center gap-2 mb-2">
        <SegmentedControl
          aria-label="失敗の種類"
          options={KINDS.map((k) => ({ value: k.key, label: k.label }))}
          value={kind}
          onChange={(v) => setKind(v as FailureKind)}
        />
        <select
          value={reasonFilter}
          onChange={(e) => setReasonFilter(e.target.value as ReasonFilterKey)}
          className="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white"
          aria-label="理由で絞り込み"
        >
          {REASON_FILTERS.map((r) => (
            <option key={r.key} value={r.key}>
              {r.label}
            </option>
          ))}
        </select>
        <span className="text-xs text-gray-500 ml-auto">
          表示 {items.length} / 取得 {allItems.length}
        </span>
      </div>

      {hasActiveFilter && (
        <div className="mb-4 flex flex-wrap items-center gap-2 rounded-md border border-blue-200 bg-blue-50/60 px-3 py-2 text-xs text-blue-950">
          <span>
            絞り込み中:
            {kind !== 'all' && ` ${KINDS.find((k) => k.key === kind)?.label}`}
            {reasonFilter !== 'all' && ` · ${REASON_FILTERS.find((r) => r.key === reasonFilter)?.label}`}
          </span>
          <button
            type="button"
            onClick={resetFilters}
            className="underline underline-offset-2 hover:text-blue-800"
          >
            解除
          </button>
        </div>
      )}

      {incomplete && (
        <div className="mb-4 rounded border border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-900">
          Scan が打ち切られたため、最新の失敗が一覧に含まれていない可能性があります。
        </div>
      )}

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
          該当する失敗はありません（フィルタ条件を変えるか、現場で 👎 / not_found / 要望フォームを使ってください）。
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
              {item.assistantPreview && (
                <p className="mt-1.5 text-xs text-gray-600 line-clamp-2 bg-gray-50 rounded px-2 py-1 border border-gray-100">
                  回答: {item.assistantPreview}
                  {(item.assistantPreview.length || 0) >= 120 ? '…' : ''}
                </p>
              )}
              <p className="mt-1 text-xs text-gray-500">{filtersLabel(item)}</p>
              {item.sessionId && (
                <p className="mt-1 text-xs text-gray-500">
                  <Link
                    href={`/chat?session=${encodeURIComponent(item.sessionId)}`}
                    className="text-blue-700 underline underline-offset-2"
                  >
                    チャットで開く
                  </Link>
                  <span className="ml-2 font-mono text-gray-400 break-all">{item.sessionId}</span>
                </p>
              )}

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
