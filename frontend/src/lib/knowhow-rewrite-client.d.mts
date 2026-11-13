import type { RewriteProposal, RewriteRequest } from './knowhow-rewrite.mjs';

export type KnowhowRewriteErrorCode =
  | 'auth' | 'config' | 'unavailable' | 'throttled' | 'failed' | 'network'
  | 'validation' | 'too_large' | 'timeout' | 'cancelled' | 'invalid_response';

export const REWRITE_TIMEOUT_MS: number;

/** 利用者に見せてよい固定文言だけを持つエラー。 */
export class KnowhowRewriteError extends Error {
  readonly code: KnowhowRewriteErrorCode;
  constructor(code: KnowhowRewriteErrorCode);
}

export function rewriteFailureMessage(error: unknown): string;

export function requestKnowhowRewrite(options: {
  baseUrl: string;
  getToken: () => Promise<string | null | undefined>;
  fetchImpl?: typeof fetch;
  request: RewriteRequest | null;
  signal?: AbortSignal;
  timeoutMs?: number;
}): Promise<RewriteProposal>;
