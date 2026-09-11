export type PeriodKey = '1' | '7' | '30' | 'custom' | 'all';
export function jstToday(now?: Date): string;
export function startOfWeekJst(now?: Date): string;
export function periodRange(key: string, now?: Date): { since: string | null; until: string | null };
export function isThisWeekJst(iso: string | null | undefined, now?: Date): boolean;
