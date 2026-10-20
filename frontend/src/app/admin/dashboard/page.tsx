'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { getDashboard, DashboardResponse, DashboardEvent, TrendDays, STATUS_META, HealthStatus } from '@/lib/metrics';
import {
  formatCount,
  formatDuration,
  formatSeconds,
  formatUsd,
  jstDateLabel,
  jstDateTime,
  jstTime,
  logsInsightsUrl,
} from '@/lib/metrics-format.mjs';
import { ChartCard, DocRanking, Legend, MsLines, PALETTE, SimpleTable, StackedBars } from '@/components/dashboard/charts';
import { StatusPill, SeverityBadge, CostBadge } from '@/components/dashboard/status';
import { Funnel } from '@/components/dashboard/funnel';
import { Loading } from '@/components/ui/Loading';

const TRENDS: TrendDays[] = [14, 30, 90];

/**
 * 運用ダッシュボード v2（設計: docs/design-2026-09-10-dashboard-v2.md §2）
 * 上から「いま」「昨日」「到達ファネル」「推移」「出来事」。期間タブは持たず、枠は固定。
 */
export default function DashboardPage() {
  const [trend, setTrend] = useState<TrendDays>(14);
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (days: TrendDays) => {
    setLoading(true);
    setError(null);
    try {
      setData(await getDashboard(days));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(trend);
  }, [trend, load]);

  return (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-3 mb-5">
        <div>
          <h2 className="text-xl font-bold text-gray-900">運用ダッシュボード</h2>
          <p className="text-sm text-gray-500 mt-0.5">昨日うまくいったか、今日直すものは何か。枠は「昨日」「7 日」「14 日」に固定</p>
        </div>
        {data && (
          <span className="text-xs text-gray-500 tabular-nums">
            最終更新 {jstTime(data.generatedAt)} · 前日確定 {jstTime(data.now.freshness.yesterdayAggregatedAt)}
            <button type="button" onClick={() => load(trend)} className="ml-3 text-blue-600 underline underline-offset-2">
              再読込
            </button>
          </span>
        )}
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">データを読み込めませんでした：{error}</div>
      )}

      {loading && !data ? (
        <div className="p-12 flex justify-center">
          <Loading size="lg" text="集計データを読み込み中..." />
        </div>
      ) : data ? (
        <div className="space-y-6">
          <Section title="いま" sub="ページを開いた瞬間に CloudWatch を直接読む">
            <NowStrip data={data} />
          </Section>

          <Section title={`昨日（${jstDateLabel(data.yesterday.date)}）`} sub="02:00 JST 確定。色はシステム信号にだけ付く">
            <YesterdayTiles data={data} />
            {data.todaySoFar && (
              <div className="mt-2 text-[13px] text-gray-600 flex flex-wrap gap-x-4 gap-y-1">
                <span>
                  今日ここまで（<span className="tabular-nums">{data.todaySoFar.asOf ?? '—'}</span> 時点）
                </span>
                <span>
                  質問 <b className="text-gray-900 tabular-nums">{formatCount(data.todaySoFar.queries)}</b>
                </span>
                <span>
                  到達できず <b className="text-gray-900 tabular-nums">{formatCount(data.todaySoFar.unreached)}</b>
                </span>
                <span>
                  5xx <b className="text-gray-900 tabular-nums">{formatCount(data.todaySoFar.http5xx)}</b>
                  {(data.todaySoFar.http5xx ?? 0) > 0 && <StatusPill status="warning" className="ml-1.5" />}
                </span>
              </div>
            )}
          </Section>

          <Section title="到達ファネル" sub="製品の成功定義「資料に到達し、疑問が解ける」を数える場所。比率の線は引かない">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              <Funnel
                title={`昨日（${jstDateLabel(data.yesterday.date, false)}）`}
                row={data.funnel.yesterday}
                showRates={false}
                minDenominator={data.thresholds.rateDenominatorMin}
              />
              <Funnel
                title={`直近 7 日（${jstDateLabel(data.funnel.last7dRange.from, false)}〜${jstDateLabel(data.funnel.last7dRange.to, false)}）`}
                row={data.funnel.last7d}
                showRates={data.funnel.showRates}
                minDenominator={data.thresholds.rateDenominatorMin}
              />
            </div>
          </Section>

          <Section
            title="推移"
            sub="1 軸ずつ。二軸は使わない"
            right={
              <div className="inline-flex rounded-md border border-gray-200 bg-gray-50 p-0.5" role="group" aria-label="日数">
                {TRENDS.map((t) => (
                  <button
                    key={t}
                    type="button"
                    aria-pressed={trend === t}
                    onClick={() => setTrend(t)}
                    className={`px-2.5 py-0.5 text-xs rounded ${trend === t ? 'bg-white text-blue-700 font-semibold shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
                  >
                    {t} 日
                  </button>
                ))}
              </div>
            }
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              <ChartCard
                title="質問数（到達できず を積み上げ）"
                subtitle="日別・JST"
                table={
                  <SimpleTable
                    columns={['日付', '質問', '到達できず']}
                    rows={[...data.trend.queriesByDay].reverse().map((d) => [jstDateLabel(d.date), d.total, d.unreached])}
                  />
                }
              >
                <Legend
                  items={[
                    { label: '到達した・その他', color: PALETTE.series1 },
                    { label: '到達できず（not_found + 👎）', color: PALETTE.warning },
                  ]}
                />
                <StackedBars data={data.trend.queriesByDay} />
              </ChartCard>
              <ChartCard
                title="rag 応答時間"
                subtitle={`API Gateway Latency・日別。基準線 ${data.thresholds.sloP90Ms / 1000} s（SLO / P2）・${data.thresholds.p1MaxMs / 1000} s（P1）`}
                table={
                  <SimpleTable
                    columns={['日付', 'p90 (s)', '最大 (s)']}
                    rows={[...data.trend.latencyByDay]
                      .reverse()
                      .map((d) => [jstDateLabel(d.date), d.p90Ms === null ? '—' : (d.p90Ms / 1000).toFixed(1), d.maxMs === null ? '—' : (d.maxMs / 1000).toFixed(1)])}
                  />
                }
              >
                <Legend
                  items={[
                    { label: 'p90', color: PALETTE.series1, line: true },
                    { label: '最大', color: PALETTE.series2, line: true },
                  ]}
                />
                <MsLines
                  data={data.trend.latencyByDay}
                  refLines={[
                    { valueMs: data.thresholds.sloP90Ms, label: `${data.thresholds.sloP90Ms / 1000} s SLO / P2` },
                    { valueMs: data.thresholds.p1MaxMs, label: `${data.thresholds.p1MaxMs / 1000} s P1` },
                  ]}
                />
              </ChartCard>
            </div>
          </Section>

          <Section title="出来事（直近 7 日）" sub="アラームの遷移を 1 列に。各行から Logs Insights へ時間範囲つきで飛ぶ">
            <EventList events={data.events} />
          </Section>

          <details className="group">
            <summary className="cursor-pointer text-sm font-semibold text-gray-600">参考（朝の判断には使わない）</summary>
            <div className="mt-3 grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-3">
              <ChartCard
                title="参照文書 TOP10"
                subtitle="直近 30 日・回答での引用回数"
                table={<SimpleTable columns={['#', '文書', '件数']} rows={data.reference.topDocuments.map((d, i) => [i + 1, d.name, d.count])} />}
              >
                <DocRanking data={data.reference.topDocuments} />
              </ChartCard>
              <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm">
                <h3 className="text-sm font-semibold text-gray-900">最終ゴールデン評価</h3>
                <p className="text-xs text-gray-500 mt-0.5 mb-2">週次・第 1 層（機械採点）</p>
                {data.reference.lastEval ? (
                  <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-[13px]">
                    <dt className="text-gray-500">実行日</dt>
                    <dd className="tabular-nums">{jstDateLabel(data.reference.lastEval.date)}</dd>
                    <dt className="text-gray-500">hit_in_candidates</dt>
                    <dd className="tabular-nums">
                      {formatCount(data.reference.lastEval.hit)} / {formatCount(data.reference.lastEval.n)}
                      <span className="text-gray-400">（ラベル済み N &lt; 10 では率を見ない）</span>
                    </dd>
                    {data.reference.lastEval.logicVersion && (
                      <>
                        <dt className="text-gray-500">logicVersion</dt>
                        <dd className="font-mono text-xs">{data.reference.lastEval.logicVersion}</dd>
                      </>
                    )}
                  </dl>
                ) : (
                  <p className="text-xs text-gray-400">評価の記録がありません（scope=eval の行が無い）</p>
                )}
              </div>
            </div>
          </details>
        </div>
      ) : null}
    </div>
  );
}

// ------------------------------------------------------------------ pieces
function Section({ title, sub, right, children }: { title: string; sub?: string; right?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section>
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 mb-2">
        <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide">{title}</h3>
        {sub && <span className="text-xs text-gray-500">{sub}</span>}
        {right && <span className="ml-auto">{right}</span>}
      </div>
      {children}
    </section>
  );
}

function NowStrip({ data }: { data: DashboardResponse }) {
  const now = data.now;
  const meta = STATUS_META[now.status];
  const cloudwatchUnavailable = now.cloudwatchAvailable === false || now.status === 'unknown';
  const heroLabel = cloudwatchUnavailable ? '取得できません（CloudWatch）' : now.status === 'good' ? '正常' : now.status === 'warning' ? '注意' : '重大';
  const crit = now.activeNotices.find((n) => n.severity === 'critical');
  const ragLabel =
    now.last60min.ragCount >= 10 && now.last60min.ragP90Ms !== null
      ? `p90 ${formatSeconds(now.last60min.ragP90Ms)}`
      : now.last60min.ragMaxMs !== null
        ? `最大 ${formatSeconds(now.last60min.ragMaxMs)}`
        : '—';

  return (
    <div className={`rounded-lg border border-gray-200 bg-white border-l-[5px] ${meta.stripe} grid grid-cols-1 md:grid-cols-[1.4fr_1fr_1fr] divide-y md:divide-y-0 md:divide-x divide-gray-200`}>
      <div className="p-4">
        <div className="text-[11px] uppercase tracking-wider text-gray-500 mb-1">現在</div>
        <div className="flex items-center gap-2.5">
          <span aria-hidden className="text-2xl leading-none" style={{ color: meta.color }}>
            {meta.icon}
          </span>
          <span className="text-2xl font-semibold leading-tight">{heroLabel}</span>
        </div>
        <div className="mt-2 flex flex-wrap gap-1">
          {cloudwatchUnavailable ? (
            <span className="text-xs text-gray-700">ALARM を取得できません（CloudWatch）</span>
          ) : now.alarms.length === 0 ? (
            <span className="text-xs text-gray-500">ALARM なし</span>
          ) : (
            now.alarms.map((a) => (
              <span
                key={a.name}
                title={a.since ? `${jstDateTime(a.since)} から ALARM` : undefined}
                className={`font-mono text-[11px] rounded border px-1.5 py-0.5 ${a.severity === 'P1' ? 'border-red-300 bg-red-50 text-red-800' : 'border-amber-300 bg-amber-50 text-amber-800'}`}
              >
                {a.name}
              </span>
            ))
          )}
        </div>
        <div className="mt-2 pt-2 border-t border-gray-100 text-xs text-gray-600 flex flex-wrap items-center gap-x-3 gap-y-1">
          {crit ? (
            <>
              <span>
                告知中: <b className="text-gray-900">{crit.title}</b>（{jstDateTime(crit.since)} から{crit.showInChat ? '・チャット表示' : ''}）
              </span>
              <Link href="/admin/announcements" className="text-blue-600 underline underline-offset-2">
                表示終了 / 更新 →
              </Link>
            </>
          ) : now.status === 'critical' ? (
            <Link href="/admin/announcements?template=incident" className="text-blue-600 underline underline-offset-2">
              利用者へ告知 →
            </Link>
          ) : (
            <>
              <span className="text-gray-500">告知中 {now.activeNotices.length} 件</span>
              <Link href="/admin/announcements" className="text-gray-500 underline underline-offset-2">
                お知らせ管理 →
              </Link>
            </>
          )}
        </div>
      </div>
      <div className="p-4">
        <div className="text-[11px] uppercase tracking-wider text-gray-500 mb-1">直近 60 分</div>
        <div className="flex gap-4">
          <Mini label="リクエスト" value={formatCount(now.last60min.requests)} />
          <Mini label="5xx" value={formatCount(now.last60min.http5xx)} status={now.last60min.http5xx > 0 ? 'warning' : undefined} />
          <Mini label={`rag 応答（${now.last60min.ragCount} 件）`} value={ragLabel} small />
        </div>
      </div>
      <div className="p-4 text-xs text-gray-600 space-y-1">
        <div className="text-[11px] uppercase tracking-wider text-gray-500 mb-1">鮮度</div>
        <div className="flex items-center gap-2">
          前日確定 <span className="tabular-nums">{jstTime(now.freshness.yesterdayAggregatedAt)}</span>
          <StatusPill status={now.freshness.status} extra={now.freshness.status !== 'good' ? '集計未完了' : undefined} />
        </div>
        <div>
          今日ここまで <span className="tabular-nums">{now.freshness.todayPartialAt ? jstTime(now.freshness.todayPartialAt) : '—'}</span> 更新（毎時）
        </div>
      </div>
    </div>
  );
}

function Mini({ label, value, status, small }: { label: string; value: string; status?: HealthStatus; small?: boolean }) {
  return (
    <div>
      <div className="text-[11px] text-gray-500 whitespace-nowrap">{label}</div>
      <div className={`font-semibold tabular-nums whitespace-nowrap ${small ? 'text-sm pt-1' : 'text-lg'}`}>
        {value}
        {status && <StatusPill status={status} className="ml-1.5 align-middle" />}
      </div>
    </div>
  );
}

function Tile({
  status,
  label,
  value,
  children,
}: {
  status?: HealthStatus;
  label: string;
  value: React.ReactNode;
  children?: React.ReactNode;
}) {
  const stripe = status ? STATUS_META[status].stripe : 'border-l-gray-200';
  return (
    <div className={`rounded-lg border border-gray-200 bg-white p-3.5 border-l-4 ${stripe}`}>
      <div className="flex items-center justify-between gap-2 text-[11px] text-gray-500 min-h-[20px]">
        <span>{label}</span>
        {status && <StatusPill status={status} />}
      </div>
      <div className="mt-1 text-2xl font-semibold tabular-nums leading-tight">{value}</div>
      <div className="mt-1.5 text-xs text-gray-600 space-y-0.5">{children}</div>
    </div>
  );
}

function YesterdayTiles({ data }: { data: DashboardResponse }) {
  const y = data.yesterday;
  if (!y.exists) {
    return (
      <div className="rounded-lg border border-dashed border-amber-300 bg-amber-50 px-4 py-6 text-sm text-amber-900">
        {jstDateLabel(y.date)} の集計行がありません。02:00 JST の日次集計が動いていない可能性があります（ランブック §5.4: <code className="text-xs">metrics-aggregator</code> を{' '}
        <code className="text-xs">{`{"date": "${y.date}"}`}</code> で手動 invoke）。
      </div>
    );
  }
  const lat = y.latency;
  const latMain = lat.showP90 && lat.p90Ms !== null ? `p90 ${formatSeconds(lat.p90Ms)}` : lat.p50Ms !== null ? `中央値 ${formatSeconds(lat.p50Ms)}` : '—';
  const byApi = Object.entries(y.incidents.byApi)
    .map(([k, v]) => `${k} ${v}`)
    .join(' · ');
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
      <Tile status={y.incidents.status} label="障害" value={<>{formatCount(y.incidents.p1Transitions)} <span className="text-sm text-gray-400">/</span> {formatCount(y.incidents.http5xx)}</>}>
        <div>P1 遷移 / 5xx 件数</div>
        <div className="text-gray-400">{byApi || '内訳なし'}</div>
      </Tile>
      <Tile status={lat.status} label="応答時間" value={latMain}>
        <div>
          最大 <span className="tabular-nums">{formatSeconds(lat.maxMs)}</span>
          {lat.count !== null && (
            <>
              {' '}
              · <span className="tabular-nums">{lat.count}</span> 件
            </>
          )}
        </div>
        <div className="text-gray-400">{lat.showP90 ? 'p90 は件数 10 以上のときだけ' : '件数 10 未満のため中央値と最大'}</div>
      </Tile>
      <Tile label="到達できず" value={<>{formatCount(y.unreached.total)} <span className="text-sm text-gray-400">件</span></>}>
        <div>
          not_found <span className="tabular-nums">{formatCount(y.unreached.notFound)}</span> · 👎 <span className="tabular-nums">{formatCount(y.unreached.bad)}</span>
          {y.unreached.reformulated !== null && (
            <>
              {' '}
              · 言い換え <span className="tabular-nums">{formatCount(y.unreached.reformulated)}</span>
            </>
          )}
        </div>
        <div>
          {y.unreached.open !== null && (
            <>
              未振り分け <b className="tabular-nums text-gray-900">{formatCount(y.unreached.open)}</b> ·{' '}
            </>
          )}
          <Link href={`/admin/failures?since=${y.date}`} className="text-blue-600 underline underline-offset-2">
            失敗一覧で見る →
          </Link>
        </div>
      </Tile>
      <Tile label="利用" value={<>{formatCount(y.usage.queries)} <span className="text-sm text-gray-400">質問</span></>}>
        <div>
          利用者 <span className="tabular-nums">{formatCount(y.usage.uniqueUsers)}</span> · 初めて <span className="tabular-nums">{formatCount(y.usage.newUsers)}</span>
        </div>
        <div className="text-gray-400">
          先週同曜日: <span className="tabular-nums">{formatCount(y.usage.queriesSameWeekdayLastWeek)}</span> 質問
        </div>
      </Tile>
      <Tile
        status={y.bedrockCost.status}
        label="Bedrock 費"
        value={
          <>
            <CostBadge kind="estimate" className="align-middle mr-1" />
            {formatUsd(y.bedrockCost.estimatedUsd)}
          </>
        }
      >
        <div>
          今月 <CostBadge kind="actual" /> <span className="tabular-nums">{formatUsd(y.bedrockCost.monthActualUsd)}</span>
        </div>
        <div className="text-gray-400">
          {y.bedrockCost.actualThrough ? `${jstDateLabel(y.bedrockCost.actualThrough, false)} まで確定 · ` : '実額は未取得 · '}
          <Link href="/admin/cost" className="text-blue-600 underline underline-offset-2">
            コストへ →
          </Link>
        </div>
      </Tile>
    </div>
  );
}

function EventList({ events }: { events: DashboardEvent[] }) {
  if (events.length === 0) {
    return <div className="rounded-lg border border-gray-200 bg-white px-4 py-5 text-sm text-gray-500">直近 7 日にアラームの遷移はありません。</div>;
  }
  return (
    <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
      {events.map((e) => {
        const open = e.kind === 'alarm' && e.resolvedAt === null;
        const url = logsInsightsUrl({ logGroup: e.logGroup, from: e.from, to: e.to });
        const hint = [e.logGroup, e.queryName, e.from && e.to ? `${jstDateTime(e.from)}〜${jstTime(e.to)}` : null].filter(Boolean).join(' · ');
        return (
          <div key={`${e.alarm}-${e.at}`} className={`grid grid-cols-1 md:grid-cols-[96px_60px_1fr_auto_auto] gap-x-3 gap-y-1 items-center px-4 py-2 text-[13px] ${open ? 'bg-red-50' : ''}`}>
            <span className="text-xs text-gray-600 tabular-nums">{jstDateTime(e.at)}</span>
            <span>
              {e.kind === 'alarm' ? (
                <SeverityBadge severity={e.severity} />
              ) : (
                <span className="inline-flex items-center rounded border border-green-200 bg-green-50 px-1.5 py-0.5 text-[11px] font-semibold text-green-800">OK</span>
              )}
            </span>
            <span className="min-w-0">
              <code className="text-xs">{e.title}</code>
              {e.kind === 'alarm' && e.resolvedAt && <span className="text-xs text-gray-500"> · {jstTime(e.resolvedAt)} に OK</span>}
              {open && <span className="text-xs text-red-700"> · 継続中</span>}
            </span>
            <span className="text-xs text-gray-500 tabular-nums whitespace-nowrap">{e.kind === 'alarm' ? formatDuration(e.durationSec) : ''}</span>
            <span className="text-xs whitespace-nowrap" title={hint}>
              {url ? (
                <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline underline-offset-2">
                  → ログ
                </a>
              ) : (
                <span className="text-gray-400">{e.queryName ?? '—'}</span>
              )}
            </span>
          </div>
        );
      })}
    </div>
  );
}
