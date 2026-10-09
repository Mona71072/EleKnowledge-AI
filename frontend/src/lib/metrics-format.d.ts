export type HealthStatus = 'good' | 'warning' | 'serious' | 'critical';

export function jstTime(iso: string | null | undefined): string;
export function jstDateTime(iso: string | null | undefined): string;
export function jstDateLabel(yyyyMmDd: string | null | undefined, withWeekday?: boolean): string;
export function formatUsd(value: number | null | undefined, digits?: number): string;
export function formatSeconds(ms: number | null | undefined, digits?: number): string;
export function formatDuration(sec: number | null | undefined): string;
export function formatCount(value: number | null | undefined): string;
export function rateLabel(
  numerator: number | null | undefined,
  denominator: number | null | undefined,
  minDenominator?: number,
): string | null;
export function logsInsightsUrl(args: {
  region?: string;
  logGroup: string | null | undefined;
  from: string | null | undefined;
  to: string | null | undefined;
}): string | null;
export const STATUS_LABELS: Record<HealthStatus, { label: string; icon: string }>;
export function worstStatus(...statuses: HealthStatus[]): HealthStatus;
