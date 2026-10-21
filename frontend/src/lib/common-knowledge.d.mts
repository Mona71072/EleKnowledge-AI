export function canonicalJson(value: unknown): string;
export function inputHash(value: unknown): Promise<string>;
export function validateConnection(options: {
  baseUrl: string; synthetic: boolean; development: boolean; hostname: string;
}): string;
export function requestKnowledge<T>(options: {
  baseUrl: string; token: string; actor: string; path: string; method?: string;
  body?: unknown; revision?: number; fetchImpl?: typeof fetch;
}): Promise<T>;
export type CommonKnowledgeMe = {
  actor: string;
  assignment: { permissions: string[]; domains: string[]; audiences: string[]; expiresAt: number } | null;
  contributions: { permissionId: string; domain: string; audience: string; expiresAt: number }[];
  evidence: { id: string; version: string; sha256: string; domain: string; audience: string;
    expiresAt: number; sourceVerified?: boolean }[];
};
export function validationGrant(me: CommonKnowledgeMe | null, scope: string): {
  scope: string; permissions: string[];
  contribution: CommonKnowledgeMe['contributions'][number] | null;
  evidence: CommonKnowledgeMe['evidence'];
};
