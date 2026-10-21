export function canonicalJson(value: unknown): string;
export function inputHash(value: unknown): Promise<string>;
export function validateConnection(options: {
  baseUrl: string; synthetic: boolean; development: boolean; hostname: string;
}): string;
export function requestKnowledge<T>(options: {
  baseUrl: string; token: string; actor: string; path: string; method?: string;
  body?: unknown; revision?: number; fetchImpl?: typeof fetch;
}): Promise<T>;
