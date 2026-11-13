export type KnowledgeReviewSource = {
  kind: 'lists' | 'onenote' | 'technical';
  id: string;
  label: string;
  pageRole?: string;
};

export type KnowledgeSourceReviewInput = {
  source: KnowledgeReviewSource;
  method: 'snapshot' | 'opened_original';
  capturedOn?: string;
  locator: string;
  outcome: 'supports' | 'conditions_differ' | 'conflict' | 'insufficient';
  note: string;
  recordedAt: string;
};

export type KnowledgeSourceReviewRecord = KnowledgeSourceReviewInput & { revision: number };

export const MAX_SOURCE_SNAPSHOT_BYTES: number;

export function getReviewSources(metadata: Record<string, unknown>): KnowledgeReviewSource[];
export function resolveReviewSource(source: KnowledgeReviewSource | undefined, enteredId?: string): KnowledgeReviewSource | null;
export function readReviewSourceSnapshot(markdown: string, source: KnowledgeReviewSource): { text: string; capturedOn: string };
export function normalizeSourceReview(
  input: KnowledgeSourceReviewInput,
  metadata: Record<string, unknown>,
  revision: number,
): KnowledgeSourceReviewRecord;
