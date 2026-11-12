export function modelWithFacts(model: string): string;
export function modelFitNotice(
  match: { modelFit?: string; modelFitProducts?: readonly string[] },
  selectedModel?: string,
): string | null;
export const KNOWHOW_NOT_OFFICIAL_NOTICE: string;
export function knowhowStatusLabel(match: { status?: string }): string;
export function scopeUnverifiedNotice(match: { modelScope?: Record<string, unknown> }): string | null;
