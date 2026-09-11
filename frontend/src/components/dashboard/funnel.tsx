'use client';

import { FunnelRow } from '@/lib/metrics';
import { formatCount, rateLabel } from '@/lib/metrics-format.mjs';

const STEPS: { key: keyof FunnelRow; label: string; source: string }[] = [
  { key: 'signIns', label: 'ログイン', source: 'Cognito SignInSuccesses' },
  { key: 'queries', label: '質問', source: 'chatlogs role=user' },
  { key: 'pages', label: '候補あり', source: 'responseType=pages' },
  { key: 'opened', label: '資料を開いた', source: '引用リンクから文書を開いた回答の数' },
  { key: 'good', label: '👍', source: 'feedback=good' },
];

/**
 * 到達ファネル（設計 §2.4）。段は入れ子ではないので比率の線は引かず、件数と相対バーだけを出す。
 * 「資料を開いた」が未計測のときは数字の代わりに「未計測」を灰色で出す。
 */
export function Funnel({
  title,
  row,
  showRates,
  minDenominator,
}: {
  title: string;
  row: FunnelRow;
  showRates: boolean;
  minDenominator: number;
}) {
  const numeric = STEPS.map((s) => {
    const v = row[s.key];
    return typeof v === 'number' ? v : 0;
  });
  const max = Math.max(1, ...numeric);
  const unreachedRate = showRates ? rateLabel(row.unreached, row.queries, minDenominator) : null;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-2 text-xs text-gray-500">{title}</div>
      <div className="grid grid-cols-5 gap-1.5">
        {STEPS.map((s, i) => {
          const v = row[s.key];
          const unmeasured = v === 'unmeasured';
          return (
            <div key={s.key} title={s.source}>
              <div className="text-[11px] text-gray-500 whitespace-nowrap">{s.label}</div>
              {unmeasured ? (
                <div className="text-xs text-gray-400 pt-1.5">未計測</div>
              ) : (
                <div className="text-xl font-semibold tabular-nums leading-tight">{formatCount(v as number | null)}</div>
              )}
              <div className="mt-1.5 h-1.5 rounded bg-blue-100 overflow-hidden">
                <div className="h-full rounded bg-blue-600" style={{ width: unmeasured ? '0%' : `${Math.round((numeric[i] / max) * 100)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-2.5 border-t border-gray-100 pt-2 text-xs text-gray-600 flex flex-wrap gap-x-3 gap-y-1">
        <span>
          到達できず <b className="text-gray-900 tabular-nums">{formatCount(row.unreached)}</b>
          {unreachedRate ? (
            <span className="text-gray-500">
              {' '}
              / {formatCount(row.queries)}（{unreachedRate}）
            </span>
          ) : (
            <span className="text-gray-400"> 件（分母 {minDenominator} 未満のため率は出さない）</span>
          )}
        </span>
        <span>
          not_found <b className="text-gray-900 tabular-nums">{formatCount(row.notFound)}</b>
        </span>
        <span>
          👎 <b className="text-gray-900 tabular-nums">{formatCount(row.bad)}</b>
        </span>
        {row.reformulated !== null && (
          <span>
            言い換え <b className="text-gray-900 tabular-nums">{formatCount(row.reformulated)}</b>
          </span>
        )}
      </div>
    </div>
  );
}
