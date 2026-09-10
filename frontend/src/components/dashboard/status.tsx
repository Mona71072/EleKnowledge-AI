'use client';

import { HealthStatus, STATUS_META } from '@/lib/metrics';

/** 状態色のピル。アイコン + ラベルで、色だけに頼らない（WCAG 1.4.1）。 */
export function StatusPill({ status, extra, className = '' }: { status: HealthStatus; extra?: string; className?: string }) {
  const meta = STATUS_META[status];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-xs font-semibold ${meta.className} ${className}`}>
      <span aria-hidden style={{ color: meta.color }}>
        {meta.icon}
      </span>
      {meta.label}
      {extra ? <span className="font-normal">{extra}</span> : null}
    </span>
  );
}

/** 表示中の告知やアラームの重要度バッジ */
export function SeverityBadge({ severity }: { severity: 'P1' | 'P2' | 'info' | 'warning' | 'critical' }) {
  const cls =
    severity === 'P1' || severity === 'critical'
      ? 'text-red-800 bg-red-50 border-red-300'
      : severity === 'P2' || severity === 'warning'
        ? 'text-amber-800 bg-amber-50 border-amber-300'
        : 'text-blue-800 bg-blue-50 border-blue-200';
  const label = severity === 'info' ? '情報' : severity === 'warning' ? '注意' : severity === 'critical' ? '重要' : severity;
  return <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[11px] font-semibold ${cls}`}>{label}</span>;
}

/** コスト画面の 4 分類バッジ（出所で機械的に決まる。設計 §5.2） */
export type CostBadgeKind = 'actual' | 'unattributed' | 'shared' | 'estimate' | 'other';

const COST_BADGE: Record<CostBadgeKind, { label: string; className: string; prefix?: string }> = {
  actual: { label: '実額・確定', className: 'bg-gray-900 text-white border-gray-900' },
  unattributed: { label: '実額・帰属未確認', className: 'border-dashed border-gray-600 text-gray-700 bg-white' },
  shared: { label: '共有・按分不能', className: 'border-dotted border-gray-500 text-gray-600 bg-gray-50' },
  estimate: { label: '推定', className: 'border-gray-400 text-gray-700 bg-gray-100', prefix: '≈' },
  other: { label: '他システム', className: 'border-gray-300 text-gray-500 bg-white' },
};

export function CostBadge({ kind, className = '' }: { kind: CostBadgeKind; className?: string }) {
  const meta = COST_BADGE[kind];
  return (
    <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10.5px] font-semibold tracking-wide whitespace-nowrap ${meta.className} ${className}`}>
      {meta.prefix ? <span aria-hidden>{meta.prefix}</span> : null}
      {meta.label}
    </span>
  );
}
