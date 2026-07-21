import { getIdToken, authHeaders } from './auth-helpers';

const API_URL = process.env.NEXT_PUBLIC_APP_API_URL || '';

export type MetricPeriod = 'today' | 'week' | 'month';
export type HealthStatus = 'good' | 'warning' | 'serious' | 'critical';

export interface KpiValue {
  value: number;
  delta?: number;
}

export interface TimePoint {
  date: string;
  value: number;
}

export interface HealthMetric {
  value: number;
  status: HealthStatus;
}

export interface MetricsResponse {
  period: string;
  generatedAt: string;
  kpi: {
    likeRate: KpiValue;
    queries: KpiValue;
    activeUsers: KpiValue;
  };
  series: {
    queriesByDay: TimePoint[];
    likeRateByDay: TimePoint[];
  };
  topDocuments: { name: string; count: number }[];
  health: {
    errorRate: HealthMetric;
    latencyP90: HealthMetric;
    http5xx: HealthMetric;
    openIncidents: number;
  };
}

export async function getMetrics(period: MetricPeriod = 'week'): Promise<MetricsResponse> {
  const token = await getIdToken();
  const res = await fetch(`${API_URL}/admin/metrics?period=${period}`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
  });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      message = data.message || data.error || message;
    } catch {
      /* ignore */
    }
    const err = new Error(message) as Error & { status?: number };
    err.status = res.status;
    throw err;
  }
  return res.json();
}

// Status palette (fixed, theme-independent) — mirrors dataviz status ramp.
export const STATUS_META: Record<
  HealthStatus,
  { label: string; icon: string; color: string; className: string }
> = {
  good: { label: '正常', icon: '●', color: '#0ca30c', className: 'text-green-700 bg-green-50 border-green-200' },
  warning: { label: '注意', icon: '▲', color: '#fab219', className: 'text-amber-800 bg-amber-50 border-amber-300' },
  serious: { label: '悪化', icon: '◆', color: '#ec835a', className: 'text-orange-800 bg-orange-50 border-orange-300' },
  critical: { label: '重大', icon: '■', color: '#d03b3b', className: 'text-red-800 bg-red-50 border-red-300' },
};

export function formatPct(v: number): string {
  return `${(v * 100).toFixed(0)}%`;
}
