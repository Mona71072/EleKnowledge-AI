'use client';

import { useCallback, useEffect, useState } from 'react';
import { getCost, CostResponse, HealthStatus } from '@/lib/metrics';
import { formatCount, formatUsd, jstDateLabel, jstTime } from '@/lib/metrics-format.mjs';
import { ChartCard, SimpleTable, TimeBars } from '@/components/dashboard/charts';
import { CostBadge, CostBadgeKind, StatusPill } from '@/components/dashboard/status';
import { Loading } from '@/components/ui/Loading';

function shiftMonth(month: string, delta: number): string {
  const [y, m] = month.split('-').map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
}

function currentMonth(): string {
  const d = new Date();
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
}

/**
 * コスト画面（設計: docs/design-2026-09-10-dashboard-v2.md §5）。
 * すべての金額に出所のバッジ（実額・確定 / 実額・帰属未確認 / 共有・按分不能 / 推定）を付け、混ぜない。
 */
export default function CostPage() {
  const [month, setMonth] = useState<string>(currentMonth());
  const [data, setData] = useState<CostResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (m: string) => {
    setLoading(true);
    setError(null);
    try {
      setData(await getCost(m));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(month);
  }, [month, load]);

  const [y, m] = month.split('-').map(Number);

  return (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-3 mb-5">
        <div>
          <h2 className="text-xl font-bold text-gray-900">コスト</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            {y} 年 {m} 月 · UTC 日基準
            {data?.settledThrough ? ` · 確定は ${jstDateLabel(data.settledThrough, false)} まで（D-2）` : ''} · Cost Explorer を 1 日 2 回読む
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <button type="button" onClick={() => setMonth(shiftMonth(month, -1))} className="rounded border border-gray-300 bg-white px-2 py-0.5 text-gray-700">
            ← 前月
          </button>
          <span className="tabular-nums font-semibold">{month}</span>
          <button
            type="button"
            onClick={() => setMonth(shiftMonth(month, 1))}
            disabled={month >= currentMonth()}
            className="rounded border border-gray-300 bg-white px-2 py-0.5 text-gray-700 disabled:opacity-40"
          >
            翌月 →
          </button>
          {data && <span className="text-xs text-gray-500 ml-2">最終更新 {jstTime(data.generatedAt)}</span>}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-600">
        <span>バッジ:</span>
        <CostBadge kind="actual" />
        <CostBadge kind="unattributed" />
        <CostBadge kind="shared" />
        <CostBadge kind="estimate" />
        <span className="text-gray-400">出所で機械的に決まる。費用対効果の分母は「実額・確定」だけ</span>
      </div>

      {error && <div className="mb-4 rounded border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-800">データを読み込めませんでした：{error}</div>}

      {loading && !data ? (
        <div className="p-12 flex justify-center">
          <Loading size="lg" text="コストを読み込み中..." />
        </div>
      ) : data ? (
        <div className="space-y-6">
          <Boxes data={data} />
          <Checks data={data} />
          <Daily data={data} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <PerQuery data={data} />
            <Projection data={data} />
          </div>
          <Budget data={data} />
        </div>
      ) : null}
    </div>
  );
}

// ------------------------------------------------------------------ pieces
function Box({
  kind,
  caption,
  total,
  rows,
  footnote,
  hero,
  children,
}: {
  kind: CostBadgeKind;
  caption: string;
  total: string;
  rows: [string, string][];
  footnote?: React.ReactNode;
  hero?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between gap-2 mb-2">
        <CostBadge kind={kind} />
        <span className="text-xs text-gray-500">{caption}</span>
      </div>
      <div className={`${hero ? 'text-3xl' : 'text-2xl'} font-semibold tabular-nums leading-tight`}>{total}</div>
      {children}
      <div className="mt-2 text-[13px]">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between gap-2 border-t border-gray-100 py-0.5">
            <span className="text-gray-600 truncate" title={k}>
              {k}
            </span>
            <span className="tabular-nums whitespace-nowrap">{v}</span>
          </div>
        ))}
      </div>
      {footnote && <div className="mt-2 text-[11.5px] text-gray-500">{footnote}</div>}
    </div>
  );
}

function byServiceRows(map: Record<string, number>, max = 6): [string, string][] {
  return Object.entries(map)
    .slice(0, max)
    .map(([k, v]) => [k, formatUsd(v)]);
}

function Boxes({ data }: { data: CostResponse }) {
  const c = data.confirmed;
  const pct = c.budgetPct ?? 0;
  return (
    <section>
      <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">
        今月 <span className="ml-2 text-xs font-normal text-gray-500">4 つの箱を混ぜない</span>
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
        <Box
          kind="actual"
          caption="帰属が確定"
          total={formatUsd(c.total)}
          hero
          rows={[
            [c.bedrock.service, formatUsd(c.bedrock.total)],
            ['　入力トークン', formatUsd(c.bedrock.input)],
            ['　出力トークン', formatUsd(c.bedrock.output)],
            ['　キャッシュ', formatUsd(c.bedrock.cache)],
            ['Amplify（専用）', formatUsd(c.amplify)],
          ]}
          footnote={<>予算 {formatUsd(c.budgetUsd, 0)} の <span className="tabular-nums">{c.budgetPct ?? '—'} %</span>（Bedrock）</>}
        >
          <div className="mt-2.5 h-2 rounded bg-blue-100 relative">
            <div className="h-full rounded bg-blue-600" style={{ width: `${Math.min(100, pct)}%` }} />
            <span aria-hidden className="absolute -top-[3px] left-1/2 w-px h-3.5 bg-gray-400" />
          </div>
          <div className="flex justify-between text-[10px] text-gray-500 mt-1">
            <span>0</span>
            <span>50 %</span>
            <span>予算 {formatUsd(c.budgetUsd, 0)}</span>
          </div>
        </Box>
        <Box
          kind="unattributed"
          caption="タグ待ち"
          total={formatUsd(data.unattributed.total)}
          rows={byServiceRows(data.unattributed.byService)}
          footnote="コスト配分タグ有効化後に Project=EleKnowledge で「実額・確定」へ移る。有効化前には遡及しない。WAF は Web ACL が別のため有効化後に切り分けできる"
        />
        <Box
          kind="shared"
          caption="切り出せない"
          total={formatUsd(data.shared.total, 0)}
          rows={byServiceRows(data.shared.byService)}
          footnote="費用対効果の分母に入れない。OCU が増えない限り EleKnowledge の増分は 0"
        />
        <Box
          kind="other"
          caption="同居する別システム"
          total={formatUsd(data.otherSystems.total, 0)}
          rows={byServiceRows(data.otherSystems.byService, 4)}
          footnote="他モデルの Bedrock 行など。EleKnowledge とは無関係。参考として表示"
        />
      </div>
    </section>
  );
}

function Checks({ data }: { data: CostResponse }) {
  const ck = data.checks;
  const sole = ck.soleUser.ok;
  const rows: { status: HealthStatus; name: string; detail: React.ReactNode }[] = [
    {
      status: sole === false ? 'critical' : sole === null ? 'warning' : 'good',
      name: `${data.confirmed.bedrock.service.split(' (')[0]} の唯一の利用者`,
      detail:
        sole === null ? (
          '判定材料なし（Bedrock メトリクスが未取得）'
        ) : (
          <>
            {sole ? '成立' : '不成立'}。{ck.soleUser.detail}（1 回答 1 呼び出し）。
            {sole ? '' : ' 他システムが同じモデルを使っているため、上の実額は EleKnowledge 分と言い切れない'}
          </>
        ),
    },
    {
      status: ck.actualVsEstimate.status,
      name: '実額 vs 推定',
      detail:
        ck.actualVsEstimate.estimate === null ? (
          '推定が無い（トークンのメトリクスか単価が未取得）'
        ) : (
          <>
            <span className="tabular-nums">{formatUsd(ck.actualVsEstimate.actual)}</span> / <span className="tabular-nums">{formatUsd(ck.actualVsEstimate.estimate)}</span>（
            <span className="tabular-nums">{ck.actualVsEstimate.diffPct === null ? '—' : `${ck.actualVsEstimate.diffPct > 0 ? '+' : ''}${ck.actualVsEstimate.diffPct} %`}</span>、{ck.actualVsEstimate.days} 日分）。±20 % 超で注意。SSM 単価の妥当性もここで検証
          </>
        ),
    },
    {
      status: ck.modelIds.length <= 1 ? 'good' : 'warning',
      name: 'モデル ID',
      detail: ck.modelIds.length ? (
        <>
          <code className="text-xs">{ck.modelIds.join(', ')}</code>
          {ck.modelIds.length > 1 ? '。月内に切り替えがあるため、この月の Bedrock 行は EleKnowledge 分として切り出せない' : '、変更なし'}
        </>
      ) : (
        '記録なし'
      ),
    },
    { status: 'warning', name: 'コスト配分タグ', detail: '未有効（管理アカウント側の作業）。有効化後は「帰属未確認」の箱が「確定」に移る' },
  ];
  return (
    <section>
      <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">
        前提チェック <span className="ml-2 text-xs font-normal text-gray-500">実額を「EleKnowledge 分」と言い切れる条件を毎日自動で確かめる</span>
      </h3>
      <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-100">
        {rows.map((r) => (
          <div key={r.name} className="grid grid-cols-1 md:grid-cols-[auto_200px_1fr] gap-x-3 gap-y-1 items-baseline px-4 py-2 text-[13px]">
            <StatusPill status={r.status} />
            <span className="font-semibold">{r.name}</span>
            <span className="text-gray-700">{r.detail}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Daily({ data }: { data: CostResponse }) {
  const cost = data.daily.map((d) => ({ date: d.date, value: d.bedrockUsd }));
  const queries = data.queriesDaily.map((d) => ({ date: d.date, value: d.queries }));
  return (
    <section>
      <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">
        日次推移 <span className="ml-2 text-xs font-normal text-gray-500">日付基準が違うものは別チャートに分ける</span>
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <ChartCard
          title={`${data.confirmed.bedrock.service.split(' (')[0]} 実額`}
          subtitle="USD・UTC 日。暫定の日は確定後に上書きされる"
          table={<SimpleTable columns={['日付（UTC）', 'USD', '確定']} rows={[...data.daily].reverse().map((d) => [d.date, d.bedrockUsd.toFixed(2), d.settled ? '確定' : '暫定'])} />}
        >
          <TimeBars data={cost} ariaLabel="Bedrock 実額の推移" yFormat={(v) => v.toFixed(1)} valueFormat={(v) => `${v.toFixed(2)} USD`} />
        </ChartCard>
        <ChartCard
          title="質問数"
          subtitle="件・JST 日（ダッシュボードと同じ値）"
          table={<SimpleTable columns={['日付（JST）', '質問']} rows={[...data.queriesDaily].reverse().map((d) => [jstDateLabel(d.date), d.queries])} />}
        >
          <TimeBars data={queries} ariaLabel="質問数の推移" valueFormat={(v) => `${formatCount(v)} 質問`} />
        </ChartCard>
      </div>
    </section>
  );
}

function PerQuery({ data }: { data: CostResponse }) {
  const p = data.perQuery;
  const fmt4 = (v: number | null) => (v === null ? '—' : v.toFixed(3));
  return (
    <section>
      <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">1 質問あたり</h3>
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <table className="w-full text-[13px]">
          <thead className="text-xs text-gray-500">
            <tr>
              <th className="text-left font-medium py-1">基準</th>
              <th className="text-right font-medium py-1">USD</th>
              <th className="text-left font-medium py-1 pl-3">出所</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            <tr>
              <td className="py-1.5">実額 ÷ 質問（今月）</td>
              <td className="py-1.5 text-right tabular-nums">{fmt4(p.actualUsd)}</td>
              <td className="py-1.5 pl-3">
                <CostBadge kind="estimate" /> {formatUsd(data.confirmed.bedrock.total)} ÷ {formatCount(p.queries)} 質問
              </td>
            </tr>
            <tr>
              <td className="py-1.5">実額 ÷ 回答（今月）</td>
              <td className="py-1.5 text-right tabular-nums">{fmt4(p.perAnswerUsd)}</td>
              <td className="py-1.5 pl-3">
                <CostBadge kind="estimate" /> ÷ {formatCount(p.answers)} 回答（候補あり）
              </td>
            </tr>
            <tr>
              <td className="py-1.5">トレース 1 回答 中央値 / p90</td>
              <td className="py-1.5 text-right tabular-nums">
                {fmt4(p.traceMedianUsd)} / {fmt4(p.traceP90Usd)}
              </td>
              <td className="py-1.5 pl-3 text-gray-500">retrievalTrace 実装後</td>
            </tr>
          </tbody>
        </table>
        <p className="mt-2 text-[11.5px] text-gray-500">生成（Bedrock 呼び出し）は「候補あり」の回答でだけ走る。聞き返し・not_found はトークンを使わない</p>
      </div>
    </section>
  );
}

function Projection({ data }: { data: CostResponse }) {
  return (
    <section>
      <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">見込み（いまの単価で）</h3>
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <table className="w-full text-[13px]">
          <thead className="text-xs text-gray-500">
            <tr>
              <th className="text-right font-medium py-1">質問/日</th>
              <th className="text-right font-medium py-1">Bedrock 月額</th>
              <th className="text-left font-medium py-1 pl-3">備考</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.projection.map((p) => (
              <tr key={p.queriesPerDay}>
                <td className="py-1.5 text-right tabular-nums">{formatCount(p.queriesPerDay)}</td>
                <td className="py-1.5 text-right tabular-nums whitespace-nowrap">
                  <CostBadge kind="estimate" /> {formatUsd(p.monthlyUsd, 0)}
                </td>
                <td className="py-1.5 pl-3 text-gray-600">
                  {p.queriesPerDay === 1000 ? '設計上限。Lambda / DynamoDB / API GW は合計 1 USD 未満' : p.monthlyUsd !== null && p.monthlyUsd > data.confirmed.budgetUsd ? `予算 ${formatUsd(data.confirmed.budgetUsd, 0)} を超える水準` : ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-2 text-[11.5px] text-gray-500">利用が伸びて効くのは Bedrock だけ。CloudWatch Logs は月 2 USD 程度</p>
      </div>
    </section>
  );
}

function Budget({ data }: { data: CostResponse }) {
  const c = data.confirmed;
  return (
    <section>
      <h3 className="text-[13px] font-semibold text-gray-900 tracking-wide mb-2">予算アラート</h3>
      <div className="rounded-lg border border-gray-200 bg-white p-4 text-[13px]">
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
          <dt className="text-gray-500">予算</dt>
          <dd>
            AWS Budgets · 月次 {formatUsd(c.budgetUsd, 0)} · フィルタ Service = {c.bedrock.service}
          </dd>
          <dt className="text-gray-500">通知</dt>
          <dd>実績 50 % / 実績 100 % / 予測 100 % → SNS（監視スタックと同じ宛先）</dd>
          <dt className="text-gray-500">今月</dt>
          <dd className="tabular-nums">
            実績 <CostBadge kind="actual" /> {formatUsd(c.bedrock.total)}（{c.budgetPct ?? '—'} %）· 月末予測 <CostBadge kind="estimate" /> {formatUsd(c.forecastUsd)}
          </dd>
          <dt className="text-gray-500">次回見直し</dt>
          <dd>翌月 1 日に「前月実績 × 2 と 100 USD の大きい方」へ。コスト配分タグ有効化後に Project=EleKnowledge の 2 本目を追加</dd>
        </dl>
      </div>
    </section>
  );
}
