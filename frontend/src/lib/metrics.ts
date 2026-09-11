import { getIdToken, authHeaders } from './auth-helpers';

const API_URL = process.env.NEXT_PUBLIC_APP_API_URL || '';

export type HealthStatus = 'good' | 'warning' | 'serious' | 'critical';
/** null = 集計行が無い（0 と区別する。設計 §2.7） */
export type Count = number | null;
export type TrendDays = 14 | 30 | 90;

export interface AlarmNow {
  name: string;
  severity: 'P1' | 'P2';
  since: string | null;
}

export interface ActiveNotice {
  id: string;
  title: string;
  severity: 'info' | 'warning' | 'critical';
  since: string | null;
  showInChat: boolean;
}

export interface FunnelRow {
  signIns: Count;
  queries: Count;
  pages: Count;
  /** 'unmeasured' = DocumentOpen 未実装（設計 §2.4） */
  opened: Count | 'unmeasured';
  good: Count;
  unreached: Count;
  notFound: Count;
  bad: Count;
  reformulated: Count;
}

export interface DashboardEvent {
  at: string;
  kind: 'alarm' | 'ok';
  alarm: string;
  severity: 'P1' | 'P2';
  title: string;
  durationSec: number | null;
  resolvedAt: string | null;
  logGroup: string | null;
  queryName: string | null;
  from: string | null;
  to: string | null;
}

export interface DashboardResponse {
  generatedAt: string;
  today: string;
  now: {
    alarms: AlarmNow[];
    status: HealthStatus;
    last60min: { requests: number; http5xx: number; ragP90Ms: number | null; ragMaxMs: number | null; ragCount: number };
    freshness: { yesterdayAggregatedAt: string | null; todayPartialAt: string | null; status: HealthStatus };
    activeNotices: ActiveNotice[];
  };
  yesterday: {
    date: string;
    exists: boolean;
    incidents: { p1Transitions: Count; http5xx: Count; byApi: Record<string, number>; status: HealthStatus };
    latency: { p90Ms: number | null; p50Ms: number | null; maxMs: number | null; count: number | null; showP90: boolean; status: HealthStatus };
    unreached: { total: Count; notFound: Count; bad: Count; reformulated: Count; open: Count };
    usage: { queries: Count; uniqueUsers: Count; newUsers: Count; queriesSameWeekdayLastWeek: Count };
    bedrockCost: { estimatedUsd: number | null; estimateSource: string | null; monthActualUsd: number | null; actualThrough: string | null; status: HealthStatus };
  };
  todaySoFar: { asOf: string | null; queries: Count; unreached: Count; http5xx: Count } | null;
  funnel: { yesterday: FunnelRow; last7d: FunnelRow; last7dRange: { from: string; to: string }; showRates: boolean };
  trend: {
    days: number;
    queriesByDay: { date: string; total: number; unreached: number }[];
    latencyByDay: { date: string; p90Ms: number | null; maxMs: number | null }[];
    hourlyToday: { hour: string; queries: number; unreached: number }[];
  };
  events: DashboardEvent[];
  reference: {
    topDocuments: { name: string; count: number }[];
    lastEval: { date: string; hit: number | null; n: number | null; logicVersion?: string | null } | null;
  };
  thresholds: { sloP90Ms: number; p1MaxMs: number; timeoutMs: number; rateDenominatorMin: number };
}

export interface CostResponse {
  generatedAt: string;
  month: string;
  settledThrough: string | null;
  basis: 'UTC';
  confirmed: {
    total: number;
    bedrock: { service: string; total: number; input: number; output: number; cache: number; other: number };
    amplify: number;
    budgetUsd: number;
    budgetPct: number | null;
    forecastUsd: number | null;
  };
  unattributed: { total: number; byService: Record<string, number>; note: string };
  shared: { total: number; byService: Record<string, number> };
  otherSystems: { total: number; byService: Record<string, number> };
  checks: {
    soleUser: { ok: boolean | null; invocations: number; answers: number; detail: string };
    actualVsEstimate: { actual: number; estimate: number | null; diffPct: number | null; status: HealthStatus; days: number };
    modelIds: string[];
  };
  daily: { date: string; bedrockUsd: number; totalUsd: number; settled: boolean }[];
  queriesDaily: { date: string; queries: number }[];
  perQuery: { actualUsd: number | null; perAnswerUsd: number | null; queries: number; answers: number; traceMedianUsd: number | null; traceP90Usd: number | null };
  projection: { queriesPerDay: number; monthlyUsd: number | null }[];
}

async function request<T>(path: string): Promise<T> {
  const token = await getIdToken();
  const res = await fetch(`${API_URL}${path}`, {
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
  return res.json() as Promise<T>;
}

export function getDashboard(trend: TrendDays = 14): Promise<DashboardResponse> {
  return request<DashboardResponse>(`/admin/metrics/dashboard?trend=${trend}`);
}

export function getCost(month?: string): Promise<CostResponse> {
  const qs = month ? `?month=${encodeURIComponent(month)}` : '';
  return request<CostResponse>(`/admin/metrics/cost${qs}`);
}

// Status palette (fixed, theme-independent) — mirrors dataviz status ramp.
export const STATUS_META: Record<
  HealthStatus,
  { label: string; icon: string; color: string; className: string; stripe: string }
> = {
  good: { label: '正常', icon: '●', color: '#0ca30c', className: 'text-green-700 bg-green-50 border-green-200', stripe: 'border-l-green-500' },
  warning: { label: '注意', icon: '▲', color: '#fab219', className: 'text-amber-800 bg-amber-50 border-amber-300', stripe: 'border-l-amber-400' },
  serious: { label: '悪化', icon: '◆', color: '#ec835a', className: 'text-orange-800 bg-orange-50 border-orange-300', stripe: 'border-l-orange-400' },
  critical: { label: '重大', icon: '■', color: '#d03b3b', className: 'text-red-800 bg-red-50 border-red-300', stripe: 'border-l-red-500' },
};

export function formatPct(v: number): string {
  return `${(v * 100).toFixed(0)}%`;
}
