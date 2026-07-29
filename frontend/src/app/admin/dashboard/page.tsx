'use client';

import { useEffect, useState } from 'react';
import { getMetrics, MetricsResponse, MetricPeriod, STATUS_META, formatPct } from '@/lib/metrics';
import {
  ChartCard,
  StatTile,
  TimeBars,
  RateLine,
  DocRanking,
  SimpleTable,
} from '@/components/dashboard/charts';
import { Loading } from '@/components/ui/Loading';

const PERIODS: { key: MetricPeriod; label: string }[] = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '今週' },
  { key: 'month', label: '今月' },
];

export default function DashboardPage() {
  const [period, setPeriod] = useState<MetricPeriod>('week');
  const [data, setData] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setError(null);
    getMetrics(period)
      .then((res) => alive && setData(res))
      .catch((e) => alive && setError((e as Error).message))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [period]);

  const updatedAt = data?.generatedAt
    ? new Date(data.generatedAt).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
    : '—';

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">運用ダッシュボード</h2>
          <p className="text-sm text-gray-500 mt-0.5">利用状況とシステム健全性のサマリー</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="inline-flex rounded-lg bg-gray-100 p-1" role="tablist" aria-label="期間">
            {PERIODS.map((p) => (
              <button
                key={p.key}
                role="tab"
                aria-selected={period === p.key}
                onClick={() => setPeriod(p.key)}
                className={`px-3 py-1 text-sm rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  period === p.key ? 'bg-white font-semibold text-blue-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
          <span className="text-xs text-gray-500">最終更新 {updatedAt}</span>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">
          データを読み込めませんでした：{error}
        </div>
      )}

      {loading ? (
        <div className="p-12 flex justify-center">
          <Loading size="lg" text="集計データを読み込み中..." />
        </div>
      ) : data ? (
        <div className="space-y-6">
          {/* KPI row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatTile
              label="いいね率"
              value={formatPct(data.kpi.likeRate.value)}
              delta={data.kpi.likeRate.delta}
              deltaLabel={
                data.kpi.likeRate.delta
                  ? `${Math.abs(Math.round(data.kpi.likeRate.delta * 100))}pt`
                  : undefined
              }
            />
            <StatTile
              label="総クエリ数"
              value={data.kpi.queries.value.toLocaleString('ja-JP')}
              delta={data.kpi.queries.delta}
              deltaLabel={
                data.kpi.queries.delta ? `${Math.abs(Math.round(data.kpi.queries.delta))}` : undefined
              }
            />
            <StatTile
              label="アクティブユーザー"
              value={`${data.kpi.activeUsers.value}`}
              sublabel="期間内の一意ユーザー数"
            />
          </div>

          {/* Two SEPARATE time charts (never dual-axis) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ChartCard
              title="クエリ数の推移"
              subtitle="日別・棒グラフ（1軸）"
              table={
                <SimpleTable
                  columns={['日付', 'クエリ数']}
                  rows={data.series.queriesByDay.map((d) => [d.date, d.value])}
                />
              }
            >
              <TimeBars data={data.series.queriesByDay} />
            </ChartCard>

            <ChartCard
              title="いいね率の推移"
              subtitle="日別・折れ線（0–100%・目標85%）"
              table={
                <SimpleTable
                  columns={['日付', 'いいね率']}
                  rows={data.series.likeRateByDay.map((d) => [d.date, `${Math.round(d.value * 100)}%`])}
                />
              }
            >
              <RateLine data={data.series.likeRateByDay} target={0.85} />
            </ChartCard>
          </div>

          {/* Health + document ranking */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ChartCard title="障害状況" subtitle="直近スナップショット">
              <HealthPanel health={data.health} />
            </ChartCard>

            <ChartCard
              title="参照文書 TOP5"
              subtitle="期間内のヒット件数"
              table={
                <SimpleTable
                  columns={['#', '文書', '件数']}
                  rows={data.topDocuments.map((d, i) => [i + 1, d.name, d.count])}
                />
              }
            >
              <DocRanking data={data.topDocuments} />
            </ChartCard>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function HealthPanel({ health }: { health: MetricsResponse['health'] }) {
  const rows = [
    { label: 'エラー率', ...health.errorRate, fmt: (v: number) => `${(v * 100).toFixed(1)}%` },
    { label: 'p90レイテンシ', ...health.latencyP90, fmt: (v: number) => `${v.toFixed(1)}s` },
    { label: '5xxエラー', ...health.http5xx, fmt: (v: number) => `${v}件` },
  ];
  return (
    <div className="space-y-2">
      {rows.map((r) => {
        const meta = STATUS_META[r.status];
        return (
          <div
            key={r.label}
            className={`flex items-center justify-between rounded border px-3 py-2 text-sm ${meta.className}`}
          >
            <span className="flex items-center gap-2">
              <span aria-hidden style={{ color: meta.color }}>
                {meta.icon}
              </span>
              <span className="font-medium">{meta.label}</span>
              <span className="text-gray-600">{r.label}</span>
            </span>
            <span className="tabular-nums font-semibold">{r.fmt(r.value)}</span>
          </div>
        );
      })}
      <div className="flex items-center justify-between rounded border border-gray-200 px-3 py-2 text-sm">
        <span className="text-gray-600">未解決アラート</span>
        <span className="tabular-nums font-semibold">{health.openIncidents} 件</span>
      </div>
    </div>
  );
}
