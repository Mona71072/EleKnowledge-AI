'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Loading } from '@/components/ui/Loading';
import { SegmentedControl } from '@/components/ui/SegmentedControl';
import {
  FEEDBACK_REASON_LABELS,
  TRIAGE_CAUSE_LABELS,
  TRIAGE_NOTE_MAX,
  TRIAGE_STATUS_LABELS,
  FailureItem,
  FailureKind,
  FeedbackReason,
  ProductWish,
  Triage,
  TriageCause,
  TriageInput,
  TriageStatus,
  formatCategoryKey,
  getAdminSuggestions,
  getChatFailures,
  toGoldenCandidateLine,
  updateTriage,
} from '@/lib/chat-failures';
import {
  IMPROVEMENT_PROPOSAL_THRESHOLD,
  ReasonFilterKey,
  aggregateFailureSignals,
  buildImprovementProposals,
  filterFailureItems,
  isUnresolved,
} from '@/lib/improvement-proposals';
import { isThisWeekJst, periodRange } from '@/lib/failures-period.mjs';
import { buildChatSessionHref } from '@/lib/chat-session-link.mjs';
import { failureTruncationNotices, isReformulatedFailure } from '@/lib/failures-selection.mjs';

type PeriodKey = '1' | '7' | '30' | 'custom' | 'all';
type TriageFilter = TriageStatus | 'all';

const PERIODS: { key: PeriodKey; label: string }[] = [
  { key: '1', label: '昨日' },
  { key: '7', label: '7 日' },
  { key: '30', label: '30 日' },
  { key: 'custom', label: '指定' },
  { key: 'all', label: '全期間' },
];

const KINDS: { key: FailureKind; label: string }[] = [
  { key: 'all', label: 'すべて' },
  { key: 'bad', label: '👎 bad' },
  { key: 'not_found', label: 'not_found' },
  { key: 'reformulated', label: '言い換え' },
];

const REASON_CHIP_ORDER: FeedbackReason[] = ['wrong_doc', 'unresolved', 'bad_answer', 'other', 'wrong_page'];
const REFORMULATED_EMPTY_NOTICE = '言い換えは #111（RAG の記録）のデプロイ後から記録されます';

const REASON_FILTERS: { key: ReasonFilterKey; label: string }[] = [
  { key: 'all', label: '理由: すべて' },
  { key: 'wrong_doc', label: '資料が違う' },
  { key: 'unresolved', label: '疑問が解けない' },
  { key: 'bad_answer', label: '回答がおかしい' },
  { key: 'other', label: 'その他' },
  { key: 'wrong_page', label: '頁（旧）' },
  { key: 'reason_omitted', label: '理由なし 👎' },
];

const TRIAGE_FILTERS: { key: TriageFilter; label: string }[] = [
  { key: 'open', label: '未振り分け' },
  { key: 'in_progress', label: '対応中' },
  { key: 'done', label: '対応済み' },
  { key: 'wontfix', label: '対応しない' },
  { key: 'all', label: 'すべて' },
];

const TRIAGE_CLS: Record<TriageStatus, string> = {
  open: 'border-gray-700 text-gray-900 bg-white',
  in_progress: 'border-blue-300 text-blue-800 bg-blue-50',
  done: 'border-gray-300 text-gray-500 bg-gray-50',
  wontfix: 'border-gray-300 text-gray-500 bg-gray-50',
};

function formatTs(iso: string): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('ja-JP', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
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

function triageOf(item: { triage?: Triage }): Triage {
  return item.triage ?? { status: 'open' };
}

/**
 * 失敗・改善提案 v2（設計 docs/design-2026-09-10-dashboard-v2.md §9）。
 * 期間で絞り、1 件ずつ振り分けを記録する。週次レビューのゴールは未振り分けを 0 にすること（部分取得時は表示中の範囲）。
 */
export default function AdminFailuresPage() {
  const [period, setPeriod] = useState<PeriodKey>('7');
  const [customSince, setCustomSince] = useState('');
  const [customUntil, setCustomUntil] = useState('');
  const [triageFilter, setTriageFilter] = useState<TriageFilter>('all');
  const [kind, setKind] = useState<FailureKind>('all');
  const [reasonFilter, setReasonFilter] = useState<ReasonFilterKey>('all');
  const [allItems, setAllItems] = useState<FailureItem[]>([]);
  const [wishes, setWishes] = useState<ProductWish[]>([]);
  const [note, setNote] = useState<string | null>(null);
  const [wishesError, setWishesError] = useState<string | null>(null);
  const [scannedCount, setScannedCount] = useState(0);
  const [incomplete, setIncomplete] = useState(false);
  const [truncationNotices, setTruncationNotices] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showOpsGuide, setShowOpsGuide] = useState(false);
  const [drafts, setDrafts] = useState<Record<string, TriageInput>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  const range = useMemo(() => {
    if (period === 'custom') return { since: customSince || null, until: customUntil || null };
    return periodRange(period);
  }, [period, customSince, customUntil]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setWishesError(null);
    try {
      const [failRes, refRes] = await Promise.all([
        getChatFailures('all', 100, { since: range.since, until: range.until }),
        getChatFailures('reformulated', 100, { since: range.since, until: range.until }),
      ]);
      const seen = new Set<string>();
      const reformulatedFailures = (refRes.failures || []).filter(isReformulatedFailure);
      const merged = [...(failRes.failures || []), ...reformulatedFailures].filter((it) => {
        if (seen.has(it.messageId)) return false;
        seen.add(it.messageId);
        return true;
      });
      merged.sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''));
      setAllItems(merged);
      setNote(failRes.note || null);
      setScannedCount(failRes.scannedCount || 0);
      setIncomplete(Boolean(failRes.incomplete || refRes.incomplete));
      setTruncationNotices(failureTruncationNotices(failRes, refRes));
      setDrafts({});
      try {
        const wishRes = await getAdminSuggestions(30);
        setWishes(wishRes.wishes || []);
      } catch (wishErr) {
        setWishes([]);
        setWishesError((wishErr as Error).message || '要望一覧の取得に失敗しました');
      }
    } catch (e) {
      setError((e as Error).message);
      setAllItems([]);
      setIncomplete(false);
      setTruncationNotices([]);
    } finally {
      setLoading(false);
    }
  }, [range.since, range.until]);

  useEffect(() => {
    load();
  }, [load]);

  // ダッシュボード「到達できず」からの導線: /admin/failures?since=YYYY-MM-DD
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const since = params.get('since');
    if (since) {
      setPeriod('custom');
      setCustomSince(since);
      setCustomUntil(params.get('until') || since);
      const k = params.get('kind') as FailureKind | null;
      if (k && KINDS.some((x) => x.key === k)) setKind(k);
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const unresolvedItems = useMemo(() => allItems.filter(isUnresolved), [allItems]);
  const summary = useMemo(() => aggregateFailureSignals(allItems), [allItems]);
  const proposals = useMemo(() => buildImprovementProposals(summary), [summary]);
  const items = useMemo(() => {
    const byKind = filterFailureItems(allItems, kind, reasonFilter);
    if (triageFilter === 'all') return byKind;
    return byKind.filter((i) => triageOf(i).status === triageFilter);
  }, [allItems, kind, reasonFilter, triageFilter]);

  const work = useMemo(() => {
    const open = allItems.filter((i) => triageOf(i).status === 'open').length;
    const inProgress = allItems.filter((i) => triageOf(i).status === 'in_progress').length;
    const doneThisWeek = allItems.filter((i) => triageOf(i).status === 'done' && isThisWeekJst(triageOf(i).at)).length;
    const causes: Record<string, number> = {};
    for (const i of allItems) {
      const t = triageOf(i);
      if (t.status === 'done' && t.cause && isThisWeekJst(t.at)) causes[t.cause] = (causes[t.cause] || 0) + 1;
    }
    const wishesUnread = wishes.filter((w) => triageOf(w).status === 'open').length;
    return { open, inProgress, doneThisWeek, causes, wishesUnread };
  }, [allItems, wishes]);

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
    setKind('bad');
    setReasonFilter(reason);
  };

  const resetFilters = () => {
    setKind('all');
    setReasonFilter('all');
    setTriageFilter('all');
  };

  const hasActiveFilter = kind !== 'all' || reasonFilter !== 'all' || triageFilter !== 'all';

  const nearThresholdSignals = useMemo(() => {
    const candidates: { label: string; count: number; onClick: () => void }[] = [];
    for (const reason of REASON_CHIP_ORDER) {
      const count = summary.reasonCounts[reason] || 0;
      if (count > 0 && count < IMPROVEMENT_PROPOSAL_THRESHOLD) {
        candidates.push({ label: FEEDBACK_REASON_LABELS[reason], count, onClick: () => applyReasonChip(reason) });
      }
    }
    if (summary.notFoundCount > 0 && summary.notFoundCount < IMPROVEMENT_PROPOSAL_THRESHOLD) {
      candidates.push({ label: 'not_found', count: summary.notFoundCount, onClick: () => { setKind('not_found'); setReasonFilter('all'); } });
    }
    if (summary.badWithoutReason > 0 && summary.badWithoutReason < IMPROVEMENT_PROPOSAL_THRESHOLD) {
      candidates.push({ label: '理由なし 👎', count: summary.badWithoutReason, onClick: () => applyReasonChip('reason_omitted') });
    }
    if (summary.reformulatedCount > 0) {
      candidates.push({ label: '言い換え（暗黙の失敗。カードのルールは v1 で）', count: summary.reformulatedCount, onClick: () => { setKind('reformulated'); setReasonFilter('all'); } });
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

  const draftFor = (item: FailureItem): TriageInput => {
    const t = triageOf(item);
    return drafts[item.messageId] ?? { status: t.status, cause: t.cause ?? '', note: t.note ?? '', ref: t.ref ?? '' };
  };

  const setDraft = (item: FailureItem, patch: Partial<TriageInput>) => {
    setDrafts((prev) => ({ ...prev, [item.messageId]: { ...draftFor(item), ...patch } }));
  };

  const saveTriage = async (item: FailureItem, override?: Partial<TriageInput>) => {
    const input = { ...draftFor(item), ...override };
    setSavingId(item.messageId);
    setError(null);
    try {
      const saved = await updateTriage(item.sessionId, item.messageId, input);
      setAllItems((prev) => prev.map((i) => (i.messageId === item.messageId ? { ...i, triage: saved } : i)));
      setDrafts((prev) => {
        const next = { ...prev };
        delete next[item.messageId];
        return next;
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSavingId(null);
    }
  };

  const saveWishTriage = async (w: ProductWish, status: TriageStatus) => {
    if (!w.sessionId) return;
    setSavingId(w.messageId);
    setError(null);
    try {
      const saved = await updateTriage(w.sessionId, w.messageId, { status });
      setWishes((prev) => prev.map((x) => (x.messageId === w.messageId ? { ...x, triage: saved } : x)));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSavingId(null);
    }
  };

  const rangeLabel =
    range.since && range.until ? `${range.since}〜${range.until}` : range.since ? `${range.since} 以降` : '全期間';

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
        <div>
          <h2 className="text-xl font-bold text-gray-900">失敗・改善提案</h2>
          <p className="text-sm text-gray-500 mt-0.5">到達できなかった 1 件ずつをどう扱い、何を直したか。週次レビューのゴールは「未振り分けを 0 にする」</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button type="button" onClick={load} className="px-3 py-1.5 text-sm rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50">
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

      {/* 絞り込み */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mb-3 text-sm">
        <span className="flex items-center gap-2 text-xs text-gray-500">
          期間
          <SegmentedControl aria-label="期間" options={PERIODS.map((p) => ({ value: p.key, label: p.label }))} value={period} onChange={(v) => setPeriod(v as PeriodKey)} />
        </span>
        {period === 'custom' && (
          <span className="flex items-center gap-1 text-xs text-gray-600">
            <input type="date" value={customSince} onChange={(e) => setCustomSince(e.target.value)} className="border border-gray-300 rounded-md px-2 py-1 bg-white" />
            〜
            <input type="date" value={customUntil} onChange={(e) => setCustomUntil(e.target.value)} className="border border-gray-300 rounded-md px-2 py-1 bg-white" />
          </span>
        )}
        <label className="flex items-center gap-2 text-xs text-gray-500">
          状態
          <select value={triageFilter} onChange={(e) => setTriageFilter(e.target.value as TriageFilter)} className="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white text-gray-800">
            {TRIAGE_FILTERS.map((t) => (
              <option key={t.key} value={t.key}>
                {t.label}
              </option>
            ))}
          </select>
        </label>
        <span className="flex items-center gap-2 text-xs text-gray-500">
          種類
          <SegmentedControl aria-label="失敗の種類" options={KINDS.map((k) => ({ value: k.key, label: k.label }))} value={kind} onChange={(v) => setKind(v as FailureKind)} />
        </span>
        <select value={reasonFilter} onChange={(e) => setReasonFilter(e.target.value as ReasonFilterKey)} className="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white" aria-label="理由で絞り込み">
          {REASON_FILTERS.map((r) => (
            <option key={r.key} value={r.key}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      {/* 作業量の帯 */}
      {(incomplete || truncationNotices.length > 0) && (
        <p className="mb-2 text-xs text-amber-800">
          件数は表示中の範囲（先頭 100 件／走査済みの範囲）の数です。
        </p>
      )}
      <div className="grid grid-cols-2 md:grid-cols-4 rounded-lg border border-gray-200 bg-white divide-x divide-gray-200 mb-6">
        <div className="px-4 py-3 bg-blue-50/60">
          <div className="text-[11px] text-gray-500">未振り分け</div>
          <div className="text-xl font-semibold tabular-nums">
            {work.open} <span className="text-[11px] font-normal text-gray-500">件 → {(incomplete || truncationNotices.length > 0) ? '表示中の範囲で ' : ''}0 にするのが週次のゴール</span>
          </div>
        </div>
        <div className="px-4 py-3">
          <div className="text-[11px] text-gray-500">対応中</div>
          <div className="text-xl font-semibold tabular-nums">{work.inProgress}</div>
        </div>
        <div className="px-4 py-3">
          <div className="text-[11px] text-gray-500">今週 対応済み</div>
          <div className="text-xl font-semibold tabular-nums">
            {work.doneThisWeek}
            {Object.keys(work.causes).length > 0 && (
              <span className="text-[11px] font-normal text-gray-500 ml-1">
                原因: {Object.entries(work.causes).map(([c, n]) => `${TRIAGE_CAUSE_LABELS[c as TriageCause] ?? c} ${n}`).join(' · ')}
              </span>
            )}
          </div>
        </div>
        <div className="px-4 py-3">
          <div className="text-[11px] text-gray-500">要望（未読）</div>
          <div className="text-xl font-semibold tabular-nums">{work.wishesUnread}</div>
        </div>
      </div>

      {/* 改善提案パネル */}
      <section className="mb-6 rounded-lg border border-blue-200 bg-blue-50/40 p-4">
        <div className="flex flex-wrap items-start justify-between gap-2 mb-3">
          <div>
            <h3 className="text-sm font-bold text-blue-950">改善提案（ルール v0）</h3>
            <p className="text-xs text-blue-900/80 mt-0.5">
              {rangeLabel} の未対応 {summary.total} 件（取得 {allItems.length} 件、うち未対応 {unresolvedItems.length}。集計は各一覧の先頭 100 件内）から集計。件数≥{IMPROVEMENT_PROPOSAL_THRESHOLD} でカード表示（出荷判断は第1層 eval のまま）
            </p>
          </div>
          <button type="button" onClick={() => setShowOpsGuide((v) => !v)} className="text-xs text-blue-800 underline underline-offset-2">
            {showOpsGuide ? '運用ガイドを閉じる' : '運用ガイド'}
          </button>
        </div>

        <dl className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-3 text-xs">
          {[
            ['👎', summary.badCount],
            ['not_found', summary.notFoundCount],
            ['言い換え', summary.reformulatedCount],
            ['理由なし 👎', summary.badWithoutReason],
            ['要望（文字）', wishes.length],
          ].map(([k, v]) => (
            <div key={String(k)} className="rounded bg-white/80 px-2 py-1.5 border border-blue-100">
              <dt className="text-gray-500">{k}</dt>
              <dd className="font-semibold text-gray-900 tabular-nums">{v}</dd>
            </div>
          ))}
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
                  className={`text-[11px] px-2 py-1 rounded-full border transition-colors ${active ? 'bg-blue-700 text-white border-blue-700' : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300'}`}
                >
                  {FEEDBACK_REASON_LABELS[reason]} · {count}
                </button>
              );
            })}
            {summary.badWithoutReason > 0 && (
              <button
                type="button"
                onClick={() => applyReasonChip('reason_omitted')}
                className={`text-[11px] px-2 py-1 rounded-full border transition-colors ${kind === 'bad' && reasonFilter === 'reason_omitted' ? 'bg-blue-700 text-white border-blue-700' : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300'}`}
              >
                理由なし 👎 · {summary.badWithoutReason}
              </button>
            )}
            {summary.notFoundCount > 0 && (
              <button
                type="button"
                onClick={() => { setKind('not_found'); setReasonFilter('all'); }}
                className={`text-[11px] px-2 py-1 rounded-full border transition-colors ${kind === 'not_found' ? 'bg-amber-700 text-white border-amber-700' : 'bg-white text-gray-700 border-gray-200 hover:border-amber-300'}`}
              >
                not_found · {summary.notFoundCount}
              </button>
            )}
          </div>
        )}

        {showOpsGuide && (
          <div className="mb-3 text-xs text-blue-950/90 bg-white/70 rounded-md border border-blue-100 px-3 py-2 space-y-1">
            <p>週次: failures → 未振り分けを 0 に → golden 追加 → run_retrieve_eval.py → 悪化なしなら PR</p>
            <p>
              <code className="text-[11px]">unresolved</code> は KB 悪と決め打ちせず、件ごとに検索／snippet／作文／KB を振り分け（原因を選んで保存）
            </p>
            <p>ヒントは機械的な手がかりであって判断ではない。第1層の主指標は <code className="text-[11px]">hit_in_candidates</code>（ラベル済み）</p>
          </div>
        )}

        {proposals.length === 0 ? (
          <div className="text-xs text-gray-600 space-y-1.5">
            <p>しきい値（{IMPROVEMENT_PROPOSAL_THRESHOLD} 件）未満のため定型提案はありません。信号が増えたらここにカードが出ます。</p>
            {nearThresholdSignals.length > 0 && (
              <p className="text-gray-500">
                注目:{' '}
                {nearThresholdSignals.map((s, i) => (
                  <span key={s.label}>
                    {i > 0 ? ' / ' : ''}
                    <button type="button" onClick={s.onClick} className="underline underline-offset-2 hover:text-blue-800">
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
              <li key={p.id} className="rounded-md border border-blue-200 bg-white p-3 text-sm">
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
                  <button type="button" onClick={() => applyProposalFilter(p)} className="shrink-0 text-xs px-2.5 py-1 rounded-md border border-blue-300 bg-blue-50 text-blue-900 hover:bg-blue-100">
                    該当を見る
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span className="text-xs text-gray-500">
          表示 {items.length} / 取得 {allItems.length}（{rangeLabel}）
        </span>
        {hasActiveFilter && (
          <button type="button" onClick={resetFilters} className="text-xs text-blue-800 underline underline-offset-2">
            絞り込みを解除
          </button>
        )}
      </div>

      {incomplete && (
        <div className="mb-4 rounded border border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-900">
          Scan が打ち切られたため一覧は不完全です。欠けているのは最新分とは限らず、任意の範囲の失敗が含まれていない可能性があります。
        </div>
      )}

      {truncationNotices.length > 0 && (
        <div className="mb-4 rounded border border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-900">
          {truncationNotices.map((notice) => <p key={notice}>{notice}</p>)}
        </div>
      )}

      {note && (
        <p className="mb-4 text-xs text-gray-500 bg-gray-50 border border-gray-200 rounded-md px-3 py-2">
          {note}
          {scannedCount > 0 ? `（scan ${scannedCount}）` : ''}
        </p>
      )}

      {error && <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">{error}</div>}

      {loading ? (
        <div className="p-12 flex justify-center">
          <Loading size="lg" text="失敗ログを読み込み中..." />
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white px-6 py-12 text-center text-sm text-gray-500">
          該当する失敗はありません（期間・フィルタ条件を変えるか、現場で 👎 / not_found / 要望フォームを使ってください）。
          {kind === 'reformulated' && <p className="mt-2">{REFORMULATED_EMPTY_NOTICE}</p>}
        </div>
      ) : (
        <ul className="space-y-3">
          {items.map((item, index) => {
            const t = triageOf(item);
            const draft = draftFor(item);
            const busy = savingId === item.messageId;
            return (
              <li key={`${item.sessionId}-${item.messageId}`} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                  <div className="flex flex-wrap items-center gap-1.5">
                    {item.signals.map((s) => (
                      <span
                        key={s}
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                          s === 'bad' ? 'bg-red-50 text-red-700 border-red-200' : s === 'not_found' ? 'bg-amber-50 text-amber-800 border-amber-200' : 'bg-white text-gray-700 border-dashed border-gray-400'
                        }`}
                      >
                        {s === 'reformulated' ? '↻ 言い換え' : s}
                      </span>
                    ))}
                    {item.feedbackReason && (
                      <span className="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                        {FEEDBACK_REASON_LABELS[item.feedbackReason as FeedbackReason] || item.feedbackReason}
                      </span>
                    )}
                    <span className="text-[11px] text-gray-400">{formatTs(item.timestamp)}</span>
                  </div>
                  <div className="flex gap-2">
                    {item.sessionId && (
                      <Link href={buildChatSessionHref(item.sessionId, item.ragMode)} className="text-xs px-2.5 py-1 rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50">
                        チャットで開く
                      </Link>
                    )}
                    <button type="button" onClick={() => copyGolden(item, index)} className="text-xs px-2.5 py-1 rounded-md border border-blue-200 bg-blue-50 text-blue-800 hover:bg-blue-100">
                      {copiedId === item.messageId ? 'コピー済み' : 'ゴールデン候補をコピー'}
                    </button>
                  </div>
                </div>

                <p className="text-sm text-gray-900 font-medium whitespace-pre-wrap break-words">{item.userQuery || '（直前の質問を取得できませんでした）'}</p>
                {item.assistantPreview && (
                  <p className="mt-1.5 text-xs text-gray-600 line-clamp-2 bg-gray-50 rounded px-2 py-1 border border-gray-100">
                    回答: {item.assistantPreview}
                    {(item.assistantPreview.length || 0) >= 120 ? '…' : ''}
                  </p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  {filtersLabel(item)}
                  {item.feedbackComment && <span className="ml-3">コメント: {item.feedbackComment}</span>}
                </p>
                {item.topDocuments?.length > 0 && (
                  <p className="mt-1 text-xs text-gray-600">
                    候補資料: <span className="font-mono">{item.topDocuments.slice(0, 5).join(', ')}</span>
                  </p>
                )}

                {/* ヒント */}
                {item.hints && item.hints.length > 0 && (
                  <div className="mt-2 flex flex-wrap items-center gap-1.5">
                    <span className="text-[11px] text-gray-500">ヒント</span>
                    {item.hints.map((h) => (
                      <span key={h} className="text-[11.5px] rounded border border-blue-200 bg-blue-50 text-blue-800 px-1.5 py-0.5">
                        ◇ {h}
                      </span>
                    ))}
                  </div>
                )}

                {/* 検索の要約 */}
                <div className="mt-2 text-[11.5px] text-gray-600 flex flex-wrap gap-x-3 gap-y-1">
                  <span className="text-gray-500">検索の要約</span>
                  {item.traceSummary ? (
                    <>
                      <span>候補 <b className="font-mono">{item.traceSummary.mergedCount}</b></span>
                      <span>選択 <b className="font-mono">{item.traceSummary.selectedCount}</b></span>
                      <span>機種除外 <b className="font-mono">{item.traceSummary.excludedByModelScope}</b></span>
                      <span>上位スコア <b className="font-mono">{item.traceSummary.topScore === null ? '—' : item.traceSummary.topScore.toFixed(2)}</b></span>
                      {item.traceSummary.latencyMs?.retrieve !== undefined && <span>retrieve <b className="font-mono">{item.traceSummary.latencyMs.retrieve} ms</b></span>}
                    </>
                  ) : (
                    <span className="text-gray-400">トレース実装後に表示</span>
                  )}
                  <span>
                    資料を開いた <b className="font-mono">{item.opened != null ? `${item.opened} 件` : '—'}</b>
                  </span>
                </div>

                {/* 振り分け */}
                <div className="mt-3 pt-2 border-t border-gray-100 grid grid-cols-1 md:grid-cols-[auto_auto_minmax(160px,1fr)_auto_auto] gap-2 items-center">
                  <span className={`inline-flex items-center rounded border px-2 py-0.5 text-[11px] font-semibold whitespace-nowrap ${TRIAGE_CLS[t.status]}`} title={t.by && t.at ? `${t.by.slice(0, 8)} · ${formatTs(t.at)}` : undefined}>
                    {TRIAGE_STATUS_LABELS[t.status]}
                  </span>
                  <select
                    aria-label="原因"
                    value={draft.cause ?? ''}
                    onChange={(e) => setDraft(item, { cause: e.target.value as TriageCause | '' })}
                    className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white"
                  >
                    <option value="">原因を選ぶ</option>
                    {(Object.keys(TRIAGE_CAUSE_LABELS) as TriageCause[]).map((c) => (
                      <option key={c} value={c}>
                        {TRIAGE_CAUSE_LABELS[c]}
                      </option>
                    ))}
                  </select>
                  <input
                    type="text"
                    aria-label="メモ"
                    maxLength={TRIAGE_NOTE_MAX}
                    placeholder={`メモ（${TRIAGE_NOTE_MAX} 字まで）`}
                    value={draft.note ?? ''}
                    onChange={(e) => setDraft(item, { note: e.target.value })}
                    className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white min-w-0"
                  />
                  <input
                    type="text"
                    aria-label="参照"
                    placeholder="参照 #issue / G0xx / commit"
                    value={draft.ref ?? ''}
                    onChange={(e) => setDraft(item, { ref: e.target.value })}
                    className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white w-full md:w-44"
                  />
                  <span className="flex gap-1.5">
                    <select
                      aria-label="状態"
                      value={draft.status}
                      onChange={(e) => setDraft(item, { status: e.target.value as TriageStatus })}
                      className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white"
                    >
                      {(Object.keys(TRIAGE_STATUS_LABELS) as TriageStatus[]).map((s) => (
                        <option key={s} value={s}>
                          {TRIAGE_STATUS_LABELS[s]}
                        </option>
                      ))}
                    </select>
                    <button type="button" disabled={busy} onClick={() => saveTriage(item)} className="text-xs px-2.5 py-1 rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-40">
                      保存
                    </button>
                    {t.status !== 'done' && (
                      <button type="button" disabled={busy} onClick={() => saveTriage(item, { status: 'done' })} className="text-xs px-2.5 py-1 rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-40 whitespace-nowrap">
                        対応済みにする
                      </button>
                    )}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      )}

      {/* 利用者の文字フィードバック */}
      <section className="mt-8 rounded-lg border border-violet-200 bg-violet-50/30 p-4">
        <h3 className="text-sm font-bold text-violet-950 mb-2">
          こうなってほしい（利用者の文字）<span className="ml-2 text-xs font-normal text-gray-500">未読 {work.wishesUnread}</span>
        </h3>
        {wishesError ? (
          <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-950">
            <p className="font-medium">要望一覧を取得できませんでした</p>
            <p className="mt-1 text-amber-900/80">{wishesError}</p>
          </div>
        ) : wishes.length === 0 ? (
          <p className="text-xs text-gray-600">まだ投稿はありません。チャット画面右上の「こうなってほしい」から届きます。</p>
        ) : (
          <ul className="space-y-2 max-h-72 overflow-y-auto">
            {wishes.map((w) => {
              const t = triageOf(w);
              return (
                <li key={w.messageId} className="rounded-md border border-violet-100 bg-white px-3 py-2 text-sm">
                  <p className="text-gray-900 whitespace-pre-wrap break-words">{w.text}</p>
                  <p className="text-[11px] text-gray-500 mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
                    <span>{formatTs(w.timestamp)}</span>
                    {w.contextSessionId && (
                      <Link href={buildChatSessionHref(w.contextSessionId, w.ragMode)} className="text-blue-700 underline">
                        関連セッション
                      </Link>
                    )}
                    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[11px] font-semibold ${TRIAGE_CLS[t.status]}`}>
                      {t.status === 'open' ? '未読' : t.status === 'in_progress' ? '既読' : TRIAGE_STATUS_LABELS[t.status]}
                    </span>
                    {w.sessionId && t.status === 'open' && (
                      <button type="button" disabled={savingId === w.messageId} onClick={() => saveWishTriage(w, 'in_progress')} className="underline underline-offset-2 hover:text-violet-800 disabled:opacity-40">
                        既読にする
                      </button>
                    )}
                    {w.sessionId && t.status !== 'done' && (
                      <button type="button" disabled={savingId === w.messageId} onClick={() => saveWishTriage(w, 'done')} className="underline underline-offset-2 hover:text-violet-800 disabled:opacity-40">
                        対応済みにする
                      </button>
                    )}
                  </p>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
