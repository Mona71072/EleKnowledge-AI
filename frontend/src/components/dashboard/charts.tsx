'use client';

import { useState, ReactNode } from 'react';

/**
 * Lightweight, dependency-free SVG charts for the ops dashboard.
 * Design follows the dataviz guide:
 *  - ONE axis per chart (queries and like-rate are SEPARATE charts, never dual-axis)
 *  - sequential single-hue blue for magnitude; status palette (icon+label) for health
 *  - every chart offers a "表で見る" table fallback (accessibility / export)
 */

// dataviz light palette (CSS-var-ready; dark steps documented for future theming)
export const PALETTE = {
  series1: '#2a78d6', // blue
  seriesLight: '#cde2fb',
  grid: '#e1e0d9',
  axis: '#c3c2b7',
  ink: '#0b0b0b',
  muted: '#898781',
  good: '#006300',
  bad: '#d03b3b',
  target: '#898781',
};

function fmt(n: number): string {
  return n.toLocaleString('ja-JP');
}

// ---------------------------------------------------------------- ChartCard
export function ChartCard({
  title,
  subtitle,
  children,
  table,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  table?: ReactNode;
}) {
  const [showTable, setShowTable] = useState(false);
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        {table && (
          <button
            type="button"
            onClick={() => setShowTable((s) => !s)}
            className="text-xs text-blue-600 hover:text-blue-800 underline underline-offset-2"
            aria-pressed={showTable}
          >
            {showTable ? 'グラフで見る' : '表で見る'}
          </button>
        )}
      </div>
      {showTable && table ? table : children}
    </div>
  );
}

// ---------------------------------------------------------------- StatTile
export function StatTile({
  label,
  value,
  delta,
  deltaLabel,
  sublabel,
}: {
  label: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  sublabel?: string;
}) {
  const hasDelta = typeof delta === 'number' && delta !== 0;
  const up = (delta ?? 0) > 0;
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="text-xs font-medium text-gray-500">{label}</div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-gray-900 tabular-nums">{value}</span>
        {hasDelta && (
          <span
            className="text-sm font-semibold"
            style={{ color: up ? PALETTE.good : PALETTE.bad }}
          >
            {up ? '▲' : '▼'} {deltaLabel ?? Math.abs(delta as number)}
          </span>
        )}
      </div>
      {sublabel && <div className="mt-0.5 text-xs text-gray-400">{sublabel}</div>}
    </div>
  );
}

// ---------------------------------------------------------------- TimeBars
export function TimeBars({
  data,
  height = 160,
}: {
  data: { date: string; value: number }[];
  height?: number;
}) {
  if (data.length === 0) return <EmptyChart />;
  const w = 640;
  const pad = { l: 36, r: 8, t: 8, b: 22 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;
  const max = Math.max(1, ...data.map((d) => d.value));
  const bw = innerW / data.length;
  const barW = Math.max(3, bw * 0.62);

  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" role="img" aria-label="クエリ数の推移">
      {/* y gridlines */}
      {[0, 0.5, 1].map((t) => {
        const y = pad.t + innerH * (1 - t);
        return (
          <g key={t}>
            <line x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke={PALETTE.grid} strokeWidth={1} />
            <text x={pad.l - 6} y={y + 3} textAnchor="end" fontSize={10} fill={PALETTE.muted}>
              {Math.round(max * t)}
            </text>
          </g>
        );
      })}
      {data.map((d, i) => {
        const h = (d.value / max) * innerH;
        const x = pad.l + i * bw + (bw - barW) / 2;
        const y = pad.t + innerH - h;
        const showLabel = data.length <= 10 || i % Math.ceil(data.length / 8) === 0;
        return (
          <g key={d.date}>
            <rect x={x} y={y} width={barW} height={h} rx={3} fill={PALETTE.series1}>
              <title>{`${d.date}: ${fmt(d.value)}`}</title>
            </rect>
            {showLabel && (
              <text
                x={pad.l + i * bw + bw / 2}
                y={height - 8}
                textAnchor="middle"
                fontSize={9}
                fill={PALETTE.muted}
              >
                {d.date.slice(5)}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

// ---------------------------------------------------------------- LineChart (0-100%)
export function RateLine({
  data,
  target = 0.85,
  height = 160,
}: {
  data: { date: string; value: number }[];
  target?: number;
  height?: number;
}) {
  if (data.length === 0) return <EmptyChart />;
  const w = 640;
  const pad = { l: 36, r: 8, t: 8, b: 22 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;
  const x = (i: number) => pad.l + (data.length === 1 ? innerW / 2 : (innerW * i) / (data.length - 1));
  const y = (v: number) => pad.t + innerH * (1 - Math.min(1, Math.max(0, v)));

  const path = data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${x(i)} ${y(d.value)}`).join(' ');
  const targetY = y(target);

  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" role="img" aria-label="いいね率の推移">
      {[0, 0.25, 0.5, 0.75, 1].map((t) => {
        const gy = y(t);
        return (
          <g key={t}>
            <line x1={pad.l} y1={gy} x2={w - pad.r} y2={gy} stroke={PALETTE.grid} strokeWidth={1} />
            <text x={pad.l - 6} y={gy + 3} textAnchor="end" fontSize={10} fill={PALETTE.muted}>
              {Math.round(t * 100)}%
            </text>
          </g>
        );
      })}
      {/* target line */}
      <line
        x1={pad.l}
        y1={targetY}
        x2={w - pad.r}
        y2={targetY}
        stroke={PALETTE.target}
        strokeWidth={1}
        strokeDasharray="4 3"
      />
      <text x={w - pad.r} y={targetY - 4} textAnchor="end" fontSize={9} fill={PALETTE.muted}>
        目標 {Math.round(target * 100)}%
      </text>
      <path d={path} fill="none" stroke={PALETTE.series1} strokeWidth={2} strokeLinejoin="round" />
      {data.map((d, i) => (
        <circle key={d.date} cx={x(i)} cy={y(d.value)} r={3} fill={PALETTE.series1}>
          <title>{`${d.date}: ${Math.round(d.value * 100)}%`}</title>
        </circle>
      ))}
    </svg>
  );
}

// ---------------------------------------------------------------- DocRanking
export function DocRanking({ data }: { data: { name: string; count: number }[] }) {
  if (data.length === 0) return <EmptyChart label="参照データがありません" />;
  const max = Math.max(1, ...data.map((d) => d.count));
  return (
    <ol className="space-y-2">
      {data.map((d, i) => (
        <li key={d.name} className="text-sm">
          <div className="flex items-center justify-between gap-2 mb-0.5">
            <span className="truncate text-gray-800" title={d.name}>
              {i + 1}. {d.name}
            </span>
            <span className="tabular-nums text-gray-500 flex-shrink-0">{fmt(d.count)}</span>
          </div>
          <div className="h-2 rounded bg-gray-100 overflow-hidden">
            <div
              className="h-full rounded"
              style={{ width: `${(d.count / max) * 100}%`, backgroundColor: PALETTE.series1 }}
            />
          </div>
        </li>
      ))}
    </ol>
  );
}

// ---------------------------------------------------------------- helpers
function EmptyChart({ label = 'データがありません' }: { label?: string }) {
  return (
    <div className="h-40 flex items-center justify-center text-sm text-gray-400">{label}</div>
  );
}

export function SimpleTable({
  columns,
  rows,
}: {
  columns: string[];
  rows: (string | number)[][];
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead className="text-gray-500">
          <tr>
            {columns.map((c) => (
              <th key={c} className="text-left font-medium px-2 py-1">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((cell, j) => (
                <td key={j} className="px-2 py-1 tabular-nums text-gray-700">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
