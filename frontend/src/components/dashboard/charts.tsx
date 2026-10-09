'use client';

import { useState, ReactNode } from 'react';

/**
 * Lightweight, dependency-free SVG charts for the ops dashboard.
 * Design follows the dataviz guide:
 *  - ONE axis per chart (never dual-axis)
 *  - sequential single-hue blue for magnitude; status palette (icon+label) for health
 *  - every chart offers a "表で見る" table fallback (accessibility / export)
 *  - bars <= 24px, 4px rounded data-end, 2px surface gap between stacked segments
 */

// dataviz light palette
export const PALETTE = {
  series1: '#2a78d6', // blue
  series2: '#eb6834', // orange (2nd categorical slot)
  seriesLight: '#cde2fb',
  warning: '#fab219',
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

function niceMax(v: number): number {
  if (v <= 0) return 1;
  const p = Math.pow(10, Math.floor(Math.log10(v)));
  const m = v / p;
  const n = m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 4 ? 4 : m <= 5 ? 5 : 10;
  return n * p;
}

function xLabel(date: string): string {
  return date.length >= 10 ? `${Number(date.slice(5, 7))}/${Number(date.slice(8, 10))}` : date;
}

// ---------------------------------------------------------------- ChartCard
export function ChartCard({
  title,
  subtitle,
  children,
  table,
  action,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  table?: ReactNode;
  action?: ReactNode;
}) {
  const [showTable, setShowTable] = useState(false);
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between mb-3 gap-2">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {action}
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
      </div>
      {showTable && table ? table : children}
    </div>
  );
}

// ---------------------------------------------------------------- Legend
export function Legend({ items }: { items: { label: string; color: string; line?: boolean }[] }) {
  return (
    <div className="flex flex-wrap gap-3 text-[11px] text-gray-600 mb-1">
      {items.map((it) => (
        <span key={it.label} className="inline-flex items-center gap-1.5">
          <span
            aria-hidden
            className="inline-block rounded-sm"
            style={{ backgroundColor: it.color, width: it.line ? 14 : 10, height: it.line ? 2 : 10 }}
          />
          {it.label}
        </span>
      ))}
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
          <span className="text-sm font-semibold" style={{ color: up ? PALETTE.good : PALETTE.bad }}>
            {up ? '▲' : '▼'} {deltaLabel ?? Math.abs(delta as number)}
          </span>
        )}
      </div>
      {sublabel && <div className="mt-0.5 text-xs text-gray-400">{sublabel}</div>}
    </div>
  );
}

// ---------------------------------------------------------------- helpers
function roundedTopPath(x: number, y: number, w: number, h: number, r: number): string {
  if (h < r * 1.5) return `M${x},${y} h${w} v${h} h-${w} z`;
  return `M${x},${y + r} a${r},${r} 0 0 1 ${r},-${r} h${w - 2 * r} a${r},${r} 0 0 1 ${r},${r} v${h - r} h-${w} z`;
}

function Grid({
  pad,
  w,
  innerH,
  max,
  format,
}: {
  pad: { l: number; r: number; t: number; b: number };
  w: number;
  innerH: number;
  max: number;
  format: (v: number) => string;
}) {
  return (
    <>
      {[0, 0.25, 0.5, 0.75, 1].map((t) => {
        const y = pad.t + innerH * (1 - t);
        return (
          <g key={t}>
            <line x1={pad.l} y1={y} x2={w - pad.r} y2={y} stroke={PALETTE.grid} strokeWidth={1} />
            {(t === 0 || t === 0.5 || t === 1) && (
              <text x={pad.l - 6} y={y + 3.5} textAnchor="end" fontSize={10} fill={PALETTE.muted}>
                {format(max * t)}
              </text>
            )}
          </g>
        );
      })}
    </>
  );
}

// ---------------------------------------------------------------- TimeBars (single series)
export function TimeBars({
  data,
  height = 160,
  ariaLabel = '推移',
  yFormat = (v: number) => fmt(Math.round(v)),
  valueFormat = (v: number) => fmt(v),
  marker,
}: {
  data: { date: string; value: number }[];
  height?: number;
  ariaLabel?: string;
  yFormat?: (v: number) => string;
  valueFormat?: (v: number) => string;
  marker?: { date: string; label: string };
}) {
  if (data.length === 0) return <EmptyChart />;
  const w = 640;
  const pad = { l: 42, r: 8, t: 10, b: 22 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;
  const max = niceMax(Math.max(1, ...data.map((d) => d.value)));
  const bw = innerW / data.length;
  const barW = Math.min(24, Math.max(3, bw * 0.64));
  const every = data.length <= 16 ? 1 : Math.ceil(data.length / 10);
  const markerIndex = marker ? data.findIndex((d) => d.date === marker.date) : -1;

  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" role="img" aria-label={ariaLabel}>
      <Grid pad={pad} w={w} innerH={innerH} max={max} format={yFormat} />
      {data.map((d, i) => {
        const h = (d.value / max) * innerH;
        const x = pad.l + i * bw + (bw - barW) / 2;
        const y = pad.t + innerH - h;
        return (
          <g key={d.date}>
            {h > 0 && (
              <path d={roundedTopPath(x, y, barW, h, 4)} fill={PALETTE.series1}>
                <title>{`${xLabel(d.date)}: ${valueFormat(d.value)}`}</title>
              </path>
            )}
            <rect x={pad.l + i * bw} y={pad.t} width={bw} height={innerH} fill="transparent">
              <title>{`${xLabel(d.date)}: ${valueFormat(d.value)}`}</title>
            </rect>
            {(i % every === 0 || i === data.length - 1) && (
              <text x={pad.l + i * bw + bw / 2} y={height - 7} textAnchor="middle" fontSize={9} fill={PALETTE.muted}>
                {xLabel(d.date)}
              </text>
            )}
          </g>
        );
      })}
      {markerIndex >= 0 && (
        <g>
          <line
            x1={pad.l + markerIndex * bw + bw / 2}
            y1={pad.t}
            x2={pad.l + markerIndex * bw + bw / 2}
            y2={pad.t + innerH}
            stroke={PALETTE.muted}
            strokeWidth={1}
            strokeDasharray="3 3"
          />
          <text x={pad.l + markerIndex * bw + bw / 2 + 4} y={pad.t + 9} fontSize={9} fill={PALETTE.muted}>
            {marker?.label}
          </text>
        </g>
      )}
    </svg>
  );
}

// ---------------------------------------------------------------- StackedBars (2 series, one axis)
export function StackedBars({
  data,
  height = 160,
  ariaLabel = '質問数の推移',
}: {
  data: { date: string; total: number; unreached: number }[];
  height?: number;
  ariaLabel?: string;
}) {
  if (data.length === 0) return <EmptyChart />;
  const w = 640;
  const pad = { l: 42, r: 8, t: 10, b: 22 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;
  const max = niceMax(Math.max(1, ...data.map((d) => d.total)));
  const bw = innerW / data.length;
  const barW = Math.min(24, Math.max(3, bw * 0.64));
  const every = data.length <= 16 ? 1 : Math.ceil(data.length / 10);

  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" role="img" aria-label={ariaLabel}>
      <Grid pad={pad} w={w} innerH={innerH} max={max} format={(v) => fmt(Math.round(v))} />
      {data.map((d, i) => {
        const reached = Math.max(0, d.total - d.unreached);
        const hReached = (reached / max) * innerH;
        const hUnreached = (d.unreached / max) * innerH;
        const x = pad.l + i * bw + (bw - barW) / 2;
        const base = pad.t + innerH;
        const yReached = base - hReached;
        const yUnreached = yReached - hUnreached;
        const tip = `${xLabel(d.date)}: 質問 ${fmt(d.total)} · 到達できず ${fmt(d.unreached)}`;
        return (
          <g key={d.date}>
            {hReached > 0 && (
              d.unreached > 0 ? (
                <rect x={x} y={yReached + 2} width={barW} height={Math.max(0, hReached - 2)} fill={PALETTE.series1} />
              ) : (
                <path d={roundedTopPath(x, yReached, barW, hReached, 4)} fill={PALETTE.series1} />
              )
            )}
            {hUnreached > 0 && <path d={roundedTopPath(x, yUnreached, barW, hUnreached, 4)} fill={PALETTE.warning} />}
            <rect x={pad.l + i * bw} y={pad.t} width={bw} height={innerH} fill="transparent">
              <title>{tip}</title>
            </rect>
            {(i % every === 0 || i === data.length - 1) && (
              <text x={pad.l + i * bw + bw / 2} y={height - 7} textAnchor="middle" fontSize={9} fill={PALETTE.muted}>
                {xLabel(d.date)}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

// ---------------------------------------------------------------- MsLines (latency, seconds axis, reference lines)
export function MsLines({
  data,
  refLines = [],
  height = 160,
  ariaLabel = '応答時間の推移',
}: {
  data: { date: string; p90Ms: number | null; maxMs: number | null }[];
  refLines?: { valueMs: number; label: string }[];
  height?: number;
  ariaLabel?: string;
}) {
  if (data.length === 0) return <EmptyChart />;
  const w = 640;
  const pad = { l: 42, r: 8, t: 10, b: 22 };
  const innerW = w - pad.l - pad.r;
  const innerH = height - pad.t - pad.b;
  const values = data.flatMap((d) => [d.p90Ms ?? 0, d.maxMs ?? 0]).concat(refLines.map((r) => r.valueMs));
  const max = niceMax(Math.max(30000, ...values));
  const x = (i: number) => pad.l + (data.length === 1 ? innerW / 2 : (innerW * i) / (data.length - 1));
  const y = (v: number) => pad.t + innerH * (1 - Math.min(1, v / max));
  const every = data.length <= 16 ? 1 : Math.ceil(data.length / 10);

  const path = (key: 'p90Ms' | 'maxMs') => {
    let d = '';
    let pen = false;
    data.forEach((row, i) => {
      const v = row[key];
      if (v === null || v === undefined) {
        pen = false;
        return;
      }
      d += `${pen ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)} `;
      pen = true;
    });
    return d;
  };
  const last = (key: 'p90Ms' | 'maxMs') => {
    for (let i = data.length - 1; i >= 0; i--) {
      const v = data[i][key];
      if (v !== null && v !== undefined) return { i, v };
    }
    return null;
  };
  const lastP90 = last('p90Ms');
  const lastMax = last('maxMs');

  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" role="img" aria-label={ariaLabel}>
      <Grid pad={pad} w={w} innerH={innerH} max={max} format={(v) => `${Math.round(v / 1000)} s`} />
      {refLines.map((r) => (
        <g key={r.label}>
          <line x1={pad.l} y1={y(r.valueMs)} x2={w - pad.r} y2={y(r.valueMs)} stroke={PALETTE.target} strokeWidth={1} strokeDasharray="4 3" />
          <text x={pad.l + 4} y={y(r.valueMs) - 3} fontSize={9} fill={PALETTE.muted}>
            {r.label}
          </text>
        </g>
      ))}
      <path d={path('maxMs')} fill="none" stroke={PALETTE.series2} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      <path d={path('p90Ms')} fill="none" stroke={PALETTE.series1} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      {lastMax && <circle cx={x(lastMax.i)} cy={y(lastMax.v)} r={4} fill={PALETTE.series2} stroke="#fff" strokeWidth={2} />}
      {lastP90 && <circle cx={x(lastP90.i)} cy={y(lastP90.v)} r={4} fill={PALETTE.series1} stroke="#fff" strokeWidth={2} />}
      {data.map((d, i) => (
        <g key={d.date}>
          <rect x={x(i) - innerW / Math.max(1, data.length - 1) / 2} y={pad.t} width={innerW / Math.max(1, data.length - 1)} height={innerH} fill="transparent">
            <title>
              {d.p90Ms === null
                ? `${xLabel(d.date)}: 質問なし`
                : `${xLabel(d.date)}: p90 ${(d.p90Ms / 1000).toFixed(1)} s · 最大 ${((d.maxMs ?? 0) / 1000).toFixed(1)} s`}
            </title>
          </rect>
          {(i % every === 0 || i === data.length - 1) && (
            <text x={x(i)} y={height - 7} textAnchor="middle" fontSize={9} fill={PALETTE.muted}>
              {xLabel(d.date)}
            </text>
          )}
        </g>
      ))}
    </svg>
  );
}

// ---------------------------------------------------------------- RateLine (0-100%) — kept for compatibility
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
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" role="img" aria-label="率の推移">
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
      <line x1={pad.l} y1={targetY} x2={w - pad.r} y2={targetY} stroke={PALETTE.target} strokeWidth={1} strokeDasharray="4 3" />
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
            <div className="h-full rounded" style={{ width: `${(d.count / max) * 100}%`, backgroundColor: PALETTE.series1 }} />
          </div>
        </li>
      ))}
    </ol>
  );
}

// ---------------------------------------------------------------- helpers
export function EmptyChart({ label = 'データがありません' }: { label?: string }) {
  return <div className="h-40 flex items-center justify-center text-sm text-gray-400">{label}</div>;
}

export function SimpleTable({ columns, rows }: { columns: string[]; rows: (string | number)[][] }) {
  return (
    <div className="overflow-x-auto max-h-56">
      <table className="w-full text-xs">
        <thead className="text-gray-500 sticky top-0 bg-white">
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
